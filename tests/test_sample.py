import hashlib
import json
import sys

import numpy as np
import pytest

from voxel_context import cli
from voxel_context.data import metrics_from_confusion
from voxel_context.release import verified_sample_files, validate_selection


def sample_manifest(root):
    def payload(relative):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"sample content")
        return {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    dense = payload("data/tiles/a.npz")
    sparse = payload("data/labeler/a.npz")
    assets = {role: payload(f"data/assets/city/a/{role}.{suffix}") for role, suffix in
              (("model_mask", "npz"), ("osm_mask", "png"), ("llm_mask", "png"), ("ortho", "png"))}
    (root / "data/selection.json").write_text(json.dumps({"tiles": [{"id": "a", "city": "city"}],
            "requested_tiles_per_city": 3, "cities": [{"city": "city", "selected": 1}]}), encoding="utf-8")
    return {"scope": "sample_only", "tiles": [{"id": "a", "city": "city", "annotation_status": "ready", "input_path": dense["path"],
            "input_sha256": dense["sha256"], "labeler_path": sparse["path"],
            "labeler_sha256": sparse["sha256"], "assets": assets}]}


def test_release_includes_all_masks_and_rejects_non_sample_tiles(tmp_path):
    manifest = sample_manifest(tmp_path)
    assert len(verified_sample_files(tmp_path, manifest)) == 6
    (tmp_path / "data/tiles/unselected.npz").write_bytes(b"private data")
    with pytest.raises(ValueError, match="outside the sample"):
        verified_sample_files(tmp_path, manifest)


@pytest.mark.parametrize("role", ["model_mask", "osm_mask", "llm_mask", "ortho"])
def test_incomplete_multimodal_sample_is_rejected(tmp_path, role):
    manifest = sample_manifest(tmp_path)
    del manifest["tiles"][0]["assets"][role]
    with pytest.raises(ValueError, match="Incomplete context"):
        verified_sample_files(tmp_path, manifest)


def test_corrupt_context_image_is_rejected(tmp_path):
    manifest = sample_manifest(tmp_path)
    (tmp_path / "data/assets/city/a/llm_mask.png").write_bytes(b"changed")
    with pytest.raises(ValueError, match="checksum"):
        verified_sample_files(tmp_path, manifest)


def test_all_released_test_tiles_still_report_a_partial_paper_benchmark(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    (data / "splits.json").write_text(json.dumps({"test": ["a"]}), encoding="utf-8")
    (data / "manifest.json").write_text(json.dumps({"reference_test_tile_count": 25,
            "tiles": [{"id": "a", "input_path": "data/tiles/a.npz"}]}), encoding="utf-8")
    output = tmp_path / "report.json"
    monkeypatch.setattr(sys, "argv", ["voxel-context", "evaluate", "--root", str(tmp_path), "--output", str(output)])
    monkeypatch.setattr(cli, "load_model", lambda *args: (None, {"variant": "E3"}, "cpu"))
    monkeypatch.setattr(cli, "load_tile", lambda *args: {})
    monkeypatch.setattr(cli, "predict", lambda *args: {"metrics": metrics_from_confusion(np.eye(8, dtype=np.int64))})
    cli.main()
    report = json.loads(output.read_text())
    assert report["tile_count"] == report["available_test_tiles"] == 1
    assert report["partial_benchmark"] is True
    assert report["reference_test_tile_count"] == 25
    assert report["evaluation_scope"] == "released_test_sample"


def test_city_alias_or_tile_assignment_cannot_change_silently(tmp_path):
    manifest = sample_manifest(tmp_path)
    selection = json.loads((tmp_path / "data/selection.json").read_text())
    manifest["tiles"][0]["city"] = "another-city"
    with pytest.raises(ValueError, match="fixed city/tile selection"):
        validate_selection(manifest, selection)


def test_more_than_requested_tiles_per_city_is_rejected():
    records = [{"id": str(i), "city": "city", "annotation_status": "ready"} for i in range(4)]
    with pytest.raises(ValueError, match="quota"):
        validate_selection({"tiles": records}, {"tiles": records, "requested_tiles_per_city": 3,
                            "cities": [{"city": "city", "selected": 4}]})
