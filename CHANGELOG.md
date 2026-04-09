# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-09

### Breaking

- Renamed `filepath` argument to `output_dir` in all `save_*` functions to clearly indicate directory input.
- `load_*` functions now strictly validate file extensions and raise `ValueError` for mismatches.
- `load_*` functions now consistently raise `FileNotFoundError` if the file is missing.
- Upgraded project dependencies to **Pandas 3.0.0+** and **NumPy 2.1.0+**.

### Added

- Added `parquet_handler` for high-performance columnar data storage.
- Added support for `pyarrow` and `fastparquet` engines.
- Added `validate_extension` utility function.
- Added `PDFDocument` orchestration for interactive, indexed reports with clickable TOCs.
- Added `excel` optional dependency group (`openpyxl`, `xlsxwriter`).

### Changed

- PDF dependencies (`reportlab`, `pypdf`, `matplotlib`, `pillow`) are now core dependencies.
- Standardized all docstrings to **NumPy format**.
- Modernized type hints to use native union syntax (e.g., `str | Path`).
- Enhanced `to_JSON_safe` to recursively handle `np.ndarray`, `pd.Series`, and `Path` objects.
- Updated `save_excel` engine default to `"auto"`.
- Standardized `pd.testing.assert_frame_equal` in tests to use `check_dtype=False` for cross-engine compatibility.

## [1.0.3] - 2026-02-09

### Fixed

- Added Python version classifiers to improve PyPI badge metadata.

## [1.0.2] - 2026-02-09

### Fixed

- Added Python version classifiers to improve PyPI badge metadata.

## [1.0.0] - 2026-02-08

### Breaking

- Version reset to 1.0.0 to reflect non-backward-compatible changes across the library.

### Fixed

- Tests and documentation aligned with current save/load helper signatures.
