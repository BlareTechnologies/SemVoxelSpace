"""Make reproducible GitHub Release archives and a SHA-256 asset index."""
from __future__ import annotations

import hashlib
import argparse
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from voxel_context.release import verified_sample_files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=["all", "models", "data"], default="all")
    args = parser.parse_args()
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    groups = {}
    if args.kind in ("all", "models"):
        paths = [ROOT / "models" / variant / name for variant in ("E0", "E1", "E2", "E3")
                 for name in ("weights.pt", "model.json")]
        if not all(path.is_file() for path in paths):
            raise ValueError("A model weight or configuration file is missing")
        groups["voxel-context3d-models-v1.zip"] = paths
    if args.kind in ("all", "data"):
        manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
        groups["voxel-context3d-sample-v1.zip"] = verified_sample_files(ROOT, manifest)
    assets = []
    for name, paths in groups.items():
        path = out / name
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for source in sorted(paths):
                info = zipfile.ZipInfo(source.relative_to(ROOT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED if source.suffix == ".npz" else zipfile.ZIP_DEFLATED
                with archive.open(info, "w") as target, source.open("rb") as handle:
                    for block in iter(lambda: handle.read(1024 * 1024), b""):
                        target.write(block)
        checksum = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                checksum.update(block)
        assets.append({"name": name, "sha256": checksum.hexdigest(), "size_bytes": path.stat().st_size,
                       "kind": "models" if "models" in name else "data", "file_count": len(paths)})
        print(f"{name}: {path.stat().st_size / 1048576:.1f} MiB", flush=True)
    (ROOT / "artifacts.json").write_bytes((json.dumps({"schema_version": 1, "assets": assets}, indent=2) + "\n").replace("\n", "\r\n").encode())


if __name__ == "__main__":
    main()
