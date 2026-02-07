"""
Docstring for PEMS_GUI11
Author: S. Lee
Description: A Windows 11 styled GUI for processing PEMS data with dynamic widget states and in
-memory icon generation.

Create a Windows 11 color 600x675 size GUI using tkinter, pillow icons, and font size 12 for the following.
1) Create a text box with a "PEMS File" label and the "Select" button to select an Excel file. Create the "Read" button to read the selected file using df = pd.read_csv with encoding='utf-8', low_memory=False, skiprows=0, header=0 and skipping first 0 rows when clicking the "Read" button. 
Replace the "Select" button with a Windows 11 color "Folder" large icon. Replace the "Read" button with Windows 11 color "Read File" large icon. Display the "Select a file" and "Read File" when placing a mouse pointer on the "Select" icon and "Read" icon respectively. Adjust the textbox length to tightly fit with the "Select" icon and "Read" icon horizontally.
Assign columns = df.columns, vars = df.loc[0, :] and units = df.loc[1, :]. Update df.columns = vars and df = df.loc[2:, :].
2) Create a "Input_file_dir" checkbox button named "Check to process all CSV file in a folder". Create the "Input_file_dir_checked" variable to pass the status.
3) Create a 15-row scrollable "columns_listbox" list box to display the data frame column header for data labeling. Label the "columns_listbox" list box with the "Data Fields". Enable multiple selection in the list box by clicking mouse pointers. 
Set the '' in the  "columns_listbox" list box before clicking the "Read" icon.
4) Draw a blue horizontal line between two list boxes.
4) Create a 5-row scrollable "align_listbox" list box to display the "Vehicle Speed", "Engine Speed", "Exhaust Mass Flowrate" and "Battery Current" alignment data.
Enable multiple selection in the list box by clicking mouse pointers. 
Label the "align_listbox" list box with the "Time Alignment".
5) Set the align_listbox width equal to the columns_listbox width.
6) Create an "Alignment" checkbox button and "Report" checkbox button horizontally to call back functions. Check the "Report" checkbox.
7) Create a text box with an "OBD File" label. Create an "OBD" button. Replace the "OBD" button with a Windows 11 color Truck icon to select a CSV file. Display the "Select an OBD file" when placing a mouse pointer on the "OBD" icon. Only Enable the "OBD File" text box and "OBD" button when the "Alignment" checkbox is True.
8) Create the "Check Alignment" button. Create an input textbox next to the "Check Alignment" button. Display the “View Alignment Plot” and the "Type Alignment Values to OBD" when placing a mouse pointer on the "Check Alignment" button and the Alignment "input textbox" respectively.
Enable only the input textbox after when the "Alignment" checkbox is True and the “OBD File” text box is not empty.
Adjust the horizontal x coordinate of the "OBD" button at the btn_read.winfo_x().
Adjust the “OBD File” text box width little less than the horizontal x coordinate of the "OBD" button.
9) Set the "Check Alignment" button with a light magenta-color background to call back "time_alignment()" function with the selected items in the "align_listbox".
10) Create a font size 20, black bold font, "RUN" big button with a light blue-color background to call back the "run_analysis()" function.
11) Assign Alignment_checked and Report_checked variables to pass the "Alignment"  and "Report" Checkbox check status.
12) After clicking the "Read" icon, pre-select the ['eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'EXH_RATE', 'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'] in the columns_listbox.
13) Pre-select the "Vehicle Speed"  and "Engine Speed" in the "align_listbox" listbox.
14) Fix the _tkinter.TclError: expected integer but got "UI"
15) Enable to select multiple items in both the columns_listbox and align_listbox listbox
16) Print the obd_ent, pems_ent, "Alignment", "Report", "Input_file_dir"  checkbox status, "Check Alignment" button, align_values_ent textbox values, and the index of 'iVEH_SPEED' in df.columns when clicking the "RUN" button.
17) Fix automatically deselecting an item in a listbox while selecting an item in another listbox 

"""


import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from PIL import Image, ImageTk, ImageDraw

# Global DataFrame variable to store data between functions
df = None

class Windows11GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows 11 Data Processor")
        self.root.geometry("600x675")
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

        # --- Icon Generation (In-Memory) ---
        # We create these once to prevent garbage collection
        self.icon_folder = self.create_icon("Folder", "#ffe680", "#E8B931")
        self.icon_read = self.create_icon("Read", "#ffffff", "#0078d4", text_color="#0078d4")
        self.icon_truck = self.create_icon("Truck", "#73ec8e", "#107c10")

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
        self.columns_listbox = tk.Listbox(frame_cols, height=15, font=self.font_default, 
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
                                        selectmode=tk.MULTIPLE, yscrollcommand=sb_align.set,
                                        exportselection=False, borderwidth=1, relief="solid")
        sb_align.config(command=self.align_listbox.yview)

        sb_align.pack(side="right", fill="y")
        self.align_listbox.pack(side="left", fill="x", expand=True)

        # Populate Alignment Options
        align_opts = ["Vehicle Speed", "Engine Speed", "Exhaust Mass Flowrate", "Battery Current"]
        for item in align_opts:
            self.align_listbox.insert(tk.END, item)

        # =========================================================================
        # 6) Alignment & Report Checkboxes
        # =========================================================================
        frame_checks = tk.Frame(root, bg="#f3f3f3")
        frame_checks.pack(fill="x", padx=20, pady=5)

        chk_align = tk.Checkbutton(frame_checks, text="Alignment", variable=self.alignment_checked,
                                   font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3")
        chk_align.pack(side="left", padx=(0, 20))

        chk_report = tk.Checkbutton(frame_checks, text="Report", variable=self.report_checked,
                                    font=self.font_default, bg="#f3f3f3", activebackground="#f3f3f3")
        chk_report.pack(side="left")

        # =========================================================================
        # 7) OBD File Section
        # =========================================================================
        frame_obd = tk.Frame(root, bg="#f3f3f3")
        frame_obd.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_obd, text="OBD File", font=self.font_default, bg="#f3f3f3").grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.ent_obd = tk.Entry(frame_obd, textvariable=self.obd_file_path, font=self.font_default, state="disabled")
        self.ent_obd.grid(row=0, column=1, sticky="ew")

        # OBD Button (Truck Icon)
        self.btn_obd = tk.Button(frame_obd, image=self.icon_truck, command=self.select_obd_file,
                                 bd=0, bg="#f3f3f3", activebackground="#e5e5e5", cursor="hand2", state="disabled")
        # Placing in column 3 to match the 'Read' button from the top frame structure
        self.btn_obd.grid(row=0, column=3, padx=5)
        self.create_tooltip(self.btn_obd, "Select an OBD file")

        # Layout Weights: Matches PEMS frame to align the buttons vertically
        frame_obd.columnconfigure(1, weight=1)

        # =========================================================================
        # 8 & 9) Check Alignment Button & Input
        # =========================================================================
        frame_check_align = tk.Frame(root, bg="#f3f3f3")
        frame_check_align.pack(fill="x", padx=20, pady=10)

        # Check Alignment Button (Light Magenta)
        self.btn_check_align = tk.Button(frame_check_align, text="Check Alignment", command=self.time_alignment,
                                         font=self.font_default, bg="#ff80ff", width=16)
        self.btn_check_align.pack(side="left", padx=(0, 10))
        self.create_tooltip(self.btn_check_align, "View Alignment Plot")

        # Alignment Input Textbox
        self.ent_align_input = tk.Entry(frame_check_align, textvariable=self.align_values_var, 
                                        font=self.font_default, state="disabled")
        self.ent_align_input.pack(side="left", fill="x", expand=True)
        self.create_tooltip(self.ent_align_input, "Type Alignment Values to OBD")

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
        file = filedialog.askopenfilename(title="Select PEMS File", filetypes=[("CSV/Excel", "*.csv *.xlsx")])
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
        # Also re-check the input box state
        self.check_alignment_input_state()

    def check_alignment_input_state(self, *args):
        """Enable Input Box only if Alignment Checked AND OBD File not empty."""
        if self.alignment_checked.get() and self.obd_file_path.get().strip():
            self.ent_align_input.config(state="normal")
        else:
            self.ent_align_input.config(state="disabled")

    def read_file(self):
        global df
        path = self.pems_file_path.get()
        if not path:
            messagebox.showwarning("Warning", "Please select a PEMS file first.")
            return

        try:
            # 1) Read Logic:
            # skiprows=0, header=0, skip first 1 row logic as requested
            temp_df = pd.read_csv(path, encoding='utf-8', low_memory=False, skiprows=0, header=0)
            
            # Logic: 
            # Row 0 -> variable names (vars)
            # Row 1 -> units
            # Row 2+ -> data
            
            # Ensure file has enough rows
            if len(temp_df) < 2:
                raise ValueError("File too short to contain Vars, Units, and Data.")

            vars_row = temp_df.loc[0, :]
            # units_row = temp_df.loc[1, :] # Captured but unused in prompt logic, just required assignment
            
            # Update columns
            temp_df.columns = vars_row
            
            # Slice data
            df = temp_df.loc[2:, :].copy()
            df.reset_index(drop=True, inplace=True)

            # 3) Populate Listbox
            self.columns_listbox.delete(0, tk.END) # Clear existing
            for col in df.columns:
                self.columns_listbox.insert(tk.END, str(col))

            # 12) Pre-select specific items in columns_listbox
            pre_select_items = [
                'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 
                'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'EXH_RATE', 
                'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 
                'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 
                'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 
                'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'
            ]

            # Loop through listbox items to find indices
            listbox_items = self.columns_listbox.get(0, tk.END)
            for idx, item in enumerate(listbox_items):
                if item in pre_select_items:
                    self.columns_listbox.selection_set(idx)

            # 13) Pre-select items in align_listbox
            # "Vehicle Speed" is index 0, "Engine Speed" is index 1 based on initialization
            self.align_listbox.selection_set(0)
            self.align_listbox.selection_set(1)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")

    def time_alignment(self):
        """Callback for Check Alignment Button"""
        # Get selected items from align_listbox
        selected_indices = self.align_listbox.curselection()
        selected_values = [self.align_listbox.get(i) for i in selected_indices]
        print(f"Executing time_alignment() with: {selected_values}")

    def run_analysis(self):
        """Callback for RUN Button"""
        # 16) Print Requirements
        print("--- RUN ANALYSIS ---")
        print(f"OBD Entry Widget Object: {self.ent_obd}")
        print(f"PEMS Entry Widget Object: {self.ent_pems}")
        
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

if __name__ == "__main__":
    root = tk.Tk()
    app = Windows11GUI(root)
    root.mainloop()