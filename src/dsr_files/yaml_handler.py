# dsr_files/yaml_handler.py
from pathlib import Path
from typing import Any, Optional

import yaml
from dsr_files.json_handler import to_JSON_safe


def save_yaml(data: Any, filepath: Path, header: Optional[str] = None) -> None:
    """
    Saves data to a YAML file with standardized formatting and optional headers.

    This function utilizes `to_JSON_safe` to recursively convert complex Python
    objects (such as Enums, Paths, and NumPy types) into YAML-serializable primitives
    before writing to disk.

    Parameters
    ----------
    data : Any
        The Python object, list, or dictionary to be serialized.
    filepath : Path
        The destination filesystem path for the YAML file.
    header : str, optional
        A string to be prepended to the file as a comment block. Lines are
        automatically prefixed with '#'.

    Notes
    -----
    - Uses `yaml.safe_dump` to prevent arbitrary code execution.
    - Sets `default_flow_style=False` for human-readable block formatting.
    - Sets `sort_keys=False` to preserve the original order of recommendations
      or dictionary entries.
    """
    serializable_data = to_JSON_safe(data)

    with open(filepath, "w", encoding="utf-8") as f:
        if header:
            # Ensure the header is properly commented and followed by a newline
            commented_header = "\n".join(f"# {line}" for line in header.splitlines())
            f.write(commented_header + "\n\n")

        yaml.safe_dump(serializable_data, f, default_flow_style=False, sort_keys=False)


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


def load_yaml(filepath: Path) -> Any:
    """
    Loads data from a YAML file into Python objects with unique key validation.

    Parameters
    ----------
    filepath : Path
        The path to the YAML file to be loaded.

    Returns
    -------
    Any
        The parsed content of the YAML file (typically a dict or list).

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist.
    yaml.constructor.ConstructorError
        If the YAML contains duplicate keys.
    yaml.YAMLError
        If the file contains invalid YAML syntax.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=UniqueKeyLoader)
