import shutil
from pathlib import Path

import pandas as pd


def ensure_atlas_dir(base: Path, atlas_name: str) -> Path:
    d = base / "atlases" / f"atlas-{atlas_name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_tsv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, sep="\t", index=False)


def safe_copy(src: Path, dst: Path) -> None:
    """Copy src to dst, removing any existing file or symlink at dst first.

    Necessary because git-annex marks objects read-only; a plain shutil.copy2
    to an annexed symlink destination raises PermissionError.
    """
    if dst.is_symlink() or dst.exists():
        dst.unlink()
    shutil.copy2(src, dst)
