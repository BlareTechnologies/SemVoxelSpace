"""Copy original context images and export the exact numeric model mask."""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import numpy as np
from PIL import Image


REQUIRED_IMAGES = {
    "ortho": ("ortho2048", "ortho_2048"),
    "osm_mask": ("osmMask", "osm_masks"),
    "llm_mask": ("llmMask", "llm_masks"),
    "model_overlay": ("overlay", "overlays"),
}


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def image_sources(workspace_root: Path, tile: dict) -> dict[str, Path]:
    sources = {}
    for role, (field, directory) in REQUIRED_IMAGES.items():
        value = tile.get(field)
        source = Path(value) if value else workspace_root / directory / f"{tile['id']}.png"
        if value and not source.is_absolute():
            source = workspace_root / source
        if not source.is_file():
            raise FileNotFoundError(f"Missing {role} for {tile['id']}: {source}")
        sources[role] = source
    # Some original raster predictions were not retained. The numerical mask
    # exported below is available for every tile and never uses human labels.
    original = workspace_root / "ortho_predictions" / f"{tile['id']}.png"
    if original.is_file():
        sources["model_mask_raster"] = original
    return sources


def export_context_assets(workspace_root: Path, tile: dict, dense: dict,
                          destination: Path, city: str) -> dict:
    sources = image_sources(workspace_root, tile)
    target_dir = destination / "data/assets" / city / tile["id"]
    if not target_dir.resolve().is_relative_to((destination / "data/assets").resolve()):
        raise ValueError("Sample asset path leaves the destination")
    target_dir.mkdir(parents=True, exist_ok=True)
    assets = {}
    for role, source in sources.items():
        with Image.open(source) as image:
            image.load()
            size, mode = list(image.size), image.mode
        target = target_dir / f"{role}.png"
        shutil.copyfile(source, target)
        assets[role] = {"path": target.relative_to(destination).as_posix(),
                        "sha256": digest(target), "size_bytes": target.stat().st_size,
                        "width_height": size, "mode": mode,
                        "provenance": "original_labeler_file_unmodified"}
    # Masks can have different pixel resolutions over the same tile extent.
    # Preserve native pixels; the runtime consumes the already aligned arrays.
    target = target_dir / "model_mask.npz"
    np.savez_compressed(target, labels=dense["ortho"], occ=dense["occ"],
                        origin=dense["origin"], voxel_size=dense["voxel_size"])
    assets["model_mask"] = {"path": target.relative_to(destination).as_posix(),
                            "sha256": digest(target), "size_bytes": target.stat().st_size,
                            "shape_zyx": list(dense["ortho"].shape),
                            "provenance": "exact_prepared_input_ortho_array"}
    return assets


def write_sample_index(destination: Path, records: list[dict], selection: dict) -> None:
    lines = ["# Released data sample", "",
             "The sample files are included in the repository; these links work after cloning.",
             "Each example has a dense input, sparse human annotations, ortho, model mask, OSM mask and LLM mask.",
             "Model masks are complete numeric NPZ volumes; PNG source masks are included where retained.", "",
             "| City | Released tiles | Available ready tiles in the source corpus |",
             "| --- | ---: | ---: |"]
    for city in selection["cities"]:
        lines.append(f"| {city['city_name']} | {city['selected']} | {city['available_ready']} |")
    shortfalls = [f"{c['city_name']} ({c['selected']})" for c in selection["cities"] if c["shortfall"]]
    lines += ["", "Availability exceptions: " + (", ".join(shortfalls) or "none") + ".",
              f"Target: {selection['requested_tiles_per_city']} tiles per city. Released: {len(records)} tiles and "
              f"{sum(r['current_voxel_count'] for r in records):,} occupied voxels.",
              "Splits retain their original role. These examples do not comprise the full paper benchmark.", ""]
    for city in selection["cities"]:
        lines += [f"## {city['city_name']}", ""]
        for record in sorted((r for r in records if r["city"] == city["city"]), key=lambda r: r["id"]):
            def link(label, path):
                return f"[{label}]({Path(path).relative_to('data').as_posix()})"
            links = [link("Input NPZ", record["input_path"]), link("Human labels", record["labeler_path"])]
            links += [link(label, record["assets"][role]["path"]) for label, role in
                      (("Ortho", "ortho"), ("Model mask", "model_mask"), ("OSM mask", "osm_mask"),
                       ("LLM mask", "llm_mask"), ("Model overlay", "model_overlay"))]
            if "model_mask_raster" in record["assets"]:
                links.append(link("Original model PNG", record["assets"]["model_mask_raster"]["path"]))
            lines += [f"- **`{record['id']}`** — {record['split']}, {record['current_voxel_count']:,} voxels.  ",
                      "  " + " · ".join(links)]
        lines.append("")
    (destination / "data/SAMPLES.md").write_bytes(("\n".join(lines) + "\n").replace("\n", "\r\n").encode("utf-8"))
