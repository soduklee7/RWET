"""
Update a Windows 11 color style 600x750 size PEMS Data Analysis PEMSAnalysisGUI(object) GUI using tkinter, pillow icons, and default font size 12, and the Python code here.
1)	Create a text box with a "PEMS File" label and the "Select" button to select a CSV file. Read the selected file using self.df = pd.read_csv with encoding='utf-8', low_memory=False, skiprows=0, header=0 and skipping first 0 rows in the “read_file” fuction when clicking the " Select " button. 
2)	Replace the "Select" button with the self.icon_folder for a Windows 11 style “Folder” large color icon. Display the "Select a file" when placing a mouse pointer on the "Select" icon. Adjust the textbox length to tightly fit with the "Select" button horizontally.
3)	Remove columns with "Not Available" or "Unnamed" in the self.df.columns.
4)	Update the “read_file” fuction by create eTIME by converting hh:mm:s.xxx format data in self.df['TIME] in seconds using the ensure_eTIME() function after reading the file and then add the following code part.
5)	Use the following code before assigning columns_row, vars_row and units_row.
if 'eTIME' not in self.df.columns:
self.df.insert(1, 'eTIME', None)
self.df.loc[0, 'eTIME'] = 'eTIME'
self.df.loc[1, 'eTIME'] = 's'
6)	Assign columns_row = self.df.columns, vars_row = self.df.loc[0, :] and units_row = self.df.loc[1, :]. Update self.df = self.df.loc[2:, :].
7)	Create self.df_summary data frame starting from the row that contains the "Summary Information:" in the first column of self.df data frame using the summary_row_idx = pd.Index(self.df[first_col]).get_loc("Summary Information:") in the “read_file” function.
8)	Save self.df_summary using self.df_summary.to_csv(). 
9)	Create self.df = self.df.loc[2:summary_row_idx-1, :].copy()
10)	Create pre_select_columns = ['eTIME', 'Gas Path', 'Catalyst Temperature', 'Limit Adjusted iSCB_RH', 'Ambient Pressure', 'Limit Adjusted iSCB_LAT', 'Load Percent',  'Limit Adjusted iCOOL_TEMP', 'Engine RPM', 'Vehicle Speed', 'Mass Air Flow Rate', 'Catalyst Temp. 1-1', 'F/A Equiv. Ratio', 'Engine Fuel Rate',  'Eng. Exh. Flow Rate', 'GPS Latitude', 'GPS Longitude', 'Limit Adjusted iGPS_ALT', 'Limit Adjusted iGPS_GROUND_SPEED', 'Fuel Rate', 'Instantaneous Fuel Flow',  'Derived Engine Torque.1', 'Derived Engine Power.1', 'Instantaneous Mass CO2', 'Instantaneous Mass CO', 'Instantaneous Mass NO', 'Instantaneous Mass NO2',  'Instantaneous Mass NOx', 'Corrected Instantaneous Mass NOx', 'Instantaneous Mass HC', 'Instantaneous Mass CH4', 'Instantaneous Mass NMHC', 'Instantaneous Mass O2', 'Air/Fuel Ratio at stoichiometry', 'Air/Fuel Ratio of Sample', 'Lambda', 'Ambient Temperature', 'AMB Ambient Temperature', 'Brake Specific Fuel Consumption', 'Mass Air Flow Rate.1'] in the “read_file” function.
11)	Create  pre_select_vars = [ 'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD',  'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'icMASS_FLOWx', 'EXH_RATE',  'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP' ] in the “read_file” function
12)	Create an "Input_file_dir" checkbox labeled "Process all CSV files in a Folder". Create the "Input_file_dir_checked" variable to pass the status. Create the "pre_selected_columns" checkbox button labeled the “Display Selected Data Fields only”. Locate an "Input_file_dir" checkbox and the “pre_selected_columns” checkbox horizontally.
13)	After clicking the "btn_select" icon, select the pre_select_columns in the columns_listbox.  When you click the “btn_select” button, the items in pre_select_columns are selected in the columns_listbox.
14)	Create a 10-row scrollable "columns_listbox" list box to display the data frame column header for data labeling. Label the "columns_listbox" list box with the "Data Fields". Enable multiple selection in the list box by clicking mouse pointers. 
15)	Empty the "columns_listbox" list box before clicking the "btn_select" icon.
16)	Create the “selected_columns_list” list to store additionally selected items in the “columns_listbox” list box. Show only the selected_columns_list in the “columns_listbox” list box when the “pre_selected_columns” checkbox is checked. Update the refresh_columns_listbox method so that when “Display Selected Data Fields only” is not checked, the listbox shows self.columns_row and then select any items that match selected_columns_list. 
17)	Create a 5-row scrollable "align_listbox" list box labeled “Time Alignment” to display the 'Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', and 'Total Current' alignment data. Enable single selection in the list box by clicking a mouse pointer. 
18)	Create a 5-row scrollable "data_format_listbox" list box labeled “Data Format” to display the 'EPA PEMS', 'EPA Dyno', 'EPA BEV', and 'FEV PEMS' alignment data. Select the 'EPA PEMS' in the "data_format_listbox" list box.
19)	Locate the "align_listbox" label and "data_format_listbox" label horizontally.
20)	Create an "Alignment" checkbox button and "Report" checkbox button horizontally to call back functions. Check the "Report" checkbox.
21)	Locate the "Alignment" checkbox button and "Report" checkbox button horizontally.
22)	Create a text box with an "OBD File" label. Display the "Press a OBD button to select an OBD/HEMDATA file" when placing a mouse pointer on the "OBD File" text box.
23)	Create an "OBD" button. Replace the "OBD" button with the self.icon_truck for a Windows 11 color Truck icon to select a CSV file. Display the "Select OBD file" when placing a mouse pointer on the "OBD" icon. Only Enable the "OBD File" text box and "OBD" button when the "Alignment" checkbox is True.
24)	Call the select_obd_file function to read the OBD file when clicking the "OBD" button. Read the selected file using tmp = pd.read_csv(file, encoding='utf-8', low_memory=False, skiprows=0, header=0). Remove columns with "Not Available" or "Unnamed" in the tmp.columns
25)	Add the following code in the select_obd_file function to convert hh:mm:s.xxx format data in tmp['TIME] in seconds using the ensure_eTIME() function after reading the file and then add the following code part.
26)	before assigning columns_row, vars_row and units_row in step 23).
if 'eTIME' not in tmp.columns:
tmp.insert(1, 'eTIME', None)
tmp.loc[0, 'eTIME'] = 'eTIME'
tmp.loc[1, 'eTIME'] = 's'
27)	Assign columns_row = tmp.columns, vars_row = tmp.loc[0, :] and units_row = tmp.loc[1, :]. Update tmp = tmp.loc[2:, :]. Remove all NaN rows using tmp.dropna(how='all', inplace=True) and filter only tmp['sSTATUS_PATH'] == 'SAMPLE' rows.
28)	Create self.obd_df_summary data frame starting from the row that contains the "Summary Information:" in the first column of tmp data frame using the summary_row_idx = pd.Index(tmp[first_col]).get_loc("Summary Information:") in the “select_obd_file” function.
Create self.obd_df = tmp.loc[2:summary_row_idx-1, :].copy()
29)	Save self.obd_df_summary using self.obd_df_summary.to_csv(). 
30)	Adjust the horizontal x coordinate of the "OBD" button at the btn_select.winfo_x().
31)	Adjust the “OBD File” text box width little less than the horizontal x coordinate of the "OBD" button.
32)	Create the “frame_check_align” frame using tk.Frame and pack(fill="x", padx=20, pady=10). Create the "Check Alignment" button labeled the “btn_check_align“. Create a “ent_align_input” input textbox next to the "Check Alignment" button. Display the “Check/Plot Alignment” and the "Type Alignment Values to OBD" when placing a mouse pointer on the "Check Alignment" button and the “btn_check_align“ input textbox respectively. 
33)	Enable the “ent_align_input“ input textbox if the “btn_check_align” alignment checkbox is True and “OBD File” text box is not empty.
34)	Create a "Plot" button next to the “ent_align_input“ input textbox to call back the "plot_alignment” function. Enable only the "Plot" button when the “ent_align_input “ alignment input textbox is not empty.
35)	Replace the "Plot" button labeled “btn_plot” using the self.icon_figure in the following code.
36)	Adjust the horizontal x coordinate of the " btn_plot " button at the btn_select.winfo_x().
37)	Display the "Plot Alignments" when placing a mouse pointer on the " btn_plot " button.
38)	Create the following self.align_map code.
self.align_map = {
"Vehicle Speed": "iVEH_SPEED",
"Engine RPM": "iENG_SPEED",
"Exhaust Mass Flow Rate": "icMASS_FLOW",
"Total Current": "TotalCurrent"
}
39)	Call back the plot_check_alignment when clicking the “btn_check_align“  button.
40)	Close all opened figures using “if plt.get_fignums(): plt.close('all')” before calling the ImageDistanceMeasurer object in the “plot_check_alignment” function.
41)	Create the “check_alignment_view” function to call back the “plot_alignment” function when clicking the self.btn_plot button. 
self.plot_alignment(
self.ent_pems.get(),
self.ent_obd.get(),
align_col
)
42)	Set the "Check Alignment" button with a light magenta-color background to call back "check_alignment()" function with the selected items in the "align_listbox".
43)	Add the self.ent_pems.get(), self.ent_obd.get(), self.align_values_var.get() arguments the plot_alignment function. Plot df[self.align_values_var.get()] in the self.ent_pems.get() and self.ent_obd.get().
44)	Create a font size 20, black bold font, "RUN" big button with a light blue-color background to call back the "run_analysis()" function.
45)	Assign Alignment_checked and Report_checked variables to pass the "Alignment" and "Report" Checkbox check status.
46)	Pre-select the 'Vehicle Speed' in the "align_listbox" listbox.
47)	Fix the _tkinter.TclError: expected integer but got "UI"
48)	Enable to select multiple items in both the columns_listbox. Enable to select a single item in the align_listbox.
49)	Print the obd_ent, pems_ent, "Alignment", "Report", "Input_file_dir" checkbox status, "Check Alignment" button, align_values_ent textbox values, and the index of 'Vehicle Speed' in df.columns when clicking the "RUN" button. Keep current run_analysis() function in the code.
50)	Fix automatically deselecting an item in a listbox while selecting an item in another listbox.
51)	Update that converts the GUI to use two tabs labeled “Main” and “Options/Report” using a bold font size 12, while preserving all existing functionality. 
The “Main” tab contains PEMS/OBD, "Process all CSV files in a Folder" check box, Data Fields, Alignment, Report checkbox, and RUN controls. Change the “Options/Report” tab using blue color font.
52)	Create a text box labeled the "Options/Controls:" and the "Import" button in the “Options/Report” tab to select a folder directory. 
The “Options/Report” tab contains Options import button (now using import.png), "options_listbox" list box and the "reportPMS_listbox" list box.
53)	Create a 10-row scrollable "options_listbox" list box labeled “Options Lists” in the “Options/Report” tab to display the Excel and matlab .mlx files in the selected folder. 
Enable single selection in the list box by clicking a mouse pointer. Locate the "options_listbox" list box just below the “Import” button. 
Create self.df_options for reading data in the “Settings” worksheet of the double-clicked Excel file which contains the “RDE_Settings_” file name. 
Read a matlab .m and .mlx files when double-clicking the .m and .mlx file using the "read_m_file_to_df" function and the "read_mlx_content" function, respectively. 
Save the content of the .m and .mlx files using df.to_csv().
54)	Create a 10-row scrollable "reportPMS_listbox" list box labeled “Report PDF” in the “Options/Report” tab. Enable single selection in the list box by clicking a mouse pointer. 
55)	Create a text box labeled the "Options/Controls:" and the "Import" button in the “Options/Report” tab to select a folder directory. 
56)	Draw a blue solid line between the "options_listbox"  and the "reportPMS_listbox" list box.
57)	Create the “lbl_report_fmt” text box labeled “Report Format:”, “self.ent_report_format” input text box and the “self.btn_format” button labeled “Format” to select a folder directory just above the "reportPMS_listbox" list box in the “Options/Report” tab. 
Replace the “self.btn_format” button with the “PEMSreport.png” icon. Display the Excel and “.mlx” matlab files in the "reportPMS_listbox" list box in the selected folder when clicking the “self.btn_format” button.
58)	Remove self.align_map.get(selected_value, selected_value) in the code and set align_col = selected_value.
59)	Locate the “lbl_report_fmt” text box, “self.ent_report_format” input text box and the “self.btn_format” button just above the "reportPMS_listbox" list box in the “Options/Report” tab. 
"""

"""
PEMSAnalysisGUI11 - Tabs Version
Author: S. Lee

Windows 11 color style PEMS Data Analysis GUI, 600x750, tkinter + Pillow icons,
default font size 12. Implements requirements 1-59.
"""

import os
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw

# matplotlib for plotting
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------------
# import matlab.engine
import os

import pandas as pd

        # self.icon_folder = self.create_icon("Folder", "#ffe680", "#E8B931")
        # self.icon_read = self.create_icon("Read", "#ffffff", "#0078d4", text_color="#0078d4")
        # self.icon_truck = self.create_icon("Truck", "#73ec8e", "#107c10")
        # self.icon_figure = self.create_icon("Figure", "#73ec8e", "#107c10")
        # self.icon_import = self.create_icon("import", "#B4FFB4", "#146414", text_color="#32C832", size=(40, 30))
        # self.icon_PEMSreport = self.create_icon("PEMSreport", "#FFFFFF", "#2850A0", text_color="#2850A0", size=(40, 30))
        # self.icon_Folder24 = self.create_icon("Folder24", "#FFFCD2", "#825F19", text_color="#D7AA46",size=(40, 30))
        # # self.icon_format = self.create_icon("icons/import.png", size=(40, 30))
               
        # # self.icon_PEMSreport = self.load_icon_from_file("icons/PEMSreport.png", size=(40, 30))
        # # self.icon_Folder24 = self.load_icon_from_file("icons/Folder_24.png", size=(40, 30))
        # # self.icon_format = self.load_icon_from_file("icons/import.png", size=(40, 30))

def create_icon(icon_type, fill_color, border_color, text_color="black", size=(40, 30)):
    """Generates a simple 40x30 icon in-memory using Pillow."""
    w, h = size
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
    if icon_type == "Folder24":
        # Folder Back & Tab
        draw.rectangle([4, 4, 15, 10], fill=fill_color, outline=border_color)
        draw.rectangle([4, 8, 36, 26], fill=fill_color, outline=border_color)
        # Folder Front (slightly offset for 3D effect)
        draw.rectangle([6, 12, 36, 26], fill=fill_color, outline=border_color)

    elif icon_type == "PEMSreport":
        # Paper Shape with dog-ear fold
        x0, y0, x1, y1 = 8, 4, 32, 26
        fold = 6
        shape = [(x0, y0), (x1-fold, y0), (x1, y0+fold), (x1, y1), (x0, y1)]
        draw.polygon(shape, fill=fill_color, outline=border_color)
        # Folded corner triangle
        draw.polygon([(x1-fold, y0), (x1-fold, y0+fold), (x1, y0+fold)], fill=fill_color, outline=border_color)
        # Text lines using 'text_color'
        for i, y_off in enumerate(range(12, 24, 4)):
            draw.line([(x0+4, y_off), (x1-4, y_off)], fill=text_color, width=1)

    elif icon_type == "import":
        # The Box/Tray at bottom
        draw.rectangle([6, 18, 34, 26], fill=fill_color, outline=border_color)
        # The Arrow pointing down
        # Shaft
        draw.rectangle([16, 4, 24, 14], fill=text_color, outline=border_color)
        # Head
        draw.polygon([(10, 14), (30, 14), (20, 22)], fill=text_color, outline=border_color)

    # return img
    return ImageTk.PhotoImage(img)


def read_m_file_to_df(file_path):
    data = []
    
    with open(file_path, 'r') as file:
        for line in file:
            # Clean whitespace and ignore empty lines or comments
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            
            # Split by the first '=' found
            if '=' in line:
                parts = line.split('=', 1)
                key = parts[0].strip()
                value = parts[1].strip().split(';', 1)[0] # Remove MATLAB semicolons
                data.append({'Variable': key, 'Value': value})
                
    # Create the DataFrame
    df = pd.DataFrame(data)
    return df

# Usage
# df = read_m_file_to_df('your_script.m')
# print(df)

def read_mlx_content(mlx_file_path):
    # 1. Start the MATLAB engine
    print("Starting MATLAB engine...")
    eng = matlab.engine.start_matlab()

    try:
        # Resolve absolute path for MATLAB
        abs_path = os.path.abspath(mlx_file_path)
        temp_m_file = abs_path.replace('.mlx', '_converted.m')

        # 2. Use MATLAB's 'export' function to convert MLX to plain text .m
        # Note: 'export' requires MATLAB R2022a or later
        print(f"Converting {mlx_file_path} to {temp_m_file}...")
        eng.export(abs_path, temp_m_file, nargout=0)

        # 3. Read the converted .m file content in Python
        with open(temp_m_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Optional: Clean up the temporary file
        # os.remove(temp_m_file)
        
        return content

    except Exception as e:
        return f"Error: {e}"
    finally:
        # 4. Always stop the engine to free resources
        eng.quit()

def get_time_axis(df_local):
    if 'eTIME' in df_local.columns:
        return pd.to_numeric(df_local['eTIME'], errors='coerce')
    else:
        return pd.Series(range(len(df_local)), dtype=float)

def ensure_eTIME(df_local):
    """Ensure df_local has a numeric 'eTIME' column in seconds, derived from 'TIME' (hh:mm:s.xxx) if needed."""
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

    # If eTIME exists but is non-numeric, rebuild from TIME
    if 'eTIME' in df_local.columns:
        df_local['eTIME'] = pd.to_numeric(df_local['eTIME'], errors='coerce')
        if df_local['eTIME'].isna().all() and 'TIME' in df_local.columns:
            df_local['eTIME'] = df_local['TIME'].apply(convert_to_seconds)
            try:
                df_local['eTIME'] = df_local['eTIME'] - float(df_local.loc[2, 'eTIME'])
            except Exception:
                pass
    elif 'TIME' in df_local.columns:
        df_local.insert(1, 'eTIME', None)
        df_local['eTIME'] = df_local['TIME'].apply(convert_to_seconds)
        try:
            df_local['eTIME'] = df_local['eTIME'] - float(df_local.loc[2, 'eTIME'])
        except Exception:
            pass
    return df_local

class ZoomManager:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.base_scale = 1.1  # Zoom intensity
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_scroll(self, event):
        if event.inaxes != self.ax:
            return
        scale_factor = 1 / self.base_scale if event.button == 'up' else self.base_scale
        self._apply_zoom(scale_factor, event.xdata, event.ydata)

    def on_key(self, event):
        if 'ctrl+' in event.key:
            if '+' in event.key or '=' in event.key:
                self._apply_zoom(1 / self.base_scale)
            elif '-' in event.key:
                self._apply_zoom(self.base_scale)

    def _apply_zoom(self, scale_factor, x_center=None, y_center=None):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        if x_center is None:
            x_center = (cur_xlim[0] + cur_xlim[1]) / 2
            y_center = (cur_ylim[0] + cur_ylim[1]) / 2
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        rel_x = (cur_xlim[1] - x_center) / (cur_xlim[1] - cur_xlim[0])
        rel_y = (cur_ylim[1] - y_center) / (cur_ylim[1] - cur_ylim[0])
        self.ax.set_xlim([x_center - new_width * (1 - rel_x), x_center + new_width * rel_x])
        self.ax.set_ylim([y_center - new_height * (1 - rel_y), y_center + new_height * rel_y])
        self.fig.canvas.draw_idle()

class ImageDistanceMeasurer:
    """
    Interactive panel to click twice and measure horizontal & vertical pixel distances
    against plotted series. Used when align_values_var is empty or for visual checks.
    """
    def __init__(self, data_to_plot, align_col):
        self.fig, self.ax = plt.subplots(figsize=(19.2, 10.8))

        idx = 0
        for x_vals, y_vals, label in (data_to_plot):
            if idx == 0:
                self.ax.plot(x_vals, y_vals, label=label, linewidth=1)
            else:
                self.ax.plot(x_vals, y_vals, '--', label=label, linewidth=1)
            idx += 1

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel(align_col)
        self.ax.grid(True, linestyle="--", alpha=0.4)
        self.ax.legend(loc="upper left")
        self.ax.set_title("Click twice to measure pixels (H & V)")
        self.points = []
        self.markers = []
        self.elements = []

        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        zm = ZoomManager(self.fig, self.ax)
        plt.show()

    def onclick(self, event):
        if event.inaxes != self.ax:
            return
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

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def create_icon(icon_type, fill_color, border_color, text_color="black"):
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

def load_icon_from_file(path, size=(40, 30)):
    """Load an external icon and resize to match button size."""
    try:
        img = Image.open(path).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Could not load icon '{path}': {e}")
        return None
