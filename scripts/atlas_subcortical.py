"""Build standalone subcortical atlas outputs.

Copies pre-built NIfTI and TSV files from sourcedata/ into atlases/ for:
- atlas-4SSubcortical  (CIT168 + ThalamusHCP + HCPSubcortical)
- atlas-HCPexSubcortex (HCPex subcortical extension, indices 361–426)
"""

from pathlib import Path

import pandas as pd

from scripts.utils import ensure_atlas_dir, safe_copy

SOURCEDATA = Path(__file__).parent.parent / "sourcedata"


def _copy_atlas(atlas_name: str, base: Path) -> None:
    src_dir = SOURCEDATA / f"atlas-{atlas_name}"
    if not src_dir.exists():
        print(f"  [{atlas_name}] Skipped (sourcedata unavailable): {src_dir}")
        return

    out_dir = ensure_atlas_dir(base, atlas_name)

    src_nii = src_dir / f"atlas-{atlas_name}_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz"
    dst_nii = out_dir / f"atlas-{atlas_name}_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz"
    safe_copy(src_nii, dst_nii)

    src_tsv = src_dir / f"atlas-{atlas_name}_dseg.tsv"
    dst_tsv = out_dir / f"atlas-{atlas_name}_dseg.tsv"
    safe_copy(src_tsv, dst_tsv)

    df = pd.read_csv(dst_tsv, sep="\t")
    print(f"  [{atlas_name}] {len(df)} regions → {out_dir.name}/")


def build(base: Path) -> None:
    _copy_atlas("4SSubcortical", base)
    _copy_atlas("HCPexSubcortex", base)
