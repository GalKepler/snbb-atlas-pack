"""Build standalone Schaefer2018 surface atlases with FreeSurfer .annot files.

For each Schaefer parcel count N, downloads the fsaverage .annot files from
the CBIG GitHub repository and builds a cortex-only TSV from the corresponding
4S{N+56}Parcels atlas.

The .annot files are cached in sourcedata/Schaefer2018/ to avoid repeated
downloads. Must run after atlas_qsirecon.build() so that the 4S atlas
directories are populated (needed for the TSV).
"""

import urllib.request
from pathlib import Path

import pandas as pd

from scripts.utils import ensure_atlas_dir, safe_copy, write_tsv

PARCELS = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
_4S_SUBCORTICAL_COUNT = 56  # CIT168 + ThalamusHCP + HCPSubcortical + Cerebellum

SOURCEDATA = Path(__file__).parent.parent / "sourcedata" / "Schaefer2018"

_CBIG_ANNOT_BASE = (
    "https://raw.githubusercontent.com/ThomasYeoLab/CBIG/master"
    "/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal"
    "/Parcellations/FreeSurfer5.3/fsaverage/label"
)


def _annot_src_name(n: int, hemi: str) -> str:
    """Filename as distributed by CBIG (lh/rh prefix, lowercase)."""
    return f"{hemi.lower()}h.Schaefer2018_{n}Parcels_7Networks_order.annot"


def _annot_cache_path(n: int, hemi: str) -> Path:
    return SOURCEDATA / _annot_src_name(n, hemi)


def _download_annot(n: int, hemi: str) -> Path:
    dst = _annot_cache_path(n, hemi)
    if dst.exists():
        return dst
    SOURCEDATA.mkdir(parents=True, exist_ok=True)
    url = f"{_CBIG_ANNOT_BASE}/{_annot_src_name(n, hemi)}"
    print(f"    Downloading {dst.name}...")
    urllib.request.urlretrieve(url, dst)
    return dst


def build(base: Path) -> None:
    atlases_dir = base / "atlases"

    for n in PARCELS:
        atlas_name = f"Schaefer2018N{n}"
        s4_name = f"4S{n + _4S_SUBCORTICAL_COUNT}Parcels"
        s4_dir = atlases_dir / f"atlas-{s4_name}"

        if not s4_dir.exists():
            print(f"  [WARN] {s4_dir} not found, skipping {atlas_name}")
            continue

        out_dir = ensure_atlas_dir(base, atlas_name)

        # Copy surface CIFTI from the corresponding 4S atlas
        src_cifti = s4_dir / f"atlas-{s4_name}_space-fsLR_den-91k_dseg.dlabel.nii"
        if src_cifti.exists():
            dst_cifti = out_dir / f"atlas-{atlas_name}_space-fsLR_den-91k_dseg.dlabel.nii"
            safe_copy(src_cifti, dst_cifti)
        else:
            print(f"  [WARN] CIFTI not found: {src_cifti}")

        # Download and copy per-hemisphere .annot files
        for hemi in ("L", "R"):
            src_annot = _download_annot(n, hemi)
            dst_annot = out_dir / f"atlas-{atlas_name}_space-fsaverage_hemi-{hemi}_dseg.annot"
            safe_copy(src_annot, dst_annot)

        # Build cortex-only TSV (indices 1..N are the Schaefer cortex parcels)
        s4_tsv = s4_dir / f"atlas-{s4_name}_dseg.tsv"
        df = pd.read_csv(s4_tsv, sep="\t")
        cortex_df = df[df["index"] <= n].copy()
        cortex_df["atlas_name"] = atlas_name
        write_tsv(cortex_df, out_dir / f"atlas-{atlas_name}_dseg.tsv")

        print(f"  [{atlas_name}] {len(cortex_df)} regions → {out_dir.name}/")
