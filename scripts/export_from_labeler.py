"""Build the selected public sample from an existing GVDB labeler workspace.

This is an offline, read-only export of source data. The destination must be empty.
The original repository is needed only for this maintainer command, not inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

from sample_assets import export_context_assets, write_sample_index

JOBS = {
    "E0": "e3water_ladder_E0",
    "E1": "e3water_ladder_E1",
    "E2": "e3water_ladder_E2",
    "E3": "20260621T164812_train_e3water",
}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(payload, indent=2, ensure_ascii=False) + "\n").replace("\n", "\r\n").encode("utf-8"))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def export(source: Path, destination: Path, selection_path: Path, resume: bool = False) -> None:
    source = source.resolve()
    destination = destination.resolve()
    workspace = source / "out/labeler-real-cloud/data/workspace/workspace.json"
    root = workspace.parent
    selection = read_json(selection_path)
    selected = {record["id"]: record for record in selection["tiles"]}
    if selection.get("scope") != "sample_only" or not selected or len(selected) != len(selection["tiles"]):
        raise ValueError("Expected a nonempty, unique sample selection")
    for directory in ("data/tiles", "data/labeler", "models"):
        path = destination / directory
        if path.exists() and any(path.iterdir()) and not resume:
            raise FileExistsError(f"Export destination is not empty: {path}")
        path.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(source / "tools"))
    from voxel_ml_common import load_tile_arrays, tile_sample_from_workspace, dense_tile_from_sparse
    from voxel_osm_context import build_dense_osm_context, load_osm_georef, _load_feature_collection
    from voxel_ml_model import make_model

    manifest = read_json(workspace)
    tiles = {tile["id"]: tile for tile in manifest["tiles"]}
    ready = {}
    for tile_id, tile in tiles.items():
        state_path = root / "states" / f"{tile_id}.json"
        state = read_json(state_path) if state_path.exists() else {}
        if state.get("status", tile.get("status")) == "ready":
            if not (root / "states" / f"{tile_id}.npz").is_file():
                raise ValueError(f"Ready tile has no saved reference labels: {tile_id}")
            ready[tile_id] = tile

    if not set(selected) <= set(ready):
        raise ValueError("Selected tiles must have saved, ready human annotations")
    source_ready_count = len(ready)

    dataset_root = root / "ml/datasets" / JOBS["E3"]
    training = read_json(dataset_root / "summary.json")
    benchmark = read_json(root / "ml/models" / JOBS["E3"] / "benchmark_summary.json")
    split = {
        "train": sorted(training["trainTileIds"]),
        "validation": sorted(training["valTileIds"]),
        "test": sorted(benchmark["tileIds"]),
    }
    assigned = [tile_id for ids in split.values() for tile_id in ids]
    if len(assigned) != len(set(assigned)) or not set(assigned) <= set(ready):
        raise ValueError("Overlapping splits or model tiles missing from the ready set")
    split["additional"] = sorted(set(ready) - set(assigned))
    source_split_counts = {name: len(ids) for name, ids in split.items()}
    source_voxels = {}
    for name, ids in split.items():
        count = 0
        for tile_id in ids:
            with np.load(root / "states" / f"{tile_id}.npz", allow_pickle=False) as state:
                count += state["labels"].size
        source_voxels[name] = count
    split_lookup = {tile_id: name for name, ids in split.items() for tile_id in ids}
    sample_split = {name: [tile_id for tile_id in ids if tile_id in selected] for name, ids in split.items()}
    write_json(destination / "data/splits.json", sample_split)
    write_json(destination / "data/selection.json", selection)
    write_json(destination / "data/classes.json", manifest["classes"])
    configs = {}
    model_records = []
    for variant, job in JOBS.items():
        model_root = root / "ml/models" / job
        info = read_json(model_root / "model_info.json")
        summary = read_json(root / "ml/datasets" / job / "summary.json")
        result = read_json(model_root / "benchmark_summary.json")
        if set(summary["trainTileIds"]) != set(split["train"]) or set(summary["valTileIds"]) != set(split["validation"]):
            raise ValueError(f"Training split differs for {variant}")
        if set(result["tileIds"]) != set(split["test"]):
            raise ValueError(f"Benchmark split differs for {variant}")
        checkpoint_path = model_root / "best.pt"
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        # Export tensor weights only: no optimizer, paths or executable objects.
        out = destination / "models" / variant
        out.mkdir(parents=True, exist_ok=True)
        torch.save(checkpoint["model_state"], out / "weights.pt")
        config = {
            "variant": variant, "source_job": job, "architecture": checkpoint["architecture"],
            "in_channels": checkpoint["in_channels"], "num_classes": checkpoint["num_classes"],
            "base_channels": checkpoint["base_channels"], "epoch": checkpoint["epoch"],
            "seed": checkpoint["seed"], "chunk_size_xyz": info["chunkSizeXYZ"],
            "stride_xyz": info["strideXYZ"], "color_normalization": checkpoint["color_normalization"],
            "input_channel_config": checkpoint["input_channel_config"],
            "class_names": checkpoint["classes"], "voxel_size_m": 0.5,
        }
        config["input_channel_config"].get("osmContext", {}).pop("cacheRoot", None)
        config["input_channel_config"].get("osmContext", {}).pop("overpassUrl", None)
        configs[variant] = config
        model = make_model(architecture=config["architecture"], in_channels=config["in_channels"],
                           num_classes=config["num_classes"], base_channels=config["base_channels"])
        model.load_state_dict(checkpoint["model_state"], strict=True)
        config["parameter_count"] = sum(parameter.numel() for parameter in model.parameters())
        write_json(out / "model.json", config)
        report_keys = ("updatedAt", "tileCount", "tileIds", "accuracy", "meanIoU", "meanClassAccuracy", "voxelCount", "perClassIoU", "perClassAccuracy", "confusionMatrix", "classes")
        report = {key: result[key] for key in report_keys if key in result}
        report["source_job"] = job
        write_json(destination / f"reports/{variant}_benchmark.json", report)
        write_json(destination / f"reports/{variant}_epoch_history.json", read_json(model_root / "epoch_history.json"))
        summary.pop("workspacePath", None)
        summary.get("inputChannelConfig", {}).get("osmContext", {}).pop("cacheRoot", None)
        write_json(destination / f"reports/{variant}_training_dataset.json", summary)
        model_records.append({"variant": variant, "source_job": job,
                              "source_checkpoint_sha256": digest(checkpoint_path),
                              "weights_sha256": digest(out / "weights.pt"),
                              "parameter_count": config["parameter_count"],
                              "benchmark_mean_iou": result["meanIoU"]})
        print(f"Exported {variant}: {config['parameter_count']:,} parameters", flush=True)

    ready = {tile_id: ready[tile_id] for tile_id in selected}
    records = []
    for index, (tile_id, tile) in enumerate(sorted(ready.items()), 1):
        sample = tile_sample_from_workspace(workspace, tile)
        arrays = load_tile_arrays(sample)
        subset = split_lookup[tile_id]
        # Retain original sparse geometry plus the actual saved human labels.
        sparse_path = destination / "data/labeler" / f"{tile_id}.npz"
        np.savez_compressed(sparse_path, indices=arrays.indices, rgb=arrays.rgb, labels=arrays.labels,
                            ortho_labels=arrays.ortho_labels, llm_ortho_labels=arrays.llm_ortho_labels,
                            osm_ortho_labels=arrays.osm_ortho_labels, origin=arrays.origin,
                            tile_origin=arrays.tile_origin, voxel_size=np.asarray([arrays.voxel_size], dtype=np.float32))
        snapshot_source = "current_labeler_export"
        source_snapshot_hash = None
        if subset in ("train", "validation"):
            old_path = dataset_root / ("train" if subset == "train" else "val") / f"{tile_id}.npz"
            with np.load(old_path, allow_pickle=False) as old:
                dense = {name: np.array(old[name], copy=True) for name in old.files}
            snapshot_source = "frozen_E3_training_snapshot"
            source_snapshot_hash = digest(old_path)
        else:
            dense = dense_tile_from_sparse(arrays)
            if not arrays.osm_mask_available:
                georef = load_osm_georef(sample, input_channel_config=configs["E3"]["input_channel_config"])
                if georef is None or _load_feature_collection(georef) is None:
                    raise ValueError(f"No frozen OSM mask or cached features for {tile_id}; export never downloads missing data")
            osm = build_dense_osm_context(sample=sample, dense=dense, input_channel_config=configs["E3"]["input_channel_config"])
            dense = {name: dense[name] for name in ("occ", "rgb", "ortho", "llm_ortho", "labels")} | {
                "osm_context": osm, "origin": np.asarray(arrays.tile_origin + arrays.origin + arrays.indices.min(axis=0) * arrays.voxel_size, dtype=np.float32),
                "voxel_size": np.asarray([arrays.voxel_size], dtype=np.float32), "tile_id": np.asarray([tile_id]),
            }
        # vehicle_prior is not an input to any E0-E3 model in the paper.
        dense.pop("vehicle_prior", None)
        input_path = destination / "data/tiles" / f"{tile_id}.npz"
        np.savez_compressed(input_path, **dense)
        current_dense = dense_tile_from_sparse(arrays)
        same_geometry = dense["occ"].shape == current_dense["occ"].shape and np.array_equal(dense["occ"], current_dense["occ"])
        changed_labels = int(np.count_nonzero(dense["labels"] != current_dense["labels"])) if same_geometry else None
        record = {
            "id": tile_id, "split": subset, "tags": tile.get("tags", []),
            "city": selected[tile_id]["city"], "city_name": selected[tile_id]["city_name"],
            "annotation_status": "ready",
            "raster_bounds_xy": {"min": tile["bbox"]["min"][:2], "max": tile["bbox"]["max"][:2]},
            "voxel_size_m": arrays.voxel_size, "current_voxel_count": int(len(arrays.labels)),
            "input_voxel_count": int(np.count_nonzero(dense["occ"])), "shape_zyx": list(dense["occ"].shape),
            "input_path": input_path.relative_to(destination).as_posix(),
            "labeler_path": sparse_path.relative_to(destination).as_posix(),
            "input_snapshot": snapshot_source, "source_snapshot_sha256": source_snapshot_hash,
            "source_geometry_sha256": digest(sample.data_path),
            "source_labels_sha256": digest(sample.state_labels_path),
            "input_sha256": digest(input_path), "labeler_sha256": digest(sparse_path),
            "geometry_matches_current_labeler": same_geometry,
            "labels_changed_since_training": changed_labels,
            "class_counts_current": np.bincount(arrays.labels, minlength=8).tolist(),
            "assets": export_context_assets(root, tile, dense, destination, selected[tile_id]["city"]),
        }
        records.append(record)
        if index % 10 == 0 or index == len(ready):
            print(f"Exported {index}/{len(ready)} tiles", flush=True)

    split_counts = Counter(record["split"] for record in records)
    voxels = {name: sum(record["current_voxel_count"] for record in records if record["split"] == name) for name in split}
    provenance = {
        "schema_version": 2, "scope": "sample_only", "exported_at": datetime.now(timezone.utc).isoformat(),
        "paper_source": "docs/paper_voxel_space_classification/drafts/ieee_draft_v4_en.md",
        "paper_source_sha256": digest(source / "docs/paper_voxel_space_classification/drafts/ieee_draft_v4_en.md"),
        "source_workspace_sha256": digest(workspace), "tile_count": len(ready),
        "split_counts": dict(split_counts), "current_voxels_by_split": voxels,
        "total_current_voxels": sum(voxels.values()), "models": model_records,
        "source_corpus": {"tile_count": source_ready_count, "split_counts": source_split_counts,
                          "current_voxels_by_split": source_voxels, "total_current_voxels": sum(source_voxels.values())},
        "city_counts": {city: sum(r["city"] == city for r in records) for city in sorted({r["city"] for r in records})},
        "tiles_with_label_changes_after_training": [r["id"] for r in records if r["labels_changed_since_training"]],
        "tiles_with_geometry_changes_after_training": [r["id"] for r in records if not r["geometry_matches_current_labeler"]],
        "paper_count_discrepancy": "Paper v4 calls 150 tiles training/validation; checkpoint manifests contain 127 train + 14 validation. Nine additional New York tiles were not in these model runs. The expanded benchmark has 25 tiles.",
    }
    write_json(destination / "data/manifest.json", {"schema_version": 2, "scope": "sample_only",
               "reference_test_tile_count": selection["reference_test_tile_count"], "tiles": records})
    write_json(destination / "reports/provenance.json", provenance)
    write_sample_index(destination, records, selection)
    print(json.dumps({"completed": True, "counts": dict(split_counts), "voxels": voxels}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--selection", type=Path, default=Path(__file__).resolve().parents[1] / "data/selection.json")
    parser.add_argument("--resume", action="store_true", help="Rebuild generated files after an interrupted export")
    args = parser.parse_args()
    export(args.source_repo, args.output, args.selection, resume=args.resume)
