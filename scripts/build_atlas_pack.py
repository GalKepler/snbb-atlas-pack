"""Orchestrate generation of the SNBB Atlas Pack BIDS structure."""

import json
import os
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
        "Tzourio-Mazoyer et al. 2002 - NeuroImage - AAL (https://doi.org/10.1006/nimg.2001.0978)",
        "Joliot et al. 2015 - J Neurosci Methods - AICHA (https://doi.org/10.1016/j.jneumeth.2015.07.013)",
        "Gordon et al. 2016 - Cereb Cortex - Gordon333 (https://doi.org/10.1093/cercor/bhu239)",
        "Cieslak et al. 2021 - Nat Methods - QSIRecon/4S (https://doi.org/10.1038/s41592-021-01185-5)",
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


def _unlock_atlases(base: Path) -> None:
    """Ensure all output files are writable before the build.

    git-annex marks annexed objects read-only (either as symlinks to
    .git/annex/objects/ or as read-only regular files after unlock).
    This function:
      - Replaces symlinks with their content (or removes broken ones)
      - chmod +w on read-only regular files
    Also removes broken sourcedata symlinks so download functions can
    re-fetch files from their upstream URLs.
    """
    output_dirs = [base / "atlases", base / "qsirecon_ext"]
    sourcedata_dirs = [base / "sourcedata" / "Schaefer2018"]

    for directory in output_dirs:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_symlink():
                real = path.resolve()
                try:
                    if real.exists():
                        data = real.read_bytes()
                        path.unlink()
                        path.write_bytes(data)
                    else:
                        path.unlink()
                except OSError:
                    pass
            elif path.is_file() and not os.access(path, os.W_OK):
                try:
                    path.chmod(path.stat().st_mode | 0o200)
                except OSError:
                    pass

    # Remove broken sourcedata symlinks so download functions can re-fetch
    for directory in sourcedata_dirs:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_symlink() and not path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass


def build() -> None:
    from scripts import (
        atlas_brainnetome,
        atlas_hcpex,
        atlas_hcpmmp,
        atlas_qsirecon,
        atlas_schaefer_surface,
        atlas_schaefer_tian,
        atlas_subcortical,
        atlas_tian,
        build_qsirecon_ext,
    )

    print("Building SNBB Atlas Pack...")
    _unlock_atlases(BASE)

    # dataset_description.json
    desc_path = BASE / "dataset_description.json"
    desc_path.write_text(json.dumps(DATASET_DESCRIPTION, indent=2))
    print(f"  Wrote {desc_path.name}")

    atlas_tian.build(BASE)
    try:
        atlas_hcpex.build(BASE)
    except FileNotFoundError as exc:
        print(f"  [HCPex] Skipped (sourcedata unavailable): {exc}")
    try:
        atlas_hcpmmp.build(BASE)
    except FileNotFoundError as exc:
        print(f"  [HCPMMP] Skipped (sourcedata unavailable): {exc}")
    atlas_schaefer_tian.build(BASE)
    try:
        atlas_brainnetome.build(BASE)
    except (FileNotFoundError, OSError) as exc:
        print(f"  [Brainnetome246Ext] Skipped (sourcedata unavailable): {exc}")
    atlas_qsirecon.build(BASE)
    atlas_schaefer_surface.build(BASE)
    atlas_subcortical.build(BASE)

    print("Building qsirecon_ext/...")
    build_qsirecon_ext.build(BASE)

    print("Done.")
