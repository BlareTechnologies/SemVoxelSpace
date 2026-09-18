"""Strict loading of the portable, pickle-free tile schema."""
from __future__ import annotations

from pathlib import Path

import numpy as np


def load_tile(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        tile = {name: np.array(archive[name], copy=True) for name in archive.files}
    for key in ("occ", "rgb", "origin", "voxel_size"):
        if key not in tile:
            raise ValueError(f"Missing tile array: {key}")
    shape = tile["occ"].shape
    if len(shape) != 3 or not all(shape) or tile["occ"].dtype != np.uint8:
        raise ValueError("occ must be a nonempty uint8 Z,Y,X array")
    if not np.isin(tile["occ"], [0, 1]).all() or not tile["occ"].any():
        raise ValueError("occ must contain occupied voxels, with values 0 or 1")
    if tile["rgb"].shape != shape + (3,) or tile["rgb"].dtype != np.uint8:
        raise ValueError("rgb must be uint8 Z,Y,X,3")
    for key in ("ortho", "llm_ortho", "labels"):
        if key in tile and (tile[key].shape != shape or tile[key].dtype != np.uint8 or np.any(tile[key] > 7)):
            raise ValueError(f"{key} must be uint8 Z,Y,X with class IDs 0..7")
    if "osm_context" in tile:
        array = tile["osm_context"]
        if array.shape != shape + (3,) or array.dtype != np.uint8 or not np.isin(array, [0, 1]).all():
            raise ValueError("osm_context must be binary uint8 Z,Y,X,3 (building, road, water)")
    if tile["origin"].shape != (3,) or not np.isfinite(tile["origin"]).all():
        raise ValueError("origin must have three finite coordinates")
    if tile["voxel_size"].size != 1 or not np.isfinite(tile["voxel_size"]).all() or float(tile["voxel_size"].item()) <= 0:
        raise ValueError("voxel_size must contain one finite, positive value")
    if "rgb_is_normalized" in tile and (tile["rgb_is_normalized"].size != 1 or tile["rgb_is_normalized"].dtype != np.bool_):
        raise ValueError("rgb_is_normalized must be one boolean")
    return tile


def confusion_metrics(reference: np.ndarray, prediction: np.ndarray, classes: int = 8) -> dict:
    matrix = np.bincount(reference.astype(np.int64) * classes + prediction.astype(np.int64), minlength=classes * classes).reshape(classes, classes)
    return metrics_from_confusion(matrix)


def metrics_from_confusion(matrix: np.ndarray) -> dict:
    matrix = np.asarray(matrix, dtype=np.int64)
    diagonal = np.diag(matrix)
    union = matrix.sum(0) + matrix.sum(1) - diagonal
    iou = np.divide(diagonal, union, out=np.zeros(8, dtype=np.float64), where=union != 0)
    return {"voxel_count": int(matrix.sum()), "accuracy": float(diagonal.sum() / max(1, matrix.sum())),
            "mean_iou": float(iou.mean()), "foreground_mean_iou": float(iou[1:].mean()),
            "per_class_iou": iou.tolist(), "confusion_matrix": matrix.tolist()}
