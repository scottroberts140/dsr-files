# dsr_files/yaml_handler.py
from pathlib import Path
from typing import Any

import yaml
from dsr_files.json_handler import to_JSON_safe


def save_yaml(data: Any, filepath: Path) -> None:
    """
    Saves data to a YAML file with standardized formatting and type safety.

    This function utilizes `to_JSON_safe` to recursively convert complex Python
    objects (such as Enums, Paths, and NumPy types) into YAML-serializable primitives
    before writing to disk.

    Parameters
    ----------
    data : Any
        The Python object, list, or dictionary to be serialized.
    filepath : Path
        The destination filesystem path for the YAML file.

    Notes
    -----
    - Uses `yaml.safe_dump` to prevent arbitrary code execution.
    - Sets `default_flow_style=False` for human-readable block formatting.
    - Sets `sort_keys=False` to preserve the original order of recommendations.
    """
    serializable_data = to_JSON_safe(data)

    with open(filepath, "w", encoding="utf-8") as f:
        yaml.safe_dump(serializable_data, f, default_flow_style=False, sort_keys=False)


def load_yaml(filepath: Path) -> Any:
    """
    Loads data from a YAML file into Python objects safely.

    Parameters
    ----------
    filepath : Path
        The path to the YAML file to be loaded.

    Returns
    -------
    Any
        The parsed content of the YAML file (typically a dict or list).

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist.
    yaml.YAMLError
        If the file contains invalid YAML syntax.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
