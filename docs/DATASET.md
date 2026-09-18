# Dataset contract

## Selection and provenance

The export is a **30-tile sample** of the original 175 manually verified tiles.
It contains 3 tiles from each of Berlin, Bydgoszcz, London, Los Angeles, Maceió,
Manchester, New York, Paris, and Stockholm, plus all available ready examples
from Tokyo (2) and Rome (1). No unverified tiles or duplicate copies are used to
fill these shortfalls. See `data/selection.json` and [the index](../data/SAMPLES.md).

Selection uses natural tile X/Y order and round-robin across acquisition areas,
without using model accuracy. `qualitytest2`, `maciejo`, and `maciejo2` are grouped
as Maceió: their capture bounds are areas of the same city, not three cities.
Only cities represented in the original 175-tile corpus are included.

Every selected tile has effective labeler status `ready`.
Effective status comes from `states/<id>.json`, with the workspace
manifest as fallback. Every selected tile has a saved `states/<id>.npz` label
array. New, in-progress, deleted and review-only tiles are not included.

`data/manifest.json` records every tile ID, split, existing region tags, voxel
count, local array shape and SHA-256 hashes of the original geometry, original
saved labels, and exported representations. Original capture IDs are preserved
as opaque identifiers. Some IDs contain `19700101`; they are identifiers, not
reliable acquisition dates.

No user-account records, authentication data, local absolute paths, API keys or
harvest request URLs are needed by the public runtime. The release does not
include the original labeler workspace JSON or source meshes. It includes the
original orthorender **only for each selected sample tile**.

## Context files: `data/assets/<city>/<id>/`

Every tile includes the following files, with checksums in `data/manifest.json`:

| File | Contents |
| --- | --- |
| `ortho.png` | Original orthographic RGB/RGBA render, normally 2048 × 2048 |
| `model_mask.npz` | Exact `ortho` class-ID volume from the prepared model input, plus occupancy and grid metadata |
| `osm_mask.png` | Original OSM semantic mask in the fixed class palette |
| `llm_mask.png` | Original VLM/LLM semantic mask in the fixed class palette |
| `model_overlay.png` | Original model-overlay visualization; do not decode it as class IDs |
| `model_mask_raster.png` | Original model prediction PNG, included only where it was retained |

The model mask is complete for **every tile** in NPZ form. Some source model PNGs
were not retained in the workspace, so the release does not fabricate replacements
or present blended overlays as class masks. In `model_mask.npz`, `labels` is the
model's auxiliary class map, **not the human reference**; it equals the prepared
input's `ortho` array exactly. Arrays use Z,Y,X order. `occ`, `origin`, and
`voxel_size` define the occupied cells and the same grid as the input tile.

All PNG files are copied byte-for-byte. OSM images can be 1024 × 1024 while
orthorenders and LLM masks are 2048 × 2048; no resizing is applied. Each file's
native dimensions are recorded. `raster_bounds_xy` records the source tile extent:
image columns increase with X, rows increase toward decreasing Y. For voxel-center
coordinates `(x,y)`, the original sampling uses
`u=(x-minX)/(maxX-minX)`, `v=(maxY-y)/(maxY-minY)`, then rounded pixel indices
`u*(width-1)`, `v*(height-1)`, clamped to the image. The overlay is for inspection
only and can have a different size. Prepared arrays are authoritative for
reproducing the released model inputs; current source images and historical
training snapshots are not assumed to be interchangeable.

## Prepared model inputs: `data/tiles/<id>.npz`

All files are compressed NumPy archives without Python objects. Load with
`np.load(path, allow_pickle=False)`. Spatial array order is **Z, Y, X**; channel
dimensions come last. The dataset grid resolution is 0.5 m.

| Array | Dtype / shape | Meaning |
| --- | --- | --- |
| `occ` | `uint8 [Z,Y,X]` | Binary occupied-voxel mask |
| `rgb` | `uint8 [Z,Y,X,3]` | RGB before gray-world normalization |
| `ortho` | `uint8 [Z,Y,X]` | Land-cover-model class IDs |
| `llm_ortho` | `uint8 [Z,Y,X]` | Frozen VLM class IDs |
| `osm_context` | `uint8 [Z,Y,X,3]` | Binary building, road, water channels, in this order |
| `labels` | `uint8 [Z,Y,X]` | Human reference class IDs; used only for evaluation |
| `origin` | `float32 [3]` | Tile-local grid origin in the original scene frame |
| `voxel_size` | `float32 [1]` | Grid spacing in meters |
| `tile_id` | Unicode `[1]` | Stable identifier |

The training and validation files preserve the arrays frozen for E3 training.
E0–E2 use the appropriate subset of the same input fields; the source snapshots
are compared in `reports/ablation_input_parity.json`. The unused `vehicle_prior`
array is omitted, because none of these four models consumes it.

Test and additional files are built from the current saved labeler arrays and
frozen masks. When a precomputed OSM mask is absent, the maintainer exporter can
rasterize an already cached OSM feature collection. It refuses missing caches
instead of fetching data. One test tile uses this cached-feature path; dense OSM
context may occupy empty cells as well, and the full context is preserved.

Gray-world normalization uses all occupied voxels in a tile before windowing.
Do not normalize RGB separately in each window. Empty RGB cells are zero; some
derived color features of zero RGB are 0.5. The runtime therefore pads the raw
window **before** constructing features.

The optional `rgb_is_normalized = True` flag is supported only for arrays that
have already received full-tile gray-world normalization; normal dataset tiles
omit it.

## Saved annotations: `data/labeler/<id>.npz`

This representation retains the original sparse voxel order:

| Array | Meaning |
| --- | --- |
| `indices: int32 [N,3]` | Original voxel indices in X,Y,Z order |
| `rgb: uint8 [N,3]` | Original voxel colors |
| `labels: uint8 [N]` | Actual saved human reference labels |
| `ortho_labels`, `llm_ortho_labels`, `osm_ortho_labels` | Auxiliary class IDs aligned to the same sparse order |
| `origin`, `tile_origin: float32 [3]` | Offsets in the original scene coordinate frame |
| `voxel_size: float32 [1]` | Grid spacing in meters |

Voxel centers are `tile_origin + origin + (indices + 0.5) * voxel_size`.
An auxiliary label array of zeros does not imply that the corresponding prepared
context is absent: OSM context may have been rasterized from cached features.

For this export, all frozen training/validation geometries and reference labels
match the current labeler state. Counts in `reports/provenance.json` make this
check explicit. The original input and reference labels are stored separately
from model predictions.

## Classes and splits

| ID | Class |
| ---: | --- |
| 0 | background |
| 1 | buildings |
| 2 | roads |
| 3 | water |
| 4 | barren |
| 5 | forests |
| 6 | grass / agriculture |
| 7 | metal |

The canonical colors are in `data/classes.json`. `data/splits.json` is the source
of truth for the **released sample**: train (16), validation (1), test (10), and
additional (3) are disjoint. The original corpus counts (127/14/25/9) are retained
in `reports/provenance.json` under `source_corpus` and in the experiment reports.
Do not recalculate the split from sorted IDs or treat
the additional set as part of the released checkpoint's training history.

The released test sample contains 3 Bydgoszcz, 3 Los Angeles, 3 Manchester and
1 Rome tiles. The full benchmark used 13, 6, 5 and 1, respectively. Sample-only
evaluation cannot reproduce the full benchmark score.
Full-tile predictions are scored only on occupied voxels. Absent classes have
zero IoU, and the eight-class mean includes background; foreground mIoU averages
classes 1–7.

## Preparing a new tile

Voxelize your geometry at 0.5 m, place RGB and occupancy into a local Z,Y,X grid,
and save `origin` and `voxel_size`. These four fields suffice for E0. For E1, also
provide model-mask class IDs in `ortho`; for E2, add `osm_context`; for E3, add
`llm_ortho`. Use the same class IDs and spatial alignment. `labels` is optional
for inference. The runtime reports missing required inputs as errors.

This repository does not regenerate orthorenders or source masks. It supplies
their prepared numeric representations for the released data and describes the
input contract for separately licensed source scenes.

Dataset redistribution status is explained in [../LICENSING.md](../LICENSING.md).
