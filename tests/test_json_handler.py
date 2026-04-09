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
        json_handler.save_json(complex_serializable_data, dir_path, "test")

        loaded = json_handler.load_json(dir_path / "test.json")
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
