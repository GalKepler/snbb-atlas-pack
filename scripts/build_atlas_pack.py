"""Orchestrate generation of the SNBB Atlas Pack BIDS structure."""

import json
from pathlib import Path

BASE = Path(__file__).parent.parent

DATASET_DESCRIPTION = {
    "Name": "SNBB Atlas Pack",
    "BIDSVersion": "1.9.0",
    "DatasetType": "atlas",
    "License": "CC-BY-4.0",
    "Authors": ["Gal Kepler"],
    "HowToAcknowledge": "Please cite the original atlas publications listed in ReferencesAndLinks.",
    "ReferencesAndLinks": [
        "Tian et al. 2020 - Nat Neurosci - https://doi.org/10.1038/s41593-020-00711-6",
        "Glasser et al. 2016 - Nature - https://doi.org/10.1038/nature18933",
        "Huang et al. 2022 - NeuroImage - HCPex (https://doi.org/10.1016/j.neuroimage.2022.119385)",
        "Schaefer et al. 2018 - Cereb Cortex - https://doi.org/10.1093/cercor/bhx179",
        "Fan et al. 2016 - Cereb Cortex - Brainnetome Atlas (https://doi.org/10.1093/cercor/bhw157)",
    ],
    "GeneratedBy": [
        {
            "Name": "snbb-atlas-pack",
            "Version": "0.1.0",
            "Description": "Custom build pipeline that assembles BIDS-compatible atlas directories from source NIfTI/CIFTI/GIFTI files and look-up tables.",
            "CodeURL": "https://github.com/GalKepler/snbb-atlas-pack",
        }
    ],
}


def build() -> None:
    from scripts import atlas_brainnetome, atlas_hcpex, atlas_hcpmmp, atlas_schaefer_tian, atlas_tian

    print("Building SNBB Atlas Pack...")

    # dataset_description.json
    desc_path = BASE / "dataset_description.json"
    desc_path.write_text(json.dumps(DATASET_DESCRIPTION, indent=2))
    print(f"  Wrote {desc_path.name}")

    atlas_tian.build(BASE)
    atlas_hcpex.build(BASE)
    atlas_hcpmmp.build(BASE)
    atlas_schaefer_tian.build(BASE)
    atlas_brainnetome.build(BASE)

    print("Done.")
