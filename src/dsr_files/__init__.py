"""
dsr_files: File handling library for creating, saving, and loading various file types.

Supports CSV, JSON, JOBLIB, PARQUET, YAML, Excel, and PDF file operations.
"""

from importlib.metadata import PackageNotFoundError, version

from dsr_files.csv_handler import create_csv, load_csv, save_csv
from dsr_files.enums import FileType
from dsr_files.excel_handler import (
    ExcelSheetConfig,
    create_excel,
    load_excel,
    save_excel,
)
from dsr_files.joblib_handler import load_joblib, save_joblib
from dsr_files.json_handler import create_json, load_json, save_json, to_JSON_safe
from dsr_files.parquet_handler import load_parquet, save_parquet
from dsr_files.utils import MkDir, get_full_path, validate_extension
from dsr_files.yaml_handler import load_yaml, save_yaml

try:
    from dsr_files.pdf_handler import (
        PageColors,
        PageConfiguration,
        PageOrientation,
        PageSize,
        PDFDocument,
        load_pdf,
        save_pdf,
    )
except ImportError:
    # Define placeholders if PDF dependencies are missing
    def _missing_pdf_dependency(*args, **kwargs):
        raise ImportError(
            "PDF dependencies are missing. Install with 'pip install dsr-files[pdf]'"
        )

    save_pdf = _missing_pdf_dependency
    load_pdf = _missing_pdf_dependency
    PageOrientation = None
    PageSize = None
    PageColors = None
    PageConfiguration = None
    PDFDocument = None

__all__ = [
    "FileType",
    "save_csv",
    "load_csv",
    "create_csv",
    "save_excel",
    "load_excel",
    "create_excel",
    "ExcelSheetConfig",
    "save_json",
    "load_json",
    "create_json",
    "to_JSON_safe",
    "save_joblib",
    "load_joblib",
    "save_parquet",
    "load_parquet",
    "load_yaml",
    "save_yaml",
    "validate_extension",
    "save_pdf",
    "load_pdf",
    "PageOrientation",
    "PageSize",
    "PageColors",
    "PageConfiguration",
    "PDFDocument",
    "MkDir",
    "get_full_path",
]

try:
    __version__ = version("dsr-files")
except PackageNotFoundError:
    __version__ = "unknown"
