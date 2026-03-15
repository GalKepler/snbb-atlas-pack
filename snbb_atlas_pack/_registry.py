from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class AtlasMeta:
    atlas_id: str
    dir_name: str
    space: str
    modality: Literal["volumetric", "surface"]
    has_subcortical_mesh: bool
    has_cortical_mesh: bool
    subcortical_mesh_is_tian: str | None  # Schaefer combos reuse a Tian mesh


_REGISTRY: dict[str, AtlasMeta] = {
    "TianS1": AtlasMeta("TianS1", "atlas-TianS1", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "TianS2": AtlasMeta("TianS2", "atlas-TianS2", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "TianS3": AtlasMeta("TianS3", "atlas-TianS3", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "TianS4": AtlasMeta("TianS4", "atlas-TianS4", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "HCPex":  AtlasMeta("HCPex",  "atlas-HCPex",  "MNI152NLin2009cAsym", "volumetric", True, True,  None),
    "HCPMMP": AtlasMeta("HCPMMP", "atlas-HCPMMP", "fsLR",                "surface",    False, True,  None),
}

for _n in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
    for _s in [1, 2, 3, 4]:
        _aid = f"Schaefer2018N{_n}n7Tian2020S{_s}"
        _REGISTRY[_aid] = AtlasMeta(
            _aid,
            f"atlas-{_aid}",
            "MNI152NLin2009cAsym",
            "volumetric",
            True,
            True,
            f"TianS{_s}",
        )
