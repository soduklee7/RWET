"""
Docstring for PEMSAnalysisGUI11
Author: S. Lee

Update a Windows 11 color style 600x750 size PEMS Data Analysis PEMSAnalysisGUI(object) GUI using tkinter, pillow icons, and default font size 12, and the Python code here.
1)	Create a text box with a "PEMS File" label and the "Select" button to select a CSV file. Read the selected file using self.df = pd.read_csv with encoding='utf-8', low_memory=False, skiprows=0, header=0 and skipping first 0 rows in the “read_file” fuction when clicking the " Select " button. 
2)	Replace the "Select" button with the self.icon_folder for a Windows 11 color "Folder" large icon. Display the "Select a file" when placing a mouse pointer on the "Select" icon. Adjust the textbox length to tightly fit with the "Select" button horizontally.
3)	Remove columns with "Not Available" or "Unnamed" in the self.df.columns.
4)	Update the “read_file” fuction by create eTIME by converting hh:mm:s.xxx format data in self.df['sTIME] in seconds using the ensure_eTIME() function after reading the file and then add the following code part.
5)	Use the following code before assigning columns_row, vars_row and units_row in step 6).
    if 'eTIME' not in self.df.columns:
        self.df.insert(1, 'eTIME', None)
        self.df.loc[0, 'eTIME'] = 'eTIME'
        self.df.loc[1, 'eTIME'] = 's'
6)	Assign columns_row = self.df.columns, vars_row = self.df.loc[0, :] and units_row = self.df.loc[1, :]. Update self.df = self.df.loc[2:, :].
7)	Create df_summary data frame starting from the row that contains the "Summary Information:" in the first column of self.df data frame using the summary_row_idx = pd.Index(self.df[first_col]).get_loc("Summary Information:") in the “read_file” function.
Save self.df_summary using self.df_summary.to_csv(). 
Create self.df = self.df.loc[2:summary_row_idx-1, :].copy()
8)	Create pre_select_columns = ['eTIME', 'Gas Path', 'Catalyst Temperature', 'Limit Adjusted iSCB_RH', 'Ambient Pressure', 'Limit Adjusted iSCB_LAT', 'Load Percent',  'Limit Adjusted iCOOL_TEMP', 'Engine RPM', 'Vehicle Speed', 'Mass Air Flow Rate', 'Catalyst Temp. 1-1', 'F/A Equiv. Ratio', 'Engine Fuel Rate',  'Eng. Exh. Flow Rate', 'GPS Latitude', 'GPS Longitude', 'Limit Adjusted iGPS_ALT', 'Limit Adjusted iGPS_GROUND_SPEED', 'Fuel Rate', 'Instantaneous Fuel Flow',  'Derived Engine Torque.1', 'Derived Engine Power.1', 'Instantaneous Mass CO2', 'Instantaneous Mass CO', 'Instantaneous Mass NO', 'Instantaneous Mass NO2',  'Instantaneous Mass NOx', 'Corrected Instantaneous Mass NOx', 'Instantaneous Mass HC', 'Instantaneous Mass CH4', 'Instantaneous Mass NMHC', 'Instantaneous Mass O2', 'Air/Fuel Ratio at stoichiometry', 'Air/Fuel Ratio of Sample', 'Lambda', 'Ambient Temperature', 'AMB Ambient Temperature', 'Brake Specific Fuel Consumption', 'Mass Air Flow Rate.1'] in the “read_file” function.
9)	Create  pre_select_vars = [ 'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD',  'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'icMASS_FLOWx', 'EXH_RATE',  'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP' ] in the “read_file” function
10)	Create an "Input_file_dir" checkbox button labeled "Check to process all CSV file in a folder". Create the "Input_file_dir_checked" variable to pass the status.
11)	After clicking the "btn_select" icon, select the pre_select_columns in the columns_listbox.  When you click the “btn_select” button, the items in pre_select_columns are selected in the columns_listbox.
12)	Create a 10-row scrollable "columns_listbox" list box to display the data frame column header for data labeling. Label the "columns_listbox" list box with the "Data Fields". Enable multiple selection in the list box by clicking mouse pointers. 
13)	Empty the "columns_listbox" list box before clicking the "Read" icon.
14)	Create the "pre_selected_columns" checkbox button labeled the “Display Selected Data Fields only”. Place the “pre_selected_columns” checkbox directly below the “columns_listbox” by introducing a listbox container frame. 
15)	Create the “selected_columns_list” list to store additionally selected items in the “columns_listbox” list box. Show only the selected_columns_list in the “columns_listbox” list box when the “pre_selected_columns” checkbox is checked. Update the refresh_columns_listbox method so that when “Display Selected Data Fields only” is not checked, the listbox shows self.columns_row and then select any items that match selected_columns_list. 
16)	Create a 5-row scrollable "align_listbox" list box to display the 'Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', and 'Total Current' alignment data.
17)	Enable multiple selection in the list box by clicking mouse pointers. 
18)	Label the "align_listbox" list box with the "Time Alignment".
19)	Set the align_listbox width equal to the columns_listbox width.
20)	Create an "Alignment" checkbox button and "Report" checkbox button horizontally to call back functions. Check the "Report" checkbox.
21)	Create a text box with an "OBD File" label. Display the "Press a OBD button to select an OBD/HEMDATA file" when placing a mouse pointer on the "OBD File" text box.
22)	Create an "OBD" button. Replace the "OBD" button with the self.icon_truck for a Windows 11 color Truck icon to select a CSV file. Display the "Select OBD file" when placing a mouse pointer on the "OBD" icon. Only Enable the "OBD File" text box and "OBD" button when the "Alignment" checkbox is True.
23)	Call the select_obd_file function to read the OBD file when clicking the "OBD" button. Add the following code in the select_obd_file function to convert hh:mm:s.xxx format data in self.df['sTIME] in seconds using the ensure_eTIME() function after reading the file and then add the following code part.
before assigning columns_row, vars_row and units_row in step 23).
    if 'eTIME' not in self.df.columns:
        tmp.insert(1, 'eTIME', None)
        tmp.loc[0, 'eTIME'] = 'eTIME'
        tmp.loc[1, 'eTIME'] = 's'
24)	Assign columns_row = tmp.columns, vars_row = tmp.loc[0, :] and units_row = tmp.loc[1, :]. Update tmp = tmp.loc[2:, :].
25)	Create tmp.df_summary data frame starting from the row that contains the "Summary Information:" in the first column of tmp data frame using the summary_row_idx = pd.Index(tmp[first_col]).get_loc("Summary Information:") in the “select_obd_file” function.
I.	Save tmp.df_summary using tmp.df_summary.to_csv().
II.	Create tmp = tmp.loc[2:summary_row_idx-1, :].copy()
26)	Adjust the horizontal x coordinate of the "OBD" button at the btn_select.winfo_x().
27)	Adjust the “OBD File” text box width little less than the horizontal x coordinate of the "OBD" button.
28)	Create the “frame_check_align” frame using tk.Frame and pack(fill="x", padx=20, pady=10). Create the "Check Alignment" button labeled the “btn_check_align“. Create a “ent_align_input” input textbox next to the "Check Alignment" button. Display the “Check/Plot Alignment” and the "Type Alignment Values to OBD" when placing a mouse pointer on the "Check Alignment" button and the “btn_check_align“ input textbox respectively. 
29)	Enable the “ent_align_input “ input textbox if the “btn_check_align” alignment checkbox is True and “OBD File” text box is not empty.
30)	Create a "Plot" button next to the  “ent_align_input “ input textbox to call back the "plot_alignment” function. Enable only the "Plot" button when the “ent_align_input “ alignment input textbox is not empty.
31)	Replace the "Plot" button labeled “btn_plot” using  the self.icon_figure in the following code.
32)	Adjust the horizontal x coordinate of the " btn_plot " button at the btn_select.winfo_x().
33)	Display the "Plot Alignments" when placing a mouse pointer on the " btn_plot " button.
34)	Create the following self.align_map code.
        self.align_map = {
            "Vehicle Speed": "iVEH_SPEED",
            "Engine RPM": "iENG_SPEED",
            "Exhaust Mass Flow Rate": "icMASS_FLOW",
            "Total Current": "TotalCurrent"
        }
35)	Call back the plot_check_alignment when clicking the “btn_check_align“  button.
36)	Close all opened figures using “if plt.get_fignums(): plt.close('all')” before calling the ImageDistanceMeasurer object in the “plot_check_alignment” function.
37)	Create the “check_alignment_view” function to call back the “plot_alignment” function when clicking the self.btn_plot button. 
self.plot_alignment(
            self.ent_pems.get(),
            self.ent_obd.get(),
            align_col
        )
38)	Set the "Check Alignment" button with a light magenta-color background to call back "check_alignment()" function with the selected items in the "align_listbox".
39)	Add the self.ent_pems.get(), self.ent_obd.get(), self.align_values_var.get() arguments the plot_alignment function. Plot df[self.align_values_var.get()] in the self.ent_pems.get() and self.ent_obd.get().
40)	Create a font size 20, black bold font, "RUN" big button with a light blue-color background to call back the "run_analysis()" function.
41)	Assign Alignment_checked and Report_checked variables to pass the "Alignment" and "Report" Checkbox check status.
42)	Pre-select the 'Vehicle Speed' in the "align_listbox" listbox.
43)	Fix the _tkinter.TclError: expected integer but got "UI"
44)	Enable to select multiple items in both the columns_listbox. Enable to select a single item in the align_listbox.
45)	Print the obd_ent, pems_ent, "Alignment", "Report", "Input_file_dir" checkbox status, "Check Alignment" button, align_values_ent textbox values, and the index of 'Vehicle Speed' in df.columns when clicking the "RUN" button. Keep current run_analysis() function in the code.
46)	 Fix automatically deselecting an item in a listbox while selecting an item in another listbox

"""
import os
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

# matplotlib for plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------------

def get_time_axis(df_local):
    if 'eTIME' in df_local.columns:
        return pd.to_numeric(df_local['eTIME'], errors='coerce')
    else:
        return pd.Series(range(len(df_local)), dtype=float)
            
def ensure_eTIME(df_local):
    """Ensure df_local has a numeric 'eTIME' column in seconds, derived from 'sTIME' (hh:mm:s.xxx) if needed."""
    if df_local is None or df_local.empty:
        return df_local

    def convert_to_seconds(val):
        if pd.isna(val):
            return math.nan
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip().replace(',', '.')
        # Try numeric first
        try:
            return float(s)
        except Exception:
            pass
        # Try to parse colon-separated time
        parts = s.split(':')
        try:
            if len(parts) == 3:
                h = int(parts[0])
                m = int(parts[1])
                sec = float(parts[2])
            elif len(parts) == 2:
                h = 0
                m = int(parts[0])
                sec = float(parts[1])
            elif len(parts) == 1:
                h = 0
                m = 0
                sec = float(parts[0])
            else:
                return math.nan
            return h * 3600 + m * 60 + sec
        except Exception:
            return math.nan

    # If eTIME exists but is non-numeric, rebuild from sTIME
    if 'eTIME' in df_local.columns:
        df_local['eTIME'] = pd.to_numeric(df_local['eTIME'], errors='coerce')
        if df_local['eTIME'].isna().all() and 'sTIME' in df_local.columns:
            df_local['eTIME'] = df_local['sTIME'].apply(convert_to_seconds)
            # Normalize to start at zero if possible
            try:
                df_local['eTIME'] = df_local['eTIME'] - float(df_local.loc[2, 'eTIME'])
            except Exception:
                pass
    elif 'sTIME' in df_local.columns:
        df_local.insert(1, 'eTIME', None)
        df_local['eTIME'] = df_local['sTIME'].apply(convert_to_seconds)
        # Normalize to start at zero if possible
        try:
            df_local['eTIME'] = df_local['eTIME'] - float(df_local.loc[2, 'eTIME'])
        except Exception:
            pass
    return df_local

import matplotlib.pyplot as plt

class PlotManager:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.base_scale = 1.1
        
        # Panning state
        self.pressed = False
        self.xpress = None
        self.ypress = None

        # Connect Zoom and Key Events
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # Connect Panning Events
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

    # --- PANNING LOGIC ---
    def on_press(self, event):
        if event.inaxes != self.ax: return
        self.pressed = True
        self.xpress, self.ypress = event.xdata, event.ydata

    def on_motion(self, event):
        if not self.pressed or event.inaxes != self.ax: return
        
        # Calculate how far we've moved
        dx = event.xdata - self.xpress
        dy = event.ydata - self.ypress
        
        # Shift the current limits by the delta
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        self.ax.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
        self.ax.set_ylim(cur_ylim[0] - dy, cur_ylim[1] - dy)
        self.fig.canvas.draw_idle()

    def on_release(self, event):
        self.pressed = False

    # --- ZOOM LOGIC (Scroll & Keys) ---
    def on_scroll(self, event):
        if event.inaxes != self.ax: return
        scale_factor = 1 / self.base_scale if event.button == 'up' else self.base_scale
        self._apply_zoom(scale_factor, event.xdata, event.ydata)

    def on_key(self, event):
        if 'ctrl+' in event.key:
            if '+' in event.key or '=' in event.key:
                self._apply_zoom(1 / self.base_scale)
            elif '-' in event.key:
                self._apply_zoom(self.base_scale)

    def _apply_zoom(self, scale_factor, x_center=None, y_center=None):
        cur_xlim, cur_ylim = self.ax.get_xlim(), self.ax.get_ylim()
        if x_center is None:
            x_center, y_center = sum(cur_xlim)/2, sum(cur_ylim)/2

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rel_x, rel_y = (cur_xlim[1]-x_center)/(cur_xlim[1]-cur_xlim[0]), (cur_ylim[1]-y_center)/(cur_ylim[1]-cur_ylim[0])

        self.ax.set_xlim([x_center - new_width * (1-rel_x), x_center + new_width * rel_x])
        self.ax.set_ylim([y_center - new_height * (1-rel_y), y_center + new_height * rel_y])
        self.fig.canvas.draw_idle()

# Run the Plot
# fig, ax = plt.subplots()
# ax.plot(range(50), [x**0.5 for x in range(50)], label="Square Root")
# pm = PlotManager(fig, ax)
# plt.show()

class ZoomManager:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.base_scale = 1.1  # Zoom intensity
        
        # Connect the events
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_scroll(self, event):
        # Ensure the mouse is over the axes
        if event.inaxes != self.ax:
            return
        
        # Determine zoom direction
        if event.button == 'up':
            scale_factor = 1 / self.base_scale
        elif event.button == 'down':
            scale_factor = self.base_scale
        else:
            scale_factor = 1

        self._apply_zoom(scale_factor, event.xdata, event.ydata)

    def on_key(self, event):
        # Standard Matplotlib key strings for + and -
        # Note: 'ctrl+=' is often the result of Ctrl and +
        if 'ctrl+' in event.key:
            if '+' in event.key or '=' in event.key:
                self._apply_zoom(1 / self.base_scale)
            elif '-' in event.key:
                self._apply_zoom(self.base_scale)

    def _apply_zoom(self, scale_factor, x_center=None, y_center=None):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        # If no specific center (like keyboard zoom), use the middle of the view
        if x_center is None:
            x_center = (cur_xlim[0] + cur_xlim[1]) / 2
            y_center = (cur_ylim[0] + cur_ylim[1]) / 2

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        # Calculate new limits based on the center point
        rel_x = (cur_xlim[1] - x_center) / (cur_xlim[1] - cur_xlim[0])
        rel_y = (cur_ylim[1] - y_center) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([x_center - new_width * (1 - rel_x), x_center + new_width * rel_x])
        self.ax.set_ylim([y_center - new_height * (1 - rel_y), y_center + new_height * rel_y])
        self.fig.canvas.draw_idle()

# # Usage
# fig, ax = plt.subplots()
# ax.plot(range(10), [x**2 for x in range(10)])
# zm = ZoomManager(fig, ax)
# plt.show()

class ImageDistanceMeasurer:
    """
    Interactive panel to click twice and measure horizontal & vertical pixel distances
    against plotted series. Used when align_values_var is empty or for visual checks.
    """
    def __init__(self, pems_df, data_to_plot, align_col):
        self.fig, self.ax = plt.subplots(figsize=(19.2, 10.8))

        idx = 0
        for x_vals, y_vals, label in (data_to_plot):
            if idx == 0:
                self.ax.plot(x_vals, y_vals, label=label, linewidth=1)
            else:
                self.ax.plot(x_vals, y_vals, '--', label=label, linewidth=1)
            idx += 1

        self.ax.set_xlabel("Time (s)" if 'eTIME' in pems_df.columns else "Index")
        self.ax.set_ylabel(align_col)
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.ax.legend(loc="upper left")
        self.ax.set_title("Click twice to measure pixels (H & V)")
        self.points = []
        self.markers = []
        self.elements = []

        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        zm = ZoomManager(self.fig, self.ax)
        # pm = PlotManager(self.fig, self.ax)
        plt.show()

    def onclick(self, event):
        if event.inaxes != self.ax:
            return
            # Stop listening for this specific event
            self.fig.canvas.mpl_disconnect(self.cid)
            self.cid = None # Good practice to clear the reference
        if len(self.points) == 2:
            self.clear_previous()

        self.points.append((event.xdata, event.ydata))
        marker, = self.ax.plot(event.xdata, event.ydata, 'ro', markersize=6)
        self.markers.append(marker)

        if len(self.points) == 2:
            (x1, y1), (x2, y2) = self.points
            dx, dy = (x2 - x1), (y2 - y1)

            h_line, = self.ax.plot([x1, x2], [y1, y1], 'b--', alpha=0.8)
            v_line, = self.ax.plot([x2, x2], [y1, y2], 'g--', alpha=0.8)
            h_text = self.ax.text((x1 + x2) / 2, y1, f' {dx:.1f}px', color='blue', va='bottom')
            v_text = self.ax.text(x2, (y1 + y2) / 2, f' {dy:.1f}px', color='green', ha='left')
            self.elements.extend([h_line, v_line, h_text, v_text])
            print(f"Pixels -> H: {dx:.2f} | V: {dy:.2f}")

        self.fig.canvas.draw()

    def clear_previous(self):
        self.points = []
        for m in self.markers + self.elements:
            try:
                m.remove()
            except Exception:
                pass
        self.markers, self.elements = [], []

# -------------------------------------------------------------------------
# Main GUI Class
# -------------------------------------------------------------------------
class PEMSAnalysisGUI(object):
    """
    PEMSAnalysisGUI11
    Author: S. Lee

    Windows 11 color style PEMS Data Analysis GUI, 600x750, tkinter + Pillow icons,
    default font size 12. Implements requirements 1-46.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("PEMS Data Analysis")
        self.root.geometry("600x750")
        self.root.configure(bg="#f3f3f3")  # Windows 11 Light Grey Background

        # Fonts (Fix for TclError: use proper tuples; do not pass strings into width/height)
        self.font_default = ("Segoe UI", 12)
        self.font_header = ("Segoe UI", 12, "bold")
        self.font_run = ("Segoe UI", 20, "bold")

        # Variables
        self.df = None
        self.df_summary = None
        self.columns_row = None
        self.vars_row = None
        self.units_row = None

        # OBD/HEM
        self.obd_df = None
        self.obd_df_summary = None

        self.data_to_align = None

        self.pems_file_path = tk.StringVar()
        self.obd_file_path = tk.StringVar()
        self.align_values_var = tk.StringVar()

        # Checkbox Variables
        self.input_file_dir_checked = tk.BooleanVar()
        self.alignment_checked = tk.BooleanVar()
        self.report_checked = tk.BooleanVar(value=True)  # Default True
        self.pre_selected_columns_var = tk.BooleanVar()  # Display Selected Data Fields only

        # Storage for user selections (14)
        self.selected_columns_list = []

        # Pre-select lists (7, 8)
        self.pre_select_columns = [
            'eTIME', 'Gas Path', 'Catalyst Temperature', 'Limit Adjusted iSCB_RH',
            'Ambient Pressure', 'Limit Adjusted iSCB_LAT', 'Load Percent',
            'Limit Adjusted iCOOL_TEMP', 'Engine RPM', 'Vehicle Speed',
            'Mass Air Flow Rate', 'Catalyst Temp. 1-1', 'F/A Equiv. Ratio',
            'Engine Fuel Rate', 'Eng. Exh. Flow Rate', 'GPS Latitude',
            'GPS Longitude', 'Limit Adjusted iGPS_ALT', 'Limit Adjusted iGPS_GROUND_SPEED',
            'Fuel Rate', 'Instantaneous Fuel Flow', 'Derived Engine Torque.1',
            'Derived Engine Power.1', 'Instantaneous Mass CO2', 'Instantaneous Mass CO',
            'Instantaneous Mass NO', 'Instantaneous Mass NO2', 'Instantaneous Mass NOx',
            'Corrected Instantaneous Mass NOx', 'Instantaneous Mass HC',
            'Instantaneous Mass CH4', 'Instantaneous Mass NMHC', 'Instantaneous Mass O2',
            'Air/Fuel Ratio at stoichiometry', 'Air/Fuel Ratio of Sample', 'Lambda',
            'Ambient Temperature', 'AMB Ambient Temperature',
            'Brake Specific Fuel Consumption', 'Mass Air Flow Rate.1'
        ]
        self.pre_select_vars = [
            'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP',
            'iSCB_LAT', 'iENG_LOAD', 'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED',
            'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'icMASS_FLOWx', 'EXH_RATE',
            'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps',
            'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm',
            'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm',
            'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc',
            'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'
        ]
        # Map "friendly display" header -> variable name header
        self.columns_vars_map = dict(zip(self.pre_select_columns, self.pre_select_vars))

        # Alignment label to DataFrame column mapping (33)
        self.align_map = {
            "Vehicle Speed": "iVEH_SPEED",
            "Engine RPM": "iENG_SPEED",
            "Exhaust Mass Flow Rate": "icMASS_FLOW",
            "Total Current": "TotalCurrent"
        }

        # Trace variables
        self.obd_file_path.trace_add("write", self.check_alignment_input_state)
        self.alignment_checked.trace_add("write", self.toggle_obd_widgets)
        self.align_values_var.trace_add("write", self.update_plot_button_state)
        self.pre_selected_columns_var.trace_add("write", self.refresh_columns_listbox)

        # Icons (in-memory)
        self.icon_folder = self.create_icon("Folder", "#ffe680", "#E8B931")
        self.icon_read = self.create_icon("Read", "#ffffff", "#0078d4", text_color="#0078d4")
        self.icon_truck = self.create_icon("Truck", "#73ec8e", "#107c10")
        self.icon_figure = self.create_icon("Figure", "#73ec8e", "#107c10")

        # =========================================================================
        # 1) PEMS File Section
        # =========================================================================
        self.frame_pems = tk.Frame(root, bg="#f3f3f3")
        self.frame_pems.pack(fill="x", padx=20, pady=(15, 5))

        lbl_pems = tk.Label(self.frame_pems, text="PEMS File", font=self.font_default, bg="#f3f3f3")
        lbl_pems.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.ent_pems = tk.Entry(self.frame_pems, textvariable=self.pems_file_path, font=self.font_default)
        self.ent_pems.grid(row=0, column=1, sticky="ew")

        self.btn_select = tk.Button(self.frame_pems, image=self.icon_folder, command=self.select_pems_file,
                                    bd=0, bg="#f3f3f3", activebackground="#e5e5e5", cursor="hand2")
        self.btn_select.grid(row=0, column=2, padx=5)
        self.create_tooltip(self.btn_select, "Select a file")
        self.frame_pems.columnconfigure(1, weight=1)  # Tight fit between label and icons

        # =========================================================================
        # 9) Input Directory Checkbox
        # =========================================================================
        self.frame_dir = tk.Frame(root, bg="#f3f3f3")
        self.frame_dir.pack(fill="x", padx=20, pady=0)
        chk_input_dir = tk.Checkbutton(self.frame_dir,
                                       text="Check to process all CSV file in a folder",
                                       variable=self.input_file_dir_checked,
                                       font=self.font_default, bg="#f3f3f3",
                                       activebackground="#f3f3f3", selectcolor="white")
        chk_input_dir.pack(anchor="w")

        # =========================================================================
        # 11) Data Fields Listbox
        # =========================================================================
        self.frame_cols = tk.Frame(root, bg="#f3f3f3")
        self.frame_cols.pack(fill="x", padx=20, pady=5)

        tk.Label(self.frame_cols, text="Data Fields", font=self.font_header, bg="#f3f3f3").pack(anchor="w")

        # Create a container so the checkbox sits directly below the listbox+scrollbar row
        lb_container = tk.Frame(self.frame_cols, bg="#f3f3f3")
        lb_container.pack(fill="x", pady=(2, 2))

        sb_cols = tk.Scrollbar(lb_container, orient="vertical")
        self.columns_listbox = tk.Listbox(lb_container, height=10, font=self.font_default,
                                          selectmode=tk.MULTIPLE, yscrollcommand=sb_cols.set,
                                          exportselection=False, borderwidth=1, relief="solid")
        self.columns_listbox.pack(side="left", fill="both", expand=True)
        sb_cols.config(command=self.columns_listbox.yview)
        sb_cols.pack(side="right", fill="y")

        # Track user selections to build selected_columns_list (14)
        self.columns_listbox.bind("<<ListboxSelect>>", self.update_selected_columns_list)

        # 13) Pre-selected Columns Checkbox (now just below the listbox)
        self.chk_pre_selected = tk.Checkbutton(
            self.frame_cols, text="Display Selected Data Fields only",
            variable=self.pre_selected_columns_var,
            font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3"
        )
        self.chk_pre_selected.pack(anchor="w", pady=(4, 4))

        # =========================================================================
        # 14-17) Time Alignment Listbox
        # =========================================================================
        self.frame_align_list = tk.Frame(root, bg="#f3f3f3")
        self.frame_align_list.pack(fill="x", padx=20, pady=5)

        tk.Label(self.frame_align_list, text="Time Alignment", font=self.font_header, bg="#f3f3f3").pack(anchor="w")

        sb_align = tk.Scrollbar(self.frame_align_list, orient="vertical")
        self.align_listbox = tk.Listbox(self.frame_align_list, height=5, font=self.font_default,
                                        selectmode=tk.SINGLE, yscrollcommand=sb_align.set,
                                        exportselection=False, borderwidth=1, relief="solid")
        sb_align.config(command=self.align_listbox.yview)
        sb_align.pack(side="right", fill="y")
        self.align_listbox.pack(side="left", fill="x", expand=True)

        # Populate Alignment Options and pre-select 'Vehicle Speed' (41, 43)
        align_opts = ['Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', 'Total Current']
        for item in align_opts:
            self.align_listbox.insert(tk.END, item)
        self.align_listbox.selection_set(0)

        # =========================================================================
        # 19) Alignment & Report Checkboxes
        # =========================================================================
        self.frame_checks = tk.Frame(root, bg="#f3f3f3")
        self.frame_checks.pack(fill="x", padx=20, pady=5)

        chk_align = tk.Checkbutton(self.frame_checks, text="Alignment", variable=self.alignment_checked,
                                   font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3")
        chk_align.pack(side="left", padx=(0, 20))

        chk_report = tk.Checkbutton(self.frame_checks, text="Report", variable=self.report_checked,
                                    font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3")
        chk_report.pack(side="left")

        # =========================================================================
        # 20-22) OBD File Section
        # =========================================================================
        self.frame_obd = tk.Frame(root, bg="#f3f3f3")
        self.frame_obd.pack(fill="x", padx=20, pady=5)

        tk.Label(self.frame_obd, text="OBD File", font=self.font_default, bg="#f3f3f3")\
            .grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.ent_obd = tk.Entry(self.frame_obd, textvariable=self.obd_file_path,
                                font=self.font_default, state="disabled")
        self.ent_obd.grid(row=0, column=1, sticky="ew")
        self.create_tooltip(self.ent_obd, "Press a OBD button to select an OBD/HEMDATA file")

        self.btn_obd = tk.Button(self.frame_obd, image=self.icon_truck, command=self.select_obd_file,
                                 bd=0, bg="#f3f3f3", activebackground="#e5e5e5",
                                 cursor="hand2", state="disabled")
        self.btn_obd.grid(row=0, column=3, padx=5)
        self.create_tooltip(self.btn_obd, "Select OBD file")

        self.frame_obd.columnconfigure(1, weight=1)

        # =========================================================================
        # 27-33) Check Alignment and Plot controls
        # =========================================================================
        self.frame_check_align = tk.Frame(root, bg="#f3f3f3")
        self.frame_check_align.pack(fill="x", padx=20, pady=10)

        # 37) Magenta background, callback with selected items
        self.btn_check_align = tk.Button(self.frame_check_align, text="Check Alignment",
                                         command=self.check_alignment, font=self.font_default, bg="#ff80ff", width=16)
        self.btn_check_align.pack(side="left", padx=(0, 10))
        self.create_tooltip(self.btn_check_align, "Check/Plot Alignment")

        self.ent_align_input = tk.Entry(self.frame_check_align, textvariable=self.align_values_var,
                                        font=self.font_default, state="disabled")
        self.ent_align_input.pack(side="left", fill="x", expand=True)
        self.create_tooltip(self.ent_align_input, "Type Alignment Values to OBD")

        # 30-32) Plot button with icon_figure placed at btn_select x
        self.btn_plot = tk.Button(self.frame_check_align, image=self.icon_figure, relief="flat",
                                  bg="#F3F3F3", activebackground="#EDEDED",
                                  command=self.check_alignment_view,
                                  state="disabled", cursor="hand2")
        self.btn_plot.pack(side="left", padx=(10, 0))
        self.create_tooltip(self.btn_plot, "Plot Alignments")

        # =========================================================================
        # 39) RUN Button
        # =========================================================================
        self.btn_run = tk.Button(root, text="RUN", command=self.run_analysis,
                                 font=self.font_run, bg="#add8e6", height=1)
        self.btn_run.pack(fill="x", padx=20, pady=(10, 20))

        # Position OBD and Plot buttons aligned to Select button x-coordinate (25, 31, 32)
        self.root.after(300, self.position_obd_and_plot_buttons)

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def create_icon(self, icon_type, fill_color, border_color, text_color="black"):
        """Generates a simple 40x30 icon in-memory using Pillow."""
        w, h = 40, 30
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, w-1, h-1), fill=fill_color, outline=border_color, width=2)

        if icon_type == "Folder":
            draw.rectangle((5, 8, w-5, h-8), outline="#555", width=1)
            draw.line((5, 8, 15, 8), fill="#555", width=1)
        elif icon_type == "Read":
            for y in [8, 14, 20]:
                draw.line((8, y, w-8, y), fill=text_color, width=2)
        elif icon_type == "Truck":
            draw.rectangle((5, 10, 25, 22), fill="#333")
            draw.rectangle((25, 14, 34, 22), fill="#333")
            draw.ellipse((8, 20, 14, 26), fill="black")
            draw.ellipse((24, 20, 30, 26), fill="black")
        elif icon_type == "Figure":
            col = (154, 92, 230)
            draw.rounded_rectangle([w*0.08, h*0.12, w*0.92, h*0.88], radius=6, fill=col)
            draw.line([(w*0.18, h*0.78), (w*0.85, h*0.78)], fill=(255, 255, 255), width=2)
            draw.line([(w*0.18, h*0.25), (w*0.18, h*0.78)], fill=(255, 255, 255), width=2)
            pts = [(w*0.18, h*0.70), (w*0.30, h*0.55), (w*0.38, h*0.60),
                   (w*0.50, h*0.40), (w*0.62, h*0.48), (w*0.74, h*0.35), (w*0.85, h*0.42)]
            draw.line(pts, fill=(255, 255, 255), width=3)
        return ImageTk.PhotoImage(img)

    def create_tooltip(self, widget, text):
        def enter(event):
            self.tooltip = tk.Label(self.root, text=text, bg="#ffffe0",
                                    relief="solid", borderwidth=1, font=("Segoe UI", 9))
            x = widget.winfo_rootx() - self.root.winfo_rootx() + 10
            y = widget.winfo_rooty() - self.root.winfo_rooty() + 35
            self.tooltip.place(x=x, y=y)
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def position_obd_and_plot_buttons(self):
        """
        Align OBD & Plot button x-coordinates to btn_select.winfo_x().
        Also make OBD Entry width slightly less than the OBD button x-coordinate.
        """
        try:
            self.root.update_idletasks()
            read_x_root = self.btn_select.winfo_rootx()
            # Compute positions relative to frames (25, 31, 32)
            obd_x = read_x_root - self.frame_obd.winfo_rootx()
            plot_x = read_x_root - self.frame_check_align.winfo_rootx()

            try:
                self.btn_obd.grid_forget()
            except Exception:
                pass
            self.btn_obd.place(x=obd_x, y=0)

            try:
                self.btn_plot.place_forget()
            except Exception:
                pass
            self.btn_plot.place(x=plot_x, y=0)

            # Adjust OBD Entry width (approximate chars by ~8 px per char) (26)
            entry_x = self.ent_obd.winfo_x()
            px_available = max(obd_x - entry_x - 12, 40)
            width_chars = max(int(px_available / 8), 10)
            self.ent_obd.config(width=width_chars)
        except Exception:
            self.root.after(300, self.position_obd_and_plot_buttons)

    def toggle_obd_widgets(self, *args):
        """Enable/Disable OBD widgets based on Alignment Checkbox (21)."""
        is_checked = self.alignment_checked.get()
        state = "normal" if is_checked else "disabled"
        self.ent_obd.config(state=state)
        self.btn_obd.config(state=state)
        self.check_alignment_input_state()

    def check_alignment_input_state(self, *args):
        """Enable align input entry only if Alignment is checked AND OBD file selected (28)."""
        if self.alignment_checked.get() and self.obd_file_path.get().strip():
            self.ent_align_input.config(state="normal")
        else:
            self.ent_align_input.config(state="disabled")
        self.update_plot_button_state()

    def update_plot_button_state(self, *args):
        """Enable Plot button only when align_values_var is not empty (29)."""
        if self.align_values_var.get().strip():
            self.btn_plot.config(state="normal")
        else:
            self.btn_plot.config(state="disabled")

    def update_selected_columns_list(self, event=None):
        """Maintain the selected_columns_list based on user selections (14)."""
        items = self.columns_listbox.get(0, tk.END)
        selected_idxs = self.columns_listbox.curselection()
        current_selected = [items[i] for i in selected_idxs]
        self.selected_columns_list = list(current_selected)

    def refresh_columns_listbox(self, *args):
        """Refresh columns_listbox based on the pre_selected_columns checkbox (14, 15)."""
        self.columns_listbox.delete(0, tk.END)

        if self.pre_selected_columns_var.get():
            for i, col in enumerate(self.selected_columns_list):
                self.columns_listbox.insert(tk.END, col)
                self.columns_listbox.selection_set(i)
        else:
            if self.columns_row is not None:
                for col in self.columns_row:
                    self.columns_listbox.insert(tk.END, str(col))
                list_items = self.columns_listbox.get(0, tk.END)
                for idx, item in enumerate(list_items):
                    if item in self.selected_columns_list:
                        self.columns_listbox.selection_set(idx)

    # ---------------------------------------------------------------------
    # File dialogs
    # ---------------------------------------------------------------------
    def select_pems_file(self):
        file = filedialog.askopenfilename(title="Select PEMS File", filetypes=[("CSV", "*.csv")])
        if file:
            self.pems_file_path.set(file)
            # Per (1, 11): read file immediately after selecting and preselect columns
            self.read_file()

    def select_obd_file(self):
        """Read OBD/HEMDATA CSV and prepare its DataFrame, summary, and eTIME (22-26)."""
        file = filedialog.askopenfilename(title="Select OBD File", filetypes=[("CSV", "*.csv")])
        if not file:
            return

        self.obd_file_path.set(file)
        self.obd_df = None
        self.obd_df_summary = None

        try:
            # Read OBD CSV
            tmp = pd.read_csv(file, encoding='utf-8', low_memory=False, skiprows=0, header=0)

            # Remove 'Not Available' / 'Unnamed' columns
            tmp = tmp.loc[:, ~tmp.columns.str.contains("Not Available|Unnamed", case=False, na=False)]

            # Insert eTIME label rows BEFORE header assignment in step 24 (23 in first list)
            if 'eTIME' not in tmp.columns:
                tmp.insert(1, 'eTIME', None)
                tmp.loc[0, 'eTIME'] = 'eTIME'
                tmp.loc[1, 'eTIME'] = 's'

            # Assign header rows (local to OBD), then slice data
            obd_columns_row = tmp.columns
            obd_vars_row = tmp.loc[0, :]
            obd_units_row = tmp.loc[1, :]

            # Rename columns to variable headers and slice out data rows
            tmp.columns = obd_vars_row

            # Extract summary & data blocks using "Summary Information:" in first column
            try:
                first_col = tmp.columns[0]
                summary_row_idx = pd.Index(tmp[first_col]).get_loc("Summary Information:")

                # Save summary
                self.obd_df_summary = tmp.loc[summary_row_idx:, :].copy()
                self.obd_df_summary.to_csv("obd_df_summary.csv", index=False, header=False)

                # Data up to (summary_row_idx - 1)
                tmp = tmp.loc[2:summary_row_idx-1, :].copy()
            except Exception:
                # If no summary section, use all data
                tmp = tmp.loc[2:, :].copy()

            # Clean and filter SAMPLE rows if present
            tmp.dropna(how='all', inplace=True)
            if 'sSTATUS_PATH' in tmp.columns:
                tmp = tmp.loc[tmp['sSTATUS_PATH'] == 'SAMPLE', :].copy()

            tmp.reset_index(drop=True, inplace=True)

            # Ensure eTIME (seconds) for OBD (23’s first sentence)
            tmp = ensure_eTIME(tmp)

            self.obd_df = tmp

        except Exception as e:
            messagebox.showerror("OBD Read Error", f"Failed to read OBD file:\n{e}")
            self.obd_df = None

        # Update alignment input state
        self.check_alignment_input_state()

    # ---------------------------------------------------------------------
    # Reading and UI population
    # ---------------------------------------------------------------------
    def read_file(self):
        """
        Read the selected PEMS CSV:
        - Use pd.read_csv(... encoding='utf-8', low_memory=False, skiprows=0, header=0).
        - Remove 'Not Available' / 'Unnamed' columns.
        - Ensure eTIME label rows (5) and eTIME seconds creation from sTIME (4).
        - Assign header rows (6).
        - Build df_summary from 'Summary Information:' (7/46).
        - Populate columns listbox and pre-select specified columns (10, 11, 12).
        """
        path = self.pems_file_path.get()
        if not path:
            messagebox.showwarning("Warning", "Please select a PEMS file first.")
            return

        # Empty the listbox before reading (12)
        self.columns_listbox.delete(0, tk.END)

        try:
            # Read CSV exactly as specified (1)
            self.df = pd.read_csv(path, encoding='utf-8', low_memory=False, skiprows=0, header=0)

            # Remove columns with "Not Available" or "Unnamed" (3)
            self.df = self.df.loc[:, ~self.df.columns.str.contains("Not Available|Unnamed", case=False, na=False)]

            # 5) Insert eTIME label rows if not present
            if 'eTIME' not in self.df.columns:
                self.df.insert(1, 'eTIME', None)
                self.df.loc[0, 'eTIME'] = 'eTIME'
                self.df.loc[1, 'eTIME'] = 's'

            # 6) Assign header rows
            self.columns_row = self.df.columns
            self.vars_row = self.df.loc[0, :]
            self.units_row = self.df.loc[1, :]

            # Rename columns to variable headers and slice out data rows
            self.df.columns = self.vars_row

            # 7/46) Create df_summary and slice main df using "Summary Information:"
            first_col = self.df.columns[0]
            try:
                summary_row_idx = pd.Index(self.df[first_col]).get_loc("Summary Information:")
                # Save df_summary
                self.df_summary = self.df.loc[summary_row_idx:, :].copy()
                self.df_summary.to_csv("pems_df_summary.csv", index=False, header=False)
                # Data from rows 2 to summary_row_idx - 1
                self.df = self.df.loc[2:summary_row_idx-1, :].copy()
            except Exception:
                # If summary row not found, just slice data rows
                self.df_summary = pd.DataFrame()
                self.df = self.df.loc[2:, :].copy()

            # Drop fully empty rows
            self.df.dropna(how='all', inplace=True)

            # Keep SAMPLE rows if the column exists
            if 'sSTATUS_PATH' in self.df.columns:
                self.df = self.df.loc[self.df['sSTATUS_PATH'] == 'SAMPLE', :].copy()

            self.df.reset_index(drop=True, inplace=True)

            # 4) Ensure eTIME in seconds (from sTIME) after reading and slicing
            self.df = ensure_eTIME(self.df)

            # 10/11) Populate columns_listbox and pre-select pre_select_columns
            available_cols = list(self.columns_row) if self.columns_row is not None else []
            self.selected_columns_list = [c for c in self.pre_select_columns if c in available_cols]

            if self.pre_selected_columns_var.get():
                for i, col in enumerate(self.selected_columns_list):
                    self.columns_listbox.insert(tk.END, col)
                    self.columns_listbox.selection_set(i)
            else:
                for col in available_cols:
                    self.columns_listbox.insert(tk.END, str(col))
                list_items = self.columns_listbox.get(0, tk.END)
                for idx, item in enumerate(list_items):
                    if item in self.selected_columns_list:
                        self.columns_listbox.selection_set(idx)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")

    # ---------------------------------------------------------------------
    # Alignment plotting logic
    # ---------------------------------------------------------------------
    def check_alignment(self):
        """
        Callback for Check Alignment button:
        - Use selected item in align_listbox to determine align column
        - Map via self.align_map
        - Call plot_check_alignment(...) per spec (34, 35)
        """
        selected_indices = self.align_listbox.curselection()
        selected_value = self.align_listbox.get(selected_indices[0]) if selected_indices else None
        print(f"Executing check_alignment() with: {[selected_value] if selected_value else []}")

        # Map friendly label to data column
        align_col = self.align_map.get(selected_value, selected_value) if selected_value else None

        self.plot_check_alignment(
            self.ent_pems.get(),
            self.ent_obd.get(),
            self.df,
            align_col
        )

    def check_alignment_view(self):
        """
        36 & 38) Call plot_alignment with file paths, the selected align column label (mapped),
        and the align_values entry (treated as time shift if numeric, or as column name if non-numeric).
        """
        selected_indices = self.align_listbox.curselection()
        selected_value = self.align_listbox.get(selected_indices[0]) if selected_indices else None
        print(f"Executing check_alignment_view() with: {[selected_value] if selected_value else []}")

        # Map friendly label to data column
        align_col = self.align_map.get(selected_value, selected_value) if selected_value else None

        self.plot_alignment(
            self.ent_pems.get(),
            self.ent_obd.get(),
            align_col,
            self.align_values_var.get()
        )

    def plot_check_alignment(self, pems_path, obd_path, pems_df, align_col):
        """
        35) Check/Plot Alignment logic with ImageDistanceMeasurer and provided conditional code.
        """
        if pems_df is None or pems_df.empty:
            messagebox.showwarning("Warning", "Please read a PEMS file before plotting alignment.")
            return

        align_col = (align_col or "").strip()
        if not align_col:
            messagebox.showinfo("Info", "Please select an alignment item from the list.")
            return

        self.data_to_align = []
        notes = []

        # PEMS series
        if align_col in pems_df.columns:
            x_pems = get_time_axis(pems_df)
            y_pems = pd.to_numeric(pems_df[align_col], errors='coerce')
            self.data_to_align.append((x_pems, y_pems, "PEMS"))
        else:
            notes.append(f"'{align_col}' not found in PEMS data.")

        # OBD series (if loaded)
        if self.obd_df is not None and not self.obd_df.empty:
            if align_col in self.obd_df.columns:
                x_obd = get_time_axis(self.obd_df)
                y_obd = pd.to_numeric(self.obd_df[align_col], errors='coerce')
                self.data_to_align.append((x_obd, y_obd, "OBD"))
            else:
                notes.append(f"'{align_col}' not found in OBD data.")

        # 35) Provided snippet logic
        if plt.get_fignums(): 
            plt.close('all')
        ImageDistanceMeasurer(pems_df, self.data_to_align, align_col)

        if notes:
            messagebox.showinfo("Notes", "Notes:\n- " + "\n- ".join(notes))

    def plot_alignment(self, pems_path, obd_path, align_col, align_values_str=None):
        """
        32, 36, 38) Plot alignment.
        - If align_values_str is numeric, interpret as time offset (seconds) applied to PEMS X.
        - If align_values_str is non-numeric and not empty, treat it as a column name to plot instead of align_col.
        Plots the selected/typed column in both PEMS (self.df) and OBD (self.obd_df).
        """
        if self.df is None or self.df.empty:
            messagebox.showwarning("Warning", "Please read a PEMS file before plotting alignment.")
            return

        typed_col = (align_col or "").strip()

        # Decide how to interpret align_values_str
        offset_seconds = 0.0
        if align_values_str and align_values_str.strip():
            s = align_values_str.strip()
            try:
                offset_seconds = float(s)  # numeric -> shift
            except Exception:
                typed_col = s  # non-numeric -> use as column name to plot

        if not typed_col:
            # Fallback to listbox selection if nothing provided
            selected_indices = self.align_listbox.curselection()
            selected_value = self.align_listbox.get(selected_indices[0]) if selected_indices else None
            typed_col = self.align_map.get(selected_value, selected_value if selected_value else "")

        if not typed_col:
            messagebox.showinfo("Info", "Please select an item from Time Alignment or enter a column name.")
            return

        notes = []
        self.data_to_align = []

        # PEMS
        if typed_col in self.df.columns:
            x_pems = get_time_axis(self.df)
            y_pems = pd.to_numeric(self.df[typed_col], errors='coerce')
            self.data_to_align.append((x_pems, y_pems, "PEMS"))
        else:
            notes.append(f"'{typed_col}' not found in PEMS data.")

        # OBD
        if self.obd_df is not None and not self.obd_df.empty:
            if typed_col in self.obd_df.columns:
                x_obd = get_time_axis(self.obd_df)
                y_obd = pd.to_numeric(self.obd_df[typed_col], errors='coerce')
                self.data_to_align.append((x_obd, y_obd, "OBD"))
            else:
                notes.append(f"'{typed_col}' not found in OBD data.")

        if not self.data_to_align:
            msg = "No data found to plot."
            if notes:
                msg += "\n\nDetails:\n- " + "\n- ".join(notes)
            messagebox.showwarning("Plot Alignment", msg)
            return

        # Destroy prior plot window (if any)
        if hasattr(self, 'plot_top') and self.plot_top and self.plot_top.winfo_exists():
            try:
                self.plot_top.destroy()
            except Exception:
                pass

        self.plot_top = tk.Toplevel(self.root)
        self.plot_top.title(f"Alignment Plot - {typed_col}")
        self.plot_top.geometry("1366x768")

        fig = Figure(figsize=(13.66, 7.68), dpi=100)
        ax1 = fig.add_subplot(211)

        idx = 0
        for x_vals, y_vals, label in self.data_to_align:
            if idx == 0:
                ax1.plot(x_vals, y_vals, label=label, linewidth=1)
            else:
                ax1.plot(x_vals, y_vals, '--', label=label, linewidth=1)
            idx += 1
        ax1.set_ylabel(typed_col)
        ax1.set_title(f"Alignment: {typed_col}")
        ax1.grid(True, linestyle="--", alpha=0.4)
        ax1.legend(loc="upper left")
        ax1.set_xticks([])

        ax2 = fig.add_subplot(212)
        idx = 0
        for x_vals, y_vals, label in self.data_to_align:
            # Shift only the first series (PEMS) by offset_seconds for visualization
            if idx == 0:
                ax2.plot(x_vals + offset_seconds, y_vals, label=label, linewidth=1)
            else:
                ax2.plot(x_vals, y_vals, '--', label=label, linewidth=1)
            idx += 1
        ax2.set_xlabel("Time (s)" if 'eTIME' in self.df.columns else "Index")
        ax2.set_ylabel(typed_col)
        ax2.grid(True, linestyle="--", alpha=0.4)

        fig.tight_layout(pad=2.0)

        if notes:
            messagebox.showinfo("Notes", "Notes:\n- " + "\n- ".join(notes))

        canvas = FigureCanvasTkAgg(fig, master=self.plot_top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------------------------------------------------------------
    # RUN
    # ---------------------------------------------------------------------
    def run_analysis(self):
        """
        Callback for RUN Button: keep current behavior and add required prints (44).
        """
        print("--- RUN ANALYSIS ---")
        print(f"OBD Entry Widget Object: {self.ent_obd}")
        print(f"PEMS Entry Widget Object: {self.ent_pems}")
        print(f"OBD filename: {self.ent_obd.get()}")
        print(f"PEMS filename: {self.ent_pems.get()}")

        print(f"Alignment Checkbox: {self.alignment_checked.get()}")
        print(f"Report Checkbox: {self.report_checked.get()}")
        print(f"Input_file_dir Checkbox: {self.input_file_dir_checked.get()}")

        print(f"Check Alignment Button Object: {self.btn_check_align}")
        print(f"Align Values Textbox Content: '{self.align_values_var.get()}'")

        # 44) Print index of 'Vehicle Speed' (or iVEH_SPEED) in df.columns if exists
        if self.df is not None:
            col_name = None
            if 'Vehicle Speed' in self.df.columns:
                col_name = 'Vehicle Speed'
            elif 'iVEH_SPEED' in self.df.columns:
                col_name = 'iVEH_SPEED'
            if col_name:
                try:
                    idx = self.df.columns.get_loc(col_name)
                    print(f"Index of '{col_name}' in self.df: {idx}")
                except Exception as e:
                    print(f"Error finding index of '{col_name}': {e}")
            else:
                print("'Vehicle Speed' (or mapped 'iVEH_SPEED') not found in DataFrame columns.")
        else:
            print("DataFrame not loaded.")

        selected_cols = [self.columns_listbox.get(i) for i in self.columns_listbox.curselection()]
        selected_align = [self.align_listbox.get(i) for i in self.align_listbox.curselection()]
        summary = (
            f"PEMS file: {self.ent_pems.get()}\n"
            f"OBD file: {self.ent_obd.get() if self.alignment_checked.get() else '(disabled)'}\n"
            f"Selected columns: {selected_cols}\n"
            f"Alignment selections: {selected_align}\n"
            f"Alignment_checked: {self.alignment_checked.get()}\n"
            f"Report_checked: {self.report_checked.get()}\n"
            f"Input_file_dir_checked: {self.input_file_dir_checked.get()}\n"
            f"Align Values Textbox Content: '{self.align_values_var.get()}'"
        )
        messagebox.showinfo("RUN", "Analysis started.\n\n" + summary)

# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PEMSAnalysisGUI(root)
    root.mainloop()