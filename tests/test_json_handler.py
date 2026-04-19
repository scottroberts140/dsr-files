"""Tests for JSON handler."""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from dsr_files import json_handler


@pytest.fixture
def complex_serializable_data():
    """Data containing types that usually break standard json.dump."""
    return {
        "path": Path("/tmp/test"),
        "timestamp": pd.Timestamp("2026-01-01"),
        "array": np.array([1, 2, 3], dtype=np.int64),
        "nested": {"bool": np.bool_(True)},
    }


def test_save_and_load_json(complex_serializable_data):
    """Verify that complex types are handled safely during round-trip."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        json_handler.save_json(complex_serializable_data, str(dir_path), "test")
        full_path = dir_path / "test.json"
        loaded, _ = json_handler.load_json(str(full_path))
        assert loaded["path"] == "/tmp/test"
        assert loaded["array"] == [1, 2, 3]
        assert loaded["nested"]["bool"] is True


def test_load_json_invalid_extension():
    """Verify ValueError on incorrect file extension."""
    with pytest.raises(ValueError):
        json_handler.load_json("data.yaml")


def test_to_json_safe_dataframe():
    """Verify DataFrame conversion to records."""
    df = pd.DataFrame({"a": [1], "b": [2]})
    safe = json_handler.to_JSON_safe(df)
    assert safe == [{"a": 1, "b": 2}]


def test_save_json_returns_tuple(complex_serializable_data, tmp_path):
    """Verify the new v3.0.0 return signature for savers."""
    # Ensure path and dict are returned
    path, rejected = json_handler.save_json(complex_serializable_data, tmp_path, "test_file")
    assert isinstance(path, Path)
    assert isinstance(rejected, dict)
    assert path.suffix == ".json"


def test_load_json_with_safe_call(complex_serializable_data, tmp_path):
    """Verify reflection-based filtering and return types."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_handler.save_json(complex_serializable_data, tmp_path, "test")

        # Pass an invalid parameter to verify it is caught in 'rejected'
        loaded, rejected = json_handler.load_json(
            tmp_path / "test.json", safe_call=True, fake_param="value"
        )
        assert "fake_param" in rejected
        assert loaded["path"] == "/tmp/test"
        assert loaded["array"] == [1, 2, 3]
        assert loaded["nested"]["bool"] is True
