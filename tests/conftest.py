"""Shared fixtures and data-availability markers for the test suite.

Tests decorated with ``@requires_data`` are skipped unless the atlas TSV
files have been fetched from git-annex (i.e. they are real files, not broken
symlinks).  This lets CI pass with a plain ``git checkout`` while still
exercising file-system behaviour in development and on a full DataLad clone.
"""

import pytest
from pathlib import Path

_ATLAS_DIR = Path(__file__).resolve().parent.parent / "atlases"


def _atlas_data_available() -> bool:
    """True when the TianS1 TSV is a real file (annex content fetched)."""
    tsv = _ATLAS_DIR / "atlas-TianS1" / "atlas-TianS1_dseg.tsv"
    try:
        return tsv.is_file() and tsv.stat().st_size > 100
    except OSError:
        return False


DATA_AVAILABLE = _atlas_data_available()

requires_data = pytest.mark.skipif(
    not DATA_AVAILABLE,
    reason="atlas data not fetched — run `datalad get atlases/` first",
)
