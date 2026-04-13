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
    file_path = tmp_path / "test_config.yaml"

    # 1. Save
    save_yaml(test_data, file_path)
    assert file_path.exists()

    # 2. Load
    loaded_data = load_yaml(file_path)

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
    file_path = tmp_path / "recs.yaml"

    save_yaml(recs, file_path)
    loaded_recs = load_yaml(file_path)

    assert len(loaded_recs) == 2
    assert loaded_recs[0]["column"] == "age"


def test_yaml_load_file_not_found():
    """Verify standard FileNotFoundError is raised for missing files."""
    with pytest.raises(FileNotFoundError):
        load_yaml(Path("non_existent_file.yaml"))
