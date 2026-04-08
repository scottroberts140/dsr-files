"""Tests for JSON handler."""

import pytest
from pathlib import Path
from datetime import datetime, date
import numpy as np
import tempfile
from dsr_files import json_handler


@pytest.fixture
def sample_data() -> dict[str, int | str]:
    """Sample data for testing."""
    return {"key1": "value1", "key2": 42}


def test_create_json(sample_data: dict[str, int | str]) -> None:
    """Test creating JSON-compatible dictionary."""
    result = json_handler.create_json(sample_data)
    assert result == sample_data


def test_save_and_load_json(sample_data: dict[str, int | str]) -> None:
    """Test saving and loading JSON files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        json_handler.save_json(sample_data, filepath, "test")
        loaded_data = json_handler.load_json(filepath / "test.json")

        assert loaded_data == sample_data


def test_save_json_with_indent(sample_data: dict[str, int | str]) -> None:
    """Test saving JSON with custom indentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        json_handler.save_json(sample_data, filepath, "test", indent=4)

        with open(filepath / "test.json", "r") as f:
            content = f.read()

        assert "    " in content  # Check for 4-space indent


def test_to_json_safe_complex_types() -> None:
    """Test serialization of complex types (Path, datetime, numpy)."""
    complex_data = {
        "path": Path("/tmp/test"),
        "date": date(2023, 1, 1),
        "datetime": datetime(2023, 1, 1, 12, 0, 0),
        "numpy_int": np.int64(42),
        "numpy_float": np.float64(3.14),
        "numpy_bool": np.bool_(True),
    }

    safe_data = json_handler.to_JSON_safe(complex_data)

    assert isinstance(safe_data["path"], str)
    assert isinstance(safe_data["date"], str)
    assert isinstance(safe_data["numpy_int"], int)
    assert isinstance(safe_data["numpy_float"], float)
    assert safe_data["numpy_bool"] is True
