"""The E0-E3 input contract. Arrays use Z,Y,X order and RGB uses a final axis."""
from __future__ import annotations

import numpy as np


def grayworld(rgb: np.ndarray, occupied: np.ndarray) -> np.ndarray:
    if not occupied.any():
        return np.array(rgb, copy=True)
    rgb_float = rgb.astype(np.float64)
    gains = (0.45 * 255.0) / np.maximum(rgb_float[occupied].mean(axis=0), 1.0)
    result = np.clip(rgb_float * gains, 0.0, 255.0)
    result[~occupied] = 0.0
    return result.astype(np.uint8)


def color_channels(rgb: np.ndarray, names: list[str]) -> list[np.ndarray]:
    rgb = np.clip(rgb.astype(np.float32, copy=False), 0.0, 1.0)
    r, g, b = (rgb[..., axis] for axis in range(3))
    total = np.maximum(r + g + b, 1.0e-6)
    available = {
        "green_chromaticity": g / total,
        "excess_green": np.clip(0.5 + 0.25 * (2.0 * g - r - b), 0.0, 1.0),
        "green_dominance": np.clip(0.5 + 0.5 * (g - np.maximum(r, b)), 0.0, 1.0),
        "saturation": np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b),
        "normalized_green_red": np.clip(0.5 + 0.5 * ((g - r) / np.maximum(g + r, 1.0e-6)), 0.0, 1.0),
        "normalized_green_blue": np.clip(0.5 + 0.5 * ((g - b) / np.maximum(g + b, 1.0e-6)), 0.0, 1.0),
    }
    unknown = set(names) - available.keys()
    if unknown:
        raise ValueError(f"Unsupported color features: {sorted(unknown)}")
    return [available[name][..., None] for name in names]


def build_features(chunk: dict[str, np.ndarray], config: dict) -> np.ndarray:
    """Build C,Z,Y,X float32 features, preserving the checkpoint channel order.

    Reference labels are deliberately never accessed here.
    """
    channels = config["input_channel_config"]
    base = channels["baseInputs"]
    if base.get("vehiclePrior", False):
        raise ValueError("This paper runtime supports the E0-E3 models without vehiclePrior")
    rgb = chunk["rgb"].astype(np.float32) / 255.0
    parts = []
    if base.get("occupancy", True):
        parts.append(chunk["occ"].astype(np.float32)[..., None])
    if base.get("rgb", True):
        parts.append(rgb)
    parts.extend(color_channels(rgb, channels.get("colorFeatures", [])))
    for channel in channels.get("maskChannels", []):
        mask = np.zeros(chunk["occ"].shape, dtype=np.float32)
        for item in channel["items"]:
            key = {"model": "ortho", "llm": "llm_ortho"}.get(item["source"])
            if key is None or key not in chunk:
                raise ValueError(f"Missing mask source: {item['source']}")
            mask[np.isin(chunk[key], item["classes"])] = 1.0
        parts.append((mask * float(channel["weight"]))[..., None])
    osm_layers = ["building", "road", "water"]
    for channel in channels.get("osmChannels", []):
        if "osm_context" not in chunk:
            raise ValueError("This model requires frozen osm_context channels")
        layer = osm_layers.index(channel["layer"])
        parts.append(np.clip(chunk["osm_context"][..., layer].astype(np.float32), 0.0, 1.0)[..., None] * float(channel["weight"]))
    result = np.concatenate(parts, axis=-1).transpose(3, 0, 1, 2).astype(np.float32)
    if result.shape[0] != config["in_channels"]:
        raise ValueError(f"Expected {config['in_channels']} channels, built {result.shape[0]}")
    return result


def windows(occupancy: np.ndarray, chunk_xyz: tuple[int, int, int], stride_xyz: tuple[int, int, int]):
    """Include the final boundary window on every axis, including small tiles."""
    if any(value <= 0 for value in (*chunk_xyz, *stride_xyz)):
        raise ValueError("Chunk and stride dimensions must be positive")
    if any(stride > chunk for stride, chunk in zip(stride_xyz, chunk_xyz)):
        raise ValueError("Stride larger than chunk size would leave uncovered voxels")
    axes = []
    for extent, chunk, stride in zip(reversed(occupancy.shape), chunk_xyz, stride_xyz):
        last = max(0, extent - chunk)
        positions = list(range(0, last + 1, stride))
        if positions[-1] != last:
            positions.append(last)
        axes.append(positions)
    cx, cy, cz = chunk_xyz
    for z in axes[2]:
        for y in axes[1]:
            for x in axes[0]:
                if np.any(occupancy[z:z + cz, y:y + cy, x:x + cx]):
                    yield x, y, z


def extract_window(tile: dict[str, np.ndarray], start_xyz: tuple[int, int, int], chunk_xyz: tuple[int, int, int]) -> dict[str, np.ndarray]:
    x, y, z = start_xyz
    cx, cy, cz = chunk_xyz
    result = {}
    for key in ("occ", "rgb", "ortho", "llm_ortho", "osm_context"):
        if key not in tile:
            continue
        array = tile[key]
        part = array[z:z + cz, y:y + cy, x:x + cx]
        target = np.zeros((cz, cy, cx) + array.shape[3:], dtype=array.dtype)
        target[:part.shape[0], :part.shape[1], :part.shape[2]] = part
        result[key] = target
    return result
