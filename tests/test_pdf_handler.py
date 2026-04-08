"""Tests for PDF handler."""

import pytest
from pathlib import Path
import tempfile

# Skip tests if PDF dependencies are not installed
pytest.importorskip("reportlab")
pytest.importorskip("pypdf")
pytest.importorskip("matplotlib")
pytest.importorskip("PIL")

from dsr_files import pdf_handler


def test_save_pdf_text() -> None:
    """Test saving simple text to PDF."""
    content = ["Line 1", "Line 2"]
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        filepath = pdf_handler.save_pdf(content, output_dir, "test_doc")

        assert filepath.exists()
        assert filepath.name == "test_doc.pdf"
        assert filepath.stat().st_size > 0


def test_load_pdf_raises_not_implemented() -> None:
    """Test that load_pdf raises NotImplementedError as expected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy file to pass existence check if it were implemented
        p = Path(tmpdir) / "test.pdf"
        p.touch()

        with pytest.raises(NotImplementedError, match="requires additional dependencies"):
            pdf_handler.load_pdf(p)
