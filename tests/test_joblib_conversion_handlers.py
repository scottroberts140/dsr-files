"""Tests for handler-level from_joblib conversions."""

import pandas as pd
import pytest
from dsr_files.csv_handler import from_joblib as csv_from_joblib
from dsr_files.excel_handler import from_joblib as excel_from_joblib
from dsr_files.joblib_handler import save_joblib
from dsr_files.json_handler import from_joblib as json_from_joblib
from dsr_files.json_handler import load_json
from dsr_files.parquet_handler import from_joblib as parquet_from_joblib
from dsr_files.parquet_handler import load_parquet
from dsr_files.yaml_handler import from_joblib as yaml_from_joblib
from dsr_files.yaml_handler import load_yaml


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Simple DataFrame used for conversion tests."""
    return pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})


def test_from_joblib_defaults_output_dir_to_source_dir(sample_df, tmp_path):
    """Verify CSV conversion writes beside the source joblib by default."""
    save_joblib(sample_df, tmp_path, "data")

    output_path, rejected = csv_from_joblib(tmp_path, "data")

    assert output_path == tmp_path / "data.csv"
    assert isinstance(rejected, dict)
    assert output_path.exists()


def test_from_joblib_uses_explicit_output_dir_and_filename(sample_df, tmp_path):
    """Verify output_dir and output_filename override defaults."""
    save_joblib(sample_df, tmp_path, "clean_data")
    output_dir = tmp_path / "exports"

    output_path, _ = parquet_from_joblib(
        source_dir=tmp_path,
        filename="clean_data.joblib",
        output_dir=output_dir,
        output_filename="clean_snapshot",
    )

    assert output_path == output_dir / "clean_snapshot.parquet"
    loaded_df, _ = load_parquet(output_path)
    pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_from_joblib_json_and_yaml_produce_records(sample_df, tmp_path):
    """Verify JSON and YAML conversion persist list-of-record structures."""
    save_joblib(sample_df, tmp_path, "data")

    json_path, _ = json_from_joblib(tmp_path, "data")
    yaml_path, _ = yaml_from_joblib(tmp_path, "data")

    json_data, _ = load_json(json_path)
    yaml_data, _ = load_yaml(yaml_path)

    assert isinstance(json_data, list)
    assert isinstance(yaml_data, list)
    assert json_data[0]["a"] == 1
    assert yaml_data[0]["b"] == "x"


def test_from_joblib_excel_writes_workbook(sample_df, tmp_path):
    """Verify Excel conversion writes an .xlsx artifact."""
    save_joblib(sample_df, tmp_path, "data")

    output_path, _ = excel_from_joblib(tmp_path, "data")

    assert output_path == tmp_path / "data.xlsx"
    assert output_path.exists()


def test_from_joblib_raises_when_joblib_content_is_not_dataframe(tmp_path):
    """Verify type safety check rejects non-DataFrame joblib objects."""
    save_joblib({"foo": 1}, tmp_path, "not_a_df")

    with pytest.raises(TypeError, match="Expected a pandas DataFrame"):
        csv_from_joblib(tmp_path, "not_a_df")
