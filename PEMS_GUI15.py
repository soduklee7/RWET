"""
Docstring for PEMS_GUI11
Author: S. Lee
Description: A Windows 11 styled GUI for processing PEMS data with dynamic widget states and in
-memory icon generation.

Create a Windows 11 color styple 600x735 size PEMS Data Analysis GUI using tkinter, pillow icons, and font size 12 for the following.
1) Create a text box with a "PEMS File" label and the "Select" button to select a CSV file. Create the "Read" button to read the selected file using df = pd.read_csv with encoding='utf-8', low_memory=False, skiprows=0, header=0 and skipping first 0 rows when clicking the "Read" button. 
Replace the "Select" button with a Windows 11 color "Folder" large icon. Replace the "Read" button with Windows 11 color "Read File" large icon. Display the "Select a file" and "Read File" when placing a mouse pointer on the "Select" icon and "Read" icon respectively. Adjust the textbox length to tightly fit with the "Select" icon and "Read" icon horizontally.
Assign columns = df.columns, vars = df.loc[0, :] and units = df.loc[1, :]. Update df.columns = vars and df = df.loc[2:, :].
Create eTIME by converting hh:mm:s.xxx format data in df['sTIME] in seconds using the convert_hms_cols_to_seconds() function after reading the file.
2) Create a "Input_file_dir" checkbox button named "Check to process all CSV file in a folder". Create the "Input_file_dir_checked" variable to pass the status.
3) Create a 10-row scrollable "columns_listbox" list box to display the data frame column header for data labeling. Label the "columns_listbox" list box with the "Data Fields". Enable multiple selection in the list box by clicking mouse pointers. 
Set the '' in the  "columns_listbox" list box before clicking the "Read" icon.
4) Draw a blue horizontal line between two list boxes.
4) Create a 5-row scrollable "align_listbox" list box to display the 'iVEH_SPEED', 'iENG_SPEED', 'icMASS_FLOW', and 'iBATT_CURR' alignment data.
Enable multiple selection in the list box by clicking mouse pointers. 
Label the "align_listbox" list box with the "Time Alignment".
5) Set the align_listbox width equal to the columns_listbox width.
6) Create an "Alignment" checkbox button and "Report" checkbox button horizontally to call back functions. Check the "Report" checkbox.
7) Create a text box with an "OBD File" label. Display the "Press a OBD button to select an OBD/HEMDATA file" when placing a mouse pointer on the ""OBD File"" text box.
Create an "OBD" button. Replace the "OBD" button with a Windows 11 color Truck icon to select a CSV file. Display the "Select OBD file" when placing a mouse pointer on the "OBD" icon. Only Enable the "OBD File" text box and "OBD" button when the "Alignment" checkbox is True.
8) Create the "Check Alignment" button. Create an input textbox next to the "Check Alignment" button. Display the “View Alignment Plot” and the "Type Alignment Values to OBD" when placing a mouse pointer on the "Check Alignment" button and the Alignment "input textbox" respectively.
Enable only the input textbox after when the "Alignment" checkbox is True and the “OBD File” text box is not empty.
Adjust the horizontal x coordinate of the "OBD" button at the btn_read.winfo_x().
Adjust the “OBD File” text box width little less than the horizontal x coordinate of the "OBD" button.
9) Set the "Check Alignment" button with a light magenta-color background to call back "check_alignment()" function with the selected items in the "align_listbox".
Add the self.ent_pems.get(), self.ent_obd.get(), self.align_values_var.get(), df arguments the plot_alignment function. Plot df[self.align_values_var.get()] in the self.ent_pems.get() and self.ent_obd.get().
Create the "plot_alignment()" function when clicking the "Check Alignment" button.
10) Create a font size 20, black bold font, "RUN" big button with a light blue-color background to call back the "run_analysis()" function.
11) Assign Alignment_checked and Report_checked variables to pass the "Alignment"  and "Report" Checkbox check status.
12) After clicking the "Read" icon, pre-select the ['eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'EXH_RATE', 'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'] in the columns_listbox.
13) Pre-select the 'iVEH_SPEED' in the "align_listbox" listbox.
14) Fix the _tkinter.TclError: expected integer but got "UI"
15) Enable to select multiple items in both the columns_listbox and align_listbox listbox
16) Print the obd_ent, pems_ent, "Alignment", "Report", "Input_file_dir"  checkbox status, "Check Alignment" button, align_values_ent textbox values, and the index of 'iVEH_SPEED' in df.columns when clicking the "RUN" button.
17) Fix automatically deselecting an item in a listbox while selecting an item in another listbox 

"""

import os
import math
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from PIL import Image, ImageTk, ImageDraw

# NEW: matplotlib imports for plotting inside Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global DataFrame variable to store data between functions
df = None
# dist_x = None

def convert_hms_cols_to_seconds(df, columns=None, inplace=True):
    """
    Convert columns with 'hh:mm:s.xxx' (or hh:mm:ss.xxx) time strings to seconds.
    If columns is None, auto-detect columns where a majority of values match the pattern.
    """
    pattern = r'^\s*\d{1,2}:\d{2}:\d{1,2}(?:\.\d+)?\s*$'

    def _convert(series):
        td = pd.to_timedelta(series.astype(str).str.strip(), errors='coerce')
        return td.dt.total_seconds()

    # Auto-detect columns if not provided
    if columns is None:
        columns = []
        for c in df.columns:
            s = df[c].astype(str)
            frac_match = s.str.match(pattern, na=False).mean()
            if frac_match > 0.5:  # heuristic: majority look like H:M:S(.xxx)
                columns.append(c)

    # Convert selected columns
    converted = {}
    for c in columns:
        converted[c] = _convert(df[c])
        if inplace:
            df[c] = converted[c]

    return df if inplace else converted

def ensure_eTIME(df_local):
    """Ensure df_local has a numeric 'eTIME' column in seconds, derived from 'sTIME' if needed."""
    if df_local is None or df_local.empty:
        return

    def convert_to_seconds(val):
        if pd.isna(val):
            return math.nan
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val).strip()
        # Normalize decimal separator
        s = s.replace(',', '.')
        # If it's a simple numeric string, return it
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

    if 'eTIME' in df_local.columns:
        # Coerce to numeric; if all NaN and 'sTIME' exists, try to derive from sTIME
        df_local['eTIME'] = pd.to_numeric(df_local['eTIME'], errors='coerce')
        if df_local['eTIME'].isna().all() and 'sTIME' in df_local.columns:
            df_local['eTIME'] = df_local['sTIME'].apply(convert_to_seconds)
            df_local['eTIME'] -= df_local.loc[0, 'eTIME']
    elif 'sTIME' in df_local.columns:
        df_local.insert(1, 'eTIME', None)
        df_local['eTIME'] = df_local['sTIME'].apply(convert_to_seconds)
        df_local['eTIME'] -= df_local.loc[0, 'eTIME']
        
    return df_local

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

class ImageDistanceMeasurer:
    def __init__(self, image_path):
        self.img = mpimg.imread(image_path)
        self.fig, self.ax = plt.subplots(figsize=(19.2, 10.8))
        self.ax.imshow(self.img)
        self.ax.set_title("Click twice to measure pixels (H & V)")
        
        self.points = []
        self.markers = []
        self.elements = []

        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        plt.show()

    def onclick(self, event):
        if event.inaxes != self.ax: return
        if len(self.points) == 2: self.clear_previous()

        self.points.append((event.xdata, event.ydata))
        marker, = self.ax.plot(event.xdata, event.ydata, 'ro', markersize=6)
        self.markers.append(marker)

        if len(self.points) == 2:
            (x1, y1), (x2, y2) = self.points
            dx, dy = (x2 - x1), (y2 - y1)
            # dx, dy = abs(x2 - x1), abs(y2 - y1)

            # Draw measurement lines
            h_line, = self.ax.plot([x1, x2], [y1, y1], 'b--', alpha=0.8)
            v_line, = self.ax.plot([x2, x2], [y1, y2], 'g--', alpha=0.8)
            
            # Label pixel distances
            h_text = self.ax.text((x1+x2)/2, y1, f' {dx:.1f}px', color='blue', va='bottom')
            v_text = self.ax.text(x2, (y1+y2)/2, f' {dy:.1f}px', color='green', ha='left')

            self.elements.extend([h_line, v_line, h_text, v_text])
            print(f"Pixels -> H: {dx:.2f} | V: {dy:.2f}")

        self.fig.canvas.draw()

    def clear_previous(self):
        self.points = []
        for m in self.markers + self.elements: m.remove()
        self.markers, self.elements = [], []

# if __name__ == "__main__":
#     # Provide your image path here
    # ImageDistanceMeasurer("your_image.png")
     
class PEMSAnalysisGUI(object):
    def __init__(self, root):
        self.root = root
        self.root.title("PEMS Data Analysis")
        self.root.geometry("600x735")
        self.root.configure(bg="#f3f3f3")  # Windows 11 Light Grey Background

        # --- Styles & Fonts ---
        # Fix for "expected integer but got UI" error: 
        # Ensure these are only passed to font= parameters.
        self.font_default = ("Segoe UI", 12)
        self.font_header = ("Segoe UI", 12, "bold")
        self.font_run = ("Segoe UI", 20, "bold")

        # --- Variables ---
        self.pems_file_path = tk.StringVar()
        self.obd_file_path = tk.StringVar()
        self.align_values_var = tk.StringVar()
        
        # Checkbox Variables
        self.input_file_dir_checked = tk.BooleanVar()
        self.alignment_checked = tk.BooleanVar()
        self.report_checked = tk.BooleanVar(value=True)  # Default True

        # Trace variables to handle enabling/disabling widgets dynamically
        self.obd_file_path.trace_add("write", self.check_alignment_input_state)
        self.alignment_checked.trace_add("write", self.toggle_obd_widgets)

        # NEW: Alignment label -> DataFrame column mapping
        # Adjust as needed to match your dataset
        self.align_map = {
            "Vehicle Speed": "iVEH_SPEED",
            "Engine RPM": "iENG_SPEED",
            "Exhaust Mass Flow Rate": "icMASS_FLOW",
            "Total Current": "TotalCurrent"  # If missing in DF, a notice will be shown
        }

        self.df_columns_selected = []  # To store selected columns from columns_listbox
        self.df_columns = []  # To store selected columns from columns_listbox

        # self.align_map.keys()
        # self.align_map.values()
        # self.align_map.get('Vehicle Speed')
        # self.align_map.get('Engine Speed')
        # self.align_map.get('Exhaust Mass Flowrate')
        # self.align_map.get('Battery Current')
        
        # --- Icon Generation (In-Memory) ---
        # We create these once to prevent garbage collection
        self.icon_folder = self.create_icon("Folder", "#ffe680", "#E8B931")
        self.icon_read = self.create_icon("Read", "#ffffff", "#0078d4", text_color="#0078d4")
        self.icon_truck = self.create_icon("Truck", "#73ec8e", "#107c10")
        self.icon_figure = self.create_icon("Figure", "#73ec8e", "#107c10")

        # =========================================================================
        # 1) PEMS File Section
        # =========================================================================
        frame_pems = tk.Frame(root, bg="#f3f3f3")
        frame_pems.pack(fill="x", padx=20, pady=(15, 5))

        # Label
        lbl_pems = tk.Label(frame_pems, text="PEMS File", font=self.font_default, bg="#f3f3f3")
        lbl_pems.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Textbox (Entry)
        self.ent_pems = tk.Entry(frame_pems, textvariable=self.pems_file_path, font=self.font_default)
        self.ent_pems.grid(row=0, column=1, sticky="ew")

        # Select Button (Folder Icon)
        self.btn_select = tk.Button(frame_pems, image=self.icon_folder, command=self.select_pems_file,
                                    bd=0, bg="#f3f3f3", activebackground="#e5e5e5", cursor="hand2")
        self.btn_select.grid(row=0, column=2, padx=5)
        self.create_tooltip(self.btn_select, "Select a file")

        # Read Button (Read File Icon)
        self.btn_read = tk.Button(frame_pems, image=self.icon_read, command=self.read_file,
                                  bd=0, bg="#f3f3f3", activebackground="#e5e5e5", cursor="hand2")
        self.btn_read.grid(row=0, column=3, padx=5)
        self.create_tooltip(self.btn_read, "Read File")

        # Configure Grid Weights: Column 1 (Entry) expands to tighten fit
        frame_pems.columnconfigure(1, weight=1)

        # =========================================================================
        # 2) Input Directory Checkbox
        # =========================================================================
        frame_dir = tk.Frame(root, bg="#f3f3f3")
        frame_dir.pack(fill="x", padx=20, pady=0)
        
        chk_input_dir = tk.Checkbutton(frame_dir, text="Check to process all CSV file in a folder", 
                                       variable=self.input_file_dir_checked, font=self.font_default,
                                       bg="#f3f3f3", activebackground="#f3f3f3", selectcolor="white")
        chk_input_dir.pack(anchor="w")

        # =========================================================================
        # 3) Data Fields Listbox
        # =========================================================================
        frame_cols = tk.Frame(root, bg="#f3f3f3")
        frame_cols.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_cols, text="Data Fields", font=self.font_header, bg="#f3f3f3").pack(anchor="w")

        sb_cols = tk.Scrollbar(frame_cols, orient="vertical")
        # Fix #17: exportselection=False prevents auto-deselect logic
        self.columns_listbox = tk.Listbox(frame_cols, height=10, font=self.font_default, 
                                          selectmode=tk.MULTIPLE, yscrollcommand=sb_cols.set,
                                          exportselection=False, borderwidth=1, relief="solid")
        sb_cols.config(command=self.columns_listbox.yview)
        
        sb_cols.pack(side="right", fill="y")
        self.columns_listbox.pack(side="left", fill="x", expand=True)

        # =========================================================================
        # 4) Blue Separator Line
        # =========================================================================
        tk.Frame(root, height=2, bg="#0078d4").pack(fill="x", padx=20, pady=10)

        # =========================================================================
        # 5) Time Alignment Listbox
        # =========================================================================
        frame_align_list = tk.Frame(root, bg="#f3f3f3")
        frame_align_list.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_align_list, text="Time Alignment", font=self.font_header, bg="#f3f3f3").pack(anchor="w")

        sb_align = tk.Scrollbar(frame_align_list, orient="vertical")
        self.align_listbox = tk.Listbox(frame_align_list, height=5, font=self.font_default,
                                        selectmode=tk.SINGLE, yscrollcommand=sb_align.set,
                                        exportselection=False, borderwidth=1, relief="solid")
                                        # selectmode=tk.MULTIPLE, yscrollcommand=sb_align.set,

        sb_align.config(command=self.align_listbox.yview)

        sb_align.pack(side="right", fill="y")
        self.align_listbox.pack(side="left", fill="x", expand=True)

        # Populate Alignment Options
        align_opts = ['Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', 'Total Current']
        # align_opts = ["Vehicle Speed", "Engine Speed", "Exhaust Mass Flowrate", "Battery Current"]
        for item in align_opts:
            self.align_listbox.insert(tk.END, item)

        # =========================================================================
        # 6) Alignment & Report Checkboxes
        # =========================================================================
        frame_checks = tk.Frame(root, bg="#f3f3f3")
        frame_checks.pack(fill="x", padx=20, pady=5)

        # chk_align = tk.Checkbutton(frame_checks, text="Alignment", variable=self.alignment_checked,
        #                            font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3")
        # chk_align.pack(side="left", padx=(0, 20))

        chk_align = tk.Checkbutton(frame_checks, text="Alignment", variable=self.alignment_checked, 
                                        font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3",
                                        command=self.update_widget_states)
        chk_align.pack(side="left", padx=(0, 20))

        chk_report = tk.Checkbutton(frame_checks, text="Report", variable=self.report_checked,
                                    font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3")
        # chk_report.pack(side="left")
        chk_align.pack(side="left", padx=(0, 20))

        # =========================================================================
        # 7) OBD File Section
        # =========================================================================
        frame_obd = tk.Frame(root, bg="#f3f3f3")
        frame_obd.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_obd, text="OBD File", font=self.font_default, bg="#f3f3f3").grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.ent_obd = tk.Entry(frame_obd, textvariable=self.obd_file_path, font=self.font_default, state="disabled")
        self.ent_obd.grid(row=0, column=1, sticky="ew")
        self.create_tooltip(self.ent_obd, "Press a OBD button to select an OBD/HEMDATA file")

        # OBD Button (Truck Icon)
        self.btn_obd = tk.Button(frame_obd, image=self.icon_truck, command=self.select_obd_file,
                                 bd=0, bg="#f3f3f3", activebackground="#e5e5e5", cursor="hand2", state="disabled")
        # Placing in column 3 to match the 'Read' button from the top frame structure
        self.btn_obd.grid(row=0, column=3, padx=5)
        self.create_tooltip(self.btn_obd, "Select OBD file")

        # Layout Weights: Matches PEMS frame to align the buttons vertically
        frame_obd.columnconfigure(1, weight=1)

        # =========================================================================
        # 8 & 9) Check Alignment Button & Input
        # =========================================================================
        frame = tk.Frame(root, bg="#f3f3f3")
        frame.pack(fill="x", padx=20, pady=10)

        # frame = tk.Frame(self.master, bg="#F3F3F3")
        # frame.pack(fill="x", padx=12, pady=(6, 6))

        # Check Alignment button
        self.btn_check_alignment = tk.Button(
            frame, text="Check Alignment", bg="#FFCCFF", activebackground="#F2A6F2",
            command=self.check_alignment
        )
        
        
        # self.btn_check_alignment = tk.Button(
        #     frame, text="Check Alignment", bg="#FFCCFF", activebackground="#F2A6F2",
        #     command=self.on_check_alignment_clicked
        # )
        self.btn_check_alignment.grid(row=0, column=0, sticky="w")
        self.create_tooltip(self.btn_check_alignment, "Estimate Alignment")

        # Alignment input textbox (disabled until Alignment checked AND OBD file set)
        self.align_values_ent = tk.Entry(frame, textvariable=self.align_values_var, state="disabled", font=self.font_default)
        self.align_values_ent.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        frame.grid_columnconfigure(1, weight=1)
        self.create_tooltip(self.align_values_ent, "Type Alignment Values to OBD")

        # Plot icon button next to entry
        self.btn_plot = tk.Button(frame, image=self.icon_figure, relief="flat",
                                  bg="#F3F3F3", activebackground="#EDEDED",
                                  command=self.plot_alignment_with_offset, state="disabled")
        self.btn_plot.grid(row=0, column=2, sticky="e")
        self.create_tooltip(self.btn_plot, "Plot Alignments")

        # Position the Plot icon at same x as Read icon
        # self.master.after(100, self.place_plot_button_like_read)
        # # Check Alignment Button (Light Magenta)
        # self.btn_check_align = tk.Button(frame_check_align, text="Check Alignment", command=self.check_alignment,
        #                                  font=self.font_default, bg="#ff80ff", width=16)
        # self.btn_check_align.pack(side="left", padx=(0, 10))
        # # UPDATED tooltip text to match spec
        # self.create_tooltip(self.btn_check_align, "View/Plot Alignment")

        # # Alignment Input Textbox
        # self.ent_align_input = tk.Entry(frame_check_align, textvariable=self.align_values_var, 
        #                                 font=self.font_default, state="disabled")
        # self.ent_align_input.pack(side="left", fill="x", expand=True)
        # self.create_tooltip(self.ent_align_input, "Type Alignment Values to OBD")

        # self.icon_plot = self.load_icon("plot")
        # self.btn_plot = tk.Button(frame_act, image=self.icon_plot, command=self.plot_alignment, 
        #                           borderwidth=0, bg="#f3f3f3", state='disabled')
        # self.btn_plot.grid(row=0, column=2)
        # self.create_tooltip(self.btn_plot, "Plot Alignments")
        # frame_act.columnconfigure(1, weight=1)
        
        # =========================================================================
        # 10) RUN Button
        # =========================================================================
        # Light Blue Background
        self.btn_run = tk.Button(root, text="RUN", command=self.run_analysis,
                                 font=self.font_run, bg="#add8e6", height=1)
        self.btn_run.pack(fill="x", padx=20, pady=(10, 20))


    # =========================================================================
    # Helpers & Logic
    # =========================================================================
    def toggle_plot_btn(self, *args):
        txt = self.align_values_var.get().strip()
        self.btn_plot.config(state="normal" if txt else "disabled")

    # def make_icon(self, size=(32, 32), fill="#0078D4", glyph=None):
    #     img = Image.new("RGBA", size, fill)
    #     if glyph:
    #         draw = ImageDraw.Draw(img)
    #         w, h = size
    #         draw.text((w//2, h//2), glyph, anchor="mm", fill="#ffffff")
    #     return ImageTk.PhotoImage(img)
            
    def create_icon(self, icon_type, fill_color, border_color, text_color="black"):
        """Generates a simple 40x30 icon in-memory using Pillow."""
        w, h = 40, 30
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Base rounded rect look (simple rectangle for Tkinter)
        draw.rectangle((0, 0, w-1, h-1), fill=fill_color, outline=border_color, width=2)
        
        if icon_type == "Folder":
            # Draw folder tab
            draw.rectangle((5, 8, w-5, h-8), outline="#555", width=1)
            draw.line((5, 8, 15, 8), fill="#555", width=1)
        elif icon_type == "Read":
            # Draw lines representing text
            for y in [8, 14, 20]:
                draw.line((8, y, w-8, y), fill=text_color, width=2)
        elif icon_type == "Truck":
            # Simple truck profile
            draw.rectangle((5, 10, 25, 22), fill="#333") # Cargo
            draw.rectangle((25, 14, 34, 22), fill="#333") # Cab
            draw.ellipse((8, 20, 14, 26), fill="black") # Wheel 1
            draw.ellipse((24, 20, 30, 26), fill="black") # Wheel 2
        elif icon_type == "Figure":
            # Plot/Figure with a stylized vehicle speed trace:
            # Background frame
            col = (154, 92, 230)  # Win11 purple
            draw.rounded_rectangle([w*0.08, h*0.12, w*0.92, h*0.88], radius=6, fill=col)
            # Axes
            draw.line([(w*0.18, h*0.78), (w*0.85, h*0.78)], fill=(255, 255, 255), width=2)
            draw.line([(w*0.18, h*0.25), (w*0.18, h*0.78)], fill=(255, 255, 255), width=2)
            # Stylized "vehicle speed trace" polyline inside the frame
            pts = [(w*0.18, h*0.70), (w*0.30, h*0.55), (w*0.38, h*0.60),
                   (w*0.50, h*0.40), (w*0.62, h*0.48), (w*0.74, h*0.35), (w*0.85, h*0.42)]
            draw.line(pts, fill=(255, 255, 255), width=3)
            

        return ImageTk.PhotoImage(img)

    def create_tooltip(self, widget, text):
        def enter(event):
            self.tooltip = tk.Label(self.root, text=text, bg="#ffffe0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
            # Position tooltip slightly below widget
            x = widget.winfo_rootx() - self.root.winfo_rootx() + 10
            y = widget.winfo_rooty() - self.root.winfo_rooty() + 35
            self.tooltip.place(x=x, y=y)
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # --- Callbacks ---

    def select_pems_file(self):
        file = filedialog.askopenfilename(title="Select PEMS File", filetypes=[("CSV", "*.csv")])
        if file:
            self.pems_file_path.set(file)

    def select_obd_file(self):
        file = filedialog.askopenfilename(title="Select OBD File", filetypes=[("CSV", "*.csv")])
        if file:
            self.obd_file_path.set(file)

    def toggle_obd_widgets(self, *args):
        """Enable/Disable OBD widgets based on Alignment Checkbox."""
        is_checked = self.alignment_checked.get()
        state = "normal" if is_checked else "disabled"
        
        self.ent_obd.config(state=state)
        self.btn_obd.config(state=state)
        self.align_values_ent.config(state=state if self.obd_file_path.get().strip() else "disabled")
        # Also re-check the input box state
        self.check_alignment_input_state()

    def on_check_alignment_clicked(self):
        """Callback when Check Alignment button is clicked"""
        selected_indices = self.align_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select an alignment field.")
            return
        
        selected_value = self.align_listbox.get(selected_indices[0])
        align_col = self.align_map.get(selected_value)
        
        self.plot_alignment(
            self.ent_pems.get(),
            self.ent_obd.get(),
            align_col,
            df
        )
        
    def update_widget_states(self, *args):
        """Logic to enable/disable widgets based on Checkbox and Entry content."""
        is_alignment_on = self.alignment_checked.get()
        is_obd_not_empty = len(self.obd_file_path.get().strip()) > 0

        print(f"Alignment Checked: {is_alignment_on}, OBD File Path: '{self.obd_file_path.get()}'")
        print(f"Enabling OBD widgets: {is_alignment_on}, Enabling Alignment Input: {is_alignment_on and is_obd_not_empty}")
        # Step 1: Handle OBD Widgets (only depend on Checkbox)
        obd_state = 'normal' if is_alignment_on else 'disabled'
        self.ent_obd.config(state=obd_state)
        self.btn_obd.config(state=obd_state)

        # Step 2: Handle Alignment Input (depends on Checkbox AND OBD Content)
        if is_alignment_on: # and is_obd_not_empty:
            self.align_values_ent.config(state='normal')
        else:
            self.align_values_ent.config(state='disabled')

    def check_alignment_input_state(self, *args):
        """Enable Input Box only if Alignment Checked AND OBD File not empty."""
        if self.alignment_checked.get() and self.obd_file_path.get().strip():
            self.align_values_ent.config(state="normal")
        else:
            self.align_values_ent.config(state="disabled")

    def read_file(self):
        global df
        path = self.pems_file_path.get()
        if not path:
            messagebox.showwarning("Warning", "Please select a PEMS file first.")
            return

        try:
            # 1) Read Logic:
            temp_df = pd.read_csv(path, escapechar='\\', encoding = 'unicode_escape', low_memory=False, skiprows=0, header=0) # , on_bad_lines='skip')
            # escapechar='\\', encoding = 'unicode_escape',
            # Logic: 
            # Row 0 -> variable names (vars)
            # Row 1 -> units
            # Row 2+ -> data
            
            # Ensure file has enough rows
            if len(temp_df) < 2:
                raise ValueError("File too short to contain Vars, Units, and Data.")
            if 'eTIME' not in temp_df.columns:
                temp_df.insert(1, 'eTIME', None)
                temp_df.loc[0, 'eTIME'] = 'eTIME'
                temp_df.loc[1, 'eTIME'] = 's'
            # Remove columns with "Not Available" or "Unnamed" in the column name
            temp_df = temp_df.loc[:, ~temp_df.columns.str.contains("Not Available|Unnamed", case=False, na=False)]
            self.df_columns = columns_row = temp_df.columns  # Original columns before assignment
            vars_row = temp_df.loc[0, :]
            units_row = temp_df.loc[1, :] # Captured but unused in prompt logic, just required assignment
            
            # Update columns
            temp_df.columns = vars_row
            
            summary = "Summary Information:"
            # Find the row containing the summary string in the first column
            summary_row_idx = None
            first_col = temp_df.columns[0]
            # 2. Use get_loc on a temporary index of that column's values
            summary_row_idx = pd.Index(temp_df[first_col]).get_loc("Summary Information:")
            # print(f"The integer location is: {summary_row_idx}")

            if summary_row_idx is not None:
                df = temp_df.loc[2:summary_row_idx-1, :].copy()
                df_summary = temp_df.loc[summary_row_idx:, :].copy()
                df_summary.reset_index(drop=True, inplace=True)
                df_summary.to_csv("df_summary.csv", index=False, header=False)
            else:
                df = temp_df.loc[2:, :].copy()
                df_summary = pd.DataFrame()  # Empty summary if not found
            # Drop rows where all values are NaN
            df = df.dropna(how='all')
            df = df.loc[df['sSTATUS_PATH'] == 'SAMPLE', :].copy()
            df.reset_index(drop=True, inplace=True)
            
            df = ensure_eTIME(df)

            # 3) Populate Listbox
            self.columns_listbox.delete(0, tk.END) # Clear existing
            for col in columns_row: # df.columns:
                self.columns_listbox.insert(tk.END, str(col))

            # 12) Pre-select specific items in columns_listbox
            pre_select_vars = [
                'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 
                'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'icMASS_FLOWx', 'EXH_RATE', 
                'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 
                'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 
                'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 
                'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'
            ]

            pre_select_columns = ['eTIME', 'Gas Path', 'Catalyst Temperature', 'Limit Adjusted iSCB_RH', 'Ambient Pressure', 'Limit Adjusted iSCB_LAT', 'Load Percent', 
                                  'Limit Adjusted iCOOL_TEMP', 'Engine RPM', 'Vehicle Speed', 'Mass Air Flow Rate', 'Catalyst Temp. 1-1', 'F/A Equiv. Ratio', 'Engine Fuel Rate', 
                                  'Eng. Exh. Flow Rate', 'GPS Latitude', 'GPS Longitude', 'Limit Adjusted iGPS_ALT', 'Limit Adjusted iGPS_GROUND_SPEED', 'Fuel Rate', 'Instantaneous Fuel Flow', 
                                  'Derived Engine Torque.1', 'Derived Engine Power.1', 'Instantaneous Mass CO2', 'Instantaneous Mass CO', 'Instantaneous Mass NO', 'Instantaneous Mass NO2', 
                                  'Instantaneous Mass NOx', 'Corrected Instantaneous Mass NOx', 'Instantaneous Mass HC', 'Instantaneous Mass CH4', 'Instantaneous Mass NMHC', 'Instantaneous Mass O2', 
                                  'Air/Fuel Ratio at stoichiometry', 'Air/Fuel Ratio of Sample', 'Lambda', 'Ambient Temperature', 'AMB Ambient Temperature', 'Brake Specific Fuel Consumption', 
                                  'Mass Air Flow Rate.1']
            # Loop through listbox items to find indices
            listbox_items = self.columns_listbox.get(0, tk.END)
            idx_vars = []
            for idx, item in enumerate(listbox_items):
                if item in pre_select_columns:
                    idx_vars.append((idx))
                    self.columns_listbox.selection_set(idx)
                    # self.columns_listbox.see(idx)

            self.df_columns_selected = columns_row[idx_vars].tolist()
            columns_vars_mapping = dict(zip(columns_row, vars_row))
            # print(columns_vars_mapping)
            print(columns_row[idx_vars].tolist())
            print(columns_vars_mapping.get('TIME'))
            # Remove items that are not in the pre-select list
            # for idx in range(self.columns_listbox.size() - 1, -1, -1):
            #     item = self.columns_listbox.get(idx)
            #     idx_item = columns_row.get_loc(item) if item in columns_row else None
            #     item_var = vars_row.iloc[idx_item] if idx_item is not None else None
            #     # if item not in pre_select_items:
            #     if item_var not in pre_select_items:
            #         self.columns_listbox.delete(idx)
            # 13) Pre-select items in align_listbox
            # "Vehicle Speed" is index 0, "Engine Speed" is index 1 based on initialization
            self.align_listbox.selection_set(0)
            # self.align_listbox.selection_set(1)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")

    def check_alignment(self):
        """Callback for Check Alignment Button"""
        # Keep printing the selected items from align_listbox as before (spec #9)
        selected_indices = self.align_listbox.curselection()
        selected_values = [self.align_listbox.get(i) for i in selected_indices]
        print(f"Executing check_alignment() with: {selected_values}")

        # NEW: Call plot_alignment with requested arguments
        self.plot_alignment(
            self.ent_pems.get(),
            self.ent_obd.get(),
            self.align_map.get(selected_values[0]) if selected_values else None,  # Pass the first selected alignment value or None
            df
        )

    # 8) Plot button callback to call plotAlignmentWithOffset
    def plot_alignment_with_offset(self):
        # This can apply any offset/overlay logic; here we reuse plot_alignment using current align_values_var.
        self.plot_alignment(self.ent_pems.get(), self.ent_obd.get(), self.align_map.get(selected_values[0]) if selected_values else None, df)

    def plot_alignment(self, pems_path, obd_path, align_col, pems_df):
        if pems_df is None or pems_df.empty:
            messagebox.showwarning("Warning", "Please read a PEMS file before plotting alignment.")
            return

        align_col = (align_col or "").strip()
        if not align_col:
            messagebox.showinfo("Info", "Please type a column name in the Alignment input box.")
            return

        data_to_plot = []
        missing_sources = []

        def get_time_axis(df_local):
            if 'eTIME' in df_local.columns:
                return pd.to_numeric(df_local['eTIME'], errors='coerce')
            else:
                return pd.RangeIndex(start=0, stop=len(df_local))

        # PEMS series
        if align_col in pems_df.columns:
            x_pems = get_time_axis(pems_df)
            y_pems = pd.to_numeric(pems_df[align_col], errors='coerce')
            import os
            pems_label = f"PEMS: {os.path.basename(pems_path) if pems_path else 'current'}"
            data_to_plot.append((x_pems, y_pems, pems_label.split(':')[0]))
        else:
            missing_sources.append(f"'{align_col}' not found in PEMS data.")

        # OBD series (read if path provided)
        obd_df = None
        if obd_path and obd_path.strip():
            try:
                tmp = pd.read_csv(obd_path, encoding='utf-8', low_memory=False, skiprows=0, header=0)
                if len(tmp) >= 2:
                    tmp.columns = tmp.loc[0, :]
                    summary_row_idx = None
                    summary_row_idx = pd.Index(tmp[tmp.columns[0]]).get_loc("Summary Information:")
                    if summary_row_idx is not None and summary_row_idx > 2:
                        obd_df = tmp.loc[2:summary_row_idx, :].copy()
                        obd_df = obd_df.dropna(how='all')
                        obd_df = obd_df.loc[obd_df['sSTATUS_PATH'] == 'SAMPLE', :].copy()
                    else:
                        obd_df = tmp.loc[2:, :].copy()
                    obd_df.reset_index(drop=True, inplace=True)
                    # NEW: ensure eTIME exists for OBD
                    ensure_eTIME(obd_df)
                else:
                    missing_sources.append("OBD file too short to parse.")
            except Exception as e:
                missing_sources.append(f"Failed to read OBD file: {e}")

        if obd_df is not None and not obd_df.empty:
            if align_col in obd_df.columns:
                x_obd = get_time_axis(obd_df)
                y_obd = pd.to_numeric(obd_df[align_col], errors='coerce')
                import os
                obd_label = f"OBD: {os.path.basename(obd_path)}"
                data_to_plot.append((x_obd, y_obd, obd_label.split(':')[0]))
            else:
                missing_sources.append(f"'{align_col}' not found in OBD data.")

        if not data_to_plot:
            msg = "No data found to plot."
            if missing_sources:
                msg += "\n\nDetails:\n- " + "\n- ".join(missing_sources)
            messagebox.showwarning("Plot Alignment", msg)
            return

        if hasattr(self, 'plot_top') and self.plot_top and self.plot_top.winfo_exists():
            self.plot_top.destroy()

        # fig = Figure(figsize=(8, 6), dpi=100)
        fig = Figure(figsize=(19.2, 10.8), dpi=100)
        ax = fig.add_subplot(111)

        idx = 0
        for x_vals, y_vals, label in (data_to_plot):
            print(f"Plotting series {idx}: {label} with {len(x_vals)} points.")
            ax.plot(x_vals, y_vals, label=label, linewidth=1) if idx == 0 else ax.plot(x_vals, y_vals, '--', label=label, linewidth=1)
            idx += 1

        # X-axis labeling
        ax.set_xlabel("Time (s)" if 'eTIME' in pems_df.columns else "Index")
        ax.set_ylabel(align_col)
        # ax.set_title(f"Alignment: {align_col}")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper left")
        # ax.set_xticks([])

        figname = 'time_alignment.png'
        fig.savefig(figname, dpi=300, bbox_inches='tight')
        ImageDistanceMeasurer(figname)

        if (len(self.align_values_var.get()) > 0): 
            dist_x_align = float(self.align_values_var.get()) # Example fixed distance for alignment visualization
            plt.close('all')
        
        self.plot_top = tk.Toplevel(self.root)
        self.plot_top.title(f"Alignment Plot - {align_col}")
        self.plot_top.geometry("1280x720")
        
        fig = Figure(figsize=(10, 7), dpi=100)
        ax = fig.add_subplot(211)

        idx = 0
        for x_vals, y_vals, label in (data_to_plot):
            print(f"Plotting series {idx}: {label} with {len(x_vals)} points.")
            ax.plot(x_vals, y_vals, label=label, linewidth=1) if idx == 0 else ax.plot(x_vals, y_vals, '--', label=label, linewidth=1)
            idx += 1

        # X-axis labeling
        # ax.set_xlabel("Time (s)" if 'eTIME' in pems_df.columns else "Index")
        ax.set_ylabel(align_col)
        ax.set_title(f"Alignment: {align_col}")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="upper left")
        ax.set_xticks([])        
        
        ax = fig.add_subplot(212)

        idx = 0
        for x_vals, y_vals, label in data_to_plot:
            ax.plot(x_vals + dist_x_align, y_vals, label=label, linewidth=1) if idx == 0 else ax.plot(x_vals, y_vals, '--', label=label, linewidth=1)
            idx += 1

        # X-axis labeling
        ax.set_xlabel("Time (s)" if 'eTIME' in pems_df.columns else "Index")
        ax.set_ylabel(align_col)
        # ax.set_title(f"Alignment: {align_col}")
        ax.grid(True, linestyle="--", alpha=0.4)
        # ax.legend(loc="upper left")

        fig.tight_layout(pad=2.0) # Prevents overlap
        # plt.show()

        if missing_sources:
            messagebox.showinfo("Missing/Info", "Notes:\n- " + "\n- ".join(missing_sources))
        
        # Save at high resolution (300 DPI) for publication
        # figname = 'time_alignment.png'
        # fig.savefig(figname, dpi=300, bbox_inches='tight')
        # dist_x = ImageDistanceMeasurer(figname)
        # print(dist_x)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def run_analysis(self):
        """Callback for RUN Button"""
        # 16) Print Requirements
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
        
        # Print index of 'iVEH_SPEED'
        if df is not None and 'iVEH_SPEED' in df.columns:
            try:
                idx = df.columns.get_loc('iVEH_SPEED')
                print(f"Index of 'iVEH_SPEED' in df: {idx}")
            except Exception as e:
                print(f"Error finding iVEH_SPEED: {e}")
        else:
            print("'iVEH_SPEED' not found or Dataframe not loaded.")

        selected_cols = [self.columns_listbox.get(i) for i in self.columns_listbox.curselection()]
        selected_align = [self.align_listbox.get(i) for i in self.align_listbox.curselection()]
        summary = (
            f"PEMS file: {self.ent_pems.get()}\n"
            f"OBD file: {self.ent_obd.get() if self.alignment_checked.get() else '(disabled)'}\n"
            f"Selected columns: {selected_cols}\n"
            f"Alignment selections: {selected_align}\n"
            f"Alignment_checked: {self.alignment_checked.get()}\n"
            f"Report_checked: {self.report_checked.get()}\n"
            f"Input_file_dir_checked: {self.input_file_dir_checked.get()}"
            f"Align Values Textbox Content: '{self.align_values_var.get()}'"
        )
        messagebox.showinfo("RUN", "Analysis started.\n\n" + summary)

if __name__ == "__main__":
    root = tk.Tk()
    app = PEMSAnalysisGUI(root)
    root.mainloop()