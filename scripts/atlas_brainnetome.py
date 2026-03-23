"""Build Brainnetome246Ext surface atlas BIDS outputs.

Produces per-hemisphere GIFTI label files in fsLR 32k space from the
BN_Atlas fsaverage_LR32k source files (210 cortical + 36 subcortical
regions listed in TSV).
"""

import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

from scripts.utils import ensure_atlas_dir, write_tsv

SOURCEDATA = (
    Path(__file__).parent.parent
    / "sourcedata"
    / "Brainnetome"
    / "BN_Atlas_freesurfer"
    / "BN_Atlas_freesurfer"
)
LUT_FILE = SOURCEDATA / "BN_Atlas_246_LUT.txt"
GCA_FILE = SOURCEDATA / "BN_Atlas_subcortex.gca"
GIFTI_DIR = SOURCEDATA / "fsaverage" / "fsaverage_LR32k"

ATLAS_NAME = "Brainnetome246Ext"


def _parse_lut() -> pd.DataFrame:
    """Parse BN_Atlas_246_LUT.txt → DataFrame.

    Format per line: <index> <label> <R> <G> <B> <alpha>
    Returns rows for all 247 entries (index 0 = background, 1–246 = regions).
    """
    rows = []
    with open(LUT_FILE) as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            idx = int(parts[0])
            label = parts[1]
            r, g, b = int(parts[2]), int(parts[3]), int(parts[4])
            rows.append({"index": idx, "label": label, "r": r, "g": g, "b": b})
    df = pd.DataFrame(rows)
    df["hemisphere"] = df["label"].apply(
        lambda x: "L" if x.endswith("_L") else ("R" if x.endswith("_R") else "")
    )
    # Indices 1–210 are cortical; 211–246 are subcortical.
    df["structure"] = df["index"].apply(
        lambda x: "Unknown" if x == 0 else ("cortex" if x <= 210 else "subcortex")
    )
    return df


def _build_gifti(
    src_gii: nib.gifti.GiftiImage,
    lut_df: pd.DataFrame,
    hemi: str,
) -> nib.gifti.GiftiImage:
    """Rebuild a hemisphere GIFTI with a LUT-derived label table.

    Vertex index values from the source file are kept intact; only the
    label table (colours + names) is replaced with data from the LUT.
    """
    vertex_data = src_gii.darrays[0].data.astype(np.int32)
    # Source uses -1 for the medial wall; normalise to 0 (Unknown).
    vertex_data[vertex_data < 0] = 0

    # Background entry
    label_table = nib.gifti.GiftiLabelTable()
    bg = nib.gifti.GiftiLabel(key=0, red=25 / 255, green=5 / 255, blue=25 / 255, alpha=0.0)
    bg.label = "Unknown"
    label_table.labels.append(bg)

    hemi_cortical = lut_df[(lut_df["hemisphere"] == hemi) & (lut_df["structure"] == "cortex")]
    for _, row in hemi_cortical.sort_values("index").iterrows():
        lbl = nib.gifti.GiftiLabel(
            key=int(row["index"]),
            red=row["r"] / 255,
            green=row["g"] / 255,
            blue=row["b"] / 255,
            alpha=1.0,
        )
        lbl.label = row["label"]
        label_table.labels.append(lbl)

    structure_name = "CORTEX_LEFT" if hemi == "L" else "CORTEX_RIGHT"
    darray = nib.gifti.GiftiDataArray(
        data=vertex_data,
        intent=nib.nifti1.intent_codes["NIFTI_INTENT_LABEL"],
        datatype="NIFTI_TYPE_INT32",
        meta=nib.gifti.GiftiMetaData({"AnatomicalStructurePrimary": structure_name}),
    )
    gii = nib.gifti.GiftiImage(darrays=[darray])
    gii.labeltable = label_table
    return gii


def build(base: Path) -> None:
    out_dir = ensure_atlas_dir(base, ATLAS_NAME)
    lut_df = _parse_lut()

    for hemi in ("L", "R"):
        src_path = GIFTI_DIR / f"fsaverage.{hemi}.BN_Atlas.32k_fs_LR.label.gii"
        src_gii = nib.load(src_path)
        gii = _build_gifti(src_gii, lut_df, hemi)
        dst = out_dir / f"atlas-{ATLAS_NAME}_space-fsLR_hemi-{hemi}_dseg.label.gii"
        nib.save(gii, dst)

    # TSV includes all 246 regions (cortical + subcortical).
    tsv_df = (
        lut_df[lut_df["index"] > 0][["index", "label", "hemisphere", "structure"]]
        .copy()
        .sort_values("index")
        .reset_index(drop=True)
    )
    # Use the short label as name; no long-form names are distributed with the source.
    tsv_df.insert(2, "name", tsv_df["label"])
    write_tsv(tsv_df, out_dir / f"atlas-{ATLAS_NAME}_dseg.tsv")

    # Copy the FreeSurfer GCA classifier for subcortical segmentation.
    dst_gca = out_dir / f"atlas-{ATLAS_NAME}_subcortex.gca"
    shutil.copy2(GCA_FILE, dst_gca)

    n_ctx = (tsv_df["structure"] == "cortex").sum()
    n_sub = (tsv_df["structure"] == "subcortex").sum()
    print(f"  [{ATLAS_NAME}] {n_ctx} cortical + {n_sub} subcortical → {out_dir.name}/")
