from dataclasses import dataclass
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
    labels: pd.DataFrame
    space: str
    modality: str


def get_atlas(
    atlas_id: str,
    hemi: Literal["L", "R"] | None = None,
) -> AtlasResult:
    """Fetch atlas image path(s) and labels DataFrame.

    Parameters
    ----------
    atlas_id:
        Atlas identifier, e.g. ``'TianS1'``, ``'HCPMMP'``.
    hemi:
        For surface atlases, return only this hemisphere (``'L'`` or ``'R'``).
        ``None`` (default) returns both hemispheres (``maps`` = LH, ``maps_R`` = RH).
        Must be ``None`` for volumetric atlases.

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

    if meta.modality == "volumetric":
        if hemi is not None:
            raise ValueError(
                f"Atlas {atlas_id!r} is volumetric; 'hemi' must be None, got {hemi!r}."
            )
        img_path = atlas_dir / f"{meta.dir_name}_space-{meta.space}_res-01_dseg.nii.gz"
        maps = img_path
        maps_R = None
    else:
        if hemi is None:
            maps = atlas_dir / f"{meta.dir_name}_space-{meta.space}_hemi-L_dseg.label.gii"
            maps_R = atlas_dir / f"{meta.dir_name}_space-{meta.space}_hemi-R_dseg.label.gii"
        elif hemi == "L":
            maps = atlas_dir / f"{meta.dir_name}_space-{meta.space}_hemi-L_dseg.label.gii"
            maps_R = None
        elif hemi == "R":
            maps = atlas_dir / f"{meta.dir_name}_space-{meta.space}_hemi-R_dseg.label.gii"
            maps_R = None
        else:
            raise ValueError(f"hemi must be 'L', 'R', or None, got {hemi!r}.")

    tsv_path = atlas_dir / f"{meta.dir_name}_dseg.tsv"
    labels = pd.read_csv(tsv_path, sep="\t")

    return AtlasResult(
        atlas_id=atlas_id,
        maps=maps,
        maps_R=maps_R,
        labels=labels,
        space=meta.space,
        modality=meta.modality,
    )


def list_atlases() -> list[str]:
    """Return sorted list of available atlas IDs."""
    return sorted(_REGISTRY.keys())
