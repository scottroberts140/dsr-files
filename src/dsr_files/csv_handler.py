"""CSV file handling operations."""

from pathlib import Path
from typing import Any, Optional
import pandas as pd


def create_csv(data: dict[str, Any] | pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame from dictionary or return DataFrame as-is.

    Args:
        data: Dictionary or pandas DataFrame

    Returns:
        pandas DataFrame
    """
    if isinstance(data, dict):
        return pd.DataFrame(data)
    return data


def save_csv(
    data: pd.DataFrame | dict[str, Any],
    filepath: Path,
    filename: str,
    index: bool = False,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> Path:
    """
    Save data to CSV file.

    Args:
        data: DataFrame or dictionary to save
        filepath: Path to save the file
        filename: Name of the file (without the extension)
        index: Whether to write row indices
        encoding: File encoding (default: utf-8)
        **kwargs: Additional arguments passed to DataFrame.to_csv()

    Returns:
        Path to the saved CSV file
    """
    filepath.mkdir(parents=True, exist_ok=True)
    full_path = Path(filepath) / f"{filename}.csv"
    df = create_csv(data) if isinstance(data, dict) else data
    df.to_csv(full_path, index=index, encoding=encoding, **kwargs)
    return full_path


def load_csv(
    filepath: str | Path,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load data from CSV file.

    Args:
        filepath: Path to CSV file
        encoding: File encoding (default: utf-8)
        **kwargs: Additional arguments passed to pd.read_csv()

    Returns:
        pandas DataFrame
    """
    return pd.read_csv(filepath, encoding=encoding, **kwargs)
