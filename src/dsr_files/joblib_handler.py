"""JOBLIB file handling operations."""

from pathlib import Path
from typing import Any
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
    Save data to JOBLIB file using joblib serialization.

    Args:
        data: Any Python object to save
        output_dir: Directory to save the file
        filename: Name of the file (without the extension)
        compress: Compression level (0-9 or compression spec tuple)
        **kwargs: Additional arguments passed to joblib.dump()

    Returns:
        Path to the saved JOBLIB file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    full_path = Path(output_dir) / f"{filename}.joblib"
    joblib.dump(data, full_path, compress=compress, **kwargs)  # type: ignore[arg-type]
    return full_path


def load_joblib(
    filepath: str | Path,
    **kwargs: Any,
) -> Any:
    """
    Load data from JOBLIB file.

    Args:
        filepath: Path to JOBLIB file (string or Path object)
        **kwargs: Additional arguments passed to joblib.load()

    Returns:
        Deserialized Python object
    """
    validate_extension(filepath, ".joblib")
    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    return joblib.load(path_obj, **kwargs)
