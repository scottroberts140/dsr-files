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
        csv_handler.save_csv(sample_df, dir_path, "test")
        loaded_df = csv_handler.load_csv(dir_path / "test.csv")

        pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_save_csv_from_dict(sample_data: dict[str, list[int]]) -> None:
    """
    Verify saving a CSV directly from a dictionary.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        csv_handler.save_csv(sample_data, dir_path, "test")
        loaded_df = csv_handler.load_csv(dir_path / "test.csv")

        assert len(loaded_df) == 3


def test_load_csv_invalid_extension() -> None:
    """
    Verify that loading a non-CSV file raises a ValueError.
    """
    with pytest.raises(ValueError):
        csv_handler.load_csv("data.txt")


def test_load_csv_not_found() -> None:
    """
    Verify that loading a missing file raises a FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        csv_handler.load_csv("non_existent_file.csv")
