"""Sliding-window inference with summed logits; no ground-truth fallbacks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

import numpy as np
import torch

from .data import confusion_metrics
from .features import build_features, extract_window, grayworld, windows
from .network import make_model


def load_model(directory: Path, device: str = "auto") -> tuple[object, dict, str]:
    config = json.loads((directory / "model.json").read_text(encoding="utf-8"))
    device = ("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; choose --device cpu or install a CUDA PyTorch build")
    model = make_model(architecture=config["architecture"], in_channels=config["in_channels"],
                       num_classes=config["num_classes"], base_channels=config["base_channels"])
    state = torch.load(directory / "weights.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=True)
    model.to(device).eval()
    return model, config, device


def predict(tile: dict[str, np.ndarray], model: object, config: dict, device: str,
            progress: Callable[[int, int], None] | None = None) -> dict:
    tile = dict(tile)
    occupied = tile["occ"].astype(bool)
    if config["color_normalization"] != "grayworld":
        raise ValueError("The published models require grayworld normalization")
    if not bool(tile.get("rgb_is_normalized", False)):
        tile["rgb"] = grayworld(tile["rgb"], occupied)
    chunk_xyz = tuple(config["chunk_size_xyz"])
    stride_xyz = tuple(config["stride_xyz"])
    if any(value % 8 for value in chunk_xyz):
        raise ValueError("Three downsampling levels require chunk dimensions divisible by 8")
    starts = list(windows(tile["occ"], chunk_xyz, stride_xyz))
    accumulator = np.zeros((config["num_classes"],) + occupied.shape, dtype=np.float32)
    coverage = np.zeros(occupied.shape, dtype=bool)
    cx, cy, cz = chunk_xyz
    with torch.inference_mode():
        for index, (x, y, z) in enumerate(starts, 1):
            chunk = extract_window(tile, (x, y, z), chunk_xyz)
            features = build_features(chunk, config)
            inputs = torch.from_numpy(features[None]).to(device)
            logits = model(inputs)[0].detach().cpu().numpy().astype(np.float32, copy=False)
            az, ay, ax = (min(size, extent - offset) for size, extent, offset in zip((cz, cy, cx), occupied.shape, (z, y, x)))
            accumulator[:, z:z + az, y:y + ay, x:x + ax] += logits[:, :az, :ay, :ax]
            coverage[z:z + az, y:y + ay, x:x + ax] = True
            if progress:
                progress(index, len(starts))
    if not np.all(coverage[occupied]):
        raise RuntimeError("Inference left occupied voxels uncovered")
    prediction = np.argmax(accumulator[:, occupied], axis=0).astype(np.uint8)
    indices = np.argwhere(occupied)[:, ::-1].astype(np.int32)
    result = {"indices": indices, "labels": prediction, "rgb": tile["rgb"][occupied],
              "origin": tile["origin"], "voxel_size": tile["voxel_size"], "window_count": len(starts)}
    if "labels" in tile:
        result["reference_labels"] = tile["labels"][occupied]
        result["metrics"] = confusion_metrics(result["reference_labels"], prediction)
    return result


def write_prediction(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **{key: value for key, value in result.items() if isinstance(value, np.ndarray)})


def write_ply(path: Path, result: dict, class_colors: list[list[int]]) -> None:
    points = result["origin"] + (result["indices"] + 0.5) * float(result["voxel_size"].item())
    colors = np.asarray(class_colors, dtype=np.uint8)[result["labels"]]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
        handle.write("property float x\nproperty float y\nproperty float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n")
        for xyz, rgb in zip(points, colors):
            handle.write("%.6f %.6f %.6f %d %d %d\n" % (*xyz, *rgb))
