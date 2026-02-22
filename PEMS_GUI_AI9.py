import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk, ImageDraw
import os
import math

try:
    import matlab.engine
except ImportError:
    pass # Fails silently if matlab engine is not installed

# -------------------------------------------------------------------------
# Utilities and Helper Functions
# -------------------------------------------------------------------------

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
        try:
            return float(s)
        except Exception:
            pass
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

def get_time_axis(df_local):
    if 'eTIME' in df_local.columns:
        return pd.to_numeric(df_local['eTIME'], errors='coerce')
    else:
        return pd.Series(range(len(df_local)), dtype=float)

def read_m_file_to_df(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            if '=' in line:
                parts = line.split('=', 1)
                key = parts[0].strip()
                value = parts[1].strip().split(';', 1)[0]
                comments = parts[1].strip().split(';', 1)[1] if len(parts[1].strip().split(';', 1)) > 1 else ""
                comments = comments.strip().split('% ', 1)[1] if len(comments.strip().split('% ', 1)) > 1 else comments.strip()
                group = ''
                if 'pems' in key.lower(): group = 'PEMS'
                elif 'sd' in key.lower(): group = 'SD'
                elif 'bins' in key.lower(): group = 'Bins'
                elif 'log' in key.lower(): group = 'Log'
                elif 'import' in key.lower(): group = 'Import'
                elif 'dyno' in key.lower(): group = 'Dyno'
                elif 'sensors' in key.lower(): group = 'Sensors'
                elif 'trace' in key.lower(): group = 'Trace'
                elif 'gps' in key.lower(): group = 'GPS'
                elif 'can' in key.lower(): group = 'CAN'
                elif 'fuel' in key.lower(): group = 'Fuel'
                elif 'display' in key.lower(): group = 'Display'
                elif 'none' in key.lower(): group = 'None'
                else: group = 'Other'  
                data.append({'Variable': key, 'Value': value, 'Comments': comments, 'Group': group})
    df = pd.DataFrame(data)
    return df

def read_mlx_content(mlx_file_path):
    print("Starting MATLAB engine...")
    try:
        eng = matlab.engine.start_matlab()
        abs_path = os.path.abspath(mlx_file_path)
        temp_m_file = abs_path.replace('.mlx', '_converted.m')
        print(f"Converting {mlx_file_path} to {temp_m_file}...")
        eng.export(abs_path, temp_m_file, nargout=0)
        with open(temp_m_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {e}"
    finally:
        try: eng.quit()
        except: pass

class ZoomManager:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax
        self.base_scale = 1.1
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

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
        if event.inaxes != self.ax: return
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
            try: m.remove()
            except Exception: pass
        self.markers, self.elements = [], []

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class IconFactory:
    def __init__(self, icon_size=(40, 30)):
        self.size = icon_size
        self.colors = {
            "Folder":  {"fill": "#ffe680", "border": "#E8B931", "text": "#D7AA46"},
            "Read":  {"fill": "#ffffff", "border": "#0078d4", "text": "#0078d4"},
            "Truck":  {"fill": "#73ec8e", "border": "#107c10", "text": "#D7AA46"},
            "Figure":  {"fill": "#73ec8e", "border": "#107c10", "text": "#D7AA46"},
            "Folder_24":  {"fill": "#FFFCE4", "border": "#825F19", "text": "#D7AA46"},
            "import":     {"fill": "#FFFFFF", "border": "#404040", "text": "#32C832"},
            "PEMSreport": {"fill": "#FFFFFF", "border": "#2850A0", "text": "#2850A0"},
            "PDFreport":  {"fill": "#FFFFFF", "border": "#E02020", "text": "#E02020"}
        }
        (self.icon_Folder, self.icon_Read, self.icon_Truck, self.icon_Figure, self.icon_Folder_24, 
         self.icon_import, self.icon_PEMSreport, self.icon_PDFreport) = self.generate_all_icons()

    def generate_all_icons(self):
        f = self.colors["Folder"]
        self.icon_Folder = self.create_icon("Folder", f["fill"], f["border"], f["text"], self.size)
        f = self.colors["Read"]
        self.icon_Read = self.create_icon("Read", f["fill"], f["border"], f["text"], self.size)
        f = self.colors["Truck"]
        self.icon_Truck = self.create_icon("Truck", f["fill"], f["border"], f["text"], self.size)
        f = self.colors["Figure"]
        self.icon_Figure = self.create_icon("Figure", f["fill"], f["border"], f["text"], self.size)
        f = self.colors["Folder_24"]
        self.icon_Folder_24 = self.create_icon("Folder_24", f["fill"], f["border"], f["text"], self.size)
        i = self.colors["import"]
        self.icon_import = self.create_icon("import", i["fill"], i["border"], i["text"], self.size)
        r = self.colors["PEMSreport"]
        self.icon_PEMSreport = self.create_icon("PEMSreport", r["fill"], r["border"], r["text"], self.size)
        p = self.colors["PDFreport"]
        self.icon_PDFreport = self.create_icon("PDFreport", p["fill"], p["border"], p["text"], self.size)
        return self.icon_Folder, self.icon_Read, self.icon_Truck, self.icon_Figure, self.icon_Folder_24, self.icon_import, self.icon_PEMSreport, self.icon_PDFreport

    def create_icon(self, icon_type, fill_color, border_color, text_color, size):
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        w, h = size

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
        elif icon_type == "Folder_24":
            draw.rectangle([4, 4, 15, 8], fill=text_color, outline=border_color) 
            draw.rectangle([4, 7, 34, 24], fill=text_color, outline=border_color)
            draw.rectangle([4, 11, 34, 24], fill=fill_color, outline=border_color)
        elif icon_type in ["PEMSreport", "PDFreport"]:
            coords = [(10, 2), (24, 2), (30, 8), (30, 26), (10, 26)]
            draw.polygon(coords, fill=fill_color, outline=border_color)
            for y in range(12, 24, 4):
                draw.line([(14, y), (26, y)], fill=text_color, width=1)
            if icon_type == "PDFreport":
                draw.rectangle([13, 19, 27, 23], fill=text_color)
        elif icon_type == "import":
            draw.rectangle([6, 18, 34, 26], fill=fill_color, outline=border_color)
            draw.rectangle([17, 4, 23, 14], fill=text_color, outline=border_color)
            draw.polygon([(12, 14), (28, 14), (20, 21)], fill=text_color, outline=border_color)

        return ImageTk.PhotoImage(img)

# -------------------------------------------------------------------------
# GUI Class
# -------------------------------------------------------------------------
class PEMSAnalysisGUI(object):
    def __init__(self, root):
        self.root = root
        self.root.title("PEMS Analysis GUI")
        
        # Scaling and Resolution adjustments
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        if height >= 2160: 
            self.default_font = ("Arial", 14)
            self.big_bold_font = ("Arial", 30, "bold")
            self.tabs_bold_font = ("Arial", 14, "bold")
            self.root.geometry("600x700")
        else:
            self.default_font = ("Arial", 12)
            self.big_bold_font = ("Arial", 20, "bold")
            self.tabs_bold_font = ("Arial", 12, "bold")
            self.root.geometry("600x750")

        self.root.option_add("*Font", self.default_font)
        
        # Load Icons
        factory = IconFactory((40, 30))
        self.icon_folder = factory.icon_Folder_24
        self.icon_truck = factory.icon_Truck
        self.icon_figure = factory.icon_Figure
        self.icon_import = factory.icon_import
        self.icon_PEMSreport = factory.icon_PEMSreport
        
        # Variables
        self.input_file_dir_checked = tk.BooleanVar(value=False)
        self.pre_select_checked = tk.BooleanVar(value=False)
        self.alignment_checked = tk.BooleanVar(value=False)
        self.report_checked = tk.BooleanVar(value=True) # Check Report by default
        self.align_val_var = tk.StringVar()
        
        self.df = pd.DataFrame()
        self.df_summary = pd.DataFrame()
        self.obd_df = pd.DataFrame()
        self.obd_df_summary = pd.DataFrame()
        self.df_options = pd.DataFrame()
        self.df_report = pd.DataFrame()
        
        self.columns_row = None
        self.vars_row = None
        self.units_row = None
        
        self.selected_columns_list = []
        
        # Tabs Style with Blue Font Color
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook.Tab", font=self.tabs_bold_font, foreground="blue")
        
        self.tab_control = ttk.Notebook(root)
        self.tab_main = ttk.Frame(self.tab_control)
        self.tab_options = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_main, text='Main')
        self.tab_control.add(self.tab_options, text='Options/Report')
        self.tab_control.pack(expand=1, fill="both")
        
        self.setup_main_tab()
        self.setup_options_tab()

    def setup_main_tab(self):
        # 1. PEMS File
        frame_pems = tk.Frame(self.tab_main)
        frame_pems.pack(fill="x", padx=10, pady=(5, 0))
        tk.Label(frame_pems, text="PEMS File").pack(side=tk.LEFT)
        self.ent_pems = tk.Entry(frame_pems)
        self.ent_pems.pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 0))
        self.btn_select = tk.Button(frame_pems, image=self.icon_folder, command=self.read_file)
        self.btn_select.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.btn_select, "Select a file")

        # 2. Checkboxes
        frame_checks = tk.Frame(self.tab_main)
        frame_checks.pack(fill="x", padx=10, pady=5)
        self.chk_input_file_dir = tk.Checkbutton(frame_checks, text="Process all CSV files in a Folder", variable=self.input_file_dir_checked)
        self.chk_input_file_dir.pack(side="left")
        self.chk_pre_select = tk.Checkbutton(frame_checks, text="Display Selected Data Fields only", variable=self.pre_select_checked, command=self.refresh_columns_listbox)
        self.chk_pre_select.pack(side="left", padx=20)

        # 3. Data Fields Listbox
        tk.Label(self.tab_main, text="Data Fields").pack(anchor="w", padx=10)
        frame_listbox = tk.Frame(self.tab_main)
        frame_listbox.pack(fill="x", padx=10, pady=5)
        self.scroll_cols = tk.Scrollbar(frame_listbox, orient="vertical")
        self.columns_listbox = tk.Listbox(frame_listbox, height=10, selectmode="multiple", yscrollcommand=self.scroll_cols.set, exportselection=False)
        self.scroll_cols.config(command=self.columns_listbox.yview)
        self.columns_listbox.pack(side="left", fill="x", expand=True)
        self.scroll_cols.pack(side="right", fill="y")
        self.columns_listbox.bind("<<ListboxSelect>>", self.on_column_select)

        # 4. Alignment & Format Listboxes
        frame_lists_container = tk.Frame(self.tab_main)
        frame_lists_container.pack(fill="x", padx=10, pady=5)
        
        frame_align = tk.Frame(frame_lists_container)
        frame_align.pack(side="left", fill="both", expand=True, padx=(0, 5))
        tk.Label(frame_align, text="Time Alignment").pack(anchor="w")
        align_scroll = tk.Scrollbar(frame_align, orient="vertical")
        self.align_listbox = tk.Listbox(frame_align, height=5, selectmode="single", yscrollcommand=align_scroll.set, exportselection=False)
        self.align_listbox.pack(side="left", fill="x", expand=True)
        align_scroll.config(command=self.align_listbox.yview)
        align_scroll.pack(side="right", fill="y")
        align_items = ['Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', 'Total Current']
        for item in align_items: self.align_listbox.insert(tk.END, item)
        self.align_listbox.selection_set(0) # Pre-select 'Vehicle Speed'

        frame_format = tk.Frame(frame_lists_container)
        frame_format.pack(side="left", fill="both", expand=True, padx=(5, 0))
        tk.Label(frame_format, text="Data Format").pack(anchor="w")
        format_scroll = tk.Scrollbar(frame_format, orient="vertical")
        self.data_format_listbox = tk.Listbox(frame_format, height=5, selectmode="single", yscrollcommand=format_scroll.set, exportselection=False)
        self.data_format_listbox.pack(side="left", fill="x", expand=True)
        format_scroll.config(command=self.data_format_listbox.yview)
        format_scroll.pack(side="right", fill="y")
        format_items = ['EPA PEMS', 'EPA Dyno', 'EPA BEV', 'FEV PEMS']
        for item in format_items: self.data_format_listbox.insert(tk.END, item)
        self.data_format_listbox.selection_set(0) # Pre-select 'EPA PEMS'

        # 5. Alignment and Report Checkboxes
        frame_ar_checks = tk.Frame(self.tab_main)
        frame_ar_checks.pack(fill="x", padx=10, pady=5)
        self.chk_alignment = tk.Checkbutton(frame_ar_checks, text="Alignment", variable=self.alignment_checked, command=self.toggle_obd_section)
        self.chk_alignment.pack(side="left")
        self.chk_report = tk.Checkbutton(frame_ar_checks, text="Report", variable=self.report_checked)
        self.chk_report.pack(side="left", padx=20)

        # 6. OBD File
        frame_obd = tk.Frame(self.tab_main)
        frame_obd.pack(fill="x", padx=10, pady=5)
        self.lbl_obd = tk.Label(frame_obd, text="OBD File")
        self.lbl_obd.pack(side=tk.LEFT)
        self.ent_obd = tk.Entry(frame_obd, state='disabled')
        self.ent_obd.pack(side=tk.LEFT, fill='x', expand=True, padx=(5, 0))
        ToolTip(self.ent_obd, "Press a OBD button to select an OBD/HEMDATA file")
        self.btn_obd = tk.Button(frame_obd, image=self.icon_truck, command=self.select_obd_file, state='disabled')
        self.btn_obd.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.btn_obd, "Select OBD file")

        # 7. Check Alignment Frame (Expanded Left/Right Layout)
        self.frame_check_align = tk.Frame(self.tab_main)
        self.frame_check_align.pack(fill="x", padx=10, pady=10)
        
        self.btn_check_align = tk.Button(self.frame_check_align, text="Check Alignment", bg="#FF99FF", command=self.plot_check_alignment)
        # Pack left-most item first
        self.btn_check_align.pack(side="left", anchor="w")
        ToolTip(self.btn_check_align, "Check/Plot Alignment")
        
        self.btn_plot = tk.Button(self.frame_check_align, image=self.icon_figure, state='disabled', command=self.check_alignment_view)
        # Pack right-most item second, before the expanding center
        self.btn_plot.pack(side="right", anchor="e")
        ToolTip(self.btn_plot, "Plot Alignments")
        
        self.ent_align_input = tk.Entry(self.frame_check_align, width=10, textvariable=self.align_val_var, state='disabled')
        # Fill the remaining space between the two buttons
        self.ent_align_input.pack(side="left", fill="x", expand=True, padx=(10, 10))
        ToolTip(self.ent_align_input, "Type Alignment Values to OBD")
        self.align_val_var.trace_add("write", self.update_plot_button_state)

        # 8. RUN Button
        self.btn_run = tk.Button(self.tab_main, text="RUN", font=self.big_bold_font, bg="lightblue", fg="black", command=self.run_analysis)
        self.btn_run.pack(pady=20, fill="x", padx=40)

        # Update widths and alignment
        self.root.update_idletasks()
        try:
            self.ent_pems.config(width=50) # Tightly fit horizontally logic
        except Exception:
            pass

    def setup_options_tab(self):
        # Apply bold font to elements in this tab
        bold_font = ("Arial", 12, "bold")
        
        # 1. Options/Controls Import
        frame_opt_top = tk.Frame(self.tab_options)
        frame_opt_top.pack(fill="x", padx=10, pady=10)
        tk.Label(frame_opt_top, text="Options/Controls:", font=bold_font, fg="black").pack(side="left")
        self.ent_options_dir = tk.Entry(frame_opt_top)
        self.ent_options_dir.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_import = tk.Button(frame_opt_top, image=self.icon_import, command=self.import_options_folder)
        self.btn_import.pack(side="left")

        # 2. Options Listbox
        tk.Label(self.tab_options, text="Options Lists", font=bold_font, fg="black").pack(anchor="w", padx=10)
        self.options_listbox = tk.Listbox(self.tab_options, height=10, selectmode="single", exportselection=False)
        self.options_listbox.pack(fill="x", padx=10, pady=(0, 10))
        self.options_listbox.bind("<Double-Button-1>", self.on_option_double_click)

        # 3. Separator
        sep_canvas = tk.Canvas(self.tab_options, height=2, bg="blue", highlightthickness=0)
        sep_canvas.pack(fill="x", padx=10, pady=10)

        # 4. Report Format
        frame_rep_fmt = tk.Frame(self.tab_options)
        frame_rep_fmt.pack(fill="x", padx=10, pady=5)
        self.lbl_report_fmt = tk.Label(frame_rep_fmt, text="Report Format:", font=bold_font, fg="black")
        self.lbl_report_fmt.pack(side="left")
        self.ent_report_format = tk.Entry(frame_rep_fmt)
        self.ent_report_format.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_format = tk.Button(frame_rep_fmt, image=self.icon_PEMSreport, command=self.load_report_formats)
        self.btn_format.pack(side="left")

        # 5. Report PDF Listbox
        tk.Label(self.tab_options, text="Report PDF", font=bold_font, fg="black").pack(anchor="w", padx=10)
        self.reportPEMS_listbox = tk.Listbox(self.tab_options, height=10, selectmode="single", exportselection=False)
        self.reportPEMS_listbox.pack(fill="x", padx=10, pady=(0, 10))
        self.reportPEMS_listbox.bind("<Double-Button-1>", self.on_reportPEMS_double_click)

    # --- UI Logic Methods ---
    def toggle_obd_section(self):
        state = 'normal' if self.alignment_checked.get() else 'disabled'
        self.ent_obd.config(state=state)
        self.btn_obd.config(state=state)
        self.update_plot_button_state()

    def update_plot_button_state(self, *args):
        obd_file = self.ent_obd.get()
        align_checked = self.alignment_checked.get()
        if align_checked and obd_file:
            self.ent_align_input.config(state='normal')
        else:
            self.ent_align_input.config(state='disabled')
            
        if self.align_val_var.get().strip():
            self.btn_plot.config(state='normal')
        else:
            self.btn_plot.config(state='disabled')

    def on_column_select(self, event):
        if not self.pre_select_checked.get():
            selection = self.columns_listbox.curselection()
            self.selected_columns_list = [self.columns_listbox.get(i) for i in selection]

    def refresh_columns_listbox(self, event=None):
        self.columns_listbox.delete(0, tk.END)
        if not self.pre_select_checked.get():
            if not self.df.empty:
                for col in self.df.columns:
                    self.columns_listbox.insert(tk.END, col)
                    if col in self.selected_columns_list:
                        idx = self.columns_listbox.size() - 1
                        self.columns_listbox.selection_set(idx)
        else:
            for col in self.selected_columns_list:
                self.columns_listbox.insert(tk.END, col)
                self.columns_listbox.selection_set(tk.END)

    # --- Data Processing Methods ---
    def read_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path: return
        
        self.columns_listbox.delete(0, tk.END)

        self.ent_pems.delete(0, tk.END)
        self.ent_pems.insert(0, file_path)

        try:
            self.df = pd.read_csv(file_path, encoding='utf-8', low_memory=False, skiprows=0, header=0)
            
            # Remove Not Available or Unnamed
            cols = [c for c in self.df.columns if "Not Available" not in str(c) and "Unnamed" not in str(c)]
            self.df = self.df[cols]
            
            self.df = ensure_eTIME(self.df)
            
            if 'eTIME' not in self.df.columns:
                self.df.insert(1, 'eTIME', None)
                self.df.loc[0, 'eTIME'] = 'eTIME'
                self.df.loc[1, 'eTIME'] = 's'
                
            self.columns_row = self.df.columns
            self.vars_row = self.df.loc[0, :]
            self.units_row = self.df.loc[1, :]
            
            self.df = self.df.loc[2:, :]
            
            # Summary Information Splitting
            first_col = self.df.columns[0]
            try:
                summary_row_idx = pd.Index(self.df[first_col]).get_loc("Summary Information:")
                if isinstance(summary_row_idx, np.ndarray):
                    summary_row_idx = np.where(summary_row_idx)[0][0]
                self.df_summary = self.df.iloc[summary_row_idx:].copy()
                out_csv = file_path.replace(".csv", "_summary.csv")
                self.df_summary.to_csv(out_csv, index=False)
                
                self.df = self.df.loc[:summary_row_idx-1, :].copy()
            except KeyError:
                pass
                
            pre_select_columns = [
                'eTIME', 'Gas Path', 'Catalyst Temperature', 'Limit Adjusted iSCB_RH', 'Ambient Pressure', 
                'Limit Adjusted iSCB_LAT', 'Load Percent', 'Limit Adjusted iCOOL_TEMP', 'Engine RPM', 
                'Vehicle Speed', 'Mass Air Flow Rate', 'Catalyst Temp. 1-1', 'F/A Equiv. Ratio', 
                'Engine Fuel Rate', 'Eng. Exh. Flow Rate', 'GPS Latitude', 'GPS Longitude', 
                'Limit Adjusted iGPS_ALT', 'Limit Adjusted iGPS_GROUND_SPEED', 'Fuel Rate', 
                'Instantaneous Fuel Flow', 'Derived Engine Torque.1', 'Derived Engine Power.1', 
                'Instantaneous Mass CO2', 'Instantaneous Mass CO', 'Instantaneous Mass NO', 
                'Instantaneous Mass NO2', 'Instantaneous Mass NOx', 'Corrected Instantaneous Mass NOx', 
                'Instantaneous Mass HC', 'Instantaneous Mass CH4', 'Instantaneous Mass NMHC', 
                'Instantaneous Mass O2', 'Air/Fuel Ratio at stoichiometry', 'Air/Fuel Ratio of Sample', 
                'Lambda', 'Ambient Temperature', 'AMB Ambient Temperature', 'Brake Specific Fuel Consumption', 'Mass Air Flow Rate.1'
            ]
            
            self.selected_columns_list = [c for c in pre_select_columns if c in self.df.columns]
            
            self.refresh_columns_listbox()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")

    def select_obd_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path: return

        self.ent_obd.config(state='normal')
        self.ent_obd.delete(0, tk.END)
        self.ent_obd.insert(0, file_path)
        
        try:
            tmp = pd.read_csv(file_path, encoding='utf-8', low_memory=False, skiprows=0, header=0)
            cols = [c for c in tmp.columns if "Not Available" not in str(c) and "Unnamed" not in str(c)]
            tmp = tmp[cols]

            tmp = ensure_eTIME(tmp)

            if 'eTIME' not in tmp.columns:
                tmp.insert(1, 'eTIME', None)
                tmp.loc[0, 'eTIME'] = 'eTIME'
                tmp.loc[1, 'eTIME'] = 's'

            columns_row = tmp.columns
            vars_row = tmp.loc[0, :]
            units_row = tmp.loc[1, :]
            
            tmp = tmp.loc[2:, :]
            tmp.dropna(how='all', inplace=True)
            if 'sSTATUS_PATH' in tmp.columns:
                tmp = tmp[tmp['sSTATUS_PATH'] == 'SAMPLE']

            first_col = tmp.columns[0]
            try:
                summary_row_idx = pd.Index(tmp[first_col]).get_loc("Summary Information:")
                if isinstance(summary_row_idx, np.ndarray):
                    summary_row_idx = np.where(summary_row_idx)[0][0]
                self.obd_df_summary = tmp.iloc[summary_row_idx:].copy()
                out_csv = file_path.replace(".csv", "_summary.csv")
                self.obd_df_summary.to_csv(out_csv, index=False)
                
                self.obd_df = tmp.loc[:summary_row_idx-1, :].copy()
            except KeyError:
                self.obd_df = tmp.copy()

            self.update_plot_button_state()
        except Exception as e:
             messagebox.showerror("Error", f"Error reading OBD file: {e}")

    def plot_check_alignment(self):
        sel_idx = self.align_listbox.curselection()
        if not sel_idx:
            messagebox.showwarning("Warning", "Please select a parameter in 'Time Alignment' listbox.")
            return
            
        align_col = self.align_listbox.get(sel_idx)
        
        if plt.get_fignums(): plt.close('all')
        
        data_to_plot = []
        if not self.df.empty and align_col in self.df.columns:
            x_pems = get_time_axis(self.df)
            y_pems = pd.to_numeric(self.df[align_col], errors='coerce')
            data_to_plot.append((x_pems, y_pems, f"PEMS: {align_col}"))
            
        if not self.obd_df.empty and align_col in self.obd_df.columns:
            x_obd = get_time_axis(self.obd_df)
            y_obd = pd.to_numeric(self.obd_df[align_col], errors='coerce')
            data_to_plot.append((x_obd, y_obd, f"OBD: {align_col}"))

        ImageDistanceMeasurer(data_to_plot, align_col)

    def check_alignment_view(self):
        sel_idx = self.align_listbox.curselection()
        if not sel_idx:
            messagebox.showwarning("Warning", "Please select a parameter in 'Time Alignment' listbox.")
            return
        align_col = self.align_listbox.get(sel_idx)
        
        self.plot_alignment(
            self.ent_pems.get(),
            self.ent_obd.get(),
            align_col
        )

    def plot_alignment(self, pems_file, obd_file, align_col):
        try:
            align_val = float(self.align_val_var.get())
        except ValueError:
            messagebox.showerror("Error", "Alignment value must be a number.")
            return
            
        if plt.get_fignums(): plt.close('all')
        fig, ax = plt.subplots(figsize=(10, 6))

        if not self.df.empty and align_col in self.df.columns:
            x_pems = get_time_axis(self.df)
            y_pems = pd.to_numeric(self.df[align_col], errors='coerce')
            ax.plot(x_pems, y_pems, label=f"PEMS: {align_col}", linewidth=1)

        if not self.obd_df.empty and align_col in self.obd_df.columns:
            x_obd = get_time_axis(self.obd_df)
            y_obd = pd.to_numeric(self.obd_df[align_col], errors='coerce')
            ax.plot(x_obd + align_val, y_obd, '--', label=f"OBD (Shifted {align_val}): {align_col}", linewidth=1.5)

        ax.set_xlabel("Time (s)")
        ax.set_ylabel(align_col)
        ax.set_title(f"Alignment Verification: {align_col}")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        
        ZoomManager(fig, ax)
        plt.show()

    def run_analysis(self):
        print("--- RUN ANALYSIS ---")
        print(f"OBD File: {self.ent_obd.get()}")
        print(f"PEMS File: {self.ent_pems.get()}")
        print(f"Alignment Checked: {self.alignment_checked.get()}")
        print(f"Report Checked: {self.report_checked.get()}")
        print(f"Input_file_dir Checked: {self.input_file_dir_checked.get()}")
        print(f"Alignment Input: {self.ent_align_input.get()}")
        if 'Vehicle Speed' in self.df.columns:
            print(f"Index of 'Vehicle Speed' in df.columns: {list(self.df.columns).index('Vehicle Speed')}")
        else:
            print("'Vehicle Speed' not found in df.columns")
        print("--------------------")

    # --- Options Tab Methods ---
    def import_options_folder(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.ent_options_dir.delete(0, tk.END)
        self.ent_options_dir.insert(0, folder)
        
        self.options_listbox.delete(0, tk.END)
        for f in os.listdir(folder):
            if f.endswith(('.xlsx', '.xls', '.m', '.mlx')):
                self.options_listbox.insert(tk.END, f)

    def on_option_double_click(self, event):
        sel = self.options_listbox.curselection()
        if not sel: return
        filename = self.options_listbox.get(sel)
        path = os.path.join(self.ent_options_dir.get(), filename)

        try:
            if filename.endswith(('.xlsx', '.xls')) and "RDE_Settings_" in filename:
                self.df_options = pd.read_excel(path, sheet_name="Settings")
                out_csv = os.path.splitext(path)[0] + "_Settings.csv"
                self.df_options.to_csv(out_csv, index=False)
                messagebox.showinfo("Saved", f"Loaded Settings and saved to:\n{out_csv}")
            elif filename.endswith('.m'):
                df_m = read_m_file_to_df(path)
                out_csv = path.replace('.m', '.csv')
                df_m.to_csv(out_csv, index=False)
                messagebox.showinfo("Saved", f"Loaded M and saved to:\n{out_csv}")
            elif filename.endswith('.mlx'):
                content = read_mlx_content(path)
                out_txt = path.replace('.mlx', '.txt')
                with open(out_txt, "w", encoding="utf-8") as text_file:
                    text_file.write(content)
                messagebox.showinfo("Saved", f"Loaded MLX and saved to:\n{out_txt}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process options file:\n{e}")

    def load_report_formats(self):
        folder = filedialog.askdirectory()
        if not folder: return
        self.ent_report_format.delete(0, tk.END)
        self.ent_report_format.insert(0, folder)
        
        self.reportPEMS_listbox.delete(0, tk.END)
        for f in os.listdir(folder):
            if f.endswith(('.xlsx', '.xls', '.m', '.mlx')):
                self.reportPEMS_listbox.insert(tk.END, f)

    def on_reportPEMS_double_click(self, event):
        sel = self.reportPEMS_listbox.curselection()
        if not sel: return
        filename = self.reportPEMS_listbox.get(sel)
        folder = self.ent_report_format.get().strip()
        path = os.path.join(folder, filename)

        try:
            if filename.lower().endswith(('.xlsx', '.xls')):
                xls = pd.ExcelFile(path)
                if not xls.sheet_names:
                    messagebox.showwarning("Excel", "No sheets found.")
                    return
                first_sheet = xls.sheet_names[0]
                df_xls = pd.read_excel(xls, sheet_name=first_sheet)
                out_csv = f"{os.path.splitext(path)[0]}_{first_sheet}.csv"
                df_xls.to_csv(out_csv, index=False)
                self.df_report = df_xls
                messagebox.showinfo("Saved", f"Loaded Excel (sheet: {first_sheet}) and saved to:\n{out_csv}")
            else:
                messagebox.showwarning("Unsupported", "Options integration for reports handles xlsx currently based on your logic.")
        except Exception as e:
            messagebox.showerror("Read Error", f"Failed to read file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PEMSAnalysisGUI(root)
    root.mainloop()