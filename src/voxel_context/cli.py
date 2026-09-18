from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from .data import load_tile, metrics_from_confusion
from .inference import load_model, predict, write_ply, write_prediction
from .release import verified_sample_files

COLORS = [[0, 0, 0], [220, 20, 60], [255, 215, 0], [30, 144, 255],
          [160, 82, 45], [34, 139, 34], [124, 252, 0], [176, 196, 222]]


def verify(root: Path) -> dict:
    manifest = json.loads((root / "data/manifest.json").read_text(encoding="utf-8"))
    splits = json.loads((root / "data/splits.json").read_text(encoding="utf-8"))
    files = verified_sample_files(root, manifest)
    all_ids = [tile_id for ids in splits.values() for tile_id in ids]
    expected_ids = [record["id"] for record in manifest["tiles"]]
    if len(all_ids) != len(set(all_ids)) or set(all_ids) != set(expected_ids) or len(expected_ids) != len(set(expected_ids)):
        raise ValueError("Splits are overlapping, duplicated or incomplete")
    labels_total = 0
    for record in manifest["tiles"]:
        if record["id"] not in splits[record["split"]]:
            raise ValueError(f"Split mismatch: {record['id']}")
        tile = load_tile(root / record["input_path"])
        with np.load(root / record["assets"]["model_mask"]["path"], allow_pickle=False) as mask:
            for field, source in (("labels", "ortho"), ("occ", "occ"), ("origin", "origin"), ("voxel_size", "voxel_size")):
                if not np.array_equal(mask[field], tile[source]):
                    raise ValueError(f"Model mask/input mismatch: {record['id']} ({field})")
        if int(tile["occ"].sum()) != record["input_voxel_count"]:
            raise ValueError(f"Voxel count mismatch: {record['id']}")
        with np.load(root / record["labeler_path"], allow_pickle=False) as source:
            count = len(source["labels"])
            if source["indices"].shape != (count, 3) or count != record["current_voxel_count"]:
                raise ValueError(f"Annotation count mismatch: {record['id']}")
            labels_total += count
    return {"verified_tiles": len(expected_ids), "current_labeler_voxels": labels_total,
            "verified_payload_files": len(files), "scope": manifest["scope"],
            "city_counts": {city: sum(r["city"] == city for r in manifest["tiles"])
                            for city in sorted({r["city"] for r in manifest["tiles"]})},
            "split_counts": {name: len(ids) for name, ids in splits.items()}}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the paper's E0-E3 semantic voxel classifiers")
    sub = parser.add_subparsers(dest="command", required=True)
    infer = sub.add_parser("infer", help="Classify one prepared tile")
    infer.add_argument("--model", type=Path, default=Path("models/E3"))
    infer.add_argument("--tile", type=Path, required=True, help="Path to a prepared input tile (NPZ)")
    infer.add_argument("--output", type=Path, default=Path("outputs/prediction.npz"))
    infer.add_argument("--ply", type=Path, help="Also export class-colored voxel centers as PLY")
    infer.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    infer.add_argument("--threads", type=int, default=4, help="CPU thread count")
    evaluate = sub.add_parser("evaluate", help="Evaluate the explicit held-out test split")
    evaluate.add_argument("--root", type=Path, default=Path("."))
    evaluate.add_argument("--model", type=Path, default=Path("models/E3"))
    evaluate.add_argument("--output", type=Path, default=Path("outputs/benchmark.json"))
    evaluate.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    evaluate.add_argument("--threads", type=int, default=4)
    evaluate.add_argument("--limit", type=int, default=0, help="Smoke run on the first N test tiles; zero evaluates all")
    check = sub.add_parser("verify", help="Verify all dataset hashes, schemas and split membership")
    check.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    if args.command == "verify":
        print(json.dumps(verify(args.root), indent=2))
        return
    if args.threads <= 0:
        parser.error("--threads must be positive")
    torch.set_num_threads(args.threads)
    model, config, device = load_model(args.model, args.device)
    started = time.monotonic()
    if args.command == "infer":
        tile = load_tile(args.tile)
        def progress(done: int, total: int) -> None:
            if done == 1 or done == total or done % 25 == 0:
                print(f"Window {done}/{total}", flush=True)
        result = predict(tile, model, config, device, progress)
        write_prediction(args.output, result)
        if args.ply:
            write_ply(args.ply, result, COLORS)
        print(json.dumps({"output": str(args.output), "variant": config["variant"], "device": device,
                          "voxels": len(result["labels"]), "windows": result["window_count"],
                          "seconds": round(time.monotonic() - started, 2),
                          "metrics": result.get("metrics")}, indent=2))
    else:
        if args.limit < 0:
            parser.error("--limit cannot be negative")
        splits = json.loads((args.root / "data/splits.json").read_text(encoding="utf-8"))
        manifest = json.loads((args.root / "data/manifest.json").read_text(encoding="utf-8"))
        records = {record["id"]: record for record in manifest["tiles"]}
        tile_ids = splits["test"][:args.limit] if args.limit else splits["test"]
        matrix = np.zeros((8, 8), dtype=np.int64)
        per_tile = []
        for index, tile_id in enumerate(tile_ids, 1):
            print(f"Tile {index}/{len(tile_ids)}: {tile_id}", flush=True)
            result = predict(load_tile(args.root / records[tile_id]["input_path"]), model, config, device)
            if "metrics" not in result:
                raise ValueError(f"Test tile lacks reference labels: {tile_id}")
            matrix += np.asarray(result["metrics"]["confusion_matrix"], dtype=np.int64)
            per_tile.append({"tile_id": tile_id, **result["metrics"]})
        report = {"variant": config["variant"], "device": device, "tile_count": len(tile_ids),
                  "partial_benchmark": len(tile_ids) != manifest["reference_test_tile_count"],
                  "evaluation_scope": "released_test_sample", "available_test_tiles": len(splits["test"]),
                  "reference_test_tile_count": manifest["reference_test_tile_count"], "tile_ids": tile_ids,
                  "seconds": round(time.monotonic() - started, 2), **metrics_from_confusion(matrix), "per_tile": per_tile}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in report.items() if key not in ("per_tile", "confusion_matrix", "tile_ids")}, indent=2))
