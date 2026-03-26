"""Build the qsirecon_ext/ subset.

Contains only atlases that are NOT already shipped by QSIRecon/AtlasPack,
so it can be used as a supplemental atlas source for QSIRecon runs.
"""

import shutil
from pathlib import Path

# Atlas directory names already shipped by QSIRecon / PennLINC AtlasPack.
# These are excluded from qsirecon_ext/ because QSIRecon handles them natively.
QSIRECON_NATIVE = {
    "atlas-4S156Parcels",
    "atlas-4S256Parcels",
    "atlas-4S356Parcels",
    "atlas-4S456Parcels",
    "atlas-4S556Parcels",
    "atlas-4S656Parcels",
    "atlas-4S756Parcels",
    "atlas-4S856Parcels",
    "atlas-4S956Parcels",
    "atlas-4S1056Parcels",
    "atlas-AAL116",
    "atlas-AICHA384Ext",
    "atlas-Brainnetome246Ext",
    "atlas-Gordon333Ext",
}


def build(base: Path) -> None:
    atlases_dir = base / "atlases"
    ext_dir = base / "qsirecon_ext"

    # Clear and recreate qsirecon_ext/
    if ext_dir.exists():
        shutil.rmtree(ext_dir)
    ext_dir.mkdir()

    copied = 0
    for atlas_dir in sorted(atlases_dir.iterdir()):
        if not atlas_dir.is_dir() or atlas_dir.name in QSIRECON_NATIVE:
            continue
        shutil.copytree(atlas_dir, ext_dir / atlas_dir.name)
        copied += 1

    # Copy dataset metadata
    desc = atlases_dir / "dataset_description.json"
    if desc.exists():
        shutil.copy2(desc, ext_dir / "dataset_description.json")
    readme = atlases_dir / "README"
    if readme.exists():
        shutil.copy2(readme, ext_dir / "README")

    print(f"  [qsirecon_ext] {copied} atlases → qsirecon_ext/")
