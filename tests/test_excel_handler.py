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
    df, rejected = excel_handler.load_excel(
        file_path, safe_call=True, fake_param="value"
    )
    assert "fake_param" in rejected
    assert isinstance(df, pd.DataFrame)


def test_save_excel_truncates_overlong_cell_text(tmp_path):
    """Verify overlong cell text is truncated to Excel's hard character limit."""
    long_text = "x" * 40000
    df = pd.DataFrame({"payload": [long_text]})

    path, _ = excel_handler.save_excel(df, tmp_path, "long_cell", index=False)
    loaded, _ = excel_handler.load_excel(path)

    assert len(loaded.iloc[0]["payload"]) <= 32767
    assert str(loaded.iloc[0]["payload"]).endswith("... [truncated]")


def test_save_excel_truncates_overlong_object_cell_text(tmp_path):
    """Verify large object repr values are truncated before Excel write."""
    long_object = {"payload": "x" * 76000}
    df = pd.DataFrame({"payload": [long_object]})

    path, _ = excel_handler.save_excel(df, tmp_path, "long_object_cell", index=False)
    loaded, _ = excel_handler.load_excel(path)

    assert len(str(loaded.iloc[0]["payload"])) <= 32767
    assert str(loaded.iloc[0]["payload"]).endswith("... [truncated]")


def test_replace_excel_sheet_replaces_existing_sheet(tmp_path):
    """Verify replacing an existing sheet updates only that sheet's content."""
    original = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    updated = pd.DataFrame({"A": [9], "B": [8]})
    other = pd.DataFrame({"X": [10]})

    workbook_path, _ = excel_handler.save_excel(
        [
            ExcelSheetConfig(data=original, sheet_name="Sheet1"),
            ExcelSheetConfig(data=other, sheet_name="Sheet2"),
        ],
        tmp_path,
        "replace_test",
    )

    excel_handler.replace_excel_sheet(workbook_path, "Sheet1", updated)

    loaded_sheet1, _ = excel_handler.load_excel(workbook_path, sheet_name="Sheet1")
    loaded_sheet2, _ = excel_handler.load_excel(workbook_path, sheet_name="Sheet2")

    pd.testing.assert_frame_equal(loaded_sheet1, updated)
    pd.testing.assert_frame_equal(loaded_sheet2, other, check_dtype=False)


def test_replace_excel_sheet_raises_when_workbook_missing(tmp_path):
    """Verify replacing a sheet fails with a clear error when workbook is missing."""
    missing = tmp_path / "missing.xlsx"

    with pytest.raises(FileNotFoundError, match="Workbook not found"):
        excel_handler.replace_excel_sheet(
            missing,
            "Sheet1",
            pd.DataFrame({"A": [1]}),
        )
