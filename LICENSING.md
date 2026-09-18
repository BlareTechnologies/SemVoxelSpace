# Licensing

Different components of this repository have different licensing scopes.

| Component | License or applicable notice |
| --- | --- |
| Standalone Python code, maintainer scripts and tests | BSD-3-Clause; see [LICENSE](LICENSE) |
| Retained upstream network implementation | Original BSD terms and copyright notice in [UPSTREAM_LICENSE.txt](UPSTREAM_LICENSE.txt) |
| Author-owned trained model weights | CC BY 4.0; see [LICENSE-MODEL.md](LICENSE-MODEL.md) |
| Author-owned human semantic annotations (`labels` arrays) | CC BY 4.0; see [LICENSE-MODEL.md](LICENSE-MODEL.md) |
| Scene geometry, RGB values, raster images and other context data | Not covered by the code or model/annotation license grants; applicable source-data terms remain in effect |
| OpenStreetMap-derived context | © OpenStreetMap contributors; see the [OpenStreetMap copyright and license page](https://www.openstreetmap.org/copyright) |

## Scope of the data licenses

The NPZ files combine several kinds of data. The CC BY 4.0 grant for human
annotations covers the `labels` arrays only; it does not assign that license to
the geometry, RGB values or auxiliary masks stored alongside them.

The code license likewise does not relicense scene data or other third-party
materials. Retain the applicable attribution and notices when redistributing
components of the project.

Use [CITATION.cff](CITATION.cff) to cite the software. The attribution for the
model weights and human annotations is specified in
[LICENSE-MODEL.md](LICENSE-MODEL.md).
