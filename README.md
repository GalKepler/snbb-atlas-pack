# SNBB Atlas Pack

[![Tests](https://github.com/GalKepler/snbb-atlas-pack/actions/workflows/tests.yml/badge.svg)](https://github.com/GalKepler/snbb-atlas-pack/actions/workflows/tests.yml)
[![Docs](https://github.com/GalKepler/snbb-atlas-pack/actions/workflows/docs.yml/badge.svg)](https://github.com/GalKepler/snbb-atlas-pack/actions/workflows/docs.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

A BIDS-compatible parcellation atlas repository for the **Strauss Neuroplasticity Brain Bank (SNBB)**, providing atlases not shipped with [QSIRecon/PennLINC](https://github.com/PennLINC/AtlasPack). This dataset is managed with [DataLad](https://www.datalad.org/) and git-annex.

---

## Atlases Included

Each atlas lives in its own `atlas-<Name>/` directory and contains:
- An image file (NIfTI `.nii.gz` for volumetric, GIFTI `.label.gii` for surface)
- A `_dseg.tsv` lookup table with region metadata

### Tian Melbourne Subcortex Atlas (S1–S4)

> Tian et al. (2020). *Topographic organization of the human subcortex unveiled with functional connectivity gradients.* Nature Neuroscience. https://doi.org/10.1038/s41593-020-00711-6

Four hierarchical scales of subcortical parcellation (3T, MNI152NLin2009cAsym, 1 mm isotropic):

| Atlas | Regions | Structures |
|-------|---------|------------|
| `atlas-TianS1` | 16 | Hippocampus, Amygdala, Thalamus (ant/post), NAc, GP, Putamen, Caudate — bilateral |
| `atlas-TianS2` | 32 | Anterior/posterior subdivisions of S1 structures |
| `atlas-TianS3` | 50 | Further hippocampal and thalamic subdivisions |
| `atlas-TianS4` | 54 | Finest available granularity |

**TSV columns:** `index`, `label`, `name`, `hemisphere` (L/R), `structure`, `x_cog`, `y_cog`, `z_cog` (MNI mm)

### HCPex

> Huang et al. (2022). *[HCPex] An extended Human Connectome Project multimodal parcellation atlas of the human cortex.* NeuroImage. https://doi.org/10.1016/j.neuroimage.2022.119385

An extension of the HCP Multimodal Parcellation that adds 66 subcortical structures (7 bilateral pairs: hippocampus, amygdala, thalamus, striatum, etc.) to the 360 HCP-MMP cortical areas.

| Atlas | Regions | Space | Resolution |
|-------|---------|-------|------------|
| `atlas-HCPex` | 426 | MNI152NLin2009cAsym | 1 mm |

**TSV columns:** `index`, `label`, `name`, `hemisphere`, `lobe`, `cortex_type`, `region_id`, `r`, `g`, `b` (RGB), `x_cog`, `y_cog`, `z_cog`, `volume_mm3`

### HCP Multimodal Parcellation (HCP-MMP 1.0)

> Glasser et al. (2016). *A multi-modal parcellation of human cerebral cortex.* Nature. https://doi.org/10.1038/nature18933

The original 360-region (180/hemisphere) cortical parcellation in surface space. Extracted from the HCP Q1–Q6 RelatedValidation210 CIFTI file distributed with the Tian 2020 MSA.

| Atlas | Regions | Space | Format |
|-------|---------|-------|--------|
| `atlas-HCPMMP` | 360 | fsLR 32k | GIFTI `.label.gii` |

Files: `atlas-HCPMMP_space-fsLR_hemi-L_dseg.label.gii`, `atlas-HCPMMP_space-fsLR_hemi-R_dseg.label.gii`

**TSV columns:** `index`, `label`, `name`, `hemisphere`, `region_abbrev`, `lobe`, `cortex_type`, `x_cog`, `y_cog`, `z_cog`, `volume_mm3`

---

## Atlases Not Included (QSIRecon / PennLINC)

The following atlases are already distributed by [QSIRecon's AtlasPack](https://github.com/PennLINC/AtlasPack) and are therefore **not** included here to avoid duplication.

| Atlas | Regions | Notes |
|-------|---------|-------|
| **4S series** (4S156 – 4S1056) | 156–1056 | Schaefer2018 cortex + CIT168 subcortex + HCP thalamus + MDTB10 cerebellum + HCP hippocampus/amygdala; 10 variants |
| **Schaefer 2018** | 100–1000 | 7- and 17-network solutions |
| **AAL** | 116 | Tzourio-Mazoyer et al. |
| **AICHA384Ext** | 384 | Joliot et al., extended subcortical |
| **Brainnetome246Ext** | 246 | Fan et al., extended subcortical |
| **Gordon333Ext** | 333 | Gordon et al., extended subcortical |

### Getting QSIRecon Atlases

**Option 1 — DataLad clone (recommended, preserves version history):**
```bash
datalad clone https://github.com/PennLINC/AtlasPack
cd AtlasPack
datalad get atlas-4S456Parcels/  # download specific atlas
```

**Option 2 — TemplateFlow Python client:**
```python
import templateflow.api as tflow
files = tflow.get('MNI152NLin2009cAsym', atlas='Schaefer2018', resolution=1)
```

**Option 3 — Inside QSIRecon containers:** atlases are pre-bundled in the QSIRecon Docker/Singularity image under `/opt/templateflow/`.

---

## Usage

### Build / Regenerate All Atlases

```bash
# Activate the environment (or prefix commands with `uv run`)
source .venv/bin/activate

# Regenerate all atlas-*/ directories from source data
python main.py
```

This reads raw source files (Tian MSA and HCPex source data) and writes the BIDS-structured output into `atlas-*/` directories. Safe to re-run; existing files are overwritten.

### DataLad Save After Build

```bash
datalad save -m "Rebuild all atlases"
```

Use `datalad save` (not `git commit`) so that NIfTI/GIFTI files are properly annexed.

---

## Adding a New Atlas

1. **Add source data** — place raw files in `sourcedata/<AtlasName>/` (or point to an external path).

2. **Create a processing module** — add `scripts/atlas_<name>.py` with a `build(base: Path) -> None` function following the pattern of the existing modules:
   - Copy/convert the NIfTI or GIFTI to `atlas-<Name>/atlas-<Name>_space-<space>_<res>_dseg.<ext>`
   - Write a TSV to `atlas-<Name>/atlas-<Name>_dseg.tsv` using `utils.write_tsv()`
   - At minimum include columns: `index`, `label`, `name`, `hemisphere`

3. **Register in the orchestrator** — import and call your module in `scripts/build_atlas_pack.py`:
   ```python
   from scripts import atlas_<name>
   # inside build():
   atlas_<name>.build(BASE)
   ```

4. **Add citation to `dataset_description.json`** — update `DATASET_DESCRIPTION["ReferencesAndLinks"]` in `scripts/build_atlas_pack.py`.

5. **Test:**
   ```bash
   python main.py
   # Verify the new atlas directory has the expected files:
   ls atlas-<Name>/
   # Check row count matches expected region count:
   python -c "import pandas as pd; df=pd.read_csv('atlas-<Name>/atlas-<Name>_dseg.tsv', sep='\t'); print(len(df))"
   ```

6. **Save:**
   ```bash
   datalad save -m "Add atlas-<Name>"
   ```

### BIDS Naming Reference

| Entity | Example | Notes |
|--------|---------|-------|
| `atlas-` | `TianS1`, `HCPex`, `HCPMMP` | CamelCase, no hyphens |
| `space-` | `MNI152NLin2009cAsym`, `fsLR`, `fsaverage` | Use templateflow space names |
| `res-` | `01` (1 mm), `02` (2 mm) | Only for volumetric, omit for surface |
| `hemi-` | `L`, `R` | Required for per-hemisphere surface files |
| `_dseg` | — | Suffix for discrete segmentation (label map) |
| `_dseg.tsv` | — | Lookup table; no space/res/hemi entities |

---

## Publishing to DataLad

This dataset is already a DataLad dataset (see `.datalad/config`). To make it publicly accessible:

### 1. Commit current state

```bash
datalad save -m "Initial atlas pack build"
```

### 2. Create a sibling on GitHub (or GitLab)

```bash
# Requires a GitHub personal access token in your keyring
datalad create-sibling-github \
    --dataset . \
    --name github \
    --github-organization <your-org-or-username> \
    snbb-atlas-pack
```

### 3. Configure storage for annexed files

The NIfTI/GIFTI files are annexed (not stored in git). Options:

**Option A — Push to a RIA (Remote Indexed Archive) store** (best for institutional storage):
```bash
datalad create-sibling-ria \
    --dataset . \
    --name ria \
    "ria+ssh://hostname/path/to/ria-store"

# Set RIA as the annex remote for annexed data
datalad siblings configure --name github --annex-wanted "not largerthan=0"
datalad push --to ria      # push data
datalad push --to github   # push metadata + scripts
```

**Option B — Push annexed data directly to GitHub via git-annex special remote** (smaller datasets):
```bash
git annex initremote github-annex type=git url=<github-url>
datalad push --to github
```

**Option C — OSF (Open Science Framework)**:
```bash
pip install datalad-osf
datalad create-sibling-osf --dataset . --name osf --title "SNBB Atlas Pack"
datalad push --to osf
```

### 4. Verify

```bash
datalad status          # should be clean
git log --oneline -5    # confirm commits
```

After publishing, others can access the dataset with:
```bash
datalad clone https://github.com/<org>/snbb-atlas-pack
cd snbb-atlas-pack
datalad get atlas-TianS1/  # download specific atlas
```

---

## Dependencies

Managed with [uv](https://docs.astral.sh/uv/). To install:

```bash
uv sync
```

Key dependencies:

| Package | Purpose |
|---------|---------|
| `nibabel` | NIfTI and GIFTI I/O, CIFTI parsing |
| `pandas` | TSV generation and label table merging |
| `numpy` | Array operations |
| `nilearn` | Neuroimaging utilities |
| `templateflow` | Standard space templates |

---

## Repository Structure

```
snbb-atlas-pack/
├── main.py                        # Entry point: runs the full build
├── dataset_description.json       # BIDS dataset metadata
├── scripts/
│   ├── build_atlas_pack.py        # Orchestrator
│   ├── atlas_tian.py              # Tian S1–S4 processing
│   ├── atlas_hcpex.py             # HCPex processing
│   ├── atlas_hcpmmp.py            # HCP-MMP surface atlas (extracted from CIFTI)
│   └── utils.py                   # Shared helpers
├── sourcedata/
│   └── HCPex/                     # Raw HCPex lookup tables and NIfTI
├── atlas-TianS1/  atlas-TianS2/  atlas-TianS3/  atlas-TianS4/
├── atlas-HCPex/
├── atlas-HCPMMP/
└── notebooks/
    └── hcpex.ipynb                # Exploratory notebook for HCPex merge logic
```

---

## License

`CC BY 4.0` — see `dataset_description.json`. Refer to the original atlas publications for any additional license terms specific to each atlas.