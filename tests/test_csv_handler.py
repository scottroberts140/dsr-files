"""Tests for CSV handler."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
from dsr_files import csv_handler


@pytest.fixture
def sample_data() -> dict[str, list[int]]:
    """Sample data for testing."""
    return {"col1": [1, 2, 3], "col2": [4, 5, 6]}


@pytest.fixture
def sample_df(sample_data: dict[str, list[int]]) -> pd.DataFrame:
    """Sample DataFrame for testing."""
    return pd.DataFrame(sample_data)


def test_create_csv_from_dict(sample_data: dict[str, list[int]]) -> None:
    """Test creating DataFrame from dictionary."""
    df = csv_handler.create_csv(sample_data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3


def test_create_csv_from_dataframe(sample_df: pd.DataFrame) -> None:
    """Test creating DataFrame from DataFrame."""
    df = csv_handler.create_csv(sample_df)
    assert isinstance(df, pd.DataFrame)
    pd.testing.assert_frame_equal(df, sample_df)


def test_save_and_load_csv(sample_df: pd.DataFrame) -> None:
    """Test saving and loading CSV files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        csv_handler.save_csv(sample_df, filepath, "test")
        loaded_df = csv_handler.load_csv(filepath / "test.csv")

        pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_save_csv_from_dict(sample_data: dict[str, list[int]]) -> None:
    """Test saving CSV directly from dictionary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir)
        csv_handler.save_csv(sample_data, filepath, "test")
        loaded_df = csv_handler.load_csv(filepath / "test.csv")

        assert len(loaded_df) == 3
