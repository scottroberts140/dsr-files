"""JOBLIB file handling operations."""

from pathlib import Path
from typing import Any
import joblib


def save_joblib(
    data: Any,
    filepath: Path,
    filename: str,
    compress: int | tuple[str, int] = 3,
    **kwargs: Any,
) -> Path:
    """
    Save data to JOBLIB file using joblib serialization.

    Args:
        data: Any Python object to save
        filepath: Path to save the file
        filename: Name of the file (without the extension)
        compress: Compression level (0-9 or compression spec tuple)
        **kwargs: Additional arguments passed to joblib.dump()

    Returns:
        Path to the saved JOBLIB file
    """
    filepath.mkdir(parents=True, exist_ok=True)
    full_path = Path(filepath) / f"{filename}.joblib"
    joblib.dump(data, full_path, compress=compress, **kwargs)  # type: ignore[arg-type]
    return full_path


def load_joblib(
    filepath: Path,
    **kwargs: Any,
) -> Any:
    """
    Load data from JOBLIB file.

    Args:
        filepath: Path to JOBLIB file
        **kwargs: Additional arguments passed to joblib.load()

    Returns:
        Deserialized Python object
    """
    if not filepath.exists():
        raise FileNotFoundError(f"No audit state found at {filepath}")

    return joblib.load(filepath, **kwargs)
