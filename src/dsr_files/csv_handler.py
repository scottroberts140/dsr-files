"""CSV file handling operations."""

from pathlib import Path
from typing import Any, Union

import pandas as pd
from cloudpathlib import AnyPath, CloudPath
from dsr_files.enums import FileType
from dsr_files.utils import MkDir, get_full_path
from dsr_utils.reflection import safe_call as d_safe_call


def create_csv(data: dict[str, Any] | pd.DataFrame) -> pd.DataFrame:
    """
    Standardize input data into a pandas DataFrame.

    Parameters
    ----------
    data : dict[str, Any] | pd.DataFrame
        The input data, either as a dictionary of column-value pairs
        or an existing DataFrame.

    Returns
    -------
    pd.DataFrame
        The processed DataFrame.
    """
    if isinstance(data, dict):
        return pd.DataFrame(data)
    return data


def save_csv(
    data: pd.DataFrame | dict[str, Any],
    output_dir: AnyPath | str,
    filename: str,
    index: bool = False,
    encoding: str = "utf-8",
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Save a DataFrame or dictionary to a CSV file.

    Parameters
    ----------
    data : pd.DataFrame | dict[str, Any]
        The data to persist to disk.
    output_dir : AnyPath | str
        The destination directory.
    filename : str
        The base name of the file (extension '.csv' is appended automatically).
    index : bool, default False
        Whether to include the DataFrame index in the output file.
    encoding : str, default "utf-8"
        The character encoding for the resulting file.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling the underlying pandas save method.
    **kwargs : Any
        Additional keyword arguments passed to `pd.DataFrame.to_csv()`. If `safe_call`
        is True, these are automatically filtered based on the pandas method signature.

    Returns
    -------
    full_path : Path, CloudPath
        The full path to the saved CSV file.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        save method. Returns an empty dictionary if `safe_call` is False.
    """
    full_path = get_full_path(output_dir, FileType.CSV.format_filename(filename), MkDir())
    df = create_csv(data)

    if safe_call:
        _, rejected = d_safe_call(
            df.to_csv, kwargs, path_or_buf=full_path, index=index, encoding=encoding
        )
        return full_path, rejected
    else:
        df.to_csv(full_path, index=index, encoding=encoding, **kwargs)
        return full_path, {}


def load_csv(
    filepath: str | AnyPath,
    encoding: str = "utf-8",
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Load data from a CSV file into a DataFrame.

    Parameters
    ----------
    filepath : str | AnyPath
        Path to the target CSV file.
    encoding : str, default "utf-8"
        The character encoding used to read the file.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling the underlying pandas read method.
    **kwargs : Any
        Additional keyword arguments passed to `pd.read_csv()`. If `safe_call`
        is True, these are automatically filtered based on the pandas method signature.

    Returns
    -------
    data : pd.DataFrame
        The loaded pandas DataFrame.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        read method. Returns an empty dictionary if `safe_call` is False.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.csv'.
    """
    FileType.CSV.validate_extension(filepath)

    path_obj = AnyPath(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    if safe_call:
        df, rejected = d_safe_call(
            pd.read_csv, kwargs, filepath_or_buffer=path_obj, encoding=encoding
        )
        return df, rejected
    else:
        df = pd.read_csv(path_obj, encoding=encoding, **kwargs)
        return df, {}
