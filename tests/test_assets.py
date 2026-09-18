import hashlib
import importlib.util
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/download_assets.py"
SPEC = importlib.util.spec_from_file_location("download_assets", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def archive(tmp_path, name, data=b"contents"):
    path = tmp_path / "asset.zip"
    with zipfile.ZipFile(path, "w") as handle:
        handle.writestr(name, data)
    # Python's ZIP writer normalizes backslashes on Windows. Restore the raw
    # filename bytes in both headers to exercise the untrusted archive case.
    if "\\" in name:
        path.write_bytes(path.read_bytes().replace(name.replace("\\", "/").encode(), name.encode()))
    record = {"kind": "data", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "size_bytes": path.stat().st_size, "file_count": 1}
    return path, record


@pytest.mark.parametrize("member", ["../escape", "/absolute", "data/../../escape", "data\\tiles\\escape", "data/tiles/C:escape"])
def test_archive_paths_cannot_escape(tmp_path, member):
    path, record = archive(tmp_path, member)
    with pytest.raises(ValueError):
        MODULE.extract_verified(path, tmp_path / "installed", record)


def test_corrupt_archive_rejected_before_extracting(tmp_path):
    path, record = archive(tmp_path, "data/tiles/a.npz")
    record["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="checksum"):
        MODULE.extract_verified(path, tmp_path / "installed", record)
    assert not (tmp_path / "installed").exists()


def test_existing_data_not_overwritten_and_identical_install_is_idempotent(tmp_path):
    path, record = archive(tmp_path, "data/tiles/a.npz")
    root = tmp_path / "installed"
    assert MODULE.extract_verified(path, root, record) == 1
    assert MODULE.extract_verified(path, root, record) == 1
    target = root / "data/tiles/a.npz"
    target.write_bytes(b"my changes")
    with pytest.raises(FileExistsError):
        MODULE.extract_verified(path, root, record)
    assert target.read_bytes() == b"my changes"


@pytest.mark.parametrize("filename", ["ortho.png", "model_mask.npz", "osm_mask.png", "llm_mask.png"])
def test_context_assets_are_installed_with_city_and_tile_directories(tmp_path, filename):
    member = f"data/assets/city/tile/{filename}"
    path, record = archive(tmp_path, member)
    root = tmp_path / "installed"
    assert MODULE.extract_verified(path, root, record) == 1
    assert (root / member).read_bytes() == b"contents"


@pytest.mark.parametrize("member", ["data/assets/city/ortho.png", "data/assets/city/tile/script.py", "data/manifest.json"])
def test_unexpected_context_layout_is_rejected(tmp_path, member):
    path, record = archive(tmp_path, member)
    with pytest.raises(ValueError, match="Unexpected data"):
        MODULE.extract_verified(path, tmp_path / "installed", record)
