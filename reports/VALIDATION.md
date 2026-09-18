# Export validation record

The results below were recorded during preparation of the standalone model
and data export. They describe the environment and checks at that stage.

Validation was executed on Windows with Python 3.10.11, NumPy 2.2.6 and PyTorch
2.5.1+cu121. Both CPU inference and CUDA inference were exercised. The validation
environment reused the installed numerical dependencies; this was not a fresh
download of every dependency on Linux or macOS.

| Check | Result |
| --- | --- |
| Standalone test suite | **38 passed** |
| Original network copy | Byte-for-byte match; SHA-256 `603f97006e798a22fbe92421ab0d00adb27b7a71d67c668ad38369c7968df0c7` |
| E0–E3 checkpoint loading | All four exported state dictionaries loaded strictly |
| Input feature parity | Bitwise identical to original code for all four variants on two windows of a real benchmark tile |
| Full-tile E3 inference parity | **55,961 / 55,961 predictions identical**, 256 windows, `tile_x1_y1`, CUDA |
| Frozen ablation input parity | E0, E1 and E2 input fields equal their E3 counterparts on all 141 train/validation tiles |
| Sample integrity | All 30 tiles and 215 payload files verified: SHA-256 hashes, array schemas, city selection, reference-label counts and disjoint splits; 2,177,510 occupied voxels |
| Context completeness | Each tile has ortho, numerical model mask, original OSM and LLM masks, and a model overlay; 5 original model PNGs also retained |
| Numeric mask parity | All 30 standalone model masks equal the prepared input's `ortho`, occupancy and grid metadata exactly |
| Selection-only change | All 30 dense/sparse file hashes match their entries in the previous full export; all four weight files remain unchanged |
| Frozen/current label consistency | No geometry or reference-label changes in the 141 frozen training/validation snapshots |
| Python package build/install | Wheel built and installed successfully into a separate local virtual environment |
| Earlier full-export relocation | The previous 175-tile numerical export passed relocation and installed-runtime validation before being replaced by this sample |
| Sample relocation | Copied source without binary payload, installed the model and sample ZIPs with the public downloader, then verified all 30 tiles / 215 files using the installed wheel |
| Sample inference after relocation | E3 CUDA evaluation on one real Los Angeles tile scored 40,544 voxels and correctly reported a partial benchmark (1 evaluated / 10 released / 25 original test tiles) |
| Portable metadata | No local Windows/WSL absolute paths in release documentation or metadata |
| Source workspace | `workspace.json` SHA-256 unchanged after export |

The unit tests cover boundary-window coverage, input schema rejection, channel
ordering and weights, gray-world behavior, reference-label independence, empty
cell feature values, metric convention, archive traversal rejection, corrupt
archive rejection, and refusal to overwrite changed files. Sample-specific tests
cover missing context sources, changed image bytes, city quotas, fixed city/tile
membership, exclusion of unselected payload files, nested asset extraction, and
marking sample evaluation as partial even when all released test tiles are used.

The release contains 3 tiles from each of nine cities, plus 2 from Tokyo and 1
from Rome. These are all the ready tiles available for the two shortfall cities.
The packaging command uses the explicit sample manifest and rejects unlisted
payload files, so the sample archive contains only the selected tiles.

Detailed parity evidence is in `upstream_parity.json` and
`ablation_input_parity.json`. Dataset and checkpoint provenance is in
`provenance.json`; ZIP hashes are in the root `artifacts.json`.
The final sample checks are recorded in `sample_validation.json`; the one-tile
evaluation smoke report is `sample_smoke.json`.

No models were retrained. The complete 25-tile benchmark was **not rerun** during
this packaging task; `E0_benchmark.json` through `E3_benchmark.json` preserve the
original experiment reports.
For the checked real tile, the current original pipeline and standalone runtime
both produce mIoU 0.501391 and accuracy 0.888011; the archived per-tile report
stores 0.5015 and 0.8881. The small historical difference has not been isolated.
Exact parity here means parity with the current original runtime, not a claim
that every historical benchmark metric has been reproduced.
