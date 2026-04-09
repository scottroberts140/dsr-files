"""Parquet file handling operations."""

from pathlib import Path
from typing import Any, Literal, cast

import pandas as pd
from dsr_files.utils import validate_extension

# Define supported engines for Parquet operations
ParquetEngine = Literal["pyarrow", "fastparquet", "auto"]


def save_parquet(
    data: pd.DataFrame,
    output_dir: Path,
    filename: str,
    engine: ParquetEngine = "auto",
    compression: str | None = "snappy",
    index: bool | None = None,
    **kwargs: Any,
) -> Path:
    """
    Save a DataFrame to a Parquet file.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame to persist to disk.
    output_dir : Path
        The destination directory.
    filename : str
        The base name of the file (extension '.parquet' is added).
    engine : ParquetEngine, default "auto"
        Parquet library to use (pyarrow or fastparquet).
    compression : str | None, default "snappy"
        Name of the compression to use.
    index : bool | None, default None
        Whether to include the DataFrame index.
    **kwargs : Any
        Additional arguments passed to `pd.DataFrame.to_parquet()`.

    Returns
    -------
    Path
        The full path to the saved Parquet file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    full_path = output_dir / f"{filename}.parquet"

    # Fastparquet fix: Convert Arrow-backed strings to object dtype
    if engine == "fastparquet":
        data = data.copy()
        for col in data.select_dtypes(include=["string", "object"]).columns:
            data[col] = data[col].astype(object)

    data.to_parquet(
        path=full_path,
        engine=cast(Any, engine),
        compression=cast(Any, compression),
        index=index,
        **kwargs,
    )

    return full_path


def load_parquet(
    filepath: str | Path,
    engine: ParquetEngine = "auto",
    columns: list[str] | None = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load data from a Parquet file into a DataFrame.

    Parameters
    ----------
    filepath : str | Path
        Path to the target Parquet file.
    engine : ParquetEngine, default "auto"
        Parquet library to use (pyarrow or fastparquet).
    columns : list[str] | None, default None
        If not None, only these columns will be read from the file.
    **kwargs : Any
        Additional arguments passed to `pd.read_parquet()`.

    Returns
    -------
    pd.DataFrame
        The loaded data.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not '.parquet'.
    """
    validate_extension(filepath, ".parquet")
    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    return pd.read_parquet(path_obj, engine=engine, columns=columns, **kwargs)
