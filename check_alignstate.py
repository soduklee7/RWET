import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
from PIL import Image, ImageTk, ImageDraw

class PEMSAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PEMS Data Analysis")
        self.root.geometry("600x735")
        
        # Variables
        self.Alignment_checked = tk.BooleanVar()
        self.obd_path_var = tk.StringVar()  # Monitors the OBD File path
        self.align_values_var = tk.StringVar()
        
        # Add trace to monitor OBD path changes
        self.obd_path_var.trace_add("write", self.update_widget_states)
        
        self.setup_ui()

    def setup_ui(self):
        self.font_std = ("Segoe UI", 12)
        
        # --- OBD File Section ---
        frame_obd = tk.Frame(self.root)
        frame_obd.pack(padx=20, fill='x', pady=5)
        
        tk.Label(frame_obd, text="OBD File", font=self.font_std).grid(row=0, column=0, sticky='w')
        
        # Linked to self.obd_path_var
        self.ent_obd = ttk.Entry(frame_obd, textvariable=self.obd_path_var, font=self.font_std, state='disabled')
        self.ent_obd.grid(row=1, column=0, sticky='ew', padx=(0, 5))
        
        self.btn_obd = tk.Button(frame_obd, text="OBD", state='disabled', command=self.select_obd)
        self.btn_obd.grid(row=1, column=1)
        frame_obd.columnconfigure(0, weight=1)

        # --- Alignment Controls ---
        frame_align = tk.Frame(self.root)
        frame_align.pack(padx=20, fill='x', pady=10)
        
        self.chk_align = tk.Checkbutton(frame_align, text="Alignment", 
                                        variable=self.Alignment_checked, 
                                        command=self.update_widget_states)
        self.chk_align.pack(side='left')

        self.btn_check = tk.Button(frame_align, text="Check Alignment", bg="#FFD1FF")
        self.btn_check.pack(side='left', padx=10)

        # The target textbox
        self.ent_align_val = ttk.Entry(frame_align, textvariable=self.align_values_var, width=15, state='disabled')
        self.ent_align_val.pack(side='left')

    def select_obd(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            # Setting the var triggers the trace automatically
            self.obd_path_var.set(path)

    def update_widget_states(self, *args):
        """Logic to enable/disable widgets based on Checkbox and Entry content."""
        is_alignment_on = self.Alignment_checked.get()
        is_obd_not_empty = len(self.obd_path_var.get().strip()) > 0

        # Step 1: Handle OBD Widgets (only depend on Checkbox)
        obd_state = 'normal' if is_alignment_on else 'disabled'
        self.ent_obd.config(state=obd_state)
        self.btn_obd.config(state=obd_state)

        # Step 2: Handle Alignment Input (depends on Checkbox AND OBD Content)
        if is_alignment_on and is_obd_not_empty:
            self.ent_align_val.config(state='normal')
        else:
            self.ent_align_val.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = PEMSAnalysisGUI(root)
    root.mainloop()
