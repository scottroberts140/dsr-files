"""Tests for JOBLIB handler."""

import pytest
from pathlib import Path
import tempfile
from dsr_files import joblib_handler


@pytest.fixture
def sample_data() -> dict[str, list[int]]:
    """Sample data for testing."""
    return {"model": [1, 2, 3, 4, 5], "metadata": {"name": "test"}}


def test_save_and_load_joblib(sample_data: dict[str, list[int]]) -> None:
    """Test saving and loading JOBLIB files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        filename = "test"

        saved_path = joblib_handler.save_joblib(sample_data, filepath, filename)
        loaded_data = joblib_handler.load_joblib(saved_path)

        assert loaded_data == sample_data


def test_save_joblib_with_compression(sample_data: dict[str, list[int]]) -> None:
    """Test saving JOBLIB with compression."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        filename = "test"

        saved_path = joblib_handler.save_joblib(sample_data, filepath, filename, compress=9)
        loaded_data = joblib_handler.load_joblib(saved_path)

        assert loaded_data == sample_data


def test_load_joblib_missing_file_raises() -> None:
    """Test loading missing JOBLIB file raises FileNotFoundError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "missing.joblib"

        with pytest.raises(FileNotFoundError):
            joblib_handler.load_joblib(filepath)
