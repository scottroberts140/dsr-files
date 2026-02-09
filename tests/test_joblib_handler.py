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
        joblib_handler.save_joblib(sample_data, filepath, "test")
        loaded_data = joblib_handler.load_joblib(filepath / "test.joblib")

        assert loaded_data == sample_data


def test_save_joblib_with_compression(sample_data: dict[str, list[int]]) -> None:
    """Test saving JOBLIB with compression."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        joblib_handler.save_joblib(sample_data, filepath, "test", compress=9)
        loaded_data = joblib_handler.load_joblib(filepath / "test.joblib")

        assert loaded_data == sample_data
