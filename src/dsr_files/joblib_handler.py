"""JOBLIB file handling operations."""

from pathlib import Path
from typing import Any, cast

import joblib
from dsr_files.utils import validate_extension


def save_joblib(
    data: Any,
    output_dir: Path,
    filename: str,
    compress: int | tuple[str, int] = 3,
    **kwargs: Any,
) -> Path:
    """
    Save a Python object to a JOBLIB file using joblib serialization.

    Parameters
    ----------
    data : Any
        The Python object to persist (e.g., a trained model or a large array).
    output_dir : Path
        The destination directory.
    filename : str
        The base name of the file (extension '.joblib' is appended automatically).
    compress : int | tuple[str, int], default 3
        The compression level from 0 to 9, or a tuple specifying the
        compression method and level.
    **kwargs : Any
        Additional keyword arguments passed directly to `joblib.dump()`.

    Returns
    -------
    Path
        The full path to the saved JOBLIB file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    full_path = output_dir / f"{filename}.joblib"

    # Cast compress to Any specifically for the call to satisfy the restrictive stub
    joblib.dump(data, full_path, compress=cast(Any, compress), **kwargs)

    return full_path


def load_joblib(
    filepath: str | Path,
    **kwargs: Any,
) -> Any:
    """
    Load and deserialize data from a JOBLIB file.

    Parameters
    ----------
    filepath : str | Path
        Path to the target JOBLIB file.
    **kwargs : Any
        Additional keyword arguments passed directly to `joblib.load()`.

    Returns
    -------
    Any
        The deserialized Python object.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.joblib'.
    """
    validate_extension(filepath, ".joblib")

    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    return joblib.load(path_obj, **kwargs)
