# Model card

The public data release is a 30-tile sample with context masks and orthorenders.
Training and benchmark counts below describe the original experiments, not the
sample payload. The full 25-tile benchmark cannot be rerun from this sample alone.

## Intended use and inputs

Research classifiers for per-occupied-voxel semantic labeling of urban geometry
at 0.5 m resolution. The eight output classes are background, buildings, roads,
water, barren, forests, grass/agriculture and metal. E3 is the full context model;
E0–E2 expose the controlled input ablations.

The model architecture is a residual 3D U-Net with three 2× downsampling steps,
group normalization and base width 32. The exact original implementation is in
`src/voxel_context/network.py`. E3 has 5,702,632 trainable parameters. Checkpoints
are tensor state dictionaries loaded with `weights_only=True` and strict key and
shape matching.

## Exact E3 channel order

| Zero-based index | Input |
| --- | --- |
| 0 | Occupancy |
| 1–3 | Gray-world-normalized RGB divided by 255 |
| 4–9 | Green chromaticity, excess green, green dominance, saturation, normalized green/red, normalized green/blue |
| 10–11 | Model building and forest masks, weight 0.5 |
| 12–14 | VLM metal, barren, grass/agriculture masks, weight 0.5 |
| 15–17 | OSM building, road, water context, weight 0.5 |

The conceptual E0→E3 addition order in the paper is not the final tensor order.
In particular, E2's OSM channels are at 12–14, while E3's OSM channels are at
15–17. Always use the model-specific `model.json`.

## Training provenance

| Variant | Source run | Selected epoch |
| --- | --- | ---: |
| E0 | `e3water_ladder_E0` | 39 |
| E1 | `e3water_ladder_E1` | 28 |
| E2 | `e3water_ladder_E2` | 20 |
| E3 | `20260621T164812_train_e3water` | 12 |

All four models use seed 1337. The recorded recipe uses AdamW, CE+Dice, mixed
precision, 40 epochs, batch size 4, a peak learning rate of 1e-4, a cosine schedule
with three warm-up epochs, random 32×32×64 windows, 96 samples per tile per epoch,
horizontal rotations/flips and per-tile gray-world normalization. The actual
split is 127 train / 14 validation, with 25 separate benchmark tiles in the
expanded evaluation. Full saved dataset summaries and epoch histories accompany
the models. No training was repeated during packaging.

## Inference and evaluation

The runtime normalizes the full tile, extracts windows at stride 8×8×64, pads
raw arrays at boundaries, and builds the feature stack. It sums class logits
over overlapping windows and applies argmax at occupied voxels. Labels never
enter the input features or fill prediction gaps. An uncovered occupied voxel
causes an error.

Reported E3 benchmark values are accuracy 0.8954, mIoU 0.6266 and foreground mIoU
0.7162 over 1,539,265 occupied voxels. These are the archived experiment results.
The software's release tests and any freshly run evaluation are recorded
separately, so a smoke test is never presented as a full benchmark reproduction.

## Limits

The corpus is small and class-imbalanced, and the enlarged benchmark results use
one fixed seed. The photogrammetric geometry and auxiliary masks contain errors.
Models require consistent voxel scale, color treatment and aligned masks;
changing the source domain or omitting a required mask changes the task.

The release uses frozen numeric model/VLM/OSM masks and does not package or call
the original SegFormer or image-generation service. It provides model inference
and evaluation, not scene harvesting, interactive annotation or a training CLI.

The author-owned model weights and human annotations are licensed under
[CC BY 4.0](LICENSE-MODEL.md). See [LICENSING.md](LICENSING.md) for the licensing
scope of code, weights, annotations and scene data.
