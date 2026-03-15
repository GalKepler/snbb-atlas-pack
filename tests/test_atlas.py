"""Tests for the atlas fetcher API (_atlas.py)."""

import pytest
from pathlib import Path

import snbb_atlas_pack as snbb
from snbb_atlas_pack._atlas import AtlasResult
from .conftest import requires_data


# ---------------------------------------------------------------------------
# list_atlases
# ---------------------------------------------------------------------------

def test_list_atlases_count():
    assert len(snbb.list_atlases()) == 46


def test_list_atlases_is_sorted():
    atlases = snbb.list_atlases()
    assert atlases == sorted(atlases)


def test_list_atlases_contains_known_ids():
    atlases = snbb.list_atlases()
    for aid in ["TianS1", "TianS2", "TianS3", "TianS4", "HCPex", "HCPMMP"]:
        assert aid in atlases


def test_list_atlases_contains_schaefer_combos():
    atlases = snbb.list_atlases()
    assert "Schaefer2018N100n7Tian2020S1" in atlases
    assert "Schaefer2018N1000n7Tian2020S4" in atlases


# ---------------------------------------------------------------------------
# get_atlas — error handling
# ---------------------------------------------------------------------------

def test_get_atlas_unknown_id_raises():
    with pytest.raises(KeyError, match="Unknown atlas"):
        snbb.get_atlas("DoesNotExist")


def test_get_atlas_volumetric_with_hemi_raises():
    with pytest.raises(ValueError, match="volumetric"):
        snbb.get_atlas("TianS1", hemi="L")


def test_get_atlas_schaefer_with_hemi_raises():
    with pytest.raises(ValueError, match="volumetric"):
        snbb.get_atlas("Schaefer2018N400n7Tian2020S2", hemi="R")


def test_get_atlas_invalid_hemi_raises():
    with pytest.raises(ValueError):
        snbb.get_atlas("HCPMMP", hemi="X")


# ---------------------------------------------------------------------------
# get_atlas — volumetric path structure
# ---------------------------------------------------------------------------

def test_get_atlas_returns_atlas_result():
    result = snbb.get_atlas("TianS1")
    assert isinstance(result, AtlasResult)


def test_get_atlas_volumetric_fields():
    result = snbb.get_atlas("TianS1")
    assert result.atlas_id == "TianS1"
    assert result.modality == "volumetric"
    assert result.space == "MNI152NLin2009cAsym"
    assert result.maps_R is None


def test_get_atlas_volumetric_maps_is_path():
    result = snbb.get_atlas("TianS1")
    assert isinstance(result.maps, Path)


def test_get_atlas_volumetric_maps_filename():
    result = snbb.get_atlas("TianS1")
    assert result.maps.name == "atlas-TianS1_space-MNI152NLin2009cAsym_res-01_dseg.nii.gz"


def test_get_atlas_schaefer_maps_filename():
    result = snbb.get_atlas("Schaefer2018N400n7Tian2020S2")
    assert "Schaefer2018N400n7Tian2020S2" in result.maps.name
    assert result.maps.name.endswith("_dseg.nii.gz")


# ---------------------------------------------------------------------------
# get_atlas — surface path structure
# ---------------------------------------------------------------------------

def test_get_atlas_surface_both_hemispheres():
    result = snbb.get_atlas("HCPMMP")
    assert result.modality == "surface"
    assert result.space == "fsLR"
    assert result.maps is not None
    assert result.maps_R is not None


def test_get_atlas_surface_hemi_l_filename():
    result = snbb.get_atlas("HCPMMP")
    assert "hemi-L" in result.maps.name
    assert "hemi-R" in result.maps_R.name


def test_get_atlas_surface_left_only():
    result = snbb.get_atlas("HCPMMP", hemi="L")
    assert "hemi-L" in result.maps.name
    assert result.maps_R is None


def test_get_atlas_surface_right_only():
    result = snbb.get_atlas("HCPMMP", hemi="R")
    assert "hemi-R" in result.maps.name
    assert result.maps_R is None


# ---------------------------------------------------------------------------
# Tests that require actual atlas data (skipped in CI)
# ---------------------------------------------------------------------------

@requires_data
def test_tian_s1_maps_exists():
    assert snbb.get_atlas("TianS1").maps.exists()


@requires_data
def test_hcpmmp_maps_exist():
    result = snbb.get_atlas("HCPMMP")
    assert result.maps.exists()
    assert result.maps_R.exists()


@requires_data
def test_tian_s1_labels_shape():
    result = snbb.get_atlas("TianS1")
    assert len(result.labels) == 16
    assert {"index", "label", "name", "hemisphere"}.issubset(result.labels.columns)


@requires_data
def test_tian_s2_labels_shape():
    assert len(snbb.get_atlas("TianS2").labels) == 32


@requires_data
def test_tian_s3_labels_shape():
    assert len(snbb.get_atlas("TianS3").labels) == 50


@requires_data
def test_tian_s4_labels_shape():
    assert len(snbb.get_atlas("TianS4").labels) == 54


@requires_data
def test_hcpex_labels_shape():
    result = snbb.get_atlas("HCPex")
    assert len(result.labels) == 426
    assert {"index", "label", "name", "hemisphere"}.issubset(result.labels.columns)


@requires_data
def test_hcpmmp_labels_shape():
    result = snbb.get_atlas("HCPMMP")
    assert len(result.labels) == 360
    assert {"index", "label", "name", "hemisphere"}.issubset(result.labels.columns)


@requires_data
def test_schaefer_n100_s1_labels_shape():
    result = snbb.get_atlas("Schaefer2018N100n7Tian2020S1")
    # 100 cortex + 16 subcortex = 116 total
    assert len(result.labels) == 116
