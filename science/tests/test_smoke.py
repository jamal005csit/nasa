"""Stage 1 smoke test: the scaffold imports and the Python version is in the SPEC range.

Real tests arrive in Stage 2 (ingest/validate) and Stage 3 (stats engine).
"""

import sys


def test_package_imports() -> None:
    import earthnext

    assert earthnext.__version__ == "0.0.0"


def test_python_version_in_supported_range() -> None:
    assert (3, 11) <= sys.version_info[:2] < (3, 13), (
        f"SPEC requires Python 3.11 or 3.12; got {sys.version_info[:3]}"
    )
