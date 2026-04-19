"""Tests for CSV handler."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest
from dsr_files import csv_handler


@pytest.fixture
def sample_data() -> dict[str, list[int]]:
    """
    Sample data for testing.
    """
    return {"col1": [1, 2, 3], "col2": [4, 5, 6]}


@pytest.fixture
def sample_df(sample_data: dict[str, list[int]]) -> pd.DataFrame:
    """
    Sample DataFrame for testing.
    """
    return pd.DataFrame(sample_data)


def test_create_csv_from_dict(sample_data: dict[str, list[int]]) -> None:
    """
    Verify DataFrame creation from a dictionary.
    """
    df = csv_handler.create_csv(sample_data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3


def test_create_csv_from_dataframe(sample_df: pd.DataFrame) -> None:
    """
    Verify the function returns an existing DataFrame as-is.
    """
    df = csv_handler.create_csv(sample_df)
    assert isinstance(df, pd.DataFrame)
    pd.testing.assert_frame_equal(df, sample_df)


def test_save_and_load_csv(sample_df: pd.DataFrame) -> None:
    """
    Verify round-trip saving and loading of CSV files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        csv_handler.save_csv(sample_df, str(dir_path), "test")
        full_path = dir_path / "test.csv"
        loaded_df, _ = csv_handler.load_csv(str(full_path))

        pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_save_csv_from_dict(sample_data: dict[str, list[int]]) -> None:
    """
    Verify saving a CSV directly from a dictionary.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        csv_handler.save_csv(sample_data, str(dir_path), "test")
        full_path = dir_path / "test.csv"
        loaded_df, _ = csv_handler.load_csv(str(full_path))

        assert len(loaded_df) == 3


def test_load_csv_invalid_extension() -> None:
    """
    Verify that loading a non-CSV file raises a ValueError.
    """
    with pytest.raises(ValueError):
        csv_handler.load_csv("data.pdf")


def test_load_csv_not_found() -> None:
    """
    Verify that loading a missing file raises a FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        csv_handler.load_csv("non_existent_file.csv")


def test_save_csv_returns_tuple(sample_data, tmp_path):
    """Verify the new v3.0.0 return signature for savers."""
    # Ensure path and dict are returned
    path, rejected = csv_handler.save_csv(sample_data, tmp_path, "test_file")
    assert isinstance(path, Path)
    assert isinstance(rejected, dict)
    assert path.suffix == ".csv"


def test_load_csv_with_safe_call(sample_data, tmp_path):
    """Verify reflection-based filtering and return types."""
    file_path = tmp_path / "test.csv"
    pd.DataFrame({"x": [1]}).to_csv(file_path, index=False)

    # Pass an invalid parameter to verify it is caught in 'rejected'
    df, rejected = csv_handler.load_csv(file_path, safe_call=True, fake_param="value")
    assert "fake_param" in rejected
    assert isinstance(df, pd.DataFrame)
