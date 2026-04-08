from pathlib import Path


def validate_extension(filepath: str | Path, expected_extensions: str | list[str]) -> None:
    """
    Validate that the file has one of the expected extensions.

    Args:
        filepath: Path to the file
        expected_extensions: Single extension (e.g. '.csv') or list of extensions

    Raises:
        ValueError: If extension doesn't match
    """
    path = Path(filepath)
    if isinstance(expected_extensions, str):
        expected_extensions = [expected_extensions]

    # Ensure extensions start with .
    expected_extensions = [e if e.startswith(".") else f".{e}" for e in expected_extensions]

    if path.suffix.lower() not in [e.lower() for e in expected_extensions]:
        raise ValueError(
            f"Invalid file extension '{path.suffix}'. "
            f"Expected one of: {', '.join(expected_extensions)}"
        )
