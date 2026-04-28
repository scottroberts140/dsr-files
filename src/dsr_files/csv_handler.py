"""CSV file handling operations."""

from pathlib import Path
from typing import Any, Union

import pandas as pd
from cloudpathlib import AnyPath, CloudPath
from dsr_utils.reflection import safe_call as d_safe_call

from dsr_files.enums import FileType
from dsr_files.joblib_handler import load_joblib_dataframe
from dsr_files.utils import MkDir, PathLike, _get_valid_params, get_full_path


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
    output_dir: PathLike,
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
    output_dir : str | Path | CloudPath
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
    full_path = get_full_path(
        output_dir,
        FileType.CSV.format_filename(filename),
        MkDir(),
        replace_existing=True,
    )
    df = create_csv(data)

    if safe_call:
        valid_params = _get_valid_params(FileType.CSV, "save")
        _, rejected = d_safe_call(
            df.to_csv,
            kwargs,
            path_or_buf=full_path,
            index=index,
            encoding=encoding,
            valid_params=valid_params,
        )
        return full_path, rejected
    else:
        df.to_csv(full_path, index=index, encoding=encoding, **kwargs)
        return full_path, {}


def load_csv(
    filepath: PathLike,
    encoding: str = "utf-8",
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Load data from a CSV file into a DataFrame.

    Parameters
    ----------
    filepath : str | Path | CloudPath
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
        valid_params = _get_valid_params(FileType.CSV, "load")
        df, rejected = d_safe_call(
            pd.read_csv,
            kwargs,
            filepath_or_buffer=path_obj,
            encoding=encoding,
            valid_params=valid_params,
        )
        return df, rejected
    else:
        df = pd.read_csv(path_obj, encoding=encoding, **kwargs)
        return df, {}


def from_joblib(
    source_dir: PathLike,
    filename: str,
    output_dir: PathLike | None = None,
    output_filename: str | None = None,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Convert a JOBLIB DataFrame artifact to CSV.

    Parameters
    ----------
    source_dir : str | Path | CloudPath
        Directory containing the source JOBLIB artifact.
    filename : str
        JOBLIB filename with or without ``.joblib`` extension.
    output_dir : str | Path | CloudPath | None, default None
        Destination directory for CSV output. Defaults to ``source_dir``.
    output_filename : str | None, default None
        Output filename stem. Defaults to the JOBLIB stem.
    safe_call : bool, default False
        Whether to filter unsupported kwargs for load/save calls.
    **kwargs : Any
        Additional kwargs forwarded to :func:`save_csv`.
    """
    df, rejected = load_joblib_dataframe(source_dir, filename, safe_call=safe_call)
    target_dir = source_dir if output_dir is None else output_dir
    stem = Path(FileType.JOBLIB.format_filename(filename)).stem
    target_name = output_filename or stem

    output_path, save_rejected = save_csv(
        df,
        output_dir=target_dir,
        filename=target_name,
        safe_call=safe_call,
        **kwargs,
    )
    return output_path, {**rejected, **save_rejected}
