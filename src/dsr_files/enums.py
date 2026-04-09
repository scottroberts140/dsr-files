"""
Enumerations for file handling and type identification.

This module defines the supported file formats used across the
dsr-files library for reading, writing, and auditing.
"""

from enum import Flag, auto


class FileType(Flag):
    """
    Bitwise flags representing supported file formats.

    Using Flag allows for combining multiple file types using bitwise
    operators (e.g., FileType.CSV | FileType.JSON), which is useful
    for filtering or multi-format processing pipelines.

    Attributes
    ----------
    CSV : auto
        Comma-Separated Values format.
    JSON : auto
        JavaScript Object Notation format.
    JOBLIB : auto
        Joblib serialized Python objects (often used for ML models).
    PDF : auto
        Portable Document Format (used for report generation).
    EXCEL : auto
        Microsoft Excel spreadsheet format (.xlsx).
    PARQUET : auto
        Apache Parquet columnar storage format (highly optimized for large datasets).
    """

    CSV = auto()
    JSON = auto()
    JOBLIB = auto()
    PDF = auto()
    EXCEL = auto()
    PARQUET = auto()
