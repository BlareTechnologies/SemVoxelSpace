# Source notices

The standalone feature and inference runtime was developed by Łukasz Błaszkowski.
The code is distributed under BSD-3-Clause; see `LICENSE` and the
component-specific scope in `LICENSING.md`.

The research pipeline used model-generated masks (SegFormer land-cover
classification), vision-language-generated masks, and OpenStreetMap context.
This package consumes frozen numeric masks; it does not redistribute those
source model weights, API tokens or raw map requests.

OSM attribution: © OpenStreetMap contributors,
https://www.openstreetmap.org/copyright.

Licensing scopes for the code, model weights, annotations and scene data are
described in `LICENSING.md`.
