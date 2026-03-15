"""Tests for the mesh fetcher API (_mesh.py)."""

import pytest
from pathlib import Path

import snbb_atlas_pack as snbb
import snbb_atlas_pack._mesh as _mesh_mod
from snbb_atlas_pack._mesh import DERIV_DIR
from .conftest import requires_data


# ---------------------------------------------------------------------------
# get_mesh — error handling
# ---------------------------------------------------------------------------

def test_get_mesh_unknown_id_raises():
    with pytest.raises(KeyError):
        snbb.get_mesh("DoesNotExist")


def test_get_mesh_missing_raises_file_not_found(tmp_path, monkeypatch):
    """FileNotFoundError is raised when the mesh directory doesn't exist."""
    monkeypatch.setattr(_mesh_mod, "DERIV_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="Mesh not built"):
        snbb.get_mesh("TianS1")


def test_get_mesh_schaefer_missing_raises(tmp_path, monkeypatch):
    """Schaefer atlas reuses TianS mesh — same error if Tian mesh missing."""
    monkeypatch.setattr(_mesh_mod, "DERIV_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="Mesh not built"):
        snbb.get_mesh("Schaefer2018N400n7Tian2020S2")


def test_get_mesh_error_message_contains_atlas_id(tmp_path, monkeypatch):
    monkeypatch.setattr(_mesh_mod, "DERIV_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="TianS1"):
        snbb.get_mesh("TianS1")


def test_get_mesh_error_suggests_build_meshes(tmp_path, monkeypatch):
    monkeypatch.setattr(_mesh_mod, "DERIV_DIR", tmp_path)
    with pytest.raises(FileNotFoundError, match="build_meshes"):
        snbb.get_mesh("TianS1")


def test_get_mesh_returns_path_when_exists(tmp_path, monkeypatch):
    """get_mesh returns the directory path when it exists."""
    fake_dir = tmp_path / "atlas-TianS1"
    fake_dir.mkdir()
    monkeypatch.setattr(_mesh_mod, "DERIV_DIR", tmp_path)
    result = snbb.get_mesh("TianS1")
    assert result == fake_dir


def test_get_mesh_schaefer_reuses_tian_dir(tmp_path, monkeypatch):
    """Schaefer+TianS2 subcortical mesh points to atlas-TianS2/ directory."""
    tian_dir = tmp_path / "atlas-TianS2"
    tian_dir.mkdir()
    monkeypatch.setattr(_mesh_mod, "DERIV_DIR", tmp_path)
    result = snbb.get_mesh("Schaefer2018N400n7Tian2020S2", component="subcortical")
    assert result == tian_dir


def test_get_mesh_hcpex_subcortical_dir(tmp_path, monkeypatch):
    """HCPex subcortical mesh lives in atlas-HCPex/subcortical/."""
    hcpex_sub = tmp_path / "atlas-HCPex" / "subcortical"
    hcpex_sub.mkdir(parents=True)
    monkeypatch.setattr(_mesh_mod, "DERIV_DIR", tmp_path)
    result = snbb.get_mesh("HCPex", component="subcortical")
    assert result == hcpex_sub


# ---------------------------------------------------------------------------
# list_meshes
# ---------------------------------------------------------------------------

def test_list_meshes_returns_dict():
    result = snbb.list_meshes()
    assert isinstance(result, dict)


def test_list_meshes_values_are_lists_of_strings():
    for atlas_id, components in snbb.list_meshes().items():
        assert isinstance(atlas_id, str)
        assert isinstance(components, list)
        assert all(c in ("subcortical", "cortical") for c in components)


def test_list_meshes_only_known_atlas_ids():
    import snbb_atlas_pack
    all_ids = set(snbb_atlas_pack.list_atlases())
    for atlas_id in snbb.list_meshes():
        assert atlas_id in all_ids


# ---------------------------------------------------------------------------
# Tests that require actual mesh data (skipped in CI)
# ---------------------------------------------------------------------------

_tian_s1_mesh = DERIV_DIR / "atlas-TianS1"
requires_meshes = pytest.mark.skipif(
    not _tian_s1_mesh.exists(),
    reason="mesh derivatives not built — run `snbb_atlas_pack.build_meshes()` first",
)


@requires_meshes
def test_get_mesh_tian_returns_existing_path():
    result = snbb.get_mesh("TianS1")
    assert result.exists()
    assert result.is_dir()


@requires_meshes
def test_list_meshes_includes_tian_when_built():
    result = snbb.list_meshes()
    assert "TianS1" in result
    assert "subcortical" in result["TianS1"]
