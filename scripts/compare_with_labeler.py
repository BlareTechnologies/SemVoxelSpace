"""Maintainer check: independent runtime versus the original labeler pipeline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--tile", default="tile_x1_y1")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    args = parser.parse_args()
    public = Path(__file__).resolve().parents[1]
    source = args.source_repo.resolve()
    sys.path.insert(0, str(source / "tools"))
    sys.path.insert(0, str(public / "src"))
    from voxel_ml_common import apply_grayworld_rgb, build_input_features
    from voxel_ml_infer import predict_tile_labels
    from voxel_context.data import load_tile
    from voxel_context.features import build_features, extract_window, grayworld
    from voxel_context.inference import load_model, predict

    torch.set_num_threads(4)
    tile = load_tile(public / "data/tiles" / f"{args.tile}.npz")
    normalized = dict(tile)
    normalized["rgb"] = grayworld(tile["rgb"], tile["occ"].astype(bool))
    np.testing.assert_array_equal(normalized["rgb"], apply_grayworld_rgb(tile["rgb"], tile["occ"].astype(bool)))
    checks = []
    for variant in ("E0", "E1", "E2", "E3"):
        model, config, device = load_model(public / "models" / variant, args.device)
        for start in ((0, 0, 0), (max(0, tile["occ"].shape[2] - 32), max(0, tile["occ"].shape[1] - 32), 0)):
            chunk = extract_window(normalized, start, tuple(config["chunk_size_xyz"]))
            original = build_input_features(occ=chunk["occ"].astype(np.float32), rgb=chunk["rgb"].astype(np.float32) / 255.0,
                ortho=chunk["ortho"], num_classes=8, llm_ortho=chunk["llm_ortho"],
                input_channel_config=config["input_channel_config"], osm_context=chunk["osm_context"], expected_in_channels=config["in_channels"])
            np.testing.assert_array_equal(build_features(chunk, config), original.transpose(3, 0, 1, 2))
        checks.append({"variant": variant, "strict_weight_load": True, "feature_parity": "bitwise exact"})
        del model
    workspace = source / "out/labeler-real-cloud/data/workspace/workspace.json"
    model, config, device = load_model(public / "models/E3", args.device)
    print("Running the original E3 full-tile inference...", flush=True)
    original = predict_tile_labels(workspace_path=workspace, tile_id=args.tile,
        chunk_size_xyz=tuple(config["chunk_size_xyz"]), stride_xyz=tuple(config["stride_xyz"]), device=device,
        checkpoint_path=workspace.parent / "ml/models" / config["source_job"] / "best.pt")
    print("Running the independent E3 full-tile inference...", flush=True)
    actual = predict(tile, model, config, device)
    with np.load(public / "data/labeler" / f"{args.tile}.npz", allow_pickle=False) as sparse:
        indices = sparse["indices"] - sparse["indices"].min(axis=0)
    # Original output preserves input sparse order; release output uses Z,Y,X order.
    linear = np.ravel_multi_index(indices[:, ::-1].T, tile["occ"].shape)
    order = np.argsort(linear)
    np.testing.assert_array_equal(actual["labels"], original["predicted"][order])
    np.testing.assert_array_equal(actual["reference_labels"], original["labels"][order])
    result = {"device": device, "models": checks, "tile_id": args.tile,
              "compared_voxels": len(actual["labels"]), "full_tile_prediction_parity": "bitwise exact",
              "windows": actual["window_count"], "current_tile_metrics": actual["metrics"]}
    (public / "reports/upstream_parity.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
