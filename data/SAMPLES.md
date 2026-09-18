# Released data sample

The sample files are included in the repository; these links work after cloning.
Each example has a dense input, sparse human annotations, ortho, model mask, OSM mask and LLM mask.
Model masks are complete numeric NPZ volumes; PNG source masks are included where retained.

| City | Released tiles | Available ready tiles in the source corpus |
| --- | ---: | ---: |
| Berlin | 3 | 8 |
| Bydgoszcz | 3 | 13 |
| London | 3 | 7 |
| Los Angeles | 3 | 6 |
| MaceiÃ³ | 3 | 92 |
| Manchester | 3 | 5 |
| New York | 3 | 9 |
| Paris | 3 | 25 |
| Rome | 1 | 1 |
| Stockholm | 3 | 7 |
| Tokyo | 2 | 2 |

Availability exceptions: Rome (1), Tokyo (2).
Target: 3 tiles per city. Released: 30 tiles and 2,177,510 occupied voxels.
Splits retain their original role. These examples do not comprise the full paper benchmark.

## Berlin

- **`aoi_19700101T000203Z__tile_x1_y4`** — train, 83,379 voxels.  
  [Input NPZ](tiles/aoi_19700101T000203Z__tile_x1_y4.npz) · [Human labels](labeler/aoi_19700101T000203Z__tile_x1_y4.npz) · [Ortho](assets/berlin/aoi_19700101T000203Z__tile_x1_y4/ortho.png) · [Model mask](assets/berlin/aoi_19700101T000203Z__tile_x1_y4/model_mask.npz) · [OSM mask](assets/berlin/aoi_19700101T000203Z__tile_x1_y4/osm_mask.png) · [LLM mask](assets/berlin/aoi_19700101T000203Z__tile_x1_y4/llm_mask.png) · [Model overlay](assets/berlin/aoi_19700101T000203Z__tile_x1_y4/model_overlay.png)
- **`aoi_19700101T000203Z__tile_x3_y3`** — train, 93,529 voxels.  
  [Input NPZ](tiles/aoi_19700101T000203Z__tile_x3_y3.npz) · [Human labels](labeler/aoi_19700101T000203Z__tile_x3_y3.npz) · [Ortho](assets/berlin/aoi_19700101T000203Z__tile_x3_y3/ortho.png) · [Model mask](assets/berlin/aoi_19700101T000203Z__tile_x3_y3/model_mask.npz) · [OSM mask](assets/berlin/aoi_19700101T000203Z__tile_x3_y3/osm_mask.png) · [LLM mask](assets/berlin/aoi_19700101T000203Z__tile_x3_y3/llm_mask.png) · [Model overlay](assets/berlin/aoi_19700101T000203Z__tile_x3_y3/model_overlay.png)
- **`aoi_19700101T000203Z__tile_x4_y3`** — train, 75,240 voxels.  
  [Input NPZ](tiles/aoi_19700101T000203Z__tile_x4_y3.npz) · [Human labels](labeler/aoi_19700101T000203Z__tile_x4_y3.npz) · [Ortho](assets/berlin/aoi_19700101T000203Z__tile_x4_y3/ortho.png) · [Model mask](assets/berlin/aoi_19700101T000203Z__tile_x4_y3/model_mask.npz) · [OSM mask](assets/berlin/aoi_19700101T000203Z__tile_x4_y3/osm_mask.png) · [LLM mask](assets/berlin/aoi_19700101T000203Z__tile_x4_y3/llm_mask.png) · [Model overlay](assets/berlin/aoi_19700101T000203Z__tile_x4_y3/model_overlay.png)

## Bydgoszcz

- **`tile_x1_y1`** — test, 55,961 voxels.  
  [Input NPZ](tiles/tile_x1_y1.npz) · [Human labels](labeler/tile_x1_y1.npz) · [Ortho](assets/bydgoszcz/tile_x1_y1/ortho.png) · [Model mask](assets/bydgoszcz/tile_x1_y1/model_mask.npz) · [OSM mask](assets/bydgoszcz/tile_x1_y1/osm_mask.png) · [LLM mask](assets/bydgoszcz/tile_x1_y1/llm_mask.png) · [Model overlay](assets/bydgoszcz/tile_x1_y1/model_overlay.png) · [Original model PNG](assets/bydgoszcz/tile_x1_y1/model_mask_raster.png)
- **`tile_x2_y1`** — test, 64,882 voxels.  
  [Input NPZ](tiles/tile_x2_y1.npz) · [Human labels](labeler/tile_x2_y1.npz) · [Ortho](assets/bydgoszcz/tile_x2_y1/ortho.png) · [Model mask](assets/bydgoszcz/tile_x2_y1/model_mask.npz) · [OSM mask](assets/bydgoszcz/tile_x2_y1/osm_mask.png) · [LLM mask](assets/bydgoszcz/tile_x2_y1/llm_mask.png) · [Model overlay](assets/bydgoszcz/tile_x2_y1/model_overlay.png) · [Original model PNG](assets/bydgoszcz/tile_x2_y1/model_mask_raster.png)
- **`tile_x3_y1`** — test, 69,561 voxels.  
  [Input NPZ](tiles/tile_x3_y1.npz) · [Human labels](labeler/tile_x3_y1.npz) · [Ortho](assets/bydgoszcz/tile_x3_y1/ortho.png) · [Model mask](assets/bydgoszcz/tile_x3_y1/model_mask.npz) · [OSM mask](assets/bydgoszcz/tile_x3_y1/osm_mask.png) · [LLM mask](assets/bydgoszcz/tile_x3_y1/llm_mask.png) · [Model overlay](assets/bydgoszcz/tile_x3_y1/model_overlay.png) · [Original model PNG](assets/bydgoszcz/tile_x3_y1/model_mask_raster.png)

## London

- **`aoi_19700101T000404Z__tile_x2_y1`** — train, 98,637 voxels.  
  [Input NPZ](tiles/aoi_19700101T000404Z__tile_x2_y1.npz) · [Human labels](labeler/aoi_19700101T000404Z__tile_x2_y1.npz) · [Ortho](assets/london/aoi_19700101T000404Z__tile_x2_y1/ortho.png) · [Model mask](assets/london/aoi_19700101T000404Z__tile_x2_y1/model_mask.npz) · [OSM mask](assets/london/aoi_19700101T000404Z__tile_x2_y1/osm_mask.png) · [LLM mask](assets/london/aoi_19700101T000404Z__tile_x2_y1/llm_mask.png) · [Model overlay](assets/london/aoi_19700101T000404Z__tile_x2_y1/model_overlay.png)
- **`aoi_19700101T000404Z__tile_x2_y2`** — train, 74,473 voxels.  
  [Input NPZ](tiles/aoi_19700101T000404Z__tile_x2_y2.npz) · [Human labels](labeler/aoi_19700101T000404Z__tile_x2_y2.npz) · [Ortho](assets/london/aoi_19700101T000404Z__tile_x2_y2/ortho.png) · [Model mask](assets/london/aoi_19700101T000404Z__tile_x2_y2/model_mask.npz) · [OSM mask](assets/london/aoi_19700101T000404Z__tile_x2_y2/osm_mask.png) · [LLM mask](assets/london/aoi_19700101T000404Z__tile_x2_y2/llm_mask.png) · [Model overlay](assets/london/aoi_19700101T000404Z__tile_x2_y2/model_overlay.png)
- **`aoi_19700101T000404Z__tile_x2_y3`** — train, 60,080 voxels.  
  [Input NPZ](tiles/aoi_19700101T000404Z__tile_x2_y3.npz) · [Human labels](labeler/aoi_19700101T000404Z__tile_x2_y3.npz) · [Ortho](assets/london/aoi_19700101T000404Z__tile_x2_y3/ortho.png) · [Model mask](assets/london/aoi_19700101T000404Z__tile_x2_y3/model_mask.npz) · [OSM mask](assets/london/aoi_19700101T000404Z__tile_x2_y3/osm_mask.png) · [LLM mask](assets/london/aoi_19700101T000404Z__tile_x2_y3/llm_mask.png) · [Model overlay](assets/london/aoi_19700101T000404Z__tile_x2_y3/model_overlay.png)

## Los Angeles

- **`aoi_19700101T000043Z__tile_x1_y3`** — test, 40,544 voxels.  
  [Input NPZ](tiles/aoi_19700101T000043Z__tile_x1_y3.npz) · [Human labels](labeler/aoi_19700101T000043Z__tile_x1_y3.npz) · [Ortho](assets/los-angeles/aoi_19700101T000043Z__tile_x1_y3/ortho.png) · [Model mask](assets/los-angeles/aoi_19700101T000043Z__tile_x1_y3/model_mask.npz) · [OSM mask](assets/los-angeles/aoi_19700101T000043Z__tile_x1_y3/osm_mask.png) · [LLM mask](assets/los-angeles/aoi_19700101T000043Z__tile_x1_y3/llm_mask.png) · [Model overlay](assets/los-angeles/aoi_19700101T000043Z__tile_x1_y3/model_overlay.png)
- **`aoi_19700101T000043Z__tile_x2_y2`** — test, 45,188 voxels.  
  [Input NPZ](tiles/aoi_19700101T000043Z__tile_x2_y2.npz) · [Human labels](labeler/aoi_19700101T000043Z__tile_x2_y2.npz) · [Ortho](assets/los-angeles/aoi_19700101T000043Z__tile_x2_y2/ortho.png) · [Model mask](assets/los-angeles/aoi_19700101T000043Z__tile_x2_y2/model_mask.npz) · [OSM mask](assets/los-angeles/aoi_19700101T000043Z__tile_x2_y2/osm_mask.png) · [LLM mask](assets/los-angeles/aoi_19700101T000043Z__tile_x2_y2/llm_mask.png) · [Model overlay](assets/los-angeles/aoi_19700101T000043Z__tile_x2_y2/model_overlay.png)
- **`aoi_19700101T000043Z__tile_x3_y1`** — test, 44,772 voxels.  
  [Input NPZ](tiles/aoi_19700101T000043Z__tile_x3_y1.npz) · [Human labels](labeler/aoi_19700101T000043Z__tile_x3_y1.npz) · [Ortho](assets/los-angeles/aoi_19700101T000043Z__tile_x3_y1/ortho.png) · [Model mask](assets/los-angeles/aoi_19700101T000043Z__tile_x3_y1/model_mask.npz) · [OSM mask](assets/los-angeles/aoi_19700101T000043Z__tile_x3_y1/osm_mask.png) · [LLM mask](assets/los-angeles/aoi_19700101T000043Z__tile_x3_y1/llm_mask.png) · [Model overlay](assets/los-angeles/aoi_19700101T000043Z__tile_x3_y1/model_overlay.png)

## MaceiÃ³

- **`aoi_19700101T000138Z__tile_x2_y2`** — train, 63,381 voxels.  
  [Input NPZ](tiles/aoi_19700101T000138Z__tile_x2_y2.npz) · [Human labels](labeler/aoi_19700101T000138Z__tile_x2_y2.npz) · [Ortho](assets/maceio/aoi_19700101T000138Z__tile_x2_y2/ortho.png) · [Model mask](assets/maceio/aoi_19700101T000138Z__tile_x2_y2/model_mask.npz) · [OSM mask](assets/maceio/aoi_19700101T000138Z__tile_x2_y2/osm_mask.png) · [LLM mask](assets/maceio/aoi_19700101T000138Z__tile_x2_y2/llm_mask.png) · [Model overlay](assets/maceio/aoi_19700101T000138Z__tile_x2_y2/model_overlay.png)
- **`aoi_20260331T161435Z__tile_x1_y1`** — train, 51,514 voxels.  
  [Input NPZ](tiles/aoi_20260331T161435Z__tile_x1_y1.npz) · [Human labels](labeler/aoi_20260331T161435Z__tile_x1_y1.npz) · [Ortho](assets/maceio/aoi_20260331T161435Z__tile_x1_y1/ortho.png) · [Model mask](assets/maceio/aoi_20260331T161435Z__tile_x1_y1/model_mask.npz) · [OSM mask](assets/maceio/aoi_20260331T161435Z__tile_x1_y1/osm_mask.png) · [LLM mask](assets/maceio/aoi_20260331T161435Z__tile_x1_y1/llm_mask.png) · [Model overlay](assets/maceio/aoi_20260331T161435Z__tile_x1_y1/model_overlay.png) · [Original model PNG](assets/maceio/aoi_20260331T161435Z__tile_x1_y1/model_mask_raster.png)
- **`aoi_20260403T100225Z__tile_x1_y1`** — validation, 42,667 voxels.  
  [Input NPZ](tiles/aoi_20260403T100225Z__tile_x1_y1.npz) · [Human labels](labeler/aoi_20260403T100225Z__tile_x1_y1.npz) · [Ortho](assets/maceio/aoi_20260403T100225Z__tile_x1_y1/ortho.png) · [Model mask](assets/maceio/aoi_20260403T100225Z__tile_x1_y1/model_mask.npz) · [OSM mask](assets/maceio/aoi_20260403T100225Z__tile_x1_y1/osm_mask.png) · [LLM mask](assets/maceio/aoi_20260403T100225Z__tile_x1_y1/llm_mask.png) · [Model overlay](assets/maceio/aoi_20260403T100225Z__tile_x1_y1/model_overlay.png) · [Original model PNG](assets/maceio/aoi_20260403T100225Z__tile_x1_y1/model_mask_raster.png)

## Manchester

- **`aoi_19700101T000338Z__tile_x2_y1`** — test, 81,266 voxels.  
  [Input NPZ](tiles/aoi_19700101T000338Z__tile_x2_y1.npz) · [Human labels](labeler/aoi_19700101T000338Z__tile_x2_y1.npz) · [Ortho](assets/manchester/aoi_19700101T000338Z__tile_x2_y1/ortho.png) · [Model mask](assets/manchester/aoi_19700101T000338Z__tile_x2_y1/model_mask.npz) · [OSM mask](assets/manchester/aoi_19700101T000338Z__tile_x2_y1/osm_mask.png) · [LLM mask](assets/manchester/aoi_19700101T000338Z__tile_x2_y1/llm_mask.png) · [Model overlay](assets/manchester/aoi_19700101T000338Z__tile_x2_y1/model_overlay.png)
- **`aoi_19700101T000338Z__tile_x3_y1`** — test, 82,906 voxels.  
  [Input NPZ](tiles/aoi_19700101T000338Z__tile_x3_y1.npz) · [Human labels](labeler/aoi_19700101T000338Z__tile_x3_y1.npz) · [Ortho](assets/manchester/aoi_19700101T000338Z__tile_x3_y1/ortho.png) · [Model mask](assets/manchester/aoi_19700101T000338Z__tile_x3_y1/model_mask.npz) · [OSM mask](assets/manchester/aoi_19700101T000338Z__tile_x3_y1/osm_mask.png) · [LLM mask](assets/manchester/aoi_19700101T000338Z__tile_x3_y1/llm_mask.png) · [Model overlay](assets/manchester/aoi_19700101T000338Z__tile_x3_y1/model_overlay.png)
- **`aoi_19700101T000338Z__tile_x4_y1`** — test, 82,320 voxels.  
  [Input NPZ](tiles/aoi_19700101T000338Z__tile_x4_y1.npz) · [Human labels](labeler/aoi_19700101T000338Z__tile_x4_y1.npz) · [Ortho](assets/manchester/aoi_19700101T000338Z__tile_x4_y1/ortho.png) · [Model mask](assets/manchester/aoi_19700101T000338Z__tile_x4_y1/model_mask.npz) · [OSM mask](assets/manchester/aoi_19700101T000338Z__tile_x4_y1/osm_mask.png) · [LLM mask](assets/manchester/aoi_19700101T000338Z__tile_x4_y1/llm_mask.png) · [Model overlay](assets/manchester/aoi_19700101T000338Z__tile_x4_y1/model_overlay.png)

## New York

- **`aoi_19700101T000215Z__tile_x3_y8`** — additional, 75,502 voxels.  
  [Input NPZ](tiles/aoi_19700101T000215Z__tile_x3_y8.npz) · [Human labels](labeler/aoi_19700101T000215Z__tile_x3_y8.npz) · [Ortho](assets/new-york/aoi_19700101T000215Z__tile_x3_y8/ortho.png) · [Model mask](assets/new-york/aoi_19700101T000215Z__tile_x3_y8/model_mask.npz) · [OSM mask](assets/new-york/aoi_19700101T000215Z__tile_x3_y8/osm_mask.png) · [LLM mask](assets/new-york/aoi_19700101T000215Z__tile_x3_y8/llm_mask.png) · [Model overlay](assets/new-york/aoi_19700101T000215Z__tile_x3_y8/model_overlay.png)
- **`aoi_19700101T000215Z__tile_x3_y9`** — additional, 69,518 voxels.  
  [Input NPZ](tiles/aoi_19700101T000215Z__tile_x3_y9.npz) · [Human labels](labeler/aoi_19700101T000215Z__tile_x3_y9.npz) · [Ortho](assets/new-york/aoi_19700101T000215Z__tile_x3_y9/ortho.png) · [Model mask](assets/new-york/aoi_19700101T000215Z__tile_x3_y9/model_mask.npz) · [OSM mask](assets/new-york/aoi_19700101T000215Z__tile_x3_y9/osm_mask.png) · [LLM mask](assets/new-york/aoi_19700101T000215Z__tile_x3_y9/llm_mask.png) · [Model overlay](assets/new-york/aoi_19700101T000215Z__tile_x3_y9/model_overlay.png)
- **`aoi_19700101T000215Z__tile_x4_y9`** — additional, 67,147 voxels.  
  [Input NPZ](tiles/aoi_19700101T000215Z__tile_x4_y9.npz) · [Human labels](labeler/aoi_19700101T000215Z__tile_x4_y9.npz) · [Ortho](assets/new-york/aoi_19700101T000215Z__tile_x4_y9/ortho.png) · [Model mask](assets/new-york/aoi_19700101T000215Z__tile_x4_y9/model_mask.npz) · [OSM mask](assets/new-york/aoi_19700101T000215Z__tile_x4_y9/osm_mask.png) · [LLM mask](assets/new-york/aoi_19700101T000215Z__tile_x4_y9/llm_mask.png) · [Model overlay](assets/new-york/aoi_19700101T000215Z__tile_x4_y9/model_overlay.png)

## Paris

- **`aoi_19700101T000222Z__tile_x1_y3`** — train, 110,025 voxels.  
  [Input NPZ](tiles/aoi_19700101T000222Z__tile_x1_y3.npz) · [Human labels](labeler/aoi_19700101T000222Z__tile_x1_y3.npz) · [Ortho](assets/paris/aoi_19700101T000222Z__tile_x1_y3/ortho.png) · [Model mask](assets/paris/aoi_19700101T000222Z__tile_x1_y3/model_mask.npz) · [OSM mask](assets/paris/aoi_19700101T000222Z__tile_x1_y3/osm_mask.png) · [LLM mask](assets/paris/aoi_19700101T000222Z__tile_x1_y3/llm_mask.png) · [Model overlay](assets/paris/aoi_19700101T000222Z__tile_x1_y3/model_overlay.png)
- **`aoi_19700101T000222Z__tile_x1_y6`** — train, 94,814 voxels.  
  [Input NPZ](tiles/aoi_19700101T000222Z__tile_x1_y6.npz) · [Human labels](labeler/aoi_19700101T000222Z__tile_x1_y6.npz) · [Ortho](assets/paris/aoi_19700101T000222Z__tile_x1_y6/ortho.png) · [Model mask](assets/paris/aoi_19700101T000222Z__tile_x1_y6/model_mask.npz) · [OSM mask](assets/paris/aoi_19700101T000222Z__tile_x1_y6/osm_mask.png) · [LLM mask](assets/paris/aoi_19700101T000222Z__tile_x1_y6/llm_mask.png) · [Model overlay](assets/paris/aoi_19700101T000222Z__tile_x1_y6/model_overlay.png)
- **`aoi_19700101T000222Z__tile_x2_y3`** — train, 87,179 voxels.  
  [Input NPZ](tiles/aoi_19700101T000222Z__tile_x2_y3.npz) · [Human labels](labeler/aoi_19700101T000222Z__tile_x2_y3.npz) · [Ortho](assets/paris/aoi_19700101T000222Z__tile_x2_y3/ortho.png) · [Model mask](assets/paris/aoi_19700101T000222Z__tile_x2_y3/model_mask.npz) · [OSM mask](assets/paris/aoi_19700101T000222Z__tile_x2_y3/osm_mask.png) · [LLM mask](assets/paris/aoi_19700101T000222Z__tile_x2_y3/llm_mask.png) · [Model overlay](assets/paris/aoi_19700101T000222Z__tile_x2_y3/model_overlay.png)

## Rome

- **`aoi_19700101T000659Z__tile_x2_y5`** — test, 92,273 voxels.  
  [Input NPZ](tiles/aoi_19700101T000659Z__tile_x2_y5.npz) · [Human labels](labeler/aoi_19700101T000659Z__tile_x2_y5.npz) · [Ortho](assets/rome/aoi_19700101T000659Z__tile_x2_y5/ortho.png) · [Model mask](assets/rome/aoi_19700101T000659Z__tile_x2_y5/model_mask.npz) · [OSM mask](assets/rome/aoi_19700101T000659Z__tile_x2_y5/osm_mask.png) · [LLM mask](assets/rome/aoi_19700101T000659Z__tile_x2_y5/llm_mask.png) · [Model overlay](assets/rome/aoi_19700101T000659Z__tile_x2_y5/model_overlay.png)

## Stockholm

- **`aoi_19700101T000513Z__tile_x5_y6`** — train, 43,273 voxels.  
  [Input NPZ](tiles/aoi_19700101T000513Z__tile_x5_y6.npz) · [Human labels](labeler/aoi_19700101T000513Z__tile_x5_y6.npz) · [Ortho](assets/stockholm/aoi_19700101T000513Z__tile_x5_y6/ortho.png) · [Model mask](assets/stockholm/aoi_19700101T000513Z__tile_x5_y6/model_mask.npz) · [OSM mask](assets/stockholm/aoi_19700101T000513Z__tile_x5_y6/osm_mask.png) · [LLM mask](assets/stockholm/aoi_19700101T000513Z__tile_x5_y6/llm_mask.png) · [Model overlay](assets/stockholm/aoi_19700101T000513Z__tile_x5_y6/model_overlay.png)
- **`aoi_19700101T000513Z__tile_x6_y2`** — train, 70,043 voxels.  
  [Input NPZ](tiles/aoi_19700101T000513Z__tile_x6_y2.npz) · [Human labels](labeler/aoi_19700101T000513Z__tile_x6_y2.npz) · [Ortho](assets/stockholm/aoi_19700101T000513Z__tile_x6_y2/ortho.png) · [Model mask](assets/stockholm/aoi_19700101T000513Z__tile_x6_y2/model_mask.npz) · [OSM mask](assets/stockholm/aoi_19700101T000513Z__tile_x6_y2/osm_mask.png) · [LLM mask](assets/stockholm/aoi_19700101T000513Z__tile_x6_y2/llm_mask.png) · [Model overlay](assets/stockholm/aoi_19700101T000513Z__tile_x6_y2/model_overlay.png)
- **`aoi_19700101T000513Z__tile_x6_y6`** — train, 23,805 voxels.  
  [Input NPZ](tiles/aoi_19700101T000513Z__tile_x6_y6.npz) · [Human labels](labeler/aoi_19700101T000513Z__tile_x6_y6.npz) · [Ortho](assets/stockholm/aoi_19700101T000513Z__tile_x6_y6/ortho.png) · [Model mask](assets/stockholm/aoi_19700101T000513Z__tile_x6_y6/model_mask.npz) · [OSM mask](assets/stockholm/aoi_19700101T000513Z__tile_x6_y6/osm_mask.png) · [LLM mask](assets/stockholm/aoi_19700101T000513Z__tile_x6_y6/llm_mask.png) · [Model overlay](assets/stockholm/aoi_19700101T000513Z__tile_x6_y6/model_overlay.png)

## Tokyo

- **`aoi_19700101T000143Z__tile_x12_y4`** — train, 127,869 voxels.  
  [Input NPZ](tiles/aoi_19700101T000143Z__tile_x12_y4.npz) · [Human labels](labeler/aoi_19700101T000143Z__tile_x12_y4.npz) · [Ortho](assets/tokyo/aoi_19700101T000143Z__tile_x12_y4/ortho.png) · [Model mask](assets/tokyo/aoi_19700101T000143Z__tile_x12_y4/model_mask.npz) · [OSM mask](assets/tokyo/aoi_19700101T000143Z__tile_x12_y4/osm_mask.png) · [LLM mask](assets/tokyo/aoi_19700101T000143Z__tile_x12_y4/llm_mask.png) · [Model overlay](assets/tokyo/aoi_19700101T000143Z__tile_x12_y4/model_overlay.png)
- **`aoi_19700101T000143Z__tile_x23_y4`** — train, 105,762 voxels.  
  [Input NPZ](tiles/aoi_19700101T000143Z__tile_x23_y4.npz) · [Human labels](labeler/aoi_19700101T000143Z__tile_x23_y4.npz) · [Ortho](assets/tokyo/aoi_19700101T000143Z__tile_x23_y4/ortho.png) · [Model mask](assets/tokyo/aoi_19700101T000143Z__tile_x23_y4/model_mask.npz) · [OSM mask](assets/tokyo/aoi_19700101T000143Z__tile_x23_y4/osm_mask.png) · [LLM mask](assets/tokyo/aoi_19700101T000143Z__tile_x23_y4/llm_mask.png) · [Model overlay](assets/tokyo/aoi_19700101T000143Z__tile_x23_y4/model_overlay.png)

