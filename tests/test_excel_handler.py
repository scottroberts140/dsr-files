"""Tests for Excel handler."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
from dsr_files import excel_handler


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for testing."""
    return pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})


def test_create_excel_from_dict() -> None:
    """Test creating DataFrame from dictionary."""
    data = {"col1": [1, 2], "col2": ["a", "b"]}
    df = excel_handler.create_excel(data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


def test_save_and_load_excel_single_sheet(sample_df: pd.DataFrame) -> None:
    """Test saving and loading single sheet Excel file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        # Note: Depending on installed libraries, engine might need to be specified or auto
        # We use 'openpyxl' or 'xlsxwriter' if available, otherwise let pandas decide
        excel_handler.save_excel(
            sample_df, output_dir, "test_single", index=False, engine="openpyxl"
        )

        filepath = output_dir / "test_single.xlsx"
        assert filepath.exists()

        loaded_df = excel_handler.load_excel(filepath)
        pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_save_excel_multi_sheet(sample_df: pd.DataFrame) -> None:
    """Test saving multiple sheets to one Excel file."""
    sheet1 = excel_handler.ExcelSheetConfig(data=sample_df, sheet_name="Sheet1")
    sheet2 = excel_handler.ExcelSheetConfig(data={"A": [10, 20]}, sheet_name="Sheet2")

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        excel_handler.save_excel([sheet1, sheet2], output_dir, "test_multi", engine="openpyxl")

        filepath = output_dir / "test_multi.xlsx"
        assert filepath.exists()

        # Load specific sheets to verify
        df1 = excel_handler.load_excel(filepath, sheet_name="Sheet1")
        df2 = excel_handler.load_excel(filepath, sheet_name="Sheet2")

        pd.testing.assert_frame_equal(df1, sample_df, check_dtype=False)
        assert len(df2) == 2
        assert "A" in df2.columns
