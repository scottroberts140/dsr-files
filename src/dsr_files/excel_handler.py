"""Excel file handling operations."""

from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from typing import Any, Optional, List, Union, Literal, Dict
import logging

# Define a type alias for the supported engines
ExcelEngine = Literal["xlsxwriter", "openpyxl", "odf", "auto"]


def create_excel(data: Union[pd.DataFrame, Dict[Any, Any], List[Any]]) -> pd.DataFrame:
    """
    Create a DataFrame from various inputs.

    Args:
        data: Input data - can be DataFrame, dictionary, or list of dictionaries

    Returns:
        pandas DataFrame created from the input data
    """
    if isinstance(data, pd.DataFrame):
        return data

    try:
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(f"Failed to convert data to DataFrame: {e}")
        return pd.DataFrame()


@dataclass
class ExcelSheetConfig:
    """Configuration for an individual sheet in an Excel workbook."""

    data: Union[pd.DataFrame, Dict[Any, Any], List[Any]]
    sheet_name: str
    index: bool = False
    header: bool = True


def save_excel(
    data: Union[pd.DataFrame, List[ExcelSheetConfig]],
    filepath: Path,
    filename: str,
    engine: ExcelEngine = "xlsxwriter",
    **kwargs: Any,
) -> Path:
    """
    Save data to Excel file with support for single or multiple sheets.

    Args:
        data: Either a DataFrame for single-sheet or list of ExcelSheetConfig for multi-sheet
        filepath: Path to save the file
        filename: Name of the file (without the extension)
        engine: Excel writing engine (xlsxwriter, openpyxl, odf, or auto)
        **kwargs: Additional arguments passed to DataFrame.to_excel() for single-sheet mode

    Returns:
        Path to the saved Excel file
    """
    filepath.mkdir(parents=True, exist_ok=True)
    full_path = filepath / f"{filename}.xlsx"

    try:
        if isinstance(data, pd.DataFrame):
            data.to_excel(full_path, engine=engine, **kwargs)
        else:
            with pd.ExcelWriter(full_path, engine=engine) as writer:
                for sheet_cfg in data:
                    df = create_excel(sheet_cfg.data)
                    df.to_excel(
                        writer,
                        sheet_name=sheet_cfg.sheet_name,
                        index=sheet_cfg.index,
                        header=sheet_cfg.header,
                    )
    except ModuleNotFoundError:
        logging.error(f"Excel export failed: Install '{engine}' (pip install {engine})")
        raise

    return full_path


def load_excel(
    filepath: str | Path,
    sheet_name: str | int = 0,
    **kwargs: Any,
) -> pd.DataFrame:
    """
    Load data from Excel file.

    Args:
        filepath: Path to Excel file
        sheet_name: Sheet to read (name or index, default: 0 for first sheet)
        **kwargs: Additional arguments passed to pd.read_excel()

    Returns:
        pandas DataFrame loaded from Excel file
    """
    return pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
