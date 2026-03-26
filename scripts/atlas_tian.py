"""Build Tian Melbourne Subcortex Atlas (3T, Scales S1–S4) BIDS outputs."""

from pathlib import Path

import pandas as pd

from scripts.utils import ensure_atlas_dir, safe_copy, write_tsv

TIAN_SRC = Path("/media/storage/yalab-dev/Tian2020MSA_v1.4/Tian2020MSA/3T/Subcortex-Only")
SCALES = [1, 2, 3, 4]


def _parse_labels(scale: int) -> pd.DataFrame:
    label_file = TIAN_SRC / f"Tian_Subcortex_S{scale}_3T_label.txt"
    cog_file = TIAN_SRC / f"Tian_Subcortex_S{scale}_3T_COG.txt"

    labels = label_file.read_text().splitlines()
    labels = [l for l in labels if l.strip()]

    cog = pd.read_csv(cog_file, sep="\t", header=None, names=["x_cog", "y_cog", "z_cog"])

    rows = []
    for i, label in enumerate(labels, start=1):
        hemi = "R" if label.endswith("-rh") else "L"
        structure = label.rsplit("-", 1)[0]  # strip -lh/-rh
        rows.append(
            {
                "index": i,
                "label": label,
                "name": label,
                "hemisphere": hemi,
                "structure": structure,
                "x_cog": cog.loc[i - 1, "x_cog"],
                "y_cog": cog.loc[i - 1, "y_cog"],
                "z_cog": cog.loc[i - 1, "z_cog"],
            }
        )
    return pd.DataFrame(rows)


def build(base: Path) -> None:
    for scale in SCALES:
        atlas_name = f"TianS{scale}"
        out_dir = ensure_atlas_dir(base, atlas_name)

        # Copy NIfTI
        src_nii = TIAN_SRC / f"Tian_Subcortex_S{scale}_3T_2009cAsym_1mm.nii.gz"
        dst_nii = out_dir / f"atlas-{atlas_name}_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz"
        safe_copy(src_nii, dst_nii)

        # Write TSV
        df = _parse_labels(scale)
        write_tsv(df, out_dir / f"atlas-{atlas_name}_dseg.tsv")
        print(f"  [TianS{scale}] {len(df)} regions → {out_dir.name}/")
