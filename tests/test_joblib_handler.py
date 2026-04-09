"""Tests for JOBLIB handler."""

import tempfile
from pathlib import Path

import pytest
from dsr_files import joblib_handler


@pytest.fixture
def complex_data():
    """Sample complex Python object for serialization testing."""
    return [{"id": 1, "metadata": [1.1, 2.2]}, {"id": 2, "metadata": {"status": "active"}}]


def test_save_and_load_joblib(complex_data):
    """Verify round-trip saving and loading of Python objects."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        filename = "test_model"

        saved_path = joblib_handler.save_joblib(complex_data, dir_path, filename)
        assert saved_path.exists()
        assert saved_path.suffix == ".joblib"

        loaded_data = joblib_handler.load_joblib(saved_path)
        assert loaded_data == complex_data


def test_load_joblib_invalid_extension():
    """Verify ValueError on incorrect file extension."""
    with pytest.raises(ValueError):
        joblib_handler.load_joblib("model.pkl")


def test_load_joblib_not_found():
    """Verify FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        joblib_handler.load_joblib("missing_model.joblib")
