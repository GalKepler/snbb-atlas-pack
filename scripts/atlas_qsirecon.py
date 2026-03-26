"""Import QSIRecon/AtlasPack atlases into the SNBB Atlas Pack.

Copies atlas files from the locally-cloned qsirecon_atlases/ directory
into atlases/ so that atlases/ is a single source of truth for all atlases.

Sources:
  - qsirecon_atlases/atlas/AtlasPack/  — 4S series (4S156–4S1056 Parcels)
  - qsirecon_atlases/atlas/qsirecon_atlases/  — AAL116, AICHA384Ext, Gordon333Ext
"""

from pathlib import Path

from scripts.utils import safe_copy

_BASE = Path(__file__).parent.parent
ATLASPACK_SRC = _BASE / "qsirecon_atlases" / "atlas" / "AtlasPack"
QSIRECON_SRC = _BASE / "qsirecon_atlases" / "atlas" / "qsirecon_atlases"

_4S_SIZES = [156, 256, 356, 456, 556, 656, 756, 856, 956, 1056]
_SIMPLE_ATLASES = ["AAL116", "AICHA384Ext", "Gordon333Ext"]


def _copy_atlas(src: Path, dst: Path) -> None:
    """Copy all files from src atlas dir into dst atlas dir."""
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.is_file():
            safe_copy(f, dst / f.name)


def build(base: Path) -> None:
    atlases_dir = base / "atlases"

    # 4S series (Schaefer cortex + CIT168 subcortex + more)
    for size in _4S_SIZES:
        atlas_name = f"4S{size}Parcels"
        src = ATLASPACK_SRC / f"atlas-{atlas_name}"
        if not src.exists():
            print(f"  [WARN] {src} not found, skipping")
            continue
        dst = atlases_dir / f"atlas-{atlas_name}"
        _copy_atlas(src, dst)
        print(f"  [{atlas_name}] → {dst.name}/")

    # Simple volumetric atlases from qsirecon_atlases
    for name in _SIMPLE_ATLASES:
        src = QSIRECON_SRC / f"atlas-{name}"
        if not src.exists():
            print(f"  [WARN] {src} not found, skipping")
            continue
        dst = atlases_dir / f"atlas-{name}"
        _copy_atlas(src, dst)
        print(f"  [{name}] → {dst.name}/")
