import sys
import os
import glob
import tkinter as tk
from tkinter import ttk, messagebox

# Try to import MATLAB Engine (optional but recommended for full functionality)
try:
    import matlab.engine
    HAS_MATLAB = True
except ImportError:
    HAS_MATLAB = False


class ReportMenu(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("reportMenu")
        # Approximate MATLAB UI size
        self.geometry("382x650")
        self.resizable(False, False)

        self.eng = None      # MATLAB engine handle, if available
        self.num_set = 0     # number of datasets
        self.dataset_names = []
        self.report_items = [
            "PEMS LD Quality",
            "PEMS HD Quality",
            "PEMS PM Quality",
            "PEMS LD Emissions",
            "PEMS HD Emissions",
            "PEMS HD Offcycle Bins",
            "Chassis Horiba Dilute",
            "PEMS ForkLift Quality",
            "PEMS ForkLift Emissions",
        ]
        self.report_ids = list(range(1, 10))  # 1..9

        # Build UI
        self._build_ui()

        # Startup function (equivalent to MATLAB startupFcn)
        self._startup()

    def _build_ui(self):
        # Dataset panel
        dataset_frame = ttk.LabelFrame(self, text="Dataset")
        dataset_frame.place(x=1, y=496, width=382, height=155)

        self.list_dataset = tk.Listbox(dataset_frame, exportselection=False)
        self.list_dataset.place(x=29, y=17, width=323, height=104)

        # Report Template panel
        report_frame = ttk.LabelFrame(self, text="Report Template")
        report_frame.place(x=1, y=282, width=382, height=215)

        self.list_report = tk.Listbox(report_frame, exportselection=False)
        for item in self.report_items:
            self.list_report.insert(tk.END, item)
        self.list_report.select_set(0)  # default to 1 (index 0)
        self.list_report.place(x=30, y=17, width=323, height=163)

        # Create Report panel
        create_frame = ttk.LabelFrame(self, text="Create Report")
        create_frame.place(x=1, y=1, width=382, height=166)

        self.delete_png_var = tk.BooleanVar(value=True)
        self.delete_png_checkbox = ttk.Checkbutton(
            create_frame, text="Delete *.png files", variable=self.delete_png_var
        )
        self.delete_png_checkbox.place(x=139, y=102)

        self.create_button = ttk.Button(
            create_frame, text="Create Report", command=self._on_create_report
        )
        self.create_button.place(x=101, y=20, width=188, height=61)

        # PDF File Name panel
        pdf_frame = ttk.LabelFrame(self, text="PDF File Name (no extension)")
        pdf_frame.place(x=1, y=166, width=382, height=117)

        self.filename_label = ttk.Label(pdf_frame, text="File Name")
        self.filename_label.place(x=30, y=55)

        self.filename_entry = ttk.Entry(pdf_frame, justify="center")
        self.filename_entry.insert(0, "defaultReport")
        self.filename_entry.place(x=30, y=26, width=323, height=27)

    def _startup(self):
        """
        Equivalent to MATLAB's startupFcn:
        - Acquire numSet and vehData from MATLAB base (if MATLAB engine is present)
        - Populate dataset list
        """
        if not HAS_MATLAB:
            # Fallback: no MATLAB engine. Show placeholder list.
            self.dataset_names = ["empty"]
            self._populate_dataset_list(self.dataset_names)
            return

        try:
            self.eng = matlab.engine.start_matlab()
            # Read numSet from base workspace
            num_set = self.eng.evalin("base", "numSet", nargout=1)
            # MATLAB returns double; interpret truthiness like MATLAB code
            try:
                self.num_set = int(num_set)
            except Exception:
                self.num_set = 0

            if self.num_set:
                # Get dataset names as cellstr(char(vehData.name))
                # This returns a list[str] in Python
                names = self.eng.evalin("base", "cellstr(char(vehData.name))", nargout=1)
                self.dataset_names = [str(s) for s in names]
                self._populate_dataset_list(self.dataset_names)
                # Select first item
                if self.list_dataset.size() > 0:
                    self.list_dataset.select_set(0)
            else:
                self.dataset_names = ["empty"]
                self._populate_dataset_list(self.dataset_names)

        except Exception as e:
            self.dataset_names = ["empty"]
            self._populate_dataset_list(self.dataset_names)
            messagebox.showerror(
                "MATLAB Engine Error",
                f"Failed to initialize MATLAB engine or read base variables.\n\n{e}",
            )

    def _populate_dataset_list(self, items):
        self.list_dataset.delete(0, tk.END)
        for item in items:
            self.list_dataset.insert(tk.END, item)

    def _mquote(self, s: str) -> str:
        """
        Escape a Python string to a MATLAB single-quoted string.
        """
        return s.replace("'", "''")

    def _on_create_report(self):
        """
        Equivalent to CreateReportButtonPushed.
        Reads GUI selections, calls the selected report(s),
        and optionally deletes *.png files.
        """
        # Validate selection
        sel = self.list_report.curselection()
        if not sel:
            messagebox.showwarning("Selection required", "Please select a report template.")
            return
        report_id = self.report_ids[sel[0]]

        # Dataset index: MATLAB code uses 1-based
        ds_sel = self.list_dataset.curselection()
        if not ds_sel:
            # If empty dataset was displayed
            messagebox.showwarning("Dataset required", "Please select a dataset.")
            return
        set_idx = ds_sel[0] + 1  # 1-based like MATLAB

        file_name = self.filename_entry.get().strip()
        if not file_name:
            messagebox.showwarning("File name required", "Please enter a PDF file name (without extension).")
            return

        png_flag = self.delete_png_var.get()

        # If MATLAB engine is available, forward calls to MATLAB
        if HAS_MATLAB and self.eng is not None:
            try:
                # Build MATLAB commands to evaluate in base workspace.
                # We reuse existing vehData and udp in base, as in the MATLAB app.
                fn_m = self._mquote(file_name)

                if report_id == 1:
                    cmd = f"reportPEMS_LDQuality({set_idx}, '{fn_m}', vehData, udp);"
                elif report_id == 2:
                    cmd = f"reportPEMS_HDQuality({set_idx}, '{fn_m}', vehData, udp);"
                elif report_id == 3:
                    cmd = f"reportPEMS_PMQuality({set_idx}, '{fn_m}', vehData, udp);"
                elif report_id == 4:
                    cmd = f"reportPEMS_LDEmissions({set_idx}, '{fn_m}', vehData, udp);"
                elif report_id == 5:
                    cmd = f"reportPEMS_HDEmissions({set_idx}, '{fn_m}', vehData, udp);"
                elif report_id == 6:
                    # [binData, vehData] = dieselBinCalc(...);
                    # testReportBin(..., binData)
                    # assignin('base','binData',binData)
                    cmd = (
                        f"[binData, vehData] = dieselBinCalc({set_idx}, vehData, udp);"
                        f"testReportBin({set_idx}, '{fn_m}', vehData, udp, binData);"
                        f"assignin('base','binData',binData);"
                    )
                elif report_id == 7:
                    cmd = f"reportHoriba_Dilute({set_idx}, '{fn_m}', vehData, udp);"
                elif report_id == 8:
                    cmd = f"reportPEMS_ForkLiftQuality({set_idx}, '{fn_m}', vehData, udp);"
                elif report_id == 9:
                    cmd = f"reportPEMS_ForkliftEmissions({set_idx}, '{fn_m}', vehData, udp);"
                else:
                    messagebox.showerror("Invalid selection", "Unknown report ID.")
                    return

                self.eng.evalin("base", cmd, nargout=0)

                if png_flag:
                    # Keep MATLAB behavior
                    self.eng.evalin("base", "delete *.png", nargout=0)

                messagebox.showinfo("Success", "Report generation completed.")
            except Exception as e:
                messagebox.showerror(
                    "Report Error",
                    f"An error occurred while generating the report via MATLAB:\n\n{e}",
                )
        else:
            # Fallback: no MATLAB engine. Provide guidance or stubs.
            # If you want to implement pure-Python equivalents, replace these with your own functions.
            try:
                # OPTIONAL: implement your Python-side report generation here
                # For now, we just inform the user.
                messagebox.showwarning(
                    "MATLAB engine not available",
                    "MATLAB Engine for Python is not installed. "
                    "Install and configure it to call your existing MATLAB reports.\n\n"
                    "Alternatively, implement Python-native report-generation functions here."
                )

                # If you still want to delete *.png in the local directory (Python side):
                if png_flag:
                    for p in glob.glob("*.png"):
                        try:
                            os.remove(p)
                        except OSError:
                            pass

            except Exception as e:
                messagebox.showerror("Report Error", f"An error occurred:\n\n{e}")

    def run(self):
        self.mainloop()


def main():
    app = ReportMenu()
    app.run()


if __name__ == "__main__":
    main()