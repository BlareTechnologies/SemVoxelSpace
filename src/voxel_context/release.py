"""Manifest-driven sample inventory shared by validation and packaging."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


REQUIRED_ASSETS = {"model_mask", "osm_mask", "llm_mask", "ortho"}


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def sample_files(root: Path, manifest: dict) -> dict[Path, str]:
    root = root.resolve()
    if manifest.get("scope") != "sample_only":
        raise ValueError("Only an explicitly declared sample may be packaged")
    files = {}
    ids = set()
    for record in manifest["tiles"]:
        if record["id"] in ids:
            raise ValueError(f"Duplicate tile: {record['id']}")
        ids.add(record["id"])
        if not REQUIRED_ASSETS <= record.get("assets", {}).keys():
            raise ValueError(f"Incomplete context assets: {record['id']}")
        entries = [(record["input_path"], record["input_sha256"]),
                   (record["labeler_path"], record["labeler_sha256"])]
        entries += [(a["path"], a["sha256"]) for a in record["assets"].values()]
        for relative, checksum in entries:
            path = (root / relative).resolve()
            if not path.is_relative_to(root / "data") or path in files:
                raise ValueError(f"Unsafe or duplicate sample path: {relative}")
            files[path] = checksum
    if not files:
        raise ValueError("The sample must contain at least one tile")
    return files


def verified_sample_files(root: Path, manifest: dict) -> list[Path]:
    selection = json.loads((root / "data/selection.json").read_text(encoding="utf-8"))
    validate_selection(manifest, selection)
    files = sample_files(root, manifest)
    for path, checksum in files.items():
        if sha256(path) != checksum:
            raise ValueError(f"Sample checksum mismatch: {path.name}")
    actual = {path.resolve() for directory in ("tiles", "labeler", "assets")
              for path in (root / "data" / directory).rglob("*") if path.is_file()}
    if actual != set(files):
        raise ValueError("Unlisted or missing payload files; refusing to publish data outside the sample")
    return sorted(files)


def validate_selection(manifest: dict, selection: dict) -> None:
    selected = {record["id"]: record["city"] for record in selection["tiles"]}
    actual = {record["id"]: record["city"] for record in manifest["tiles"]}
    if len(selected) != len(selection["tiles"]) or selected != actual:
        raise ValueError("Manifest does not match the fixed city/tile selection")
    if any(record["annotation_status"] != "ready" for record in manifest["tiles"]):
        raise ValueError("The sample may only contain verified reference annotations")
    count = Counter(actual.values())
    limit = selection["requested_tiles_per_city"]
    declared = {city["city"]: city["selected"] for city in selection["cities"]}
    if limit <= 0 or dict(count) != declared or any(value > limit for value in count.values()):
        raise ValueError("Sample city counts do not match the declared quota")
