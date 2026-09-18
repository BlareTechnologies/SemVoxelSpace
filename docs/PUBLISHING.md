# Maintainer guide

Repository: [BlareTechnologies/SemVoxelSpace](https://github.com/BlareTechnologies/SemVoxelSpace).

A normal clone includes the code, all four pretrained models, and the 30-tile
sample with masks and orthorenders. The original labeler workspace is only
needed to rebuild an export, not to run inference or evaluate the sample.

## Verify a checkout

Install the runtime and test dependencies as described in [README.md](../README.md),
then run these commands from the repository root:

```bash
python -m pytest -q
python -m voxel_context verify
python -m voxel_context infer --model models/E3 --tile data/tiles/tile_x1_y1.npz --device cpu --output outputs/tile_x1_y1_prediction.npz
```

Keep [CITATION.cff](../CITATION.cff), [LICENSING.md](../LICENSING.md) and the
[experiment split description](EXPERIMENTS.md) consistent with the version
being published. Preserve the upstream notices and OpenStreetMap attribution.

## Publish repository updates

The existing checkout already has an `origin` remote and a `main` branch.
Stage the intended changes with `git add`, inspect them, then commit and push:

```bash
git diff --cached
git commit -m "Update VoxelContext3D"
git push origin main
```

The sample has 215 binary payload files totaling about 238 MiB. Each of the four
weight files is about 21.8 MiB. These files are tracked in ordinary Git; Git LFS
is not required for this layout. `dist/`, `.downloads/` and local `outputs/`
remain ignored.

## Optional ZIP releases

ZIP downloads are an alternative to cloning. A repository push does not create
a GitHub Release or upload these archives. Build the archives locally with:

```bash
python scripts/package_release.py
```

The command creates:

- `dist/voxel-context3d-models-v1.zip`: four weight files and their configurations.
- `dist/voxel-context3d-sample-v1.zip`: the 215 sample payload files.
- `artifacts.json`: archive sizes, file counts and SHA-256 hashes.

Packaging verifies every sample hash and rejects unlisted payload files.
Rebuild the archives whenever their binary contents or model configurations
change, and commit the matching `artifacts.json`.

To offer these downloads, create a GitHub Release for the intended version
(for example, tag `v1.0.0`) and attach both ZIPs. Link the release notes to
[LICENSING.md](../LICENSING.md) and [LICENSE-MODEL.md](../LICENSE-MODEL.md) so
archive users can find the applicable terms. `artifacts.json` describes the
archives; their availability depends on the corresponding GitHub Release.

After the release and attachments exist, the optional downloader can install
or verify them:

```bash
python scripts/download_assets.py --repo BlareTechnologies/SemVoxelSpace --tag v1.0.0
```

If publishing only the model ZIP, use `python scripts/package_release.py --kind models`
and commit the resulting index so it lists only the offered archive. All model
and sample files remain available through a normal clone.

The same downloader can check the locally built archives without a release:

```bash
python scripts/download_assets.py --from-dir dist
```

It validates checksums and sizes, rejects unsafe archive paths, and refuses to
overwrite files whose contents differ.

## Re-export from the original project

Use a new destination when rebuilding data from the original workspace:

```bash
python scripts/export_from_labeler.py --source-repo PATH_TO_GVDB_REPOSITORY --selection data/selection.json --output PATH_TO_NEW_EXPORT
```

This maintainer operation needs PyTorch, NumPy, Pillow, the original tools and
the local source artifacts. It exports only the IDs in `data/selection.json`
and preserves their recorded roles. It reads the source workspace without
changing it and refuses to download missing OSM features. Use `--resume` only
to continue an interrupted export into the same dedicated destination.

Verify a new export and rebuild its archive index before publishing it.
`scripts/compare_with_labeler.py` provides optional parity checks against the
original implementation.
