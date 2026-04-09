"""General utility functions for file operations."""

from pathlib import Path


def validate_extension(filepath: str | Path, expected_extensions: str | list[str]) -> None:
    """
    Validate that a file has one of the expected extensions.

    Parameters
    ----------
    filepath : str | Path
        The path to the file to validate.
    expected_extensions : str | list[str]
        A single extension (e.g., '.csv') or a list of valid
        extensions (e.g., ['.xlsx', '.xls']).

    Raises
    ------
    ValueError
        If the file's extension does not match any of the
        expected extensions.
    """
    path = Path(filepath)

    # Standardize expected_extensions to a list
    if isinstance(expected_extensions, str):
        expected_extensions = [expected_extensions]

    # Ensure extensions start with a dot and are lowercased for comparison
    valid_exts = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in expected_extensions]

    if path.suffix.lower() not in valid_exts:
        raise ValueError(
            f"Invalid file extension '{path.suffix}'. " f"Expected one of: {', '.join(valid_exts)}"
        )
