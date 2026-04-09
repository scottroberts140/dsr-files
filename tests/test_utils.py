"""Tests for utility functions."""

import pytest
from dsr_files.utils import validate_extension


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
