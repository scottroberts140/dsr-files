"""Tests for Parquet handler."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest
from dsr_files import parquet_handler


@pytest.fixture
def sample_df():
    """Simple DataFrame for testing."""
    return pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})


@pytest.mark.parametrize("engine", ["pyarrow", "fastparquet"])
def test_save_and_load_parquet_engines(sample_df, engine):
    """
    Verify Parquet round-trip using specific engines.
    """
    # Skip if the specific engine is not installed
    pytest.importorskip(engine)

    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        filename = f"test_{engine}"

        parquet_handler.save_parquet(sample_df, dir_path, filename, engine=engine)
        loaded = parquet_handler.load_parquet(dir_path / f"{filename}.parquet", engine=engine)

        # Disable strict dtype checking to account for engine-specific string handling
        pd.testing.assert_frame_equal(loaded, sample_df, check_dtype=False)


def test_save_and_load_parquet(sample_df):
    """Verify Parquet round-trip saving and loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        parquet_handler.save_parquet(sample_df, dir_path, "test")

        loaded = parquet_handler.load_parquet(dir_path / "test.parquet")
        pd.testing.assert_frame_equal(loaded, sample_df)


def test_load_parquet_column_projection(sample_df):
    """Verify loading specific columns from a Parquet file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        parquet_handler.save_parquet(sample_df, dir_path, "subset")

        # Column projection is a key benefit of Parquet
        loaded = parquet_handler.load_parquet(dir_path / "subset.parquet", columns=["A"])
        assert loaded.columns.tolist() == ["A"]
        assert len(loaded) == 3


def test_load_parquet_invalid_extension():
    """Verify ValueError on incorrect file extension."""
    with pytest.raises(ValueError):
        parquet_handler.load_parquet("data.csv")
