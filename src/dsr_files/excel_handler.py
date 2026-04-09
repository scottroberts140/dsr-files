"""Excel file handling operations."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from dsr_files.utils import validate_extension

# Define a type alias for the supported engines
ExcelEngine = Literal["xlsxwriter", "openpyxl", "odf", "auto"]


def create_excel(data: pd.DataFrame | dict[Any, Any] | list[Any]) -> pd.DataFrame:
    """
    Standardize various input types into a pandas DataFrame.

    Parameters
    ----------
    data : pd.DataFrame | dict[Any, Any] | list[Any]
        Input data which can be a DataFrame, a dictionary, or a list of
        dictionaries.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame created from the input data.

    Raises
    ------
    ValueError
        If the data cannot be converted to a DataFrame.
    """
    if isinstance(data, pd.DataFrame):
        return data

    try:
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(f"Failed to convert data to DataFrame: {e}")
        raise ValueError(f"Could not convert input to DataFrame: {e}") from e


@dataclass
class ExcelSheetConfig:
    """
    Configuration for an individual sheet in an Excel workbook.

    Attributes
    ----------
    data : pd.DataFrame | dict[Any, Any] | list[Any]
        The data to be written to the sheet.
    sheet_name : str
        The name of the worksheet.
    index : bool, default False
        Whether to include the DataFrame index.
    header : bool, default True
        Whether to include the column headers.
    """

    data: pd.DataFrame | dict[Any, Any] | list[Any]
    sheet_name: str
    index: bool = False
    header: bool = True


def save_excel(
    data: pd.DataFrame | list[ExcelSheetConfig],
    output_dir: Path,
    filename: str,
    engine: ExcelEngine = "auto",
    **kwargs: Any,
) -> Path:
    """
    Save data to an Excel file with support for single or multiple sheets.

    Parameters
    ----------
    data : pd.DataFrame | list[ExcelSheetConfig]
        Either a single DataFrame for a one-sheet workbook, or a list
        of ExcelSheetConfig objects for multiple sheets.
    output_dir : Path
        The destination directory.
    filename : str
        The base name of the file (extension '.xlsx' is added).
    engine : ExcelEngine, default "auto"
        The writing engine (xlsxwriter, openpyxl, odf, or auto).
    **kwargs : Any
        Additional arguments passed to `to_excel()` for single-sheet mode.

    Returns
    -------
    Path
        The full path to the saved Excel file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    full_path = output_dir / f"{filename}.xlsx"

    # Map 'auto' to None so pandas uses its default detection
    write_engine = None if engine == "auto" else engine

    try:
        if isinstance(data, pd.DataFrame):
            data.to_excel(full_path, engine=write_engine, **kwargs)
        else:
            with pd.ExcelWriter(full_path, engine=write_engine) as writer:
                for sheet_cfg in data:
                    df = create_excel(sheet_cfg.data)
                    df.to_excel(
                        writer,
                        sheet_name=sheet_cfg.sheet_name,
                        index=sheet_cfg.index,
                        header=sheet_cfg.header,
                    )
    except ModuleNotFoundError as e:
        target = engine if engine != "auto" else "openpyxl/xlsxwriter"
        logging.error(f"Excel export failed: Install engine (pip install {target})")
        raise ModuleNotFoundError(f"Missing Excel engine: {e}") from e

    return full_path


def load_excel(
    filepath: str | Path,
    sheet_name: str | int = 0,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load data from an Excel file into a DataFrame.

    Parameters
    ----------
    filepath : str | Path
        Path to the Excel file.
    sheet_name : str | int, default 0
        The sheet to read (name or zero-based index).
    **kwargs : Any
        Additional keyword arguments passed to `pd.read_excel()`.

    Returns
    -------
    pd.DataFrame
        The loaded data.
    """
    validate_extension(filepath, [".xlsx", ".xls", ".xlsm", ".ods"])
    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    return pd.read_excel(path_obj, sheet_name=sheet_name, **kwargs)
