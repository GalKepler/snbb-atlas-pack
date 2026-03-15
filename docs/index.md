<p align="center">
  <img src="assets/logo.png" alt="SNBB Atlas Pack" width="200">
</p>

# SNBB Atlas Pack

A **BIDS-compatible** brain parcellation atlas repository for the **Strauss Neuroplasticity Brain Bank (SNBB)**, providing atlases not shipped with [QSIRecon/PennLINC AtlasPack](https://github.com/PennLINC/AtlasPack). The dataset is managed with [DataLad](https://www.datalad.org/) and git-annex for reproducible, version-controlled distribution of large binary files.

---

## Atlases at a Glance

| Atlas | Regions | Space | Format | Citation |
|-------|--------:|-------|--------|----------|
| `atlas-TianS1` | 16 | MNI152NLin2009cAsym | NIfTI | [Tian 2020](https://doi.org/10.1038/s41593-020-00711-6) |
| `atlas-TianS2` | 32 | MNI152NLin2009cAsym | NIfTI | [Tian 2020](https://doi.org/10.1038/s41593-020-00711-6) |
| `atlas-TianS3` | 50 | MNI152NLin2009cAsym | NIfTI | [Tian 2020](https://doi.org/10.1038/s41593-020-00711-6) |
| `atlas-TianS4` | 54 | MNI152NLin2009cAsym | NIfTI | [Tian 2020](https://doi.org/10.1038/s41593-020-00711-6) |
| `atlas-HCPex` | 426 | MNI152NLin2009cAsym | NIfTI | [Huang 2022](https://doi.org/10.1016/j.neuroimage.2022.119385) |
| `atlas-HCPMMP` | 360 | fsLR 32k | GIFTI | [Glasser 2016](https://doi.org/10.1038/nature18933) |
| `atlas-Schaefer2018N{N}n7Tian2020S{S}` | 116–1054 | MNI152NLin2009cAsym | NIfTI | [Schaefer 2018](https://doi.org/10.1093/cercor/bhx179) + [Tian 2020](https://doi.org/10.1038/s41593-020-00711-6) |

The 40 Schaefer+Tian combined atlases span N ∈ {100, 200, …, 1000} cortical parcels × S ∈ {1, 2, 3, 4} subcortical scales.

---

## Quick Start

```bash
# Clone and fetch a specific atlas (no build needed)
datalad clone https://github.com/GalKepler/snbb-atlas-pack
cd snbb-atlas-pack
datalad get atlases/atlas-TianS1/

# Or rebuild everything from source
uv sync
uv run python main.py
datalad save -m "Rebuild all atlases"

# Generate atlas visualizations
uv run python scripts/visualize_atlases.py
```

---

## Repository Structure

```
snbb_atlas_pack/
├── main.py                        # Entry point: runs the full build
├── dataset_description.json       # BIDS dataset metadata
├── scripts/
│   ├── build_atlas_pack.py        # Orchestrator
│   ├── atlas_tian.py              # Tian S1–S4 processing
│   ├── atlas_hcpex.py             # HCPex processing
│   ├── atlas_hcpmmp.py            # HCP-MMP surface atlas
│   ├── atlas_schaefer_tian.py     # Schaefer2018+Tian combined atlases
│   └── utils.py                   # Shared helpers
├── sourcedata/
│   ├── HCPex/                     # Raw HCPex lookup tables and NIfTI
│   └── Schaefer2018/              # Auto-downloaded Schaefer files
├── atlases/
│   ├── atlas-TianS{1-4}/
│   ├── atlas-HCPex/
│   ├── atlas-HCPMMP/
│   └── atlas-Schaefer2018N{N}n7Tian2020S{S}/   # 40 combined atlases
└── derivatives/
    └── yabplot/                   # Brain visualizations per atlas
```

---

## License

**CC BY 4.0** — see `dataset_description.json`. Refer to the original atlas publications for any additional license terms specific to each atlas.

## Citation

Please cite the original atlas publications listed in [`dataset_description.json`](https://github.com/GalKepler/snbb-atlas-pack/blob/main/dataset_description.json):

- Tian et al. 2020 — *Nature Neuroscience* — [doi:10.1038/s41593-020-00711-6](https://doi.org/10.1038/s41593-020-00711-6)
- Glasser et al. 2016 — *Nature* — [doi:10.1038/nature18933](https://doi.org/10.1038/nature18933)
- Huang et al. 2022 — *NeuroImage* — [doi:10.1016/j.neuroimage.2022.119385](https://doi.org/10.1016/j.neuroimage.2022.119385)
- Schaefer et al. 2018 — *Cerebral Cortex* — [doi:10.1093/cercor/bhx179](https://doi.org/10.1093/cercor/bhx179)
