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

        saved_path, _ = joblib_handler.save_joblib(complex_data, str(dir_path), filename)
        assert saved_path.exists()
        assert saved_path.suffix == ".joblib"

        loaded_data, _ = joblib_handler.load_joblib(str(saved_path))
        assert loaded_data == complex_data


def test_load_joblib_invalid_extension():
    """Verify ValueError on incorrect file extension."""
    with pytest.raises(ValueError):
        joblib_handler.load_joblib("model.pkl")


def test_load_joblib_not_found():
    """Verify FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        joblib_handler.load_joblib("missing_model.joblib")


def test_save_joblib_returns_tuple(complex_data, tmp_path):
    """Verify the new v3.0.0 return signature for savers."""
    # Ensure path and dict are returned
    path, rejected = joblib_handler.save_joblib(complex_data, tmp_path, "test_file")
    assert isinstance(path, Path)
    assert isinstance(rejected, dict)
    assert path.suffix == ".joblib"


def test_load_joblib_with_safe_call(complex_data, tmp_path):
    """Verify reflection-based filtering and return types."""
    file_name = "test.joblib"
    file_path, _ = joblib_handler.save_joblib(complex_data, tmp_path, file_name)

    # Pass an invalid parameter to verify it is caught in 'rejected'
    loaded_data, rejected = joblib_handler.load_joblib(
        str(file_path), safe_call=True, fake_param="value"
    )
    assert "fake_param" in rejected
    assert loaded_data == complex_data
