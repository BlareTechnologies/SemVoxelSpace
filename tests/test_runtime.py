from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from voxel_context.data import load_tile, metrics_from_confusion
from voxel_context.features import build_features, extract_window, grayworld, windows
from voxel_context.inference import predict

ROOT = Path(__file__).resolve().parents[1]


def config(variant="E3"):
    return json.loads((ROOT / "models" / variant / "model.json").read_text(encoding="utf-8"))


def fixture_tile(shape=(11, 19, 21)):
    rng = np.random.default_rng(47)
    occ = rng.integers(0, 2, shape, dtype=np.uint8)
    rgb = rng.integers(0, 256, shape + (3,), dtype=np.uint8)
    rgb[occ == 0] = 0
    return {"occ": occ, "rgb": rgb, "ortho": rng.integers(0, 8, shape, dtype=np.uint8),
            "llm_ortho": rng.integers(0, 8, shape, dtype=np.uint8),
            "osm_context": rng.integers(0, 2, shape + (3,), dtype=np.uint8),
            "labels": rng.integers(0, 8, shape, dtype=np.uint8),
            "origin": np.zeros(3, dtype=np.float32), "voxel_size": np.array([0.5], dtype=np.float32)}


@pytest.mark.parametrize("shape", [(3, 7, 5), (64, 150, 150), (73, 51, 49)])
def test_windows_cover_every_occupied_voxel_including_edges(shape):
    occ = np.ones(shape, dtype=np.uint8)
    coverage = np.zeros(shape, dtype=bool)
    starts = list(windows(occ, (32, 32, 64), (8, 8, 64)))
    assert len(starts) == len(set(starts))
    for x, y, z in starts:
        coverage[z:z + 64, y:y + 32, x:x + 32] = True
    assert coverage.all()


def test_stride_cannot_skip_voxels():
    with pytest.raises(ValueError, match="uncovered"):
        list(windows(np.ones((16, 16, 16), np.uint8), (8, 8, 8), (9, 8, 8)))


@pytest.mark.parametrize("variant,channels", [("E0", 10), ("E1", 12), ("E2", 15), ("E3", 18)])
def test_features_exclude_reference_labels(variant, channels):
    tile = fixture_tile()
    before = build_features(tile, config(variant))
    tile["labels"][:] = 7 - tile["labels"]
    assert np.array_equal(before, build_features(tile, config(variant)))
    assert before.shape == (channels,) + tile["occ"].shape


def test_e3_exact_mask_channel_order_and_weights():
    tile = fixture_tile((1, 1, 3))
    tile["ortho"] = np.array([[[1, 5, 0]]], dtype=np.uint8)
    tile["llm_ortho"] = np.array([[[7, 4, 6]]], dtype=np.uint8)
    tile["osm_context"] = np.eye(3, dtype=np.uint8)[None, None]
    features = build_features(tile, config())[:, 0, 0]
    np.testing.assert_array_equal(features[10:12], [[0.5, 0, 0], [0, 0.5, 0]])
    np.testing.assert_array_equal(features[12:15], np.eye(3) * 0.5)
    np.testing.assert_array_equal(features[15:18], np.eye(3) * 0.5)


def test_missing_context_is_an_error():
    tile = fixture_tile()
    del tile["osm_context"]
    with pytest.raises(ValueError, match="osm_context"):
        build_features(tile, config())
    assert build_features(tile, config("E0")).shape[0] == 10


def test_small_tile_padding_preserves_color_feature_background():
    tile = fixture_tile((1, 1, 1))
    window = extract_window(tile, (0, 0, 0), (8, 8, 8))
    features = build_features(window, config("E0"))
    assert features[0, -1, -1, -1] == 0
    # These transformed color features are 0.5 even on padded RGB=0 cells.
    np.testing.assert_array_equal(features[[5, 6, 8, 9], -1, -1, -1], 0.5)


def test_grayworld_uses_occupied_voxels_and_keeps_empty_zero():
    rgb = np.array([[[[100, 50, 25], [0, 0, 0]]]], dtype=np.uint8)
    actual = grayworld(rgb, np.array([[[True, False]]]))
    np.testing.assert_array_equal(actual[0, 0, 0], [114, 114, 114])
    np.testing.assert_array_equal(actual[0, 0, 1], [0, 0, 0])


def test_predictions_never_fall_back_to_ground_truth():
    class Classifier(torch.nn.Module):
        def forward(self, inputs):
            logits = torch.zeros((len(inputs), 8) + inputs.shape[2:])
            logits[:, 3] = 1
            return logits
    tile = fixture_tile((9, 9, 9))
    settings = config("E0") | {"chunk_size_xyz": [8, 8, 8], "stride_xyz": [4, 4, 4]}
    result = predict(tile, Classifier(), settings, "cpu")
    assert np.all(result["labels"] == 3)
    assert len(result["labels"]) == tile["occ"].sum()
    del tile["labels"]
    np.testing.assert_array_equal(predict(tile, Classifier(), settings, "cpu")["labels"], result["labels"])


def test_schema_rejects_invalid_mask_and_pickle(tmp_path):
    tile = fixture_tile()
    tile["ortho"][0, 0, 0] = 8
    path = tmp_path / "bad.npz"
    np.savez(path, **tile)
    with pytest.raises(ValueError, match="ortho"):
        load_tile(path)
    np.savez(path, obj=np.array([{}], dtype=object))
    with pytest.raises(ValueError, match="Object arrays"):
        load_tile(path)


def test_metric_convention_includes_zero_background_iou():
    matrix = np.diag([0, 10, 10, 10, 10, 10, 10, 10])
    metrics = metrics_from_confusion(matrix)
    assert metrics["mean_iou"] == 7 / 8
    assert metrics["foreground_mean_iou"] == 1
