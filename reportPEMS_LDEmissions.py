import os
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

from fpdf import FPDF


# ----------------------------- Main API -----------------------------

def reportPEMS_LDEmissions(setIdx: int,
                             filename: str,
                             vehData: List[Dict[str, Any]],
                             udp: List[Dict[str, Any]]) -> None:
    """
    FPDF-based implementation of reportPEMS_LDEmissions (MATLAB).
    - setIdx: zero-based dataset index
    - filename: PDF file name ('.pdf' added if missing)
    - vehData[setIdx]: dict with keys:
        data (pandas.DataFrame),
        units (dict: column name -> unit string),
        scalarData (dict of scalars),
        scalarUnits (dict of units for scalars),
        logData (dict of metadata),
        figtitle1 (optional, plot title string)
      optional:
        scalarBinData, binData (if you also calculate bins, not used here)
    - udp[setIdx]: dict with keys:
        pems (dict of column names),
        fuel (dict: nhv, cwf, sg),
        import (dict: missingData, endValues),
        log (dict: kh, dataType, ftpNormCalc(bool), pm2Active(bool), enableAnalog(bool),
             filterPosition, filter2ID, filter2WtPre, filter2WtPost,
             pmTaipipeMass, pmTailpipeDistanceSpec)
    """
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"

    pems = udp[setIdx]["pems"]
    df: pd.DataFrame = vehData[setIdx]["data"]
    units_map: Dict[str, str] = vehData[setIdx].get("units", {})
    scalar_data: Dict[str, Any] = vehData[setIdx].get("scalarData", {})
    scalar_units: Dict[str, str] = vehData[setIdx].get("scalarUnits", {})
    log_data: Dict[str, Any] = vehData[setIdx].get("logData", {})
    figtitle1: str = vehData[setIdx].get("figtitle1", "")

    # Header title content
    oem = str(log_data.get("oem", ""))
    model = str(log_data.get("model", ""))
    my = str(log_data.get("my", ""))
    veh_model_str = f"{oem} {model} {my}".strip()
    header_title = f"EPA NVFEL Laboratory:  PEMS Emissions Test Report:  {veh_model_str}"

    # Initialize FPDF (Letter, inches)
    pdf = PDF(header_title=header_title, unit="in", format="letter")
    pdf.set_margins(left=0.5, top=0.5, right=0.5)   # as in MATLAB
    pdf.set_auto_page_break(auto=True, margin=0.25)  # bottom 0.25"

    # ------------------ Page 1: Tables ------------------
    pdf.add_page()
    pdf.ln(0.05)

    # Test Information (Heading3)
    pdf_add_heading(pdf, "Test Information", level=3)
    pg1_tab1 = [
        ["Date and Time", str(log_data.get("dateTime", ""))],
        ["Vehicle Model", veh_model_str],
        ["Vehicle ID", str(log_data.get("vehicleID", ""))],
        ["File Name", str(log_data.get("filename", ""))],
    ]
    draw_table(pdf, pg1_tab1, align_center=False, force_width=7.5)

    # Vehicle and Cycle (Heading3)
    pdf.ln(0.12)
    A = scalar_data.get("Distance_Mile", np.nan)
    S = scalar_units.get("Distance_Mile", "(mile)")
    cycle_distance = f"{A:10.2f} {S}"

    pdf_add_heading(pdf, "Vehicle and Cycle", level=3)
    tabVC = [
        ["Test Cycle", str(log_data.get("testCycle", "")), "  ---  ", "Fuel", str(log_data.get("fuel", ""))],
        ["Cycle Distance", cycle_distance, "  ---  ", "VIN", str(log_data.get("vin", ""))],
        ["Odometer (miles)", str(log_data.get("odo", "")), "  ---  ", "Start Conditions", str(log_data.get("startCond", ""))],
        ["Test Group", str(log_data.get("testGroup", "")), "  ---  ", "Displacement", str(log_data.get("disp", ""))],
        ["Drive Mode", str(log_data.get("driveMode", "")), "  ---  ", "Emissons Standard", str(log_data.get("emStandard", ""))],
        ["Start/Stop", str(log_data.get("startStop", "")), "  ---  ", "Air Conditioning", str(log_data.get("airCond", ""))],
        ["Driver", str(log_data.get("driver", "")), "  ---  ", "Equipment", str(log_data.get("equipment", ""))],
        ["Trailer", str(log_data.get("trailer", "")), "  ---  ", "Trailer + Ballast Wt.", str(log_data.get("trailerWt", ""))],
    ]
    draw_table(pdf, tabVC, align_center=False, force_width=7.5)

    # Fuel Properties (Heading3)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Fuel Properties", level=3)
    tabFuel = [
        ["FTAG", str(log_data.get("ftag", ""))],
        ["Lower Heating Value (BTU/lb)", str(udp[setIdx]["fuel"]["nhv"])],
        ["Carbon Weight Fraction", str(udp[setIdx]["fuel"]["cwf"])],
        ["Specific Gravity", str(udp[setIdx]["fuel"]["sg"])],
    ]
    draw_table(pdf, tabFuel, align_center=True, force_width=7.5)

    # File Import and Analysis Options (Heading3)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "File Import and Analysis Options", level=3)
    kh = int(udp[setIdx]["log"]["kh"])
    if kh == 0:
        kh_str = "No Correction"
    elif kh == 1:
        kh_str = "CFR 1066.615 Vehicles at or below 14,000 lbs GVWR"
    elif kh == 2:
        kh_str = "CFR 1065.670 SI"
    else:
        kh_str = "CFR 1065.670 Diesel"
    tabAno = [
        ["File Import: Fill Missing Data", str(udp[setIdx]["import"].get("missingData", ""))],
        ["File Import: Fill End Values (extrapolate)", str(udp[setIdx]["import"].get("endValues", ""))],
        ["Humidity Correction Factor", kh_str],
    ]
    if str(udp[setIdx]["log"].get("dataType", "")).lower() == "pems":
        tabAno.append(["Vehicle Speed Source (CAN or GPS)", str(udp[setIdx]["pems"].get("speedSource", ""))])
    draw_table(pdf, tabAno, align_center=True, force_width=7.5)

    # Ambient and Start Conditions (Heading3)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Ambient and Start Conditions", level=3)
    def sget(name, fmt="%8.1f"):
        v = scalar_data.get(name, np.nan)
        return fmt_float(v, fmt)

    idle_unit = scalar_units.get("Idle_Time_At_Start", "(s)")
    amb_start_unit = scalar_units.get("Ambient_T_At_Start", "(F)")
    coolant_start_unit = scalar_units.get("Coolant_T_At_Start", "(F)")

    tabAmb = [
        ["Average Ambient Temperature", "F", sget("Avg_Ambient_Temperature", "%8.1f")],
        ["Average Ambient Relative Humidity", "%", sget("Avg_Ambient_RelativeHumidity", "%8.1f")],
        ["Ambient Temperature At Start", amb_start_unit, sget("Ambient_T_At_Start", "%8.1f")],
        ["Coolant Temperature At Start", coolant_start_unit, sget("Coolant_T_At_Start", "%8.1f")],
        ["Idle Time At Start", idle_unit, sget("Idle_Time_At_Start", "%8.1f")],
    ]
    draw_table(pdf, tabAmb, align_center=True, force_width=7.5)

    # Test Purpose and Notes (Heading3)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Test Purpose and Notes", level=3)
    tabPn = [
        ["Test Purpose", str(log_data.get("purpose", ""))],
        ["Notes and Issues", str(log_data.get("notes", ""))],
    ]
    draw_table(pdf, tabPn, align_center=False, force_width=7.5)

    # ------------------ Page 2: Mass Emissions Tables ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)

    pdf.ln(0.12)
    pdf_add_heading(pdf, "Test Cycle Mass Emissions", level=3)
    # mg/mile for LD
    fspec = "%8.1f"
    kNOx_val = scalar_data.get("kNOx_Mg_Per_Mile", np.nan); kNOx_unit = scalar_units.get("kNOx_Mg_Per_Mile", "(mg/mile)")
    HC_val = scalar_data.get("HC_Mg_Per_Mile", np.nan); HC_unit = scalar_units.get("HC_Mg_Per_Mile", "(mg/mile)")
    NMHC_val = scalar_data.get("NMHC_Mg_Per_Mile", np.nan); NMHC_unit = scalar_units.get("NMHC_Mg_Per_Mile", "(mg/mile)")
    Plus_val = scalar_data.get("NOxPlusNMHC_Mg_Per_Mile", np.nan); Plus_unit = scalar_units.get("NOxPlusNMHC_Mg_Per_Mile", "(mg/mile)")
    CO_val = scalar_data.get("CO_Gms_Per_Mile", np.nan); CO_unit = scalar_units.get("CO_Gms_Per_Mile", "(gm/mile)")
    CO2_val = scalar_data.get("CO2_Gms_Per_Mile", np.nan); CO2_unit = scalar_units.get("CO2_Gms_Per_Mile", "(gm/mile)")

    tabMe = [
        ["kNOx", "THC", "NMHC", "kNOx+NMHC", "CO", "CO2"],
        [kNOx_unit, HC_unit, NMHC_unit, Plus_unit, CO_unit, CO2_unit],
        [fmt_float(kNOx_val, fspec), fmt_float(HC_val, fspec), fmt_float(NMHC_val, fspec),
         fmt_float(Plus_val, fspec), fmt_float(CO_val, "%8.2f"), fmt_float(CO2_val, "%8.1f")],
    ]
    draw_table(pdf, tabMe, align_center=True, force_width=7.5)

    # Particulates (optional)
    if bool(udp[setIdx]["log"].get("pm2Active", False)):
        pdf.ln(0.12)
        pdf_add_heading(pdf, "Particulate Emissions", level=3)
        lg = udp[setIdx]["log"]
        tabPe = [
            ["Filter Position #", "(-)", str(lg.get("filterPosition", "")),
             "Filter ID #", "(-)", str(lg.get("filter2ID", ""))],
            ["Pre-Weight", "(mg)", fmt_float(lg.get("filter2WtPre", np.nan), "%8.4f"),
             "Post-Weight", "(mg)", fmt_float(lg.get("filter2WtPost", np.nan), "%8.4f")],
            ["PM Tailpipe Mass", "(mg)", fmt_float(lg.get("pmTaipipeMass", np.nan), "%8.2f"),
             "PM Tailpipe mg/mile", "(mg/mile)", fmt_float(lg.get("pmTailpipeDistanceSpec", np.nan), "%8.2f")],
        ]
        draw_table(pdf, tabPe, align_center=True, force_width=7.5)

    # Fuel Economy
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Fuel Economy", level=3)
    FE_val = scalar_data.get("Fuel_Economy", np.nan)
    FE_unit = scalar_units.get("Fuel_Economy", "(mpg)")
    tabFe = [["Fuel Economy"], [FE_unit], [f"{FE_val:8.2f}"]]
    draw_table(pdf, tabFe, align_center=True, force_width=2.0)

    # Weighted to FTP75 (optional)
    if bool(udp[setIdx]["log"].get("ftpNormCalc", False)):
        pdf.ln(0.12)
        pdf_add_heading(pdf, "Test Cycle Mass Emissions:  Weighted to FTP75", level=3)
        fspec = "%8.1f"
        tabFtp = [
            ["kNOx", "THC", "NMHC", "kNOx+NMHC", "CO", "CO2"],
            [
                scalar_units.get("kNOx_Mg_Per_Mile_FTPEquiv", "(mg/mile)"),
                scalar_units.get("HC_Mg_Per_Mile_FTPEquiv", "(mg/mile)"),
                scalar_units.get("NMHC_Mg_Per_Mile_FTPEquiv", "(mg/mile)"),
                scalar_units.get("NOxPlusNMHC_Mg_Per_Mile_FTPEquiv", "(mg/mile)"),
                scalar_units.get("CO_Gms_Per_Mile_FTPEquiv", "(gm/mile)"),
                scalar_units.get("CO2_Gms_Per_Mile_FTPEquiv", "(gm/mile)"),
            ],
            [
                fmt_float(scalar_data.get("kNOx_Mg_Per_Mile_FTPEquiv", np.nan), fspec),
                fmt_float(scalar_data.get("HC_Mg_Per_Mile_FTPEquiv", np.nan), fspec),
                fmt_float(scalar_data.get("NMHC_Mg_Per_Mile_FTPEquiv", np.nan), fspec),
                fmt_float(scalar_data.get("NOxPlusNMHC_Mg_Per_Mile_FTPEquiv", np.nan), fspec),
                fmt_float(scalar_data.get("CO_Gms_Per_Mile_FTPEquiv", np.nan), "%8.2f"),
                fmt_float(scalar_data.get("CO2_Gms_Per_Mile_FTPEquiv", np.nan), "%8.1f"),
            ],
        ]
        draw_table(pdf, tabFtp, align_center=True, force_width=7.5)

    # ------------------ Figures: Ambient Conditions ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Ambient Conditions", level=3)
    img_amb = _plot_ambient_conditions(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_amb, w=7.0)

    # ------------------ Figures: Exhaust Flow ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Exhaust Flow", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Exhaust Flow", level=3)
    img_exh = _plot_exhaust_flow(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_exh, w=7.0)

    # ------------------ Figures: Lambda and Coolant Temp ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Lambda and Coolant Temperature", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Lambda and Coolant Temperature", level=4)
    img_lam = _plot_lambda_coolant(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_lam, w=7.0)

    # ------------------ Figures: NOx Summary ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Test Cycle NOx", level=3)
    img_nox = _plot_nox_summary(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_nox, w=7.0)

    # ------------------ Figures: CO Summary ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Test Cycle CO", level=3)
    img_co = _plot_co_summary(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_co, w=7.0)

    # ------------------ Figures: HC Summary ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Test Cycle HC", level=3)
    img_hc = _plot_hc_summary(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_hc, w=7.0)

    # ------------------ Figures: CO2 Summary ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Test Cycle CO2", level=3)
    img_co2 = _plot_co2_summary(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_co2, w=7.0)

    # ------------------ Figures: PM Summary (optional) ------------------
    if bool(udp[setIdx]["log"].get("pm2Active", False)):
        pdf.add_page()
        pdf_add_heading(pdf, "Test Information", level=2)
        header_table_pdf(pdf, log_data, veh_model_str)
        pdf.ln(0.12)
        pdf_add_heading(pdf, "Figure:  Test Cycle PM", level=3)
        img_pm = _plot_pm_summary(setIdx, vehData, udp, figtitle1)
        pdf_image_center(pdf, img_pm, w=7.0)

    # ------------------ Figures: Analog Signals (optional) ------------------
    if bool(udp[setIdx]["log"].get("enableAnalog", False)):
        pdf.add_page()
        pdf_add_heading(pdf, "Test Information", level=2)
        header_table_pdf(pdf, log_data, veh_model_str)
        pdf.ln(0.12)
        pdf_add_heading(pdf, "Figure:  Analog Signals", level=3)
        img_ana = _plot_analog_signals(setIdx, vehData, udp, figtitle1)
        pdf_image_center(pdf, img_ana, w=7.0)

    # ------------------ Figures: Geographic Location ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Geogaphic Location", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  GPS Latitude and Longitude Test Route", level=3)
    img_geo = _plot_geo_route(setIdx, vehData, udp)
    pdf_image_center(pdf, img_geo, w=7.0)

    # Save PDF
    pdf.output(filename)


# ----------------------------- PDF helpers -----------------------------

class PDF(FPDF):
    def __init__(self, header_title: str, unit: str = "in", format: str = "letter"):
        super().__init__(orientation="P", unit=unit, format=format)
        self.header_title = header_title
        self.alias_nb_pages()

    def header(self):
        # Header rule and centered title (approx MATLAB)
        width = self.w
        # draw line ~0.5in from top
        y_line = 0.5
        self.set_line_width(0.02)
        self.set_draw_color(0, 0, 0)
        self.line(0.5, y_line, width - 0.5, y_line)

        # header text
        self.set_font("Helvetica", size=8)  # Heading font size "8pt" in MATLAB
        self.set_y(y_line + 0.05)
        self.cell(0, 0.2, self.header_title, border=0, ln=1, align="C")

    def footer(self):
        # Footer rule and page number centered
        width = self.w
        y_line = 0.5
        self.set_y(-y_line - 0.2)
        self.set_line_width(0.02)
        self.set_draw_color(0, 0, 0)
        self.line(0.5, self.h - y_line, width - 0.5, self.h - y_line)
        self.set_y(-y_line + 0.05)
        self.set_font("Helvetica", size=8)
        self.cell(0, 0.2, f"Page {self.page_no()}", align="C")


def pdf_add_heading(pdf: PDF, text: str, level: int = 3):
    """
    Heading styles:
      level 2 -> larger
      level 3 -> medium
      level 4 -> smaller
    Centered headings, bold.
    """
    if level == 2:
        pdf.set_font("Helvetica", "B", 12)
    elif level == 3:
        pdf.set_font("Helvetica", "B", 11)
    else:
        pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 0.25, text, ln=1, align="C")


def draw_table(pdf: PDF,
               data: List[List[Any]],
               align_center: bool = True,
               force_width: float = None,
               col_widths: List[float] = None):
    """
    Draw a bordered table similar to MATLAB Report Generator styling:
    - data: rows (list of list)
    - align_center: center vs left alignment
    - force_width: table width (inches). Defaults to available content width.
    - col_widths: optional column widths (inches), must sum to force_width if provided.
    """
    # Convert all cells to strings
    rows = [[coalesce(cell) for cell in row] for row in data]
    ncols = max(len(r) for r in rows)

    # Dimensions
    content_width = pdf.w - pdf.l_margin - pdf.r_margin
    table_width = force_width if force_width else content_width
    if col_widths is None:
        cw = table_width / ncols
        col_widths = [cw] * ncols
    else:
        # normalize if not sum
        s = sum(col_widths)
        if abs(s - table_width) > 1e-6:
            col_widths = [w * (table_width / s) for w in col_widths]

    # start X to center horizontally
    x_start = pdf.l_margin + (content_width - table_width) / 2.0
    pdf.set_x(x_start)

    # style
    pdf.set_draw_color(192, 192, 192)  # silver
    pdf.set_line_width(0.02)
    pdf.set_font("Helvetica", size=9)
    line_h = 0.22  # approximately 9pt

    for row in rows:
        pdf.set_x(x_start)
        for i in range(ncols):
            txt = row[i] if i < len(row) else ""
            align = "C" if align_center else "L"
            pdf.cell(col_widths[i], line_h, txt, border=1, align=align)
        pdf.ln(line_h)


def header_table_pdf(pdf: PDF, log_data: Dict[str, Any], veh_model_str: str):
    data = [
        ["Date and Time", str(log_data.get("dateTime", ""))],
        ["Vehicle Model", veh_model_str],
        ["Vehicle ID", str(log_data.get("vehicleID", ""))],
        ["File Name", str(log_data.get("filename", ""))],
    ]
    draw_table(pdf, data, align_center=False, force_width=7.0)


def pdf_image_center(pdf: PDF, img_path: str, w: float):
    # center an image by width (inches), keep aspect
    content_width = (pdf.w - pdf.l_margin - pdf.r_margin)
    x = pdf.l_margin + (content_width - w) / 2.0
    pdf.image(img_path, x=x, w=w)
    pdf.ln(0.1)


def fmt_float(val: Any, fmt: str = "%8.4f") -> str:
    try:
        return fmt % float(val)
    except Exception:
        return str(val)


def coalesce(val: Any, default: str = "") -> str:
    try:
        if val is None:
            return default
        if isinstance(val, str):
            return val
        return str(val)
    except Exception:
        return default


# ------------------------- Plotting helpers -------------------------

def _get_series(vehData: List[Dict[str, Any]], setIdx: int, col: str):
    df = vehData[setIdx]["data"]
    return df[col].to_numpy()


def _plot_ambient_conditions(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # Vehicle speed CAN / GPS
    axs[0].grid(True, axis="y"); axs[0].set_ylim(0, 80)
    axs[0].plot(x, df[p["speedCAN"]], color="b", label="CAN")
    ax0r = axs[0].twinx(); ax0r.set_ylim(0, 80)
    ax0r.plot(x, df[p["speedGPS"]], color=(0.8510, 0.3255, 0.0980), label="GPS")
    axs[0].set_title(figtitle)
    axs[0].legend(loc="upper right")

    # Ambient Temp (F) from two sensors
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["ambientAirT"]], color="k", linewidth=1, label=p["ambientAirT"])
    axs[1].plot(x, df[p["ambientAirTCAN"]], color=(0.3098, 0.5098, 0.0471), linewidth=1, label=p["ambientAirTCAN"])
    axs[1].set_ylabel("Ambient Temperature (F)")
    axs[1].legend(loc="upper left")

    # RH and Dry-to-Wet correction factor
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["rHumidity"]], linewidth=1)
    ax2r = axs[2].twinx(); ax2r.set_ylim(0.5, 1.0)
    ax2r.plot(x, df[p["dryWetCorrFac"]], linewidth=1, color=(0.85, 0.33, 0.1))

    # Barometric pressure and altitude
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["ambientAirP"]], color="k", linewidth=1)
    ax3r = axs[3].twinx()
    ax3r.plot(x, df[p["altitude"]], linewidth=1)
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "ambient_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_exhaust_flow(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    # engine speed
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["engineSpeed"]], color=(0.3098, 0.5098, 0.0471))
    # SCFM
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["scfm"]], linewidth=1)
    # Exhaust temperature
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["texhaust"]], linewidth=1)
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "exhFlow_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_lambda_coolant(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    # pedal position D
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["pedalPosD"]], color=(0.3098, 0.5098, 0.0471))
    # coolant temperature
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["coolantT"]], color="k")
    # lambda
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["lambda"]], color="k")
    axs[3].set_ylim(0.6, 1.6)
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "lambda_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_nox_summary(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed + dist (right)
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    ax0r = axs[0].twinx()
    ax0r.plot(x, df[p["distSumMile"]], color=(0.8510, 0.3255, 0.0980))
    # humidity corr factor + corrected cumulative NOx g/mi (right)
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["noxHumidCorrFac"]], color=(0.3098, 0.5098, 0.0471))
    axs[1].set_ylim(0.6, 1.4)
    ax1r = axs[1].twinx()
    ax1r.plot(x, df[p["corrCuNOxGmPerMile"]], color="k")
    # NOx concentration
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["wetkNOx"]], color="k")
    # cumulative NOx + NOx mass flow (right)
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["kNOxSum"]], color="k")
    ax3r = axs[3].twinx()
    ax3r.plot(x, df[p["kNOxMassFlow"]], color=(0.8510, 0.3255, 0.0980))
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "pg2_nox_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_co_summary(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed + dist
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    ax0r = axs[0].twinx()
    ax0r.plot(x, df[p["distSumMile"]], color=(0.8510, 0.3255, 0.0980))
    # cumulative CO g/mi
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["cuCOGmPerMile"]], color=(0.4667, 0.6745, 0.1882), linewidth=2)
    axs[1].set_ylim(0, 10)
    # CO concentration + lambda (right)
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["wetCO"]], color="k", linewidth=2)
    ax2r = axs[2].twinx()
    ax2r.plot(x, df[p["lambda"]], color="C1", linewidth=1)
    # cumulative CO + CO mass flow (right)
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["coSum"]], color="k", linewidth=1)
    ax3r = axs[3].twinx()
    ax3r.plot(x, df[p["coMassFlow"]], color=(0.8510, 0.3255, 0.0980), linewidth=1)
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "co_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_hc_summary(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed + dist
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    ax0r = axs[0].twinx()
    ax0r.plot(x, df[p["distSumMile"]], color=(0.8510, 0.3255, 0.0980))
    # cumulative HC g/mi
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["cuHCGmPerMile"]], color=(0.4667, 0.6745, 0.1882), linewidth=2)
    axs[1].set_ylim(0, 0.4)
    # HC concentration + lambda (right)
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["wetHC"]], color="k", linewidth=2)
    ax2r = axs[2].twinx()
    ax2r.plot(x, df[p["lambda"]], color="C1", linewidth=1)
    # cumulative HC + HC mass flow (right)
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["hcSum"]], color="k", linewidth=1)
    ax3r = axs[3].twinx()
    ax3r.plot(x, df[p["hcMassFlow"]], color=(0.8510, 0.3255, 0.0980), linewidth=1)
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "hc_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_co2_summary(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed + dist
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    ax0r = axs[0].twinx()
    ax0r.plot(x, df[p["distSumMile"]], color=(0.8510, 0.3255, 0.0980))
    # cumulative CO2 g/mi
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["cuCO2GmPerMile"]], color=(0.4667, 0.6745, 0.1882), linewidth=1)
    axs[1].set_ylim(0, 1400)
    # CO2 concentration
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["wetCO2"]], color="k", linewidth=1)
    # cumulative CO2 + CO2 mass flow (right)
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["co2Sum"]], color="k", linewidth=1)
    ax3r = axs[3].twinx()
    ax3r.plot(x, df[p["co2MassFlow"]], color=(0.8510, 0.3255, 0.0980), linewidth=1)
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "co2_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_pm_summary(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(3, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    # lambda
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["lambda"]], color=(0.4667, 0.6745, 0.1882), linewidth=2)
    axs[1].set_ylim(0.6, 1.6)
    # cumulative PM + PM mass flow (right)
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["pmSum"]], color="k", linewidth=1)
    ax2r = axs[2].twinx()
    ax2r.plot(x, df[p["pmMassTailpipe"]], color=(0.8510, 0.3255, 0.0980), linewidth=1)
    axs[2].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "pm_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_analog_signals(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)
    # vehicle speed
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["speed"]], color="b")
    axs[0].set_title(figtitle)
    # pressure transducer psi
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["prTransPsi"]], color=(0.4667, 0.6745, 0.1882), linewidth=1)
    # temp before/after cat
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["tcTemp1"]], color="k", linewidth=1, label=p["tcTemp1"])
    axs[2].plot(x, df[p["tcTemp2"]], color="b", linewidth=1, label=p["tcTemp2"])
    axs[2].legend(loc="upper left")
    # temp at pressure transducer
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["tcTemp3"]], color="k", linewidth=1)
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "ana_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_geo_route(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]]) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    lat = df[p["latitude"]].to_numpy()
    lon = df[p["longitude"]].to_numpy()

    fig, ax = plt.subplots(figsize=(9.42, 9.82))
    ax.plot(lon, lat, "b--")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    out = "geo_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ------------------------- Example runner placeholder -------------------------
if __name__ == "__main__":
    # Example usage:
    # report_pems_ld_emissions(setIdx, "LD_Emissions_Report", vehData, udp)
    pass