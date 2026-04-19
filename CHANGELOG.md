# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-04-19

### Added

- **Configuration-Driven Parameter Filtering**: Introduced a centralized `params.yaml` registry to define valid arguments for various file engines, ensuring strict validation through the `UniqueKeyLoader`.
- **High-Performance Registry Caching**: Implemented `lru_cache` for internal parameter retrieval to eliminate redundant disk I/O and set-conversion overhead during high-frequency I/O operations.
- **Defensive Parameter Validation**: Added a private `_get_valid_params` helper with "fail-fast" `ValueError` reporting to catch unsupported `FileType` configurations during development.

### Changed

- **Optimized `safe_call` Integration**: Refined all file handlers to automatically utilize YAML-defined `valid_params` when `safe_call=True` is enabled, resolving `**kwargs` passthrough issues in engines like Parquet and JSON.

## [3.0.0] - 2026-04-19

### BREAKING CHANGES

- **Signature Update**: `load_...` and `save_...` functions now return a tuple of `(result, rejected_params)` to accommodate calls when `safe_call=True` is enabled.
- **Dependency Requirement**: This version now requires `dsr-utils >= 1.6.0` to support the underlying reflection logic.

### Added

- **Cloud-Native Path Support**: Integrated `cloudpathlib` to provide polymorphic support for local and cloud filesystems (S3, GCS, Azure) via `AnyPath`.
- **Centralized Path Utilities**: Introduced `get_full_path` and the `MkDir` configuration object to standardize protocol-safe path joining and directory creation across all handlers.
- **Universal Parameter Filtering**: Integrated `dsr_utils.safe_call` into all I/O functions, leveraging `valid_params` for strict filtering on complex engines (JSON, Parquet).
- **Load/Save Logic Robustness**: Added `safe_call` support to all `load...` and `save_...` functions, ensuring that exporting data is as resilient to configuration drift as importing it.

## [2.3.0] - 2026-04-17

### Added

- **Enhanced Logical Validation**: Introduced `is_valid_extension` and `_check_single_type` to the `FileType` enum to allow for extension verification without filesystem access.
- **Expanded Extension Support**: Added support for modern data science extensions including `.jsonl` for JSON, and `.pq` for Parquet.
- **Excel Compatibility**: Added recognition for various Microsoft Excel formats, including `.xlsx`, `.xls`, `.xlsm`, and `.xlsb`.
- **Multi-part Joblib Support**: Explicitly added `.joblib.gz` to the valid extensions for `FileType.JOBLIB`.

### Changed

- **Case-Insensitive Validation**: Normalized extension checking to handle mixed-case inputs and optional leading dots (e.g., ".CSV" vs "csv").
- **Bitwise Flag Logic**: Optimized the `is_valid_extension` method to support validation against combined bitwise flags (e.g., `FileType.CSV` | `FileType.JSON`).

## [2.2.0] - 2026-04-14

### Added

- **Strict YAML Loading**: Introduced the UniqueKeyLoader class to the yaml_handler module to prevent duplicate keys in configuration files.

- **Integrity Validation**: The new loader ensures that human-edited YAML files (like recommendations.yaml) do not contain conflicting entries, which could otherwise lead to unpredictable model auditing behavior.

- **Enhanced Error Reporting**: Implemented explicit raising of ConstructorError when duplicate keys are detected during the parsing phase, aiding in faster debugging for the "Human-in-the-Loop" workflow.

### Changed

- **Default Loader Strategy**: Updated internal yaml_handler functions to utilize the UniqueKeyLoader by default, standardizing configuration integrity across the project.

## [2.1.0] - 2026-04-13

### Added

- **YAML Handler**: Added `save_yaml` and `load_yaml` to support standardized configuration management.
- **Serialization Parity**: Extended the reach of the existing recursive serialization logic to the YAML handler, ensuring that Enums, Paths, and NumPy types are handled with the same rigor as JSON.
- **Unit Testing**: Added a comprehensive test suite in `tests/test_yaml_handler.py` to verify data integrity during round-trip serialization.

### Changed

- **Internal Consistency**: Standardized file-handling patterns to match existing CSV and Parquet loaders, ensuring uniform encoding and error handling across the library.

### Fixed

- Updated ```__init__.py``` to include PARQUET files.

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
