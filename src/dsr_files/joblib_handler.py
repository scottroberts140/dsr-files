"""JOBLIB file handling operations."""

from pathlib import Path
from typing import Any, Union, cast

import joblib
import pandas as pd
from cloudpathlib import AnyPath, CloudPath
from dsr_utils.reflection import safe_call as d_safe_call

from dsr_files.enums import FileType
from dsr_files.utils import MkDir, PathLike, _get_valid_params, get_full_path


def save_joblib(
    data: Any,
    output_dir: PathLike,
    filename: str,
    compress: int | tuple[str, int] = 3,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Save a Python object to a JOBLIB file using joblib serialization.

    Parameters
    ----------
    data : Any
        The Python object to persist (e.g., a trained model or a large array).
    output_dir : str | Path | CloudPath
        The destination directory.
    filename : str
        The base name of the file (extension '.joblib' is appended automatically).
    compress : int | tuple[str, int], default 3
        The compression level from 0 to 9, or a tuple specifying the
        compression method and level.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `joblib.dump()`.
    **kwargs : Any
        Additional keyword arguments passed directly to `joblib.dump()`. If `safe_call`
        is True, these are automatically filtered based on the `joblib.dump` signature.

    Returns
    -------
    full_path : Path, CloudPath
        The full path to the saved JOBLIB file.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        save method. Returns an empty dictionary if `safe_call` is False.
    """
    full_path = get_full_path(
        output_dir, FileType.JOBLIB.format_filename(filename), MkDir()
    )

    # Cast compress to Any specifically for the call to satisfy the restrictive stub
    if safe_call:
        valid_params = _get_valid_params(FileType.JOBLIB, "save")
        _, rejected = d_safe_call(
            joblib.dump,
            kwargs,
            value=data,
            filename=full_path,
            compress=cast(Any, compress),
            valid_params=valid_params,
        )
        return full_path, rejected
    else:
        joblib.dump(data, full_path, compress=cast(Any, compress), **kwargs)
        return full_path, {}


def load_joblib(
    filepath: PathLike,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Any, dict[str, Any]]:
    """
    Load and deserialize data from a JOBLIB file.

    Parameters
    ----------
    filepath : str | Path | CloudPath
        Path to the target JOBLIB file.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `joblib.load()`.
    **kwargs : Any
        Additional keyword arguments passed directly to `joblib.load()`. If `safe_call`
        is True, these are automatically filtered based on the `joblib.load` signature.

    Returns
    -------
    data : Any
        The deserialized Python object.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        load method. Returns an empty dictionary if `safe_call` is False.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.joblib'.
    """
    FileType.JOBLIB.validate_extension(filepath)

    path_obj = AnyPath(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    if safe_call:
        valid_params = _get_valid_params(FileType.JOBLIB, "load")
        j, rejected = d_safe_call(
            joblib.load, kwargs, filename=path_obj, valid_params=valid_params
        )
        return j, rejected
    else:
        j = joblib.load(path_obj, **kwargs)
        return j, {}


def load_joblib_dataframe(
    source_dir: PathLike,
    filename: str,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Load a JOBLIB artifact from directory + filename and validate DataFrame type.

    Parameters
    ----------
    source_dir : str | Path | CloudPath
        Directory containing the source JOBLIB file.
    filename : str
        Source file name with or without the ``.joblib`` extension.
    safe_call : bool, default False
        Whether to filter unsupported kwargs before calling ``joblib.load``.
    **kwargs : Any
        Additional arguments forwarded to :func:`load_joblib`.

    Returns
    -------
    tuple[pd.DataFrame, dict[str, Any]]
        Loaded DataFrame and rejected kwargs dict.

    Raises
    ------
    TypeError
        If the loaded object is not a pandas DataFrame.
    """
    source_file = FileType.JOBLIB.format_filename(filename)
    source_path = AnyPath(source_dir) / source_file
    obj, rejected = load_joblib(source_path, safe_call=safe_call, **kwargs)

    if not isinstance(obj, pd.DataFrame):
        raise TypeError(
            "Expected a pandas DataFrame in JOBLIB artifact "
            f"'{source_path}', but loaded {type(obj).__name__}."
        )

    return obj, rejected
