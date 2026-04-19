"""Tests for utility functions."""

from pathlib import Path

import pytest
from cloudpathlib import CloudPath
from dsr_files.utils import MkDir, get_full_path, validate_extension


def test_validate_extension_success():
    """Verify validation passes for correct extensions."""
    # Should not raise any error
    validate_extension("data.csv", ".csv")
    validate_extension("report.XLSX", ".xlsx")
    validate_extension("model.joblib", [".joblib", ".pkl"])


def test_validate_extension_failure():
    """Verify ValueError is raised for mismatched extensions."""
    with pytest.raises(ValueError, match="Expected one of: .csv"):
        validate_extension("data.txt", ".csv")


def test_validate_extension_formatting():
    """Verify the utility handles extensions missing the leading dot."""
    # Should automatically prepend the dot and succeed
    validate_extension("data.parquet", "parquet")


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
