"""PDF file handling operations."""

from __future__ import annotations
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, Union, List, Tuple, Callable
from dataclasses import dataclass
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.layout_engine import ConstrainedLayoutEngine
import matplotlib.font_manager as fm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import tempfile
from pypdf import PdfWriter, PdfReader
from pypdf.annotations import Link
from pypdf.generic import ArrayObject, FloatObject, NameObject
from PIL import ImageColor
import io


class PageOrientation(Enum):
    """Page orientation options for PDF layouts."""

    LANDSCAPE = auto()
    PORTRAIT = auto()


class PageSize(Enum):
    """Supported page sizes with layout defaults."""

    LETTER = auto()
    A4 = auto()

    def _portrait_dimensions(self) -> Tuple[float, float]:
        """Return portrait (width, height) in inches for this page size."""
        match self:
            case PageSize.LETTER:
                return 8.5, 11.0
            case PageSize.A4:
                return 8.27, 11.69

        raise NotImplementedError(f"Dimensions for page size {self.name} not implemented.")

    def width(self, orientation: PageOrientation) -> float:
        """Return page width in inches for the given orientation."""
        w, h = self._portrait_dimensions()
        match orientation:
            case PageOrientation.LANDSCAPE:
                return h
            case PageOrientation.PORTRAIT:
                return w

        raise NotImplementedError(f"Dimensions for orientation {orientation.name} not implemented.")

    def height(self, orientation: PageOrientation) -> float:
        """Return page height in inches for the given orientation."""
        w, h = self._portrait_dimensions()
        match orientation:
            case PageOrientation.LANDSCAPE:
                return w
            case PageOrientation.PORTRAIT:
                return h

        raise NotImplementedError(f"Dimensions for orientation {orientation.name} not implemented.")

    @property
    def line_height(self) -> float:
        """Default line height as a fraction of page height."""
        match self:
            case PageSize.LETTER:
                return 0.03
            case PageSize.A4:
                return 0.025

        raise NotImplementedError(f"Line height for page size {self.name} not implemented.")

    @property
    def row_height(self) -> float:
        """Default row height as a fraction of page height."""
        match self:
            case PageSize.LETTER:
                return 0.035
            case PageSize.A4:
                return 0.045

        raise NotImplementedError(f"Row height for page size {self.name} not implemented.")

    @property
    def margins(self) -> Tuple[float, float, float, float]:  # L, R, T, B
        """Default margins as (left, right, top, bottom) fractions."""
        match self:
            case PageSize.LETTER:
                return 0.07, 0.93, 0.90, 0.10
            case PageSize.A4:
                return 0.06, 0.94, 0.90, 0.10

        raise NotImplementedError(f"Default margins for page size {self.name} not implemented.")


@dataclass
class PageColors:
    """Color configuration for page title and page numbers."""

    page_num: str
    title: str


class PageConfiguration:
    """Layout settings for PDF page creation.

    Stores page size/orientation, margins, colors, and optional header/footer
    callbacks used by `PDFDocument` when creating pages.
    """

    def __init__(
        self,
        page_size: PageSize,
        orientation: PageOrientation,
        colors: PageColors,
        margins: Tuple[float, float, float, float],  # L, R, T, B
        line_height: Optional[float] = None,
        row_height: Optional[float] = None,
        header_func: Optional[Callable[[PDFDocument.Page, str, bool], None]] = None,
        footer_func: Optional[Callable[[PDFDocument.Page], None]] = None,
    ):
        """Initialize page configuration values.

        Args:
            page_size: Page size (e.g., Letter, A4).
            orientation: Page orientation (landscape or portrait).
            colors: Title and page number colors.
            margins: Margins as (left, right, top, bottom) fractions.
            line_height: Optional line height override (fraction of page height).
            row_height: Optional row height override (fraction of page height).
            header_func: Optional callback for header rendering.
            footer_func: Optional callback for footer rendering.
        """
        self.page_size = page_size
        self.orientation = orientation
        self.colors = colors
        self.margins = margins
        self.line_height = line_height if line_height is not None else self.page_size.line_height
        self.row_height = row_height if row_height is not None else self.page_size.row_height
        self.header_func = header_func
        self.footer_func = footer_func

    @property
    def left_margin(self) -> float:
        return self.margins[0]

    @property
    def right_margin(self) -> float:
        return self.margins[1]

    @property
    def top_margin(self) -> float:
        return self.margins[2]

    @property
    def bottom_margin(self) -> float:
        return self.margins[3]

    @property
    def content_width(self) -> float:
        return self.right_margin - self.left_margin

    @property
    def content_height(self) -> float:
        return self.top_margin - self.bottom_margin

    @property
    def page_dimensions(self) -> Tuple[float, float]:
        w = self.page_size.width(self.orientation)
        h = self.page_size.height(self.orientation)
        return w, h

    @property
    def content_dimensions(self) -> Tuple[float, float, float, float]:
        return (self.left_margin, self.bottom_margin, self.content_width, self.content_height)


class PDFDocument:
    """PDF document builder with optional table-of-contents support."""

    @dataclass
    class Page:
        """Container for a rendered page and metadata."""

        pdf_doc: PDFDocument
        fig: Figure
        layout_engine: ConstrainedLayoutEngine
        page_name: str
        include_header: bool = True
        include_footer: bool = True
        include_in_page_numbering: bool = True
        print_page_name: bool = True
        include_in_index: bool = True
        displayed_page_number: Optional[int] = None
        page_index: int = 0
        continuation_text: str = ""
        continuation_page_top_y: float = 1.0
        parent_page: Optional[PDFDocument.Page] = None
        toc_rect: Tuple[int, int, int, int] = (0, 0, 0, 0)

        @classmethod
        def renumber_pages(cls, pdf_doc: PDFDocument) -> None:
            """Assign page indices and displayed page numbers.

            Inserts TOC pages after `page_count_before_toc` and updates page
            numbering for both content and TOC pages.
            """
            displayed_page_num = 0
            page_index = 0

            for p in pdf_doc.pages:
                if page_index == pdf_doc.page_count_before_toc:
                    for toc_page in pdf_doc.toc_pages:
                        page_index += 1
                        toc_page.actual_page_number = page_index
                        displayed_page_num += 1
                        toc_page.displayed_page_number = displayed_page_num

                p.page_index = page_index

                if p.include_in_page_numbering:
                    displayed_page_num += 1
                    p.displayed_page_number = displayed_page_num

                page_index += 1

        @classmethod
        def generate_toc(
            cls,
            pages: List[PDFDocument.Page],
            start_index: int,
            entry_count: int,
        ) -> Tuple[List[PDFDocument.Page], int]:
            """Return TOC entries starting at `start_index`.

            Args:
                pages: All document pages.
                start_index: Index to begin scanning for entries.
                entry_count: Maximum number of entries to include.

            Returns:
                Tuple of (entries, next_start_index).
            """
            entries: List[PDFDocument.Page] = []
            i = start_index
            included_count = 0

            while included_count < entry_count:
                p = pages[i]
                i += 1
                if p.include_in_index:
                    entries.append(p)
                    included_count += 1

                if i >= len(pages):
                    break

            return entries, i

    @dataclass
    class TOCPage:
        """Container for a Table of Contents page and its entries."""

        fig: Figure
        entries: List[PDFDocument.Page]
        is_last_toc_page: bool
        actual_page_number: int = 0
        displayed_page_number: int = 0

    @property
    def page_configuration(self) -> PageConfiguration:
        return self._page_configuration

    @property
    def canvas(self) -> canvas.Canvas:
        return self._canvas

    @property
    def toc_temp_file_path(self) -> Path:
        return self._toc_temp_file_path

    @property
    def pages(self) -> List[PDFDocument.Page]:
        return self._pages

    @property
    def toc_pages(self) -> List[PDFDocument.TOCPage]:
        return self._toc_pages

    @property
    def page_count_before_toc(self) -> int:
        return self._page_count_before_toc

    @page_count_before_toc.setter
    def page_count_before_toc(self, val: int) -> None:
        self._page_count_before_toc = val

    def __init__(
        self,
        doc_title: str,
        page_configuration: PageConfiguration,
        page_count_before_toc: int = 0,
    ):
        """Create a PDF document with the given configuration.

        Args:
            doc_title: Title used for metadata and TOC labeling.
            page_configuration: Layout configuration for new pages.
            page_count_before_toc: Page count to keep before the TOC insertion.
        """
        self.doc_title = doc_title
        self._page_configuration = page_configuration
        self._page_count_before_toc = page_count_before_toc
        self._y_pos = page_configuration.top_margin
        self._pages: List[PDFDocument.Page] = []
        self._toc_first_page_top_y: float = 0.82
        self._toc_subsequent_page_top_y: float = 0.94
        self._toc_first_page_entry_count = int(
            (self._toc_first_page_top_y - page_configuration.bottom_margin)
            / page_configuration.line_height
        )
        self._toc_subsequent_page_entry_count = int(
            (self._toc_subsequent_page_top_y - page_configuration.bottom_margin)
            / page_configuration.line_height
        )
        self._toc_pages: List[PDFDocument.TOCPage] = []
        temp_dir = tempfile.gettempdir()
        self._toc_temp_file_path = Path(temp_dir) / "temp_toc.pdf"
        dimensions_inches = self._page_configuration.page_dimensions
        dimensions_points = (dimensions_inches[0] * 72, dimensions_inches[1] * 72)
        self._canvas = canvas.Canvas(str(self._toc_temp_file_path), pagesize=dimensions_points)

        # Register default 'sans-serif' and 'sans-serif bold' fonts in ReportLab
        font_path = fm.findfont(fm.FontProperties(family=["sans-serif"]))
        pdfmetrics.registerFont(font=TTFont(name="sans-serif", filename=font_path))
        font_path = fm.findfont(fm.FontProperties(family=["sans-serif"], weight="bold"))
        pdfmetrics.registerFont(font=TTFont(name="sans-serif-bold", filename=font_path))
        font_path = fm.findfont(fm.FontProperties(family=["monospace"]))
        pdfmetrics.registerFont(font=TTFont(name="monospace", filename=font_path))

    @property
    def content(self) -> List[Figure]:
        """Return the list of page figures in document order."""
        return [p.fig for p in self.pages]

    def create_new_page(
        self,
        page_name: str,
        include_header: bool = True,
        include_footer: bool = True,
        include_in_page_numbering: bool = True,
        print_page_name: bool = True,
        include_in_index: bool = True,
        parent_page: Optional[PDFDocument.Page] = None,
        is_toc_page: bool = False,
    ) -> PDFDocument.Page:
        """Create and register a new page with layout settings.

        Args:
            page_name: Display name for the page.
            include_header: Whether to render the header.
            include_footer: Whether to render the footer.
            include_in_page_numbering: Whether to include in page numbering.
            print_page_name: Whether the header should print the page name.
            include_in_index: Whether to include in the TOC.
            parent_page: Optional parent for continuation pages.
            is_toc_page: Whether this page is a TOC page (not appended to pages list).

        Returns:
            The created `PDFDocument.Page` instance.
        """
        pc = self._page_configuration
        fig = plt.figure(figsize=pc.page_dimensions)
        layout_engine = ConstrainedLayoutEngine(rect=pc.content_dimensions)
        fig.set_layout_engine(layout_engine)

        pdf_page = PDFDocument.Page(
            pdf_doc=self,
            fig=fig,
            layout_engine=layout_engine,
            page_name=page_name,
            include_header=include_header,
            include_footer=include_footer,
            include_in_page_numbering=include_in_page_numbering,
            print_page_name=print_page_name,
            include_in_index=include_in_index,
            parent_page=parent_page,
        )

        if not is_toc_page:
            self._pages.append(pdf_page)

        self._y_pos = pc.top_margin

        if parent_page is not None:
            actual_page_name = f"{page_name} {parent_page.continuation_text}"
        else:
            actual_page_name = page_name

        if include_header and pc.header_func is not None:
            pc.header_func(pdf_page, actual_page_name, print_page_name)

        if include_footer and pc.footer_func is not None:
            pc.footer_func(pdf_page)

        return pdf_page

    def create_continuation_page(self, page: PDFDocument.Page) -> PDFDocument.Page:
        """Create a continuation page that inherits settings from `page`."""
        return self.create_new_page(
            page_name=page.page_name,
            include_header=page.include_header,
            include_footer=page.include_footer,
            include_in_page_numbering=page.include_in_page_numbering,
            print_page_name=True,
            include_in_index=False,
            parent_page=page,
        )

    def _render_page_numbers(self) -> None:
        """Render page numbers onto all document and TOC pages."""
        pc = self._page_configuration
        y_pos = 0.93

        def render_page_number(
            fig: Figure, x: float, y: float, page_num: Optional[int], color: str
        ) -> None:
            fig.text(
                x,
                y,
                f"Page {page_num}",
                color=color,
                fontsize=9,
                weight="bold",
                ha="right",
                transform=fig.transFigure,
            )

        for p in self.pages:
            if p.include_in_page_numbering:
                render_page_number(
                    fig=p.fig,
                    x=pc.right_margin,
                    y=y_pos,
                    page_num=p.displayed_page_number,
                    color=pc.colors.page_num,
                )

        for p in self.toc_pages:
            render_page_number(
                fig=p.fig,
                x=pc.right_margin,
                y=y_pos,
                page_num=p.displayed_page_number,
                color=pc.colors.page_num,
            )

    def render_table_of_contents(self) -> None:
        """Build and render the table of contents pages.

        Creates TOC figures, draws entries, updates page numbering, and
        writes a temporary TOC PDF used later during `save`.
        """
        pc = self._page_configuration
        include_in_toc_count = sum(p.include_in_index for p in self.pages)
        included_in_toc_count = 0
        pages_start_index = 0
        self.toc_pages.clear()
        is_first_toc_page = True

        while included_in_toc_count < include_in_toc_count:
            pdf_page = self.create_new_page(
                page_name=f"Contents",
                print_page_name=not is_first_toc_page,
                include_in_index=False,
                is_toc_page=True,
            )

            entries, pages_last_index = PDFDocument.Page.generate_toc(
                self.pages,
                start_index=pages_start_index,
                entry_count=(
                    self._toc_first_page_entry_count
                    if is_first_toc_page
                    else self._toc_subsequent_page_entry_count
                ),
            )
            pages_start_index = pages_last_index + 1
            included_in_toc_count += len(entries)
            self.toc_pages.append(
                PDFDocument.TOCPage(
                    fig=pdf_page.fig,
                    entries=entries,
                    is_last_toc_page=(included_in_toc_count == included_in_toc_count),
                )
            )
            is_first_toc_page = False

        PDFDocument.Page.renumber_pages(self)
        self._render_page_numbers()
        c = self.canvas
        is_first_toc_page = True

        # Define layout parameters in points (ReportLab units)
        width, height = pc.page_dimensions
        page_width = width * 72
        page_height = height * 72
        line_height = pc.line_height * page_height

        # Margin conversion to points
        left_margin = 0.2 * page_width
        right_margin = 0.8 * page_width
        top_margin = pc.top_margin * page_height

        # Position mapping
        page_name_x = left_margin
        page_num_x = right_margin

        # Set up dot string
        c.setFont("monospace", 10)
        dot_width = c.stringWidth(".", "monospace", 10)
        available_width = page_num_x - page_name_x
        page_count_str = str(len(self.pages))
        page_num_buffer = 10 + ((len(page_count_str) - 1) * 5)
        max_dot_string_width = int(available_width - page_num_buffer)
        # dot_string = "." * int((available_width - page_num_buffer) / dot_width)
        dot_string_x = page_num_x - page_num_buffer
        vert_line_x_pos = page_name_x - 10

        # Color for Title
        title_color = ImageColor.getrgb(pc.colors.title)
        title_rl_color = tuple(c / 255.0 for c in title_color)

        for toc_page in self.toc_pages:
            # Render the Matplotlib Figure to an image buffer
            buf = io.BytesIO()
            toc_page.fig.savefig(buf, format="png", dpi=300)
            buf.seek(0)

            # Draw the Matplotlib image onto the ReportLab canvas
            img = ImageReader(buf)
            c.drawImage(img, 0, 0, width=page_width, height=page_height)
            plt.close(toc_page.fig)  # Clean up Matplotlib figure

            if is_first_toc_page:
                # Title
                c.setFillColorRGB(title_rl_color[0], title_rl_color[1], title_rl_color[2])
                c.setFont("sans-serif-bold", 18)
                title_y_pos = top_margin - 15
                title = "Table of Contents"
                title_x_pos = page_width / 2
                c.drawCentredString(title_x_pos, title_y_pos, title)
                title_width = c.stringWidth(title, "sans-serif-bold", 18)

                # Subtitle line
                c.setStrokeColorRGB(title_rl_color[0], title_rl_color[1], title_rl_color[2])
                c.setLineWidth(1)
                subtitle_line_y_pos = title_y_pos - 5
                left_x = title_x_pos - (title_width / 2)
                right_x = left_x + title_width
                c.line(left_x, subtitle_line_y_pos, right_x, subtitle_line_y_pos)

                # Starting vertical position (in points)
                y_pos = self._toc_first_page_top_y * page_height
                is_first_toc_page = False
            else:
                y_pos = self._toc_subsequent_page_top_y * page_height

            initial_y_pos = y_pos + line_height - 9

            for entry in toc_page.entries:
                page_name = entry.page_name
                page_num = entry.displayed_page_number

                # Fixed height for clickable link area (points)
                link_height = 14

                # Draw White Background Box for Name
                page_name_width = (
                    c.stringWidth(page_name, "sans-serif", 12) + 4
                )  # Add space after the page name

                # Draw Leader Dots
                c.setFont("monospace", 10)  # Monospace font for dots
                available_dot_width = int(max_dot_string_width - page_name_width)
                total_dot_width = int(available_dot_width / dot_width)
                dot_string = "." * total_dot_width
                c.drawRightString(dot_string_x, y_pos, dot_string)

                # Draw Page Name
                c.setFillColorRGB(0, 0, 1)
                c.setFont("sans-serif", 12)
                c.drawString(page_name_x, y_pos, page_name)

                # Draw Page Number
                c.setFillColorRGB(0, 0, 1)
                c.setFont("sans-serif-bold", 12)
                c.drawRightString(right_margin, y_pos, str(page_num))

                entry.toc_rect = (
                    int(page_name_x),
                    int(y_pos - 2),
                    int(page_num_x),
                    int(y_pos + link_height),
                )

                y_pos -= pc.line_height * page_height  # Move down for the next entry

            end_y_pos = initial_y_pos - (len(toc_page.entries) * line_height) + 8

            # Add a subtle vertical line on the left for design consistency
            c.setStrokeColorRGB(title_rl_color[0], title_rl_color[1], title_rl_color[2])
            c.setLineWidth(1)
            c.line(vert_line_x_pos, initial_y_pos, vert_line_x_pos, end_y_pos)
            c.showPage()
        c.save()

    def save(self, filepath: Path, filename: str, **kwargs: Any) -> Path:
        """Save the document to disk, merging TOC and content pages.

        Args:
            filepath: Target directory.
            filename: File name without extension.
            **kwargs: Additional options passed to `save_pdf`.

        Returns:
            Path to the final PDF file.
        """
        temp_dir = tempfile.gettempdir()
        temp_main_pdf_filepath = Path(temp_dir) / f"temp_main_{filename}"
        main_pdf_path = save_pdf(self.content, temp_main_pdf_filepath, filename, **kwargs)
        writer = PdfWriter()
        main_reader = PdfReader(main_pdf_path)

        if len(self.toc_pages) > 0:
            toc_reader = PdfReader(self.toc_temp_file_path)
        else:
            toc_reader = None

        for i in range(self.page_count_before_toc):
            writer.add_page(main_reader.pages[i])

        # Table of Contents
        if toc_reader is not None:
            toc_page_index = 0
            for page in toc_reader.pages:
                writer.add_page(page)
                toc_page = self.toc_pages[toc_page_index]

                for entry in toc_page.entries:
                    annotation = Link(
                        rect=entry.toc_rect,
                        target_page_index=entry.page_index,
                    )
                    writer.add_annotation(
                        page_number=toc_page.actual_page_number - 1, annotation=annotation
                    )

        # Remaining pages
        for i in range(2, len(main_reader.pages)):
            writer.add_page(main_reader.pages[i])

        # Write merged file
        full_path = _get_pdf_fullpath(filepath, filename)

        with open(full_path, "wb") as f:
            writer.write(f)

        main_pdf_path.unlink(missing_ok=True)
        self.toc_temp_file_path.unlink(missing_ok=True)

        return full_path


def _get_pdf_fullpath(
    filepath: Path,
    filename: str,
) -> Path:
    """Return the full .pdf path, ensuring the directory exists."""
    filepath.mkdir(parents=True, exist_ok=True)
    return filepath / f"{filename}.pdf"


def save_pdf(
    content: Union[str, List[str], List[Figure]],
    filepath: Path,
    filename: str,
    **kwargs: Any,
) -> Path:
    """
    Save text content to PDF file.

    Args:
        content: Text string or list of text strings to write
        filepath: Path to save the PDF file
        filename: Name of the file (without extension)
        **kwargs: Additional arguments for canvas creation
    """
    full_path = _get_pdf_fullpath(filepath, filename)

    # Handle Matplotlib Figures
    if isinstance(content, list) and len(content) > 0 and isinstance(content[0], Figure):
        with PdfPages(full_path) as pdf:
            for fig in content:
                pdf.savefig(fig)
                plt.close(fig)
        return full_path

    # Handle Text
    final_lines: List[str] = []
    if isinstance(content, str):
        final_lines = content.split("\n")
    elif isinstance(content, list):
        # This list comprehension acts as a type-safe filter
        final_lines = [str(x) for x in content if not isinstance(x, Figure)]

    page_size = kwargs.get("page_size", letter)
    margin = kwargs.get("margin", 50)
    title = kwargs.get("title", None)

    # Filter kwargs to avoid passing page_size/margin/title to canvas constructor
    canvas_kwargs = {k: v for k, v in kwargs.items() if k not in ["page_size", "margin", "title"]}
    c = canvas.Canvas(str(full_path), pagesize=page_size, **canvas_kwargs)

    if title:
        c.setTitle(title)

    y = page_size[1] - margin
    line_height = 14

    for line in final_lines:
        if y < margin:
            c.showPage()
            y = page_size[1] - margin

        c.drawString(margin, y, line)
        y -= line_height

    c.save()
    return full_path


def load_pdf(
    filepath: str | Path,
    **kwargs: Any,
) -> str:
    """
    Load text content from PDF file.

    Note: This is a placeholder implementation. Full PDF text extraction
    requires additional dependencies like PyPDF2 or pdfplumber.

    Args:
        filepath: Path to PDF file
        **kwargs: Additional arguments for PDF reader

    Returns:
        Extracted text from PDF

    Raises:
        NotImplementedError: Full PDF extraction requires additional dependencies
    """
    raise NotImplementedError(
        "PDF text extraction requires additional dependencies. "
        "Install 'pdfplumber' or 'PyPDF2' for this functionality."
    )
