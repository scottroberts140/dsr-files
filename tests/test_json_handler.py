"""Tests for JSON handler."""

import pytest
from pathlib import Path
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
        filename = "test"

        saved_path = json_handler.save_json(sample_data, filepath, filename)
        loaded_data = json_handler.load_json(saved_path)

        assert loaded_data == sample_data


def test_save_json_with_indent(sample_data: dict[str, int | str]) -> None:
    """Test saving JSON with custom indentation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        filename = "test"

        saved_path = json_handler.save_json(sample_data, filepath, filename, indent=4)

        with open(saved_path, "r") as f:
            content = f.read()

        assert "    " in content  # Check for 4-space indent


def test_to_json_safe_handles_complex_types() -> None:
    """Test that to_JSON_safe converts common non-JSON types."""
    import numpy as np
    from dataclasses import dataclass
    from datetime import date

    @dataclass
    class Sample:
        name: str
        count: int

    payload = {
        "flag": np.bool_(True),
        "count": np.int64(7),
        "ratio": np.float64(3.5),
        "day": date(2023, 1, 1),
        "data": Sample(name="test", count=2),
    }

    safe = json_handler.to_JSON_safe(payload)

    assert safe["flag"] is True
    assert safe["count"] == 7
    assert safe["ratio"] == 3.5
    assert safe["day"] == "2023-01-01"
    assert safe["data"] == {"name": "test", "count": 2}
