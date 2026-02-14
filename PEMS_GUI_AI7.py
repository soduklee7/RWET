import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk, ImageDraw
import os

# --- Requested Import ---
# Note: Since I am an AI, I cannot access your local file 'PEMS_GUI_AI5.py'.
# I have included mock classes/functions below so this code runs standalone for testing.
# In your actual environment, ensure 'PEMS_GUI_AI5.py' is in the same directory.
try:
    from PEMS_GUI_AI5 import ensure_eTIME, get_time_axis, ZoomManager, ImageDistanceMeasurer, read_m_file_to_df, read_mlx_content
except ImportError:
    # Mocks for demonstration if file is missing
    def ensure_eTIME(df):
        if 'eTIME' in df.columns: return df
        df['eTIME'] = np.arange(len(df))
        return df
    def get_time_axis(df): return df['eTIME']
    class ZoomManager:
        def __init__(self, ax, base_scale=1.1): pass
    class ImageDistanceMeasurer:
        def __init__(self, ax): pass
    def read_m_file_to_df(path): return pd.DataFrame([["M File Content"]], columns=["Data"])
    def read_mlx_content(path): return pd.DataFrame([["MLX File Content"]], columns=["Data"])

# --- ToolTip Utility ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# --- Main GUI Class ---
class PEMSAnalysisGUI(object):
    def __init__(self, root):
        self.root = root
        self.root.title("PEMS Analysis GUI")
        self.root.geometry("600x700")
        
        # Default Font
        self.default_font = ("Arial", 14)
        self.root.option_add("*Font", self.default_font)

        # 1) Create Icons
        # self.create_icons()
        self.icon_folder = self.create_icon("Folder", "#ffe680", "#E8B931")
        self.icon_read = self.create_icon("Read", "#ffffff", "#0078d4", text_color="#0078d4")
        self.icon_truck = self.create_icon("Truck", "#73ec8e", "#107c10")
        self.icon_figure = self.create_icon("Figure", "#73ec8e", "#107c10")
        self.icon_import = self.load_icon_from_file("icons/import.png", size=(40, 30))
        self.icon_PEMSreport = self.load_icon_from_file("icons/PEMSreport.png", size=(40, 30))
        self.icon_Folder24 = self.load_icon_from_file("icons/Folder_24.png", size=(40, 30))
        self.icon_format = self.load_icon_from_file("icons/import.png", size=(40, 30))
        # Variables
        self.input_file_dir_checked = tk.BooleanVar()
        self.alignment_checked = tk.BooleanVar()
        self.report_checked = tk.BooleanVar(value=True) # Default Checked
        self.pre_select_checked = tk.BooleanVar()
        self.df = pd.DataFrame()
        self.obd_df = pd.DataFrame()
        self.df_summary = pd.DataFrame()
        self.obd_df_summary = pd.DataFrame()
        self.df_options = pd.DataFrame()
        self.selected_columns_list = []

        # Tabs Setup
        self.tab_control = ttk.Notebook(root)
        self.tab_main = ttk.Frame(self.tab_control)
        self.tab_options = ttk.Frame(self.tab_control)
        
        # Style for Options tab
        style = ttk.Style()
        style.configure("Blue.TLabel", foreground="blue", font=("Arial", 12, "bold"))
        
        self.tab_control.add(self.tab_main, text='Main')
        self.tab_control.add(self.tab_options, text='Options/Report')
        self.tab_control.pack(expand=1, fill="both")

        # --- Build Tabs ---
        self.setup_main_tab()
        self.setup_options_tab()

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

    # def create_icons(self):
    #     """Creates 40x40 icons using Pillow without loading external files."""
    #     def make_base(color):
    #         img = Image.new('RGB', (40, 40), color='white')
    #         return img, ImageDraw.Draw(img)

    #     # Folder Icon
    #     img, draw = make_base('white')
    #     draw.rectangle([5, 10, 35, 30], fill='#FFCC00', outline='black')
    #     draw.polygon([(5, 10), (15, 10), (18, 5), (28, 5), (35, 10)], fill='#FFCC00', outline='black')
    #     self.icon_folder = ImageTk.PhotoImage(img)

    #     # Truck Icon
    #     img, draw = make_base('white')
    #     draw.rectangle([5, 15, 25, 30], fill='blue', outline='black') # Cab
    #     draw.rectangle([25, 5, 38, 30], fill='grey', outline='black') # Trailer
    #     draw.ellipse([8, 28, 15, 35], fill='black') # Wheel
    #     draw.ellipse([28, 28, 35, 35], fill='black') # Wheel
    #     self.icon_truck = ImageTk.PhotoImage(img)

    #     # Plot Icon
    #     img, draw = make_base('white')
    #     draw.line([5, 35, 35, 35], fill='black', width=2) # X axis
    #     draw.line([5, 5, 5, 35], fill='black', width=2)   # Y axis
    #     draw.line([5, 30, 15, 10, 25, 25, 35, 5], fill='red', width=2)
    #     self.icon_figure = ImageTk.PhotoImage(img)
    #     self.btn_plot_icon = self.icon_figure # Alias

    #     # Import Icon (Arrow)
    #     img, draw = make_base('white')
    #     draw.rectangle([10, 15, 30, 35], outline='black', width=2)
    #     draw.line([20, 5, 20, 25], fill='green', width=3)
    #     draw.polygon([(15, 20), (25, 20), (20, 25)], fill='green')
    #     self.icon_import = ImageTk.PhotoImage(img)

    #     # Format Icon (Doc/Sheet)
    #     img, draw = make_base('white')
    #     draw.rectangle([8, 5, 32, 35], outline='blue', width=2)
    #     draw.line([12, 10, 28, 10], fill='blue', width=1)
    #     draw.line([12, 15, 28, 15], fill='blue', width=1)
    #     draw.line([12, 20, 28, 20], fill='blue', width=1)
    #     self.icon_format = ImageTk.PhotoImage(img)

    def load_icon_from_file(self, path, size=(40, 30)):
        """Load an external icon and resize to match button size."""
        try:
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Could not load icon '{path}': {e}")
            return None

    def setup_main_tab(self):
        # 1 & 2) PEMS File Selection
        frame_pems = tk.Frame(self.tab_main)
        frame_pems.pack(fill="x", padx=10, pady=5)
        
        lbl_pems = tk.Label(frame_pems, text="PEMS File")
        lbl_pems.pack(side="left")
        
        self.ent_pems_file = tk.Entry(frame_pems)
        self.ent_pems_file.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ToolTip(self.ent_pems_file, "Press a PEMS button to select a PEMS file")

        self.btn_select = tk.Button(frame_pems, image=self.icon_folder, command=self.read_file)
        self.btn_select.pack(side="left", padx=(0, 5))
        ToolTip(self.btn_select, "Select a file")

        # 12) Process Folder Checkbox & Pre-select Columns Checkbox
        frame_checks = tk.Frame(self.tab_main)
        frame_checks.pack(fill="x", padx=10, pady=2)
        
        self.chk_input_file_dir = tk.Checkbutton(frame_checks, text="Process all CSV files in a Folder", 
                                                 variable=self.input_file_dir_checked)
        self.chk_input_file_dir.pack(side="left")

        self.chk_pre_select = tk.Checkbutton(frame_checks, text="Display Selected Data Fields only", 
                                             variable=self.pre_select_checked, command=self.refresh_columns_listbox)
        self.chk_pre_select.pack(side="left", padx=20)

        # 14, 15, 16) Data Fields Listbox
        lbl_data_fields = tk.Label(self.tab_main, text="Data Fields")
        lbl_data_fields.pack(anchor="w", padx=10)

        frame_listbox = tk.Frame(self.tab_main)
        frame_listbox.pack(fill="x", padx=10, pady=5)
        
        self.scrollbar_cols = tk.Scrollbar(frame_listbox, orient="vertical")
        self.columns_listbox = tk.Listbox(frame_listbox, height=8, selectmode="multiple", 
                                          yscrollcommand=self.scrollbar_cols.set, exportselection=False)
        self.scrollbar_cols.config(command=self.columns_listbox.yview)
        self.columns_listbox.pack(side="left", fill="x", expand=True)
        self.scrollbar_cols.pack(side="right", fill="y")
        self.columns_listbox.bind("<<ListboxSelect>>", self.on_column_select)

        # 17) Time Alignment and Data Format Listboxes
        frame_lists_container = tk.Frame(self.tab_main)
        frame_lists_container.pack(fill="x", padx=10, pady=5)

        # Time Alignment
        frame_align_list = tk.Frame(frame_lists_container)
        frame_align_list.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(frame_align_list, text="Time Alignment").pack(anchor="w")
        self.align_listbox = tk.Listbox(frame_align_list, height=5, selectmode="single", exportselection=False)
        self.align_listbox.pack(fill="x", expand=True)
        
        align_items = ['Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', 'iBAT_CURR', 'Total Current']
        for item in align_items: self.align_listbox.insert(tk.END, item)
        # Pre-select Vehicle Speed
        idx = align_items.index('Vehicle Speed')
        self.align_listbox.selection_set(idx)
        self.align_listbox.activate(idx)

        # Data Format
        frame_format_list = tk.Frame(frame_lists_container)
        frame_format_list.pack(side="left", fill="both", expand=True, padx=(5, 0))
        tk.Label(frame_format_list, text="Data Format").pack(anchor="w")
        self.format_listbox = tk.Listbox(frame_format_list, height=5, selectmode="single", exportselection=False)
        self.format_listbox.pack(fill="x", expand=True)

        format_items = ['EPA PEMS', 'EPA Dyno', 'EPA SD', 'EPA BEV', 'FEV PEMS', 'Custom']
        for item in format_items: self.format_listbox.insert(tk.END, item)
        # Pre-select EPA PEMS
        idx = format_items.index('EPA PEMS')
        self.format_listbox.selection_set(idx)

        # 20) Alignment and Report Checkboxes
        frame_ar_checks = tk.Frame(self.tab_main)
        frame_ar_checks.pack(fill="x", padx=10, pady=5)

        self.chk_alignment = tk.Checkbutton(frame_ar_checks, text="Alignment", 
                                            variable=self.alignment_checked, command=self.toggle_obd_section)
        self.chk_alignment.pack(side="left")
        
        self.chk_report = tk.Checkbutton(frame_ar_checks, text="Report", variable=self.report_checked)
        self.chk_report.pack(side="left", padx=20)

        # 21, 22) OBD File Section
        frame_obd = tk.Frame(self.tab_main)
        frame_obd.pack(fill="x", padx=10, pady=5)

        lbl_obd = tk.Label(frame_obd, text="OBD File")
        lbl_obd.pack(side="left")
        
        self.ent_obd_file = tk.Entry(frame_obd, state='disabled')
        self.ent_obd_file.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ToolTip(self.ent_obd_file, "Press a OBD button to select an OBD/HEMDATA file")

        self.btn_obd = tk.Button(frame_obd, image=self.icon_truck, command=self.select_obd_file, state='disabled')
        self.btn_obd.pack(side="left", padx=(0, 5))
        ToolTip(self.btn_obd, "Select OBD file")

        # 32) Check Alignment Frame
        self.frame_check_align = tk.Frame(self.tab_main)
        self.frame_check_align.pack(fill="x", padx=10, pady=10)

        self.btn_check_align = tk.Button(self.frame_check_align, text="Check Alignment", bg="#ffccff", 
                                         command=self.plot_check_alignment) # Light magenta
        self.btn_check_align.pack(side="left")
        ToolTip(self.btn_check_align, "Check/Plot Alignment")

        self.ent_align_input = tk.Entry(self.frame_check_align, width=10, state='disabled')
        self.ent_align_input.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ToolTip(self.ent_align_input, "Type Alignment Values to OBD")

        self.btn_plot = tk.Button(self.frame_check_align, image=self.icon_figure, state='disabled',
                                  command=self.check_alignment_view)
        self.btn_plot.pack(side="left", padx=(0,5))
        ToolTip(self.btn_plot, "Plot Alignments")

        # 44) RUN Button
        self.btn_run = tk.Button(self.tab_main, text="RUN", font=("Arial", 30, "bold"), bg="lightblue",
                                 command=self.run_analysis)
        self.btn_run.pack(pady=20, fill="x", padx=40)


    def setup_options_tab(self):
        # 52) Options/Controls
        frame_opt_top = tk.Frame(self.tab_options)
        frame_opt_top.pack(fill="x", padx=10, pady=10)

        lbl_opt = tk.Label(frame_opt_top, text="Options/Controls:", font=("Arial", 12))
        lbl_opt.pack(side="left")

        self.ent_options_dir = tk.Entry(frame_opt_top)
        self.ent_options_dir.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_import = tk.Button(frame_opt_top, text="Import", image=self.icon_import, compound="left",
                                    command=self.import_options_folder)
        self.btn_import.pack(side="left")

        # 53) Options Listbox
        lbl_opt_list = tk.Label(self.tab_options, text="Options Lists")
        lbl_opt_list.pack(anchor="w", padx=10)

        self.options_listbox = tk.Listbox(self.tab_options, height=8, selectmode="single", exportselection=False)
        self.options_listbox.pack(fill="x", padx=10, pady=(0, 10))
        self.options_listbox.bind("<Double-Button-1>", self.on_option_double_click)

        # 56) Separator
        sep = tk.Frame(self.tab_options, height=2, bd=1, relief="sunken", bg="blue")
        sep.pack(fill="x", padx=10, pady=10)

        # 57) Report Format Section
        frame_rep_fmt = tk.Frame(self.tab_options)
        frame_rep_fmt.pack(fill="x", padx=10, pady=5)

        # 60) Blue Bold Label
        lbl_rep_fmt = tk.Label(frame_rep_fmt, text="Report Format:", font=("Arial", 12, "bold"), fg="blue")
        lbl_rep_fmt.pack(side="left")

        self.ent_report_format = tk.Entry(frame_rep_fmt)
        self.ent_report_format.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_format = tk.Button(frame_rep_fmt, image=self.icon_format, command=self.load_report_formats)
        self.btn_format.pack(side="left")

        # 54) Report PDF Listbox
        lbl_rep_pdf = tk.Label(self.tab_options, text="Report PDF")
        lbl_rep_pdf.pack(anchor="w", padx=10)

        self.reportPMS_listbox = tk.Listbox(self.tab_options, height=8, selectmode="single", exportselection=False)
        self.reportPMS_listbox.pack(fill="x", padx=10, pady=(0, 10))

    # --- Logic Methods ---

    def read_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path: return

        self.ent_pems_file.delete(0, tk.END)
        self.ent_pems_file.insert(0, file_path)

        # 1) Read file, skip rows
        self.df = pd.read_csv(file_path, encoding='utf-8', low_memory=False, skiprows=0, header=0)

        # 3) Remove Not Available / Unnamed
        cols = [c for c in self.df.columns if "Not Available" not in str(c) and "Unnamed" not in str(c)]
        self.df = self.df[cols]

        # 4) Ensure eTIME exists
        if 'eTIME' not in self.df.columns:
            self.df.insert(1, 'eTIME', None)
            self.df.loc[0, 'eTIME'] = 'eTIME'
            self.df.loc[1, 'eTIME'] = 's'

        # 5) Assign rows
        self.columns_row = self.df.columns
        self.vars_row = self.df.loc[0, :]
        self.units_row = self.df.loc[1, :]
        self.df = self.df.loc[2:, :]

        # 6) Summary Info
        first_col = self.df.columns[0]
        try:
            summary_row_idx = self.df[self.df[first_col] == "Summary Information:"].index[0]
            
            # 7) Save Summary
            self.df_summary = self.df.loc[summary_row_idx:, :]
            self.df_summary.to_csv("PEMS_Summary.csv")
            
            # 8) Crop main DF
            self.df = self.df.loc[:summary_row_idx-1, :].copy()
            self.df.dropna(how='all', inplace=True)
            if 'Gas Path' in self.df.columns:
                self.df = self.df[self.df['Gas Path'] == 'SAMPLE']
        except IndexError:
            pass # No summary found

        # 9) Ensure eTIME conversion
        self.df = ensure_eTIME(self.df)

        # 10) Pre-select columns
        pre_select_columns = ['eTIME', 'Gas Path', 'Catalyst Temperature', 'Limit Adjusted iSCB_RH', 'Ambient Pressure', 
                              'Limit Adjusted iSCB_LAT', 'Load Percent', 'Limit Adjusted iCOOL_TEMP', 'Engine RPM', 
                              'Vehicle Speed', 'Mass Air Flow Rate', 'Catalyst Temp. 1-1', 'F/A Equiv. Ratio', 
                              'Engine Fuel Rate', 'Eng. Exh. Flow Rate', 'GPS Latitude', 'GPS Longitude', 
                              'Limit Adjusted iGPS_ALT', 'Limit Adjusted iGPS_GROUND_SPEED', 'Fuel Rate', 
                              'Instantaneous Fuel Flow', 'Derived Engine Torque.1', 'Derived Engine Power.1', 
                              'Instantaneous Mass CO2', 'Instantaneous Mass CO', 'Instantaneous Mass NO', 
                              'Instantaneous Mass NO2', 'Instantaneous Mass NOx', 'Corrected Instantaneous Mass NOx', 
                              'Instantaneous Mass HC', 'Instantaneous Mass CH4', 'Instantaneous Mass NMHC', 
                              'Instantaneous Mass O2', 'Air/Fuel Ratio at stoichiometry', 'Air/Fuel Ratio of Sample', 
                              'Lambda', 'Ambient Temperature', 'AMB Ambient Temperature', 'Brake Specific Fuel Consumption', 
                              'Mass Air Flow Rate.1']
        
        # 11) Pre-select vars (stored but currently unused in GUI logic per prompt except potentially for display)
        pre_select_vars = [ 'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 
                            'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'icMASS_FLOWx', 
                            'EXH_RATE', 'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 
                            'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 
                            'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 
                            'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP' ]

        # 13, 15) Populate Listbox
        self.columns_listbox.delete(0, tk.END)
        for col in self.df.columns:
            self.columns_listbox.insert(tk.END, col)
            if col in pre_select_columns:
                idx = self.columns_listbox.size() - 1
                self.columns_listbox.selection_set(idx)
                if col not in self.selected_columns_list:
                    self.selected_columns_list.append(col)

    def refresh_columns_listbox(self):
        # 16) Update listbox based on checkbox
        self.columns_listbox.delete(0, tk.END)
        
        if self.pre_select_checked.get():
            # Show only selected
            for col in self.selected_columns_list:
                self.columns_listbox.insert(tk.END, col)
                self.columns_listbox.selection_set(tk.END) # Select all visible since they are the selected ones
        else:
            # Show all, select match
            if not self.df.empty:
                for col in self.df.columns:
                    self.columns_listbox.insert(tk.END, col)
                    if col in self.selected_columns_list:
                        self.columns_listbox.selection_set(self.columns_listbox.size()-1)

    def on_column_select(self, event):
        # 16) Update selected_columns_list based on user interaction
        # Note: In multiple selection mode, curselection returns a tuple of indices.
        # We need to respect that users might deselect things.
        
        # If showing all
        if not self.pre_select_checked.get():
            selection = self.columns_listbox.curselection()
            current_visible = [self.columns_listbox.get(i) for i in selection]
            
            # Simple approach: add newly selected to internal list, logic can be complex for deselection 
            # without a persistent map, but we'll try to sync.
            # For this requirement, we assume we just track what is currently highlighted.
            self.selected_columns_list = current_visible

    def toggle_obd_section(self):
        # 22, 33) Enable/Disable OBD controls
        state = 'normal' if self.alignment_checked.get() else 'disabled'
        self.ent_obd_file.config(state=state)
        self.btn_obd.config(state=state)
        
        # 33) Enable ent_align_input if Alignment True AND OBD File not empty
        obd_file = self.ent_obd_file.get()
        if self.alignment_checked.get() and obd_file:
            self.ent_align_input.config(state='normal')
            self.btn_plot.config(state='normal') # 34
        else:
            self.ent_align_input.config(state='disabled')
            self.btn_plot.config(state='disabled')

    def select_obd_file(self):
        # 24) Read OBD
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path: return

        self.ent_obd_file.config(state='normal')
        self.ent_obd_file.delete(0, tk.END)
        self.ent_obd_file.insert(0, file_path)
        
        tmp = pd.read_csv(file_path, encoding='utf-8', low_memory=False, skiprows=0, header=0)
        
        # Remove Not Available/Unnamed
        cols = [c for c in tmp.columns if "Not Available" not in str(c) and "Unnamed" not in str(c)]
        tmp = tmp[cols]

        # 25) Insert eTIME if missing
        if 'eTIME' not in tmp.columns:
            tmp.insert(1, 'eTIME', None)
            tmp.loc[0, 'eTIME'] = 'eTIME'
            tmp.loc[1, 'eTIME'] = 's'

        # 26) Assign rows, update tmp
        # self.obd_columns_row = tmp.columns # Not explicitly requested to store, but good practice
        tmp = tmp.loc[2:, :]
        tmp.dropna(how='all', inplace=True)
        if 'Gas Path' in tmp.columns:
            tmp = tmp[tmp['Gas Path'] == 'SAMPLE']

        # 27) Summary Logic
        first_col = tmp.columns[0]
        try:
            summary_row_idx = tmp[tmp[first_col] == "Summary Information:"].index[0]
            self.obd_df_summary = tmp.loc[summary_row_idx:, :]
            # 28) Save Summary
            self.obd_df_summary.to_csv("OBD_Summary.csv")
            
            self.obd_df = tmp.loc[:summary_row_idx-1, :].copy()
        except IndexError:
            self.obd_df = tmp.copy()

        # 29) Ensure eTIME
        self.obd_df = ensure_eTIME(self.obd_df)

        # Update controls state
        self.toggle_obd_section()

    def plot_check_alignment(self):
        # 38) Plot selected alignment column
        sel_idx = self.align_listbox.curselection()
        if not sel_idx:
            messagebox.showwarning("Warning", "Please select a parameter in 'Time Alignment' listbox.")
            return
        
        align_col = self.align_listbox.get(sel_idx)

        # 40) Close figures
        if plt.get_fignums(): plt.close('all')

        # Logic to plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot PEMS
        if align_col in self.df.columns:
            ax.plot(self.df['eTIME'], pd.to_numeric(self.df[align_col], errors='coerce'), label=f"PEMS {align_col}")
        
        # Plot OBD
        if not self.obd_df.empty and align_col in self.obd_df.columns:
            ax.plot(self.obd_df['eTIME'], pd.to_numeric(self.obd_df[align_col], errors='coerce'), label=f"OBD {align_col}")

        ax.legend()
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(align_col)
        ax.set_title(f"Alignment Check: {align_col}")

        # 40) Call ImageDistanceMeasurer + Zoom
        # Assuming these classes attach to the axes/figure
        _ = ImageDistanceMeasurer(ax)
        _ = ZoomManager(ax)

        plt.show()

    def check_alignment_view(self):
        # 41) Callback for btn_plot
        sel_idx = self.align_listbox.curselection()
        if not sel_idx: return
        align_col = self.align_listbox.get(sel_idx)

        # 43) Add arguments
        pems_file = self.ent_pems_file.get()
        obd_file = self.ent_obd_file.get()
        align_input = self.ent_align_input.get()

        # 62) Call plot_alignment using align_col directly (no mapping)
        self.plot_alignment(self.df, self.obd_df, align_col)

    def plot_alignment(self, pems_df, obd_df, align_col):
        # 61) Plot df[align_col] and obd_df[align_col]
        # Remove ent_pems/ent_obd usage inside here as requested
        
        if plt.get_fignums(): plt.close('all')
        
        fig, ax = plt.subplots()
        
        if align_col in pems_df.columns:
            ax.plot(pems_df['eTIME'], pd.to_numeric(pems_df[align_col], errors='coerce'), label="PEMS")
        
        if not obd_df.empty and align_col in obd_df.columns:
            # Apply offset if exists in ent_align_input (Basic implementation)
            offset = 0
            try:
                offset = float(self.ent_align_input.get())
            except ValueError:
                pass
            
            # Assuming eTIME adjustment for alignment
            ax.plot(obd_df['eTIME'] + offset, pd.to_numeric(obd_df[align_col], errors='coerce'), label="OBD")

        ax.legend()
        plt.show()

    def run_analysis(self):
        # 49) Print status
        # Get Vehicle Speed index
        try:
            veh_speed_idx = self.df.columns.get_loc('Vehicle Speed')
        except KeyError:
            veh_speed_idx = "Not Found"

        print("--- RUN ANALYSIS ---")
        print(f"OBD File: {self.ent_obd_file.get()}")
        print(f"PEMS File: {self.ent_pems_file.get()}")
        print(f"Alignment Checked: {self.alignment_checked.get()}")
        print(f"Report Checked: {self.report_checked.get()}")
        print(f"Input Folder Checked: {self.input_file_dir_checked.get()}")
        print(f"Check Alignment Button: (Available)")
        print(f"Alignment Input: {self.ent_align_input.get()}")
        print(f"Index of 'Vehicle Speed': {veh_speed_idx}")
        print("--------------------")

    # --- Options Tab Methods ---

    def import_options_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.ent_options_dir.delete(0, tk.END)
        self.ent_options_dir.insert(0, folder)
        
        self.options_listbox.delete(0, tk.END)
        files = [f for f in os.listdir(folder) if f.endswith(('.xlsx', '.xls', '.m', '.mlx'))]
        for f in files:
            self.options_listbox.insert(tk.END, f)

    def on_option_double_click(self, event):
        sel = self.options_listbox.curselection()
        if not sel: return
        filename = self.options_listbox.get(sel)
        folder = self.ent_options_dir.get()
        path = os.path.join(folder, filename)

        if filename.endswith(('.xlsx', '.xls')):
            # Read 'Settings' worksheet, look for RDE_Settings_
            try:
                # 53) Logic implies reading specific sheet
                self.df_options = pd.read_excel(path, sheet_name="Settings")
            except Exception as e:
                print(f"Error reading Excel: {e}")

        elif filename.endswith('.m'):
            df_m = read_m_file_to_df(path)
            df_m.to_csv(path + ".csv")
        elif filename.endswith('.mlx'):
            df_mlx = read_mlx_content(path)
            df_mlx.to_csv(path + ".csv")

    def load_report_formats(self):
        # 57) Same directory logic or specific one? Assuming ask directory or use existing
        folder = filedialog.askdirectory()
        if not folder: return
        self.ent_report_format.delete(0, tk.END)
        self.ent_report_format.insert(0, folder)
        
        self.reportPMS_listbox.delete(0, tk.END)
        files = [f for f in os.listdir(folder) if f.endswith(('.xlsx', '.mlx'))]
        for f in files:
            self.reportPMS_listbox.insert(tk.END, f)

if __name__ == "__main__":
    root = tk.Tk()
    app = PEMSAnalysisGUI(root)
    root.mainloop()