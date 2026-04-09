"""Tests for PDF handler."""

import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

# Skip tests if PDF dependencies are not installed
pytest.importorskip("reportlab")
pytest.importorskip("pypdf")
pytest.importorskip("matplotlib")
pytest.importorskip("PIL")

from dsr_files import pdf_handler
from dsr_files.pdf_handler import (
    PageColors,
    PageConfiguration,
    PageOrientation,
    PageSize,
    PDFDocument,
)


@pytest.fixture
def page_config() -> PageConfiguration:
    """Fixture for standard document configuration."""
    colors = PageColors(page_num="#000000", title="#444444")
    return PageConfiguration(
        page_size=PageSize.LETTER,
        orientation=PageOrientation.PORTRAIT,
        colors=colors,
        margins=(0.07, 0.93, 0.90, 0.10),
    )


def test_page_size_dimensions() -> None:
    """Verify PageSize conversion logic for different orientations."""
    letter = PageSize.LETTER
    # Portrait: 8.5 x 11
    assert letter.width(PageOrientation.PORTRAIT) == 8.5
    assert letter.height(PageOrientation.PORTRAIT) == 11.0

    # Landscape: 11 x 8.5
    assert letter.width(PageOrientation.LANDSCAPE) == 11.0
    assert letter.height(PageOrientation.LANDSCAPE) == 8.5


def test_pdf_document_page_creation(page_config: PageConfiguration) -> None:
    """Verify that PDFDocument correctly tracks new pages."""
    doc = PDFDocument("Audit Report", page_config)
    doc.create_new_page("Summary")
    doc.create_new_page("Data Table")

    assert len(doc.pages) == 2
    assert doc.pages[0].page_name == "Summary"
    assert isinstance(doc.pages[0].fig, Figure)


def test_pdf_document_full_save(page_config: PageConfiguration) -> None:
    """Verify the full interactive save process including TOC."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        doc = PDFDocument("Interactive Audit", page_config)

        # Create enough pages to trigger numbering and TOC
        doc.create_new_page("Page 1")
        doc.create_new_page("Page 2")

        doc.render_table_of_contents()
        save_path = doc.save(output_dir, "interactive_audit")

        assert save_path.exists()
        # Check that temp files were cleaned up
        assert not doc.toc_temp_file_path.exists()


def test_save_pdf_text() -> None:
    """Test saving simple text to PDF."""
    content = ["Line 1", "Line 2"]
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        filepath = pdf_handler.save_pdf(content, output_dir, "test_doc")

        assert filepath.exists()
        assert filepath.name == "test_doc.pdf"


def test_load_pdf_raises_not_implemented() -> None:
    """Test that load_pdf raises NotImplementedError as expected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir) / "test.pdf"
        p.touch()

        with pytest.raises(NotImplementedError, match="requires additional dependencies"):
            pdf_handler.load_pdf(p)
