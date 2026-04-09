"""JSON file handling operations."""

import dataclasses
import json
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from dsr_files.utils import validate_extension


def create_json(data: dict[str, Any]) -> dict[str, Any]:
    """
    Standardize or validate a JSON-compatible dictionary.

    Parameters
    ----------
    data : dict[str, Any]
        The dictionary to prepare for serialization.

    Returns
    -------
    dict[str, Any]
        The validated dictionary.
    """
    return data


def save_json(
    data: dict[str, Any],
    output_dir: Path,
    filename: str,
    indent: int | None = 2,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> Path:
    """
    Save a dictionary to a JSON file with safe type conversion.

    Parameters
    ----------
    data : dict[str, Any]
        The dictionary to save.
    output_dir : Path
        The destination directory.
    filename : str
        The base name of the file (extension '.json' is appended automatically).
    indent : int | None, default 2
        The indentation level for the JSON output.
    encoding : str, default "utf-8"
        The character encoding for the resulting file.
    **kwargs : Any
        Additional keyword arguments passed directly to `json.dump()`.

    Returns
    -------
    Path
        The full path to the saved JSON file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    full_path = output_dir / f"{filename}.json"

    # Ensure all data is JSON-serializable
    safe_data = to_JSON_safe(data)

    with open(full_path, "w", encoding=encoding) as f:
        json.dump(safe_data, f, indent=indent, **kwargs)

    return full_path


def load_json(
    filepath: str | Path,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Load data from a JSON file.

    Parameters
    ----------
    filepath : str | Path
        Path to the target JSON file.
    encoding : str, default "utf-8"
        The character encoding used to read the file.
    **kwargs : Any
        Additional keyword arguments passed directly to `json.load()`.

    Returns
    -------
    dict[str, Any]
        The dictionary loaded from the JSON file.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.json'.
    """
    validate_extension(filepath, ".json")
    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(path_obj, "r", encoding=encoding) as f:
        return json.load(f, **kwargs)


def to_JSON_safe(o: Any) -> Any:
    """
    Recursively convert Python objects to JSON-serializable values.

    Safely handles complex nested structures including dictionaries, lists,
    tuples, sets, NumPy types, Enums, dataclasses, Paths, and datetime
    objects.

    Parameters
    ----------
    o : Any
        The Python object to convert.

    Returns
    -------
    Any
        A JSON-serializable value.
    """
    # 1. Handle Recursion for Containers
    if isinstance(o, dict):
        return {str(k): to_JSON_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [to_JSON_safe(i) for i in o]

    # 2. Handle NumPy Arrays (The Fix)
    if isinstance(o, np.ndarray):
        return [to_JSON_safe(i) for i in o.tolist()]

    # 3. Handle NumPy/Python Booleans
    if isinstance(o, (np.bool_, bool)):
        return bool(o)

    # 4. Handle NumPy Numbers
    if isinstance(o, (np.integer, np.floating)):
        return o.item()

    # 5. Handle Enums
    if isinstance(o, Enum):
        return o.name

    # 6. Handle Paths and Dates
    if isinstance(o, (Path, datetime, date)):
        return str(o)

    # 7. Handle Dataclasses
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        return to_JSON_safe(dataclasses.asdict(o))  # type: ignore

    # 8. Handle DataFrame
    if isinstance(o, pd.DataFrame):
        return o.to_dict(orient="records")

    # 9. Handle Series
    if isinstance(o, pd.Series):
        return [to_JSON_safe(i) for i in o.tolist()]

    return o
