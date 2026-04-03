import os
from typing import Any, Callable, Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
from annotated_types import doc
from fpdf import data

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
# import os
# from typing import Any, Callable, Optional, Sequence
# from annotated_types import doc
# from fpdf import data
# import numpy as np
# import matplotlib.pyplot as plt

# # ReportLab imports
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.platypus import (
#     BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle,
#     Image, Spacer
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib.units import inch

# from reportlab.platypus import SimpleDocTemplate
# from reportlab.platypus import Paragraph
# from reportlab.lib.styles import ParagraphStyle
# from reportlab.lib import colors

# # Reuse the same blue as your table titles (or set your preferred blue)
# from reportlab.lib import colors
# from reportlab.platypus import Paragraph
# from reportlab.lib.styles import ParagraphStyle
# from reportlab.platypus import PageBreak
# from reportlab.platypus import CondPageBreak

# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle, Paragraph, KeepTogether
# from reportlab.lib.styles import ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.pdfbase.pdfmetrics import stringWidth
# from reportlab.lib import colors
# from reportlab.lib.units import inch

# Matlab title font size = 8.5
# default Helvetica 10pt is a bit larger, so we reduce the legend font size to fit better
LEGEND_FONT_SIZE = 7.65
LEGEND_BOX_RIGHT_OFFSET = 0.8
BORDER_AXES_PAD = 4.0

BLUE_BOLD_LEFT = ParagraphStyle(
    name="BlueBoldLeft",
    fontName="Helvetica-Bold",
    fontSize=11,
    textColor=colors.HexColor("#1f77b4"),
    alignment=0,     # left
    leading=13,
    spaceBefore=6,   # NEW: gap above this paragraph
    # spaceAfter=6
)

# from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

def make_table(
    data,
    col_widths=None,                 # relative weights for non-empty columns (ignored for empty cols)
    available_width_in=None,         # width in inches to fit the table into
    doc=None,                        # if provided, uses doc.width as available width
    border_color=colors.HexColor("#BFBFBF"),
    header_bg=colors.HexColor("#F2F2F2"),
    body_font=("Helvetica", 10),
    header_font=("Helvetica-Bold", 10),
    # Title options
    title=None,                      # string caption above the table (optional)
    title_font=("Helvetica-Bold", 11),
    title_color=colors.HexColor("#1f77b4"),
    title_space_after=4,             # space after the title in points
    keep_title_with_table=True       # return a KeepTogether flowable if title is provided
):
    """
    - Empty columns (all None/empty-string cells) are set to 10% of page width each.
    - If there are one or two columns, the first column width is set to 22.5% of the available width.
      For two columns, the second column takes the remaining width.
    - For 3+ columns, the total table width equals the available (page/text) width.
    """
    if not data:
        tbl = Table([[]])
        tbl.hAlign = "LEFT"
        return tbl

    # Determine available (target) width in points
    if doc is not None and available_width_in is None:
        avail_width = doc.width
    elif available_width_in is not None:
        avail_width = available_width_in * inch
    else:
        # Fallback if no width context is provided
        avail_width = 6.5 * inch

    # Optional title Paragraph (left-aligned, blue)
    title_flowable = None
    if title:
        title_style = ParagraphStyle(
            "TableTitle",
            fontName=title_font[0],
            fontSize=title_font[1],
            textColor=title_color,
            alignment=0,  # left
            leading=title_font[1] + 2,
            spaceAfter=title_space_after
        )
        title_flowable = Paragraph(title, title_style)

    ncols = len(data[0])

    # Special case: one or two columns -> first column is 22.5% of available width
    if ncols in (1, 2):
        first_w = 0.215 * avail_width
        if ncols == 1:
            computed_col_widths = [first_w]
        else:  # ncols == 2
            second_w = max(avail_width - first_w, 0.0)
            computed_col_widths = [first_w, second_w]
    else:
        # Helper to test if a value is "empty" for column-emptiness detection
        def _is_empty_cell(v):
            if v is None:
                return True
            if isinstance(v, str) and v.strip() == "":
                return True
            return False

        # Identify empty columns: all rows empty in that column
        empty_cols = []
        for j in range(ncols):
            col_empty = True
            for row in data:
                cell = row[j] if j < len(row) else None
                if not _is_empty_cell(cell):
                    col_empty = False
                    break
            if col_empty:
                empty_cols.append(j)

        # Widths array to fill
        computed_col_widths = [None] * ncols

        # Assign fixed width to empty columns (10% of page width each)
        empty_col_width = 0.10 * avail_width if empty_cols else 0.0
        fixed_empty_total = empty_col_width * len(empty_cols)

        # If too many empty columns to fit, scale them down so they sum to avail_width
        if fixed_empty_total > avail_width and len(empty_cols) > 0:
            empty_col_width = avail_width / float(len(empty_cols))
            fixed_empty_total = empty_col_width * len(empty_cols)

        for j in empty_cols:
            computed_col_widths[j] = empty_col_width

        # Remaining width for non-empty columns
        remaining_width = max(avail_width - fixed_empty_total, 0.0)
        non_empty_cols = [j for j in range(ncols) if j not in empty_cols]
        n_non_empty = len(non_empty_cols)

        if n_non_empty == 0:
            # All columns are empty: spread to fill full width
            if fixed_empty_total < avail_width and len(empty_cols) > 0:
                bump = (avail_width - fixed_empty_total) / float(len(empty_cols))
                for j in empty_cols:
                    computed_col_widths[j] += bump
        else:
            # If user provided col_widths as weights, apply them to non-empty columns only
            weights = None
            if col_widths is not None and len(col_widths) == ncols:
                weights = [col_widths[j] for j in non_empty_cols]
                total_w = float(sum(w for w in weights if w is not None))
                if total_w <= 0:
                    weights = None  # fall back to equal

            if n_non_empty == 1:
                computed_col_widths[non_empty_cols[0]] = remaining_width
            else:
                if weights is None:
                    share = remaining_width / float(n_non_empty)
                    for j in non_empty_cols:
                        computed_col_widths[j] = share
                else:
                    total_w = float(sum(weights))
                    for idx, j in enumerate(non_empty_cols):
                        w = weights[idx]
                        computed_col_widths[j] = (w / total_w) * remaining_width

        # Final safety for multi-column case: ensure widths are set and sum to avail_width
        if any(w is None for w in computed_col_widths):
            remaining = avail_width - sum(w for w in computed_col_widths if w is not None)
            missing = sum(1 for w in computed_col_widths if w is None)
            fill = (remaining / missing) if missing > 0 else 0.0
            computed_col_widths = [w if w is not None else fill for w in computed_col_widths]

        total_w = sum(computed_col_widths)
        if total_w != 0 and abs(total_w - avail_width) > 1e-6:
            scale = avail_width / total_w
            computed_col_widths = [w * scale for w in computed_col_widths]

    # Build the table
    tbl = Table(data, colWidths=computed_col_widths, repeatRows=1)

    ts = TableStyle([
        ("FONT", (0, 0), (-1, -1), body_font[0], body_font[1]),
        ("FONT", (0, 0), (-1, 0), header_font[0], header_font[1]),
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEABOVE", (0, 0), (-1, 0), 0.75, border_color),
        ("LINEBELOW", (0, 0), (-1, 0), 0.75, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, border_color),
        ("BOX", (0, 0), (-1, -1), 0.75, border_color),
    ])
    tbl.setStyle(ts)

    # Position table flush-left
    tbl.hAlign = "LEFT"

    # Return table with optional title
    if title_flowable and keep_title_with_table:
        return KeepTogether([title_flowable, tbl])
    elif title_flowable:
        return [title_flowable, tbl]
    else:
        return tbl

def make_on_page(header_title):
    def on_page(canvas, doc):
        canvas.saveState()

        # Use the current document’s page size and margins
        width, height = doc.pagesize

        # Header: horizontal rule
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1)
        canvas.line(
            doc.leftMargin,
            height - doc.topMargin - 0.25 * inch,
            width - doc.rightMargin,
            height - doc.topMargin - 0.25 * inch
        )

        # Header text (centered)
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(width / 2.0, height - doc.topMargin, header_title)

        # Footer: horizontal rule
        canvas.line(
            doc.leftMargin,
            doc.bottomMargin + 0.5 * inch,
            width - doc.rightMargin,
            doc.bottomMargin + 0.5 * inch
        )

        # Footer page number (centered)
        canvas.setFont("Helvetica", 9)
        page_str = f"Page {canvas.getPageNumber()}"
        canvas.drawCentredString(width / 2.0, doc.bottomMargin + 0.25 * inch, page_str)

        canvas.restoreState()
    return on_page

# Usage with SimpleDocTemplate
header_title = "My Report Title"
header_offset_from_top = 0.75 * inch  # where header text sits
line_drop = 0.25 * inch               # distance from header text to header rule
gap_below_line = 0.15 * inch          # desired blank space below the line before content starts

doc = SimpleDocTemplate(
    "report.pdf",
    pagesize=letter,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    # Top margin includes both the header line drop and the gap below it
    topMargin=header_offset_from_top + line_drop + gap_below_line,
    bottomMargin=0.75 * inch
)
        
def reportPEMS_HDOffcycleBins(
    setIdx: int,
    filename: str,
    vehData: list[dict[str, Any]],
    udp: list[dict[str, Any]],
    scalarData: list[dict[str, Any]],
    scalarBinData: list[dict[str, Any]],
    logData: list[dict[str, Any]],
    binData: list[Sequence[Any]],
    binData_avg: list[dict[str, Any]],
    # getData: Callable[[int, str], tuple[np.ndarray, dict]]
    )  -> str:
    """
    Python translation of reportPEMS_HDOffcycleBins(setIdx, filename, vehData, udp, binData).

    Parameters
    ----------
    setIdx : int
        Index of dataset.
    filename : str
        Desired report filename or 'defaultReport' to derive from vehData.
    vehData : list of dict
        Vehicle data structure analogous to MATLAB vehData, including:
        - 'filename', 'pathname', 'logData', 'data', 'scalarData',
          'scalarBinData', 'binData', etc.
    udp : list of dict
        Configuration labels analogous to MATLAB udp; e.g., udp[setIdx]['pems']
        contains label strings for time-series keys.
    binData : list of sequences
        Analogous to MATLAB cell array binData; treated as a list of columns.
        Each element (column) is an indexable sequence (list/tuple).
    getData : function
        Fetches time-series data: y, meta = getData(setIdx, label)
        - y: 1D numpy array of values
        - meta: dict with optional keys: 'units', 'ylabel', 'xlabel', 'title'

    Returns
    -------
    pdf_path : str
        Path to the generated PDF report.
    """
    # Determine filename
    # if isinstance(filename, str) and filename.lower() == "defaultreport":
    #     # Use vehData path and filename (minus extension)
    #     default_fn = vehData[setIdx]["filename"]
    #     folder, base_name = os.path.split(default_fn)
    #     base_name_no_ext, _ext = os.path.splitext(base_name)
    #     filename = base_name_no_ext

    # Full PDF path (place into vehData pathname)
    file_path = r"C:\Users\slee02\Matlab\RoadaC"
    pdf_path = os.path.join(file_path, f"{filename}.pdf")

    # Header title and model string
    oem = logData.get("oem", "")[0] # if isinstance(logData.get("oem", ""), (list, tuple)) and len(logData["oem"]) > 0 else ""
    model = logData.get("model", "")[0] # if isinstance(logData.get("model", ""), (list, tuple)) and len(logData["model"]) > 0 else ""
    my = logData.get("my", "")[0] # if isinstance(logData.get("my", ""), (list, tuple)) and len(logData["my"]) > 0 else ""

    header_title = f"NVFEL Laboratory:  PEMS Test Report:  {oem} {model} {my}"
    veh_model = f"{oem} {model} {my}"

    # Styles
    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_heading2 = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceBefore=6,
        spaceAfter=6,
        alignment=1  # center
    )
    style_small_center = ParagraphStyle(
        "SmallCenter",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        alignment=1
    )
    style_table_text = ParagraphStyle(
        "TableText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
    )

    # ReportLab doc with header/footer
    # doc = BaseDocTemplate(
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.25 * inch,
        bottomMargin=0.0 * inch
    )

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin + 0.5 * inch,  # leave space for footer
        doc.width,
        doc.height - 1.0 * inch,        # leave space top+header
        id="normal"
    )

    def on_page(canvas, _doc):
        # Header line and centered header title
        canvas.saveState()
        width, height = letter

        # Header: horizontal rule
        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, height - doc.topMargin - 0.25 * inch,
                    width - doc.rightMargin, height - doc.topMargin - 0.25 * inch)

        # Header text
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(width / 2.0, height - doc.topMargin, header_title)

        # Footer: horizontal rule above footer area
        canvas.line(doc.leftMargin, doc.bottomMargin + 0.5 * inch,
                    width - doc.rightMargin, doc.bottomMargin + 0.5 * inch)
        # Footer page number centered
        canvas.setFont("Helvetica", 9)
        page_str = f"Page {canvas.getPageNumber()}"
        canvas.drawCentredString(width / 2.0, doc.bottomMargin + 0.25 * inch, page_str)

        canvas.restoreState()

    # template = PageTemplate(id="ReportTemplate", frames=[frame], onPage=on_page)
    # doc.addPageTemplates([template])

    on_page_cb = make_on_page(header_title) # , header_offset_from_top=header_offset_from_top, line_drop=line_drop)
    story = []
    # ... add your flowables (Paragraphs, tables, etc.) ...
    # story.append(PageBreak())

    doc.build(story, onFirstPage=on_page_cb, onLaterPages=on_page_cb)

    # Helper to build the "basic info header table" (nested function equivalent)
    def header_table():
        data = [
            ["Date and Time", logData.get("dateTime", "")[0]],
            ["Vehicle Model", veh_model],
            ["Vehicle ID", logData.get("vehicleID", "")[0]],
            ["File Name", filename],
        ]
        return make_table(data, doc=doc) # width_in=7.0, center=False)

    # PAGE 1 - Test Information
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    pg1_tab1_data = [
        ["Date and Time", logData.get("dateTime", "")[0]],
        ["Vehicle Model", veh_model],
        ["Vehicle ID", logData.get("vehicleID", "")[0]],
        ["File Name", filename],
    ]
    story.append(make_table(pg1_tab1_data, doc=doc)) # width_in=7.0, center=False)

    # Vehicle and Cycle
    story.append(Paragraph("Vehicle and Cycle", BLUE_BOLD_LEFT))
    # Cycle Distance with units (assumes a units dict)
    dist_val = scalarData.get("Distance_Mile", "")[0]
    dist_unit = "miles" # get_unit(vehData, setIdx, "Distance_Mile")
    cycle_distance_str = f"{dist_val:10.2f} {dist_unit}" if isinstance(dist_val, (int, float)) else str(dist_val)

    test_cycle = logData.get("testCycle", "")[0]
    odo = logData.get("odo", "")[0]
    fuel = logData.get("fuel", "")[0]
    vin = logData.get("vin", "")[0]
    notes = logData.get("notes", "")[0]

    pg1_tab2_data = [
        ["Test Cycle", test_cycle, "       ", "Fuel", fuel],
        ["Cycle Distance", cycle_distance_str, "       ", "VIN", vin],
        ["Odometer", odo, "       ", "Notes", notes]
    ]
    story.append(make_table(pg1_tab2_data, doc=doc)) # width_in=7.0, center=False)

    # Test Cycle Mass Emissions
    story.append(Paragraph("Test Cycle Mass Emissions", BLUE_BOLD_LEFT))

    def scalar_with_unit(key):
        val = scalarData.get(key, "")[0]
        unit = "g/mile"  # get_unit(vehData, setIdx, key)
        val_str = f"{val:8.4f}" if isinstance(val, (int, float)) else str(val)
        return unit, val_str

    nox_unit, nox_val = scalar_with_unit("kNOx_Gms_Per_Mile")
    co_unit, co_val = scalar_with_unit("CO_Gms_Per_Mile")
    hc_unit, hc_val = scalar_with_unit("HC_Gms_Per_Mile")
    co2_unit, co2_val = scalar_with_unit("CO2_Gms_Per_Mile")

    pg1_tab3_data = [
        ["NOx", coerce_text(nox_unit), coerce_text(nox_val)],
        ["CO", coerce_text(co_unit), coerce_text(co_val)],
        ["HC", coerce_text(hc_unit), coerce_text(hc_val)],
        ["CO2", coerce_text(co2_unit), coerce_text(co2_val)],
    ]
    # Render table with 4 columns like in MATLAB (name, unit, value, filler)
    pg1_tab3_data_render = [
        ["NOx", "CO", "HC", "CO2"],
        [nox_unit, co_unit, hc_unit, co2_unit],
        [nox_val, co_val, hc_val, co2_val],
        # ["NOx", nox_unit, nox_val, ""],
        # ["CO", co_unit, co_val, ""],
        # ["HC", hc_unit, hc_val, ""],
        # ["CO2", co2_unit, co2_val, ""],
    ]
    story.append(make_table(pg1_tab3_data_render, doc=doc)) # width_in=7.0, center=False)

    # Particulate Emissions (placeholder table as in MATLAB)
    story.append(Paragraph("Particulate Emissions", BLUE_BOLD_LEFT))
    pg1_tab4_data = [
        ["Filter Number", "Pre-Weight", "Post-Weight", "Net Total Mass", "Total Mass/Dis"],
        ["(-)", "(mg)", "(mg)", "(mg)", "(gm/mile)"],
        [" ", " ", " ", " ", " "]
    ]
    story.append(make_table(pg1_tab4_data, doc=doc)) # width_in=7.0, center=False)

    # Fuel Economy
    story.append(Paragraph("Fuel Economy", BLUE_BOLD_LEFT))
    fe_val = scalarData.get("Fuel_Economy", "")[0]
    fe_unit = "mpg"  # get_unit(vehData, setIdx, "Fuel_Economy")
    fe_val_str = f"{fe_val:8.2f}" if isinstance(fe_val, (int, float)) else str(fe_val)
    pg1_tab5_data = [
        ["Fuel Economy"],
        [fe_unit],
        [fe_val_str]
    ]
    story.append(make_table(pg1_tab5_data, doc=doc)) # width_in=2.0

    # Off-Cycle Emissions - Intervals
    story.append(Paragraph("Off-Cycle Emissions - Intervals", BLUE_BOLD_LEFT))
    sb = scalarBinData
    pg1_tab6_data = [
        ["Total Intervals", "Valid Intervals", "Invalid Intervals", "Bin 1 Intervals", "Bin 2 Intervals"],
        [sb.get("Number_Intervals", "")[0], sb.get("NumValid_Intervals", "")[0], sb.get("NumInValid_Intervals", "")[0], sb.get("NumBin1_Intervals", "")[0], sb.get("NumBin2_Intervals", "")[0]]
    ]
    story.append(make_table(pg1_tab6_data, doc=doc)) # width_in=7.0, center=False)

    # Bin 1 NOx Emissions
    story.append(Paragraph("Bin 1 NOx Emissions", BLUE_BOLD_LEFT))
    bin1_nox_val = scalarBinData.get("NOxMassFlow_Bin1", "")[0]
    bin1_nox_unit = "g/hr"  # get_unit_scalar_bin(vehData, setIdx, "NOxMassFlow_Bin1")
    bin1_nox_val_str = f"{bin1_nox_val:8.4f}" if isinstance(bin1_nox_val, (int, float)) else str(bin1_nox_val)
    pg1_tab7_data = [
        ["NOx Bin 1"],
        [bin1_nox_unit],
        [bin1_nox_val_str]
    ]
    story.append(make_table(pg1_tab7_data, doc=doc)) # width_in=2.0

    # Bin 2 Emissions
    story.append(Paragraph("Bin 2 NOx Emissions", BLUE_BOLD_LEFT))
    bin2_nox_val = scalarBinData.get("NOxBrakeSpecific_Bin2", "")[0]
    bin2_nox_unit = "mg/hp-hr"  # get_unit_scalar_bin(vehData, setIdx, "NOxBrakeSpecific_Bin2")
    bin2_nox_val_str = f"{bin2_nox_val:8.4f}" if isinstance(bin2_nox_val, (int, float)) else str(bin2_nox_val)

    bin2_hc_val = scalarBinData.get("hcBrakeSpecific_Bin2", "")[0]
    bin2_hc_unit = "mg/hp-hr"  # get_unit_scalar_bin(vehData, setIdx, "hcBrakeSpecific_Bin2")
    bin2_hc_val_str = f"{bin2_hc_val:8.4f}" if isinstance(bin2_hc_val, (int, float)) else str(bin2_hc_val)

    bin2_co_val = scalarBinData.get("coBrakeSpecific_Bin2", "")[0]
    bin2_co_unit = "g/hp-hr"  # get_unit_scalar_bin(vehData, setIdx, "coBrakeSpecific_Bin2")
    bin2_co_val_str = f"{bin2_co_val:8.4f}" if isinstance(bin2_co_val, (int, float)) else str(bin2_co_val)

    pg1_tab8_render = [
        ["NOx Bin 2", "HC Bin 2", "PM Bin 2", "CO Bin 2"],
        [bin2_nox_unit, bin2_hc_unit, "--", bin2_co_unit],
        [bin2_nox_val_str, bin2_hc_val_str, "--", bin2_co_val_str]
    ]
    story.append(make_table(pg1_tab8_render, doc=doc)) # width_in=7.0, center=False)

    # Page Break and Figures
    story.append(PageBreak())
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    story.append(header_table())
    story.append(Paragraph("Figure:  Included Intervals", BLUE_BOLD_LEFT))
    include_image_path = _figure_included_intervals(setIdx, vehData, udp, logData)
    story.append(Image(include_image_path, width=7.5 * inch, height=7.75 * inch))

    # Invalid Intervals
    story.append(PageBreak())
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    story.append(header_table())
    story.append(Paragraph("Figure:  Invalid Intervals", BLUE_BOLD_LEFT))
    invalid_image_path = _figure_invalid_intervals(setIdx, vehData, udp, binData, logData, binData_avg)
    story.append(Image(invalid_image_path, width=7.5 * inch, height=8.0 * inch))

    # # Bin 1 NOx
    story.append(PageBreak())
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    story.append(header_table())
    story.append(Paragraph("Figure:  Bin 1 NOx", BLUE_BOLD_LEFT))
    bin1_nox_image_path = _figure_bin1_nox(setIdx, vehData, udp, binData, logData)
    story.append(Image(bin1_nox_image_path, width=7.5 * inch, height=8.0 * inch))

    # Normalized CO2
    story.append(PageBreak())
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    story.append(header_table())
    story.append(Paragraph("Figure:  Normalized CO2", BLUE_BOLD_LEFT))
    norm_co2_image_path = _figure_norm_co2(setIdx, vehData, udp, binData, logData, binData_avg)
    story.append(Image(norm_co2_image_path, width=7.5 * inch, height=8.0 * inch))

    # Bin 2 NOx
    story.append(PageBreak())
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    story.append(header_table())
    story.append(Paragraph("Figure:  Bin 2 NOx", BLUE_BOLD_LEFT))
    bin2_nox_image_path = _figure_bin2_nox(setIdx, vehData, udp, binData, logData)
    story.append(Image(bin2_nox_image_path, width=7.5 * inch, height=8.0 * inch))

    # Bin 2 CO
    story.append(PageBreak())
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    story.append(header_table())
    story.append(Paragraph("Figure:  Bin 2 CO", BLUE_BOLD_LEFT))
    bin2_co_image_path = _figure_bin2_co(setIdx, vehData, udp, binData, logData)
    story.append(Image(bin2_co_image_path, width=7.5 * inch, height=8.0 * inch))

    # Bin 2 HC
    story.append(PageBreak())
    story.append(Spacer(1, 0.25 * inch))  # 0.25" gap below the header
    story.append(Paragraph("Test Information", BLUE_BOLD_LEFT))
    story.append(header_table())
    story.append(Paragraph("Figure:  Bin 2 HC", BLUE_BOLD_LEFT))
    bin2_hc_image_path = _figure_bin2_hc(setIdx, vehData, udp, binData, logData, binData_avg)
    story.append(Image(bin2_hc_image_path, width=7.5 * inch, height=8.0 * inch))

    # Build the PDF
    doc.build(story)

    # Optionally, return path or open viewer
    # os.system(f'open "{pdf_path}"')  # macOS, adapt for Windows/Linux if desired

    return pdf_path


# ----------------------------- Helper functions and figure builders -----------------------------

def coerce_text(x: Any) -> str:
    return "" if x is None else str(x)


def get_unit(vehData: list[dict[str, Any]], setIdx: int, key: str) -> str:
    """
    Retrieve units for scalarData entries. Assumes vehData[setIdx]['scalarDataUnits'][key]
    or vehData[setIdx]['scalarData']['Units'][key] exists. Fallback to empty string.
    """
    # Try different places for units storage
    sd = vehData[setIdx].get("scalarData", {})
    sd_units = vehData[setIdx].get("scalarDataUnits", {})
    if isinstance(sd_units, dict) and key in sd_units:
        return str(sd_units[key])
    # else try embedded units dict
    units_dict = sd.get("Units", {})
    if isinstance(units_dict, dict) and key in units_dict:
        return str(units_dict[key])
    return ""


def get_unit_scalar_bin(vehData: list[dict[str, Any]], setIdx: int, key: str) -> str:
    """
    Retrieve units from scalarBinData. Assumes vehData[setIdx]['scalarBinDataUnits'][key]
    or embedded 'Units' dictionary exists.
    """
    sbd = vehData[setIdx].get("scalarBinData", {})
    sbd_units = vehData[setIdx].get("scalarBinDataUnits", {})
    if isinstance(sbd_units, dict) and key in sbd_units:
        return str(sbd_units[key])
    units_dict = sbd.get("Units", {})
    if isinstance(units_dict, dict) and key in units_dict:
        return str(units_dict[key])
    return ""


def _cell2mat_row(binData: list[Sequence[Any]], row_index: int) -> np.ndarray:
    """
    MATLAB-like cell2mat for binData(row, :) -> concatenate a row across columns.
    Expects binData to be a list of column sequences; returns a numpy array for the requested row.
    """
    vals = []
    for col in binData:
        if row_index < len(col):
            vals.append(col[row_index])
        else:
            vals.append(np.nan)
    return np.asarray(vals)

def legend_anchor_to_right_ylabel(
    ax,
    right_ax,
    handles,
    labels,
    legend_fontsize,
    gap_mult=6,
    adjust_axes=True,
    frameon=True,
    fancybox=False
):
    """
    Compute legend anchor point so the legend sits to the right of the right y-label,
    with a horizontal gap equal to gap_mult * (right y-label font size in points).
    The legend width is measured from the actual legend content. If the figure does
    not have enough space on the right, optionally shrink the axes width to make room.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Main axes (left y-axis).
    right_ax : matplotlib.axes.Axes
        Secondary y-axis (created via ax.twinx()).
    handles : list
        Legend handles (lines, patches, etc.).
    labels : list of str
        Legend labels.
    legend_fontsize : float or str
        Font size passed to legend(..., fontsize=...).
    gap_mult : float
        Multiplier of right y-label font size (in points) used as the horizontal gap.
        Default is 6.
    adjust_axes : bool
        If True, shrink the axes width to ensure the legend fits inside the figure.
    frameon : bool
        Temporary legend frame flag used for measuring (and typically for final legend).
    fancybox : bool
        Temporary legend fancybox flag used for measuring (and typically for final legend).

    Returns
    -------
    (x_fig, y_fig) : tuple of float
        Anchor point in figure coordinates for use in bbox_to_anchor with loc='upper left'.
    """
    fig0 = ax.figure

    # 1) Create a temporary legend to measure its true size
    temp_leg = ax.legend(
        handles=handles,
        labels=labels,
        loc="upper left",
        fontsize=legend_fontsize,
        frameon=frameon,
        fancybox=fancybox,
        borderaxespad=0.0,
    )
    fig0.canvas.draw()
    renderer = fig0.canvas.get_renderer()
    leg_bbox = temp_leg.get_window_extent(renderer=renderer)
    legend_width_px = leg_bbox.width
    # Remove temp legend (we will place the final one after computing anchor)
    temp_leg.remove()

    # 2) Measure right y-label position and axes top in display (pixel) coords
    label_bbox = right_ax.yaxis.label.get_window_extent(renderer=renderer)
    right_edge_px = label_bbox.x1
    ax_bbox = ax.get_window_extent(renderer=renderer)
    top_px = ax_bbox.y1

    # 3) Compute horizontal gap = gap_mult * (label font size in points)
    #    Convert points -> pixels using figure DPI (1 pt = 1/72 inch)
    label_fontsize_pt = right_ax.yaxis.label.get_size()
    gap_px = gap_mult * label_fontsize_pt * (fig0.dpi / 72.0)

    # 4) Ensure there is enough room in the figure to place the legend
    fig_right_px = fig0.bbox.x1
    current_space_px = fig_right_px - right_edge_px
    required_space_px = gap_px + legend_width_px

    if adjust_axes and current_space_px < required_space_px:
        # Shrink axes width in normalized figure coordinates to make room
        delta_px = (required_space_px - current_space_px)
        fig_width_px = (fig0.bbox.x1 - fig0.bbox.x0)
        delta_w_norm = max(0.0, delta_px / fig_width_px)

        pos = ax.get_position()
        new_width = max(0.05, pos.width - delta_w_norm)  # keep a minimal width
        ax.set_position([pos.x0, pos.y0, new_width, pos.height])
        # Keep the right twin axis aligned with the main axes
        try:
            right_ax.set_position(ax.get_position())
        except Exception:
            pass

        # Redraw and re-measure right y-label position (it can change after resizing)
        fig0.canvas.draw()
        label_bbox = right_ax.yaxis.label.get_window_extent(renderer=renderer)
        right_edge_px = label_bbox.x1
        ax_bbox = ax.get_window_extent(renderer=renderer)
        top_px = ax_bbox.y1

    # 5) Final anchor point: left edge of legend = right label right edge + gap
    x_px = right_edge_px + gap_px
    y_px = top_px
    x_fig, y_fig = fig0.transFigure.inverted().transform((x_px, y_px))
    return x_fig, y_fig

import matplotlib.pyplot as plt

def legend_right_of_right_ylabel(
    ax,
    ax_right,
    handles,
    labels,
    pad_points=6,
    min_axes_width=0.2,
    legend_fontsize=6,
):
    """
    Place a legend to the right of the right y-axis label with a gap of 'pad_points'
    (in points). Adjust only the axes width if needed so the legend remains inside
    the figure. Height is preserved.

    Returns the created legend.
    """
    fig = ax.figure
    # Ensure text extents are computed
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # Convert pad from points -> figure fraction
    fig_w_in = fig.get_size_inches()[0]
    pad_fig = pad_points / 72.0 / fig_w_in

    # Measure legend width in figure fraction (create a temp legend off-canvas)
    temp_leg = fig.legend(
        handles=handles,
        labels=labels,
        loc="upper left",
        bbox_to_anchor=(0, 0),
        frameon=True,
        prop={"size": legend_fontsize},
    )
    fig.canvas.draw()
    leg_bb_pix = temp_leg.get_window_extent(renderer=renderer)
    leg_width_fig = (leg_bb_pix.width / fig.dpi) / fig_w_in
    # Remove temp legend
    temp_leg.remove()

    # Current axes position (figure fraction)
    ax_pos = ax.get_position()

    # Measure right y-label bbox in figure fraction
    label_bb_disp = ax_right.yaxis.label.get_window_extent(renderer=renderer)
    label_bb_fig = label_bb_disp.transformed(fig.transFigure.inverted())

    # If legend would extend beyond the right edge, shrink only the width
    x_legend_right = label_bb_fig.x1 + pad_fig + leg_width_fig
    overflow = x_legend_right - 1.0
    if overflow > 0:
        # Reduce width by overflow (+ a small epsilon) but not below min_axes_width
        epsilon = 0.005
        new_width = max(min_axes_width, ax_pos.width - (overflow + epsilon))
        ax.set_position([ax_pos.x0, ax_pos.y0, new_width, ax_pos.height])
        fig.canvas.draw()
        ax_pos = ax.get_position()
        # Recompute label bbox after shrinking width
        label_bb_disp = ax_right.yaxis.label.get_window_extent(renderer=renderer)
        label_bb_fig = label_bb_disp.transformed(fig.transFigure.inverted())

    # Compute horizontal offset in axes coords so legend sits pad_points to the right of label
    delta_fig = (label_bb_fig.x1 - ax_pos.x1)  # label-right minus axes-right (in fig fraction)
    offset_axes = (delta_fig + pad_fig) / ax_pos.width

    # Place final legend in axes coordinates
    leg = ax.legend(
        handles=handles,
        labels=labels,
        loc="upper left",
        bbox_to_anchor=(1.0 + offset_axes, 1.0),
        bbox_transform=ax.transAxes,
        frameon=True,
        prop={"size": legend_fontsize},
    )
    return leg


def _figure_included_intervals(setIdx, vehData, udp, logData) -> str:
    # Prepare filenames
    img_path = "include_image.png"

    # Create figure
    fig, axes = plt.subplots(6, 1, figsize=(7.75, 7.75), sharex=True)
    line_wid = 1.5
    LEGEND_FONT_SIZE = 6.0  # legend font size

    # Time data
    x_data, x_meta = vehData['TIME'], "Time (s)"

    # 1) includeEngSpeed + engineSpeed (right axis)  [UNCHANGED WIDTH/HEIGHT]
    y_inc_es, inc_es_meta = vehData["Include_EngSpeed"], "Include Engine"
    axes[0].plot(x_data, y_inc_es, linewidth=line_wid, color=(0, 0, 1))
    axes[0].set_ylabel(inc_es_meta)

    ax0r = axes[0].twinx()
    y_eng_spd, eng_spd_meta = vehData["EngineRPM"], "Engine RPM"
    ax0r.plot(x_data, y_eng_spd, linewidth=1.5, color=(0.549, 0.337, 0.294))
    ax0r.set_ylabel(eng_spd_meta, color=(0.549, 0.337, 0.294))
    axes[0].grid(True, axis="y")

    # 2) includeRegen + regenStatus (right axis)  [UNCHANGED WIDTH/HEIGHT]
    y_inc_reg, inc_reg_meta = vehData["Include_Regen"], "Include Regen"
    axes[1].plot(x_data, y_inc_reg, linewidth=1.5, color=(0, 0, 1))
    axes[1].set_ylabel(inc_reg_meta)
    ax1r = axes[1].twinx()
    y_reg_stat, reg_stat_meta = vehData["DPFRegenStatus"], "Regen Status"
    ax1r.plot(x_data, y_reg_stat, linewidth=1.5, color='tab:brown')
    ax1r.set_ylabel(reg_stat_meta, color=(0.549, 0.337, 0.294))
    axes[1].grid(True, axis="y")

    # Lock subplot heights before legend placement so that only widths are adjusted for legends
    fig.canvas.draw()
    plt.tight_layout()  # do this once; do NOT call tight_layout again later

    # 3) includeTmax + tMaxLimit + ambientAirT  [ADJUST WIDTH ONLY]
    y_inc_tmax, inc_tmax_meta = vehData["Include_Tmax"], "Include TMax"
    line1, = axes[2].plot(x_data, y_inc_tmax, linewidth=1.5, color=(0, 0, 1))
    axes[2].set_ylabel(inc_tmax_meta)
    ax2r = axes[2].twinx()
    y_tmax_lim, tmax_lim_meta = vehData["TMax_ExcludeLimit"], "TMax Limit"
    line2, = ax2r.plot(x_data, y_tmax_lim, linewidth=1.5, color='tab:brown')
    ax2r.set_ylabel(tmax_lim_meta, color=(0.549, 0.337, 0.294))
    y_amb_t, amb_t_meta = vehData["LimitAdjustediSCB_LAT"], "LimitAdjustediSCB_LAT"
    line3, = ax2r.plot(x_data, y_amb_t, linewidth=1.5, color=(0.1608, 0.4784, 0.0431))

    # Adjust only width to place legend with 6-pt gap to the right of the right y-label
    pos0 = axes[2].get_position()  # remember original height
    leg = legend_right_of_right_ylabel(
        ax=axes[2],
        ax_right=ax2r,
        handles=[line1, line2, line3],
        labels=[inc_tmax_meta, tmax_lim_meta, amb_t_meta],
        pad_points=1,
        min_axes_width=0.2,
        legend_fontsize=LEGEND_FONT_SIZE,
    )
    for t in leg.get_texts():
        t.set_fontsize(LEGEND_FONT_SIZE)
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    # Restore original height (do not change height)
    pos1 = axes[2].get_position()
    axes[2].set_position([pos1.x0, pos0.y0, pos1.width, pos0.height])
    axes[2].grid(True, axis="y")

    # 4) includeAmbient5C + ambientTLimit + ambientAirT  [ADJUST WIDTH ONLY]
    y_inc_amb5, inc_amb5_meta = vehData["Include_Ambient5C"], "Include AmbT 5C"
    line4, = axes[3].plot(x_data, y_inc_amb5, linewidth=line_wid, color=(0, 0, 1))
    axes[3].set_ylabel(inc_amb5_meta)
    ax3r = axes[3].twinx()
    ax3r.set_ylabel(inc_amb5_meta, color='tab:brown')
    ax3r.tick_params(axis="y", color='tab:brown')

    y_amb_lim, amb_lim_meta = vehData["AmbientT_ExcludeLimit"], "AmbT Exclude Limit"
    line5, = ax3r.plot(x_data, y_amb_lim, linewidth=1.5, color='tab:brown')
    y_amb_t2, amb_t_meta2 = vehData["LimitAdjustediSCB_LAT"], "LimitAdjustediSCB_LAT"
    line6, = ax3r.plot(x_data, y_amb_t2, linewidth=1.5, color=(0.1608, 0.4784, 0.0431))

    pos0 = axes[3].get_position()
    leg = legend_right_of_right_ylabel(
        ax=axes[3],
        ax_right=ax3r,
        handles=[line4, line5, line6],
        labels=[inc_amb5_meta, amb_lim_meta, amb_t_meta2],
        pad_points=1,
        min_axes_width=0.2,
        legend_fontsize=LEGEND_FONT_SIZE,
    )
    for t in leg.get_texts():
        t.set_fontsize(LEGEND_FONT_SIZE)
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    pos1 = axes[3].get_position()
    axes[3].set_position([pos1.x0, pos0.y0, pos1.width, pos0.height])
    axes[3].grid(True, axis="y")

    # 5) includeAltitude + altitudeLimit + altitudeFt  [ADJUST WIDTH ONLY]
    y_inc_alt, inc_alt_meta = vehData["Include_Altitude"], "Include Altitude"
    line7, = axes[4].plot(x_data, y_inc_alt, linewidth=line_wid, color=(0, 0, 1))
    axes[4].set_ylabel(inc_alt_meta)
    ax4r = axes[4].twinx()
    y_alt_lim, alt_lim_meta = vehData["Altitude_ExcludeLimit"], "ALT Excl Limit"
    line8, = ax4r.plot(x_data, y_alt_lim, linewidth=1.5, color='tab:brown')
    ax4r.set_ylabel(alt_lim_meta, color='tab:brown')
    ax4r.tick_params(axis="y", colors=(0.549, 0.337, 0.294))
    y_alt_ft, alt_ft_meta = vehData["Altitude_Ft"], "Altitude (ft)"
    line9, = ax4r.plot(x_data, y_alt_ft, linewidth=1.5, color=(0.1608, 0.4784, 0.0431))

    pos0 = axes[4].get_position()
    leg = legend_right_of_right_ylabel(
        ax=axes[4],
        ax_right=ax4r,
        handles=[line7, line8, line9],
        labels=[inc_alt_meta, alt_lim_meta, alt_ft_meta],
        pad_points=1,
        min_axes_width=0.2,
        legend_fontsize=LEGEND_FONT_SIZE,
    )
    for t in leg.get_texts():
        t.set_fontsize(LEGEND_FONT_SIZE)
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    pos1 = axes[4].get_position()
    axes[4].set_position([pos1.x0, pos0.y0, pos1.width, pos0.height])
    axes[4].grid(True, axis="y")

    # 6) includeTotal  [UNCHANGED WIDTH/HEIGHT]
    y_inc_total, inc_total_meta = vehData["Include_Total"], "Include Total"
    axes[5].plot(x_data, y_inc_total, linewidth=line_wid, color=(0, 0, 1))
    axes[5].set_xlabel(x_meta)
    axes[5].set_ylabel(inc_total_meta)

    # Do NOT call tight_layout again; keep heights unchanged
    plt.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path

def _figure_invalid_intervals(setIdx, vehData, udp, binData, logData, binData_avg) -> str:
    img_path = "incTotal_image.png"

    fig, axes = plt.subplots(2, 1, figsize=(7.5, 8.0), sharex=False)
    line_wid = 3

    x_data, x_meta = vehData['TIME'], "Time (s)" # getData(setIdx, udp[setIdx]["pems"]["time"])
    y_inc_total, inc_total_meta = vehData["Include_Total"], "Include Total" # getData(setIdx, udp[setIdx]["pems"]["Include_Total"])

    axes[0].plot(x_data, y_inc_total, linewidth=line_wid, color=(0, 0, 1))
    axes[0].set_ylabel(inc_total_meta)

    # binData(3,:) for x, binData(5,:) for y (invalid intervals)
    x1data, x_meta = binData_avg['Time_BinAvg'], "Time (s)" #, 2)  # MATLAB is 1-based; row 3 => index 2
    y1data, y1_meta = binData_avg['Invalid_Intervals'], "Invalid Intervals" #, 4)  # MATLAB is 1-based; row 5 => index 4
    # y1data = _cell2mat_row(binData, 4)  # row 5 => index 4
    axes[1].plot(x1data, y1data, color=(0, 0, 0))
    axes[1].set_ylabel(y1_meta)
    axes[1].set_xlabel(x_meta)

    plt.tight_layout()
    plt.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path


def _figure_bin1_nox(setIdx, vehData, udp, binData, logData) -> str:
    img_path = "bin1Nox_image.png"
    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.0), sharex=True)

    # x = vehData[setIdx]["data"][time_key]
    x, x_meta = vehData['TIME'], "Time (s)" # getData(setIdx, udp[setIdx]["pems"]["time"])

    veh_speed = vehData['VehicleSpeedMPH']
    eng_spd = vehData["EngineRPM"] # getData(setIdx, udp[setIdx]["pems"]["EngineRPM"])

    # Top: speed + engine speed (right axis)
    axes[0].plot(x, veh_speed, color=(0, 0, 1))
    axes[0].set_ylabel("Vehicle Speed (mph)")
    ax0r = axes[0].twinx()
    ax0r.plot(x, eng_spd, color=(0.549, 0.337, 0.294)) # color='tab:brown'
    ax0r.set_ylabel("Engine Speed (rpm)", color=(0.549, 0.337, 0.294)) # color='tab:brown'
    axes[0].grid(True)

    # kNOx mass flow
    y_k, yk_meta = vehData["kNOx_MassFlow"], "kNOx Mass Flow (g/hr)" # getData(setIdx, udp[setIdx]["pems"]["kNOxMassFlow"])
    axes[1].plot(x, y_k, color=(0.1, 0.2, 0.6))
    axes[1].set_ylabel(yk_meta)
    axes[1].grid(True)

    # NOx Mass Bin 1 + NOxMassFlow_Bin1_Cummulative (right axis)
    t_binavg = binData["Time_BinAvg"].astype(float)  # binData(3,:) for x-axis; ensure it's numeric
    nox_bin1 = binData["NOx_Mass_Bin1"].astype(float)  # binData(5,:) for y-axis; ensure it's numeric
    axes[2].plot(t_binavg, nox_bin1, color=(0.2, 0.4, 0.7))
    axes[2].set_ylabel("NOx_Mass_Bin1  (gm)")
    axes[2].grid(True)

    ax2r = axes[2].twinx()
    nox_bin1_cum = binData["NOxMassFlow_Bin1_Cummulative"].astype(float)  # binData(6,:) for cumulative; ensure it's numeric
    ax2r.plot(t_binavg, nox_bin1_cum, color=(0.5, 0.2, 0.2))
    ax2r.set_ylabel("NOxMassFlow_Bin1_Cummulative (gm/hr)", color=(0.5, 0.2, 0.2))
    axes[2].set_xlabel(x_meta)

    plt.tight_layout()
    plt.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path


def _figure_norm_co2(setIdx, vehData, udp, binData, logData, binData_avg) -> str:
    img_path = "normCO2_image.png"
    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.0), sharex=True)

    x, x_meta = vehData['TIME'], "Time (s)" # getData(setIdx, udp[setIdx]["pems"]["time"])
    veh_speed = vehData['VehicleSpeedMPH']
    eng_spd = vehData["EngineRPM"] # getData(setIdx, udp[setIdx]["pems"]["EngineRPM"])

    # Top: engine speed (right axis) and speed (left)
    ax0r = axes[0].twinx()
    ax0r.plot(x, eng_spd, color=(0.549, 0.337, 0.294))
    ax0r.set_ylabel("Engine Speed (rpm)", color=(0.549, 0.337, 0.294))
    axes[0].plot(x, veh_speed, color=(0, 0, 1))
    axes[0].set_ylabel("Vehicle Speed (mph)")
    axes[0].grid(True)

    # CO2 mass flow
    y_co2, y_co2_meta = vehData["CO2_MassFlow"], "CO2 Mass Flow (g/hr)"
    axes[1].plot(x, y_co2, color=(0.2, 0.3, 0.6))
    axes[1].set_ylabel(y_co2_meta)
    axes[1].grid(True)

    # Normalized CO2 (%) and Bin Number (right axis)
    # binData(3,:) avg interval time; binData(8,:) CO2 norm; binData(9,:) bins
    x1 = binData_avg['Time_BinAvg'] # _cell2mat_row(binData, 2)  # row 3
    x2, mCO2_Norm_meta = binData_avg['mCO2_Norm'], "Normalized CO2 (%)" # _cell2mat_row(binData, 7)  # row 8
    line7, = axes[2].plot(x1, x2, color=(0.4941, 0.1843, 0.5569))
    axes[2].set_ylim(0, 80)

    # 6% CO2 norm limit across cycle start/end indices (binData(2,:))
    cycle_idx = binData_avg['Time_BinAvg'] # _cell2mat_row(binData, 1)  # row 2
    cycle_idx = cycle_idx[~np.isnan(cycle_idx)]
    if cycle_idx.size > 0:
        min_idx = int(np.min(cycle_idx))
        max_idx = int(np.max(cycle_idx))
        time_series = binData_avg['Time_BinAvg'] # vehData[setIdx]["data"][time_key]
        time_min = min_idx # if min_idx < len(time_series) else time_series[0]
        time_max = max_idx # if max_idx < len(time_series) else time_series[-1]
        line8, = axes[2].plot([time_min, time_max], [6, 6],
                     color=(0.8510, 0.3255, 0.0980), linewidth=2)

    axes[2].set_ylabel(mCO2_Norm_meta)
    axes[2].set_xlabel("Time (s)")

    # Bin Number (right axis)
    ax2r = axes[2].twinx()
    xx1 = binData_avg['Time_BinAvg'] # _cell2mat_row(binData, 2)  # row 3
    xx2, bin_num_meta = binData_avg['BIN'], "Bin Number" # _cell2mat_row(binData, 8)  # row 9
    line9, = ax2r.plot(xx1, xx2, color=(0.4667, 0.6745, 0.1882))
    ax2r.set_ylim(-10, 4)
    ax2r.set_ylabel("Bin Number", color=(0.549, 0.337, 0.294))
        # bbox_to_anchor=(1.02, 1.0), # place just outside the right edge of the axes

    leg = axes[2].legend(
        handles=[line7, line8, line9],
        labels=[mCO2_Norm_meta, '6% BIN 1 Limit', bin_num_meta],
        loc="upper right",           # anchor the legend's upper-left corner
        borderaxespad=0.0,
        fontsize=LEGEND_FONT_SIZE,
        frameon=True,
        fancybox=False,
    )
    
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path


def _figure_bin2_nox(setIdx, vehData, udp, binData, logData) -> str:
    img_path = "bin2NOx_image.png"
    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.0), sharex=True)

    x, x_meta = vehData['TIME'], "Time (s)" # getData(setIdx, udp[setIdx]["pems"]["time"])
    veh_speed = vehData['VehicleSpeedMPH']
    eng_spd = vehData["EngineRPM"] # getData(setIdx, udp[setIdx]["pems"]["EngineRPM"])

    # Top: speed + engine speed (right axis)
    axes[0].plot(x, veh_speed, color=(0, 0, 1))
    axes[0].set_ylabel("Vehicle Speed (mph)")
    ax0r = axes[0].twinx()
    ax0r.plot(x, eng_spd, color=(0.549, 0.337, 0.294))
    ax0r.set_ylabel("Engine Speed (rpm)", color=(0.549, 0.337, 0.294))
    axes[0].grid(True)

    # kNOx mass flow
    y_k, yk_meta =vehData["kNOx_MassFlow"], "kNOx Mass Flow (g/hr)" # getData(setIdx, udp[setIdx]["pems"]["kNOxMassFlow"])
    axes[1].plot(x, y_k, color=(0.1, 0.2, 0.6))
    axes[1].set_ylabel(yk_meta)
    axes[1].grid(True)

    # NOx Mass Bin 2 + NOx_BrakeSpec_Bin2_Cummulative (right axis)
    t_binavg = binData["Time_BinAvg"]
    nox_bin2, yk_meta = binData["NOx_Mass_Bin2"], "NOx Mass Bin 2 (gm)"
    axes[2].plot(t_binavg, nox_bin2, color=(0.2, 0.4, 0.7))
    axes[2].set_ylabel("NOx_Mass_Bin2  (gm)")
    axes[2].grid(True)

    ax2r = axes[2].twinx()
    nox_b2_cum, yk_meta = binData["NOx_BrakeSpec_Bin2_Cummulative"], "NOx_BS_Bin2_Cumm (gm/hp*hr)"
    ax2r.plot(t_binavg, nox_b2_cum, color=(0.5, 0.2, 0.2))
    ax2r.set_ylabel(yk_meta, color=(0.5, 0.2, 0.2))
    axes[2].set_xlabel(x_meta)

    plt.tight_layout()
    plt.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path


def _figure_bin2_co(setIdx, vehData, udp, binData, logData) -> str:
    img_path = "bin2CO_image.png"
    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.0), sharex=True)

    x, x_meta = vehData['TIME'], "Time (s)" # getData(setIdx, udp[setIdx]["pems"]["time"])
    veh_speed = vehData['VehicleSpeedMPH']
    eng_spd = vehData["EngineRPM"] # getData(setIdx, udp[setIdx]["pems"]["EngineRPM"])

    # Top: speed + engine speed (right axis)
    axes[0].plot(x, veh_speed, color=(0, 0, 1))
    axes[0].set_ylabel("Vehicle Speed (mph)")
    ax0r = axes[0].twinx()
    ax0r.plot(x, eng_spd, color=(0.549, 0.337, 0.294))
    ax0r.set_ylabel("Engine Speed (rpm)", color=(0.549, 0.337, 0.294))
    axes[0].grid(True)

    # CO mass flow
    y_co, yco_meta = vehData["CO_MassFlow"], "CO Mass Flow (g/hr)"
    axes[1].plot(x, y_co, color=(0.1, 0.2, 0.6))
    axes[1].set_ylabel(yco_meta)
    axes[1].grid(True)

    # CO Mass Bin 2 + CO_BrakeSpec_Bin2_Cummulative (right axis)
    t_binavg = binData["Time_BinAvg"]
    co_bin2 = binData["CO_Mass_Bin2"]
    axes[2].plot(t_binavg, co_bin2, color=(0.2, 0.4, 0.7))
    axes[2].set_ylabel("CO_Mass_Bin2  (gm)")
    axes[2].grid(True)

    ax2r = axes[2].twinx()
    co_b2_cum = binData["CO_BrakeSpec_Bin2_Cummulative"]
    ax2r.plot(t_binavg, co_b2_cum, color=(0.5, 0.2, 0.2))
    ax2r.set_ylabel("CO_BS_Bin2_Cumm (gm/hp*hr)", color=(0.549, 0.337, 0.294))
    ax2r.set_xlabel(yco_meta, color=(0.549, 0.337, 0.294))
    axes[2].set_xlabel(x_meta)
    
    plt.tight_layout()
    plt.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path


def _figure_bin2_hc(setIdx, vehData, udp, binData, logData, binData_avg) -> str:
    img_path = "bin2HC_image.png"
    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.0), sharex=True)

    x, x_meta = vehData['TIME'], "Time (s)" # getData(setIdx, udp[setIdx]["pems"]["time"])
    veh_speed = vehData['VehicleSpeedMPH']
    eng_spd = vehData["EngineRPM"] # getData(setIdx, udp[setIdx]["pems"]["EngineRPM"])

    # Top: speed + engine speed (right axis)
    axes[0].plot(x, veh_speed, color=(0, 0, 1))
    axes[0].set_ylabel("Vehicle Speed (mph)")
    ax0r = axes[0].twinx()
    ax0r.plot(x, eng_spd, color=(0.549, 0.337, 0.294))
    ax0r.set_ylabel("Engine Speed (rpm)", color=(0.549, 0.337, 0.294))
    axes[0].grid(True)

    # HC mass flow
    y_hc, yhc_meta = vehData["HC_MassFlow"], "HC Mass Flow (g/hr)"
    axes[1].plot(x, y_hc, color=(0.1, 0.2, 0.6))
    axes[1].set_ylabel(yhc_meta)
    axes[1].grid(True)

    # HC Mass Bin 2 + HC_BrakeSpec_Bin2_Cummulative (right axis)
    t_binavg = binData["Time_BinAvg"]
    hc_bin2, yhc_meta = binData["HC_Mass_Bin2"], "HC Mass Bin 2 (gm)"
    axes[2].plot(t_binavg, hc_bin2, color=(0.2, 0.4, 0.7))
    axes[2].set_ylabel("HC_Mass_Bin2  (gm)")
    axes[2].grid(True)

    ax2r = axes[2].twinx()
    hc_b2_cum = binData["HC_BrakeSpec_Bin2_Cummulative"]
    ax2r.plot(t_binavg, hc_b2_cum, color=(0.5, 0.2, 0.2))
    ax2r.set_ylabel("HC_BS_Bin2_Cumm (mg/hp*hr)", color=(0.549, 0.337, 0.294))

    axes[2].set_xlabel(x_meta)
    
    plt.tight_layout()
    plt.savefig(img_path, dpi=150)
    plt.close(fig)
    return img_path