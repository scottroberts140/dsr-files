import pytest
from dsr_files.enums import FileType  # Adjust import based on your actual path


class TestFileTypeValidation:

    @pytest.mark.parametrize(
        "extension, expected",
        [
            ("csv", True),
            (".csv", True),
            ("TXT", True),
            ("parquet", False),
            ("joblib.gz", False),
        ],
    )
    def test_single_type_csv(self, extension, expected):
        """Verify CSV logical matching."""
        # _check_single_type expects a lowercase, stripped string
        clean_ext = extension.lower().lstrip(".")
        assert FileType.CSV._check_single_type(clean_ext) is expected

    @pytest.mark.parametrize(
        "extension, expected",
        [
            ("joblib", True),
            (".joblib.gz", True),
            ("pdf", False),
        ],
    )
    def test_single_type_joblib(self, extension, expected):
        """Verify JOBLIB supports nested extensions."""
        clean_ext = extension.lower().lstrip(".")
        assert FileType.JOBLIB._check_single_type(clean_ext) is expected

    @pytest.mark.parametrize(
        "flag, extension, expected",
        [
            (FileType.CSV, ".csv", True),
            (FileType.CSV, "txt", True),
            (FileType.EXCEL, ".xlsx", True),
            (FileType.EXCEL, "XLSB", True),
            (FileType.PARQUET, ".pq", True),
            (FileType.JSON, "jsonl", True),
            (FileType.PDF, ".pdf", True),
        ],
    )
    def test_is_valid_extension_single_flags(self, flag, extension, expected):
        """Test public validation for individual flags."""
        assert flag.is_valid_extension(extension) is expected

    def test_is_valid_extension_combined_flags(self):
        """Verify bitwise combinations work for multi-format pipelines."""
        combined = FileType.CSV | FileType.JSON
        assert combined.is_valid_extension(".csv") is True
        assert combined.is_valid_extension("jsonl") is True
        assert combined.is_valid_extension(".parquet") is False

    def test_is_valid_extension_invalid_inputs(self):
        """Ensure non-supported extensions return False."""
        assert FileType.CSV.is_valid_extension(".exe") is False
        assert FileType.PARQUET.is_valid_extension("mp3") is False

    def test_empty_flag_returns_false(self):
        """Verify that an empty flag (0) does not validate any extension."""
        empty_flag = FileType(0)
        assert empty_flag.is_valid_extension(".csv") is False
