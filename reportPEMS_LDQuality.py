import os
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

from fpdf import FPDF


def report_pems_ld_quality(setIdx: int,
                           filename: str,
                           vehData: List[Dict[str, Any]],
                           udp: List[Dict[str, Any]]) -> None:
    """
    FPDF-based implementation of reportPEMS_LDQuality (MATLAB).
    - setIdx: zero-based dataset index
    - filename: PDF filename ('.pdf' added if missing)
    - vehData[setIdx]: dict with keys:
        data (pandas.DataFrame),
        units (dict: column name -> unit string),
        scalarData (dict of scalars),
        scalarUnits (dict of units for scalars),
        logData (dict of metadata),
        figtitle1 (optional)
    - udp[setIdx]: dict with keys:
        pems (dict of column names),
        fuel (dict: nhv, cwf, sg),
        import (dict: missingData, endValues),
        log (dict: kh, dataType, ftpNormCalc(bool), pm2Active(bool), enableAnalog(bool),
             filterPosition, filter2ID, filter2WtPre, filter2WtPost,
             pmTaipipeMass, pmTailpipeDistanceSpec,
             noRefSpan, no2RefSpan, thcRefSpan, coRefSpan, co2RefSpan)
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
    header_title = f"NVFEL Laboratory:  PEMS Quality Test Report:  {veh_model_str}"

    # Initialize FPDF (Letter, inches, margins per MATLAB)
    pdf = PDF(header_title=header_title, unit="in", format="letter")
    pdf.set_margins(left=0.5, top=0.5, right=0.5)
    pdf.set_auto_page_break(auto=True, margin=0.25)

    # ------------------ Page 1: Tables ------------------
    pdf.add_page()
    pdf.ln(0.05)

    # Test Information
    pdf_add_heading(pdf, "Test Information", level=3)
    tab1 = [
        ["Date and Time", str(log_data.get("dateTime", ""))],
        ["Vehicle Model", veh_model_str],
        ["Vehicle ID", str(log_data.get("vehicleID", ""))],
        ["File Name", str(log_data.get("filename", ""))],
    ]
    draw_table(pdf, tab1, align_center=False, force_width=7.5)

    # Vehicle and Cycle
    pdf.ln(0.12)
    A = scalar_data.get("Distance_Mile", np.nan)
    S = scalar_units.get("Distance_Mile", "(mile)")
    cycle_distance = f"{A:10.2f} {S}"

    pdf_add_heading(pdf, "Vehicle and Cycle", level=3)
    tabVC = [
        ["Test Cycle", str(log_data.get("testCycle", "")), "  ---  ", "Fuel", str(log_data.get("fuel", ""))],
        ["Cycle Distance", cycle_distance, "  ---  ", "VIN", str(log_data.get("vin", ""))],
        ["Odometer", str(log_data.get("odo", "")), "  ---  ", "Start Conditions", str(log_data.get("startCond", ""))],
        ["Test Group", str(log_data.get("testGroup", "")), "  ---  ", "Displacement", str(log_data.get("disp", ""))],
        ["Drive Mode", str(log_data.get("driveMode", "")), "  ---  ", "Emissons Standard", str(log_data.get("emStandard", ""))],
        ["Start/Stop", str(log_data.get("startStop", "")), "  ---  ", "Air Conditioning", str(log_data.get("airCond", ""))],
        ["Driver", str(log_data.get("driver", "")), "  ---  ", "Equipment", str(log_data.get("equipment", ""))],
        ["Trailer", str(log_data.get("trailer", "")), "  ---  ", "Trailer + Ballast Wt.", str(log_data.get("trailerWt", ""))],
    ]
    draw_table(pdf, tabVC, align_center=False, force_width=7.5)

    # Fuel Properties
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Fuel Properties", level=3)
    tabFuel = [
        ["FTAG", str(log_data.get("ftag", ""))],
        ["Lower Heating Value (BTU/lb)", str(udp[setIdx]["fuel"]["nhv"])],
        ["Carbon Weight Fraction", str(udp[setIdx]["fuel"]["cwf"])],
        ["Specific Gravity", str(udp[setIdx]["fuel"]["sg"])],
    ]
    draw_table(pdf, tabFuel, align_center=True, force_width=7.5)

    # File Import and Analysis Options
    pdf.ln(0.12)
    pdf_add_heading(pdf, "File Import and Analysis Options", level=3)
    kh = int(udp[setIdx]["log"]["kh"])
    kh_map = {
        0: "No Correction",
        1: "CFR 1066.615 Vehicles at or below 14,000 lbs GVWR",
        2: "CFR 1065.670 SI",
        3: "CFR 1065.670 Diesel",
    }
    tabAno = [
        ["File Import: Fill Missing Data", str(udp[setIdx]["import"].get("missingData", ""))],
        ["File Import: Fill End Values (extrapolate)", str(udp[setIdx]["import"].get("endValues", ""))],
        ["Humidity Correction Factor", kh_map.get(kh, "CFR 1065.670 Diesel")],
    ]
    if str(udp[setIdx]["log"].get("dataType", "")).lower() == "pems":
        tabAno.append(["Vehicle Speed Source (CAN or GPS)", str(udp[setIdx]["pems"].get("speedSource", ""))])
    draw_table(pdf, tabAno, align_center=True, force_width=7.5)

    # Ambient and Start Conditions
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Ambient and Start Conditions", level=3)
    def sget(name, fmt="%8.1f"):
        return fmt_float(scalar_data.get(name, np.nan), fmt)
    idle_unit = scalar_units.get("Idle_Time_At_Start", "(s)")
    cool_unit = scalar_units.get("Coolant_T_At_Start", "(F)")
    amb_start_unit = scalar_units.get("Ambient_T_At_Start", "(F)")
    tabAmb = [
        ["Average Ambient Temperature", "F", sget("Avg_Ambient_Temperature", "%8.1f")],
        ["Average Ambient Relative Humidity", "%", sget("Avg_Ambient_RelativeHumidity", "%8.1f")],
        ["Ambient Temperature At Start", amb_start_unit, sget("Ambient_T_At_Start", "%8.1f")],
        ["Coolant Temperature At Start", cool_unit, sget("Coolant_T_At_Start", "%8.1f")],
        ["Idle Time At Start", idle_unit, sget("Idle_Time_At_Start", "%8.1f")],
    ]
    draw_table(pdf, tabAmb, align_center=True, force_width=7.5)

    # Test Purpose and Notes
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Test Purpose and Notes", level=3)
    tabPn = [
        ["Test Purpose", str(log_data.get("purpose", ""))],
        ["Notes and Issues", str(log_data.get("notes", ""))],
    ]
    draw_table(pdf, tabPn, align_center=False, force_width=7.5)

    # ------------------ Page 2: Emissions, FE, etc. ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)

    pdf.ln(0.12)
    pdf_add_heading(pdf, "Test Cycle Mass Emissions", level=3)
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
                fmt_float(scalar_data.get("kNOx_Mg_Per_Mile_FTPEquiv", np.nan), "%8.1f"),
                fmt_float(scalar_data.get("HC_Mg_Per_Mile_FTPEquiv", np.nan), "%8.1f"),
                fmt_float(scalar_data.get("NMHC_Mg_Per_Mile_FTPEquiv", np.nan), "%8.1f"),
                fmt_float(scalar_data.get("NOxPlusNMHC_Mg_Per_Mile_FTPEquiv", np.nan), "%8.1f"),
                fmt_float(scalar_data.get("CO_Gms_Per_Mile_FTPEquiv", np.nan), "%8.2f"),
                fmt_float(scalar_data.get("CO2_Gms_Per_Mile_FTPEquiv", np.nan), "%8.1f"),
            ],
        ]
        draw_table(pdf, tabFtp, align_center=True, force_width=7.5)

    # ------------------ Figures: Drift Check ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Drift Check", level=3)
    img_drift = _plot_drift_check(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_drift, w=7.0)

    # ------------------ Figures: Span Gas Limits ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "Span Gas Limits", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Span Gas Limits", level=3)
    img_span = _plot_span_limits(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_span, w=7.0)

    # ------------------ Figures: PEMS Quality Checks (1) ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "PEMS Quality Checks", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Sample Flow", level=3)
    img_qc1 = _plot_pems_quality_checks1(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_qc1, w=7.0)

    # ------------------ Figures: PEMS Quality Checks (2) ------------------
    pdf.add_page()
    pdf_add_heading(pdf, "PEMS Quality Checks", level=2)
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.12)
    pdf_add_heading(pdf, "Figure:  Sample Humidity and Temperature", level=3)
    img_qc2 = _plot_pems_quality_checks2(setIdx, vehData, udp, figtitle1)
    pdf_image_center(pdf, img_qc2, w=7.0)

    # Save PDF
    pdf.output(filename)


# ----------------------------- PDF helpers -----------------------------

class PDF(FPDF):
    def __init__(self, header_title: str, unit: str = "in", format: str = "letter"):
        super().__init__(orientation="P", unit=unit, format=format)
        self.header_title = header_title
        self.alias_nb_pages()

    def header(self):
        # Horizontal rule ~0.5 in from top and centered title
        width = self.w
        y_line = 0.5
        self.set_line_width(0.02)
        self.set_draw_color(0, 0, 0)
        self.line(0.5, y_line, width - 0.5, y_line)
        self.set_font("Helvetica", size=8)
        self.set_y(y_line + 0.05)
        self.cell(0, 0.2, self.header_title, border=0, ln=1, align="C")

    def footer(self):
        # Horizontal rule ~0.5 in from bottom and centered page number
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
    # Centered bold headings with sizes roughly matching MATLAB
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
    - force_width: table width (inches). Defaults to content width.
    - col_widths: optional column widths (must sum to force_width if provided).
    """
    rows = [[coalesce(cell) for cell in row] for row in data]
    ncols = max(len(r) for r in rows)

    content_width = pdf.w - pdf.l_margin - pdf.r_margin
    table_width = force_width if force_width else content_width
    if col_widths is None:
        cw = table_width / ncols
        col_widths = [cw] * ncols
    else:
        s = sum(col_widths)
        if abs(s - table_width) > 1e-6:
            col_widths = [w * (table_width / s) for w in col_widths]

    x_start = pdf.l_margin + (content_width - table_width) / 2.0
    pdf.set_x(x_start)

    pdf.set_draw_color(192, 192, 192)  # silver
    pdf.set_line_width(0.02)
    pdf.set_font("Helvetica", size=9)
    line_h = 0.22  # ~9pt

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
    # Center an image by width (inches), keep aspect
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

def _plot_drift_check(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    # Prepare data
    y_nox = df[p["kNOxSum"]].to_numpy()
    y_nox_d = df[p["kNOxSumDrift"]].to_numpy()
    y_hc = df[p["hcSum"]].to_numpy()
    y_hc_d = df[p["hcSumDrift"]].to_numpy()
    y_co = df[p["coSum"]].to_numpy()
    y_co_d = df[p["coSumDrift"]].to_numpy()
    y_co2 = df[p["co2Sum"]].to_numpy()
    y_co2_d = df[p["co2SumDrift"]].to_numpy()

    with np.errstate(divide="ignore", invalid="ignore"):
        drift_nox = 100.0 * (y_nox - y_nox_d) / y_nox
        drift_hc = 100.0 * (y_hc - y_hc_d) / y_hc
        drift_co = 100.0 * (y_co - y_co_d) / y_co
        drift_co2 = 100.0 * (y_co2 - y_co2_d) / y_co2

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)

    # NOx
    axs[0].grid(True, axis="y")
    axs[0].plot(x, y_nox, label=p["kNOxSum"])
    axs[0].plot(x, y_nox_d, color=(0.8510, 0.3255, 0.0980), label=p["kNOxSumDrift"])
    axs[0].set_title(figtitle)
    ax0r = axs[0].twinx()
    ax0r.plot(x, drift_nox, color="C2", label="Drift %")
    ax0r.set_ylim(-10, 10)
    # limit lines
    ax0r.plot([x[0], x[-1]], [4, 4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    ax0r.plot([x[0], x[-1]], [-4, -4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    axs[0].legend(loc="upper left")

    # HC
    axs[1].grid(True, axis="y")
    axs[1].plot(x, y_hc, label=p["hcSum"])
    axs[1].plot(x, y_hc_d, color=(0.8510, 0.3255, 0.0980), label=p["hcSumDrift"])
    ax1r = axs[1].twinx()
    ax1r.plot(x, drift_hc, color="C2")
    ax1r.set_ylim(-10, 10)
    ax1r.plot([x[0], x[-1]], [4, 4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    ax1r.plot([x[0], x[-1]], [-4, -4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    axs[1].legend(loc="upper left")

    # CO
    axs[2].grid(True, axis="y")
    axs[2].plot(x, y_co, label=p["coSum"])
    axs[2].plot(x, y_co_d, color=(0.8510, 0.3255, 0.0980), label=p["coSumDrift"])
    ax2r = axs[2].twinx()
    ax2r.plot(x, drift_co, color="C2")
    ax2r.set_ylim(-10, 10)
    ax2r.plot([x[0], x[-1]], [4, 4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    ax2r.plot([x[0], x[-1]], [-4, -4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    axs[2].legend(loc="upper left")

    # CO2
    axs[3].grid(True, axis="y")
    axs[3].plot(x, y_co2, label=p["co2Sum"])
    axs[3].plot(x, y_co2_d, color=(0.8510, 0.3255, 0.0980), label=p["co2SumDrift"])
    ax3r = axs[3].twinx()
    ax3r.plot(x, drift_co2, color="C2")
    ax3r.set_ylim(-10, 10)
    ax3r.plot([x[0], x[-1]], [4, 4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    ax3r.plot([x[0], x[-1]], [-4, -4], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    axs[3].set_xlabel("Time (s)")
    axs[3].legend(loc="upper left")

    fig.tight_layout()
    out = "drift_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_span_limits(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    lg = udp[setIdx]["log"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()
    tmin, tmax = (x[0], x[-1]) if len(x) else (0.0, 1.0)

    fig, axs = plt.subplots(5, 1, figsize=(9.42, 9.82), sharex=True)

    # NO
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["NO"]], label=p["NO"])
    axs[0].plot([tmin, tmax], [lg.get("noRefSpan", np.nan)] * 2, color=(0.8510, 0.3255, 0.0980), label="NO Span")
    axs[0].set_title(figtitle); axs[0].legend(loc="upper right")

    # NO2
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["NO2"]], label=p["NO2"])
    axs[1].plot([tmin, tmax], [lg.get("no2RefSpan", np.nan)] * 2, color=(0.8510, 0.3255, 0.0980), label="NO2 Span")
    axs[1].legend(loc="upper right")

    # HC
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["HC"]], label=p["HC"])
    axs[2].plot([tmin, tmax], [lg.get("thcRefSpan", np.nan)] * 2, color=(0.8510, 0.3255, 0.0980), label="HC Span")
    axs[2].legend(loc="upper right")

    # CO (assume span units match series; convert beforehand if needed)
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["CO"]], label=p["CO"])
    axs[3].plot([tmin, tmax], [lg.get("coRefSpan", np.nan)] * 2, color=(0.8510, 0.3255, 0.0980), label="CO Span")
    axs[3].legend(loc="upper right")

    # CO2 (assume span units match series; convert beforehand if needed)
    axs[4].grid(True, axis="y")
    axs[4].plot(x, df[p["CO2"]], label=p["CO2"])
    axs[4].plot([tmin, tmax], [lg.get("co2RefSpan", np.nan)] * 2, color=(0.8510, 0.3255, 0.0980), label="CO2 Span")
    axs[4].set_xlabel("Time (s)")
    axs[4].legend(loc="upper right")

    fig.tight_layout()
    out = "spanLimit_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_pems_quality_checks1(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)

    # Sample flow
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["sampleFlow"]], color="b")
    axs[0].set_ylabel(p["sampleFlow"])
    axs[0].set_title(figtitle)
    axs[0].set_ylim(2, 4)
    axs[0].set_yticks(np.arange(2.0, 4.01, 0.2))

    # Battery 1 and Battery 2 (right axis)
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["batt1Voltage"]], color="C0")
    ax1r = axs[1].twinx()
    ax1r.plot(x, df[p["batt2Voltage"]], color="C1")
    axs[1].set_ylim(0, 15); ax1r.set_ylim(0, 15)
    axs[1].set_ylabel(p["batt1Voltage"]); ax1r.set_ylabel(p["batt2Voltage"])

    # Number of DTCs
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["numOfDTC"]], color=(0.8510, 0.3255, 0.0980))
    axs[2].set_ylabel(p["numOfDTC"])

    # Block Temperature
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["blockT"]], color=(0.4667, 0.6745, 0.1882))
    axs[3].set_ylabel(p["blockT"])
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "qchek_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_pems_quality_checks2(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]], figtitle: str) -> str:
    p = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    x = df[p["time"]].to_numpy()

    fig, axs = plt.subplots(4, 1, figsize=(9.42, 9.82), sharex=True)

    # Sample Humidity with limit at 15%
    axs[0].grid(True, axis="y")
    axs[0].plot(x, df[p["sampleH"]], color="b")
    axs[0].plot([x[0], x[-1]], [15, 15], color=(0.3020, 0.7451, 0.9333), linestyle="--")
    axs[0].set_ylabel(p["sampleH"])
    axs[0].set_title(figtitle)
    axs[0].legend([p["sampleH"], "Sample Humidity Limit < 15%"], loc="upper left")

    # Sample Temperature
    axs[1].grid(True, axis="y")
    axs[1].plot(x, df[p["sampleT"]], color="C1")
    axs[1].set_ylabel(p["sampleT"])

    # Heated Filter Temperature
    axs[2].grid(True, axis="y")
    axs[2].plot(x, df[p["heatedFilterT"]], color=(0.8510, 0.3255, 0.0980))
    axs[2].set_ylabel(p["heatedFilterT"])

    # Power Distribution Faults
    axs[3].grid(True, axis="y")
    axs[3].plot(x, df[p["faults"]], color=(0.4667, 0.6745, 0.1882))
    axs[3].set_ylabel(p["faults"])
    axs[3].set_xlabel("Time (s)")

    fig.tight_layout()
    out = "qchekSam_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ------------------------- Example runner placeholder -------------------------
if __name__ == "__main__":
    # Example usage (requires your vehData, udp structures):
    # report_pems_ld_quality(setIdx, "LD_Quality_Report", vehData, udp)
    pass