"""PDF file handling operations."""

from __future__ import annotations

import io
import tempfile
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from dsr_files.utils import validate_extension
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from matplotlib.layout_engine import ConstrainedLayoutEngine
from PIL import ImageColor
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class PageOrientation(Enum):
    """Enumeration for page orientation types."""

    LANDSCAPE = auto()
    PORTRAIT = auto()


class PageSize(Enum):
    """
    Standard page sizes and their associated physical dimensions.
    """

    LETTER = auto()
    A4 = auto()

    def _portrait_dimensions(self) -> Tuple[float, float]:
        match self:
            case PageSize.LETTER:
                return 8.5, 11.0
            case PageSize.A4:
                return 8.27, 11.69

        raise NotImplementedError(f"Dimensions for page size {self.name} not implemented.")

    def width(self, orientation: PageOrientation) -> float:
        """
        Return the page width based on orientation.

        Parameters
        ----------
        orientation : PageOrientation
            The orientation (Landscape or Portrait).

        Returns
        -------
        float
            The width in inches.
        """
        w, h = self._portrait_dimensions()
        match orientation:
            case PageOrientation.LANDSCAPE:
                return h
            case PageOrientation.PORTRAIT:
                return w

        raise NotImplementedError(f"Dimensions for orientation {orientation.name} not implemented.")

    def height(self, orientation: PageOrientation) -> float:
        """
        Return the page height based on orientation.

        Parameters
        ----------
        orientation : PageOrientation
            The orientation (Landscape or Portrait).

        Returns
        -------
        float
            The height in inches.
        """
        w, h = self._portrait_dimensions()
        match orientation:
            case PageOrientation.LANDSCAPE:
                return w
            case PageOrientation.PORTRAIT:
                return h

        raise NotImplementedError(f"Dimensions for orientation {orientation.name} not implemented.")

    @property
    def line_height(self) -> float:
        """
        Return the line height based on orientation.

        Returns
        -------
        float
            The line height as a percentage of the page height.
        """
        match self:
            case PageSize.LETTER:
                return 0.03
            case PageSize.A4:
                return 0.025

        raise NotImplementedError(f"Line height for page size {self.name} not implemented.")

    @property
    def row_height(self) -> float:
        """
        Return the row height based on orientation.

        Returns
        -------
        float
            The row height as a percentage of the page height.
        """
        match self:
            case PageSize.LETTER:
                return 0.035
            case PageSize.A4:
                return 0.045

        raise NotImplementedError(f"Row height for page size {self.name} not implemented.")

    @property
    def margins(self) -> Tuple[float, float, float, float]:  # L, R, T, B
        """
        Return the margins based on orientation.

        Returns
        -------
        tuple of float
            A tuple containing (left, right, top, bottom) margins as a percentage of the page width/height.
        """
        match self:
            case PageSize.LETTER:
                return 0.07, 0.93, 0.90, 0.10
            case PageSize.A4:
                return 0.06, 0.94, 0.90, 0.10

        raise NotImplementedError(f"Default margins for page size {self.name} not implemented.")


@dataclass
class PageColors:
    """
    Color configuration for PDF page elements.

    Attributes
    ----------
    page_num : str
        Hex color code or name for the page number text.
    title : str
        Hex color code or name for the page titles.
    """

    page_num: str
    title: str


class PageConfiguration:
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
        """
        Layout and styling settings for a PDF document.

        This class defines the physical dimensions, margins, and functional
        hooks used to render every page in the document consistently.

        Parameters
        ----------
        page_size : PageSize
            The physical dimensions (e.g., Letter, A4).
        orientation : PageOrientation
            The page layout (Landscape or Portrait).
        colors : PageColors
            Color theme for text elements.
        margins : Tuple[float, float, float, float]
            Page margins as decimal percentages of page size (Left, Right, Top, Bottom).
        line_height : Optional[float], default None
            Line height ratio; defaults to the page_size default if None.
        row_height : Optional[float], default None
            Row height ratio; defaults to the page_size default if None.
        header_func : Optional[Callable], default None
            Function to render headers: (Page, title_str, show_title_bool) -> None.
        footer_func : Optional[Callable], default None
            Function to render footers: (Page) -> None.
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
    """
    Orchestrates the creation of multi-page, interactive PDF reports.

    This class manages the generation of Matplotlib-based content pages,
    an automated Table of Contents with clickable links, and the final
    merging of document components.
    """

    @dataclass
    class Page:
        """
        Represents a single content page within the PDF document.

        Each page contains a Matplotlib figure and associated metadata for
        indexing, numbering, and rendering.

        Attributes
        ----------
        pdf_doc : PDFDocument
            The parent document instance.
        fig : Figure
            The Matplotlib figure associated with this page.
        layout_engine : ConstrainedLayoutEngine
            The layout manager for the figure's content.
        page_name : str
            The name/title of the page for the TOC and headers.
        include_header : bool, default True
            Whether to render the document header.
        include_footer : bool, default True
            Whether to render the document footer.
        include_in_page_numbering : bool, default True
            Whether this page counts toward the displayed page count.
        print_page_name : bool, default True
            Whether to explicitly print the page name in the header area.
        include_in_index : bool, default True
            Whether to include this page in the Table of Contents.
        displayed_page_number : Optional[int], default None
            The calculated page number shown on the final document.
        page_index : int, default 0
            The 0-based position of the page in the final merged PDF.
        continuation_text : str, default ""
            Text appended to titles for continued pages (e.g., "(Continued)").
        continuation_page_top_y : float, default 1.0
            The Y-coordinate for content start on continuation pages.
        parent_page : Optional[PDFDocument.Page], default None
            The original page object if this is a continuation page.
        toc_rect : Tuple[int, int, int, int], default (0, 0, 0, 0)
            Coordinates for the clickable link in the TOC (points).
        """

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
            """
            Recalculate page indices and displayed numbers across the document.

            This method accounts for TOC pages inserted between pre-TOC
            content and the main report body.

            Parameters
            ----------
            pdf_doc : PDFDocument
                The document instance containing pages to renumber.
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
            """
            Group pages into batches for rendering on TOC pages.

            Parameters
            ----------
            pages : List[PDFDocument.Page]
                The list of all document pages.
            start_index : int
                The index of the first page to consider for this TOC page.
            entry_count : int
                The maximum number of entries that fit on the current TOC page.

            Returns
            -------
            Tuple[List[PDFDocument.Page], int]
                A list of pages included in this TOC section and the index of
                the next page to be processed.
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
        """
        Metadata for a generated Table of Contents page.

        Attributes
        ----------
        fig : Figure
            The Matplotlib figure serving as the background for the TOC page.
        entries : List[PDFDocument.Page]
            The specific document pages indexed on this TOC page.
        is_last_toc_page : bool
            Indicator used for layout or numbering logic on the final TOC page.
        actual_page_number : int, default 0
            The physical 0-based index in the final PDF.
        displayed_page_number : int, default 0
            The human-readable page number shown in the footer/header.
        """

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
        """
        Initialize a new Matplotlib figure as a document page.

        Parameters
        ----------
        page_name : str
            The title of the page used in headers and the TOC.
        include_header : bool, default True
            Whether to render the document header.
        # ... (rest of params documented in NumPy style)

        Returns
        -------
        PDFDocument.Page
            The initialized page object.
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
        """
        Create a new page that continues the content of an existing page.

        This is used when content (like a large table) overflows the current page.
        The new page inherits the properties of the parent but is typically
        excluded from the Table of Contents to avoid redundancy.

        Parameters
        ----------
        page : PDFDocument.Page
            The parent page to be continued.

        Returns
        -------
        PDFDocument.Page
            A new page instance configured as a continuation.
        """
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
        """
        Iterate through all document and TOC pages to render page number text.

        This method applies the page number to the top-right margin of every
        page designated for numbering, using the colors defined in the
        document's PageConfiguration.
        """
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
        """
        Generate and render the interactive Table of Contents.

        This method performs several high-level operations:
        1. Calculates the number of TOC pages required based on the count of
        indexable content pages.
        2. Uses ReportLab to draw the TOC text, leader dots, and page numbers
        over a Matplotlib-generated background.
        3. Calculates the geometric rectangles for every TOC entry to enable
        clickable hyperlinks in the final PDF.
        4. Triggers the renumbering of all pages to ensure the TOC itself is
        accounted for in the document flow.
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

    def save(self, output_dir: Path, filename: str, **kwargs: Any) -> Path:
        """
        Compile and save the final interactive PDF document.

        This method merges the main content pages with the generated Table
        of Contents, injects clickable link annotations, and performs
        clean-up of temporary rendering files.

        Parameters
        ----------
        output_dir : Path
            The destination directory for the final PDF.
        filename : str
            The base name of the file (extension '.pdf' is added).
        **kwargs : Any
            Additional keyword arguments passed to the underlying `save_pdf`
            utility for main content rendering.

        Returns
        -------
        Path
            The full path to the successfully saved and merged PDF.
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
        full_path = _get_pdf_fullpath(output_dir, filename)

        with open(full_path, "wb") as f:
            writer.write(f)

        main_pdf_path.unlink(missing_ok=True)
        self.toc_temp_file_path.unlink(missing_ok=True)

        return full_path


def _get_pdf_fullpath(
    output_dir: Path,
    filename: str,
) -> Path:
    """
    Generate the full destination path and ensure the parent directory exists.

    Parameters
    ----------
    output_dir : Path
        The directory where the PDF should be stored.
    filename : str
        The base name of the file (extension '.pdf' is appended automatically).

    Returns
    -------
    Path
        The validated full path to the PDF file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{filename}.pdf"


def save_pdf(
    content: Union[str, List[str], List[Figure]],
    output_dir: Path,
    filename: str,
    **kwargs: Any,
) -> Path:
    """
    Save text or Matplotlib figures to a PDF file.

    This utility handles two primary modes:
    1. Direct rendering of Matplotlib Figures using `PdfPages`.
    2. Basic text rendering using a ReportLab canvas with simple
       pagination and title support.

    Parameters
    ----------
    content : Union[str, List[str], List[Figure]]
        The data to persist. Can be a raw string, a list of strings,
        or a list of Matplotlib Figure objects.
    output_dir : Path
        The destination directory.
    filename : str
        The base name of the file (without extension).
    **kwargs : Any
        Additional configuration for text rendering:
        - page_size : tuple, default letter (8.5x11 inches)
        - margin : int, default 50 points
        - title : str, optional document metadata title

    Returns
    -------
    Path
        The full path to the saved PDF file.
    """
    full_path = _get_pdf_fullpath(output_dir, filename)

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
