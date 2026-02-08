"""JSON file handling operations."""

from pathlib import Path
from typing import Any, Optional
import json


def create_json(data: dict[str, Any]) -> dict[str, Any]:
    """
    Create or validate JSON-compatible dictionary.

    Args:
        data: Dictionary to prepare as JSON

    Returns:
        Dictionary suitable for JSON serialization
    """
    return data


def save_json(
    data: dict[str, Any],
    filepath: Path,
    filename: str,
    indent: Optional[int] = 2,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> Path:
    """
    Save data to JSON file.

    Args:
        data: Dictionary to save
        filepath: Path to save the file
        filename: Name of the file (without the extension)
        indent: JSON indentation level
        encoding: File encoding (default: utf-8)
        **kwargs: Additional arguments passed to json.dump()

    Returns:
        Path to the saved JSON file
    """
    filepath.mkdir(parents=True, exist_ok=True)
    safe_data = to_JSON_safe(data)
    full_path = Path(filepath) / f"{filename}.json"
    with open(full_path, "w", encoding=encoding) as f:
        json.dump(safe_data, f, indent=indent, **kwargs)
    return full_path


def load_json(
    filepath: str | Path,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Load data from JSON file.

    Args:
        filepath: Path to JSON file
        encoding: File encoding (default: utf-8)
        **kwargs: Additional arguments passed to json.load()

    Returns:
        Dictionary loaded from JSON file
    """
    with open(filepath, "r", encoding=encoding) as f:
        return json.load(f, **kwargs)


def to_JSON_safe(o: Any) -> Any:
    """
    Recursively convert Python objects to JSON-serializable values.

    Safely handles complex nested structures including dictionaries, lists, tuples,
    sets, NumPy types, Enums, dataclasses, Paths, and datetime objects.

    Args:
        o: Python object to convert (can be nested)

    Returns:
        JSON-serializable value. Containers are recursively converted.
        Unserializable objects are converted to strings as fallback.
    """
    import numpy as np
    from enum import Enum
    from pathlib import Path
    from datetime import datetime, date
    import dataclasses
    import pandas as pd

    # 1. Handle Recursion for Containers
    if isinstance(o, dict):
        return {str(k): to_JSON_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [to_JSON_safe(i) for i in o]

    # 2. Handle NumPy/Python Booleans
    if isinstance(o, (np.bool_, bool)):
        return bool(o)

    # 3. Handle NumPy Numbers
    if isinstance(o, (np.integer, np.floating)):
        return o.item()

    # 4. Handle Enums
    if isinstance(o, Enum):
        return o.name  # or o.value

    # 5. Handle Paths and Dates
    if isinstance(o, (Path, datetime, date)):
        return str(o)

    # 6. Handle Dataclasses
    # Use the official check for dataclasses
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        # We use asdict, but we call to_JSON_safe on the result
        # to catch any non-serializable values nested inside the dataclass
        return to_JSON_safe(dataclasses.asdict(o))  # type: ignore

    # 7. Handle DataFrame
    if isinstance(o, pd.DataFrame):
        return o.to_dict(orient="records")  # Converts to list of dicts

    # 8. Handle Series
    if isinstance(o, pd.Series):
        return o.tolist()

    return o
