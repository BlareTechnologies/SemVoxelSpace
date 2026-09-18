# VoxelContext3D

**Semantic classification of voxelized computational space using geometry, color,
model masks, OpenStreetMap context, and vision-language model masks.**

Companion project for *Semantic Classification of Voxelized Computational Space
for Simulation and Planning Tasks*.

Authors: **Ł. Błaszkowski, P. Borkiewicz, G. Hawrot, K. Cichoń (Senior Member, IEEE),
and P. Kulakowski**.

This project contains a standalone PyTorch inference runtime, four pretrained
E0–E3 classifiers, a **30-tile sample from 11 cities**, explicit sample splits,
original benchmark reports, and tools for building checksummed release archives.
The sample includes orthorenders and all three context-mask sources: model, OSM,
and VLM/LLM.
It runs without RadioVoxelEditor, the labeler server, Cesium, or API credentials.

## Quick start

The commands below use the tested Python 3.10 runtime with PyTorch 2.5.1.
The validation environment used Python 3.10.11 and NumPy 2.2.6. Clone the
repository and create a virtual environment:

```bash
git clone https://github.com/BlareTechnologies/SemVoxelSpace.git
cd SemVoxelSpace
python -m venv .venv
```

Activate the environment with `.venv\Scripts\Activate.ps1` in Windows PowerShell,
or `source .venv/bin/activate` on Linux/macOS. Install the CPU build first for a
portable example:

```bash
python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e .
```

For NVIDIA GPU inference, select a compatible CUDA build using the official
[PyTorch installation instructions](https://pytorch.org/get-started/locally/).
The local validation used PyTorch `2.5.1+cu121` on Windows. `--device auto` chooses
CUDA when available, otherwise CPU.

All four pretrained model weights, the 30-tile sample, masks and orthorenders
are tracked in Git and included when you clone the repository. After installing
the Python dependencies above, you can run inference immediately.

Run inference on the included Bydgoszcz test tile on CPU:

```bash
python -m voxel_context infer --model models/E3 --tile data/tiles/tile_x1_y1.npz --device cpu --output outputs/tile_x1_y1_prediction.npz --ply outputs/tile_x1_y1_prediction.ply
```

The command processes one complete tile and saves the predictions as NPZ and a
class-colored PLY point cloud. Open the PLY in a point-cloud viewer, or read the
NPZ with `numpy.load(..., allow_pickle=False)`. Reported metrics describe this
single tile, not the full paper benchmark. Use `--tile` to select another prepared
input from `data/tiles/`.

## Data and evaluation

The release contains **3 manually verified tiles per city**, with two explicit
availability exceptions: **Tokyo has 2 and Rome has 1**. Berlin, Bydgoszcz, London,
Los Angeles, Maceió, Manchester, New York, Paris, and Stockholm each have 3.
The sample has 16 training, 1 validation, 10 test, and 3 additional tiles, retaining
their original roles. Browse [the sample index](data/SAMPLES.md) for every tile
and its files. This is a demonstration subset, not the complete training corpus
or complete paper benchmark.

Each tile has prepared model inputs, saved human annotations, an orthorender,
the exact numerical model mask, original OSM and LLM mask PNGs, and the original
model overlay. Original model-mask PNGs are also included where retained. See
[the format and provenance notes](docs/DATASET.md).

For reference, the **original 175-tile corpus** had the following membership;
these full-corpus counts do not describe the payload of this release:

| Subset | Tiles | Occupied reference voxels | Role |
| --- | ---: | ---: | --- |
| Training | 127 | 10,052,339 | Used by the released models |
| Validation | 14 | 934,727 | Checkpoint selection |
| Test | 25 | 1,539,265 | Expanded held-out benchmark |
| Additional | 9 | 581,828 | Later New York annotations, not used by these models |
| **Total** | **175** | **13,108,159** | All ready labeler tiles |

The saved runs used **141 = 127 + 14** training and validation tiles. The
150 tiles outside the test set also include 9 additional annotations that were
not used by these models. The released sample retains the original membership
of its selected tiles. See [the experiment splits](docs/EXPERIMENTS.md) for
the recorded memberships and the scope of sample-only evaluation.

The sample is already present after cloning. Verify all arrays and context files,
then evaluate E3 on the **10 released test tiles**:

```bash
python -m voxel_context verify
python -m voxel_context evaluate --model models/E3 --device auto --output outputs/E3_sample_benchmark.json
```

Use `--limit 1` for an evaluation smoke run. The output records whether it is a
partial benchmark. Even evaluation of every released test tile remains a partial
paper benchmark; its score should not be compared directly with the full 25-tile
metrics below.

## Models

The models are residual 3D U-Nets with base width 32, group normalization, and
32 × 32 × 64-voxel windows at 0.5 m voxel resolution. E3 has **5,702,632 parameters**.

| Model | Inputs | Channels | Reported test mIoU | Reported FG mIoU |
| --- | --- | ---: | ---: | ---: |
| E0 | Occupancy, RGB, six color features | 10 | 0.3237 | 0.3700 |
| E1 | E0 + building/forest model masks | 12 | 0.4639 | 0.5302 |
| E2 | E1 + OSM building/road/water masks | 15 | 0.5585 | 0.6383 |
| E3 | E2 + VLM metal/barren/grass masks | 18 | 0.6266 | 0.7162 |

These numbers are copied from the original 25-tile benchmark reports, not newly
trained results. Model weights are exported exactly from the selected checkpoints;
optimizer state is omitted. Each model configuration specifies the precise input
channel order, normalization, chunk shape, stride, seed, and selected epoch.

E0 can classify geometry with color. E1–E3 additionally require their respective
mask inputs. This runtime consumes the **frozen, prepared arrays**; it does not
download map tiles or generate VLM masks. See [MODEL_CARD.md](MODEL_CARD.md) and
[the input schema](docs/DATASET.md) before preparing your own tiles.

## Repository layout

```text
src/voxel_context/       Standalone network, feature builder, inference and CLI
models/E0 ... E3/        Model configurations and pretrained weights; tracked in Git
data/selection.json      Fixed city-balanced sample selection and exceptions
data/splits.json         Original roles of the selected sample IDs only
data/manifest.json       Per-tile provenance, counts and checksums
data/tiles/              Prepared dense inputs; tracked in Git
data/labeler/            Original sparse geometry and saved human labels
data/assets/<city>/<id>/ Ortho, model mask, OSM mask, LLM mask and model overlay
data/SAMPLES.md          Browse all 30 examples and their context files
reports/                Original metrics, training metadata and export validation
scripts/                Download, packaging and maintainer export commands
tests/                  Input, coverage, prediction and archive integrity tests
docs/                   Data contract, experiment splits and maintainer guide
```

Model weights and all sample arrays and images are tracked in Git. Each weight
file is about 21.8 MiB; the four weights total about 87 MiB. The `dist/` folder and
local outputs remain ignored. Maintainers can build optional model and sample
ZIPs and attach them to a GitHub Release. `artifacts.json` records the expected
archive hashes; it does not indicate that a downloadable release exists.
Cloning the repository already provides the complete sample and all four models.
See [docs/PUBLISHING.md](docs/PUBLISHING.md) for validation and release packaging.

## Validation and scope

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

The release preserves a data sample, configurations, epoch histories and selected
weights. The standalone runtime implements **inference and evaluation**; a new
end-to-end training implementation is not included. The complete training set and
complete benchmark are not distributed. Frozen dense arrays for the selected
training examples and the input contract are available for follow-up work.

The original network implementation is retained byte-for-byte. Release validation
compares the independent feature builder and full-tile predictions against the
labeler implementation; details are recorded in [reports/VALIDATION.md](reports/VALIDATION.md).

## Citation and licensing

Use [CITATION.cff](CITATION.cff) to cite this software.

The code is licensed under [BSD-3-Clause](LICENSE). Author-owned model weights
and human semantic annotations are licensed under [CC BY 4.0](LICENSE-MODEL.md).
These grants have separate scopes; see [LICENSING.md](LICENSING.md) for details
about the components bundled in this repository. Existing upstream notices are
retained in [UPSTREAM_LICENSE.txt](UPSTREAM_LICENSE.txt) and [NOTICE.md](NOTICE.md).
