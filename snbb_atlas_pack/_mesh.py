import os
from pathlib import Path
from typing import Literal

from ._registry import _REGISTRY

BASE_DIR = Path(__file__).resolve().parent.parent
DERIV_DIR = BASE_DIR / "derivatives" / "yabplot"


def get_mesh(
    atlas_id: str,
    component: Literal["subcortical", "cortical"] = "subcortical",
) -> Path:
    """Return path to yabplot-compatible mesh directory.

    Parameters
    ----------
    atlas_id:
        Atlas identifier, e.g. ``'TianS1'``, ``'HCPex'``.
    component:
        ``'subcortical'`` (default) or ``'cortical'``.

    Returns
    -------
    Path
        Directory containing prebuilt yabplot mesh files.

    Raises
    ------
    KeyError
        If ``atlas_id`` is not in the registry.
    FileNotFoundError
        If meshes have not been built yet.
    """
    if atlas_id not in _REGISTRY:
        raise KeyError(
            f"Unknown atlas {atlas_id!r}. "
            f"Call list_atlases() to see available atlases."
        )
    meta = _REGISTRY[atlas_id]

    if component == "subcortical":
        if meta.subcortical_mesh_is_tian is not None:
            tian_meta = _REGISTRY[meta.subcortical_mesh_is_tian]
            mesh_dir = DERIV_DIR / tian_meta.dir_name
        elif meta.atlas_id == "HCPex":
            mesh_dir = DERIV_DIR / meta.dir_name / "subcortical"
        else:
            mesh_dir = DERIV_DIR / meta.dir_name
    else:
        mesh_dir = DERIV_DIR / meta.dir_name

    if not mesh_dir.exists():
        raise FileNotFoundError(
            f"Mesh not built for {atlas_id!r} ({component}). "
            f"Run: snbb_atlas_pack.build_meshes({atlas_id!r})"
        )
    return mesh_dir


def build_meshes(atlas_id: str | None = None) -> None:
    """Build yabplot mesh cache.

    Parameters
    ----------
    atlas_id:
        Build meshes only for this atlas. ``None`` builds all atlases.
    """
    orig_cwd = os.getcwd()
    os.chdir(BASE_DIR)
    try:
        if atlas_id is None:
            from scripts.visualize_atlases import visualize_all
            visualize_all()
        else:
            _dispatch_build(atlas_id)
    finally:
        os.chdir(orig_cwd)


def _dispatch_build(atlas_id: str) -> None:
    from scripts.visualize_atlases import (
        build_and_plot_tian,
        build_and_plot_hcpex,
        build_and_plot_hcpmmp,
        build_and_plot_schaefer_tian,
    )
    if atlas_id.startswith("TianS"):
        build_and_plot_tian(atlas_id)
    elif atlas_id == "HCPex":
        build_and_plot_hcpex()
    elif atlas_id == "HCPMMP":
        build_and_plot_hcpmmp()
    elif atlas_id.startswith("Schaefer"):
        build_and_plot_schaefer_tian(atlas_id)
    else:
        raise ValueError(f"No build function known for atlas {atlas_id!r}.")


def list_meshes() -> dict[str, list[str]]:
    """Return ``{atlas_id: [built components]}`` for all cached meshes."""
    result: dict[str, list[str]] = {}
    for atlas_id, meta in _REGISTRY.items():
        built = []
        if meta.has_subcortical_mesh:
            if meta.subcortical_mesh_is_tian is not None:
                tian_meta = _REGISTRY[meta.subcortical_mesh_is_tian]
                sub_dir = DERIV_DIR / tian_meta.dir_name
            elif meta.atlas_id == "HCPex":
                sub_dir = DERIV_DIR / meta.dir_name / "subcortical"
            else:
                sub_dir = DERIV_DIR / meta.dir_name
            if sub_dir.exists():
                built.append("subcortical")
        if meta.has_cortical_mesh:
            cort_dir = DERIV_DIR / meta.dir_name
            if cort_dir.exists():
                built.append("cortical")
        if built:
            result[atlas_id] = built
    return result
