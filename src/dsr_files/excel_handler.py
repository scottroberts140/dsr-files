"""Excel file handling operations."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union

import pandas as pd
from cloudpathlib import AnyPath, CloudPath
from dsr_files.enums import FileType
from dsr_files.utils import MkDir, get_full_path
from dsr_utils.reflection import safe_call as d_safe_call

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
    output_dir: AnyPath | str,
    filename: str,
    engine: ExcelEngine = "auto",
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[Union[Path, CloudPath], dict[str, Any]]:
    """
    Save data to an Excel file with support for single or multiple sheets.

    Parameters
    ----------
    data : pd.DataFrame | list[ExcelSheetConfig]
        Either a single DataFrame for a one-sheet workbook, or a list
        of ExcelSheetConfig objects for multiple sheets.
    output_dir : AnyPath | str
        The destination directory.
    filename : str
        The base name of the file (extension '.xlsx' is added).
    engine : ExcelEngine, default "auto"
        The writing engine (xlsxwriter, openpyxl, odf, or auto).
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling the underlying pandas Excel methods.
    **kwargs : Any
        Additional arguments passed to `to_excel()` for single-sheet mode.
        In multi-sheet mode, these parameters are applied to each individual sheet.

    Returns
    -------
    full_path : Path, CloudPath
        The full path to the saved Excel file.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with the
        save method. Returns an empty dictionary if `safe_call` is False.

    Raises
    ------
    ModuleNotFoundError
        If the required Excel engine is not installed in the environment.
    """
    full_path = get_full_path(output_dir, FileType.EXCEL.format_filename(filename), MkDir())

    # Map 'auto' to None so pandas uses its default detection
    write_engine = None if engine == "auto" else engine

    try:
        if safe_call:
            if isinstance(data, pd.DataFrame):
                _, rejected = d_safe_call(
                    data.to_excel, kwargs, excel_writer=full_path, engine=write_engine
                )
                return full_path, rejected
            else:
                # Rejected parameters will be the same for every call, so they
                # can be overwritten for each sheet.
                rejected = {}
                with pd.ExcelWriter(full_path, engine=write_engine) as writer:
                    for sheet_cfg in data:
                        df = create_excel(sheet_cfg.data)
                        _, rejected = d_safe_call(
                            df.to_excel,
                            kwargs,
                            excel_writer=writer,
                            sheet_name=sheet_cfg.sheet_name,
                            index=sheet_cfg.index,
                            header=sheet_cfg.header,
                        )

                return full_path, rejected
        else:
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

            return full_path, {}
    except ModuleNotFoundError as e:
        target = engine if engine != "auto" else "openpyxl/xlsxwriter"
        logging.error(f"Excel export failed: Install engine (pip install {target})")
        raise ModuleNotFoundError(f"Missing Excel engine: {e}") from e


def load_excel(
    filepath: str | AnyPath,
    sheet_name: str | int = 0,
    safe_call: bool = False,
    **kwargs: Any,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Load data from an Excel file into a DataFrame.

    Parameters
    ----------
    filepath : str | AnyPath
        Path to the Excel file.
    sheet_name : str | int, default 0
        The sheet to read (name or zero-based index).
    safe_call : bool, default False
        If True, utilizes `dsr_utils.safe_call` to filter incompatible parameters
        from `**kwargs` before calling `pd.read_excel()`.
    **kwargs : Any
        Additional keyword arguments passed directly to `pd.read_excel()`.

    Returns
    -------
    data : pd.DataFrame
        The loaded pandas DataFrame.
    rejected_params : dict[str, Any]
        A dictionary of parameters from `**kwargs` that were incompatible with
        the read method. Returns an empty dictionary if `safe_call` is False.

    Raises
    ------
    FileNotFoundError
        If the specified filepath does not exist on disk.
    ValueError
        If the file extension is not a supported Excel format.
    """
    FileType.EXCEL.validate_extension(filepath)
    path_obj = AnyPath(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    if safe_call:
        df, rejected = d_safe_call(pd.read_excel, kwargs, io=path_obj, sheet_name=sheet_name)
        return df, rejected
    else:
        df = pd.read_excel(path_obj, sheet_name=sheet_name, **kwargs)
        return df, {}
