"""
importDataMenu_App Python conversion (non-GUI)
- Uses globals() to emulate MATLAB base workspace
- Loads "user options" from JSON instead of MATLAB .mlx
- Loads measurement data from CSV (pandas DataFrame)
- Generates optional import summary PDF with ReportLab
"""

import os
import json
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# ------------------------------------------------------------------------------
# MATLAB "base workspace" equivalents using Python globals()
# ------------------------------------------------------------------------------

def get_base(name: str, default=None):
    """Emulate evalin('base', name)."""
    return globals().get(name, default)

def set_base(name: str, value: Any):
    """Emulate assignin('base', name, value)."""
    globals()[name] = value

def clear_base(keep: Optional[List[str]] = None):
    """Emulate 'clear all' (remove user variables from globals())."""
    if keep is None:
        keep = {
            '__name__', '__package__', '__doc__', '__builtins__',
            'get_base', 'set_base', 'clear_base',
            'unitConvert', 'load_options_json', 'load_measurement_data',
            'sdDataCalc', 'dynoDataCalc', 'pemsDataCalc',
            'importDataMenu_App', 'write_import_summary_pdf',
            'np', 'pd', 'letter', 'getSampleStyleSheet',
            'SimpleDocTemplate', 'Paragraph', 'Spacer'
        }
    for k in list(globals().keys()):
        if k not in keep and not k.startswith('_'):
            try:
                del globals()[k]
            except Exception:
                pass


# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------

def unitConvert(series: pd.Series, current_unit: str, to_unit: str) -> pd.Series:
    """
    Minimal unit converter for time:
    Supported units: sec/s, ms, min, hr/h.
    """
    if series is None or series.empty:
        return series

    u = (current_unit or "").strip().lower().replace("(", "").replace(")", "")
    t = (to_unit or "").strip().lower().replace("(", "").replace(")", "")

    if u == t or t in ("-", ""):
        return series

    def factor(from_u: str, to_u: str) -> float:
        # map unit -> seconds multiplier
        sec_map = {
            "sec": 1.0, "s": 1.0,
            "ms": 1.0 / 1000.0,
            "min": 60.0,
            "m": 60.0,
            "hr": 3600.0, "h": 3600.0, "hour": 3600.0, "hours": 3600.0,
        }
        fu = sec_map.get(from_u, None)
        tu = sec_map.get(to_u, None)
        if fu is None or tu is None:
            # Unknown unit, return identity (no conversion)
            return 1.0
        # convert: value_in_sec = value * fu, then to target: / tu
        return fu / tu

    f = factor(u, t)
    try:
        return series.astype(float) * f
    except Exception:
        # If not numeric, return as-is
        return series


def load_options_json(path: str) -> Dict[str, Any]:
    """
    Load a 'user options' JSON file to emulate 'udo' struct from MATLAB .mlx.
    Expected keys:
      - "log": {"dataType": "...", "oem": "...", "model": "...", "my": "...",
                "fuel": "...", "testCycle": "...", "dateTime": "..."}
      - For each method (sd/dyno/pems/can): e.g., "pems": {"time": "Time"}
    """
    with open(path, 'r', encoding='utf-8') as f:
        udo = json.load(f)
    return udo


def load_measurement_data(path: str) -> pd.DataFrame:
    """
    Load measurement data from CSV into a pandas DataFrame.
    This emulates MATLAB's table used in the app (vehDataT).
    """
    df = pd.read_csv(path)
    # Attach a place to keep column units (like MATLAB table.VariableUnits)
    # Use DataFrame.attrs for a simple units dict keyed by column name.
    df.attrs['units'] = {col: '' for col in df.columns}
    # Also a user_data vector like MATLAB Properties.UserData (label offsets)
    df.attrs['user_data'] = np.zeros(len(df.columns), dtype=float)
    return df


# ------------------------------------------------------------------------------
# Calculation stubs – extend with your domain logic as needed
# ------------------------------------------------------------------------------

def sdDataCalc(setIdx: int, vehData: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Placeholder – insert Signature Device calculations
    return vehData

def dynoDataCalc(setIdx: int, vehData: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Placeholder – insert Chassis Dyno calculations
    return vehData

def pemsDataCalc(setIdx: int, vehData: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Placeholder – insert PEMS calculations
    return vehData


# ------------------------------------------------------------------------------
# ReportLab: optional import summary PDF (not in the MATLAB app, but useful)
# ------------------------------------------------------------------------------

def write_import_summary_pdf(pdf_path: str, dataset: Dict[str, Any]):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    flow = []

    flow.append(Paragraph("Import Summary", styles['Title']))
    flow.append(Spacer(1, 12))

    # Basic fields
    flow.append(Paragraph(f"Name: {dataset.get('name', 'Default')}", styles['Normal']))
    flow.append(Paragraph(f"Figure Title: {dataset.get('figtitle1', '')}", styles['Normal']))
    flow.append(Paragraph(f"Method: {dataset.get('method', '')}", styles['Normal']))
    flow.append(Paragraph(f"Calc Set: {dataset.get('calcSet', 0)}", styles['Normal']))

    # Time step
    ts = dataset.get('timeStep', None)
    if ts is not None:
        flow.append(Paragraph(f"Computed Time Step: {ts} sec", styles['Normal']))

    # Data columns summary
    df: pd.DataFrame = dataset.get('data')
    if isinstance(df, pd.DataFrame):
        flow.append(Spacer(1, 8))
        flow.append(Paragraph(f"Data Columns: {', '.join(df.columns.astype(str))}", styles['Normal']))
        flow.append(Paragraph(f"Rows: {len(df)}", styles['Normal']))

    doc.build(flow)
    print(f"[import summary] Wrote {pdf_path}")


# ------------------------------------------------------------------------------
# App conversion
# ------------------------------------------------------------------------------

class importDataMenu_App:
    """
    A non-GUI analogue of MATLAB importDataMenu_App that:
      - Pulls numSet, vehData, udp from Python globals() (base workspace)
      - Loads options (udo) from JSON and measurement data from CSV
      - Computes time step, builds tempData, and appends to vehData
      - Updates base workspace variables: numSet, vehData, udp
    """

    def __init__(self):
        # Private props
        self.numSet: int = int(get_base('numSet', 0))
        self.vehData: List[Dict[str, Any]] = get_base('vehData', [])
        self.udp: List[Dict[str, Any]] = get_base('udp', [])

        self.tempUser: Dict[str, Any] = {}  # temporary 'udo'
        self.tempData: Dict[str, Any] = {}  # temporary vehData struct
        self.vehDataT: Optional[pd.DataFrame] = None

        self.vehLogFlag: int = 0
        self.vehDataFlag: int = 0

        self.startup()

    # ---------------- startupFcn ----------------
    def startup(self):
        # Bring in number of datasets and vehicle database from base
        self.numSet = int(get_base('numSet', 0))
        self.vehData = get_base('vehData', [])
        self.udp = get_base('udp', [])

        # Populate current dataset list (just print here)
        if self.numSet:
            names = [str(d.get('name', 'unnamed')) for d in (self.vehData or [])]
            print("[startup] Current datasets:", names)
        else:
            print("[startup] Current datasets: empty")

        # Initialize tempData and tempUser
        self.tempData = {
            'name': "Default",
            'method': 'pems',
            'logData': {},      # In MATLAB this is a table; here we keep dict for log
            'scalarData': {},   # Placeholder for scalar data
            'figtitle1': "Figure Title",
            'offset': 0.0,
            'shift': 0.0
        }
        self.tempUser = {'log': {}}

        # Reset flags
        self.vehLogFlag = 0
        self.vehDataFlag = 0

    # -------------- ImportOptionsFileButtonPushed --------------
    def import_options(self, options_json_path: str):
        """
        Select and load user options (UDO) from a JSON file (instead of MATLAB .mlx).
        Sets tempUser and tempData.method; builds figtitle1 from log fields.
        """
        # Reset state similar to MATLAB
        self.tempUser = {}
        self.vehLogFlag = 0
        self.vehDataT = None
        self.vehDataFlag = 0
        self.tempData['timeStep'] = 0.0
        self.tempData['filename'] = ''
        self.tempData['figtitle1'] = 'Figure Title'

        # Load UDO
        udo = load_options_json(options_json_path)
        self.tempUser = udo

        # Decide method from dataType
        data_type = (self.tempUser.get('log', {}).get('dataType', '') or '').lower()
        method = {
            'none': 'none',
            'miniroad': 'sd',
            'minidyno': 'sd',
            'raw': 'dyno',
            'dilute': 'dyno',
            'pems': 'pems',
            'can': 'can',
        }.get(data_type, 'pems')
        self.tempData['method'] = method

        # Store logData (dict) and units map
        log = self.tempUser.get('log', {})
        # Units map for log-like fields (for completeness; not used in title)
        log_units = {
            'dateTime': '(-)',
            'oem': '(-)', 'model': '(-)', 'my': '(-)', 'vehicleID': '(-)', 'vin': '(-)',
            'odo': '(miles)', 'testCycle': '(-)', 'testLocation': '(-)',
            'thcAmbCorr': '(ppm)', 'noxAmbCorr': '(ppm)', 'coAmbCorr': '(ppm)', 'co2AmbCorr': '(%)',
            'ambientT': '(C)', 'rHumidity': '(%)', 'baro': '(mbar)', 'fuel': '(-)',
            'ftag': '(-)', 'notes': '(-)', 'filter1ID': '(-)', 'filter1WtPre': '(mg)',
            'filter1WtPost': '(mg)', 'filter2ID': '(-)', 'filter2WtPre': '(mg)',
            'filter2WtPost': '(mg)', 'noRefSpan': '(ppm)', 'no2RefSpan': '(ppm)',
            'coRefSpan': '(ppm)', 'co2RefSpan': '(%)', 'thcRefSpan': '(ppm)'
        }
        self.tempData['logData'] = dict(log)          # store values
        self.tempData['logUnits'] = dict(log_units)   # store units

        # Build figtitle1
        oem = str(log.get('oem', ''))
        model = str(log.get('model', ''))
        my = str(log.get('my', ''))
        fuel = str(log.get('fuel', ''))
        testCycle = str(log.get('testCycle', ''))
        dateTime = str(log.get('dateTime', ''))
        figtitle1 = f"{oem} {model} {my} {fuel} {testCycle} {dateTime}".strip()
        self.tempData['figtitle1'] = figtitle1 or "Figure Title"

        # Set flag for log data imported
        self.vehLogFlag = 1

        print(f"[options] Loaded '{options_json_path}'. method={self.tempData['method']}, figtitle1='{self.tempData['figtitle1']}'")

    # -------------- ImportDataFileButtonPushed --------------
    def import_data_file(self, csv_path: str):
        """
        Load measurement data file (CSV) to vehDataT, compute time step,
        and set vehDataFlag.
        """
        self.vehDataT = load_measurement_data(csv_path)
        self.tempData['filename'] = csv_path

        # Compute time step from first and last sample of the configured time column
        uop = self.tempData.get('method', 'pems')
        time_col = self.tempUser.get(uop, {}).get('time', None)
        if time_col is None or time_col not in self.vehDataT.columns:
            # If no time col provided, just set 0.0
            self.tempData['timeStep'] = 0.0
            print("[data] Time column not provided or not in CSV; timeStep=0.0")
        else:
            # Initialize units store for DataFrame
            units = self.vehDataT.attrs.get('units', {})
            if time_col not in units:
                units[time_col] = ''  # unknown by default
            self.vehDataT.attrs['units'] = units

            time_series = self.vehDataT[time_col]
            n = len(time_series)
            if n > 1:
                # (max-min)/(n-1) using first and last entries (consistent with MATLAB app comment)
                try:
                    t0 = float(time_series.iloc[0])
                    t1 = float(time_series.iloc[-1])
                    ts = (t1 - t0) / (n - 1)
                    self.tempData['timeStep'] = round(ts, 3)
                except Exception:
                    self.tempData['timeStep'] = 0.0
            else:
                self.tempData['timeStep'] = 0.0

        self.vehDataFlag = 1
        print(f"[data] Loaded '{csv_path}'. timeStep={self.tempData['timeStep']}")

    # -------------- FigTitleEdit / Apply --------------
    def fig_title_edit(self):
        # In MATLAB, this just enables editing; here we do nothing.
        print("[figtitle] Ready to edit.")

    def fig_title_apply(self, new_title: str):
        self.tempData['figtitle1'] = new_title
        print(f"[figtitle] Applied new title: '{new_title}'")

    # -------------- DatasetNameEditFieldValueChanged --------------
    def set_dataset_name(self, name: str):
        self.tempData['name'] = name
        print(f"[dataset] Name set to '{name}'")

    # -------------- Edit/Apply TimeStep --------------
    def edit_time_step(self):
        print("[timestep] Editing enabled.")

    def apply_time_step(self, value: float):
        self.tempData['timeStep'] = float(value)
        print(f"[timestep] Applied manual timeStep={self.tempData['timeStep']}")

    # -------------- CreateButtonPushed --------------
    """
    % determine the calculation set
    % calcSet = 0:  None
    % calcSet = 1:  Mini-PEMS - Road
    % calcSet = 2:  Mini-PEMS - Dyno
    % calcSet = 3:  Chassis Dyno - Raw
    % calcSet = 4:  Chassis Dyno - Dilute
    % calcSet = 5:  PEMS
    % calcSet = 6:  CAN
    
    % valueMethod=app.MethodDropDown.Value;
    % valueCalcSet=app.CalculationSetDropDown.Value;
    """
    def create_dataset(self, write_summary_pdf: Optional[str] = None):
        """
        Combine tempData and vehDataT; convert time to seconds (if needed);
        run calculation set; update base workspace (numSet, vehData, udp).
        Optionally write a ReportLab PDF summary.
        """
        if not (self.vehLogFlag == 1 and self.vehDataFlag == 1):
            print("[create] Not ready (need both options and data).")
            return

        # Determine calculation set from dataType
        dt = (self.tempUser.get('log', {}).get('dataType', '') or '').lower()
        calc_set_map = {
            'none': 0, 'miniroad': 1, 'minidyno': 2,
            'raw': 3, 'dilute': 4, 'pems': 5, 'can': 6
        }
        calc_set = calc_set_map.get(dt, 0)
        self.tempData['calcSet'] = calc_set

        # CAN: ensure time units set to (sec) for timestep check
        uop = self.tempData.get('method', 'pems')
        if calc_set == 6 and isinstance(self.vehDataT, pd.DataFrame):
            tcol = self.tempUser.get('can', {}).get('time', None)
            if tcol and tcol in self.vehDataT.columns:
                units = self.vehDataT.attrs.get('units', {})
                units[tcol] = '(sec)'
                self.vehDataT.attrs['units'] = units

        # Convert time column to seconds and start at zero (if calcSet != 0)
        if calc_set != 0 and isinstance(self.vehDataT, pd.DataFrame):
            tcol = self.tempUser.get(uop, {}).get('time', None)
            if tcol and tcol in self.vehDataT.columns:
                units = self.vehDataT.attrs.get('units', {})
                cur_unit = units.get(tcol, '')
                # Convert to seconds
                self.vehDataT[tcol] = unitConvert(self.vehDataT[tcol], cur_unit, 'sec')
                units[tcol] = '(sec)'
                self.vehDataT.attrs['units'] = units
                # Start at zero
                try:
                    self.vehDataT[tcol] = self.vehDataT[tcol] - self.vehDataT[tcol].iloc[0]
                except Exception:
                    pass

        # Combine tempData (log) and measurement data into one dataset
        self.tempData['data'] = self.vehDataT

        # Bring the dataset into vehData
        if not self.numSet:
            self.vehData = [self.tempData.copy()]
            self.udp = [self.tempUser.copy()]
            self.numSet = 1
        else:
            self.vehData.append(self.tempData.copy())
            self.udp.append(self.tempUser.copy())
            self.numSet += 1

        setIdx = self.numSet  # 1-based like MATLAB

        # Run calculation set (stubs)
        """
        % % -----------------------  Start of Calculation Set
        % calcSet = 0:  None/User
        % calcSet = 1:  Signature Device - Road
        % calcSet = 2:  Signature Device - Dyno
        % calcSet = 3:  Chassis Dyno - Raw
        % calcSet = 4:  Chassis Dyno - Dilute
        % calcSet = 5:  PEMS - Road
        % calcSet = 6:  CAN
        """
        if calc_set in (1, 2):
            self.vehData = sdDataCalc(setIdx, self.vehData)
        elif calc_set in (3, 4):
            self.vehData = dynoDataCalc(setIdx, self.vehData)
        elif calc_set == 5:
            self.vehData = pemsDataCalc(setIdx, self.vehData)

        # Round time to three decimals if not calcSet 0
        """
        % % round the time to three decimals.  It can happen that there is a small
        % % round-off error in Matlab and, for example, zero can be calculated as a
        % % small number like -1e-15.  this can cause issues when creating a table
        % % subset such as vehData.Data.Time >=0 when "0" time is not identically
        % % zero.
        """
        if calc_set != 0:
            tcol = self.tempUser.get(uop, {}).get('time', None)
            try:
                if tcol and isinstance(self.vehData[setIdx - 1]['data'], pd.DataFrame):
                    df = self.vehData[setIdx - 1]['data']
                    df[tcol] = np.round(df[tcol].astype(float), 3)
            except Exception:
                pass

        # Push to base workspace
        set_base('numSet', self.numSet)
        set_base('vehData', self.vehData)
        set_base('udp', self.udp)

        # Update dataset list (print)
        names = [str(d.get('name', 'unnamed')) for d in self.vehData]
        print("[create] Dataset created. Current datasets:", names)

        # Optional: write a brief PDF import summary
        if write_summary_pdf:
            try:
                write_import_summary_pdf(write_summary_pdf, self.vehData[setIdx - 1])
            except Exception as e:
                print(f"[create] Failed to write PDF summary: {e}")