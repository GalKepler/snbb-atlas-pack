from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import pandas as pd

from ._registry import _REGISTRY, AtlasMeta

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class AtlasResult:
    atlas_id: str
    maps: Path
    maps_R: Path | None
    space: str
    modality: str
    _tsv_path: Path = field(repr=False)

    @property
    def labels(self) -> pd.DataFrame:
        return pd.read_csv(self._tsv_path, sep="\t")


def get_atlas(
    atlas_id: str,
    hemi: Literal["L", "R"] | None = None,
    modality: Literal["volumetric", "surface"] | None = None,
) -> AtlasResult:
    """Fetch atlas image path(s) and labels DataFrame.

    Parameters
    ----------
    atlas_id:
        Atlas identifier, e.g. ``'TianS1'``, ``'HCPMMP'``,
        ``'Schaefer2018N100n7Tian2020S1'``.
    hemi:
        For surface atlases, return only this hemisphere (``'L'`` or ``'R'``).
        ``None`` (default) returns both hemispheres (``maps`` = LH, ``maps_R`` = RH).
        Must be ``None`` when the effective modality is volumetric.
    modality:
        ``'volumetric'`` or ``'surface'``. Only relevant for atlases that have
        both modalities (e.g. Schaefer+Tian, Brainnetome246Ext). When ``None``,
        volumetric is returned for atlases with both modalities; purely surface
        atlases (HCPMMP) always return surface.

    Returns
    -------
    AtlasResult
        Dataclass with ``maps``, ``maps_R``, ``labels``, ``space``, ``modality``.
    """
    if atlas_id not in _REGISTRY:
        raise KeyError(
            f"Unknown atlas {atlas_id!r}. "
            f"Call list_atlases() to see available atlases."
        )
    meta: AtlasMeta = _REGISTRY[atlas_id]
    atlas_dir = BASE_DIR / "atlases" / meta.dir_name

    # Determine effective modality
    if modality is not None:
        if modality not in ("volumetric", "surface"):
            raise ValueError(f"modality must be 'volumetric' or 'surface', got {modality!r}.")
        if modality == "surface" and meta.surface_space is None:
            raise ValueError(
                f"Atlas {atlas_id!r} has no surface version (surface_space is None)."
            )
        if modality == "volumetric" and meta.modality == "surface":
            raise ValueError(
                f"Atlas {atlas_id!r} is surface-only; cannot request volumetric modality."
            )
        effective = modality
    else:
        # Default: volumetric when available, else surface
        if meta.modality == "surface":
            effective = "surface"
        else:
            effective = "volumetric"

    tsv_path = atlas_dir / f"{meta.dir_name}_dseg.tsv"

    if effective == "volumetric":
        if hemi is not None:
            raise ValueError(
                f"Atlas {atlas_id!r} is being returned as volumetric; "
                f"'hemi' must be None for volumetric maps, got {hemi!r}. "
                f"Pass modality='surface' to request surface files."
            )
        img_path = atlas_dir / f"{meta.dir_name}_space-{meta.space}_res-01_dseg.nii.gz"
        return AtlasResult(
            atlas_id=atlas_id,
            maps=img_path,
            maps_R=None,
            space=meta.space,
            modality="volumetric",
            _tsv_path=tsv_path,
        )

    # Surface path — build filename based on surface format
    surf_space = meta.surface_space

    if meta.surface_format == "cifti":
        # CIFTI is a single bilateral file; hemi does not apply
        if hemi is not None:
            raise ValueError(
                f"Atlas {atlas_id!r} uses CIFTI surface format; "
                f"'hemi' must be None, got {hemi!r}."
            )
        den_part = f"_den-{meta.surface_den}" if meta.surface_den else ""
        cifti_fname = f"{meta.dir_name}_space-{surf_space}{den_part}_dseg.dlabel.nii"
        return AtlasResult(
            atlas_id=atlas_id,
            maps=atlas_dir / cifti_fname,
            maps_R=None,
            space=surf_space,
            modality="surface",
            _tsv_path=tsv_path,
        )

    # Per-hemisphere surface path (GIFTI or .annot) — optional den entity
    _ext = "_dseg.annot" if meta.surface_format == "annot" else "_dseg.label.gii"
    if meta.surface_den:
        def _surf_fname(h: str) -> str:
            return f"{meta.dir_name}_space-{surf_space}_den-{meta.surface_den}_hemi-{h}{_ext}"
    else:
        def _surf_fname(h: str) -> str:
            return f"{meta.dir_name}_space-{surf_space}_hemi-{h}{_ext}"

    if hemi is None:
        maps = atlas_dir / _surf_fname("L")
        maps_R = atlas_dir / _surf_fname("R")
    elif hemi == "L":
        maps = atlas_dir / _surf_fname("L")
        maps_R = None
    elif hemi == "R":
        maps = atlas_dir / _surf_fname("R")
        maps_R = None
    else:
        raise ValueError(f"hemi must be 'L', 'R', or None, got {hemi!r}.")

    return AtlasResult(
        atlas_id=atlas_id,
        maps=maps,
        maps_R=maps_R,
        space=surf_space,
        modality="surface",
        _tsv_path=tsv_path,
    )


def list_atlases() -> list[str]:
    """Return sorted list of available atlas IDs."""
    return sorted(_REGISTRY.keys())
