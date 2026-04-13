# -*- coding: utf-8 -*-
"""
EPA MAW Emissions Analysis and Shift-Day Emissions
Python port of the provided MATLAB script (40 CFR 1036.530 logic).

Requirements:
- pandas
- numpy
- matplotlib

Usage outline:
- Prepare a pandas DataFrame 'raw' with your test data (one row per second).
- Build a config dict 'udp' with keys:
    udp = {
        "bins": {"eco2fcl": 507.0, "pmax": 505.0},  # example
        "log":  {"fuel": "Diesel"},                 # or "Gasoline"
    }
- Call: df, results = run_emissions_analysis(raw, udp, MPG=None, fuel_density=None)
- For Diesel: results is a dict with summary_df, windows_df, sub_interval_df, compliance_df
- For Gasoline: results is a dict with final_emissions and sub_interval_df
"""

import numpy as np
import pandas as pd
import re
from pathlib import Path

import traceback
import matplotlib.pyplot as plt

# pip install pypdf
import io
import os
import tempfile
from pypdf import PdfReader, PdfWriter
# from PyPDF2 import PdfReader, PdfWriter
from matplotlib.backends.backend_pdf import PdfPages
from typing import Union, Optional, Sequence, Any   
from reportPEMS_HDOffcycleBins import reportPEMS_HDOffcycleBins
# pip install hdf5storage
import hdf5storage

def load_mat_v73(path):
    # Returns a nested dict similar to loadmat behavior
    return hdf5storage.loadmat(path)
# ---------------------------
# Helper utilities
# ---------------------------

def to_numeric(col):
    """Convert a column-like to a numeric pandas Series (floats), preserving length."""
    if col is None or isinstance(col, (list, tuple, np.ndarray, pd.Series)):
        s = pd.Series(col)
    else:
        try:
            s = pd.Series(col)
        except Exception:
            return None
    try:
        return pd.to_numeric(s, errors="coerce")
    except Exception:
        # Best-effort casting
        return pd.Series(pd.to_numeric(s.astype(str), errors="coerce"))


def normalize_colname(name):
    return str(name).strip().lower()


def get_column(df, candidates):
    """
    Return the first matching column by exact name (case-insensitive) among candidates.
    If none found, returns None.
    """
    if df is None or df.empty:
        return None
    names = [normalize_colname(c) for c in df.columns]
    for c in candidates:
        c_norm = normalize_colname(c)
        for idx, n in enumerate(names):
            if n == c_norm:
                return df.iloc[:, idx]
    return None


def find_col_contains(df, must_have_substrings):
    """
    Return first column whose name contains all provided substrings (case-insensitive).
    must_have_substrings: list of substrings (e.g., ["LimitAdjusted", "_LAT"])
    Returns Series or None.
    """
    names = list(df.columns)
    if not names:
        return None
    subs = [normalize_colname(s) for s in must_have_substrings]
    for col in names:
        lc = normalize_colname(col)
        if all(s in lc for s in subs):
            return df[col]
    return None

def grams_to_gallons(mass_g, fuel_or_density=None):
    """
    Convert fuel mass (grams) to US gallons.
    fuel_or_density can be:
      - numeric: density in kg/L
      - string: 'gasoline','e10','e85','diesel'
    Default gasoline E0 (0.745 kg/L).
    """
    if fuel_or_density is None:
        rho = 0.745
    elif isinstance(fuel_or_density, (int, float)):
        rho = float(fuel_or_density)
    else:
        kind = str(fuel_or_density).strip().lower()
        if kind in ("gasoline", "petrol", "e0"):
            rho = 0.745
        elif kind == "e10":
            rho = 0.750
        elif kind == "e85":
            rho = 0.785
        elif kind in ("diesel", "d2"):
            rho = 0.832
        else:
            raise ValueError("Unknown fuel type. Provide density (kg/L) or a known fuel string.")
    liters = (np.asarray(mass_g, dtype=float) / 1000.0) / rho
    return liters / 3.785411784

# ---------------------------
# Core calculations (Diesel MAW)
# ---------------------------

def calculate_maw_and_subintervals(df, eCO2_g_hp_hr, pmax_hp):
    """
    Implements the MAW windowing, exclusions, binning, and summary.
    Returns: df, summary_df, windows_df, sub_interval_df, invalid_count
    """
    # Base engine calcs
    df["EnginePower_hp"] = (df["Engine_Torque_Nm"] * df["Engine_RPM"]) / 7120.8
    df["Altitude_ft"] = df["Altitude_m"] * 3.28084
    # Per-second distance (assuming 1 Hz)
    df["Distance_mi"] = df["v_mph"] / 3600.0

    # Exclusion logic
    tmax_c = (-0.0014 * df["Altitude_ft"]) + 37.78
    df["Excluded_Data"] = (
        (df["AmbTempC"] < -5.0)
        | (df["AmbTempC"] > tmax_c)
        | (df["Altitude_ft"] > 5500.0)
        | (df["Engine_RPM"] < 1.0)
        | (df["ZeroCheck"] == 1.0)
        | (df["In_Regen"].fillna(0).astype(bool))
    ).fillna(True)

    # Re-classify isolated valid points as excluded (valid flanked by excluded)
    excl = df["Excluded_Data"].to_numpy().astype(bool)
    shift_fwd = np.concatenate([[True], excl[:-1]])
    shift_bwd = np.concatenate([excl[1:], [True]])
    isolated_valid = shift_fwd & shift_bwd & (~excl)
    excl[isolated_valid] = True
    df["Excluded_Data"] = excl

    # Sub-Interval IDs based on excluded breaks
    df["Sub_Interval_ID"] = np.cumsum(df["Excluded_Data"].astype(int)).astype(int)

    # Valid-only dataframe subset, also record original indices
    valid_idx = np.where(~df["Excluded_Data"].values)[0]
    if valid_idx.size == 0:
        return df, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 0

    valid_df = df.iloc[valid_idx, :].copy()
    valid_df["Original_Time_Sec"] = valid_idx

    # Sub-interval summary
    grp = valid_df.groupby("Sub_Interval_ID")
    sub_summary = pd.DataFrame({
        "Sub_Interval_ID": grp.size().index.values,
        "Duration_sec": grp.size().values,
        "Avg_Power_hp": grp["EnginePower_hp"].mean().values,
        "Work_hp_hr": (grp["EnginePower_hp"].sum() / 3600.0).values,
        "Distance_mi": grp["Distance_mi"].sum().values,
        "NOx_g": grp["instNOx"].sum().values,
        "PM_g": grp["instPM"].sum().values,
        "HC_g": grp["instHC"].sum().values,
        "CO_g": grp["instCO"].sum().values,
        "CO2_g": grp["instCO2"].sum().values,
    })

    # MAW windows
    total_points = len(df)
    num_valid = len(valid_idx)
    if num_valid < 300:
        return df, pd.DataFrame(), pd.DataFrame(), sub_summary, 0

    # Mapping from chrono index -> valid order index (0..num_valid-1), -1 for excluded
    chrono_to_valid = np.full(total_points, -1, dtype=int)
    chrono_to_valid[valid_idx] = np.arange(num_valid)

    # Prealloc
    max_windows = total_points
    Window_Index = np.zeros(max_windows, dtype=int)
    Window_Start_Time = np.zeros(max_windows, dtype=int)
    Window_End_Time = np.zeros(max_windows, dtype=int)
    Excluded_Samples_Count = np.zeros(max_windows, dtype=int)
    Total_Work_hp_hr = np.zeros(max_windows, dtype=float)
    Total_Distance_mi = np.zeros(max_windows, dtype=float)
    Total_Fuelrate_g = np.zeros(max_windows, dtype=float)
    eCO2norm_percent = np.zeros(max_windows, dtype=float)
    Bin = np.zeros(max_windows, dtype=int)
    massNOx = np.full(max_windows, np.nan)
    massHC = np.full(max_windows, np.nan)
    massPM = np.full(max_windows, np.nan)
    massCO = np.full(max_windows, np.nan)
    massCO2 = np.full(max_windows, np.nan)
    NOx_mg_mi = np.full(max_windows, np.nan)
    HC_mg_mi = np.full(max_windows, np.nan)
    PM_mg_mi = np.full(max_windows, np.nan)
    CO_g_mi = np.full(max_windows, np.nan)
    CO2_g_mi = np.full(max_windows, np.nan)

    bin2_denom = eCO2_g_hp_hr * pmax_hp * (300.0 / 3600.0)
    invalid_count = 0
    w_idx = 0

    excluded = df["Excluded_Data"].values
    for i in range(0, total_points - 1):
        # require window starts with two consecutive valid points
        if excluded[i] or excluded[i + 1]:
            continue

        v_start = chrono_to_valid[i]
        if v_start < 0:
            continue
        if v_start + 299 >= num_valid:
            break

        # 300th valid's chrono index
        j = valid_idx[v_start + 299]
        valid_end = False
        valid_samples_count = 300

        # Ensure window end is also preceded by a valid (j-1)
        if not excluded[j - 1]:
            valid_end = True
        else:
            if v_start + 300 < num_valid:
                j_301 = valid_idx[v_start + 300]
                if not excluded[j_301 - 1]:
                    j = j_301
                    valid_end = True
                    valid_samples_count = 301

        # if not valid_end:
        #     continue
        if valid_end:
            # Include both endpoints (Python iloc slice-exclusive on end, hence j+1)
            window_full = df.iloc[i:j + 1, :].copy()
            win_valid = window_full.loc[~window_full["Excluded_Data"]]
            w_idx += 1

            time_start = i
            time_end = j
            excluded_count = int(window_full["Excluded_Data"].sum())

            # Integrals (trapezoid, 1 Hz)
            def trapezoid_col(s):
                a = to_numeric(s).fillna(0.0).values
                return float(np.trapezoid(a, dx=1.0))

            t_CO2 = trapezoid_col(win_valid["instCO2"])
            t_NOx = trapezoid_col(win_valid["instNOx"])
            t_PM = trapezoid_col(win_valid["instPM"])
            t_HC = trapezoid_col(win_valid["instHC"])
            t_CO = trapezoid_col(win_valid["instCO"])
            t_work = trapezoid_col(win_valid["EnginePower_hp"]) / 3600.0
            t_dist = trapezoid_col(win_valid["Distance_mi"])
            t_fuelrate = trapezoid_col(win_valid["instFuelRate"])

            eCO2norm_pct = (t_CO2 / bin2_denom) * 100.0 if bin2_denom > 0 else np.nan

            if t_dist > 0:
                n_mi = (t_NOx * 1000.0) / t_dist
                h_mi = (t_HC * 1000.0) / t_dist
                p_mi = (t_PM * 1000.0) / t_dist
                c_mi = t_CO / t_dist
                c2_mi = t_CO2 / t_dist
            else:
                n_mi = h_mi = p_mi = c_mi = c2_mi = np.nan

            if excluded_count > 599:
                # Invalid window
                bin_label =  0
                Window_Index[w_idx - 1] = i
                Window_Start_Time[w_idx - 1] = time_start
                Window_End_Time[w_idx - 1] = time_end
                Excluded_Samples_Count[w_idx - 1] = excluded_count

                invalid_count += 1
            else:
                # Valid window
                bin_label = 1 if (eCO2norm_pct < 6.0) else 2

                Window_Index[w_idx - 1] = i
                Window_Start_Time[w_idx - 1] = time_start
                Window_End_Time[w_idx - 1] = time_end
                Excluded_Samples_Count[w_idx - 1] = excluded_count
                Total_Work_hp_hr[w_idx - 1] = t_work
                Total_Distance_mi[w_idx - 1] = t_dist
                Total_Fuelrate_g[w_idx - 1] = t_fuelrate
                eCO2norm_percent[w_idx - 1] = eCO2norm_pct
                Bin[w_idx - 1] = bin_label
                massNOx[w_idx - 1] = t_NOx
                massHC[w_idx - 1] = t_HC
                massPM[w_idx - 1] = t_PM
                massCO[w_idx - 1] = t_CO
                massCO2[w_idx - 1] = t_CO2
                NOx_mg_mi[w_idx - 1] = n_mi
                HC_mg_mi[w_idx - 1] = h_mi
                PM_mg_mi[w_idx - 1] = p_mi
                CO_g_mi[w_idx - 1] = c_mi
                CO2_g_mi[w_idx - 1] = c2_mi

    if w_idx == 0:
        return df, pd.DataFrame(), pd.DataFrame(), sub_summary, invalid_count

    # Truncate arrays to actual windows
    sl = slice(0, w_idx)
    windows_df = pd.DataFrame({
        "Window_Index": Window_Index[sl],
        "Window_Start_Time": Window_Start_Time[sl],
        "Window_End_Time": Window_End_Time[sl],
        "Excluded_Samples_Count": Excluded_Samples_Count[sl],
        "Total_Work_hp_hr": Total_Work_hp_hr[sl],
        "Total_Distance_mi": Total_Distance_mi[sl],
        "Total_Fuelrate_g": Total_Fuelrate_g[sl],
        "eCO2norm_percent": eCO2norm_percent[sl],
        "Bin": Bin[sl],
        "massNOx": massNOx[sl],
        "massHC": massHC[sl],
        "massPM": massPM[sl],
        "massCO": massCO[sl],
        "massCO2": massCO2[sl],
        "NOx_mg_mi": NOx_mg_mi[sl],
        "HC_mg_mi": HC_mg_mi[sl],
        "PM_mg_mi": PM_mg_mi[sl],
        "CO_g_mi": CO_g_mi[sl],
        "CO2_g_mi": CO2_g_mi[sl],
    })

    valid_wins = windows_df[windows_df["Bin"] != 0].copy()
    if valid_wins.empty:
        return df, pd.DataFrame(), windows_df, sub_summary, invalid_count

    # Summary by bin
    g = valid_wins.groupby("Bin")
    Total_Windows = g["eCO2norm_percent"].size()
    Avg_eCO2norm_Percent = g["eCO2norm_percent"].mean()

    # Explicit bin mapping calculations (Bin1/2 metrics)
    bin_labels = Total_Windows.index.values
    num_groups = len(bin_labels)
    Avg_Bin1_NOx_g_hr = np.full(num_groups, np.nan)
    Avg_Bin2_NOx_mg_hp_hr = np.full(num_groups, np.nan)
    Avg_Bin2_HC_mg_hp_hr = np.full(num_groups, np.nan)
    Avg_Bin2_PM_mg_hp_hr = np.full(num_groups, np.nan)
    Avg_Bin2_CO_g_hp_hr = np.full(num_groups, np.nan)
    Avg_Bin2_CO2_g_hp_hr = np.full(num_groups, np.nan)

    # Overall distance-based NOx mg/mi using the entire DF (including excluded)
    total_dist = df["Distance_mi"].sum()
    overall_nox_mg_mi = (df["instNOx"].sum() * 1000.0) / total_dist if total_dist > 0 else np.nan
    Avg_NOx_mg_mi = np.full(num_groups, overall_nox_mg_mi)
    # Also include other distance-based averages by bin (optional; here we compute overall only)
    # If you need per-bin averages for NOx/HC/PM/CO/CO2 per mile, you can compute similarly.

    # Bin 1
    if 1 in bin_labels:
        mask_bin1 = (valid_wins["Bin"] == 1).values
        num_bin1 = mask_bin1.sum()
        if num_bin1 > 0:
            nox_bin1 = (valid_wins.loc[mask_bin1, "massNOx"].sum() / (300.0 * num_bin1)) * 3600.0  # g/hr
            Avg_Bin1_NOx_g_hr[bin_labels.tolist().index(1)] = nox_bin1

    # Bin 2
    if 2 in bin_labels:
        mask_bin2 = (valid_wins["Bin"] == 2).values
        sumCO2_Bin2 = valid_wins.loc[mask_bin2, "massCO2"].sum()
        if sumCO2_Bin2 > 0:
            n2 = (valid_wins.loc[mask_bin2, "massNOx"].sum() / sumCO2_Bin2) * eCO2_g_hp_hr * 1000.0
            c2 = (valid_wins.loc[mask_bin2, "massCO"].sum() / sumCO2_Bin2) * eCO2_g_hp_hr
            h2 = (valid_wins.loc[mask_bin2, "massHC"].sum() / sumCO2_Bin2) * eCO2_g_hp_hr * 1000.0
            p2 = (valid_wins.loc[mask_bin2, "massPM"].sum() / sumCO2_Bin2) * eCO2_g_hp_hr * 1000.0
            Avg_Bin2_NOx_mg_hp_hr[bin_labels.tolist().index(2)] = n2
            Avg_Bin2_CO_g_hp_hr[bin_labels.tolist().index(2)] = c2
            Avg_Bin2_HC_mg_hp_hr[bin_labels.tolist().index(2)] = h2
            Avg_Bin2_PM_mg_hp_hr[bin_labels.tolist().index(2)] = p2
            Avg_Bin2_CO2_g_hp_hr[bin_labels.tolist().index(2)] = eCO2_g_hp_hr

    summary = pd.DataFrame({
        "Bin": bin_labels,
        "Total_Windows": Total_Windows.values,
        "Avg_eCO2norm_Percent": Avg_eCO2norm_Percent.values,
        "Avg_Bin1_NOx_g_hr": Avg_Bin1_NOx_g_hr,
        "Avg_Bin2_NOx_mg_hp_hr": Avg_Bin2_NOx_mg_hp_hr,
        "Avg_Bin2_HC_mg_hp_hr": Avg_Bin2_HC_mg_hp_hr,
        "Avg_Bin2_PM_mg_hp_hr": Avg_Bin2_PM_mg_hp_hr,
        "Avg_Bin2_CO_g_hp_hr": Avg_Bin2_CO_g_hp_hr,
        "Avg_Bin2_CO2_g_hp_hr": Avg_Bin2_CO2_g_hp_hr,
        "Avg_NOx_mg_mi": Avg_NOx_mg_mi,
        # Optional: Add other distance-based metrics here if desired
    })

    # Print a small standards table similar to MATLAB display
    Tamb = df["AmbTempC"].mean()
    if Tamb < 25:
        NOxBin1Std = 10.4 + ((25 - Tamb) * 0.25)
        NOxBin2Std = 63 + ((25 - Tamb) * 2.2)
    else:
        NOxBin1Std = 10.4
        NOxBin2Std = 63.0

    # In MATLAB, a display table is printed. Here we simply log via print.
    def safe_val(bin_val):
        try:
            return float(bin_val)
        except Exception:
            return np.nan

    val_bin1 = summary.loc[summary["Bin"] == 1, "Avg_Bin1_NOx_g_hr"]
    val_bin2 = summary.loc[summary["Bin"] == 2, "Avg_Bin2_NOx_mg_hp_hr"]
    NOxBin1 = safe_val(val_bin1.iloc[0]) if not val_bin1.empty else np.nan
    NOxBin2 = safe_val(val_bin2.iloc[0]) if not val_bin2.empty else np.nan

    print("Standards vs Test Values")
    print(f"Bin1 NOx: Standard {NOxBin1Std:.1f} g/hr | Test {NOxBin1:.4f} g/hr")
    print(f"Bin2 NOx: Standard {round(NOxBin2Std):.0f} mg/hp*hr | Test {NOxBin2:.3f} mg/hp*hr")

    return df, summary, windows_df, sub_summary, invalid_count


def evaluate_compliance(summary_df, limits):
    """
    Build a compliance table by comparing bin averages against regulatory limits.
    limits is a dict with keys:
      Bin1_NOx_g_hr, Bin2_NOx_mg_hp_hr, Bin2_HC_mg_hp_hr, Bin2_PM_mg_hp_hr, Bin2_CO_g_hp_hr, Bin2_CO2_g_hp_hr
    """
    rows = []
    if summary_df is None or summary_df.empty:
        return pd.DataFrame(columns=["Bin", "Metric", "Actual_Average", "Regulatory_Limit", "Status"])

    for _, r in summary_df.iterrows():
        b = int(r["Bin"])
        if b == 1:
            actual = r.get("Avg_Bin1_NOx_g_hr", np.nan)
            limit = limits.get("Bin1_NOx_g_hr", np.nan)
            rows.append([1, "NOx (g/hr)", round(float(actual), 3) if pd.notna(actual) else np.nan,
                         limit, "PASS" if (pd.notna(actual) and actual <= limit) else "FAIL"])
        elif b == 2:
            mets = [
                ("NOx (mg/hp-hr)", "Avg_Bin2_NOx_mg_hp_hr", "Bin2_NOx_mg_hp_hr"),
                ("HC (mg/hp-hr)",  "Avg_Bin2_HC_mg_hp_hr",  "Bin2_HC_mg_hp_hr"),
                ("PM (mg/hp-hr)",  "Avg_Bin2_PM_mg_hp_hr",  "Bin2_PM_mg_hp_hr"),
                ("CO (g/hp-hr)",   "Avg_Bin2_CO_g_hp_hr",   "Bin2_CO_g_hp_hr"),
                ("CO2 (g/hp-hr)",  "Avg_Bin2_CO2_g_hp_hr",  "Bin2_CO2_g_hp_hr"),
            ]
            for label, col, limkey in mets:
                actual = r.get(col, np.nan)
                limit = limits.get(limkey, np.nan)
                status = "PASS" if (pd.notna(actual) and actual <= limit) else "FAIL"
                rows.append([2, label, round(float(actual), 3) if pd.notna(actual) else np.nan, limit, status])

    return pd.DataFrame(rows, columns=["Bin", "Metric", "Actual_Average", "Regulatory_Limit", "Status"])


# ---------------------------
# Plotting for Diesel MAW
# ---------------------------

def plot_shift_day_emissions(df, pdf_file=None):
    """
    Visual plot: Engine power with excluded zones, and v_mph + instCO2 dual-axis with excluded zones.
    """
    time_sec = len(df)
    t = np.arange(1, time_sec + 1)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    fig.patch.set_facecolor("white")
    # Tile 1: Engine Power + excluded patches
    ax1 = axes[0]
    line1, = ax1.plot(t, df["EnginePower_hp"], color="#0072BD", linewidth=1.5, label="Engine Power (hp)")
    ax1.set_ylabel("Engine Power (hp)")
    ax1.set_title("Engine Test Data: Valid vs. Excluded Regions")
    ax1.grid(True)

    # Draw excluded zones
    excl = df["Excluded_Data"].astype(bool).values
    diff_excl = np.diff(np.concatenate(([0], excl.astype(int), [0])))
    starts = np.where(diff_excl == 1)[0]
    ends = np.where(diff_excl == -1)[0] - 1
    y_lims = ax1.get_ylim()
    for s, e in zip(starts, ends):
        ax1.axvspan(s + 1 - 0.5, e + 1 + 0.5, color="red", alpha=0.2)
    ax1.legend(loc="upper right")
    # Hide x-axis tick labels on subplot 1
    ax1.tick_params(axis='x', which='both', labelbottom=False)
    leg = axes[0].legend(
        labels=["Engine Power (hp)", "Excluded Data"],
        loc="upper left",           # anchor the legend's upper-left corner
        borderaxespad=0.0,
        fontsize=7.65,
        frameon=True,
        fancybox=False,
    )
    
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    axes[0].grid(True)
    
    # Tile 2: v_mph (left) and instCO2 (right)
    ax2 = axes[1]
    color_left = "#77AC30"
    color_right = "#D95319"
    line3, =ax2.plot(t, df["v_mph"], color=color_left, linewidth=2, label="Vehicle Speed (mph)")
    ax2.set_ylabel("Vehicle Speed (mph)", color=color_left)
    ax2.tick_params(axis="y", labelcolor=color_left)

    ax2b = ax2.twinx()
    line4, = ax2b.plot(t, df["instCO2"], color=color_right, linewidth=1.5, label="Inst. CO2 (g/s)")
    ax2b.set_ylabel("Instantaneous CO2 (g/s)", color=color_right)
    ax2b.tick_params(axis="y", labelcolor=color_right)

    ax2.set_xlabel("Time (seconds)")
    ax2.grid(True)

    # Excluded zones in tile 2
    y1, y2 = ax2.get_ylim()
    for s, e in zip(starts, ends):
        ax2.axvspan(s + 1 - 0.5, e + 1 + 0.5, color="red", alpha=0.2)

    # ax2.legend(loc="upper left")
    # ax2b.legend(loc="upper right")
    leg = axes[1].legend(
        handles=[line3, line4],
        labels=["Vehicle Speed (mph)", "Instantaneous CO2 (g/s)"],
        loc="upper left",           # anchor the legend's upper-left corner
        borderaxespad=0.0,
        fontsize=7.65,
        frameon=True,
        fancybox=False,
    )
    
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    axes[1].grid(True)
    
    plt.show()
    
    # Save figure to PDF
    # pdf_file = Path('shift_day_emissions.pdf')
    # fig.savefig(pdf_file, format='pdf', bbox_inches='tight', dpi=300)
    # print(f"PDF saved: {pdf_file}")
    
    with PdfPages(pdf_file) as pdf:
        pdf.savefig(fig, bbox_inches='tight', dpi=300)
    plt.close(fig)


def plot_cumulative_emissions(df, eCO2_g_hp_hr, pdf_file=None):
    """
    Plots cumulative NOx and CO2 (valid only) and cumulative brake-specific NOx
    for work-based and eCO2-based methods.
    """
    valid_df = df.loc[~df["Excluded_Data"]].copy()
    if valid_df.empty:
        print("No valid data available for cumulative plots.")
        return

    valid_df["Cum_NOx_g"] = valid_df["instNOx"].fillna(0.0).cumsum()
    valid_df["Cum_CO2_g"] = valid_df["instCO2"].fillna(0.0).cumsum()
    valid_df["Cum_Work_hp_hr"] = (valid_df["EnginePower_hp"].fillna(0.0) / 3600.0).cumsum()

    bs_nox = np.zeros(len(valid_df))
    work_pos = valid_df["Cum_Work_hp_hr"] > 0
    bs_nox[work_pos.values] = (valid_df.loc[work_pos, "Cum_NOx_g"] / valid_df.loc[work_pos, "Cum_Work_hp_hr"]).values
    valid_df["BS_NOx_g_hp_hr"] = bs_nox

    c2 = valid_df["Cum_CO2_g"].replace(0, np.nan)
    valid_df["bs_nox_eCO2"] = (valid_df["Cum_NOx_g"] / c2) * eCO2_g_hp_hr

    t_valid = valid_df.index.values + 1

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    fig.patch.set_facecolor("white")

    ax1 = axes[0]
    line1, =ax1.plot(t_valid, valid_df["Cum_NOx_g"], color="#A2142F", linewidth=2, label="Cumulative NOx (g)")
    ax1.set_ylabel("Cumulative NOx (g)")
    ax1.set_title("Cumulative Emissions Accrual During Valid Testing")
    ax1.grid(True)
    ax1b = ax1.twinx()
    line2, = ax1b.plot(t_valid, valid_df["Cum_CO2_g"], "--", color="#7E2F8E", linewidth=2, label="Cumulative CO2 (g)")
    ax1b.set_ylabel("Cumulative CO2 (g)", color="#7E2F8E")
    ax1b.tick_params(axis="y", color='#7E2F8E', labelcolor="#7E2F8E")

    ax1.legend(loc="best")

    # Hide x-axis tick labels on subplot 1
    ax1.tick_params(axis='x', which='both', labelbottom=False)
    leg = axes[0].legend(
        handles=[line1, line2],
        labels=["Cumulative NOx (g)", "Cumulative CO2 (g)"],
        loc="best",           # anchor the legend's upper-left corner
        borderaxespad=0.0,
        fontsize=7.65,
        frameon=True,
        fancybox=False,
    )
    
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    axes[0].grid(True)
    
    ax2 = axes[1]
    line1, = ax2.plot(t_valid, valid_df["BS_NOx_g_hp_hr"], color="#0072BD", linewidth=2, label="BS NOx via Work (g/hp-hr)")
    line2, = ax2.plot(t_valid, valid_df["bs_nox_eCO2"], color="#77AC30", linewidth=2, label="BS NOx via eCO2 (g/hp-hr)")
    if not valid_df["BS_NOx_g_hp_hr"].dropna().empty:
        final_avg = float(valid_df["BS_NOx_g_hp_hr"].dropna().iloc[-1])
        ax2.axhline(final_avg, linestyle=":", color="black", linewidth=1.5, label=f"Final Avg: {final_avg:.3f} g/hp-hr")
        ax2.set_ylim(0, 1.25 * valid_df["BS_NOx_g_hp_hr"].max())
    ax2.set_xlabel("Time (Original Second of Shift)")
    ax2.set_ylabel("Cum. BS NOx (g/hp-hr)")
    ax2.grid(True)
    ax2.legend(loc="best")
    leg = axes[1].legend(
        labels=["BS NOx via Work (g/hp-hr)", "BS NOx via eCO2 (g/hp-hr)", f"Final Avg: {final_avg:.3f} g/hp-hr"],
        loc="best",           # anchor the legend's upper-left corner
        borderaxespad=0.0,
        fontsize=7.65,
        frameon=True,
        fancybox=False,
    )
    
    frame = leg.get_frame()
    frame.set_edgecolor("black")
    frame.set_linewidth(0.5)
    axes[1].grid(True)
    
    plt.show()

    # pdf_file = Path('cumulative_emissions.pdf')
    # fig.savefig(pdf_file, format='pdf', bbox_inches='tight', dpi=300)
    append_fig_to_pdf(pdf_file, fig, dpi=600)
    # print(f"PDF saved: {pdf_file}")
    plt.close(fig)
# ---------------------------
# Shift-Day (Gasoline) calculations
# ---------------------------

def calculate_shift_day_emissions(df, ftp_eco2_g_hp_hr, pmax_hp):
    """
    Shift-day emissions using both Work method and Pmax/eCO2 method.
    Returns: df, results (dict), sub_summary (DataFrame)
    """
    df["EnginePower_hp"] = (df["Engine_Torque_Nm"] * df["Engine_RPM"]) / 7120.8
    df["Altitude_ft"] = df["Altitude_m"] * 3.28084
    df["Distance_mi"] = df["v_mph"] / 3600.0

    # Total mass from ALL data (including excluded)
    total_distance_mi = df["Distance_mi"].sum()
    total_all_NOx_g = df["instNOx"].sum()
    total_all_PM_g = df["instPM"].sum()
    total_all_HC_g = df["instHC"].sum()
    total_all_CO_g = df["instCO"].sum()
    total_all_CO2_g = df["instCO2"].sum()

    # Exclusions
    tmax_c = (-0.0014 * df["Altitude_ft"]) + 37.78
    df["Excluded_Data"] = (
        (df["AmbTempC"] < -5.0)
        | (df["AmbTempC"] > tmax_c)
        | (df["Altitude_ft"] > 5500.0)
        | (df["Engine_RPM"] < 1.0)
        | (df["ZeroCheck"] == 1.0)
        | (df["In_Regen"].fillna(0).astype(bool))
    ).fillna(True)
    df["Sub_Interval_ID"] = np.cumsum(df["Excluded_Data"].astype(int))

    valid_df = df.loc[~df["Excluded_Data"]].copy()
    if valid_df.empty:
        raise ValueError("Error: No valid data points found.")

    grp = valid_df.groupby("Sub_Interval_ID")
    sub_summary = pd.DataFrame({
        "Sub_Interval_ID": grp.size().index.values,
        "Duration_sec": grp.size().values,
        "Avg_Power_hp": grp["EnginePower_hp"].mean().values,
        "Work_hp_hr": (grp["EnginePower_hp"].sum() / 3600.0).values,
        "Distance_mi": grp["Distance_mi"].sum().values,
        "NOx_g": grp["instNOx"].sum().values,
        "PM_g": grp["instPM"].sum().values,
        "HC_g": grp["instHC"].sum().values,
        "CO_g": grp["instCO"].sum().values,
        "CO2_g": grp["instCO2"].sum().values,
    })

    total_valid_NOx_g = valid_df["instNOx"].sum()
    total_valid_PM_g = valid_df["instPM"].sum()
    total_valid_HC_g = valid_df["instHC"].sum()
    total_valid_CO_g = valid_df["instCO"].sum()
    total_valid_CO2_g = valid_df["instCO2"].sum()
    total_work_hp_hr = valid_df["EnginePower_hp"].sum() / 3600.0
    valid_distance_mi = valid_df["Distance_mi"].sum()

    bs_multiplier_work = 1.0 / total_work_hp_hr if total_work_hp_hr > 0 else np.nan

    results = {}
    results["Total_Shift_Seconds"] = int(len(df))
    results["Total_Valid_Seconds"] = int(len(valid_df))
    results["Total_Excluded_Seconds"] = int(df["Excluded_Data"].sum())
    results["Total_Sub_Intervals_Stitched"] = int(valid_df["Sub_Interval_ID"].nunique())
    results["Total_Work_hp_hr"] = float(total_work_hp_hr)
    results["Total_Distance_mi"] = float(total_distance_mi)
    results["Valid_Distance_mi"] = float(valid_distance_mi)

    # Work method - VALID ONLY
    results["NOx_mg_hp_hr_Work"] = float((total_valid_NOx_g * 1000.0) * bs_multiplier_work) if pd.notna(bs_multiplier_work) else np.nan
    results["PM_mg_hp_hr_Work"] = float((total_valid_PM_g * 1000.0) * bs_multiplier_work) if pd.notna(bs_multiplier_work) else np.nan
    results["HC_mg_hp_hr_Work"] = float((total_valid_HC_g * 1000.0) * bs_multiplier_work) if pd.notna(bs_multiplier_work) else np.nan
    results["CO_g_hp_hr_Work"] = float(total_valid_CO_g * bs_multiplier_work) if pd.notna(bs_multiplier_work) else np.nan
    results["CO2_g_hp_hr_Work"] = float(total_valid_CO2_g * bs_multiplier_work) if pd.notna(bs_multiplier_work) else np.nan

    # Pmax/eCO2 method - VALID ONLY
    if total_valid_CO2_g > 0:
        ratio = ftp_eco2_g_hp_hr / total_valid_CO2_g
        results["NOx_mg_Pmax_eCO2"] = float(total_valid_NOx_g * 1000.0 * ratio)
        results["PM_mg_Pmax_eCO2"] = float(total_valid_PM_g * 1000.0 * ratio)
        results["HC_mg_Pmax_eCO2"] = float(total_valid_HC_g * 1000.0 * ratio)
        results["CO_g_Pmax_eCO2"] = float(total_valid_CO_g * ratio * 1.0)
        results["CO2_g_Pmax_eCO2"] = float(ftp_eco2_g_hp_hr)
    else:
        results["NOx_mg_Pmax_eCO2"] = np.nan
        results["PM_mg_Pmax_eCO2"] = np.nan
        results["HC_mg_Pmax_eCO2"] = np.nan
        results["CO_g_Pmax_eCO2"] = np.nan
        results["CO2_g_Pmax_eCO2"] = float(ftp_eco2_g_hp_hr)

    # Distance-specific (total, using ALL data)
    if total_distance_mi > 0:
        results["NOx_mg_mi_TotalDist"] = float((total_all_NOx_g * 1000.0) / total_distance_mi)
        results["PM_mg_mi_TotalDist"] = float((total_all_PM_g * 1000.0) / total_distance_mi)
        results["HC_mg_mi_TotalDist"] = float((total_all_HC_g * 1000.0) / total_distance_mi)
        results["CO_g_mi_TotalDist"] = float(total_all_CO_g / total_distance_mi)
        results["CO2_g_mi_TotalDist"] = float(total_all_CO2_g / total_distance_mi)
    else:
        results["NOx_mg_mi_TotalDist"] = np.nan
        results["PM_mg_mi_TotalDist"] = np.nan
        results["HC_mg_mi_TotalDist"] = np.nan
        results["CO_g_mi_TotalDist"] = np.nan
        results["CO2_g_mi_TotalDist"] = np.nan

    # Distance-specific (valid only)
    if valid_distance_mi > 0:
        results["NOx_mg_mi_ValidDist"] = float((total_valid_NOx_g * 1000.0) / valid_distance_mi)
        results["PM_mg_mi_ValidDist"] = float((total_valid_PM_g * 1000.0) / valid_distance_mi)
        results["HC_mg_mi_ValidDist"] = float((total_valid_HC_g * 1000.0) / valid_distance_mi)
        results["CO_g_mi_ValidDist"] = float(total_valid_CO_g / valid_distance_mi)
        results["CO2_g_mi_ValidDist"] = float(total_valid_CO2_g / valid_distance_mi)
    else:
        results["NOx_mg_mi_ValidDist"] = np.nan
        results["PM_mg_mi_ValidDist"] = np.nan
        results["HC_mg_mi_ValidDist"] = np.nan
        results["CO_g_mi_ValidDist"] = np.nan
        results["CO2_g_mi_ValidDist"] = np.nan

    return df, results, sub_summary


# ---------------------------
# Main orchestration
# ---------------------------

def run_emissions_analysis(excelfile, binData_avg, raw, udp, MPG=None, fuel_density=None, do_plots=True):
    """
    Build base df from raw table and run either Diesel MAW or Gasoline shift-day logic.
    'raw' is a pandas DataFrame with instrumented signals.
    'udp' dict must include:
        udp["bins"]["eco2fcl"] (float)
        udp["bins"]["pmax"] (float)
        udp["log"]["fuel"] in {"Diesel", "Gasoline"}
    Returns: df, results_dict with details.
    
    # filename_udp = re.sub(r'_Matlab[^.]*\.xlsx$', '_udp.xlsx', vehData.filename)
    filename_udp = re.sub('_Matlab[^.]*\\.xlsx$', '_udp.xlsx', vehData.filename)
    
    p = Path(vehData.filename)
    new_name = re.sub(r'_Matlab[^.]*\.xlsx$', '_udp.xlsx', p.name)
    filename_udp = str(p.with_name(new_name))
    """
    # raw = pd.read_csv('c:\\Users\\slee02\\Matlab\\RoadaC\\vehData_data.csv') # 2021_Volvo_VNL_White_HWY_20240429\\pp_2021_Volvo_VNL_White_HWY_20240429_M1-M97_MatlabBinCalc.xlsx')
    raw = pd.read_excel(excelfile, sheet_name='vehData_data')
    udp_bins = pd.read_excel(excelfile, sheet_name='udp_bins')
    udp_log = pd.read_excel(excelfile, sheet_name='udp_log')
    udp_fuel = pd.read_excel(excelfile, sheet_name='udp_fuel')
    udp_scalar = pd.read_excel(excelfile, sheet_name='scalar')
    scalarBinData = pd.read_excel(excelfile, sheet_name='scalarBinData')
    logData = pd.read_excel(excelfile, sheet_name='logData')
    binData = pd.read_excel(excelfile, sheet_name='binData')

    # MPG = vehData(setIdx).scalarData.Fuel_Economy;

    udp = {
        "bins": {
            "eco2fcl": udp_bins['eco2fcl'],
            "pmax": udp_bins['pmax']
        },
        "log": {
            "fuel": udp_log['fuel']
        },
        "fuel": {
            "fuel_sg": udp_fuel['sg']
        },
        "scalar": {
            "MPG": udp_scalar['Fuel_Economy']
        }
    }
    # Flexible name handling to find key columns:
    # Ambient temp column (try "LimitAdjusted..._LAT" or "Temp_Amb")
    amb_col_series = find_col_contains(raw, ["limitadjusted", "_lat"])
    if amb_col_series is None:
        amb_col_series = get_column(raw, ["Temp_Amb"])
    # Vehicle speed column
    veh_spd_series = find_col_contains(raw, ["vehicle", "speed"])
    # Engine fuel-rate column (best-effort; optional in this script)
    # fuel_rate_series = find_col_contains(raw, ["engine", "fuelrate"])
    # Instantaneous fuel flow (g/s)
    inst_fuel_series = get_column(raw, ["InstantaneousFuelFlow", "Instantaneous Fuel Flow"])

    # ZeroCheck_col = getTextColumn(raw, {'Zero_Check_Flag','Zero_Check'});
    ZeroCheck_col = first_existing_column(raw, ['Zero_Check_Flag', 'Zero_Check'])
    GasPath_col = first_existing_column(raw, ['Gas Path', 'GasPath'])

    if GasPath_col is not None:
        raw['ZeroCheck'] = raw[GasPath_col].isin(['CALIBRATION', 'STANDBY', 'AMBIENT']).astype(int)

        if ('ZeroCheck' in raw.columns) and (int(raw['ZeroCheck'].sum()) > 0):
            print(f"# of non-SANPLE = {int(raw['ZeroCheck'].sum())}")
    elif ZeroCheck_col is not None:
        raw['ZeroCheck'] = raw[ZeroCheck_col].isin(['Y']).astype(int)
        
    # Build df with key signals (robust fallbacks if missing)
    df = pd.DataFrame()
    df["Time"] = to_numeric(get_column(raw, ["TIME"]))
    df["AmbTempC"] = to_numeric(amb_col_series if amb_col_series is not None else get_column(raw, ["Temp_Amb"]))

    # Emission massflow signals (g/s); adapt to your dataset names
    df["instCO"] = to_numeric(get_column(raw, ["CO_MassFlow", "CO_Mass_Sec"]))
    df["instCO2"] = to_numeric(get_column(raw, ["CO2_MassFlow", "CO2_Mass_Sec"]))

    pm_series = get_column(raw, ["PM_Mass_Sec_Final", "PM_Mass_sec_Final", "PM_Mass_Sec", "PM_Mass_sec"])
    if pm_series is None:
        df["instPM"] = 0.0
    else:
        df["instPM"] = to_numeric(pm_series)

    df["instHC"] = to_numeric(get_column(raw, ["HC_MassFlow", "THC_Mass_Sec"]))
    df["instNOx"] = to_numeric(get_column(raw, ["kNOx_MassFlow", "NOX_Mass_sec_Final", "NOX_Mass_Sec", "NOX_Mass_sec"]))
    df["In_Regen"] = to_numeric(get_column(raw, ["DPFRegenStatus", "Regen"])).fillna(0.0)

    alt_ft_series = to_numeric(get_column(raw, ["Altitude_Ft", "Alt"]))
    # raw may store altitude in feet; convert to meters
    if alt_ft_series is not None and not alt_ft_series.isna().all():
        df["Altitude_m"] = alt_ft_series / 3.28084
    else:
        df["Altitude_m"] = 0.0

    df["Engine_RPM"] = to_numeric(get_column(raw, ["EngineRPM"]))
    df["Engine_Torque_Nm"] = to_numeric(get_column(raw, ["DerivedEngineTorque"]))
    # If torque in lb-ft provided, you may convert or keep both
    df["Engine_Torque_lb_ft"] = to_numeric(get_column(raw, ["DerivedEngineTorque_1"]))

    # Distance (if logged). Optional; we also compute per-second distance from v_mph.
    df["Distance"] = to_numeric(get_column(raw, ["Cumulative_Distance_Miles", "Distance"]))

    # Vehicle speed in mph
    v_series = veh_spd_series if veh_spd_series is not None else get_column(raw, ["Vehicle Speed", "VehicleSpeedMPH", "Veh_Speed"])
    df["v_mph"] = to_numeric(v_series)

    # Instantaneous fuel flow (g/s)
    df["instFuelRate"] = to_numeric(inst_fuel_series)
    df["ZeroCheck"] = raw['ZeroCheck'] 

    # Replace fully-missing columns with zeros to avoid NaN propagation in sums
    for c in ["instCO", "instCO2", "instPM", "instHC", "instNOx", "Engine_RPM", "Engine_Torque_Nm", "v_mph", "instFuelRate"]:
        if c in df.columns:
            df[c] = df[c].fillna(0.0)

    eCO2_g_hp_hr = float(udp.get("bins", {}).get("eco2fcl", np.nan)[0])
    pmax_hp = float(udp.get("bins", {}).get("pmax", np.nan)[0])
    fuel_type = str(udp.get("log", {}).get("fuel", "Diesel")[0])
    fuel_density = float(udp.get("fuel", {}).get("fuel_sg", np.nan)[0])
    MPG = float(udp.get("scalar", {}).get("MPG", np.nan)[0])
    
    results = {}

    if fuel_type == "Diesel":
        df, summary_df, windows_df, sub_interval_df, invalid_count = calculate_maw_and_subintervals(df, eCO2_g_hp_hr, pmax_hp)

        if summary_df is not None and not summary_df.empty:
            print(f"Total Invalid Windows (>599s Excluded): {invalid_count}")

            epa_limits = {
                "Bin1_NOx_g_hr": 10.4,
                "Bin2_NOx_mg_hp_hr": 63.0,
                "Bin2_HC_mg_hp_hr": 130.0,
                "Bin2_PM_mg_hp_hr": 5.0,
                "Bin2_CO_g_hp_hr": 9.25,
                "Bin2_CO2_g_hp_hr": 600.0
            }
            compliance_df = evaluate_compliance(summary_df, epa_limits)
            print("--- EPA MAW Compliance Report ---")
            print(compliance_df)

            results["summary_df"] = summary_df
            results["windows_df"] = windows_df
            results["sub_interval_df"] = sub_interval_df
            results["compliance_df"] = compliance_df
 
            excel_file = Path('MAW_outputs.xlsx')

            # Start fresh (optional)
            if excel_file.exists():
                excel_file.unlink()

            with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                windows_df.to_excel(writer,        sheet_name='maw_detailed_windows',  index=False)
                summary_df.to_excel(writer,        sheet_name='maw_summary_averages',  index=False)
                compliance_df.to_excel(writer, sheet_name='maw_compliance_report', index=False)
                sub_interval_df.to_excel(writer,   sheet_name='sub_intervals_summary', index=False)

            print(f'Excel workbook written: {excel_file}')
        else:
            print("Error: No valid MAW data could be generated.")
            results["summary_df"] = pd.DataFrame()
            results["windows_df"] = pd.DataFrame()
            results["sub_interval_df"] = pd.DataFrame()
            results["compliance_df"] = pd.DataFrame()

        if do_plots:
            print("Generating visual analytics...")
            pdf_file = r'C:\Users\slee02\Matlab\RoadaC\shift_day_cumulative_emissions.pdf' # C:\Users\slee02\Matlab\RoadaC
            plot_shift_day_emissions(df, pdf_file=pdf_file)
            plot_cumulative_emissions(df, eCO2_g_hp_hr, pdf_file=pdf_file)

    elif fuel_type == "Gasoline":
        df, final_emissions, sub_interval_df = calculate_shift_day_emissions(df, eCO2_g_hp_hr, pmax_hp)

        # Simple data quality log
        total_sec = final_emissions["Total_Shift_Seconds"]
        valid_sec = final_emissions["Total_Valid_Seconds"]
        excluded_sec = final_emissions["Total_Excluded_Seconds"]
        print("--- Data Quality & Exclusion Summary ---")
        print(f"Total Shift Duration : {total_sec} seconds")
        print(f"Valid Data Points    : {valid_sec} seconds ({(valid_sec/total_sec)*100:.1f}%)")
        print(f"Excluded Data Points : {excluded_sec} seconds ({(excluded_sec/total_sec)*100:.1f}%)")
        results["final_emissions"] = final_emissions
        results["sub_interval_df"] = sub_interval_df
    else:
        raise ValueError("Unknown fuel type. Expected 'Diesel' or 'Gasoline'.")

        # Optionally compute MPG estimate if given density and distances
    if fuel_density is not None:
        gals = grams_to_gallons(df["instFuelRate"].fillna(0.0), fuel_density).sum()
        if gals > 0:
            # If you have a Distance_mi signal aggregated externally, use it; here we recompute:
            MPG_est = df["v_mph"].fillna(0.0).sum() / 3600.0 / gals
            print(f"MPG @ pems    : {MPG:.2f} , MPG_est {MPG_est:.2f}")

    setIdx = 1 # Placeholder; adapt as needed for multiple sets,
    vehData = raw
    reportPEMS_HDOffcycleBins(setIdx, excelfile.split('_udp')[0], vehData, udp, udp_scalar, scalarBinData, logData, binData, binData_avg)
    
    return df, results

    def read_udp(filepath):
        """Read UDP configuration from CSV file."""
        try:
            udp_df = pd.read_csv(filepath)
            return udp_df.iloc[0].to_dict()
        except Exception as e:
            print(f"Error reading UDP file {filepath}: {e}")
            return {}

# save_two_pages('your_report.pdf', fig_page1, fig, dpi=300)

def save_two_pages(pdf_file, fig_page1, fig_page2, dpi=300):
    with PdfPages(pdf_file) as pdf:
        pdf.savefig(fig_page1, bbox_inches='tight', dpi=dpi)
        pdf.savefig(fig_page2, bbox_inches='tight', dpi=dpi)

def append_fig_to_pdf(pdf_file, fig, dpi=300, bbox_inches='tight'):
    """
    Append a matplotlib Figure to an existing PDF, or create it if it doesn't exist.
    Ensures parent directory exists and writes atomically.
    """
    pdf_path = Path(pdf_file).expanduser().resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # If PDF doesn't exist, create with this figure as page 1
    if not pdf_path.exists():
        with PdfPages(pdf_path) as pdf:
            pdf.savefig(fig, bbox_inches=bbox_inches, dpi=dpi)
        print(f'Created: {pdf_path}')
        return

    # Render the figure to an in-memory single-page PDF
    buf = io.BytesIO()
    fig.savefig(buf, format='pdf', bbox_inches=bbox_inches, dpi=dpi)
    buf.seek(0)

    # Read existing PDF and new page(s), then write merged PDF
    with open(pdf_path, 'rb') as fh:
        old_reader = PdfReader(fh)
        new_reader = PdfReader(buf)
        writer = PdfWriter()
        for page in old_reader.pages:
            writer.add_page(page)
        for page in new_reader.pages:
            writer.add_page(page)

    # Atomic write
    tmp_path = pdf_path.with_suffix('.tmp.pdf')
    with open(tmp_path, 'wb') as out:
        writer.write(out)
    os.replace(tmp_path, pdf_path)
    print(f'Appended page to: {pdf_path}')
    
import numpy as np
try:
    # from scipy.io.matlab.mio5_params import mat_struct
    from scipy.io.matlab import mat_struct
except Exception:
    mat_struct = ()

def _mat_to_py(o):
    # mat_struct -> dict
    if isinstance(o, mat_struct):
        d = {}
        for k in o._fieldnames:
            d[k] = _mat_to_py(getattr(o, k))
        return d
    # numpy void (structured) -> dict
    if isinstance(o, np.void) and o.dtype.names:
        return {name: _mat_to_py(o[name]) for name in o.dtype.names}
    # structured array -> list of dicts
    if isinstance(o, np.ndarray) and o.dtype.names:
        return [_mat_to_py(x) for x in o.flat]
    # object array (cells) -> list
    if isinstance(o, np.ndarray) and o.dtype == object:
        return [_mat_to_py(x) for x in o.flat] if o.ndim > 0 else _mat_to_py(o.item())
    # basic arrays/scalars
    if isinstance(o, np.ndarray):
        return o
    return o

def first_existing_column(df, candidates):
    """Return the first column name from candidates that exists in df, else None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None

# Usage:

if __name__ == "__main__":
    try:
        # Run emissions analysis
        excelfile = "c:\\Users\\slee02\\Matlab\\RoadaC\\pp_2021_Volvo_VNL_White_HWY_20240429_M1-M97_udp.xlsx"
        binData_avg = pd.read_csv(r"c:\Users\slee02\Matlab\RoadaC\pp_2021_Volvo_VNL_White_HWY_20240429_M1-M97_binData.csv")
        # data = load_mat_v73('C:\\Users\\slee02\\Matlab\\RoadaC\\vehData.mat')
        # vehData = data.get('vehData')
        # logData = data.get('logData')
        # binData = data.get('binData')

        # raw = hdf5storage.loadmat('C:\\Users\\slee02\\Matlab\\RoadaC\\vehData.mat', struct_as_record=False, squeeze_me=True)
        # vehData_py = _mat_to_py(raw['vehData'])

        # excelfile = r"C:\Users\slee02\Matlab\RoadaC\pp_24Ford_F550_Urban_20250606_M25-M26_udp.xlsx"
        df, results = run_emissions_analysis(
            excelfile,
            binData_avg,
            raw=None,
            udp=None,
            MPG=None,
            fuel_density=0.832,
            do_plots=True
        )
        
        print("\n=== Analysis Complete ===")
        print(f"DataFrame shape: {df.shape}")
        print("\nResults keys:", results.keys())
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        traceback.print_exc()