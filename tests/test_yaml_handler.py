from pathlib import Path

import pytest
from dsr_files.yaml_handler import load_yaml, save_yaml


def test_yaml_round_trip(tmp_path):
    """Verify that saving and loading a dictionary preserves content and types."""
    test_data = {
        "dataset_id": "adult_income",
        "params": {"generate_recs": True, "max_bins": 1000},
        "columns": ["age", "workclass", "education"],
    }
    file_name = "test_config.yaml"

    # 1. Save
    file_path, _ = save_yaml(test_data, tmp_path, file_name)
    assert file_path.exists()

    # 2. Load
    loaded_data, _ = load_yaml(str(file_path))

    # 3. Assertions
    assert loaded_data == test_data
    assert isinstance(loaded_data["params"]["generate_recs"], bool)
    assert isinstance(loaded_data["params"]["max_bins"], int)


def test_yaml_save_list_of_dicts(tmp_path):
    """Verify serialization of recommendation-style data structures."""
    recs = [
        {"column": "age", "strategy": "IQR", "active": True},
        {"column": "occupation", "strategy": "IMPUTE_MODE", "active": True},
    ]
    file_name = "recs.yaml"

    file_path, _ = save_yaml(recs, tmp_path, file_name)
    loaded_recs, _ = load_yaml(str(file_path))

    assert len(loaded_recs) == 2
    assert loaded_recs[0]["column"] == "age"


def test_yaml_load_file_not_found():
    """Verify standard FileNotFoundError is raised for missing files."""
    with pytest.raises(FileNotFoundError):
        load_yaml("non_existent_file.yaml")


def test_save_yaml_returns_tuple(tmp_path):
    """Verify the new v3.0.0 return signature for savers."""
    # Ensure path and dict are returned
    recs = [
        {"column": "age", "strategy": "IQR", "active": True},
        {"column": "occupation", "strategy": "IMPUTE_MODE", "active": True},
    ]
    file_path, rejected = save_yaml(recs, tmp_path, "test_file")
    assert isinstance(file_path, Path)
    assert isinstance(rejected, dict)
    assert file_path.suffix == ".yaml"


def test_load_yaml_with_safe_call(tmp_path):
    """Verify reflection-based filtering and return types."""
    file_name = "test"
    recs = [
        {"column": "age", "strategy": "IQR", "active": True},
        {"column": "occupation", "strategy": "IMPUTE_MODE", "active": True},
    ]
    file_path, rejected = save_yaml(recs, tmp_path, file_name)

    # Pass an invalid parameter to verify it is caught in 'rejected'
    retval, rejected = load_yaml(str(file_path), safe_call=True, fake_param="value")
    assert "fake_param" in rejected
    assert isinstance(retval, list)
