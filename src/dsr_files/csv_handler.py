"""CSV file handling operations."""

from pathlib import Path
from typing import Any

import pandas as pd
from dsr_files.utils import validate_extension


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
    output_dir: Path,
    filename: str,
    index: bool = False,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> Path:
    """
    Save a DataFrame or dictionary to a CSV file.

    Parameters
    ----------
    data : pd.DataFrame | dict[str, Any]
        The data to persist to disk.
    output_dir : Path
        The destination directory.
    filename : str
        The base name of the file (extension '.csv' is appended automatically).
    index : bool, default False
        Whether to include the DataFrame index in the output file.
    encoding : str, default "utf-8"
        The character encoding for the resulting file.
    **kwargs : Any
        Additional keyword arguments passed directly to `pd.DataFrame.to_csv()`.

    Returns
    -------
    Path
        The full path to the saved CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    full_path = output_dir / f"{filename}.csv"

    df = create_csv(data)
    df.to_csv(full_path, index=index, encoding=encoding, **kwargs)

    return full_path


def load_csv(
    filepath: str | Path,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load data from a CSV file into a DataFrame.

    Parameters
    ----------
    filepath : str | Path
        Path to the target CSV file.
    encoding : str, default "utf-8"
        The character encoding used to read the file.
    **kwargs : Any
        Additional keyword arguments passed directly to `pd.read_csv()`.

    Returns
    -------
    pd.DataFrame
        The loaded data.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.csv'.
    """
    validate_extension(filepath, ".csv")

    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    return pd.read_csv(path_obj, encoding=encoding, **kwargs)
