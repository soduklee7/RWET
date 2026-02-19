import os
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for script use
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Table,
    TableStyle,
    Spacer,
    Image,
    PageBreak,
)

# pip install reportlab fpdf matplotlib pandas numpy

def report_pems_hd_offcycle_bins(setIdx: int,
                                 filename: str,
                                 vehData: List[Dict[str, Any]],
                                 udp: List[Dict[str, Any]],
                                 vehData: List[Dict[str, Any]]) -> None:
    """
    Python translation of reportPEMS_HDOffcycleBins.m.
    Creates a PDF report with tables and figures similar to the MATLAB report.

    Parameters:
      setIdx: dataset index (zero-based)
      filename: pdf filename (with or without .pdf)
      vehData: data structure described in assumptions
      udp: configuration structure with pems key map
      vehData: list of dicts from diesel bin calc. Keys expected:
                time_avg, valid, mco2_norm, idx (start,end), bin
    """
    # Normalize filename
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

    # ---------- Helpers
    def get_unit(col: str) -> str:
        return units_map.get(col, "")

    def get_series(col: str) -> Tuple[np.ndarray, str]:
        vals = df[col].to_numpy()
        unit = get_unit(col)
        # ylabel: prefer unit string if present; fallback to column name
        ylab = unit if unit else col
        return vals, ylab

    def get_time() -> Tuple[np.ndarray, str]:
        x = df[pems["time"]].to_numpy()
        xlab = get_unit(pems["time"])
        xlab = xlab if xlab else "Time (s)"
        return x, xlab

    def fmt_float(val: Any, fmt: str = "%8.4f") -> str:
        try:
            return fmt % float(val)
        except Exception:
            return str(val)

    # Fallback units for scalarBinData columns (if you didn't store units)
    scalar_bin_units_default = {
        "NOxMassFlow_Bin1": "(gm/hr)",
        "NOxBrakeSpecific_Bin2": "(mg/hp*hr)",
        "hcBrakeSpecific_Bin2": "(mg/hp*hr)",
        "coBrakeSpecific_Bin2": "(gm/hp*hr)",
    }

    # Extract vehData arrays from list-of-dicts
    bd_time_avg = np.array([d.get("time_avg", np.nan) for d in vehData], dtype=float)
    bd_valid = np.array([d.get("valid", 0) for d in vehData], dtype=float)
    bd_mco2_norm = np.array([d.get("mco2_norm", np.nan) for d in vehData], dtype=float)
    bd_bins = np.array([d.get("bin", 0) for d in vehData], dtype=float)
    bd_idx_pairs = [d.get("idx", [0, 0]) for d in vehData]
    if len(bd_idx_pairs) > 0:
        min_idx = min(pair[0] for pair in bd_idx_pairs)
        max_idx = max(pair[1] for pair in bd_idx_pairs)
    else:
        min_idx, max_idx = 0, 0

    # Veh model string and header title
    oem = str(log_data.get("oem", ""))
    model = str(log_data.get("model", ""))
    my = str(log_data.get("my", ""))
    veh_model_str = f"{oem} {model} {my}".strip()
    header_title = f"NVFEL Laboratory:  PEMS Test Report:  {veh_model_str}"

    # ---------- ReportLab document with header/footer
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Heading2Center", parent=styles["Heading2"], alignment=1))
    styles.add(ParagraphStyle(name="NormalCenter", parent=styles["Normal"], alignment=1))

    LEFT_MARGIN = 0.5 * inch
    RIGHT_MARGIN = 0.5 * inch
    TOP_MARGIN = 0.25 * inch
    BOTTOM_MARGIN = 0.0 * inch

    doc = BaseDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )

    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin + 0.5 * inch,          # leave footer area
        doc.width,
        doc.height - 1.0 * inch,                # leave header+footer areas
        id="normal",
        showBoundary=0,
    )

    def on_page(canvas_, doc_):
        # Header line and centered header title
        canvas_.saveState()
        width, height = letter
        # Header rule
        y_header_line = height - 0.5 * inch
        canvas_.setStrokeColor(colors.black)
        canvas_.setLineWidth(0.5)
        canvas_.line(0.5 * inch, y_header_line, width - 0.5 * inch, y_header_line)
        # Header text
        canvas_.setFont("Helvetica", 9)
        canvas_.drawCentredString(width / 2.0, y_header_line + 0.15 * inch, header_title)

        # Footer rule and page number centered
        y_footer_line = 0.5 * inch
        canvas_.line(0.5 * inch, y_footer_line, width - 0.5 * inch, y_footer_line)
        canvas_.setFont("Helvetica", 9)
        canvas_.drawCentredString(width / 2.0, y_footer_line - 0.2 * inch, f"Page {doc_.page}")
        canvas_.restoreState()

    template = PageTemplate(frames=[frame], onPage=on_page)
    doc.addPageTemplates([template])

    flow: List[Any] = []

    def heading2(text: str):
        flow.append(Paragraph(text, styles["Heading2Center"]))

    def mk_table(data: List[List[str]], col_widths=None, table_width="full", align_center=True):
        t = Table(data, colWidths=col_widths)
        ts = TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.silver),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.silver),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
        if align_center:
            ts.add("ALIGN", (0, 0), (-1, -1), "CENTER")
        t.setStyle(ts)
        return t

    def header_table_flowable():
        # “Test Information” header table used multiple times
        data = [
            ["Date and Time", str(log_data.get("dateTime", ""))],
            ["Vehicle Model", veh_model_str],
            ["Vehicle ID", str(log_data.get("vehid", ""))],
            ["File Name", str(log_data.get("filename", ""))],
        ]
        return mk_table(data, align_center=False)

    # -------------------- Page 1, Table 1 - Test Information (Tf)
    heading2("Test Information")
    pg1_tab1 = [
        ["Date and Time", str(log_data.get("dateTime", ""))],
        ["Vehicle Model", veh_model_str],
        ["Vehicle ID", str(log_data.get("vehid", ""))],
        ["File Name", str(log_data.get("filename", ""))],
    ]
    flow.append(mk_table(pg1_tab1, align_center=False))
    flow.append(Spacer(0, 0.15 * inch))

    # -------------------- Page 1, Table 2 - Vehicle and Cycle (Vc)
    heading2("Vehicle and Cycle")
    # Cycle Distance string with units
    dist_mi_name = "Distance_Mile"  # match scalarData key
    dist_mi_val = scalar_data.get(dist_mi_name, np.nan)
    dist_mi_unit = scalar_units.get(dist_mi_name, "(mile)")
    cycle_distance_str = f"{dist_mi_val:10.2f} {dist_mi_unit}"

    pg1_tab2 = [
        ["Test Cycle", str(log_data.get("testCycle", ""))],
        ["Cycle Distance", cycle_distance_str],
        ["Odometer", str(log_data.get("odo", ""))],
        [" ", " "],  # blank col #3
        ["Fuel", str(log_data.get("fuel", ""))],
        ["VIN", str(log_data.get("vin", ""))],
        ["Notes", str(log_data.get("notes", ""))],
    ]
    # Render as a 3x5 grid similar to MATLAB layout
    pg1_tab2_data = [
        [pg1_tab2[0][0], pg1_tab2[0][1], " ", "Fuel", str(log_data.get("fuel", ""))],
        [pg1_tab2[1][0], pg1_tab2[1][1], " ", "VIN", str(log_data.get("vin", ""))],
        [pg1_tab2[2][0], pg1_tab2[2][1], " ", "Notes", str(log_data.get("notes", ""))],
    ]
    flow.append(mk_table(pg1_tab2_data, align_center=False))
    flow.append(Spacer(0, 0.15 * inch))

    # -------------------- Page 1, Table 3 - Mass Emissions (Me)
    heading2("Test Cycle Mass Emissions")
    # Names expected to match your pems_data_calc outputs
    nox_name = "kNOx_Gms_Per_Mile"
    co_name = "CO_Gms_Per_Mile"
    hc_name = "HC_Gms_Per_Mile"
    co2_name = "CO2_Gms_Per_Mile"

    nox_unit = scalar_units.get(nox_name, "(gm/mile)")
    co_unit = scalar_units.get(co_name, "(gm/mile)")
    hc_unit = scalar_units.get(hc_name, "(gm/mile)")
    co2_unit = scalar_units.get(co2_name, "(gm/mile)")
    nox_val = scalar_data.get(nox_name, np.nan)
    co_val = scalar_data.get(co_name, np.nan)
    hc_val = scalar_data.get(hc_name, np.nan)
    co2_val = scalar_data.get(co2_name, np.nan)

    pg1_tab3 = [
        ["NOx", coalesce(nox_unit := nox_unit), fmt_float(nox_val, "%8.4f")],
        ["CO", coalesce(co_unit := co_unit), fmt_float(co_val, "%8.4f")],
        ["HC", coalesce(hc_unit := hc_unit), fmt_float(hc_val, "%8.4f")],
        ["CO2", coalesce(co2_unit := co2_unit), fmt_float(co2_val, "%8.4f")],
    ]
    flow.append(mk_table(pg1_tab3))
    flow.append(Spacer(0, 0.15 * inch))

    # -------------------- Page 1, Table 4 - Particulate Emissions (Pe)
    heading2("Particulate Emissions")
    pg1_tab4 = [
        ["Filter Number", "(-)", " ", "Total Mass/Dis", "(gm/mile)", " "],
        ["Pre-Weight", "(mg)", " ", "Post-Weight", "(mg)", " "],
        ["Net Total Mass", "(mg)", " ", " ", " ", " "],
    ]
    flow.append(mk_table(pg1_tab4))
    flow.append(Spacer(0, 0.15 * inch))

    # -------------------- Page 1, Table 5 - Fuel Economy (Fe)
    heading2("Fuel Economy")
    fe_name = "Fuel_Economy"
    fe_val = scalar_data.get(fe_name, np.nan)
    fe_unit = scalar_units.get(fe_name, "(mpg)")
    pg1_tab5 = [["Fuel Economy"], [fe_unit], [f"{fe_val:8.2f}"]]
    flow.append(mk_table(pg1_tab5, col_widths=[2 * inch]))
    flow.append(Spacer(0, 0.15 * inch))

    # ---------- Page 1, Table 6 - Off-Cycle Emissions: Intervals (Int)
    heading2("Off-Cycle Emissions - Intervals")
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
    flow.append(mk_table(pg1_tab6))
    flow.append(Spacer(0, 0.15 * inch))

    # -------------------- Page 1, Table 7 - Bin 1 NOx Emissions
    heading2("Bin 1 NOx Emissions")
    nox_bin1 = get_scalar_bin_value("NOxMassFlow_Bin1")
    nox_bin1_unit = "(gm/hr)"
    pg1_tab7 = [["NOx Bin 1"], [nox_bin1_unit], [fmt_float(nox_bin1, "%8.4f")]]
    flow.append(mk_table(pg1_tab7, col_widths=[2 * inch]))
    flow.append(Spacer(0, 0.15 * inch))

    # -------------------- Page 1, Table 8 - Bin 2 Emissions
    heading2("Bin 2 NOx Emissions")
    nox_b2 = get_scalar_bin_value("NOxBrakeSpecific_Bin2")
    hc_b2 = get_scalar_bin_value("hcBrakeSpecific_Bin2")
    co_b2 = get_scalar_bin_value("coBrakeSpecific_Bin2")
    pg1_tab8 = [
        ["NOx Bin 2", "(mg/hp*hr)", fmt_float(nox_b2, "%8.4f")],
        ["HC Bin 2", "(mg/hp*hr)", fmt_float(hc_b2, "%8.4f")],
        ["PM Bin 2", "--", "--"],
        ["CO Bin 2", "(gm/hp*hr)", fmt_float(co_b2, "%8.4f")],
    ]
    flow.append(mk_table(pg1_tab8))
    flow.append(PageBreak())

    # -------------------- Figure Set 1: Included Intervals
    heading2("Test Information")
    flow.append(header_table_flowable())
    heading2("Figure:  Included Intervals")
    img1 = _plot_included_intervals(setIdx, vehData, udp)
    flow.append(Image(img1, width=7.5 * inch, height=7.75 * inch))
    flow.append(PageBreak())

    # -------------------- Figure Set 2: Invalid Intervals
    heading2("Test Information")
    flow.append(header_table_flowable())
    heading2("Figure:  Invalid Intervals")
    img2 = _plot_invalid_intervals(setIdx, vehData, udp, bd_time_avg, bd_valid)
    flow.append(Image(img2, width=7.5 * inch, height=8.0 * inch))
    flow.append(PageBreak())

    # -------------------- Figure Set 3: Bin 1 NOx
    heading2("Test Information")
    flow.append(header_table_flowable())
    heading2("Figure:  Bin 1 NOx")
    img3 = _plot_bin1_nox(setIdx, vehData, udp)
    flow.append(Image(img3, width=7.5 * inch, height=8.0 * inch))
    flow.append(PageBreak())

    # -------------------- Figure Set 4: Normalized CO2
    heading2("Test Information")
    flow.append(header_table_flowable())
    heading2("Figure:  Normalized CO2")
    img4 = _plot_norm_co2(setIdx, vehData, udp, bd_time_avg, bd_mco2_norm, bd_idx_pairs, bd_bins)
    flow.append(Image(img4, width=7.5 * inch, height=8.0 * inch))
    flow.append(PageBreak())

    # -------------------- Figure Set 5: Bin 2 NOx
    heading2("Test Information")
    flow.append(header_table_flowable())
    heading2("Figure:  Bin 2 NOx")
    img5 = _plot_bin2_emission(setIdx, vehData, udp,
                               mass_flow_col=pems["kNOxMassFlow"],
                               mass_col_name="NOx_Mass_Bin2",
                               brake_cu_col="NOx_BrakeSpec_Bin2_Cummulative",
                               right_ylabel="NOx_BrakeSpec_Bin2_Cummulative (gm/hp*hr)")
    flow.append(Image(img5, width=7.5 * inch, height=8.0 * inch))
    flow.append(PageBreak())

    # -------------------- Figure Set 6: Bin 2 CO
    heading2("Test Information")
    flow.append(header_table_flowable())
    heading2("Figure:  Bin 2 CO")
    img6 = _plot_bin2_emission(setIdx, vehData, udp,
                               mass_flow_col=pems["coMassFlow"],
                               mass_col_name="CO_Mass_Bin2",
                               brake_cu_col="CO_BrakeSpec_Bin2_Cummulative",
                               right_ylabel="CO_BrakeSpec_Bin2_Cummulative (gm/hp*hr)")
    flow.append(Image(img6, width=7.5 * inch, height=8.0 * inch))
    flow.append(PageBreak())

    # -------------------- Figure Set 7: Bin 2 HC
    heading2("Test Information")
    flow.append(header_table_flowable())
    heading2("Figure:  Bin 2 HC")
    img7 = _plot_bin2_emission(setIdx, vehData, udp,
                               mass_flow_col=pems["hcMassFlow"],
                               mass_col_name="HC_Mass_Bin2",
                               brake_cu_col="HC_BrakeSpec_Bin2_Cummulative",
                               right_ylabel="HC_BrakeSpec_Bin2_Cummulative (mg/hp*hr)")
    flow.append(Image(img7, width=7.5 * inch, height=8.0 * inch))

    # Build PDF
    doc.build(flow)


def _plot_included_intervals(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]]) -> str:
    pems = udp[setIdx]["pems"]
    df = vehData[setIdx]["data"]
    units = vehData[setIdx].get("units", {})
    x = df[pems["time"]].to_numpy()
    # Figure
    fig, axs = plt.subplots(6, 1, figsize=(9.42, 9.82), sharex=True)
    lw = 3

    # 1: includeEngSpeed + engineSpeed
    axs[0].plot(x, df[pems["includeEngSpeed"]], linewidth=lw, color="b")
    axs[0].set_ylabel(units.get(pems["includeEngSpeed"], pems["includeEngSpeed"]))
    ax0r = axs[0].twinx()
    ax0r.grid(True)
    ax0r.plot(x, df[pems["engineSpeed"]], linewidth=1.5, color="k")
    ax0r.set_ylabel(units.get(pems["engineSpeed"], pems["engineSpeed"]))

    # 2: includeRegen + regenStatus
    axs[1].plot(x, df[pems["includeRegen"]], linewidth=lw, color="b")
    axs[1].set_ylabel(units.get(pems["includeRegen"], pems["includeRegen"]))
    ax1r = axs[1].twinx(); ax1r.grid(True)
    ax1r.plot(x, df[pems["regenStatus"]], linewidth=1.5, color="k")
    ax1r.set_ylabel(units.get(pems["regenStatus"], pems["regenStatus"]))

    # 3: includeTmax + tMaxLimit + ambientAirT
    axs[2].plot(x, df[pems["includeTmax"]], linewidth=lw, color="b")
    axs[2].set_ylabel(units.get(pems["includeTmax"], pems["includeTmax"]))
    ax2r = axs[2].twinx(); ax2r.grid(True)
    ax2r.plot(x, df[pems["tMaxLimit"]], linewidth=1.5, color="k")
    ax2r.plot(x, df[pems["ambientAirT"]], linewidth=1.5, color=(0.1608, 0.4784, 0.0431))
    ax2r.legend([units.get(pems["includeTmax"], pems["includeTmax"]),
                 units.get(pems["tMaxLimit"], pems["tMaxLimit"]),
                 units.get(pems["ambientAirT"], pems["ambientAirT"])],
                loc="upper right")

    # 4: includeAmbient5C + ambientTLimit + ambientAirT
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

    # 5: includeAltitude + altitudeLimit + altitudeFt
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

    # 6: includeTotal
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
    # 1: speed + engine speed
    ax1 = axs[0]
    ax1.plot(x, df[pems["speed"]], color="b")
    ax1.set_ylabel("Vehicle Speed (mph)")
    ax1.grid(True, axis="y")
    ax1r = ax1.twinx()
    ax1r.plot(x, df[pems["engineSpeed"]], color=".7")
    ax1r.set_ylabel("Engine Speed (rpm)")

    # 2: kNOx mass flow
    axs[1].plot(x, df[pems["kNOxMassFlow"]])
    axs[1].set_ylabel(units.get(pems["kNOxMassFlow"], pems["kNOxMassFlow"]))

    # 3: NOx Mass Bin1 and cumulative NOx mass flow
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

    # 1: speed and engine speed
    ax1 = axs[0]
    ax1r = ax1.twinx()
    ax1r.plot(x, df[pems["engineSpeed"]], color=".7")
    ax1r.set_ylabel("Engine Speed (rpm)")
    ax1.plot(x, df[pems["speed"]], color="b")
    ax1.set_ylabel("Vehicle Speed (mph)")
    ax1.grid(True, axis="y")

    # 2: CO2 mass flow
    axs[1].plot(x, df[pems["co2MassFlow"]])
    axs[1].set_ylabel(units.get(pems["co2MassFlow"], pems["co2MassFlow"]))

    # 3: Normalized CO2 and bin number
    axs[2].plot(time_avg, mco2_norm, color=(0.4941, 0.1843, 0.5569))
    axs[2].set_ylim(0, 80)
    # 6% limit line
    if len(idx_pairs) > 0:
        tmin = x[min(pair[0] for pair in idx_pairs)]
        tmax = x[max(pair[1] for pair in idx_pairs)]
    else:
        tmin, tmax = (x[0] if len(x) else 0), (x[-1] if len(x) else 0)
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

    # 1: speed + engine speed
    ax1 = axs[0]
    ax1.plot(x, df[pems["speed"]], color="b")
    ax1.set_ylabel("Vehicle Speed (mph)")
    ax1.grid(True, axis="y")
    ax1r = ax1.twinx()
    ax1r.plot(x, df[pems["engineSpeed"]], color=".7")
    ax1r.set_ylabel("Engine Speed (rpm)")

    # 2: mass flow
    axs[1].plot(x, df[mass_flow_col])
    axs[1].set_ylabel(units.get(mass_flow_col, mass_flow_col))
    axs[1].grid(True, axis="y")

    # 3: Bin 2 mass and cumulative brake-specific
    tavg = bin_df["Time_BinAvg"].to_numpy()
    axs[2].plot(tavg, bin_df[mass_col_name].to_numpy())
    axs[2].set_ylabel(f"{mass_col_name} (gm)")
    axs[2].grid(True, axis="y")
    ax2r = axs[2].twinx()
    ax2r.plot(tavg, bin_df[brake_cu_col].to_numpy())
    ax2r.set_ylabel(right_ylabel)
    axs[2].set_xlabel(units.get(pems["time"], "Time (s)"))

    fig.tight_layout()
    # Choose output name based on right_ylabel
    if "NOx" in right_ylabel:
        out = "bin2NOx_image.png"
    elif "CO_BrakeSpec" in right_ylabel:
        out = "bin2CO_image.png"
    else:
        out = "bin2HC_image.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def coalesce(val: Any, default: str = "") -> str:
    try:
        if val is None:
            return default
        if isinstance(val, str):
            return val
        return str(val)
    except Exception:
        return default


if __name__ == "__main__":
    # Example usage placeholder (requires you to populate vehData, udp, vehData)
    # report_pems_hd_offcycle_bins(setIdx, "HD_Offcycle_Bins_Report", vehData, udp, vehData)
    pass