# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A BIDS-compatible atlas pack for a brain bank (SNBB), providing both atlases not covered by Pennlinc/QSIRecon and those that are. The repo is a [DataLad](https://www.datalad.org/) dataset (git-annex tracks large binary files).

**Atlases included:**
- `atlas-TianS1` through `atlas-TianS4` — Melbourne Subcortex Atlas (3T, MNI152NLin2009cAsym, 1mm)
- `atlas-HCPex` — Extended HCP multimodal parcellation (MNI152NLin2009cAsym, 1mm)
- `atlas-HCPMMP` — HCP Multimodal Parcellation 1.0 surface atlas (fsLR 32k, extracted from Tian CIFTI)
- `atlas-Brainnetome246Ext` — Brainnetome Atlas with 246 regions (MNI152NLin2009cAsym, 1mm) and surface projections (fsLR 32k)
- `atlas-Schaefer` — Schaefer (100-1000)-region parcellation (MNI152NLin2009cAsym, 1mm) and surface projections (fsLR 32k)
- all atlases included in QSIRecon (e.g, `atlas-4SX`, `atlas-AAL116`, `atlas-Gordon333Ext`, `atlas-AICHA384Ext`, etc.)

The idea is to have a single source of truth for all atlases used in SNBB analyses, with a standardized format and metadata. The build pipeline generates both volumetric and surface versions (where applicable) of each atlas, along with TSV files containing label metadata - index, label (mandatory), hemisphere, etc. The source data is organized in `sourcedata/` and the build scripts are in `scripts/`. After building, the generated files are tracked by git-annex and can be committed with DataLad.

## Commands

```bash
# Build all atlases (generates atlases/atlas-*/ directories, dataset_description.json)
uv run python main.py

# Install dependencies
uv sync

# Run the notebook explorer
uv run jupyter notebook notebooks/hcpex.ipynb
```

## Architecture

### Build Pipeline

`main.py` → `scripts/build_atlas_pack.py` → three atlas modules:

- `scripts/atlas_tian.py` — Reads from `/media/storage/yalab-dev/Tian2020MSA_v1.4/Tian2020MSA/3T/Subcortex-Only/`, copies NIfTI files and generates TSVs from `Tian_Subcortex_S{N}_3T_label.txt` (one label per line, 1-based) and `Tian_Subcortex_S{N}_3T_COG.txt` (tab-separated x/y/z MNI coordinates).
- `scripts/atlas_hcpex.py` — Merges `sourcedata/HCPex/HCPex_LookUpTable.txt` + `mmp_labels.csv` on `regionLongName` (same merge as `notebooks/hcpex.ipynb`).
- `scripts/atlas_hcpmmp.py` — Extracts HCP-MMP cortical parcellation from the Tian CIFTI (`Q1-Q6_RelatedValidation210...32k_fs_LR_Tian_Subcortex_S1.dlabel.nii`) using nibabel; label names normalized case-insensitively against `mmp_labels.csv`.

### BIDS Conventions

- Volumetric: `atlas-<Name>_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz`
- Surface: `atlas-<Name>_space-fsLR_hemi-<L|R>_dseg.label.gii`
- Labels: `atlas-<Name>_dseg.tsv` (columns: `index`, `label`, `name`, `hemisphere`, atlas-specific extras)

### Source Data

Raw files live in `sourcedata/HCPex/` (moved from `HCPex/` at project root). Tian source files are read directly from `/media/storage/yalab-dev/Tian2020MSA_v1.4/` (not copied into sourcedata).

### DataLad

NIfTI and GIFTI files are tracked by git-annex (`.gitattributes` is configured). After running the build, commit with `datalad save -m "message"` rather than plain `git commit`.
