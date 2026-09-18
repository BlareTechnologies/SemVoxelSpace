# Dataset splits and evaluation scope

The saved training manifests and benchmark reports define the membership of
the E0–E3 experiments. The original corpus and the sample distributed in this
repository have different sizes.

## Original experiments

| Subset | Tiles | Occupied reference voxels | Role |
| --- | ---: | ---: | --- |
| Training | 127 | 10,052,339 | Model training |
| Validation | 14 | 934,727 | Checkpoint selection |
| Test | 25 | 1,539,265 | Final benchmark |
| Additional | 9 | 581,828 | Available annotations not used in these model runs |
| **Total corpus** | **175** | **13,108,159** | All annotated source tiles |

All four models use the same 127 training and 14 validation tiles. The 25 final
test tiles are disjoint from both sets. The training and validation sets are
also disjoint. The saved memberships are in the [E0](../reports/E0_training_dataset.json),
[E1](../reports/E1_training_dataset.json), [E2](../reports/E2_training_dataset.json)
and [E3](../reports/E3_training_dataset.json) training reports.

The training and validation total is **141 tiles**, containing **10,987,066**
occupied reference voxels. The broader total of **150 non-test tiles** includes
the 9 additional New York annotations (tag `newyork8`); those 9 tiles were not
used for training or checkpoint selection. Full-corpus counts are recorded in
[provenance.json](../reports/provenance.json).

## Benchmark history

The training dataset manifests list 13 reserved benchmark IDs. The final
benchmark reports contain 25 IDs: the original 13 plus 6 Los Angeles,
5 Manchester and 1 Rome tiles. The final test set remains separate from the
saved training and validation sets.

The published model metrics come from these final 25-tile reports:
[E0](../reports/E0_benchmark.json), [E1](../reports/E1_benchmark.json),
[E2](../reports/E2_benchmark.json) and [E3](../reports/E3_benchmark.json).

## Sample included in this repository

The repository contains 30 selected tiles, retaining their original roles:

| Subset | Released tiles |
| --- | ---: |
| Training | 16 |
| Validation | 1 |
| Test | 10 |
| Additional | 3 |
| **Total sample** | **30** |

[data/splits.json](../data/splits.json) defines these memberships, and
[data/SAMPLES.md](../data/SAMPLES.md) lists the individual tiles and their files.
The sample contains 2,177,510 occupied reference voxels. Its 10 test tiles
comprise 3 Bydgoszcz, 3 Los Angeles, 3 Manchester and 1 Rome tiles.

Evaluation on every released test tile is still a **10-tile sample evaluation**.
It does not reproduce the full 25-tile benchmark. The original model metrics
and results computed on the released sample should be reported separately.
