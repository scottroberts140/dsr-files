"""
Enumerations for file handling and type identification.

This module defines the supported file formats used across the
dsr-files library for reading, writing, and auditing.
"""

from enum import Flag, auto

from cloudpathlib import AnyPath


class FileType(Flag):
    """
    Bitwise flags representing supported file formats.

    Using Flag allows for combining multiple file types using bitwise
    operators (e.g., FileType.CSV | FileType.JSON), which is useful
    for filtering or multi-format processing pipelines.

    Attributes
    ----------
    CSV : auto
        Comma-Separated Values format.
    JSON : auto
        JavaScript Object Notation format.
    JOBLIB : auto
        Joblib serialized Python objects (often used for ML models).
    PDF : auto
        Portable Document Format (used for report generation).
    EXCEL : auto
        Microsoft Excel spreadsheet format (.xlsx).
    PARQUET : auto
        Apache Parquet columnar storage format (highly optimized for large datasets).
    YAML : auto
        YAML format.
    """

    CSV = auto()
    JSON = auto()
    JOBLIB = auto()
    PDF = auto()
    EXCEL = auto()
    PARQUET = auto()
    YAML = auto()

    def get_extensions(self) -> list[str]:
        match self:
            case FileType.CSV:
                return ["csv", "txt"]
            case FileType.JSON:
                return ["json", "jsonl"]
            case FileType.JOBLIB:
                return ["joblib", "joblib.gz"]
            case FileType.PDF:
                return ["pdf"]
            case FileType.EXCEL:
                return ["xlsx", "xls", "xlsm", "xlsb"]
            case FileType.PARQUET:
                return ["parquet", "pq"]
            case FileType.YAML:
                return ["yaml", "yml"]
            case _:
                return []

    def _check_single_type(self, ext_lower: str) -> bool:
        """
        Verify if a lowercase extension matches a single FileType member.

        This is an internal helper that maps specific FileType flags to their
        supported file extensions, allowing for variations such as '.txt' for
        CSV or '.pq' for Parquet.

        Parameters
        ----------
        ext_lower : str
            The file extension to check, normalized to lowercase and
            stripped of leading dots.

        Returns
        -------
        bool
            True if the extension is a logical match for the current
            FileType member, False otherwise.
        """
        return ext_lower in self.get_extensions()

    def is_valid_extension(self, ext: str) -> bool:
        """
        Validate if an extension is compatible with the current FileType instance.

        This method supports both single flags and combined bitwise flags. It
        normalizes the input extension and checks it against all members
        represented in the current flag state.

        Parameters
        ----------
        ext : str
            The file extension or file name to validate (e.g., '.csv',
            'JSON', or 'data.joblib.gz').

        Returns
        -------
        bool
            True if the extension matches any of the formats included
            in the current FileType flag, False otherwise.

        Notes
        -----
        Leading dots are stripped and the string is converted to lowercase
        before validation to ensure situational flexibility.
        """
        ext_lower = ext.lower().lstrip(".")

        return any(
            member._check_single_type(ext_lower)
            for member in FileType
            if member in self and member != FileType(0)
        )

    def validate_extension(self, filepath: str | AnyPath) -> None:
        """
        Validate that a file's extension is compatible with the FileType.

        Parameters
        ----------
        filepath : str | Path
            The path to the file to validate.

        Raises
        ------
        ValueError
            If the file's extension does not match the current FileType flag.
        """
        if not self.is_valid_extension(AnyPath(filepath).suffix):
            raise ValueError(
                f"Invalid file extension for {self.name}. "
                f"Valid extensions are {self.get_extensions()}. "
                f"Path: {filepath}"
            )

    def preferred_extension(self) -> str:
        """
        Return the standard file extension for the current FileType.

        Returns
        -------
        str
            The lowercase extension including the leading dot (e.g., '.csv').
        """
        match self:
            case FileType.CSV:
                return ".csv"
            case FileType.JSON:
                return ".json"
            case FileType.JOBLIB:
                return ".joblib"
            case FileType.PDF:
                return ".pdf"
            case FileType.EXCEL:
                return ".xlsx"
            case FileType.PARQUET:
                return ".parquet"
            case FileType.YAML:
                return ".yaml"
            case _:
                return ""

    def format_filename(self, filename: str) -> str:
        """
        Ensure the filename has the preferred extension for this FileType.

        Parameters
        ----------
        filename : str
            The base filename or partial path.

        Returns
        -------
        str
            The filename with the preferred extension appended if missing.
        """
        ext = self.preferred_extension()
        if not filename.lower().endswith(ext):
            return f"{filename}{ext}"
        return filename
