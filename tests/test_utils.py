import pytest
from pathlib import Path
from dsr_files import validate_extension


def test_validate_extension_valid_single():
    """Test validation with a single string extension."""
    validate_extension("test.csv", ".csv")
    # Test without leading dot in expected extension
    validate_extension("test.csv", "csv")


def test_validate_extension_valid_list():
    """Test validation with a list of allowed extensions."""
    validate_extension("test.json", [".csv", ".json"])
    validate_extension("test.xlsx", ["xls", "xlsx"])


def test_validate_extension_case_insensitive():
    """Test that validation is case-insensitive."""
    validate_extension("test.CSV", ".csv")
    validate_extension("test.csv", ".CSV")


def test_validate_extension_path_object():
    """Test validation when input is a Path object."""
    validate_extension(Path("test.joblib"), ".joblib")


def test_validate_extension_invalid():
    """Test that ValueError is raised for invalid extensions."""
    with pytest.raises(ValueError, match="Invalid file extension"):
        validate_extension("test.txt", ".csv")

    with pytest.raises(ValueError, match="Expected one of"):
        validate_extension("test.pdf", [".csv", ".json"])
