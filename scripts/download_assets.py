"""Download release assets, verify their SHA-256 hashes, then extract safely.

Use --from-dir dist for an entirely offline installation test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def extract_verified(archive_path: Path, root: Path, asset: dict) -> int:
    if archive_path.stat().st_size != asset["size_bytes"] or digest(archive_path) != asset["sha256"]:
        raise ValueError(f"Asset checksum or size mismatch: {archive_path.name}")
    root = root.resolve()
    allowed = ("models",) if asset["kind"] == "models" else ("data", "tiles", "labeler", "assets")
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.infolist()
        if len(entries) != asset["file_count"]:
            raise ValueError("Archive file count does not match the asset index")
        targets = []
        seen = set()
        for entry in entries:
            raw_name = entry.orig_filename
            member = PurePosixPath(raw_name)
            if (member.is_absolute() or ".." in member.parts or ":" in raw_name or "\\" in raw_name
                    or not member.parts or member.parts[0] != allowed[0]
                    or stat.S_ISLNK(entry.external_attr >> 16) or entry.is_dir()):
                raise ValueError(f"Unsafe archive member: {entry.filename}")
            if asset["kind"] == "data":
                arrays = len(member.parts) == 3 and member.parts[1] in ("tiles", "labeler") and member.suffix == ".npz"
                context = len(member.parts) == 5 and member.parts[1] == "assets" and member.suffix in (".png", ".npz")
                if not (arrays or context):
                    raise ValueError(f"Unexpected data member: {entry.filename}")
            target = (root / entry.filename).resolve()
            if not target.is_relative_to(root) or target in seen:
                raise ValueError(f"Unsafe or duplicate extraction target: {entry.filename}")
            seen.add(target)
            if target.exists():
                with archive.open(entry) as handle:
                    expected = hashlib.sha256(handle.read()).hexdigest()
                if not target.is_file() or digest(target) != expected:
                    raise FileExistsError(f"Refusing to overwrite a different existing file: {target}")
            targets.append((entry, target))
        for entry, target in targets:
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".partial")
            with archive.open(entry) as source, temporary.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            temporary.replace(target)
    return len(targets)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="GitHub owner/repository, e.g. your-account/voxel-context3d")
    parser.add_argument("--tag", default="v1.0.0")
    parser.add_argument("--kind", choices=["all", "models", "data"], default="all")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--from-dir", type=Path, help="Use local ZIP archives instead of downloading")
    args = parser.parse_args()
    if args.from_dir is None and (not args.repo or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo)):
        parser.error("Supply --repo owner/repository or --from-dir PATH")
    index = json.loads((args.root / "artifacts.json").read_text(encoding="utf-8"))
    for asset in index["assets"]:
        if args.kind != "all" and asset["kind"] != args.kind:
            continue
        if args.from_dir is not None:
            path = args.from_dir / asset["name"]
        else:
            downloads = args.root / ".downloads"
            downloads.mkdir(exist_ok=True)
            path = downloads / asset["name"]
            if not path.exists() or digest(path) != asset["sha256"]:
                url = f"https://github.com/{args.repo}/releases/download/{urllib.parse.quote(args.tag, safe='')}/{asset['name']}"
                temporary = path.with_name(path.name + ".partial")
                print(f"Downloading {asset['name']}", flush=True)
                with urllib.request.urlopen(url, timeout=60) as response, temporary.open("wb") as target:
                    shutil.copyfileobj(response, target)
                temporary.replace(path)
        count = extract_verified(path, args.root, asset)
        print(f"Verified and installed {asset['name']}: {count} files", flush=True)


if __name__ == "__main__":
    main()
