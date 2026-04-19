"""Parquet file handling operations."""

from pathlib import Path
from typing import Any, Literal, Union, cast

import pandas as pd
from cloudpathlib import AnyPath, CloudPath
from dsr_files.enums import FileType
from dsr_files.utils import MkDir, _get_valid_params, get_full_path

# Define supported engines for Parquet operations
ParquetEngine = Literal["pyarrow", "fastparquet", "auto"]


def save_parquet(
    data: pd.DataFrame,
    output_dir: AnyPath | str,
    filename: str,
    engine: ParquetEngine = "auto",
    compression: str | None = "snappy",
    index: bool | None = None,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Save a DataFrame to a Parquet file.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame to persist to disk.
    output_dir : AnyPath | str
        The destination directory.
    filename : str
        The base name of the file (extension '.parquet' is added).
    engine : ParquetEngine, default "auto"
        Parquet library to use (pyarrow or fastparquet).
    compression : str | None, default "snappy"
        Name of the compression to use.
    index : bool | None, default None
        Whether to include the DataFrame index.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `pd.DataFrame.to_parquet()`.
    **kwargs : Any
        Additional arguments passed to the engine. Supports 'storage_options'
        for remote filesystems (e.g., S3, GCS) via fsspec.

    Returns
    -------
    full_path : Path, CloudPath
        The full path to the saved Parquet file.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        save method. Returns an empty dictionary if `safe_call` is False.
    """
    # Standard path construction
    full_path = get_full_path(output_dir, FileType.PARQUET.format_filename(filename), MkDir())

    # Fastparquet fix: Convert Arrow-backed strings to object dtype
    if engine == "fastparquet":
        data = data.copy()
        for col in data.select_dtypes(include=["string", "object"]).columns:
            data[col] = data[col].astype(object)

    if safe_call:
        # Define known valid parameters for pd.DataFrame.to_parquet
        # This prevents an invalid parameter from reaching the engine
        # The parquet internal functions have a **kwargs parameter that causes any
        # parameter to be passed when using dsr_utils.safe_call
        _valid_params = _get_valid_params(FileType.PARQUET, "save")
        valid_params = set(_valid_params) if _valid_params else {}

        accepted = {k: v for k, v in kwargs.items() if k in valid_params}
        rejected = {k: v for k, v in kwargs.items() if k not in valid_params}

        data.to_parquet(
            path=full_path,
            engine=cast(Any, engine),
            compression=cast(Any, compression),
            index=index,
            **accepted,
        )

        return full_path, rejected

    else:
        data.to_parquet(
            path=full_path,
            engine=cast(Any, engine),
            compression=cast(Any, compression),
            index=index,
            **kwargs,
        )

        return full_path, {}


def load_parquet(
    filepath: str | AnyPath,
    engine: ParquetEngine = "auto",
    columns: list[str] | None = None,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Load data from a Parquet file into a DataFrame.

    Parameters
    ----------
    filepath : str | AnyPath
        Path to the target Parquet file.
    engine : ParquetEngine, default "auto"
        Parquet library to use (pyarrow or fastparquet).
    columns : list[str] | None, default None
        If not None, only these columns will be read from the file.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `pd.read_parquet()`.
    **kwargs : Any
        Additional arguments passed to the engine. Supports 'storage_options'
        for remote filesystems (e.g., S3, GCS) via fsspec.

    Returns
    -------
    data : pd.DataFrame
        The loaded pandas DataFrame.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with
        the read method. Returns an empty dictionary if `safe_call` is False.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.parquet'.
    """
    FileType.PARQUET.validate_extension(filepath)
    path_obj = AnyPath(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    if safe_call:
        # Define known valid parameters for pd.read_parquet to simulate a strict signature
        # This prevents an invalid parameter from reaching the engine
        # The parquet internal functions have a **kwargs parameter that causes any
        # parameter to be passed when using dsr_utils.safe_call
        _valid_params = _get_valid_params(FileType.PARQUET, "load")
        valid_params = set(_valid_params) if _valid_params else {}

        accepted = {k: v for k, v in kwargs.items() if k in valid_params}
        rejected = {k: v for k, v in kwargs.items() if k not in valid_params}

        # Call with only the manually verified 'accepted' parameters
        df = pd.read_parquet(path_obj, engine=engine, columns=columns, **accepted)
        return df, rejected
    else:
        df = pd.read_parquet(path_obj, engine=engine, columns=columns, **kwargs)
        return df, {}
