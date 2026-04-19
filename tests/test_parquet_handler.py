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

        parquet_handler.save_parquet(sample_df, str(dir_path), filename, engine=engine)
        full_path = dir_path / f"{filename}.parquet"
        loaded, _ = parquet_handler.load_parquet(str(full_path), engine=engine)

        # Disable strict dtype checking to account for engine-specific string handling
        pd.testing.assert_frame_equal(loaded, sample_df, check_dtype=False)


def test_save_and_load_parquet(sample_df):
    """Verify Parquet round-trip saving and loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        parquet_handler.save_parquet(sample_df, str(dir_path), "test")
        full_path = dir_path / "test.parquet"
        loaded, _ = parquet_handler.load_parquet(str(full_path))
        pd.testing.assert_frame_equal(loaded, sample_df)


def test_load_parquet_column_projection(sample_df):
    """Verify loading specific columns from a Parquet file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        parquet_handler.save_parquet(sample_df, str(dir_path), "subset")

        # Column projection is a key benefit of Parquet
        full_path = dir_path / "subset.parquet"
        loaded, _ = parquet_handler.load_parquet(str(full_path), columns=["A"])
        assert loaded.columns.tolist() == ["A"]
        assert len(loaded) == 3


def test_load_parquet_invalid_extension():
    """Verify ValueError on incorrect file extension."""
    with pytest.raises(ValueError):
        parquet_handler.load_parquet("data.pdf")


def test_save_parquet_returns_tuple(sample_df, tmp_path):
    """Verify the new v3.0.0 return signature for savers."""
    # Ensure path and dict are returned
    path, rejected = parquet_handler.save_parquet(sample_df, tmp_path, "test_file")
    assert isinstance(path, Path)
    assert isinstance(rejected, dict)
    assert path.suffix == ".parquet"


def test_load_parquet_with_safe_call(tmp_path):
    """Verify reflection-based filtering and return types."""
    file_path = tmp_path / "test.parquet"
    pd.DataFrame({"x": [1]}).to_parquet(file_path, index=False)

    # Pass an invalid parameter to verify it is caught in 'rejected'
    df, rejected = parquet_handler.load_parquet(file_path, safe_call=True, fake_param="value")
    assert "fake_param" in rejected
    assert isinstance(df, pd.DataFrame)
