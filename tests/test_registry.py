"""Tests for the internal atlas registry (_registry.py)."""

from snbb_atlas_pack._registry import _REGISTRY, AtlasMeta


def test_registry_total_count():
    assert len(_REGISTRY) == 46


def test_tian_scales_present():
    for s in range(1, 5):
        assert f"TianS{s}" in _REGISTRY


def test_named_atlases_present():
    assert "HCPex" in _REGISTRY
    assert "HCPMMP" in _REGISTRY


def test_schaefer_tian_all_combos():
    for n in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
        for s in [1, 2, 3, 4]:
            assert f"Schaefer2018N{n}n7Tian2020S{s}" in _REGISTRY


def test_tian_s1_metadata():
    meta = _REGISTRY["TianS1"]
    assert isinstance(meta, AtlasMeta)
    assert meta.atlas_id == "TianS1"
    assert meta.dir_name == "atlas-TianS1"
    assert meta.space == "MNI152NLin2009cAsym"
    assert meta.modality == "volumetric"
    assert meta.has_subcortical_mesh is True
    assert meta.has_cortical_mesh is False
    assert meta.subcortical_mesh_is_tian is None


def test_hcpex_metadata():
    meta = _REGISTRY["HCPex"]
    assert meta.modality == "volumetric"
    assert meta.space == "MNI152NLin2009cAsym"
    assert meta.has_subcortical_mesh is True
    assert meta.has_cortical_mesh is True
    assert meta.subcortical_mesh_is_tian is None


def test_hcpmmp_metadata():
    meta = _REGISTRY["HCPMMP"]
    assert meta.modality == "surface"
    assert meta.space == "fsLR"
    assert meta.has_cortical_mesh is True
    assert meta.has_subcortical_mesh is False


def test_schaefer_tian_reuses_tian_mesh():
    for s in [1, 2, 3, 4]:
        meta = _REGISTRY[f"Schaefer2018N100n7Tian2020S{s}"]
        assert meta.subcortical_mesh_is_tian == f"TianS{s}"

    meta_big = _REGISTRY["Schaefer2018N1000n7Tian2020S4"]
    assert meta_big.subcortical_mesh_is_tian == "TianS4"


def test_schaefer_tian_modality():
    meta = _REGISTRY["Schaefer2018N400n7Tian2020S2"]
    assert meta.modality == "volumetric"
    assert meta.space == "MNI152NLin2009cAsym"
    assert meta.has_subcortical_mesh is True
    assert meta.has_cortical_mesh is True


def test_all_entries_have_required_fields():
    for atlas_id, meta in _REGISTRY.items():
        assert meta.atlas_id == atlas_id
        assert meta.dir_name.startswith("atlas-")
        assert meta.space in ("MNI152NLin2009cAsym", "fsLR")
        assert meta.modality in ("volumetric", "surface")
