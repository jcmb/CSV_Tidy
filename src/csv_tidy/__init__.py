"""CSV_Tidy — clean up CSV/TSV files by removing unhelpful columns."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

__all__ = ["__version__"]


def _read_version() -> str:
    try:
        return version("csv-tidy")
    except PackageNotFoundError:
        version_file = Path(__file__).resolve().parents[2] / "VERSION"
        if version_file.is_file():
            return version_file.read_text(encoding="utf-8").strip()
        return "0.1.0"


__version__ = _read_version()
