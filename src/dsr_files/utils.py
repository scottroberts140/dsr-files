"""General utility functions for file operations."""

import functools
import warnings
from pathlib import Path
from typing import Literal, NamedTuple

from cloudpathlib import AnyPath, CloudPath

from dsr_files.enums import FileType

PathLike = str | Path | CloudPath


def validate_extension(
    filepath: PathLike, expected_extensions: str | list[str]
) -> None:
    """
    [DEPRECATED] Validate that a file has one of the expected extensions.

    .. deprecated:: 3.0.0
       Use :meth:`dsr_files.enums.FileType.validate_extension` instead. This
       function is maintained for backward compatibility but will be removed
       in a future major release.

    Parameters
    ----------
    filepath : str | Path | CloudPath
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
    valid_exts = [
        e.lower() if e.startswith(".") else f".{e.lower()}" for e in expected_extensions
    ]

    if path.suffix.lower() not in valid_exts:
        raise ValueError(
            f"Invalid file extension '{path.suffix}'. "
            f"Expected one of: {', '.join(valid_exts)}"
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


def get_full_path(
    output_dir: PathLike,
    filename: str,
    mkdir: MkDir,
    replace_existing: bool = False,
) -> CloudPath | Path:
    """
    Construct a full path from a directory and filename, optionally creating the directory.

    This function utilizes `AnyPath` to polymorphically handle both local filesystems
    and cloud protocols (e.g., S3, GCS) without corrupting URI prefixes.

    Parameters
    ----------
    output_dir : str | Path | CloudPath
        The target directory. Can be a local path string, a pathlib.Path,
        or a cloud URI (e.g., 's3://bucket/path').
    filename : str
        The name of the file, including extension.
    mkdir : MkDir
        A NamedTuple containing directory creation settings. For cloud paths,
        mkdir operations are handled safely by `cloudpathlib`.
    replace_existing : bool, default False
        If True and a file already exists at the final path, remove it before
        returning the path. This helps avoid stale in-place overwrite behavior
        in some external viewers.

    Returns
    -------
    CloudPath | Path
        the combined path object corresponding to the input protocol.
    """
    output_path = AnyPath(output_dir)

    if mkdir.mkdir:
        # cloudpathlib handles mkdir on remote URIs as a virtual operation
        output_path.mkdir(parents=mkdir.parents, exist_ok=mkdir.exist_ok)

    full_path = output_path / filename

    if replace_existing and full_path.exists():
        try:
            full_path.unlink()
        except FileNotFoundError:
            # Defensive guard for race conditions where another process deletes
            # the file between exists() and unlink().
            pass

    return full_path


@functools.lru_cache(maxsize=1)
def _get_valid_param_sets() -> dict:
    """
    Load and cache the master parameter registry from the package resources.

    This function utilizes the `UniqueKeyLoader` to ensure the integrity of the
    `params.yaml` file by preventing duplicate key definitions.
    It uses a local import of `load_yaml` to resolve circular dependencies between
    the utility and YAML handler modules.

    Returns:
        dict: The master dictionary of valid parameters for all supported file types.
    """
    from dsr_files.yaml_handler import load_yaml

    path = Path(__file__).parent / "resources/params.yaml"
    return load_yaml(str(path))[
        0
    ]  # Accessing the data part of the (result, rejected) tuple


@functools.lru_cache(maxsize=8)
def _get_valid_params(file_type: FileType, op: Literal["save", "load"]):
    """
    Retrieve the set of valid parameters for a specific FileType and operation.

    The function maps the `FileType` to the corresponding key in the cached YAML registry
    by stripping the leading dot from the preferred extension (e.g., ".csv" becomes "csv").
    If the requested operation or file type is not explicitly configured in the registry,
    it returns None to allow the `safe_call` utility to fall back to standard reflection.

    Args:
        file_type (FileType): The format of the file being processed.
        op (Literal["save", "load"]): The file operation to perform.

    Returns:
        set[str] | None: A set of valid parameter names for the engine, or None if not configured.

    Raises:
        ValueError: If the `file_type` is not one of the supported formats
                    (CSV, PARQUET, JSON, JOBLIB) that require manual registry filtering.
    """
    supported = {FileType.CSV, FileType.PARQUET, FileType.JSON, FileType.JOBLIB}

    if file_type not in supported:
        raise ValueError(f"FileType {file_type.name} does not support valid_params")

    registry = _get_valid_param_sets()
    key = file_type.preferred_extension().lstrip(".")
    param_list = registry.get(key, {}).get(op)
    return set(param_list) if param_list else None
