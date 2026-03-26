from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class AtlasMeta:
    atlas_id: str
    dir_name: str
    space: str  # primary/volumetric space
    modality: Literal["volumetric", "surface", "both"]
    has_subcortical_mesh: bool
    has_cortical_mesh: bool
    subcortical_mesh_is_tian: str | None
    # Surface-specific fields (None when no surface version available)
    surface_space: str | None = field(default=None)
    surface_den: str | None = field(default=None)  # e.g. "164k"; omitted from path when None
    surface_format: Literal["gifti", "cifti", "annot"] = field(default="gifti")


_REGISTRY: dict[str, AtlasMeta] = {
    # ------------------------------------------------------------------
    # Tian Melbourne Subcortex Atlas (S1–S4) — volumetric only
    # ------------------------------------------------------------------
    "TianS1": AtlasMeta("TianS1", "atlas-TianS1", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "TianS2": AtlasMeta("TianS2", "atlas-TianS2", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "TianS3": AtlasMeta("TianS3", "atlas-TianS3", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "TianS4": AtlasMeta("TianS4", "atlas-TianS4", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    # ------------------------------------------------------------------
    # HCPex — volumetric only (cortical + subcortical)
    # ------------------------------------------------------------------
    "HCPex":  AtlasMeta("HCPex",  "atlas-HCPex",  "MNI152NLin2009cAsym", "volumetric", True, True,  None),
    # ------------------------------------------------------------------
    # HCP-MMP 1.0 — surface only (fsLR 32k, cortical)
    # ------------------------------------------------------------------
    "HCPMMP": AtlasMeta(
        "HCPMMP", "atlas-HCPMMP", "fsLR", "surface", False, True, None,
        surface_space="fsLR", surface_den=None,
    ),
    # ------------------------------------------------------------------
    # Brainnetome246Ext — volumetric + surface (fsLR 32k)
    # ------------------------------------------------------------------
    "Brainnetome246Ext": AtlasMeta(
        "Brainnetome246Ext", "atlas-Brainnetome246Ext",
        "MNI152NLin2009cAsym", "both", True, True, None,
        surface_space="fsLR", surface_den=None,
    ),
    # ------------------------------------------------------------------
    # QSIRecon / AtlasPack — volumetric only
    # ------------------------------------------------------------------
    "AAL116":      AtlasMeta("AAL116",      "atlas-AAL116",      "MNI152NLin2009cAsym", "volumetric", False, False, None),
    "AICHA384Ext": AtlasMeta("AICHA384Ext", "atlas-AICHA384Ext", "MNI152NLin2009cAsym", "volumetric", False, False, None),
    "Gordon333Ext": AtlasMeta("Gordon333Ext", "atlas-Gordon333Ext", "MNI152NLin2009cAsym", "volumetric", False, False, None),
    # ------------------------------------------------------------------
    # Standalone subcortical atlases — volumetric only
    # ------------------------------------------------------------------
    "4SSubcortical": AtlasMeta("4SSubcortical", "atlas-4SSubcortical", "MNI152NLin2009cAsym", "volumetric", True, False, None),
    "HCPexSubcortex": AtlasMeta("HCPexSubcortex", "atlas-HCPexSubcortex", "MNI152NLin2009cAsym", "volumetric", True, False, None),
}

# 4S series (Schaefer cortex + CIT168 subcortex + HCP thalamus + more)
for _size in [156, 256, 356, 456, 556, 656, 756, 856, 956, 1056]:
    _aid = f"4S{_size}Parcels"
    _REGISTRY[_aid] = AtlasMeta(
        _aid, f"atlas-{_aid}", "MNI152NLin2009cAsym", "volumetric",
        False, False, None,
    )

# Schaefer2018+Tian2020 combined atlases — volumetric + surface (fsaverage 164k cortex)
for _n in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
    for _s in [1, 2, 3, 4]:
        _aid = f"Schaefer2018N{_n}n7Tian2020S{_s}"
        _REGISTRY[_aid] = AtlasMeta(
            _aid,
            f"atlas-{_aid}",
            "MNI152NLin2009cAsym",
            "both",
            True,
            True,
            f"TianS{_s}",
            surface_space="fsaverage",
            surface_den="164k",
        )

# Schaefer2018 standalone surface atlases — fsaverage .annot (FreeSurfer, cortex only)
for _n in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
    _aid = f"Schaefer2018N{_n}"
    _REGISTRY[_aid] = AtlasMeta(
        _aid,
        f"atlas-{_aid}",
        "fsaverage",
        "surface",
        False,
        True,
        None,
        surface_space="fsaverage",
        surface_den=None,
        surface_format="annot",
    )
