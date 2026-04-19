"""Tests for Excel handler."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest
from dsr_files import excel_handler
from dsr_files.excel_handler import ExcelSheetConfig


@pytest.fixture
def sample_df():
    """Simple DataFrame for testing."""
    return pd.DataFrame({"A": [1, 2], "B": [3, 4]})


def test_save_and_load_excel_single(sample_df):
    """Verify single-sheet Excel round-trip without index."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        # Explicitly disable index to prevent the extra column on load
        excel_handler.save_excel(sample_df, str(dir_path), "test", index=False)
        full_path = dir_path / "test.xlsx"
        loaded, _ = excel_handler.load_excel(str(full_path))
        pd.testing.assert_frame_equal(loaded, sample_df)


def test_save_and_load_excel_multi(sample_df):
    """Verify multi-sheet Excel creation using ExcelSheetConfig."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        configs = [
            # index=False is the default in ExcelSheetConfig
            ExcelSheetConfig(data=sample_df, sheet_name="Sheet1"),
            ExcelSheetConfig(data={"C": [5]}, sheet_name="Sheet2"),
        ]

        excel_handler.save_excel(configs, str(dir_path), "multi")

        # Verify both sheets exist
        full_path = dir_path / "multi.xlsx"
        str_full_path = str(full_path)
        s1, _ = excel_handler.load_excel(str_full_path, sheet_name="Sheet1")
        s2, _ = excel_handler.load_excel(str_full_path, sheet_name="Sheet2")

        # We use check_dtype=False because Excel may cast ints to floats depending on the engine
        pd.testing.assert_frame_equal(s1, sample_df, check_dtype=False)
        assert s2.iloc[0]["C"] == 5


def test_load_excel_invalid_extension():
    """Verify ValueError on incorrect file extension."""
    with pytest.raises(ValueError):
        excel_handler.load_excel("data.csv")


def test_save_excel_returns_tuple(sample_df, tmp_path):
    """Verify the new v3.0.0 return signature for savers."""
    # Ensure path and dict are returned
    path, rejected = excel_handler.save_excel(sample_df, tmp_path, "test_file")
    assert isinstance(path, Path)
    assert isinstance(rejected, dict)
    assert path.suffix == ".xlsx"


def test_load_excel_with_safe_call(sample_df, tmp_path):
    """Verify reflection-based filtering and return types."""
    file_path = tmp_path / "test.xlsx"
    pd.DataFrame({"x": [1]}).to_excel(file_path, index=False)

    # Pass an invalid parameter to verify it is caught in 'rejected'
    df, rejected = excel_handler.load_excel(file_path, safe_call=True, fake_param="value")
    assert "fake_param" in rejected
    assert isinstance(df, pd.DataFrame)
