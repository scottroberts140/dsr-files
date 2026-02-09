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
