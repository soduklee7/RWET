# sync_menu_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Colors
REF_COLOR = (32/255, 135/255, 34/255)
SYNC_COLOR = (198/255, 56/255, 0/255)

def x_corr_shift(y_ref, y_sync):
    """
    Compute cross-correlation shift (lag in samples) aligning y_sync to y_ref.
    Positive lag means y_sync should be moved forward in time by 'lag' samples.
    NaNs are replaced by 0 after normalization (z-score with nanmean/nanstd).
    Returns lag_samples (int).
    """
    y_ref = np.asarray(y_ref, dtype=float)
    y_sync = np.asarray(y_sync, dtype=float)
    n = min(len(y_ref), len(y_sync))
    if len(y_ref) != len(y_sync):
        # Pad shorter to match longer for correlation; use the first n samples to simplify
        y_ref = y_ref[:n]
        y_sync = y_sync[:n]
    # Normalize
    mu_ref = np.nanmean(y_ref) if np.isfinite(np.nanmean(y_ref)) else 0.0
    mu_sync = np.nanmean(y_sync) if np.isfinite(np.nanmean(y_sync)) else 0.0
    std_ref = np.nanstd(y_ref)
    std_sync = np.nanstd(y_sync)
    std_ref = std_ref if std_ref > 0 else 1.0
    std_sync = std_sync if std_sync > 0 else 1.0
    y_ref_z = (y_ref - mu_ref) / std_ref
    y_sync_z = (y_sync - mu_sync) / std_sync
    # Replace NaNs with zeros
    y_ref_z = np.where(np.isfinite(y_ref_z), y_ref_z, 0.0)
    y_sync_z = np.where(np.isfinite(y_sync_z), y_sync_z, 0.0)
    # Cross-correlation with 'full' mode
    corr = np.correlate(y_ref_z, y_sync_z, mode='full')
    lags = np.arange(-(len(y_sync_z) - 1), len(y_ref_z))
    max_idx = np.argmax(corr)
    lag = int(lags[max_idx])
    return lag

def nearest_point(x, y, x_click):
    """
    Find nearest point in x to x_click, ignoring NaNs.
    Returns (idx, (x[idx], y[idx])).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size == 0:
        return None, (np.nan, np.nan)
    mask = np.isfinite(x)
    if not np.any(mask):
        return None, (np.nan, np.nan)
    idx_valid = np.where(mask)[0]
    x_valid = x[mask]
    # Find nearest index
    diffs = np.abs(x_valid - x_click)
    j = int(np.argmin(diffs))
    idx = int(idx_valid[j])
    return idx, (x[idx], y[idx] if idx < len(y) else np.nan)

def resample_nearest(x_src, y_src, x_target):
    """
    Resample y_src defined at x_src onto x_target using nearest neighbor.
    Returns y_out with shape of x_target.
    """
    x_src = np.asarray(x_src, dtype=float)
    y_src = np.asarray(y_src, dtype=float)
    x_target = np.asarray(x_target, dtype=float)
    if x_src.size == 0:
        return np.full_like(x_target, np.nan, dtype=float)
    # Ensure x_src is sorted; if not, sort both
    if not np.all(np.diff(x_src) >= 0):
        order = np.argsort(x_src)
        x_src_sorted = x_src[order]
        y_src_sorted = y_src[order]
    else:
        x_src_sorted = x_src
        y_src_sorted = y_src
    # Use searchsorted to find insertion positions
    idxs = np.searchsorted(x_src_sorted, x_target, side='left')
    idxs = np.clip(idxs, 0, len(x_src_sorted)-1)
    # Compare left and right neighbor where possible
    left = np.maximum(idxs - 1, 0)
    right = np.minimum(idxs, len(x_src_sorted)-1)
    # Distances
    dleft = np.abs(x_target - x_src_sorted[left])
    dright = np.abs(x_src_sorted[right] - x_target)
    choose_left = dleft <= dright
    nearest_idx = np.where(choose_left, left, right)
    y_out = y_src_sorted[nearest_idx]
    return y_out

def label_offset(vehData, udp, offset, syncSetIdx, syncLabName, apply_label, pad_method, write=False, ref_time=None):
    """
    Compute shifted sync series based on offset and pad method.
    pad_method: 0 -> "NaN": return (time_sync + offset, y_sync)
                1 -> "Nearest": resample y_sync(time_sync + offset) onto ref_time using nearest neighbor; requires ref_time.
    If write=True:
        - pad_method==1: update vehData[syncIdx]['data'][syncLabName] = yOffset (demo).
        - pad_method==0: record applied offset in vehData[syncIdx]['applied_offsets'][syncLabName]
    Returns (xOffset, yOffset)
    """
    # Determine time series for sync dataset
    try:
        method = vehData[syncSetIdx].get('method', 'none')
        time_col = udp[syncSetIdx][method]['time']
        df_sync = vehData[syncSetIdx]['data']
        if time_col not in df_sync.columns:
            raise KeyError(f"Time column '{time_col}' not found in dataset {vehData[syncSetIdx]['name']}")
        if syncLabName not in df_sync.columns:
            raise KeyError(f"Label '{syncLabName}' not found in dataset {vehData[syncSetIdx]['name']}")
        x_sync = np.asarray(df_sync[time_col].values, dtype=float)
        y_sync = np.asarray(df_sync[syncLabName].values, dtype=float)
    except Exception as e:
        raise e

    if pad_method == 0:
        # NaN padding (no resample), just shift x by offset
        xOffset = x_sync + float(offset)
        yOffset = y_sync.copy()
        if write:
            # Record applied offset (demo meta)
            if 'applied_offsets' not in vehData[syncSetIdx]:
                vehData[syncSetIdx]['applied_offsets'] = {}
            vehData[syncSetIdx]['applied_offsets'][syncLabName] = float(offset)
        return xOffset, yOffset
    elif pad_method == 1:
        if ref_time is None:
            raise ValueError("ref_time is required for 'Nearest' padding.")
        x_shifted = x_sync + float(offset)
        y_res = resample_nearest(x_shifted, y_sync, np.asarray(ref_time, dtype=float))
        xOffset = np.asarray(ref_time, dtype=float)
        yOffset = y_res
        if write:
            # Update the sync dataset's label with resampled values (demo)
            # Assumes lengths are compatible in demo
            df_sync[syncLabName] = yOffset
        return xOffset, yOffset
    else:
        raise ValueError("Invalid pad_method")


class syncMenu_App(tk.Tk):
    def __init__(self, vehData=None, udp=None):
        super().__init__()
        self.title("syncMenu")
        self.geometry("435x625")
        self.vehData = vehData
        self.udp = udp

        # State
        self.pick_mode = None  # None, 'sync', 'ref'
        self.offset_view = False
        self.plot_data_orig = None  # dict with x_ref, y_ref, x_sync, y_sync
        self.dataset_names = [d.get('name', f"Set{i}") for i, d in enumerate(vehData)]

        # UI Variables
        self.ref_dataset_var = tk.StringVar()
        self.ref_label_var = tk.StringVar()
        self.sync_dataset_var = tk.StringVar()
        self.sync_label_var = tk.StringVar()

        self.sync_from_var = tk.StringVar()
        self.ref_to_var = tk.StringVar()
        self.manual_offset_var = tk.StringVar()
        self.auto_offset_var = tk.StringVar()
        self.final_offset_var = tk.StringVar()

        self.apply_to_var = tk.StringVar(value="Dataset")
        self.pad_with_var = tk.StringVar(value="NaN")

        # Build UI
        self._build_ui()
        self._populate_datasets()

    def _build_ui(self):
        # Frames
        self.ref_frame = ttk.LabelFrame(self, text="Reference Data")
        self.ref_frame.pack(fill='x', padx=5, pady=5)

        self.sync_frame = ttk.LabelFrame(self, text="Sync Data")
        self.sync_frame.pack(fill='x', padx=5, pady=5)

        self.display_frame = ttk.LabelFrame(self, text="Display")
        self.display_frame.pack(fill='x', padx=5, pady=5)

        self.manual_frame = ttk.LabelFrame(self, text="Manual Sync")
        self.manual_frame.pack(fill='x', padx=5, pady=5)

        self.xcorr_frame = ttk.LabelFrame(self, text="Cross Correlation")
        self.xcorr_frame.pack(fill='x', padx=5, pady=5)

        self.apply_frame = ttk.LabelFrame(self, text="Apply Offset")
        self.apply_frame.pack(fill='x', padx=5, pady=5)

        # Reference Controls
        ttk.Label(self.ref_frame, text="Reference Dataset:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.ref_dataset_cb = ttk.Combobox(self.ref_frame, textvariable=self.ref_dataset_var, state='readonly')
        self.ref_dataset_cb.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.ref_frame.columnconfigure(1, weight=1)
        self.ref_dataset_cb.bind("<<ComboboxSelected>>", self.on_ref_dataset_change)

        ttk.Label(self.ref_frame, text="Reference Label:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.ref_label_cb = ttk.Combobox(self.ref_frame, textvariable=self.ref_label_var, state='readonly')
        self.ref_label_cb.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        # Sync Controls
        ttk.Label(self.sync_frame, text="Sync Dataset:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.sync_dataset_cb = ttk.Combobox(self.sync_frame, textvariable=self.sync_dataset_var, state='readonly')
        self.sync_dataset_cb.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        self.sync_frame.columnconfigure(1, weight=1)
        self.sync_dataset_cb.bind("<<ComboboxSelected>>", self.on_sync_dataset_change)

        ttk.Label(self.sync_frame, text="Sync Label:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.sync_label_cb = ttk.Combobox(self.sync_frame, textvariable=self.sync_label_var, state='readonly')
        self.sync_label_cb.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        # Display Controls
        self.display_btn = ttk.Button(self.display_frame, text="Display", command=self.on_display)
        self.display_btn.pack(side='left', padx=5, pady=5)

        # Manual Sync Controls
        btn_frame = tk.Frame(self.manual_frame)
        btn_frame.pack(fill='x', padx=5, pady=2)
        self.pick_sync_btn = ttk.Button(btn_frame, text="From:  Sync Data", command=self.on_pick_sync)
        self.pick_sync_btn.pack(side='left', padx=5)
        self.pick_ref_btn = ttk.Button(btn_frame, text="To:  Ref. Data", command=self.on_pick_ref)
        self.pick_ref_btn.pack(side='left', padx=5)

        entries_frame = tk.Frame(self.manual_frame)
        entries_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(entries_frame, text="Sync From (s)").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.sync_from_entry = ttk.Entry(entries_frame, textvariable=self.sync_from_var)
        self.sync_from_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        entries_frame.columnconfigure(1, weight=1)

        ttk.Label(entries_frame, text="Ref To (s)").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.ref_to_entry = ttk.Entry(entries_frame, textvariable=self.ref_to_var)
        self.ref_to_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(entries_frame, text="(Ref - Sync)").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        calc_frame = tk.Frame(entries_frame)
        calc_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        calc_frame.columnconfigure(0, weight=1)
        self.calc_offset_btn = ttk.Button(calc_frame, text="Calculate Offset", command=self.on_calc_offset)
        self.calc_offset_btn.pack(side='left')
        ttk.Label(entries_frame, text="Manual Offset (s)").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.manual_offset_entry = ttk.Entry(entries_frame, textvariable=self.manual_offset_var)
        self.manual_offset_entry.grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        # Cross Correlation Controls
        xcorr_btn_frame = tk.Frame(self.xcorr_frame)
        xcorr_btn_frame.pack(fill='x', padx=5, pady=2)
        self.xcorr_btn = ttk.Button(xcorr_btn_frame, text="Calculate xCorr Offset", command=self.on_xcorr)
        self.xcorr_btn.pack(side='left', padx=5)

        xcorr_entry_frame = tk.Frame(self.xcorr_frame)
        xcorr_entry_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(xcorr_entry_frame, text="Auto Offset (s)").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.auto_offset_entry = ttk.Entry(xcorr_entry_frame, textvariable=self.auto_offset_var)
        self.auto_offset_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        xcorr_entry_frame.columnconfigure(1, weight=1)

        # Apply Offset Controls
        apply_grid = tk.Frame(self.apply_frame)
        apply_grid.pack(fill='x', padx=5, pady=2)
        ttk.Label(apply_grid, text="Offset (s)").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.final_offset_entry = ttk.Entry(apply_grid, textvariable=self.final_offset_var)
        self.final_offset_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        apply_grid.columnconfigure(1, weight=1)

        ttk.Label(apply_grid, text="Apply Offset To:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.apply_to_cb = ttk.Combobox(apply_grid, textvariable=self.apply_to_var, state='readonly',
                                        values=["Dataset", "Label"])
        self.apply_to_cb.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(apply_grid, text="Pad Missing Data With:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.pad_with_cb = ttk.Combobox(apply_grid, textvariable=self.pad_with_var, state='readonly',
                                        values=["NaN", "Nearest"])
        self.pad_with_cb.grid(row=2, column=1, sticky='ew', padx=5, pady=2)

        apply_btns = tk.Frame(self.apply_frame)
        apply_btns.pack(fill='x', padx=5, pady=5)
        self.display_offset_btn = ttk.Button(apply_btns, text="Display Offset", command=self.on_display_offset)
        self.display_offset_btn.pack(side='left', padx=5)
        self.apply_offset_btn = ttk.Button(apply_btns, text="Apply Offset", command=self.on_apply_offset)
        self.apply_offset_btn.pack(side='left', padx=5)

        # Plot Area
        self.plot_frame = ttk.Frame(self)
        self.plot_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def _populate_datasets(self):
        # Populate dataset comboboxes
        names = self.dataset_names
        self.ref_dataset_cb['values'] = names
        self.sync_dataset_cb['values'] = names

        # Defaults: ref=0, sync=1 if exists else 0
        if len(names) > 0:
            self.ref_dataset_cb.current(0)
            self.ref_dataset_var.set(names[0])
            self.update_label_combobox(self.ref_label_cb, 0)
        if len(names) > 1:
            self.sync_dataset_cb.current(1)
            self.sync_dataset_var.set(names[1])
            self.update_label_combobox(self.sync_label_cb, 1)
        elif len(names) > 0:
            self.sync_dataset_cb.current(0)
            self.sync_dataset_var.set(names[0])
            self.update_label_combobox(self.sync_label_cb, 0)

    def on_ref_dataset_change(self, event=None):
        idx = self.get_dataset_index(self.ref_dataset_var.get())
        if idx is not None:
            self.update_label_combobox(self.ref_label_cb, idx)
        # Clear picks as selection changed
        self.sync_from_var.set("")
        self.ref_to_var.set("")

    def on_sync_dataset_change(self, event=None):
        idx = self.get_dataset_index(self.sync_dataset_var.get())
        if idx is not None:
            self.update_label_combobox(self.sync_label_cb, idx)
        self.sync_from_var.set("")
        self.ref_to_var.set("")

    def update_label_combobox(self, combobox, dataset_idx):
        try:
            df = self.vehData[dataset_idx]['data']
            labels = list(df.columns)
            combobox['values'] = labels
            if labels:
                combobox.current(0)
        except Exception:
            combobox['values'] = []
            combobox.set('')

    def get_dataset_index(self, name):
        try:
            return self.dataset_names.index(name)
        except ValueError:
            return None

    def get_time_series(self, veh_idx):
        try:
            method = self.vehData[veh_idx].get('method', 'none')
            time_col = self.udp[veh_idx][method]['time']
            df = self.vehData[veh_idx]['data']
            if time_col not in df.columns:
                raise KeyError(f"Time column '{time_col}' not found in dataset {self.vehData[veh_idx]['name']}")
            x = np.asarray(df[time_col].values, dtype=float)
            return x, time_col
        except Exception as e:
            raise e

    def get_label_series(self, veh_idx, label):
        try:
            df = self.vehData[veh_idx]['data']
            if label not in df.columns:
                raise KeyError(f"Label '{label}' not found in dataset {self.vehData[veh_idx]['name']}")
            y = np.asarray(df[label].values, dtype=float)
            return y
        except Exception as e:
            raise e

    def on_display(self):
        # Read selections
        try:
            ref_idx, sync_idx, ref_label, sync_label = self.get_selections()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        try:
            x_ref, _ = self.get_time_series(ref_idx)
            y_ref = self.get_label_series(ref_idx, ref_label)
            x_sync, _ = self.get_time_series(sync_idx)
            y_sync = self.get_label_series(sync_idx, sync_label)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Plot single axes with dual y-axes
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        ax2 = ax.twinx()

        l1, = ax.plot(x_ref, y_ref, color=REF_COLOR, label=f"Ref: {ref_label}")
        l2, = ax2.plot(x_sync, y_sync, color=SYNC_COLOR, label=f"Sync: {sync_label}")

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Reference")
        ax2.set_ylabel("Sync")

        # Combined legend
        lines = [l1, l2]
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='best')

        self.canvas.draw()
        self.offset_view = False
        # Store original data for picking
        self.plot_data_orig = {
            'x_ref': x_ref, 'y_ref': y_ref,
            'x_sync': x_sync, 'y_sync': y_sync
        }

    def on_pick_sync(self):
        if self.plot_data_orig is None:
            messagebox.showerror("Error", "Please Display data before picking points.")
            return
        self.pick_mode = 'sync'
        messagebox.showinfo("Pick", "Click on the plot to pick from Sync Data (nearest time).")

    def on_pick_ref(self):
        if self.plot_data_orig is None:
            messagebox.showerror("Error", "Please Display data before picking points.")
            return
        self.pick_mode = 'ref'
        messagebox.showinfo("Pick", "Click on the plot to pick from Reference Data (nearest time).")

    def on_click(self, event):
        if self.pick_mode is None:
            return
        if event is None or event.xdata is None:
            return
        x_click = float(event.xdata)
        try:
            if self.pick_mode == 'sync':
                x = self.plot_data_orig['x_sync']
                y = self.plot_data_orig['y_sync']
                idx, (xp, yp) = nearest_point(x, y, x_click)
                if idx is not None:
                    self.sync_from_var.set(f"{xp:.6f}")
            elif self.pick_mode == 'ref':
                x = self.plot_data_orig['x_ref']
                y = self.plot_data_orig['y_ref']
                idx, (xp, yp) = nearest_point(x, y, x_click)
                if idx is not None:
                    self.ref_to_var.set(f"{xp:.6f}")
        except Exception:
            pass
        finally:
            self.pick_mode = None

    def on_calc_offset(self):
        try:
            ref_to = float(self.ref_to_var.get())
            sync_from = float(self.sync_from_var.get())
        except Exception:
            messagebox.showerror("Error", "Please enter valid 'Sync From' and 'Ref To' times.")
            return
        manual_offset = ref_to - sync_from
        self.manual_offset_var.set(f"{manual_offset:.6f}")
        self.final_offset_var.set(f"{manual_offset:.6f}")

    def on_xcorr(self):
        # Compute cross-correlation-based offset
        try:
            ref_idx, sync_idx, ref_label, sync_label = self.get_selections()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        try:
            x_sync, _ = self.get_time_series(sync_idx)
            y_sync = self.get_label_series(sync_idx, sync_label)
            x_ref, _ = self.get_time_series(ref_idx)
            y_ref = self.get_label_series(ref_idx, ref_label)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Resample y_ref onto x_sync for consistent sample step
        y_ref_res = resample_nearest(x_ref, y_ref, x_sync)
        # Compute lag in samples
        try:
            lag_samples = x_corr_shift(y_ref_res, y_sync)
        except Exception as e:
            messagebox.showerror("Error", f"Cross-correlation failed: {e}")
            return
        time_step = float(self.vehData[sync_idx].get('timeStep', 1.0))
        offset_seconds = lag_samples * time_step
        self.auto_offset_var.set(f"{offset_seconds:.6f}")
        self.final_offset_var.set(f"{offset_seconds:.6f}")

    def on_display_offset(self):
        # Display original and proposed offset plots
        try:
            ref_idx, sync_idx, ref_label, sync_label = self.get_selections()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        # Get data
        try:
            x_ref, _ = self.get_time_series(ref_idx)
            y_ref = self.get_label_series(ref_idx, ref_label)
            x_sync, _ = self.get_time_series(sync_idx)
            y_sync = self.get_label_series(sync_idx, sync_label)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        # Parse offset and options
        try:
            offset_val = float(self.final_offset_var.get())
        except Exception:
            messagebox.showerror("Error", "Please enter a valid Offset (s).")
            return
        pad_method = 0 if self.pad_with_var.get() == "NaN" else 1

        # Compute shifted sync series
        try:
            if pad_method == 0:
                xOff, yOff = label_offset(self.vehData, self.udp, offset_val, sync_idx, sync_label,
                                          apply_label=0, pad_method=pad_method, write=False, ref_time=None)
            else:
                xOff, yOff = label_offset(self.vehData, self.udp, offset_val, sync_idx, sync_label,
                                          apply_label=0, pad_method=pad_method, write=False, ref_time=x_ref)
        except Exception as e:
            messagebox.showerror("Error", f"Offset computation failed: {e}")
            return

        # Plot
        self.fig.clf()
        # Top subplot: original
        ax_top = self.fig.add_subplot(211)
        ax_top2 = ax_top.twinx()
        l1, = ax_top.plot(x_ref, y_ref, color=REF_COLOR, label=f"Ref: {ref_label}")
        l2, = ax_top2.plot(x_sync, y_sync, color=SYNC_COLOR, label=f"Sync: {sync_label}")
        ax_top.set_xlabel("Time (s)")
        ax_top.set_ylabel("Reference")
        ax_top2.set_ylabel("Sync")
        ax_top.legend([l1, l2], [l1.get_label(), l2.get_label()], loc='best')

        # Bottom subplot: with offset
        ax_bot = self.fig.add_subplot(212, sharex=ax_top)
        ax_bot2 = ax_bot.twinx()
        l3, = ax_bot.plot(x_ref, y_ref, color=REF_COLOR, label=f"Ref: {ref_label}")
        l4, = ax_bot2.plot(xOff, yOff, color=SYNC_COLOR, label=f"Sync (offset): {sync_label}")
        ax_bot.set_xlabel("Time (s)")
        ax_bot.set_ylabel("Reference")
        ax_bot2.set_ylabel("Sync (offset)")
        ax_bot.legend([l3, l4], [l3.get_label(), l4.get_label()], loc='best')

        self.canvas.draw()
        self.offset_view = True
        self.plot_data_orig = {
            'x_ref': x_ref, 'y_ref': y_ref,
            'x_sync': x_sync, 'y_sync': y_sync
        }

    def on_apply_offset(self):
        # Apply the offset (demo write)
        try:
            ref_idx, sync_idx, ref_label, sync_label = self.get_selections()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        # Parse offset
        try:
            offset_val = float(self.final_offset_var.get())
        except Exception:
            messagebox.showerror("Error", "Please enter a valid Offset (s).")
            return

        pad_method = 0 if self.pad_with_var.get() == "NaN" else 1
        apply_to = 0 if self.apply_to_var.get() == "Dataset" else 1

        # Reference time for resample if needed
        try:
            x_ref, _ = self.get_time_series(ref_idx)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            if pad_method == 0:
                xOff, yOff = label_offset(self.vehData, self.udp, offset_val, sync_idx, sync_label,
                                          apply_label=apply_to, pad_method=pad_method, write=True, ref_time=None)
            else:
                xOff, yOff = label_offset(self.vehData, self.udp, offset_val, sync_idx, sync_label,
                                          apply_label=apply_to, pad_method=pad_method, write=True, ref_time=x_ref)
        except Exception as e:
            messagebox.showerror("Error", f"Apply offset failed: {e}")
            return

        messagebox.showinfo("Apply Offset",
                            f"Applied offset {offset_val:.6f} s to "
                            f"{'dataset' if apply_to == 0 else 'label'} '{self.vehData[sync_idx]['name']}/{sync_label}' "
                            f"using pad method '{self.pad_with_var.get()}'. (Demo)")

    def get_selections(self):
        # Resolve selections and validate
        ref_name = self.ref_dataset_var.get()
        sync_name = self.sync_dataset_var.get()
        ref_label = self.ref_label_var.get()
        sync_label = self.sync_label_var.get()
        if not ref_name or not sync_name or not ref_label or not sync_label:
            raise ValueError("Please select datasets and labels for both Reference and Sync.")
        ref_idx = self.get_dataset_index(ref_name)
        sync_idx = self.get_dataset_index(sync_name)
        if ref_idx is None or sync_idx is None:
            raise ValueError("Selected dataset not found.")
        return ref_idx, sync_idx, ref_label, sync_label


# def demo_data():
#     # Create two datasets with shared time and labels A and B
#     t = np.arange(0, 100, 0.5)
#     A = np.sin(0.2 * t) + 0.05 * np.random.randn(len(t))
#     # B is shifted version of A by ~3 seconds (6 samples if timeStep=0.5)
#     shift_seconds = 3.0
#     shift_samples = int(shift_seconds / 0.5)
#     # Create B by shifting A backwards (so needs +3s to align forward)
#     A_shifted = np.roll(A, -shift_samples)
#     A_shifted[-shift_samples:] = np.nan  # introduce NaNs at the end
#     B = A_shifted + 0.03 * np.random.randn(len(t))

#     df0 = pd.DataFrame({'time': t, 'A': A, 'B': B})
#     # SyncSet has signal B as primary; keep same time base for demo
#     df1 = pd.DataFrame({'time': t, 'A': A, 'B': B})

    # vehData = [
    #     {'name': 'RefSet', 'method': 'none', 'timeStep': 0.5, 'data': df0},
    #     {'name': 'SyncSet', 'method': 'none', 'timeStep': 0.5, 'data': df1}
    # ]

    # udp = [
    #     {'none': {'time': 'time'}, 'sd': {'time': 'time'}, 'dyno': {'time': 'time'},
    #      'pems': {'time': 'time'}, 'can': {'time': 'time'}},
    #     {'none': {'time': 'time'}, 'sd': {'time': 'time'}, 'dyno': {'time': 'time'},
    #      'pems': {'time': 'time'}, 'can': {'time': 'time'}}
    # ]

    # app = syncMenu_App(vehData, udp)
#     app.mainloop()


# if __name__ == "__main__":
#     demo_data()