"""Tests for utility functions."""

from pathlib import Path

import pandas as pd
import pytest
from cloudpathlib import CloudPath
from dsr_files.csv_handler import MkDir, _get_valid_params, get_full_path, save_csv
from dsr_files.enums import FileType
from dsr_files.utils import _get_valid_param_sets


def test_validate_extension_success():
    """Verify validation passes for correct extensions."""
    # Should not raise any error
    FileType.CSV.validate_extension("data.csv")
    FileType.EXCEL.validate_extension("report.XLSX")
    FileType.JOBLIB.validate_extension("model.joblib")


def test_validate_extension_failure():
    """Verify ValueError is raised for mismatched extensions."""
    with pytest.raises(ValueError, match="Invalid file extension for CSV"):
        FileType.CSV.validate_extension("data.parquet")


def test_validate_extension_formatting():
    """Verify the utility handles extensions missing the leading dot."""
    FileType.PARQUET.validate_extension("data.parquet")


def test_get_full_path_local(tmp_path):
    """Verify local path construction and directory creation."""
    filename = "test.csv"
    # Ensure a new sub-directory is created
    target_dir = tmp_path / "new_subdir"

    result = get_full_path(target_dir, filename, MkDir(mkdir=True))

    assert isinstance(result, Path)
    assert result.name == filename
    assert target_dir.exists()


def test_get_full_path_s3_protocol():
    """Verify cloud protocol preservation and AnyPath conversion."""
    s3_dir = "s3://my-bucket/data"
    filename = "audit.parquet"

    # We use mkdir=False to avoid network calls during unit tests
    result = get_full_path(s3_dir, filename, MkDir(mkdir=False))

    assert isinstance(result, CloudPath)
    assert str(result).startswith("s3://")
    assert str(result).endswith(filename)


def test_get_full_path_no_mkdir(tmp_path):
    """Verify the mkdir=False flag is honored."""
    target_dir = tmp_path / "not_created"
    get_full_path(target_dir, "file.txt", MkDir(mkdir=False))

    assert not target_dir.exists()


def test_valid_param_registry_integrity():
    """Verify that the master YAML is loaded correctly and cached."""
    registry = _get_valid_param_sets()
    assert "csv" in registry
    assert "parquet" in registry
    # Verify the nested structure matches your notes
    assert "save" in registry["csv"]


def test_get_valid_params_caching():
    """Verify that the helper returns the correct set and honors the cache."""
    csv_save = _get_valid_params(FileType.CSV, "save")
    assert isinstance(csv_save, set)
    assert "sep" in csv_save

    # Second call should be near-instant via lru_cache
    assert _get_valid_params(FileType.CSV, "save") is csv_save


def test_get_valid_params_unsupported_type():
    """Verify that unsupported FileTypes raise a ValueError."""
    # Assuming PDF is not in your 'supported' set
    with pytest.raises(ValueError, match="does not support valid_params"):
        _get_valid_params(FileType.PDF, "save")


def test_csv_safe_call_with_yaml_filtering(tmp_path):
    """Verify end-to-end filtering using the YAML-defined valid_params."""
    df = pd.DataFrame({"a": [1]})

    # 'invalid_arg' is not in the CSV save list in params.yaml
    # 'sep' is in the list, but will be overridden by the handler's fixed logic
    _, rejected = save_csv(
        df,
        tmp_path,
        "test",
        safe_call=True,
        invalid_arg="ignore_me",
        float_format="%.2f",
    )

    assert "invalid_arg" in rejected
