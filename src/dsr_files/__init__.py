"""
dsr_files: File handling library for creating, saving, and loading various file types.

Supports CSV, JSON, JOBLIB, Excel, and PDF file operations.
"""

from dsr_files.enums import FileType
from dsr_files.csv_handler import (
    save_csv,
    load_csv,
    create_csv,
)
from dsr_files.excel_handler import (
    save_excel,
    load_excel,
    create_excel,
    ExcelSheetConfig,
)
from dsr_files.json_handler import (
    save_json,
    load_json,
    create_json,
    to_JSON_safe,
)
from dsr_files.joblib_handler import (
    save_joblib,
    load_joblib,
)
from dsr_files.pdf_handler import (
    save_pdf,
    load_pdf,
    PageOrientation,
    PageSize,
    PageColors,
    PageConfiguration,
    PDFDocument,
)

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
    "save_pdf",
    "load_pdf",
    "PageOrientation",
    "PageSize",
    "PageColors",
    "PageConfiguration",
    "PDFDocument",
]

__version__ = "1.0.3"
