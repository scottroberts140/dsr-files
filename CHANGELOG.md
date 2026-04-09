# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-04-09

### Added

- Added `parquet_handler` for high-performance columnar data storage.
- Added support for `pyarrow` and `fastparquet` engines.
- Added `PageColors` and `PageConfiguration` documentation and validation tests for `pdf_handler`.

### Changed

- Upgraded all docstrings to **NumPy format** for better IDE support and consistency.
- Modernized type hints to use native union syntax (e.g., `str | Path`).
- Updated `to_JSON_safe` to recursively handle `np.ndarray` and `pd.Series`.
- Optimized `to_JSON_safe` by moving heavy library imports to the module level.
- Updated core dependencies to **Pandas 3.0.0**, **NumPy 2.1.0**, and **pypdf 6.9.2** for performance and security.
- Standardized `pd.testing.assert_frame_equal` in tests to use `check_dtype=False` for cross-engine compatibility.

## [2.1.0] - 2026-02-18

### Changed

- PDF dependencies (`reportlab`, `pypdf`, `matplotlib`, `pillow`) are now core dependencies instead of optional.
- Removed `pdf` optional dependency group as these packages are now always installed.

## [2.0.0] - 2026-02-10

### Breaking

- Renamed `filepath` argument to `output_dir` in all `save_*` functions to clearly indicate directory input.
- `load_*` functions now strictly validate file extensions and raise `ValueError` for mismatches.
- `load_*` functions now consistently raise `FileNotFoundError` if the file is missing.

### Added

- Added `validate_extension` utility function.
- Added `excel` optional dependency group (`openpyxl`, `xlsxwriter`).
- Added `pdf` optional dependency group (`reportlab`, `pypdf`, `matplotlib`, `pillow`).

### Changed

- PDF dependencies are now optional. Install with `pip install dsr-files[pdf]`.
- `save_excel` engine default changed to `"auto"` to use installed libraries (preferring `openpyxl` if available).
- `to_JSON_safe` now supports serialization of `Path`, `datetime`, `date`, and NumPy types.

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
