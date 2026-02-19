import os
import json
import csv
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Union

import numpy as np
from scipy.io import loadmat, savemat

# ReportLab
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

# ------------------------------------------------------------------------------
# MATLAB "base workspace" equivalents using Python globals()
# ------------------------------------------------------------------------------

def get_base(name: str, default=None):
    """Emulate evalin('base', name)."""
    return globals().get(name, default)

def set_base(name: str, value: Any):
    """Emulate assignin('base', name, value)."""
    globals()[name] = value

def clear_base(keep: List[str] = None):
    """Emulate 'clear all' (keep some symbols)."""
    if keep is None:
        keep = ['__name__', '__package__', '__doc__', '__builtins__',
                'get_base', 'set_base', 'clear_base', 'openvar',
                'homeMenu_App', 'build_report', 'mat_to_native',
                'mat_struct_to_dict', 'main', 'np', 'loadmat', 'savemat',
                'tk', 'filedialog', 'messagebox', 'Any', 'Dict', 'List', 'Union',
                'os', 'json', 'csv', 'sys', 'letter', 'getSampleStyleSheet',
                'SimpleDocTemplate', 'Paragraph', 'Spacer', 'Table', 'TableStyle',
                'PageBreak', 'colors']
    for k in list(globals().keys()):
        if k not in keep and not k.startswith('_'):
            try:
                del globals()[k]
            except Exception:
                pass

def openvar(name: str, outdir: str = '.'):
    """
    Emulate MATLAB's openvar: write variable content to a JSON or CSV
    for quick inspection. If it's tabular, write CSV; else JSON.
    """
    val = get_base(name)
    if val is None:
        print(f"[openvar] Variable '{name}' not found in globals().")
        return

    # Try CSV for list of dicts or 2D arrays
    try:
        basepath = os.path.join(outdir, f"{name}")
        if isinstance(val, list) and val and isinstance(val[0], dict):
            # Write CSV for list of dicts
            headers = sorted({h for row in val for h in row.keys()})
            csv_path = basepath + ".csv"
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for row in val:
                    writer.writerow({h: row.get(h, "") for h in headers})
            print(f"[openvar] Wrote {csv_path}")
            return

        if isinstance(val, (np.ndarray, list)) and np.array(val).ndim == 2:
            csv_path = basepath + ".csv"
            arr = np.array(val, dtype=object)
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for r in arr:
                    writer.writerow([str(x) for x in r])
            print(f"[openvar] Wrote {csv_path}")
            return
    except Exception as e:
        print(f"[openvar] CSV fallback failed: {e}; will write JSON.")

    json_path = os.path.join(outdir, f"{name}.json")
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(val, f, indent=2, default=str)
        print(f"[openvar] Wrote {json_path}")
    except TypeError:
        # Convert to JSON-serializable
        def default_conv(o):
            try:
                return o.tolist()
            except Exception:
                return str(o)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(val, f, indent=2, default=default_conv)
        print(f"[openvar] Wrote {json_path} (with default converter)")

# ------------------------------------------------------------------------------
# .mat helpers – convert MATLAB structs to Python-native types
# ------------------------------------------------------------------------------

def mat_to_native(x: Any) -> Any:
    """
    Convert SciPy-loaded MATLAB data to Python-native structures:
    - MATLAB char arrays -> Python str
    - MATLAB cell arrays -> Python list
    - MATLAB struct arrays -> dict/list
    """
    # Strings
    if isinstance(x, np.ndarray) and x.dtype.char in ('U', 'S'):
        # Char array -> string
        return ''.join(x.tolist()).strip()

    # Numeric arrays -> Python types where possible
    if isinstance(x, np.ndarray) and x.dtype != object:
        # Flatten single element arrays
        if x.size == 1:
            return x.squeeze().item()
        return x

    # Cell arrays or object arrays -> list of elements
    if isinstance(x, np.ndarray) and x.dtype == object:
        if x.size == 1:
            return mat_to_native(x.item())
        return [mat_to_native(elem) for elem in x.flat]

    # Structured array (MATLAB struct)
    if isinstance(x, np.ndarray) and x.dtype.names:
        return mat_struct_to_dict(x)

    # Fallback
    return x

def mat_struct_to_dict(arr: np.ndarray) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Convert MATLAB struct (as numpy structured array) to dict(s).
    Handles struct arrays -> list of dicts; single struct -> dict.
    """
    def _one(rec) -> Dict[str, Any]:
        out = {}
        for name in rec.dtype.names:
            val = rec[name]
            # val might still be ndarray; convert recursively
            out[name] = mat_to_native(val)
        return out

    if arr.size == 1:
        return _one(arr.squeeze())
    else:
        # Vector of structs -> list of dicts
        return [_one(arr.flat[i]) for i in range(arr.size)]

# ------------------------------------------------------------------------------
# Report generation with ReportLab
# ------------------------------------------------------------------------------

def build_report(pdf_path: str, veh_data: List[Dict[str, Any]]):
    """
    Generate a PDF summarizing datasets, like a "Report" button would.
    veh_data: list of dicts with fields like ["name", "figtitle1", "data", "logData", "scalarData"].
    """
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    flow = []

    title = "Vehicle Dataset Report"
    flow.append(Paragraph(title, styles['Title']))
    flow.append(Spacer(1, 12))

    if not veh_data:
        flow.append(Paragraph("No datasets available.", styles['Normal']))
        doc.build(flow)
        print(f"[report] Wrote {pdf_path}")
        return

    # Summary table header
    table_data = [["Index", "Name", "Figure Title", "Data shape/info"]]
    for idx, d in enumerate(veh_data, start=1):
        name = str(d.get('name', ''))
        # Some MATLAB loads may bring 'name' as list or array; normalize
        if isinstance(name, list):
            name = ', '.join(map(str, name))
        figtitle = d.get('figtitle1', '')
        if isinstance(figtitle, list):
            figtitle = ', '.join(map(str, figtitle))

        # Infer data shape
        data_info = ""
        if 'data' in d:
            val = d['data']
            try:
                arr = np.array(val, dtype=object)
                data_info = f"{arr.shape}"
            except Exception:
                data_info = f"type={type(val).__name__}"
        table_data.append([str(idx), name, str(figtitle), data_info])

    t = Table(table_data, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 12))

    # Add per-dataset section
    for idx, d in enumerate(veh_data, start=1):
        flow.append(PageBreak())
        flow.append(Paragraph(f"Dataset {idx}", styles['Heading2']))

        name = d.get('name', '')
        figtitle = d.get('figtitle1', '')
        flow.append(Paragraph(f"Name: {name}", styles['Normal']))
        flow.append(Paragraph(f"Figure Title: {figtitle}", styles['Normal']))
        flow.append(Spacer(1, 6))

        # Optional: additional metadata
        for key in ['scalarData', 'logData']:
            if key in d:
                meta = d[key]
                meta_summary = f"type={type(meta).__name__}"
                try:
                    if isinstance(meta, (list, dict)):
                        meta_summary += f", size/len={len(meta)}"
                    else:
                        arr = np.array(meta, dtype=object)
                        meta_summary += f", shape={arr.shape}"
                except Exception:
                    pass
                flow.append(Paragraph(f"{key}: {meta_summary}", styles['Normal']))

    doc.build(flow)
    print(f"[report] Wrote {pdf_path}")

# ------------------------------------------------------------------------------
# Application skeleton that mirrors core MATLAB callbacks (no GUI)
# ------------------------------------------------------------------------------

class homeMenu_App:
    """
    A minimal, non-GUI analogue of the MATLAB homeMenu_App focusing on:
      - Base workspace (globals) interaction
      - Open/Save .mat
      - Dataset selection
      - Report generation with ReportLab
    """

    def __init__(self):
        self.current_index = 0  # 0-based
        self.refresh_from_globals()

    # ---------------- Base workspace sync ----------------

    def refresh_from_globals(self):
        self.numSet = bool(get_base('numSet', False))
        self.vehData = get_base('vehData', [])
        # Normalize vehData into a list of dicts if possible
        self.vehData = self._normalize_vehdata(self.vehData)
        self.numSet = bool(self.vehData)  # if list not empty

    def push_to_globals(self):
        set_base('vehData', self.vehData)
        set_base('numSet', bool(self.vehData))

    def _normalize_vehdata(self, vehData) -> List[Dict[str, Any]]:
        if vehData is None:
            return []
        # Already a list of dicts?
        if isinstance(vehData, list) and (not vehData or isinstance(vehData[0], dict)):
            return vehData
        # MATLAB struct loaded as numpy structured array
        if isinstance(vehData, np.ndarray):
            try:
                obj = mat_to_native(vehData)
                # obj may now be dict or list of dicts
                if isinstance(obj, dict):
                    return [obj]
                if isinstance(obj, list) and (not obj or isinstance(obj[0], dict)):
                    return obj
            except Exception:
                pass
        # Fallback: wrap as-is
        return [vehData] if vehData else []

    # ---------------- File actions ----------------

    def open_mat(self, path: str = None):
        """
        Equivalent to: evalin('base', 'clear all'); uiopen('*.mat')
        """
        if path is None:
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(
                title="Open MAT file",
                filetypes=[("MAT-files", "*.mat"), ("All files", "*.*")]
            )
            root.destroy()
            if not path:
                print("[open_mat] Cancelled.")
                return

        print(f"[open_mat] Loading {path}")
        # For v7.3 .mat files consider using mat73.loadmat(path) instead.
        data = loadmat(path, squeeze_me=True, struct_as_record=False)

        # Clear base and then populate with items from the MAT file
        clear_base()
        # Transfer keys while skipping meta keys
        for k, v in data.items():
            if k.startswith('__'):
                continue
            set_base(k, mat_to_native(v))

        # Refresh local cache
        self.refresh_from_globals()
        print("[open_mat] Loaded. Variables in base:", [k for k in globals().keys() if not k.startswith('_')])

    def save_mat(self, path: str = None):
        """
        Equivalent to: evalin('base','uisave')
        Save all current globals except internal ones.
        """
        if path is None:
            root = tk.Tk()
            root.withdraw()
            path = filedialog.asksaveasfilename(
                title="Save MAT file",
                defaultextension=".mat",
                filetypes=[("MAT-files", "*.mat"), ("All files", "*.*")]
            )
            root.destroy()
            if not path:
                print("[save_mat] Cancelled.")
                return

        payload = {}
        for k, v in globals().items():
            if k.startswith('_'):
                continue
            # skip non-user keys (heuristic)
            if callable(v):
                continue
            if k in ('tk', 'filedialog', 'messagebox', 'np', 'loadmat', 'savemat'):
                continue
            payload[k] = v

        print(f"[save_mat] Saving {len(payload)} variables to {path}")
        try:
            savemat(path, payload, do_compression=True)
            print("[save_mat] Done.")
        except NotImplementedError:
            # If some objects can't be saved directly, prune them
            safe_payload = {}
            for k, v in payload.items():
                try:
                    savemat(path, {k: v})
                    safe_payload[k] = v
                except Exception:
                    print(f"[save_mat] Skipping non-savable: {k}")
            savemat(path, safe_payload, do_compression=True)
            print("[save_mat] Done with reduced set.")

    # ---------------- Dataset operations ----------------

    def dataset_names(self) -> List[str]:
        names = []
        for d in self.vehData:
            n = d.get('name', 'unnamed')
            if isinstance(n, (list, tuple)):
                n = ' '.join(map(str, n))
            names.append(str(n))
        return names or ['empty']

    def select_dataset(self, index_1based: int):
        """
        popDataset_Callback equivalent: set current dataset
        """
        if not self.vehData:
            print("[select_dataset] No datasets available.")
            self.current_index = 0
            return
        idx0 = max(0, min(index_1based - 1, len(self.vehData) - 1))
        self.current_index = idx0
        title = self.vehData[idx0].get('figtitle1', 'empty')
        print(f"[select_dataset] Selected index={index_1based}, figtitle1={title}")

    # ---------------- UI-equivalent actions ----------------

    def action_open(self):
        """homeOpen: clear base, open mat, re-open home menu (stub)."""
        print("[action_open] Clearing base and opening MAT...")
        clear_base()
        self.open_mat()
        # In MATLAB: close level0 and re-launch. Here we just refresh.
        self.refresh_from_globals()

    def action_save(self):
        """homeSave: uisave equivalent."""
        self.save_mat()

    def action_report(self, out_pdf: str = "report.pdf"):
        """ReportButton: build a PDF."""
        if not self.vehData:
            print("[action_report] No data available to report.")
            return
        build_report(out_pdf, self.vehData)

    def action_open_vehData(self):
        """TopStrucButton / uipushStruc: openvar('vehData') equivalent."""
        if not self.vehData:
            print("[action_open_vehData] No data available.")
            return
        set_base('vehData', self.vehData)  # ensure current
        openvar('vehData')

    def action_open_vector(self):
        """pushOpenVar: open vehData(k).data"""
        if not self.vehData:
            print("[action_open_vector] No data available.")
            return
        k = self.current_index
        data_var = self.vehData[k].get('data', None)
        if data_var is None:
            print("[action_open_vector] vehData.data not found.")
            return
        tmp_name = f"vehData_{k+1}_data"
        set_base(tmp_name, data_var)
        openvar(tmp_name)

    def action_open_scalar(self):
        """pushScalar: open vehData(k).scalarData"""
        if not self.vehData:
            print("[action_open_scalar] No data available.")
            return
        k = self.current_index
        data_var = self.vehData[k].get('scalarData', None)
        if data_var is None:
            print("[action_open_scalar] vehData.scalarData not found.")
            return
        tmp_name = f"vehData_{k+1}_scalarData"
        set_base(tmp_name, data_var)
        openvar(tmp_name)

    def action_open_log(self):
        """pushLog: open vehData(k).logData"""
        if not self.vehData:
            print("[action_open_log] No data available.")
            return
        k = self.current_index
        data_var = self.vehData[k].get('logData', None)
        if data_var is None:
            print("[action_open_log] vehData.logData not found.")
            return
        tmp_name = f"vehData_{k+1}_logData"
        set_base(tmp_name, data_var)
        openvar(tmp_name)

    # Stubs for operations handled elsewhere in MATLAB
    def action_import(self):
        print("[action_import] Import menu not implemented (stub).")

    def action_filter(self):
        print("[action_filter] Filter menu not implemented (stub).")

    def action_sync(self):
        print("[action_sync] Sync menu not implemented (stub).")

    def action_operator(self):
        print("[action_operator] MathOperator not implemented (stub).")

    def action_scale_offset(self):
        print("[action_scale_offset] ScaleAndOffset not implemented (stub).")

    def action_drift(self):
        print("[action_drift] DriftComp not implemented (stub).")

    def action_mass_flow(self):
        print("[action_mass_flow] Mass Flow not implemented (stub).")

    def action_recalculate(self):
        print("[action_recalculate] Recalculate not implemented (stub).")

    def action_merge(self):
        print("[action_merge] Merge not implemented (stub).")

# ------------------------------------------------------------------------------
# Example usage
# ------------------------------------------------------------------------------

def main():
    # Optional: seed with existing globals (e.g., from prior session)
    # set_base('numSet', False)
    # set_base('vehData', [])

    app = homeMenu_App()

    # Emulate MATLAB "Open"
    app.action_open()  # will prompt file dialog

    # List datasets and choose one (1-based like MATLAB)
    names = app.dataset_names()
    print("Datasets:", names)
    if names and names[0] != 'empty':
        app.select_dataset(1)

    # Inspect top-level struct like openvar('vehData')
    app.action_open_vehData()

    # Inspect vector/scalar/logData fields of selected dataset
    app.action_open_vector()
    app.action_open_scalar()
    app.action_open_log()

    # Generate a ReportLab PDF
    app.action_report("veh_report.pdf")

    # Save current base workspace to a new .mat
    app.action_save()

if __name__ == '__main__':
    # If running in a headless environment, suppress Tk warnings
    try:
        main()
    except tk.TclError as e:
        print(f"[tkinter] {e}. File dialogs may not work in this environment.")
        sys.exit(1)