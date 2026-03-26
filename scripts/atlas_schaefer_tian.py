"""Build Schaefer2018+Tian2020 combined atlases (3T, MNI152NLin2009cAsym, 1mm).

Generates all 40 combinations: N={100,200,...,1000} × Tian scales S1–S4.

Sources:
  - Schaefer cortex NIfTIs: TemplateFlow S3 (MNI152NLin2009cAsym res-01)
  - Schaefer cortex GIFTIs: TemplateFlow (fsaverage 164k, 7Networks)
  - Schaefer labels: CBIG freeview_lut (7Networks order)
  - Tian subcortex: /media/storage/yalab-dev/Tian2020MSA_v1.4/
"""

import shutil
import urllib.request
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

from scripts.utils import ensure_atlas_dir, safe_copy, write_tsv

TIAN_SRC = Path("/media/storage/yalab-dev/Tian2020MSA_v1.4/Tian2020MSA/3T/Subcortex-Only")
SOURCEDATA = Path(__file__).parent.parent / "sourcedata" / "Schaefer2018"

PARCELS = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
SCALES = [1, 2, 3, 4]

_TF_BASE = "https://templateflow.s3.amazonaws.com/tpl-MNI152NLin2009cAsym"
_CBIG_BASE = (
    "https://raw.githubusercontent.com/ThomasYeoLab/CBIG/master"
    "/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal"
    "/Parcellations/MNI"
)
# N700 and N900 are absent from TemplateFlow; use CBIG FSLMNI152 for those.
_TF_MISSING = {700, 900}


def _download(url: str, dst: Path) -> None:
    if dst.exists():
        return
    SOURCEDATA.mkdir(parents=True, exist_ok=True)
    print(f"    Downloading {dst.name}...")
    urllib.request.urlretrieve(url, dst)


def _nii_path(n: int) -> Path:
    space = "FSLMNI152" if n in _TF_MISSING else "MNI152NLin2009cAsym"
    return SOURCEDATA / f"Schaefer2018_{n}Parcels_7Networks_{space}_1mm.nii.gz"


def _lut_path(n: int) -> Path:
    return SOURCEDATA / f"Schaefer2018_{n}Parcels_7Networks_order.txt"


def download_sourcedata() -> None:
    """Download Schaefer NIfTIs and LUT files to sourcedata/Schaefer2018/ if not present."""
    for n in PARCELS:
        if n in _TF_MISSING:
            nii_url = (
                f"{_CBIG_BASE}/Schaefer2018_{n}Parcels_7Networks_order_FSLMNI152_1mm.nii.gz"
            )
        else:
            nii_url = (
                f"{_TF_BASE}/tpl-MNI152NLin2009cAsym_res-01_atlas-Schaefer2018"
                f"_desc-{n}Parcels7Networks_dseg.nii.gz"
            )
        _download(nii_url, _nii_path(n))
        _download(
            f"{_CBIG_BASE}/freeview_lut/Schaefer2018_{n}Parcels_7Networks_order.txt",
            _lut_path(n),
        )


def _load_schaefer_labels(n: int) -> pd.DataFrame:
    """Parse CBIG freeview_lut (tab-separated: index name R G B 0)."""
    rows = []
    for line in _lut_path(n).read_text().splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        idx = int(parts[0])
        full_name = parts[1]                    # 7Networks_LH_Vis_1
        label = full_name[len("7Networks_"):]   # LH_Vis_1
        hemi = label.split("_")[0][0]           # L or R
        network = label.split("_")[1]           # Vis, SomMot, etc.
        rows.append(
            {
                "index": idx,
                "label": label,
                "name": full_name,
                "hemisphere": hemi,
                "network": network,
                "component": "cortex",
            }
        )
    return pd.DataFrame(rows)


def _load_tian_labels(scale: int) -> pd.DataFrame:
    """Parse Tian subcortex label file (one label per line, 1-based)."""
    label_file = TIAN_SRC / f"Tian_Subcortex_S{scale}_3T_label.txt"
    labels = [ln for ln in label_file.read_text().splitlines() if ln.strip()]
    rows = []
    for i, label in enumerate(labels, start=1):
        hemi = "R" if label.endswith("-rh") else "L"
        rows.append(
            {
                "index": i,
                "label": label,
                "name": label,
                "hemisphere": hemi,
                "network": "subcortex",
                "component": "subcortex",
            }
        )
    return pd.DataFrame(rows)


def _combine_niftis(cortex_path: Path, subcortex_path: Path, n_parcels: int, out_path: Path) -> None:
    """Merge cortex (indices 1..N) and subcortex (indices N+1..N+S) NIfTIs."""
    cortex_img = nib.load(cortex_path)
    subcortex_img = nib.load(subcortex_path)

    cortex_data = np.asarray(cortex_img.dataobj, dtype=np.int32)
    subcortex_data = np.asarray(subcortex_img.dataobj, dtype=np.int32)

    if cortex_data.shape != subcortex_data.shape:
        from nibabel.processing import resample_from_to

        subcortex_img = resample_from_to(subcortex_img, cortex_img, order=0)
        subcortex_data = np.asarray(subcortex_img.dataobj, dtype=np.int32)

    subcortex_offset = np.where(subcortex_data > 0, subcortex_data + n_parcels, 0)
    combined = np.where(cortex_data > 0, cortex_data, subcortex_offset)

    nib.save(
        nib.Nifti1Image(combined, cortex_img.affine, cortex_img.header),
        out_path,
    )


def _get_surface_gifti(n: int, hemi: str) -> Path:
    """Return TemplateFlow-cached path for the fsaverage 164k Schaefer GIFTI.

    Filters all fsaverage Schaefer label.gii files for 7-network and the
    requested parcel count and hemisphere.
    """
    import templateflow.api as tflow

    files = tflow.get("fsaverage", atlas="Schaefer2018", suffix="dseg", extension=".label.gii")
    if not isinstance(files, list):
        files = [files] if files else []

    # Pattern unique to 7-network, correct scale and hemisphere (164k only available density)
    target = f"hemi-{hemi}_den-164k_atlas-Schaefer2018_seg-7n_scale-{n}_"
    matches = [Path(f) for f in files if target in str(f)]

    if not matches:
        raise FileNotFoundError(
            f"No fsaverage 164k Schaefer {n}-parcel 7-network GIFTI found for hemi-{hemi}. "
            "Run: templateflow.api.get('fsaverage', atlas='Schaefer2018', suffix='dseg')"
        )
    return matches[0]


def build(base: Path) -> None:
    download_sourcedata()

    for n in PARCELS:
        schaefer_df = _load_schaefer_labels(n)
        cortex_nii = _nii_path(n)

        # Fetch surface GIFTIs once per parcel count (shared across all Tian scales)
        surface_giis = {hemi: _get_surface_gifti(n, hemi) for hemi in ("L", "R")}

        for scale in SCALES:
            atlas_name = f"Schaefer2018N{n}n7Tian2020S{scale}"
            out_dir = ensure_atlas_dir(base, atlas_name)

            subcortex_nii = TIAN_SRC / f"Tian_Subcortex_S{scale}_3T_2009cAsym_1mm.nii.gz"
            dst_nii = out_dir / f"atlas-{atlas_name}_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz"
            _combine_niftis(cortex_nii, subcortex_nii, n, dst_nii)

            tian_df = _load_tian_labels(scale).copy()
            tian_df["index"] += n
            df = (
                pd.concat([schaefer_df, tian_df], ignore_index=True)
                .sort_values("index")
                .reset_index(drop=True)
            )
            write_tsv(df, out_dir / f"atlas-{atlas_name}_dseg.tsv")

            # Copy cortex-only surface GIFTIs (indices 1..N match volumetric cortex labels)
            for hemi, src_gii in surface_giis.items():
                dst_gii = out_dir / (
                    f"atlas-{atlas_name}_space-fsaverage_den-164k_hemi-{hemi}_dseg.label.gii"
                )
                safe_copy(src_gii, dst_gii)

            print(f"  [Schaefer2018N{n}n7TianS{scale}] {len(df)} regions → {out_dir.name}/")
