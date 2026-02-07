"""
Programmatically creates Windows 11 style icons using Pillow.

pyinstaller --onefile main.py
Create a Windows 11 color 600x670 size GUI using tkinter and font size 11 for the following.
1)  Create a text box with a "PEMS File" label and the "Select" button to select an Excel file. Create the "Read" button to read the selected file using df = pd.read_excel by skipping first 1 rows when clicking the "Read" button. 
Replace the "Select" button with a Windows 11 color "Folder" large icon. Replace the "Read" button with Windows 11 color "Read File" large icon. Display the "Select a file" and "Read File" when placing a mouse pointer on the "Select" icon and "Read" icon respectively. Adjust the textbox length to tightly fit with the "Select" icon and "Read" icon horizontally.
2) Create a "Input_file_dir" checkbox button named "Check to process all CSV file in a folder". Create the "Input_file_dir_checked" variable to pass the status.
3) Create a 10-row scrollable "columns_listbox" list box to display the data frame column header for data labeling. Label the "columns_listbox" list box with the "Data Fields". Enable multiple selection in the list box by clicking mouse pointers. 
Set the '' in the  "columns_listbox" list box before clicking the "Read" icon.
4) Draw a blue horizontal line between two list boxes.
4) Create a 5-row scrollable "align_listbox" list box to display the "Vehicle Speed", "Engine Speed", "Exhaust Mass Flowrate" and "Battery Current" alignment data.
Enable multiple selection in the list box by clicking mouse pointers. 
Label the "align_listbox" list box with the "Time Alignment".
5) Set the align_listbox width equal to the columns_listbox width.
6) Create a "Alignment" checkbox button and "Report" checkbox button horizontally to call back functions. Check the "Report" checkbox.
7) Create a text box with an "OBD File" label. Create an "OBD" button" Replace the "OBD" button with a Windows 11 color large car icon to select an Excel file. Display the "Select an OBD file" when placing a mouse pointer on the "OBD" icon. Only Enable the "OBD File" text box and "OBD" button when the "Alignment" checkbox is True.
8) Create a font size 14, black bold font, "RUN" big button with a light blue-color background to call back the "run_analysis()" function.
Print obd_ent, pems_ent when clicking the “RUN” button.
9) Create a font size 14, black bold font, "EXIT" big button with a magenta color background to terminate/exit this GUI.
10) Create Alignment_checked and Report_checked variables to pass the "Alignment"  and "Report" Checkbox check status.
11) After clicking the "Read" icon, pre-select the ['eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'EXH_RATE', 'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'] in the columns_listbox.
12) Pre-select the "Vehicle Speed"  and "Engine Speed" in the "align_listbox" listbox.
13) Fix the _tkinter.TclError: expected integer but got "UI"
14) Enable to select multiple items in both the columns_listbox and align_listbox listbox
15) Print the "Alignment" , "Report" and "Input_file_dir" checkbox status when clicking the "RUN" button.

"""


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import pandas as pd

def create_win11_icon(icon_type):
    """Programmatically creates Windows 11 style icons using Pillow."""
    img = Image.new('RGBA', (36, 36), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    if icon_type == "folder":
        draw.rounded_rectangle([4, 10, 32, 28], radius=3, fill="#FFD666") # Yellow
        draw.polygon([(4, 14), (14, 14), (18, 10), (4, 10)], fill="#FFC107")
    elif icon_type == "read":
        draw.rounded_rectangle([6, 4, 30, 32], radius=3, fill="#0078D4") # Blue
        for y in range(12, 28, 5): draw.line([12, y, 24, y], fill="white", width=2)
    elif icon_type == "vehicle":
        draw.rounded_rectangle([6, 18, 30, 30], radius=4, fill="#4CAF50") # Green
        draw.polygon([(10, 18), (14, 8), (22, 8), (26, 18)], fill="#4CAF50")
    return ImageTk.PhotoImage(img)

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, background="#ffffff", relief="solid", borderwidth=1, font=("Segoe UI", 9)).pack()

    def hide_tip(self, event=None):
        if self.tip_window: self.tip_window.destroy()
        self.tip_window = None

class VehicleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PEMS & OBD Analysis")
        # 13: Fixed TclError by using string literal for geometry
        self.root.geometry("600x670")
        
        self.font_std = ("Segoe UI", 11)
        self.font_bold = ("Segoe UI", 14, "bold")

        # variables (2, 10)
        self.Input_file_dir_checked = tk.BooleanVar()
        self.Alignment_checked = tk.BooleanVar()
        self.Report_checked = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self.root, padding=15)
        container.pack(fill="both", expand=True)

        # 1: PEMS File Section
        pems_f = ttk.Frame(container)
        pems_f.pack(fill="x", pady=5)
        ttk.Label(pems_f, text="PEMS File", font=self.font_std).pack(side="left")
        self.pems_ent = ttk.Entry(pems_f, font=self.font_std)
        self.pems_ent.pack(side="left", fill="x", expand=True, padx=5)

        self.ico_fold = create_win11_icon("folder")
        self.ico_read = create_win11_icon("read")
        self.ico_veh = create_win11_icon("vehicle")

        btn_sel = tk.Button(pems_f, image=self.ico_fold, command=self.select_pems, bd=0, cursor="hand2")
        btn_sel.pack(side="left", padx=2)
        Tooltip(btn_sel, "Select a file")

        btn_rd = tk.Button(pems_f, image=self.ico_read, command=self.read_pems, bd=0, cursor="hand2")
        btn_rd.pack(side="left", padx=2)
        Tooltip(btn_rd, "Read File")

        # 2: Folder Checkbox
        ttk.Checkbutton(container, text="Check to process all CSV file in a folder", 
                        variable=self.Input_file_dir_checked).pack(anchor="w", pady=5)

        # 3 & 14: Data Fields Listbox
        ttk.Label(container, text="Data Fields", font=self.font_std).pack(anchor="w")
        lf1 = ttk.Frame(container)
        lf1.pack(fill="x", pady=2)
        self.columns_listbox = tk.Listbox(lf1, height=10, selectmode="multiple", font=self.font_std, exportselection=0)
        sc1 = ttk.Scrollbar(lf1, orient="vertical", command=self.columns_listbox.yview)
        self.columns_listbox.config(yscrollcommand=sc1.set)
        self.columns_listbox.pack(side="left", fill="x", expand=True)
        sc1.pack(side="right", fill="y")
        self.columns_listbox.insert(tk.END, "''")

        # 4: Blue horizontal line
        tk.Frame(container, height=2, bg="#0078D4").pack(fill="x", pady=10)

        # 4, 5, 14: Time Alignment Listbox
        ttk.Label(container, text="Time Alignment", font=self.font_std).pack(anchor="w")
        lf2 = ttk.Frame(container)
        lf2.pack(fill="x", pady=2)
        self.align_listbox = tk.Listbox(lf2, height=5, selectmode="multiple", font=self.font_std, exportselection=0)
        sc2 = ttk.Scrollbar(lf2, orient="vertical", command=self.align_listbox.yview)
        self.align_listbox.config(yscrollcommand=sc2.set)
        self.align_listbox.pack(side="left", fill="x", expand=True)
        sc2.pack(side="right", fill="y")
        
        # 12: Pre-select align data
        for item in ["Vehicle Speed", "Engine Speed", "Exhaust Mass Flowrate", "Battery Current"]:
            self.align_listbox.insert(tk.END, item)
        self.align_listbox.select_set(0, 1)

        # 6: Checkboxes
        chk_f = ttk.Frame(container)
        chk_f.pack(fill="x", pady=5)
        ttk.Checkbutton(chk_f, text="Alignment", variable=self.Alignment_checked, command=self.toggle_obd).pack(side="left", padx=10)
        ttk.Checkbutton(chk_f, text="Report", variable=self.Report_checked).pack(side="left")

        # 7: OBD File Section
        obd_f = ttk.Frame(container)
        obd_f.pack(fill="x", pady=5)
        ttk.Label(obd_f, text="OBD File", font=self.font_std).pack(side="left")
        self.obd_ent = ttk.Entry(obd_f, font=self.font_std, state="disabled")
        self.obd_ent.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_obd = tk.Button(obd_f, image=self.ico_veh, bd=0, state="disabled", command=self.select_obd)
        self.btn_obd.pack(side="left")
        Tooltip(self.btn_obd, "Select an OBD file")

        # 8 & 9: Big Action Buttons
        btn_container = ttk.Frame(container)
        btn_container.pack(fill="x", pady=15)
        tk.Button(btn_container, text="RUN", font=self.font_bold, bg="#D6EAF8", fg="black", command=self.run_analysis).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(btn_container, text="EXIT", font=self.font_bold, bg="magenta", fg="black", command=self.root.quit).pack(side="left", fill="x", expand=True, padx=5)

    def toggle_obd(self):
        state = "normal" if self.Alignment_checked.get() else "disabled"
        self.obd_ent.config(state=state); self.btn_obd.config(state=state)

    def select_pems(self):
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if p: self.pems_ent.delete(0, tk.END); self.pems_ent.insert(0, p)

    def select_obd(self):
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if p: self.obd_ent.delete(0, tk.END); self.obd_ent.insert(0, p)

    def read_pems(self):
        path = self.pems_ent.get()
        if not path: return
        try:
            # 1: read_excel skipping 1 row
            df = pd.read_excel(path, skiprows=1)
            self.columns_listbox.delete(0, tk.END)
            cols = df.columns.tolist()
            for c in cols: self.columns_listbox.insert(tk.END, c)
            # 11: Pre-selection targets
            targets = ['eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 
                       'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 
                       'EXH_RATE', 'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 
                       'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 
                       'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 
                       'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 
                       'AmbTemp', 'iBSFC', 'iMAF', 'iMAP']
            for i, c in enumerate(cols):
                if c in targets: self.columns_listbox.select_set(i)
        except Exception as e: messagebox.showerror("Error", f"Read failed: {e}")

    def run_analysis(self):
        # 15: Print checkbox statuses
        print(f"Alignment Checked: {self.Alignment_checked.get()}")
        print(f"Report Checked: {self.Report_checked.get()}")
        print(f"Input File Dir Checked: {self.Input_file_dir_checked.get()}")
        print(f"Alignment Status: {self.Alignment_checked.get()}")
        print(f"Report Status: {self.Report_checked.get()}")
        print(f"Input File Dir Status: {self.Input_file_dir_checked.get()}")
        print(f"OBD filename: {self.obd_ent.get()}")
        print(f"PEMS filename: {self.pems_ent.get()}")
        print('Running analysis... (this is a placeholder)')

if __name__ == "__main__":
    root = tk.Tk()
    app = VehicleApp(root)
    root.mainloop()
