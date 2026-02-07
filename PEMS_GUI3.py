"""
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
8) Create a font size 14, black bold font, "Check Alignment" big button with a light magenta-color background to call back "time_alignment()" function with the selected items in the "align_listbox".
9) Create a font size 14, black bold font, "RUN" big button with a light blue-color background to call back the "run_analysis()" function.
Print obd_ent, pems_ent when clicking the “RUN” button.
10) Create Alignment_checked and Report_checked variables to pass the "Alignment"  and "Report" Checkbox check status.
11) After clicking the "Read" icon, pre-select the ['eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD', 'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'EXH_RATE', 'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'] in the columns_listbox.
12) Pre-select the "Vehicle Speed"  and "Engine Speed" in the "align_listbox" listbox.
13) Fix the _tkinter.TclError: expected integer but got "UI"
14) Enable to select multiple items in both the columns_listbox and align_listbox listbox
15) Print the "Alignment" , "Report" and "Input_file_dir" checkbox status when clicking the "RUN" button.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

# Optional: Use PIL to draw Windows 11-like colored icons
try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ----------------------------
# Tooltip helper
# ----------------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tip,
            text=self.text,
            background="#FFFFE0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 10)  # integer size to avoid TclError
        )
        label.pack(ipadx=6, ipady=4)

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# ----------------------------
# Icon generators (PIL)
# ----------------------------
def make_folder_icon(size=40):
    if not PIL_AVAILABLE:
        return None
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    folder_color = "#F3C623"   # Windows 11-like warm yellow
    tab_color = "#E0A106"
    outline = "#C48A00"
    body_rect = [int(size*0.08), int(size*0.38), int(size*0.92), int(size*0.88)]
    d.rounded_rectangle(body_rect, radius=int(size*0.08), fill=folder_color, outline=outline, width=max(1, int(size*0.03)))
    tab_rect = [int(size*0.08), int(size*0.20), int(size*0.48), int(size*0.40)]
    d.rounded_rectangle(tab_rect, radius=int(size*0.06), fill=tab_color, outline=outline, width=max(1, int(size*0.03)))
    return ImageTk.PhotoImage(img)

def make_read_icon(size=40):
    if not PIL_AVAILABLE:
        return None
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    paper_fill = "#FFFFFF"
    border = "#2563EB"  # fluent blue
    line_color = "#4B5563"  # gray
    rect = [int(size*0.14), int(size*0.12), int(size*0.86), int(size*0.88)]
    d.rounded_rectangle(rect, radius=int(size*0.10), fill=paper_fill, outline=border, width=max(1, int(size*0.03)))
    for i in range(4):
        y = int(size * (0.25 + i * 0.15))
        d.line([(int(size * 0.22), y), (int(size * 0.78), y)], fill=line_color, width=max(1, int(size*0.04)))
    d.line([(int(size*0.30), int(size*0.72)), (int(size*0.42), int(size*0.82)), (int(size*0.70), int(size*0.60))],
           fill="#16A34A", width=max(1, int(size*0.05)))
    return ImageTk.PhotoImage(img)

def make_car_icon(size=40):
    if not PIL_AVAILABLE:
        return None
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = "#0078D4"  # Windows 11 accent blue
    window = "#93C5FD"
    wheel = "#111827"
    # Car body
    d.rounded_rectangle([int(size*0.15), int(size*0.35), int(size*0.85), int(size*0.70)], radius=int(size*0.12), fill=body)
    # Windows
    d.rounded_rectangle([int(size*0.30), int(size*0.25), int(size*0.70), int(size*0.45)], radius=int(size*0.10), fill=window)
    # Wheels
    d.ellipse([int(size*0.25), int(size*0.65), int(size*0.38), int(size*0.85)], fill=wheel)
    d.ellipse([int(size*0.62), int(size*0.65), int(size*0.75), int(size*0.85)], fill=wheel)
    return ImageTk.PhotoImage(img)

# ----------------------------
# App-level data
# ----------------------------
df = None
preselect_columns = [
    'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD',
    'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'EXH_RATE',
    'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp',
    'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm',
    'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda',
    'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP'
]
align_items = ["Vehicle Speed", "Engine Speed", "Exhaust Mass Flowrate", "Battery Current"]

# ----------------------------
# Callbacks
# ----------------------------
def select_pems_file():
    path = filedialog.askopenfilename(
        title="Select PEMS Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )
    if path:
        pems_file_var.set(path)

def read_pems_file():
    path = pems_file_var.get().strip()
    if not path:
        messagebox.showwarning("No file selected", "Please select a PEMS Excel file first.")
        return
    try:
        global df
        df = pd.read_excel(path, skiprows=1)
    except Exception as e:
        messagebox.showerror("Read Error", f"Failed to read file:\n{e}")
        return

    # Update columns_listbox with df columns
    cols = [str(c) for c in df.columns]
    columns_listbox.delete(0, tk.END)
    for c in cols:
        columns_listbox.insert(tk.END, c)

    # Preselect specified columns if present
    item_to_index = {columns_listbox.get(i): i for i in range(columns_listbox.size())}
    for name in preselect_columns:
        if name in item_to_index:
            columns_listbox.selection_set(item_to_index[name])

    # Compute width based on longest column name, set both listboxes equal
    width_chars = max((len(c) for c in cols), default=30) + 2
    width_chars = int(max(30, min(width_chars, 80)))  # clamp and ensure int
    columns_listbox.configure(width=width_chars)
    align_listbox.configure(width=width_chars)

    messagebox.showinfo("Read Complete", f"Loaded {len(df)} rows and {len(cols)} columns.")

def select_obd_file():
    path = filedialog.askopenfilename(
        title="Select OBD Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )
    if path:
        obd_file_var.set(path)

def on_alignment_toggle():
    enabled = Alignment_checked.get()
    state = "normal" if enabled else "disabled"
    obd_ent.configure(state=state)
    obd_btn.configure(state=state)
    print("Alignment toggled:", enabled)

def on_report_toggle():
    print("Report toggled:", Report_checked.get())

def time_alignment():
    selected_align = [align_listbox.get(i) for i in align_listbox.curselection()]
    print("time_alignment() called with:", selected_align)
    messagebox.showinfo("Alignment View", f"Selected alignment fields:\n{selected_align}")

def run_analysis():
    # Print Entry widgets and their values as requested
    print("pems_ent:", pems_ent, "value:", pems_file_var.get())
    print("obd_ent:", obd_ent, "value:", obd_file_var.get())

    # Also print checkbox states
    print("Alignment:", Alignment_checked.get())
    print("Report:", Report_checked.get())
    print("Input_file_dir:", Input_file_dir_checked.get())

    # Collect selections (optional summary)
    selected_cols = [columns_listbox.get(i) for i in columns_listbox.curselection()]
    selected_align = [align_listbox.get(i) for i in align_listbox.curselection()]
    summary = (
        f"PEMS file: {pems_file_var.get()}\n"
        f"OBD file: {obd_file_var.get() if Alignment_checked.get() else '(disabled)'}\n"
        f"Selected columns: {selected_cols}\n"
        f"Alignment selections: {selected_align}\n"
        f"Alignment_checked: {Alignment_checked.get()}\n"
        f"Report_checked: {Report_checked.get()}\n"
        f"Input_file_dir_checked: {Input_file_dir_checked.get()}"
    )
    messagebox.showinfo("RUN", "Analysis started.\n\n" + summary)

# ----------------------------
# Build UI
# ----------------------------
root = tk.Tk()
root.title("PEMS/OBD Data Processor")
root.geometry("600x670")
ui_bg = "#F7F7F7"   # Windows 11-like light background
accent_blue = "#0078D4"
light_blue = "#ADD8E6"
magenta = "#FF00FF"
light_magenta = "#F8C8FF"
line_blue = "#2563EB"

# Global font settings (tuple with integer size avoids TclError)
root.option_add("*Font", ("Segoe UI", 11))
root.configure(bg=ui_bg)

# Main container
container = tk.Frame(root, bg=ui_bg)
container.pack(fill="both", expand=True, padx=10, pady=10)

# Row 1: PEMS File selector
pems_frame = tk.Frame(container, bg=ui_bg)
pems_frame.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))
container.grid_columnconfigure(0, weight=1)
pems_frame.grid_columnconfigure(1, weight=1)  # Entry expands between label and icons

pems_label = tk.Label(pems_frame, text="PEMS File", bg=ui_bg)
pems_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

pems_file_var = tk.StringVar()
pems_ent = tk.Entry(pems_frame, textvariable=pems_file_var)
pems_ent.grid(row=0, column=1, sticky="ew", padx=(0, 8))

# Icons (Folder and Read File)
folder_icon_img = make_folder_icon(size=40)
read_icon_img = make_read_icon(size=40)

if folder_icon_img:
    select_btn = tk.Button(
        pems_frame, image=folder_icon_img, command=select_pems_file,
        bd=0, highlightthickness=0, cursor="hand2", bg=ui_bg, activebackground=ui_bg
    )
else:
    select_btn = tk.Button(
        pems_frame, text="📁", command=select_pems_file,
        bd=1, cursor="hand2", fg="white", bg=accent_blue, activebackground=accent_blue
    )
select_btn.grid(row=0, column=2, padx=(0, 6))
ToolTip(select_btn, "Select a file")

if read_icon_img:
    read_btn = tk.Button(
        pems_frame, image=read_icon_img, command=read_pems_file,
        bd=0, highlightthickness=0, cursor="hand2", bg=ui_bg, activebackground=ui_bg
    )
else:
    read_btn = tk.Button(
        pems_frame, text="📘", command=read_pems_file,
        bd=1, cursor="hand2", fg="white", bg="#005A9E", activebackground="#005A9E"
    )
read_btn.grid(row=0, column=3)
ToolTip(read_btn, "Read File")

# Row 2: Checkbox to process all CSV files in a folder
checkbox_frame = tk.Frame(container, bg=ui_bg)
checkbox_frame.grid(row=1, column=0, sticky="w", padx=4, pady=(0, 8))
Input_file_dir_checked = tk.BooleanVar(value=False)
tk.Checkbutton(
    checkbox_frame,
    text="Check to process all CSV file in a folder",
    variable=Input_file_dir_checked,
    bg=ui_bg, activebackground=ui_bg
).grid(row=0, column=0, sticky="w")

# Row 3: Columns listbox with label
columns_frame = tk.Frame(container, bg=ui_bg)
columns_frame.grid(row=2, column=0, sticky="nsew", padx=4, pady=(0, 6))
container.grid_rowconfigure(2, weight=1)
columns_frame.grid_columnconfigure(0, weight=1)
columns_frame.grid_rowconfigure(1, weight=1)

tk.Label(columns_frame, text="Data Fields", bg=ui_bg).grid(row=0, column=0, sticky="w")

columns_listbox = tk.Listbox(
    columns_frame,
    height=10,
    selectmode="multiple",     # enable multiple selection by clicking
    exportselection=False      # keep selections when switching focus
)
columns_scroll = tk.Scrollbar(columns_frame, orient="vertical", command=columns_listbox.yview)
columns_listbox.configure(yscrollcommand=columns_scroll.set)
columns_listbox.grid(row=1, column=0, sticky="nsew")
columns_scroll.grid(row=1, column=1, sticky="ns")

# Initial blank entry '' before clicking Read
columns_listbox.insert(tk.END, "")
columns_listbox.configure(width=40)  # initial width

# Row 4: Blue horizontal line between two listboxes
line_canvas = tk.Canvas(container, height=4, highlightthickness=0, bg=ui_bg)
line_canvas.grid(row=3, column=0, sticky="ew", pady=(6, 6), padx=4)
def draw_line(evt=None):
    line_canvas.delete("all")
    line_canvas.create_line(10, 2, line_canvas.winfo_width()-10, 2, fill=line_blue, width=2)
line_canvas.bind("<Configure>", draw_line)

# Row 5: Align listbox with label
align_frame = tk.Frame(container, bg=ui_bg)
align_frame.grid(row=4, column=0, sticky="nsew", padx=4, pady=(0, 8))
container.grid_rowconfigure(4, weight=1)
align_frame.grid_columnconfigure(0, weight=1)
align_frame.grid_rowconfigure(1, weight=1)

tk.Label(align_frame, text="Time Alignment", bg=ui_bg).grid(row=0, column=0, sticky="w")

align_listbox = tk.Listbox(
    align_frame,
    height=5,
    selectmode="multiple",
    exportselection=False
)
align_scroll = tk.Scrollbar(align_frame, orient="vertical", command=align_listbox.yview)
align_listbox.configure(yscrollcommand=align_scroll.set)
align_listbox.grid(row=1, column=0, sticky="nsew")
align_scroll.grid(row=1, column=1, sticky="ns")

# Populate alignment items and preselect Vehicle Speed & Engine Speed
for item in align_items:
    align_listbox.insert(tk.END, item)
for i in range(align_listbox.size()):
    val = align_listbox.get(i)
    if val in {"Vehicle Speed", "Engine Speed"}:
        align_listbox.selection_set(i)

# Match align_listbox width to columns_listbox width initially
align_listbox.configure(width=int(columns_listbox.cget("width")))

# Row 6: Alignment and Report checkboxes horizontally
checks_frame = tk.Frame(container, bg=ui_bg)
checks_frame.grid(row=5, column=0, sticky="w", padx=4, pady=(0, 8))

Alignment_checked = tk.BooleanVar(value=False)
Report_checked = tk.BooleanVar(value=True)  # Report checked

tk.Checkbutton(
    checks_frame, text="Alignment", variable=Alignment_checked, command=on_alignment_toggle,
    bg=ui_bg, activebackground=ui_bg
).grid(row=0, column=0, sticky="w", padx=(0, 12))
tk.Checkbutton(
    checks_frame, text="Report", variable=Report_checked, command=on_report_toggle,
    bg=ui_bg, activebackground=ui_bg
).grid(row=0, column=1, sticky="w")

# Row 7: OBD File selector (enabled only when Alignment is True)
obd_frame = tk.Frame(container, bg=ui_bg)
obd_frame.grid(row=6, column=0, sticky="ew", padx=4, pady=(0, 8))
obd_frame.grid_columnconfigure(1, weight=1)

tk.Label(obd_frame, text="OBD File", bg=ui_bg).grid(row=0, column=0, sticky="w", padx=(0, 8))
obd_file_var = tk.StringVar()
obd_ent = tk.Entry(obd_frame, textvariable=obd_file_var, state="disabled")
obd_ent.grid(row=0, column=1, sticky="ew", padx=(0, 8))

car_icon_img = make_car_icon(size=40) or None
if car_icon_img:
    obd_btn = tk.Button(
        obd_frame, image=car_icon_img, command=select_obd_file,
        bd=0, highlightthickness=0, cursor="hand2", state="disabled", bg=ui_bg, activebackground=ui_bg
    )
else:
    # Fallback emoji with accent color
    obd_btn = tk.Button(
        obd_frame, text="🚗", command=select_obd_file,
        bd=1, cursor="hand2", state="disabled", fg="white", bg=accent_blue, activebackground=accent_blue
    )
obd_btn.grid(row=0, column=2)
ToolTip(obd_btn, "Select an OBD file")

# Row 8: Alignment View and RUN big buttons (EXIT removed)
actions_frame = tk.Frame(container, bg=ui_bg)
actions_frame.grid(row=7, column=0, sticky="ew", padx=4, pady=(10, 0))
actions_frame.grid_columnconfigure(0, weight=1)
actions_frame.grid_columnconfigure(1, weight=1)

align_view_btn = tk.Button(
    actions_frame,
    text="Check Alignment",
    font=("Segoe UI", 14, "bold"),
    bg=light_magenta, fg="black",
    activebackground=light_magenta,
    command=time_alignment
)
align_view_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6), ipady=6)

run_btn = tk.Button(
    actions_frame,
    text="RUN",
    font=("Segoe UI", 14, "bold"),
    bg=light_blue, fg="black",
    activebackground="#93C5FD",
    command=run_analysis
)
run_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0), ipady=6)

# Final tweaks
root.update_idletasks()
draw_line()

root.mainloop()