# API Reference

The `snbb_atlas_pack` package provides a programmatic interface for accessing the SNBB Atlas Pack from Python, modelled on the [templateflow](https://www.templateflow.org/) / [nilearn](https://nilearn.github.io/) fetcher pattern.

```python
import snbb_atlas_pack as snbb
```

---

## Atlas fetcher

### `list_atlases()`

Return a sorted list of all available atlas IDs.

```python
snbb.list_atlases()
# ['HCPMMP', 'HCPex', 'Schaefer2018N1000n7Tian2020S1', ..., 'TianS4']
```

**Returns:** `list[str]`

---

### `get_atlas(atlas_id, hemi=None)`

Fetch image path(s) and the region labels table for an atlas.

| Parameter | Type | Description |
|-----------|------|-------------|
| `atlas_id` | `str` | Atlas identifier (from `list_atlases()`) |
| `hemi` | `"L"` \| `"R"` \| `None` | Surface atlases only. `None` returns both hemispheres. Must be `None` for volumetric atlases. |

**Returns:** [`AtlasResult`](#atlasresult)

**Raises:**
- `KeyError` — unknown `atlas_id`
- `ValueError` — `hemi` set for a volumetric atlas, or invalid value

```python
# Volumetric atlas
atlas = snbb.get_atlas("TianS1")
atlas.maps        # Path to .nii.gz
atlas.maps_R      # None (volumetric)
atlas.labels      # pd.DataFrame with index, label, name, hemisphere, …
atlas.space       # 'MNI152NLin2009cAsym'
atlas.modality    # 'volumetric'

# Surface atlas — both hemispheres
hcpmmp = snbb.get_atlas("HCPMMP")
hcpmmp.maps       # Path to hemi-L .label.gii
hcpmmp.maps_R     # Path to hemi-R .label.gii

# Surface atlas — single hemisphere
lh = snbb.get_atlas("HCPMMP", hemi="L")
lh.maps           # Path to hemi-L .label.gii
lh.maps_R         # None
```

---

### `AtlasResult`

Dataclass returned by `get_atlas()`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `atlas_id` | `str` | Atlas identifier |
| `maps` | `Path` | NIfTI path (volumetric) or LH GIFTI path (surface) |
| `maps_R` | `Path \| None` | RH GIFTI path for surface atlases; `None` otherwise |
| `labels` | `pd.DataFrame` | Contents of `*_dseg.tsv` |
| `space` | `str` | Template space name |
| `modality` | `str` | `"volumetric"` or `"surface"` |

`maps` is always a `Path` object — callers load images themselves:

```python
import nibabel as nib

atlas = snbb.get_atlas("TianS1")
img = nib.load(atlas.maps)        # NIfTI image
data = img.get_fdata()            # numpy array

gifti = nib.load(hcpmmp.maps)    # GIFTI image
labels = gifti.darrays[0].data   # vertex label array
```

---

## Mesh fetcher

Mesh fetchers return paths to the prebuilt [yabplot](https://github.com/GalKepler/yabplot) mesh directories under `derivatives/yabplot/`. These paths are passed directly to `yab.plot_subcortical()` or `yab.plot_cortical()`.

### `list_meshes()`

Return a mapping of atlas IDs to their already-built mesh components.

```python
snbb.list_meshes()
# {'HCPex': ['subcortical', 'cortical'], 'TianS1': ['subcortical'], …}
```

**Returns:** `dict[str, list[str]]` — only includes atlases with at least one built component.

---

### `get_mesh(atlas_id, component="subcortical")`

Return the path to a prebuilt yabplot mesh directory.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `atlas_id` | `str` | — | Atlas identifier |
| `component` | `"subcortical"` \| `"cortical"` | `"subcortical"` | Which mesh component to retrieve |

**Returns:** `Path`

**Raises:**
- `KeyError` — unknown `atlas_id`
- `FileNotFoundError` — mesh not yet built (call `build_meshes()` first)

!!! note "Schaefer+Tian subcortical mesh reuse"
    All 40 Schaefer+TianS{N} atlases share their subcortical meshes with the
    corresponding standalone Tian atlas. `get_mesh("Schaefer2018N400n7Tian2020S2", "subcortical")`
    returns the same directory as `get_mesh("TianS2")`.

```python
import yabplot as yab
import numpy as np

# Subcortical plot
mesh_dir = snbb.get_mesh("TianS1", component="subcortical")
atlas = snbb.get_atlas("TianS1")
data = np.random.rand(len(atlas.labels))   # one value per region

yab.plot_subcortical(
    data=data,
    custom_atlas_path=str(mesh_dir),
    export_path="figure.png",
    display_type="none",
)

# Cortical plot (HCPex)
mesh_dir = snbb.get_mesh("HCPex", component="cortical")
yab.plot_cortical(
    data=None,
    custom_atlas_path=str(mesh_dir),
    export_path="figure.png",
    display_type="none",
)
```

---

### `build_meshes(atlas_id=None)`

Build the yabplot mesh cache for one or all atlases. Wraps
`scripts/visualize_atlases.py` and handles the working-directory requirement.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `atlas_id` | `str \| None` | `None` | Build this atlas only. `None` builds all 46 atlases. |

```python
# Build a single atlas
snbb.build_meshes("TianS1")

# Build everything (slow — runs yabplot for all 46 atlases)
snbb.build_meshes()
```

!!! warning "Requires a display or off-screen renderer"
    `build_meshes()` uses VTK/yabplot internally. On headless servers, ensure
    VTK is configured for off-screen rendering (the build script handles this
    automatically via a monkey-patch).
