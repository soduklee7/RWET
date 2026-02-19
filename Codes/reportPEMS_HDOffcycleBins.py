import os
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for script use
import matplotlib.pyplot as plt

from fpdf import FPDF


def reportPEMS_HDOffcycleBins(setIdx: int,
                                 filename: str,
                                 vehData: List[Dict[str, Any]],
                                 udp: List[Dict[str, Any]],
                                 binData: List[Dict[str, Any]]) -> None:
    """
    FPDF-based report generator for HD Offcycle Bins (translation from MATLAB).
    Creates a PDF with tables and figures similar to the original MATLAB report.

    Parameters:
      setIdx: dataset index (zero-based)
      filename: pdf filename (with or without .pdf)
      vehData: data structure with:
        - data: pandas DataFrame of time series
        - units: dict mapping column name -> unit string (optional)
        - scalarData: dict of scalar values
        - scalarUnits: dict of scalar units (optional)
        - scalarBinData: pandas DataFrame from bin calc (one row)
        - binData: pandas DataFrame with per-interval vectors
        - logData: dict: oem, model, my, dateTime, vehid, filename, testCycle, fuel, vin, notes, odo
      udp: configuration dict/list with pems mapping to column names
      binData: list of dicts from diesel bin calc: keys: time_avg, valid, mco2_norm, idx, bin
    """
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"

    pems = udp[setIdx]["pems"]
    df: pd.DataFrame = vehData[setIdx]["data"]
    units_map: Dict[str, str] = vehData[setIdx].get("units", {})
    scalar_data: Dict[str, Any] = vehData[setIdx].get("scalarData", {})
    scalar_units: Dict[str, str] = vehData[setIdx].get("scalarUnits", {})
    scalar_bin_df: pd.DataFrame = vehData[setIdx].get("scalarBinData", pd.DataFrame())
    bin_df: pd.DataFrame = vehData[setIdx].get("binData", pd.DataFrame())
    log_data: Dict[str, Any] = vehData[setIdx].get("logData", {})

    # Header title content
    oem = str(log_data.get("oem", ""))
    model = str(log_data.get("model", ""))
    my = str(log_data.get("my", ""))
    veh_model_str = f"{oem} {model} {my}".strip()
    header_title = f"NVFEL Laboratory:  PEMS Test Report:  {veh_model_str}"

    # Extract arrays from binData list-of-dicts
    bd_time_avg = np.array([d.get("time_avg", np.nan) for d in binData], dtype=float) if binData else np.array([])
    bd_valid = np.array([d.get("valid", 0) for d in binData], dtype=float) if binData else np.array([])
    bd_mco2_norm = np.array([d.get("mco2_norm", np.nan) for d in binData], dtype=float) if binData else np.array([])
    bd_bins = np.array([d.get("bin", 0) for d in binData], dtype=float) if binData else np.array([])
    bd_idx_pairs = [d.get("idx", [0, 0]) for d in binData] if binData else []

    # Prepare figures (saved as PNGs) to embed
    img_include = _plot_included_intervals(setIdx, vehData, udp)
    img_invalid = _plot_invalid_intervals(setIdx, vehData, udp, bd_time_avg, bd_valid)
    img_bin1_nox = _plot_bin1_nox(setIdx, vehData, udp)
    img_norm_co2 = _plot_norm_co2(setIdx, vehData, udp, bd_time_avg, bd_mco2_norm, bd_idx_pairs, bd_bins)
    img_bin2_nox = _plot_bin2_emission(setIdx, vehData, udp,
                                       mass_flow_col=pems["kNOxMassFlow"],
                                       mass_col_name="NOx_Mass_Bin2",
                                       brake_cu_col="NOx_BrakeSpec_Bin2_Cummulative",
                                       right_ylabel="NOx_BrakeSpec_Bin2_Cummulative (gm/hp*hr)")
    img_bin2_co = _plot_bin2_emission(setIdx, vehData, udp,
                                      mass_flow_col=pems["coMassFlow"],
                                      mass_col_name="CO_Mass_Bin2",
                                      brake_cu_col="CO_BrakeSpec_Bin2_Cummulative",
                                      right_ylabel="CO_BrakeSpec_Bin2_Cummulative (gm/hp*hr)")
    img_bin2_hc = _plot_bin2_emission(setIdx, vehData, udp,
                                      mass_flow_col=pems["hcMassFlow"],
                                      mass_col_name="HC_Mass_Bin2",
                                      brake_cu_col="HC_BrakeSpec_Bin2_Cummulative",
                                      right_ylabel="HC_BrakeSpec_Bin2_Cummulative (mg/hp*hr)")

    # Initialize FPDF (inches, Letter)
    pdf = PDF(header_title=header_title, unit="in", format="letter")
    pdf.set_auto_page_break(auto=True, margin=0.5)  # bottom margin area

    # Page 1 content
    pdf.add_page()
    pdf.ln(0.1)
    pdf_add_heading(pdf, "Test Information")
    pg1_tab1 = [
        ["Date and Time", str(log_data.get("dateTime", ""))],
        ["Vehicle Model", veh_model_str],
        ["Vehicle ID", str(log_data.get("vehid", ""))],
        ["File Name", str(log_data.get("filename", ""))],
    ]
    draw_table(pdf, pg1_tab1, align_center=False)

    pdf.ln(0.2)
    pdf_add_heading(pdf, "Vehicle and Cycle")
    # Distance string
    dist_mi_name = "Distance_Mile"
    dist_mi_val = scalar_data.get(dist_mi_name, np.nan)
    dist_mi_unit = scalar_units.get(dist_mi_name, "(mile)")
    cycle_distance_str = f"{dist_mi_val:10.2f} {dist_mi_unit}"
    # 3 rows x 5 columns equivalent layout
    pg1_tab2 = [
        ["Test Cycle", str(log_data.get("testCycle", "")), "", "Fuel", str(log_data.get("fuel", ""))],
        ["Cycle Distance", cycle_distance_str, "", "VIN", str(log_data.get("vin", ""))],
        ["Odometer", str(log_data.get("odo", "")), "", "Notes", str(log_data.get("notes", ""))],
    ]
    draw_table(pdf, pg1_tab2, align_center=False)

    pdf.ln(0.2)
    pdf_add_heading(pdf, "Test Cycle Mass Emissions")
    # Build 3 rows with 4 columns: label row, unit row, value row
    def get_scalar_val(name, default_unit="(gm/mile)"):
        return scalar_data.get(name, np.nan), scalar_units.get(name, default_unit)

    kNOx_val, kNOx_unit = get_scalar_val("kNOx_Gms_Per_Mile")
    co_val, co_unit = get_scalar_val("CO_Gms_Per_Mile")
    hc_val, hc_unit = get_scalar_val("HC_Gms_Per_Mile")
    co2_val, co2_unit = get_scalar_val("CO2_Gms_Per_Mile")

    pg1_tab3 = [
        ["NOx", "CO", "HC", "CO2"],
        [coalesce(kNOx_unit), coalesce(co_unit), coalesce(hc_unit), coalesce(co2_unit)],
        [fmt_float(kNOx_val, "%8.4f"), fmt_float(co_val, "%8.4f"),
         fmt_float(hc_val, "%8.4f"), fmt_float(co2_val, "%8.4f")],
    ]
    draw_table(pdf, pg1_tab3, align_center=True)

    pdf.ln(0.2)
    pdf_add_heading(pdf, "Particulate Emissions")
    # Placeholder table like MATLAB
    pg1_tab4 = [
        ["Filter Number", "(-)", "", "Total Mass/Dis", "(gm/mile)", ""],
        ["Pre-Weight", "(mg)", "", "Post-Weight", "(mg)", ""],
        ["Net Total Mass", "(mg)", "", "", "", ""],
    ]
    draw_table(pdf, pg1_tab4, align_center=True)

    pdf.ln(0.2)
    pdf_add_heading(pdf, "Fuel Economy")
    fe_val = scalar_data.get("Fuel_Economy", np.nan)
    fe_unit = scalar_units.get("Fuel_Economy", "(mpg)")
    pg1_tab5 = [["Fuel Economy"], [fe_unit], [f"{fe_val:8.2f}"]]
    draw_table(pdf, pg1_tab5, align_center=True, force_width=2.0)

    pdf.ln(0.2)
    pdf_add_heading(pdf, "Off-Cycle Emissions - Intervals")
    def get_scalar_bin_value(col_name: str, default=np.nan):
        try:
            if isinstance(scalar_bin_df, pd.DataFrame) and (col_name in scalar_bin_df.columns):
                return scalar_bin_df[col_name].iloc[0]
        except Exception:
            pass
        return default

    pg1_tab6 = [
        ["Total Intervals", get_scalar_bin_value("Number_Intervals")],
        ["Valid Intervals", get_scalar_bin_value("NumValid_Intervals")],
        ["Invalid Intervals", get_scalar_bin_value("NumInValid_Intervals")],
        ["Bin 1 Intervals", get_scalar_bin_value("NumBin1_Intervals")],
        ["Bin 2 Intervals", get_scalar_bin_value("NumBin2_Intervals")],
    ]
    draw_table(pdf, pg1_tab6, align_center=True)

    pdf.ln(0.2)
    pdf_add_heading(pdf, "Bin 1 NOx Emissions")
    nox_bin1 = get_scalar_bin_value("NOxMassFlow_Bin1")
    pg1_tab7 = [["NOx Bin 1"], ["(gm/hr)"], [fmt_float(nox_bin1, "%8.4f")]]
    draw_table(pdf, pg1_tab7, align_center=True, force_width=2.0)

    pdf.ln(0.2)
    pdf_add_heading(pdf, "Bin 2 NOx Emissions")
    nox_b2 = get_scalar_bin_value("NOxBrakeSpecific_Bin2")
    hc_b2 = get_scalar_bin_value("hcBrakeSpecific_Bin2")
    co_b2 = get_scalar_bin_value("coBrakeSpecific_Bin2")
    pg1_tab8 = [
        ["NOx Bin 2", "(mg/hp*hr)", fmt_float(nox_b2, "%8.4f")],
        ["HC Bin 2", "(mg/hp*hr)", fmt_float(hc_b2, "%8.4f")],
        ["PM Bin 2", "--", "--"],
        ["CO Bin 2", "(gm/hp*hr)", fmt_float(co_b2, "%8.4f")],
    ]
    draw_table(pdf, pg1_tab8, align_center=True)

    # Included Intervals page
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information")
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.2)
    pdf_add_heading(pdf, "Figure:  Included Intervals")
    pdf_image_center(pdf, img_include, w=7.5)  # height auto

    # Invalid Intervals page
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information")
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.2)
    pdf_add_heading(pdf, "Figure:  Invalid Intervals")
    pdf_image_center(pdf, img_invalid, w=7.5)

    # Bin 1 NOx page
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information")
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.2)
    pdf_add_heading(pdf, "Figure:  Bin 1 NOx")
    pdf_image_center(pdf, img_bin1_nox, w=7.5)

    # Normalized CO2 page
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information")
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.2)
    pdf_add_heading(pdf, "Figure:  Normalized CO2")
    pdf_image_center(pdf, img_norm_co2, w=7.5)

    # Bin 2 NOx page
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information")
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.2)
    pdf_add_heading(pdf, "Figure:  Bin 2 NOx")
    pdf_image_center(pdf, img_bin2_nox, w=7.5)

    # Bin 2 CO page
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information")
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.2)
    pdf_add_heading(pdf, "Figure:  Bin 2 CO")
    pdf_image_center(pdf, img_bin2_co, w=7.5)

    # Bin 2 HC page
    pdf.add_page()
    pdf_add_heading(pdf, "Test Information")
    header_table_pdf(pdf, log_data, veh_model_str)
    pdf.ln(0.2)
    pdf_add_heading(pdf, "Figure:  Bin 2 HC")
    pdf_image_center(pdf, img_bin2_hc, w=7.5)

    # Save PDF
    pdf.output(filename)


class PDF(FPDF):
    def __init__(self, header_title: str, unit: str = "in", format: str = "letter"):
        super().__init__(orientation="P", unit=unit, format=format)
        self.header_title = header_title
        # Margins to mimic MATLAB layout
        self.set_margins(left=0.5, top=0.25, right=0.5)
        self.alias_nb_pages()

    def header(self):
        # Horizontal rule
        width, height = self.w, self.h
        y_line = 0.5  # 0.5 in from top
        self.set_line_width(0.02)
        self.set_draw_color(0, 0, 0)
        self.line(0.5, y_line, width - 0.5, y_line)
        # Header text centered
        self.set_font("Helvetica", size=9)
        self.set_y(y_line + 0.05)
        self.cell(0, 0.2, self.header_title, border=0, ln=1, align="C")

    def footer(self):
        width = self.w
        y_line = 0.5  # 0.5 in from bottom
        self.set_y(-y_line - 0.2)  # position above footer line
        self.set_line_width(0.02)
        self.set_draw_color(0, 0, 0)
        self.line(0.5, self.h - y_line, width - 0.5, self.h - y_line)
        self.set_y(-y_line + 0.05)
        self.set_font("Helvetica", size=9)
        self.cell(0, 0.2, f"Page {self.page_no()}", align="C")


def pdf_add_heading(pdf: PDF, text: str):
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 0.3, text, ln=1, align="C")


def draw_table(pdf: PDF, data: List[List[Any]], align_center: bool = True,
               force_width: float = None, col_widths: List[float] = None):
    """
    Draw a simple table with borders similar to the MATLAB report style.
    - data: list of rows (each row is a list of strings/numbers)
    - align_center: centers text if True, left-aligns otherwise
    - force_width: if given, total table width in inches
    - col_widths: optional list specifying width for each column (in inches)
    """
    # Convert all cells to strings
    rows = [[coalesce(cell) for cell in row] for row in data]
    ncols = max(len(r) for r in rows)
    # Determine table width and column widths
    content_width = (pdf.w - pdf.l_margin - pdf.r_margin)
    table_width = force_width if force_width else content_width
    if col_widths is None:
        cw = table_width / ncols
        col_widths = [cw] * ncols
    table_width = sum(col_widths)
    # Center table horizontally
    x_start = pdf.l_margin + (content_width - table_width) / 2.0
    pdf.set_x(x_start)

    # Style
    pdf.set_draw_color(192, 192, 192)  # silver
    pdf.set_line_width(0.02)
    pdf.set_font("Helvetica", size=11)
    line_h = 0.28  # approx for 11pt in inches

    # Render rows
    for ridx, row in enumerate(rows):
        # Reset X for each row
        pdf.set_x(x_start)
        for cidx in range(ncols):
            text = row[cidx] if cidx < len(row) else ""
            align = "C" if align_center else "L"
            pdf.cell(col_widths[cidx], line_h, text, border=1, align=align)
        pdf.ln(line_h)


def header_table_pdf(pdf: PDF, log_data: Dict[str, Any], veh_model_str: str):
    data = [
        ["Date and Time", str(log_data.get("dateTime", ""))],
        ["Vehicle Model", veh_model_str],
        ["Vehicle ID", str(log_data.get("vehid", ""))],
        ["File Name", str(log_data.get("filename", ""))],
    ]
    draw_table(pdf, data, align_center=False)


def pdf_image_center(pdf: PDF, img_path: str, w: float):
    """
    Insert an image centered at current Y with given width (inches). Height is auto.
    """
    # Compute X to center image
    content_width = (pdf.w - pdf.l_margin - pdf.r_margin)
    x = pdf.l_margin + (content_width - w) / 2.0
    pdf.image(img_path, x=x, w=w)
    pdf.ln(0.2)


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


# ------------------------- Plotting helpers (matplotlib) -------------------------

def _plot_included_intervals(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]]) -> str:
    pems = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    units = vehData[setIdx].get("units", {})
    x = df[pems["time"]].to_numpy()
    fig, axs = plt.subplots(6, 1, figsize=(9.42, 9.82), sharex=True)
    lw = 3

    axs[0].plot(x, df[pems["includeEngSpeed"]], linewidth=lw, color="b")
    axs[0].set_ylabel(units.get(pems["includeEngSpeed"], pems["includeEngSpeed"]))
    ax0r = axs[0].twinx(); ax0r.grid(True)
    ax0r.plot(x, df[pems["engineSpeed"]], linewidth=1.5, color="k")
    ax0r.set_ylabel(units.get(pems["engineSpeed"], pems["engineSpeed"]))

    axs[1].plot(x, df[pems["includeRegen"]], linewidth=lw, color="b")
    axs[1].set_ylabel(units.get(pems["includeRegen"], pems["includeRegen"]))
    ax1r = axs[1].twinx(); ax1r.grid(True)
    ax1r.plot(x, df[pems["regenStatus"]], linewidth=1.5, color="k")
    ax1r.set_ylabel(units.get(pems["regenStatus"], pems["regenStatus"]))

    axs[2].plot(x, df[pems["includeTmax"]], linewidth=lw, color="b")
    axs[2].set_ylabel(units.get(pems["includeTmax"], pems["includeTmax"]))
    ax2r = axs[2].twinx(); ax2r.grid(True)
    ax2r.plot(x, df[pems["tMaxLimit"]], linewidth=1.5, color="k")
    ax2r.plot(x, df[pems["ambientAirT"]], linewidth=1.5, color=(0.1608, 0.4784, 0.0431))
    ax2r.legend([units.get(pems["includeTmax"], pems["includeTmax"]),
                 units.get(pems["tMaxLimit"], pems["tMaxLimit"]),
                 units.get(pems["ambientAirT"], pems["ambientAirT"])],
                loc="upper right")

    axs[3].plot(x, df[pems["includeAmbient5C"]], linewidth=lw, color="b")
    axs[3].set_ylabel(units.get(pems["includeAmbient5C"], pems["includeAmbient5C"]))
    ax3r = axs[3].twinx()
    ax3r.plot(x, df[pems["ambientTLimit"]], linewidth=1.5, color="k")
    ax3r.plot(x, df[pems["ambientAirT"]], linewidth=1.5, color=(0.1608, 0.4784, 0.0431))
    ax3r.set_ylabel(units.get(pems["ambientTLimit"], pems["ambientTLimit"]))
    ax3r.legend([units.get(pems["includeAmbient5C"], pems["includeAmbient5C"]),
                 units.get(pems["ambientTLimit"], pems["ambientTLimit"]),
                 units.get(pems["ambientAirT"], pems["ambientAirT"])],
                loc="upper right")

    axs[4].plot(x, df[pems["includeAltitude"]], linewidth=lw, color="b")
    axs[4].set_ylabel(units.get(pems["includeAltitude"], pems["includeAltitude"]))
    ax4r = axs[4].twinx(); ax4r.grid(True)
    ax4r.plot(x, df[pems["altitudeLimit"]], linewidth=1.5, color="k")
    ax4r.plot(x, df[pems["altitudeFt"]], linewidth=1.5, color=(0.1608, 0.4784, 0.0431))
    ax4r.set_ylabel(units.get(pems["altitudeLimit"], pems["altitudeLimit"]))
    ax4r.legend([units.get(pems["includeAltitude"], pems["includeAltitude"]),
                 units.get(pems["altitudeLimit"], pems["altitudeLimit"]),
                 units.get(pems["altitudeFt"], pems["altitudeFt"])],
                loc="upper right")

    axs[5].plot(x, df[pems["includeTotal"]], linewidth=lw, color="b")
    axs[5].set_xlabel(units.get(pems["time"], "Time (s)"))
    axs[5].set_ylabel(units.get(pems["includeTotal"], pems["includeTotal"]))

    fig.tight_layout()
    out = "include_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_invalid_intervals(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]],
                            time_avg: np.ndarray, valid_vec: np.ndarray) -> str:
    pems = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    units = vehData[setIdx].get("units", {})
    x = df[pems["time"]].to_numpy()

    fig, axs = plt.subplots(2, 1, figsize=(9.42, 9.82), sharex=False)
    axs[0].plot(x, df[pems["includeTotal"]], linewidth=3, color="b")
    axs[0].set_ylabel(units.get(pems["includeTotal"], pems["includeTotal"]))

    axs[1].plot(time_avg, valid_vec, color="k")
    axs[1].set_ylabel("Invalid_Intervals")
    axs[1].set_xlabel(units.get(pems["time"], "Time (s)"))

    fig.tight_layout()
    out = "incTotal_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_bin1_nox(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]]) -> str:
    pems = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    units = vehData[setIdx].get("units", {})
    x = df[pems["time"]].to_numpy()

    fig, axs = plt.subplots(3, 1, figsize=(9.42, 9.82), sharex=True)
    ax1 = axs[0]
    ax1.plot(x, df[pems["speed"]], color="b")
    ax1.set_ylabel("Vehicle Speed (mph)")
    ax1.grid(True, axis="y")
    ax1r = ax1.twinx()
    ax1r.plot(x, df[pems["engineSpeed"]], color=".7")
    ax1r.set_ylabel("Engine Speed (rpm)")

    axs[1].plot(x, df[pems["kNOxMassFlow"]])
    axs[1].set_ylabel(units.get(pems["kNOxMassFlow"], pems["kNOxMassFlow"]))

    bin_df: pd.DataFrame = vehData[setIdx]["binData"]
    tavg = bin_df["Time_BinAvg"].to_numpy()
    nmb1 = bin_df["NOx_Mass_Bin1"].to_numpy()
    axs[2].plot(tavg, nmb1)
    axs[2].set_ylabel("NOx_Mass_Bin1 (gm)")
    axs[2].grid(True, axis="y")
    ax2r = axs[2].twinx()
    ax2r.plot(tavg, bin_df["NOxMassFlow_Bin1_Cummulative"].to_numpy(), color="orange")
    ax2r.set_ylabel("NOxMassFlow_Bin1_Cummulative (gm/hr)")
    axs[2].set_xlabel(units.get(pems["time"], "Time (s)"))

    fig.tight_layout()
    out = "bin1Nox_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_norm_co2(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]],
                   time_avg: np.ndarray, mco2_norm: np.ndarray,
                   idx_pairs: List[List[int]], bins_vec: np.ndarray) -> str:
    pems = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    units = vehData[setIdx].get("units", {})
    x = df[pems["time"]].to_numpy()

    fig, axs = plt.subplots(3, 1, figsize=(9.42, 9.82), sharex=True)

    ax1 = axs[0]
    ax1r = ax1.twinx()
    ax1r.plot(x, df[pems["engineSpeed"]], color=".7")
    ax1r.set_ylabel("Engine Speed (rpm)")
    ax1.plot(x, df[pems["speed"]], color="b")
    ax1.set_ylabel("Vehicle Speed (mph)")
    ax1.grid(True, axis="y")

    axs[1].plot(x, df[pems["co2MassFlow"]])
    axs[1].set_ylabel(units.get(pems["co2MassFlow"], pems["co2MassFlow"]))

    axs[2].plot(time_avg, mco2_norm, color=(0.4941, 0.1843, 0.5569))
    axs[2].set_ylim(0, 80)

    # 6% limit across interval time span
    if idx_pairs:
        tmin = x[min(pair[0] for pair in idx_pairs)]
        tmax = x[max(pair[1] for pair in idx_pairs)]
    else:
        tmin = x[0] if len(x) else 0
        tmax = x[-1] if len(x) else 0
    axs[2].plot([tmin, tmax], [6, 6], color=(0.8510, 0.3255, 0.0980), linewidth=2)
    axs[2].set_ylabel("Normalized CO2 (%)")
    axs[2].set_xlabel(units.get(pems["time"], "Time (s)"))

    ax2r = axs[2].twinx()
    ax2r.plot(time_avg, bins_vec, color=(0.4667, 0.6745, 0.1882))
    ax2r.set_ylim(-10, 4)
    ax2r.set_ylabel("Bin Number", color=(0.4667, 0.6745, 0.1882))

    fig.tight_layout()
    out = "normCO2_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_bin2_emission(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]],
                        mass_flow_col: str,
                        mass_col_name: str,
                        brake_cu_col: str,
                        right_ylabel: str) -> str:
    pems = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    units = vehData[setIdx].get("units", {})
    x = df[pems["time"]].to_numpy()
    bin_df: pd.DataFrame = vehData[setIdx]["binData"]

    fig, axs = plt.subplots(3, 1, figsize=(9.42, 9.82), sharex=True)
    ax1 = axs[0]
    ax1.plot(x, df[pems["speed"]], color="b")
    ax1.set_ylabel("Vehicle Speed (mph)")
    ax1.grid(True, axis="y")
    ax1r = ax1.twinx()
    ax1r.plot(x, df[pems["engineSpeed"]], color=".7")
    ax1r.set_ylabel("Engine Speed (rpm)")

    axs[1].plot(x, df[mass_flow_col])
    axs[1].set_ylabel(units.get(mass_flow_col, mass_flow_col))
    axs[1].grid(True, axis="y")

    tavg = bin_df["Time_BinAvg"].to_numpy()
    axs[2].plot(tavg, bin_df[mass_col_name].to_numpy())
    axs[2].set_ylabel(f"{mass_col_name} (gm)")
    axs[2].grid(True, axis="y")
    ax2r = axs[2].twinx()
    ax2r.plot(tavg, bin_df[brake_cu_col].to_numpy())
    ax2r.set_ylabel(right_ylabel)
    axs[2].set_xlabel(units.get(pems["time"], "Time (s)"))

    fig.tight_layout()
    out = "bin2NOx_image.png"
    if "CO_BrakeSpec" in right_ylabel:
        out = "bin2CO_image.png"
    elif "HC_BrakeSpec" in right_ylabel:
        out = "bin2HC_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ------------------------- Example runner placeholder -------------------------
if __name__ == "__main__":
    # Example usage:
    # report_pems_hd_offcycle_bins(setIdx, "HD_Offcycle_Bins_Report", vehData, udp, binData)
    pass