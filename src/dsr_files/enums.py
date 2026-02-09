"""Enumerations for dsr-files."""

from enum import Flag, auto


class FileType(Flag):
    """Supported file formats for dsr-files handlers."""

    CSV = auto()
    JSON = auto()
    JOBLIB = auto()
    PDF = auto()
    EXCEL = auto()
