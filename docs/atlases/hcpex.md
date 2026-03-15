# HCPex — Extended HCP Multimodal Parcellation

> Huang CC, Rolls ET, Feng J, Lin CP. (2022). *An extended Human Connectome Project multimodal parcellation atlas of the human cortex and subcortical areas.* **NeuroImage**, 255, 119385. [doi:10.1016/j.neuroimage.2022.119385](https://doi.org/10.1016/j.neuroimage.2022.119385)

## Overview

HCPex extends the original HCP Multimodal Parcellation (HCP-MMP 1.0, 360 cortical regions) by adding **66 subcortical structures** — covering 7 bilateral subcortical groups — to produce a comprehensive whole-brain volumetric atlas with **426 total regions**. All regions are provided in a single NIfTI file, making it straightforward to extract whole-brain connectivity matrices without combining separate files.

## Recommended Uses

- **Whole-brain volumetric connectivity matrices** — single self-contained parcellation for cortex and subcortex; no need to combine separate files.
- **Comparison with HCP-MMP literature** — cortical parcels are identical to the standard HCP-MMP 1.0 (Glasser 2016), so results are directly comparable with studies using surface-based HCP-MMP and volumetric projections.
- **Lobe- and network-level analyses** — TSV includes `lobe` and `cortex_type` columns enabling easy aggregation to coarser anatomical scales without external lookups.
- **Studies requiring subcortical detail alongside cortex** — the 66 subcortical regions cover hippocampus (10 regions), amygdala (2), thalamus (26), striatum (18), globus pallidus (4), and more.

!!! note "Volumetric cortex only"
    HCPex provides the HCP-MMP cortical parcellation as a volumetric NIfTI, not as a surface GIFTI. For surface-based analysis tools (Connectome Workbench, nilearn surface plotting), use `atlas-HCPMMP` instead.

| Atlas | Regions | Space | Resolution |
|-------|--------:|-------|-----------|
| `atlas-HCPex` | 426 | MNI152NLin2009cAsym | 1 mm isotropic |

### Composition

| Component | Regions | Description |
|-----------|--------:|-------------|
| Cortical (HCP-MMP) | 360 | 180 areas per hemisphere from multimodal parcellation |
| Subcortical (extended) | 66 | 7 bilateral subcortical groups subdivided |
| **Total** | **426** | — |

## Files

```
atlases/atlas-HCPex/
├── atlas-HCPex_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz
└── atlas-HCPex_dseg.tsv
```

## TSV Schema

| Column | Type | Description |
|--------|------|-------------|
| `index` | int | Integer label in the NIfTI (1-based) |
| `label` | str | Short label, e.g. `V1_L` |
| `name` | str | Full region name, e.g. `Primary_Visual_Cortex_L` |
| `hemisphere` | str | `L` or `R` |
| `lobe` | str | Lobe classification (e.g. `Occ`, `Par`, `Temp`, `Front`) |
| `cortex_type` | str | Cortical functional type (e.g. `Primary_Visual`, `Early_Visual`) |
| `region_id` | float | HCP-MMP region ID (NaN for subcortical) |
| `r`, `g`, `b` | int | RGB display color (0–255) |
| `x_cog`, `y_cog`, `z_cog` | float | MNI center-of-gravity (mm) |
| `volume_mm3` | float | Region volume in mm³ |

### Example rows

```
index  label    name                        hemisphere  lobe  cortex_type           region_id  r    g    b    x_cog      y_cog     z_cog     volume_mm3
1      V1_L     Primary_Visual_Cortex_L     L           Occ   Primary_Visual        1.0        216  117  0    100.49     41.14     71.64     6717.0
2      V2_L     Second_Visual_Area_L        L           Occ   Early_Visual          4.0        50   224  0    102.24     44.06     74.40     6220.0
3      V3_L     Third_Visual_Area_L         L           Occ   Early_Visual          5.0        58   133  0    107.93     40.63     76.96     4994.0
```

## Figures

Generate figures with `uv run python scripts/visualize_atlases.py`. Output location:

```
atlases/atlas-HCPex/figures/
├── atlas-HCPex_cortical.png      # 360 cortical regions
└── atlas-HCPex_subcortical.png   # 66 subcortical regions
```

Cached derivatives at `derivatives/yabplot/atlas-HCPex/`: cortical surface mesh (`.csv` + wb label file) and `subcortical/` VTK meshes.

## Source Data

Source files live in `sourcedata/HCPex/`:

```
sourcedata/HCPex/
├── atlas-HCPex_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz   # NIfTI image
├── HCPex_LookUpTable.txt    # Tab-separated: #No., Label, Name, R, G, B
├── HCPex_LookUpTable.lut    # Freeview binary LUT (alternative format)
└── mmp_labels.csv           # HCP-MMP region metadata with lobe/cortex_type
```

### HCPex_LookUpTable.txt format

```
#No.  Label                        Name:                        R    G    B
0     Unknown                      0                            0    0    0
1     Primary_Visual_Cortex_L      208                          216  117  0
2     Second_Visual_Area_L         231                          50   224  0
```

### mmp_labels.csv format

```
regionName,regionLongName,regionIdLabel,LR,region,Lobe,cortex,regionID,...,x-cog,y-cog,z-cog,volmm
V1_L,Primary_Visual_Cortex_L,1_L,L,V1,Occ,Primary_Visual,1,...,100.49,41.14,71.64,6717
```

## Build Logic

`scripts/atlas_hcpex.py` constructs the TSV by joining two source tables:

1. **Left table** — `HCPex_LookUpTable.txt`: provides index, label, RGB color
2. **Right table** — `mmp_labels.csv`: provides lobe, cortex_type, coordinates, volume

The join key is `regionLongName` (the full name string, e.g. `Primary_Visual_Cortex_L`). Background (index 0) is dropped. Hemisphere is derived from the `_L` / `_R` suffix on the label.

```python
# scripts/atlas_hcpex.py — simplified
lut = pd.read_csv("HCPex_LookUpTable.txt", sep="\t")
mmp = pd.read_csv("mmp_labels.csv")
merged = lut.merge(mmp, on="regionLongName")
# drop background, rename columns, derive hemisphere
utils.write_tsv(merged, dst_tsv)
shutil.copy(src_nii, dst_nii)
```
