# Schaefer2018 + Tian Combined Atlases

> Schaefer A, Kong R, Gordon EM, et al. (2018). *Local-Global Parcellation of the Human Cerebral Cortex from Intrinsic Functional Connectivity MRI.* **Cerebral Cortex**, 28(9), 3095–3114. [doi:10.1093/cercor/bhx179](https://doi.org/10.1093/cercor/bhx179)
>
> Tian Y, Margulies DS, Breakspear M, Zalesky A. (2020). *Topographic organization of the human subcortex unveiled with functional connectivity gradients.* **Nature Neuroscience**, 23, 1421–1432. [doi:10.1038/s41593-020-00711-6](https://doi.org/10.1038/s41593-020-00711-6)

## Overview

These 40 atlases combine the **Schaefer 2018 7-network cortical parcellation** with the **Tian Melbourne Subcortex Atlas** at multiple scales, yielding complete cortex+subcortex volumetric atlases at varying resolutions. They are built by merging a Schaefer cortical NIfTI (background = 0, cortical indices 1–N) with a Tian subcortical NIfTI (shifted so subcortical indices start at N+1), then concatenating their label tables.

## Recommended Uses

- **Whole-brain connectivity matrices at tunable resolution** — Schaefer 2018 is one of the most frequently cited cortical parcellations in recent fMRI literature; results are directly comparable with a large body of published work.
- **Multi-scale analyses** — the 10 × 4 = 40 combinations let you systematically assess how findings vary with cortical and subcortical granularity.
- **Default choice for new SNBB analyses** — N=200–400 + S1 balances resolution against statistical reliability for most fMRI sample sizes. Use S2 or S3 when subcortical subdivision is relevant.
- **7-network labeling** — the `network` column (Vis, SomMot, DorsAttn, SalVentAttn, Limbic, Cont, Default) enables network-level aggregation directly from the TSV without additional lookups.
- **Compatibility with QSIRecon outputs** — QSIRecon uses Schaefer+CIT168/HCP thalamus (4S series); these atlases use the same Schaefer cortex with Tian subcortex as a complementary option.

!!! tip "Which N and S to pick"
    - N=200, S=1 is a good starting point: 216 total regions, well-powered for most SNBB sample sizes.
    - Increase N for higher cortical resolution or when comparing with specific literature values.
    - Use S=2 when you need anterior/posterior distinctions (e.g. anterior vs. posterior thalamus); S=3/S4 for hippocampal or fine thalamic subdivision.

## Atlas Matrix

10 cortical granularities × 4 subcortical scales = **40 atlases**:

| N (cortical parcels) | S1 (16 sub) | S2 (32 sub) | S3 (50 sub) | S4 (54 sub) |
|---------------------:|:-----------:|:-----------:|:-----------:|:-----------:|
| 100  | 116  | 132  | 150  | 154  |
| 200  | 216  | 232  | 250  | 254  |
| 300  | 316  | 332  | 350  | 354  |
| 400  | 416  | 432  | 450  | 454  |
| 500  | 516  | 532  | 550  | 554  |
| 600  | 616  | 632  | 650  | 654  |
| 700  | 716  | 732  | 750  | 754  |
| 800  | 816  | 832  | 850  | 854  |
| 900  | 916  | 932  | 950  | 954  |
| 1000 | 1016 | 1032 | 1050 | 1054 |

*Cell values = total region count (N cortical + subcortical)*

## Naming Convention

```
atlas-Schaefer2018N{N}n7Tian2020S{S}
```

- `N` — number of cortical parcels: 100, 200, …, 1000
- `n7` — 7-network solution (fixed)
- `S` — Tian subcortical scale: 1, 2, 3, 4

**Examples:**
```
atlas-Schaefer2018N100n7Tian2020S1    # 116 regions
atlas-Schaefer2018N1000n7Tian2020S4   # 1054 regions
```

## Files

Each of the 40 atlases has its own BIDS directory:

```
atlases/atlas-Schaefer2018N{N}n7Tian2020S{S}/
├── atlas-Schaefer2018N{N}n7Tian2020S{S}_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz
└── atlas-Schaefer2018N{N}n7Tian2020S{S}_dseg.tsv
```

## TSV Schema

| Column | Type | Description |
|--------|------|-------------|
| `index` | int | Integer label in the NIfTI (1-based) |
| `label` | str | Short label (e.g. `LH_Vis_1`, `HIP-lh`) |
| `name` | str | Full name (e.g. `7Networks_LH_Vis_1`) |
| `hemisphere` | str | `L` or `R` |
| `network` | str | Network name for cortical (`Vis`, `SomMot`, …) or `subcortex` |
| `component` | str | Sub-component label within network |

### Example rows (N=100, S=1)

```
index  label        name                  hemisphere  network   component
1      LH_Vis_1     7Networks_LH_Vis_1    L           Vis       1
2      LH_Vis_2     7Networks_LH_Vis_2    L           Vis       2
...
100    RH_Default_3 7Networks_RH_Default_3 R          Default   3
101    HIP-rh       HIP-rh                R           subcortex HIP-rh
...
116    CAU-lh       CAU-lh                L           subcortex CAU-lh
```

## Figures

Generate figures with `uv run python scripts/visualize_atlases.py`. Output location:

```
atlases/atlas-Schaefer2018N{N}n7Tian2020S{S}/figures/
├── atlas-Schaefer2018N{N}n7Tian2020S{S}_cortical.png
└── atlas-Schaefer2018N{N}n7Tian2020S{S}_subcortical.png
```

**Subcortical figures are shared:** all `atlas-Schaefer2018N{N}n7Tian2020S{S}` variants reuse the precomputed Tian VTK meshes at `derivatives/yabplot/atlas-TianS{S}/`. The subcortical figures for all 10 N-values of a given S-scale are identical (they show the same Tian atlas boundaries).

The examples below show the N=200 parcellation at each subcortical scale.

=== "S1 — Cortical"
    ![Schaefer200+TianS1 cortical](img/atlas-Schaefer2018N200n7Tian2020S1/figures/atlas-Schaefer2018N200n7Tian2020S1_cortical.png)

=== "S1 — Subcortical"
    ![Schaefer200+TianS1 subcortical](img/atlas-Schaefer2018N200n7Tian2020S1/figures/atlas-Schaefer2018N200n7Tian2020S1_subcortical.png)

=== "S2 — Subcortical"
    ![Schaefer200+TianS2 subcortical](img/atlas-Schaefer2018N200n7Tian2020S2/figures/atlas-Schaefer2018N200n7Tian2020S2_subcortical.png)

=== "S3 — Subcortical"
    ![Schaefer200+TianS3 subcortical](img/atlas-Schaefer2018N200n7Tian2020S3/figures/atlas-Schaefer2018N200n7Tian2020S3_subcortical.png)

=== "S4 — Subcortical"
    ![Schaefer200+TianS4 subcortical](img/atlas-Schaefer2018N200n7Tian2020S4/figures/atlas-Schaefer2018N200n7Tian2020S4_subcortical.png)

## Source Data

### Schaefer2018 (auto-downloaded)

Files are auto-downloaded to `sourcedata/Schaefer2018/` on first build:

| N | NIfTI source | Notes |
|---|---|---|
| 100–600, 800, 1000 | TemplateFlow S3 | MNI152NLin2009cAsym res-01 |
| 700, 900 | CBIG GitHub | FSLMNI152 space (resampled) |

```
sourcedata/Schaefer2018/
├── Schaefer2018_100Parcels_7Networks_MNI152NLin2009cAsym_1mm.nii.gz
├── Schaefer2018_100Parcels_7Networks_order.txt
├── Schaefer2018_200Parcels_7Networks_MNI152NLin2009cAsym_1mm.nii.gz
├── ...
└── Schaefer2018_1000Parcels_7Networks_order.txt
```

**LUT format** (`Schaefer2018_{N}Parcels_7Networks_order.txt`):
```
1    7Networks_LH_Vis_1     120  18  131  0
2    7Networks_LH_Vis_2     120  18  132  0
...
```

### Tian MSA (external path)

Read directly from:
```
/media/storage/yalab-dev/Tian2020MSA_v1.4/Tian2020MSA/3T/Subcortex-Only/
```

## Build Logic

`scripts/atlas_schaefer_tian.py` performs the following for each (N, scale) pair:

### 1. Auto-download (if needed)

```python
download_sourcedata()  # idempotent; skips if files exist
```

### 2. Combine NIfTIs

```python
def _combine_niftis(cortex_path, subcortex_path, n_parcels, out_path):
    cortex_img = nib.load(cortex_path)
    subcortex_img = nib.load(subcortex_path)
    # Resample subcortex to cortex affine/shape if they differ (order=0)
    subcortex_resampled = resample_to_img(subcortex_img, cortex_img, interpolation="nearest")
    # Merge: cortex keeps indices 1..N; subcortex shifted to N+1..N+M
    combined = cortex_data.copy()
    mask = subcortex_data > 0
    combined[mask] = subcortex_data[mask] + n_parcels
    nib.save(nib.Nifti1Image(combined, cortex_img.affine), out_path)
```

### 3. Concatenate label tables

```python
schaefer_df = _load_schaefer_labels(n)    # indices 1..N
tian_df = _load_tian_labels(scale)         # indices 1..M → shifted to N+1..N+M
tian_df["index"] += n
combined_df = pd.concat([schaefer_df, tian_df], ignore_index=True)
utils.write_tsv(combined_df, tsv_path)
```

## Schaefer 7-Network Labels

The 7 cortical networks in the Yeo 2011 scheme used by Schaefer 2018:

| Network | Abbreviation | Approximate function |
|---------|-------------|---------------------|
| Visual | `Vis` | Primary and higher visual cortex |
| Somatomotor | `SomMot` | Sensorimotor cortex |
| Dorsal Attention | `DorsAttn` | Spatial attention |
| Ventral Attention | `VentAttn` | Salience / reorienting |
| Limbic | `Limbic` | Orbitofrontal, temporal pole |
| Frontoparietal | `Cont` | Cognitive control |
| Default Mode | `Default` | Default mode network |
