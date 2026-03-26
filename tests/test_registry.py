"""Tests for the internal atlas registry (_registry.py)."""

from snbb_atlas_pack._registry import _REGISTRY, AtlasMeta


def test_registry_total_count():
    # 4 Tian + 1 HCPex + 1 HCPMMP + 1 Brainnetome246Ext
    # + 40 Schaefer+Tian + 10 4S + 3 QSIRecon (AAL116, AICHA384Ext, Gordon333Ext)
    # + 10 Schaefer standalone surface + 2 subcortical (4SSubcortical, HCPexSubcortex)
    assert len(_REGISTRY) == 72


def test_tian_scales_present():
    for s in range(1, 5):
        assert f"TianS{s}" in _REGISTRY


def test_named_atlases_present():
    assert "HCPex" in _REGISTRY
    assert "HCPMMP" in _REGISTRY
    assert "Brainnetome246Ext" in _REGISTRY


def test_qsirecon_atlases_present():
    assert "AAL116" in _REGISTRY
    assert "AICHA384Ext" in _REGISTRY
    assert "Gordon333Ext" in _REGISTRY
    for size in [156, 256, 356, 456, 556, 656, 756, 856, 956, 1056]:
        assert f"4S{size}Parcels" in _REGISTRY


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
    assert meta.surface_space is None


def test_hcpex_metadata():
    meta = _REGISTRY["HCPex"]
    assert meta.modality == "volumetric"
    assert meta.space == "MNI152NLin2009cAsym"
    assert meta.has_subcortical_mesh is True
    assert meta.has_cortical_mesh is True
    assert meta.subcortical_mesh_is_tian is None
    assert meta.surface_space is None


def test_hcpmmp_metadata():
    meta = _REGISTRY["HCPMMP"]
    assert meta.modality == "surface"
    assert meta.space == "fsLR"
    assert meta.has_cortical_mesh is True
    assert meta.has_subcortical_mesh is False
    assert meta.surface_space == "fsLR"
    assert meta.surface_den is None


def test_brainnetome_metadata():
    meta = _REGISTRY["Brainnetome246Ext"]
    assert meta.modality == "both"
    assert meta.space == "MNI152NLin2009cAsym"
    assert meta.surface_space == "fsLR"
    assert meta.surface_den is None


def test_schaefer_tian_reuses_tian_mesh():
    for s in [1, 2, 3, 4]:
        meta = _REGISTRY[f"Schaefer2018N100n7Tian2020S{s}"]
        assert meta.subcortical_mesh_is_tian == f"TianS{s}"

    meta_big = _REGISTRY["Schaefer2018N1000n7Tian2020S4"]
    assert meta_big.subcortical_mesh_is_tian == "TianS4"


def test_schaefer_tian_modality():
    meta = _REGISTRY["Schaefer2018N400n7Tian2020S2"]
    assert meta.modality == "both"
    assert meta.space == "MNI152NLin2009cAsym"
    assert meta.surface_space == "fsaverage"
    assert meta.surface_den == "164k"
    assert meta.has_subcortical_mesh is True
    assert meta.has_cortical_mesh is True


def test_4s_metadata():
    meta = _REGISTRY["4S456Parcels"]
    assert meta.modality == "volumetric"
    assert meta.space == "MNI152NLin2009cAsym"
    assert meta.surface_space is None


def test_schaefer_surface_atlases_present():
    for n in [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
        assert f"Schaefer2018N{n}" in _REGISTRY


def test_schaefer_surface_metadata():
    meta = _REGISTRY["Schaefer2018N400"]
    assert meta.modality == "surface"
    assert meta.space == "fsaverage"
    assert meta.surface_space == "fsaverage"
    assert meta.surface_den is None
    assert meta.surface_format == "annot"
    assert meta.has_cortical_mesh is True
    assert meta.has_subcortical_mesh is False
    assert meta.subcortical_mesh_is_tian is None


def test_subcortical_atlases_present():
    assert "4SSubcortical" in _REGISTRY
    assert "HCPexSubcortex" in _REGISTRY


def test_subcortical_metadata():
    for aid in ("4SSubcortical", "HCPexSubcortex"):
        meta = _REGISTRY[aid]
        assert meta.modality == "volumetric"
        assert meta.space == "MNI152NLin2009cAsym"
        assert meta.has_subcortical_mesh is True
        assert meta.has_cortical_mesh is False
        assert meta.surface_space is None


def test_all_entries_have_required_fields():
    valid_spaces = {"MNI152NLin2009cAsym", "fsLR", "fsaverage"}
    valid_modalities = {"volumetric", "surface", "both"}
    for atlas_id, meta in _REGISTRY.items():
        assert meta.atlas_id == atlas_id
        assert meta.dir_name.startswith("atlas-")
        assert meta.space in valid_spaces, f"{atlas_id} has unexpected space {meta.space!r}"
        assert meta.modality in valid_modalities, f"{atlas_id} has unexpected modality {meta.modality!r}"
        # Atlases with surface must have surface_space set
        if meta.modality in ("surface", "both"):
            assert meta.surface_space is not None, f"{atlas_id} modality={meta.modality!r} but surface_space is None"
