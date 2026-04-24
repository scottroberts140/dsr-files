"""JSON file handling operations."""

import dataclasses
import json
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Union

import numpy as np
import pandas as pd
from cloudpathlib import AnyPath, CloudPath
from dsr_utils.reflection import safe_call as d_safe_call

from dsr_files.enums import FileType
from dsr_files.joblib_handler import load_joblib_dataframe
from dsr_files.utils import MkDir, PathLike, _get_valid_params, get_full_path


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
    output_dir: PathLike,
    filename: str,
    indent: int | None = 2,
    encoding: str = "utf-8",
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Save a dictionary to a JSON file with safe type conversion.

    Parameters
    ----------
    data : dict[str, Any]
        The dictionary to save.
    output_dir : str | Path | CloudPath
        The destination directory.
    filename : str
        The base name of the file (extension '.json' is appended automatically).
    indent : int | None, default 2
        The indentation level for the JSON output.
    encoding : str, default "utf-8"
        The character encoding for the resulting file.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `json.dump()`.
    **kwargs : Any
        Additional keyword arguments passed directly to `json.dump()`. If `safe_call`
        is True, these are automatically filtered based on the `json.dump` signature.

    Returns
    -------
    full_path : Path, CloudPath
        The full path to the saved JSON file.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        save method. Returns an empty dictionary if `safe_call` is False.
    """
    full_path = get_full_path(
        output_dir, FileType.JSON.format_filename(filename), MkDir()
    )

    # Ensure all data is JSON-serializable
    safe_data = to_JSON_safe(data)

    with open(full_path, "w", encoding=encoding) as f:
        if safe_call:
            from json import JSONEncoder

            valid_params = _get_valid_params(FileType.JSON, "save")
            _, rejected = d_safe_call(JSONEncoder, kwargs, valid_params=valid_params)

            clean_kwargs = {k: v for k, v in kwargs.items() if k not in rejected}
            json.dump(obj=safe_data, fp=f, indent=indent, **clean_kwargs)
            return full_path, rejected
        else:
            json.dump(safe_data, f, indent=indent, **kwargs)
            return full_path, {}


def load_json(
    filepath: PathLike,
    encoding: str = "utf-8",
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Load data from a JSON file.

    Parameters
    ----------
    filepath : str | Path | CloudPath
        Path to the target JSON file.
    encoding : str, default "utf-8"
        The character encoding used to read the file.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `json.load()`.
    **kwargs : Any
        Additional keyword arguments passed directly to `json.load()`. If `safe_call`
        is True, these are automatically filtered based on the `json.load` signature.

    Returns
    -------
    data : dict[str, Any]
        The dictionary loaded from the JSON file.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        load method. Returns an empty dictionary if `safe_call` is False.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.json'.
    """
    FileType.JSON.validate_extension(filepath)
    path_obj = AnyPath(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    with open(path_obj, "r", encoding=encoding) as f:
        if safe_call:
            from json import JSONDecoder

            valid_params = _get_valid_params(FileType.JSON, "load")
            _, rejected = d_safe_call(JSONDecoder, kwargs, valid_params=valid_params)

            clean_kwargs = {k: v for k, v in kwargs.items() if k not in rejected}
            return json.load(f, **clean_kwargs), rejected
        else:
            d = json.load(f, **kwargs)
            return d, {}


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


def from_joblib(
    source_dir: PathLike,
    filename: str,
    output_dir: PathLike | None = None,
    output_filename: str | None = None,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Convert a JOBLIB DataFrame artifact to JSON records.

    Parameters are equivalent to other handler-level ``from_joblib`` helpers.
    """
    df, rejected = load_joblib_dataframe(source_dir, filename, safe_call=safe_call)
    target_dir = source_dir if output_dir is None else output_dir
    stem = Path(FileType.JOBLIB.format_filename(filename)).stem
    target_name = output_filename or stem

    output_path, save_rejected = save_json(
        df.to_dict(orient="records"),
        output_dir=target_dir,
        filename=target_name,
        safe_call=safe_call,
        **kwargs,
    )
    return output_path, {**rejected, **save_rejected}
