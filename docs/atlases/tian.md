# Tian Melbourne Subcortex Atlas (S1–S4)

> Tian Y, Margulies DS, Breakspear M, Zalesky A. (2020). *Topographic organization of the human subcortex unveiled with functional connectivity gradients.* **Nature Neuroscience**, 23, 1421–1432. [doi:10.1038/s41593-020-00711-6](https://doi.org/10.1038/s41593-020-00711-6)

## Overview

The Melbourne Subcortex Atlas (MSA) provides four hierarchical scales of subcortical parcellation derived from resting-state fMRI functional connectivity gradients in 3T HCP-style data. Each scale subdivides the same eight bilateral subcortical structures at increasing granularity, from 8 coarse bilateral regions (S1) up to 27 distinct bilateral structures (S4). Functional boundaries are defined by connectivity gradient discontinuities rather than anatomical landmarks, making this atlas particularly well-suited for fMRI and tractography analyses.

All four atlases are in **MNI152NLin2009cAsym** space at **1 mm isotropic** resolution (3T acquisition).

## Recommended Uses

- **Subcortical tractography endpoint definition** — use S1 for coarse seeding/termination masks; S3/S4 for nucleus-specific tractography (e.g. thalamic nuclei).
- **Resting-state functional connectivity** — subcortical nodes in whole-brain connectivity matrices; pairs with any cortical atlas (Schaefer+Tian combined atlases are pre-built in this pack).
- **Multi-scale analysis** — run the same pipeline at S1 through S4 to assess sensitivity of results to subcortical granularity.
- **Scale selection guidance** — S1 is appropriate when degrees of freedom are limited or the subcortex is not the focus; S2 provides anterior/posterior subdivisions; S3 and S4 add hippocampal and thalamic subdivisions validated against known cytoarchitectural boundaries.

!!! note "Not in QSIRecon"
    The standalone Tian atlases are not distributed by QSIRecon/PennLINC AtlasPack (the 4S series uses a different subcortical parcellation). Use these when you specifically need Melbourne Subcortex Atlas boundaries.

## Scales

| Atlas | Regions | Description |
|-------|--------:|-------------|
| `atlas-TianS1` | 16 | Eight bilateral structures (1 region each per hemisphere) |
| `atlas-TianS2` | 32 | Anterior/posterior subdivisions of each S1 region |
| `atlas-TianS3` | 50 | Further hippocampal and thalamic subdivisions |
| `atlas-TianS4` | 54 | Finest available granularity |

## Structures Covered

All scales parcellate the same eight bilateral structures:

| Abbreviation | Structure |
|-------------|-----------|
| `HIP` | Hippocampus |
| `AMY` | Amygdala |
| `pTHA` | Posterior Thalamus |
| `aTHA` | Anterior Thalamus |
| `NAc` | Nucleus Accumbens |
| `GP` | Globus Pallidus |
| `PUT` | Putamen |
| `CAU` | Caudate Nucleus |

## Files

Each scale has its own BIDS directory:

```
atlases/atlas-TianS{N}/
├── atlas-TianS{N}_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz
└── atlas-TianS{N}_dseg.tsv
```

## TSV Schema

```
index  label    name     hemisphere  structure  x_cog   y_cog   z_cog
```

| Column | Description |
|--------|-------------|
| `index` | Integer label in the NIfTI (1-based) |
| `label` | Short label, e.g. `HIP-rh` |
| `name` | Same as `label` for Tian (e.g. `HIP-rh`) |
| `hemisphere` | `L` or `R` |
| `structure` | Anatomical abbreviation (e.g. `HIP`, `AMY`) |
| `x_cog` | MNI x center-of-gravity (mm) |
| `y_cog` | MNI y center-of-gravity (mm) |
| `z_cog` | MNI z center-of-gravity (mm) |

### Example rows (TianS1)

```
index  label    name     hemisphere  structure  x_cog   y_cog   z_cog
1      HIP-rh   HIP-rh   R           HIP        28.0    -22.0   -14.0
2      AMY-rh   AMY-rh   R           AMY        24.0    -4.0    -18.0
3      pTHA-rh  pTHA-rh  R           pTHA       16.0    -26.0   2.0
4      aTHA-rh  aTHA-rh  R           aTHA       10.0    -14.0   8.0
5      NAc-rh   NAc-rh   R           NAc        12.0    14.0    -6.0
6      GP-rh    GP-rh    R           GP         20.0    -4.0    -2.0
7      PUT-rh   PUT-rh   R           PUT        26.0    0.0     0.0
8      CAU-rh   CAU-rh   R           CAU        14.0    10.0    10.0
9      HIP-lh   HIP-lh   L           HIP        -26.0   -22.0   -14.0
...
```

## Figures

Generate figures with `uv run python scripts/visualize_atlases.py`. Output location:

```
atlases/atlas-TianS{N}/figures/atlas-TianS{N}_subcortical.png
```

Intermediate VTK meshes are cached at `derivatives/yabplot/atlas-TianS{N}/` and reused by all Schaefer+TianS{N} combined atlases.

## Source Data

Source files are read from an external path (not version-controlled in this repo):

```
/media/storage/yalab-dev/Tian2020MSA_v1.4/Tian2020MSA/3T/Subcortex-Only/
├── Tian_Subcortex_S{N}_3T_2009cAsym_1mm.nii.gz   # NIfTI image
├── Tian_Subcortex_S{N}_3T_label.txt               # One label per line
└── Tian_Subcortex_S{N}_3T_COG.txt                 # Tab-separated x/y/z coordinates
```

## Build Logic

`scripts/atlas_tian.py` performs the following for each scale N ∈ {1, 2, 3, 4}:

1. Reads `Tian_Subcortex_S{N}_3T_label.txt` — one label string per line (e.g. `HIP-rh`)
2. Reads `Tian_Subcortex_S{N}_3T_COG.txt` — tab-separated `x y z` MNI coordinates
3. Derives `hemisphere` (L/R) and `structure` from the label suffix (`-lh`/`-rh`)
4. Copies the NIfTI to `atlases/atlas-TianS{N}/`
5. Writes the merged TSV

```python
# scripts/atlas_tian.py — simplified
for scale in [1, 2, 3, 4]:
    labels_df = _parse_labels(scale)   # reads label + COG files
    shutil.copy(src_nii, dst_nii)
    utils.write_tsv(labels_df, dst_tsv)
```

## Region Counts by Scale

```
S1: 8 structures × 2 hemispheres = 16 regions
S2: ~32 regions  (anterior/posterior splits)
S3: ~50 regions  (hippocampal/thalamic subdivisions added)
S4: ~54 regions  (finest subdivision)
```
