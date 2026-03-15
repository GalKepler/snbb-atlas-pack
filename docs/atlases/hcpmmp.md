# HCP-MMP — HCP Multimodal Parcellation 1.0 (Surface)

> Glasser MF, Coalson TS, Robinson EC, et al. (2016). *A multi-modal parcellation of human cerebral cortex.* **Nature**, 536, 171–178. [doi:10.1038/nature18933](https://doi.org/10.1038/nature18933)

## Overview

The HCP Multimodal Parcellation 1.0 (HCP-MMP) is a 360-region **cortical surface** atlas derived from multimodal MRI data (myelin maps, cortical thickness, fMRI, and more) from 210 HCP subjects. It covers all of cortex at 180 regions per hemisphere. Boundaries were determined by abrupt changes across multiple MRI modalities simultaneously, making the parcellation more biologically grounded than purely functional or purely structural atlases.

In the SNBB Atlas Pack, this atlas is provided as per-hemisphere **GIFTI label files** in **fsLR 32k** space (32,492 vertices per hemisphere), extracted from the Tian 2020 MSA CIFTI file.

## Recommended Uses

- **Surface-based cortical analysis** — the native format of this atlas; compatible with Connectome Workbench, HCP pipelines, nilearn surface plotting, and fMRIPrep/XCP-D outputs in fsLR space.
- **Cortical morphology and thickness** — surface-based analysis of cortical thickness, surface area, or myelin maps parcellated at the HCP-MMP level.
- **High-resolution cortical parcellation** — 180 areas per hemisphere is finer than Schaefer 100–400 solutions; use when the question demands fine-grained cortical distinctions.
- **Cross-study comparison** — HCP-MMP is one of the most widely used cortical atlases; results are directly comparable with a large body of HCP-derived literature.

!!! note "Cortex only, surface space"
    This atlas covers cortex only (no subcortex) and is in fsLR 32k surface space. For volumetric or whole-brain analyses, use `atlas-HCPex` (volumetric cortex + subcortex) or an `atlas-Schaefer2018N{N}n7Tian2020S{S}` variant.

| Atlas | Regions | Space | Format |
|-------|--------:|-------|--------|
| `atlas-HCPMMP` | 360 (180 per hemisphere) | fsLR 32k | GIFTI `.label.gii` |

## Files

```
atlases/atlas-HCPMMP/
├── atlas-HCPMMP_space-fsLR_hemi-L_dseg.label.gii   # Left hemisphere
├── atlas-HCPMMP_space-fsLR_hemi-R_dseg.label.gii   # Right hemisphere
└── atlas-HCPMMP_dseg.tsv                            # Unified region table (both hemispheres)
```

The GIFTI files contain:
- A dense vertex array (32,492 values per file): 0 = background, otherwise = region index
- A label table with one entry per region, including the region name and RGB display color

## TSV Schema

| Column | Type | Description |
|--------|------|-------------|
| `index` | int | Integer region label in the GIFTI (1-based) |
| `label` | str | Short label, e.g. `V1_L` |
| `name` | str | Full region name, e.g. `Primary_Visual_Cortex_L` |
| `hemisphere` | str | `L` or `R` |
| `region_abbrev` | str | HCP-MMP short abbreviation, e.g. `V1` |
| `lobe` | str | Lobe classification (e.g. `Occ`, `Par`, `Temp`, `Front`) |
| `cortex_type` | str | Cortical functional type (e.g. `Primary_Visual`) |
| `x_cog`, `y_cog`, `z_cog` | float | MNI center-of-gravity (mm) |
| `volume_mm3` | float | Region volume in mm³ |

## Figures

Generate figures with `uv run python scripts/visualize_atlases.py`. Output location:

```
atlases/atlas-HCPMMP/figures/atlas-HCPMMP_cortical.png
```

Cached derivatives at `derivatives/yabplot/atlas-HCPMMP/`: `HCPMMP.csv` (combined 64,984-vertex array) and `HCPMMP.txt` (label + RGB LUT). These are built from the GIFTI files and do not require re-running the full atlas build.

![HCPMMP cortical](img/atlas-HCPMMP/figures/atlas-HCPMMP_cortical.png)

## Source Data

The surface atlas is extracted from a CIFTI file distributed with the Tian 2020 MSA:

```
/media/storage/yalab-dev/Tian2020MSA_v1.4/Tian2020MSA/3T/Cortex-Subcortex/
└── Q1-Q6_RelatedValidation210.CorticalAreas_dil_Final_Final_Areas_Group_Colors
    .32k_fs_LR_Tian_Subcortex_S1.dlabel.nii
```

Region metadata comes from `sourcedata/HCPex/mmp_labels.csv` (same file used by the HCPex module).

## Build Logic

`scripts/atlas_hcpmmp.py` extracts the HCP-MMP cortical surface parcellation from the CIFTI file in three steps:

### 1. CIFTI Name Normalization

CIFTI label names use a different convention than HCP-MMP standard names:

```
CIFTI name → MMP name
"L_V1_ROI"  → "V1_L"
"R_PFm_ROI" → "PFm_R"
```

The function `_cifti_label_to_mmp_name()` strips the leading hemisphere prefix and trailing `_ROI` suffix, then appends the hemisphere code.

### 2. Per-Hemisphere GIFTI Extraction

For each hemisphere (L, R):

1. Load the CIFTI file with nibabel
2. Extract the 32,492-vertex surface array for the hemisphere
3. Map CIFTI region indices → HCP-MMP region IDs via **case-insensitive** name matching against `mmp_labels.csv`
4. Build a GIFTI `LabelArray` with the dense vertex data
5. Build a GIFTI label table (index → name + RGBA color)
6. Write to `atlas-HCPMMP_space-fsLR_hemi-{L|R}_dseg.label.gii`

### 3. TSV Generation

The unified TSV is built from `mmp_labels.csv`, selecting and renaming relevant columns. Both hemispheres share a single lookup table indexed 1–360.

```python
# scripts/atlas_hcpmmp.py — simplified
cifti = nib.load(CIFTI_FILE)
mmp_df = _load_mmp_colors()   # mmp_labels.csv + RGB from HCPex LUT

for hemi in ["L", "R"]:
    gifti_img = _extract_gifti(cifti, hemi, mmp_df)
    nib.save(gifti_img, out_path)

tsv = _build_tsv(mmp_df)
utils.write_tsv(tsv, tsv_path)
```

## Usage Notes

- The GIFTI files are in **fsLR 32k** space — compatible with HCP-style surface analysis tools (Connectome Workbench, nibabel, nilearn)
- Vertex indices in the GIFTI correspond directly to the standard 32k mesh; no resampling is needed for data already in fsLR 32k
- Background vertices have label value `0` (not in TSV)
- For volumetric cortical analysis, use [HCPex](hcpex.md) instead
