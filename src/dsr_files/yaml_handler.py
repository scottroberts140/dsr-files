# dsr_files/yaml_handler.py
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from cloudpathlib import AnyPath, CloudPath
from dsr_files.enums import FileType
from dsr_files.json_handler import to_JSON_safe
from dsr_files.utils import MkDir, get_full_path
from dsr_utils.reflection import safe_call as d_safe_call


def save_yaml(
    data: Any,
    output_dir: AnyPath | str,
    filename: str,
    header: Optional[str] = None,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Saves data to a YAML file with standardized formatting and optional headers.

    This function utilizes `to_JSON_safe` to recursively convert complex Python
    objects (such as Enums, Paths, and NumPy types) into YAML-serializable primitives
    before writing to disk.

    Parameters
    ----------
    data : AnyPath | str
        The Python object, list, or dictionary to be serialized.
    output_dir : Path
        The destination directory.
    filename : str
        The base name of the file (extension '.yaml' is appended automatically).
    header : str, optional
        A string to be prepended to the file as a comment block. Lines are
        automatically prefixed with '#'.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `yaml.safe_dump()`.
    **kwargs : Any
        Additional keyword arguments passed to `yaml.safe_dump()`. If `safe_call`
        is True, these are automatically filtered based on the library signature.

    Returns
    -------
    full_path : Path, CloudPath
        The full path to the saved YAML file.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        save method. Returns an empty dictionary if `safe_call` is False.

    Notes
    -----
    - Uses `yaml.safe_dump` to prevent arbitrary code execution.
    - Sets `default_flow_style=False` for human-readable block formatting.
    - Sets `sort_keys=False` to preserve the original order of recommendations
      or dictionary entries.
    """
    full_path = get_full_path(output_dir, FileType.YAML.format_filename(filename), MkDir())
    serializable_data = to_JSON_safe(data)

    with open(full_path, "w", encoding="utf-8") as f:
        if header:
            # Ensure the header is properly commented and followed by a newline
            commented_header = "\n".join(f"# {line}" for line in header.splitlines())
            f.write(commented_header + "\n\n")

        if safe_call:
            _, rejected = d_safe_call(
                yaml.safe_dump,
                kwargs,
                data=serializable_data,
                stream=f,
                default_flow_style=False,
                sort_keys=False,
            )
            return full_path, rejected
        else:
            yaml.safe_dump(serializable_data, f, default_flow_style=False, sort_keys=False)
            return full_path, {}


class UniqueKeyLoader(yaml.SafeLoader):
    """
    A custom YAML loader that enforces unique keys in mappings.

    Extends `yaml.SafeLoader` to raise a `ConstructorError` if a duplicate key
    is encountered during parsing, preventing silent data loss from
    overwritten keys.
    """

    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise yaml.constructor.ConstructorError(f"Duplicate recommendation ID found: {key}")
            mapping.append(key)
        return super().construct_mapping(node, deep)


def load_yaml(
    filepath: AnyPath | str,
    safe_call: bool = False,
    **kwargs: Any,
) -> Any:
    """
    Loads data from a YAML file into Python objects with unique key validation.

    Parameters
    ----------
    filepath : AnyPath | str
        The path to the YAML file to be loaded.
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `yaml.load()`.
    **kwargs : Any
        Additional keyword arguments passed directly to `yaml.load()`. If `safe_call`
        is True, these are automatically filtered based on the library signature.

    Returns
    -------
    data : Any
        The parsed content of the YAML file (typically a dict or list).
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        load method. Returns an empty dictionary if `safe_call` is False.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist.
    ValueError
        If the file extension is not '.yaml'.
    yaml.constructor.ConstructorError
        If the YAML contains duplicate keys.
    yaml.YAMLError
        If the file contains invalid YAML syntax.
    """
    FileType.YAML.validate_extension(filepath)

    with open(str(filepath), "r", encoding="utf-8") as f:
        if safe_call:
            y, rejected = d_safe_call(yaml.load, kwargs, stream=f, Loader=UniqueKeyLoader)
            return y, rejected
        else:
            y = yaml.load(f, Loader=UniqueKeyLoader)
            return y, {}
