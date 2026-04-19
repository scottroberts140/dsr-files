"""General utility functions for file operations."""

import warnings
from pathlib import Path
from typing import NamedTuple

from cloudpathlib import AnyPath, CloudPath


def validate_extension(filepath: str | Path, expected_extensions: str | list[str]) -> None:
    """
    [DEPRECATED] Validate that a file has one of the expected extensions.

    .. deprecated:: 3.0.0
       Use :meth:`dsr_files.enums.FileType.validate_extension` instead. This
       function is maintained for backward compatibility but will be removed
       in a future major release.

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
    warnings.warn(
        "validate_extension is deprecated and will be removed in v4.0.0. "
        "Use FileType.validate_extension() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
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


class MkDir(NamedTuple):
    """
    Configuration for directory creation logic.

    Attributes
    ----------
    mkdir : bool, default True
        Whether to attempt directory creation.
    parents : bool, default True
        Whether to create parent directories if they do not exist.
    exist_ok : bool, default True
        If True, do not raise an error if the directory already exists.
    """

    mkdir: bool = True
    parents: bool = True
    exist_ok: bool = True


def get_full_path(output_dir: AnyPath | str, filename: str, mkdir: MkDir) -> CloudPath | Path:
    """
    Construct a full path from a directory and filename, optionally creating the directory.

    This function utilizes `AnyPath` to polymorphically handle both local filesystems
    and cloud protocols (e.g., S3, GCS) without corrupting URI prefixes.

    Parameters
    ----------
    output_dir : AnyPath | str
        The target directory. Can be a local path string, a pathlib.Path,
        or a cloud URI (e.g., 's3://bucket/path').
    filename : str
        The name of the file, including extension.
    mkdir : MkDir
        A NamedTuple containing directory creation settings. For cloud paths,
        mkdir operations are handled safely by `cloudpathlib`.

    Returns
    -------
    CloudPath | Path
        the combined path object corresponding to the input protocol.
    """
    output_path = AnyPath(output_dir)

    if mkdir.mkdir:
        # cloudpathlib handles mkdir on remote URIs as a virtual operation
        output_path.mkdir(parents=mkdir.parents, exist_ok=mkdir.exist_ok)

    return output_path / filename
