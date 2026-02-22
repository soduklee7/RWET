Generate a whole python code by refining the attached code to address the following AI prompts.
Keep the existing variable names and function names in the attached code, and add the new code to the existing code to meet GUI requirements of the AI prompt.
Spent two-days for this code refinement. But still the code is not as good as hand-coding.

Updated Master AI Prompt for PEMS Analysis GUI
Role & Objective:
Act as an expert Python GUI developer. Create a Tkinter application using ttk.Notebook with a colorful, professional interface (using the 'clam' theme). Provide the complete, fully functional Python code incorporating the following detailed requirements without skipping any sections.

1. General Setup & Scaling Logic:

Imports: tkinter, ttk, filedialog, messagebox, pandas, numpy, matplotlib.pyplot, FigureCanvasTkAgg, NavigationToolbar2Tk (from matplotlib.backends.backend_tkagg), PIL (Image, ImageDraw, ImageTk), os, math, and matlab.engine (wrapped in a try-except block).

Resolution Scaling: Add the following exact logic to adjust font sizes and window sizes based on screen resolution:

Python
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
Tabs Theme: Create 2 tabs: "Main" and "Options/Report". Configure the tab font using self.tabs_bold_font and set the text color to blue (style.configure("TNotebook.Tab", font=self.tabs_bold_font, foreground="blue")).

2. Procedural Icons & Tooltips:

IconFactory: Create an internal class to procedurally draw icons using Pillow (ImageDraw) so no external .png files are needed. Create distinct color icons for: Folder (gold/yellow), Truck (dark/green), Figure/Plot (purple/lines), Import (green arrow/tray), and Report (white document with dog-ear).

ToolTips: Implement a ToolTip class to display custom hover text over buttons and entry boxes.

3. "Main" Tab UI Layout:

PEMS File Row: Label "PEMS File", an expanding Entry box, and a button using the Folder icon. Tooltips: "Press a PEMS button to select a PEMS file" and "Select a file".

Directory Checkboxes: Two horizontal checkboxes: "Process all CSV files in a Folder" and "Display Selected Data Fields only". Bind the latter to self.refresh_columns_listbox.

Data Fields Listbox: 10-row vertically scrollable listbox allowing multiple selections (exportselection=False).

Alignment & Format Listboxes: Side-by-side inside a frame.

Time Alignment: 5-row single-select. Insert: 'Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', 'Total Current'. Pre-select 'Vehicle Speed'.

Data Format: 5-row single-select. Insert: 'EPA PEMS', 'EPA Dyno', 'EPA BEV', 'FEV PEMS'. Pre-select 'EPA PEMS'.

Alignment/Report Checkboxes: Horizontally placed. "Alignment" (default unchecked, toggles OBD UI state). "Report" (default checked).

OBD File Row: Label "OBD File", expanding Entry box, and button (Truck icon). Disabled by default. Tooltips: "Press a OBD button to select an OBD/HEMDATA file" and "Select OBD file".

Check Alignment Row (Specific Layout Rule): * Use a frame (fill="x").

Left side (pack(side="left", anchor="w")): "Check Alignment" button with light magenta (#FF99FF) background. Binds to plot_check_alignment.

Right side (pack(side="right", anchor="e")): "Plot" button (Figure icon). Disabled by default. Binds to check_alignment_view.

Middle (pack(side="left", fill="x", expand=True)): self.ent_align_input Entry box. Trace its variable to enable the "Plot" button when text is entered.

RUN Button: Large, bold (self.big_bold_font), light blue background, black text, spanning the tab width. Binds to run_analysis().

4. "Options/Report" Tab UI Layout:

Font Rule: For the specific labels "Options/Controls:", "Options Lists", "Report Format:", and "Report PDF", use a bold font ("Arial", 12, "bold") and set the text color to black (fg="black").

Options/Controls Row: Black bold label, expanding Entry box, and button (Import icon). Binds to import_options_folder.

Options Listbox: 10-row single-select scrollable listbox. Binds double-click to on_option_double_click.

Separator: Solid blue canvas line horizontally spanning the tab.

Report Format Row: Black bold label, expanding Entry box, and button (Report icon). Binds to load_report_formats.

Report PDF Listbox: 10-row single-select scrollable listbox. Binds double-click to on_reportPEMS_double_click.

5. Global Data Handling Functions:

Include exact implementations for ensure_eTIME(df_local), get_time_axis(df_local), read_m_file_to_df(file_path), read_mlx_content(mlx_file_path) (using matlab engine export), ZoomManager(fig, ax), and ImageDistanceMeasurer(data_to_plot, align_col).

ensure_eTIME must handle string conversion (hh:mm:s.xxx) to total seconds and insert the 'eTIME' column at index 1 if it doesn't exist.

6. Core GUI Methods:

read_file: Read CSV (utf-8, header=0, low_memory=False). Remove columns containing 'Not Available' or 'Unnamed'. Apply ensure_eTIME. If 'eTIME' missing, insert it. Split the dataframe at the row containing "Summary Information:" in the first column. Save the bottom half to [filename]_summary.csv. Keep the top half in self.df. Define pre_select_columns (containing 40 specific variables like 'eTIME', 'Gas Path', 'Vehicle Speed', etc.) and automatically populate self.selected_columns_list with matches. Call refresh_columns_listbox().

select_obd_file: Similar logic to read_file, but for tmp dataframe. Filter for rows where sSTATUS_PATH == 'SAMPLE'. Split at "Summary Information:" into self.obd_df_summary (save to CSV) and self.obd_df.

refresh_columns_listbox: Check "Display Selected Data Fields only" state. If false, show all columns and highlight tracked selections. If true, clear listbox and insert only the tracked selected_columns_list.

plot_check_alignment & plot_alignment: plot_check_alignment closes previous plots and instantiates ImageDistanceMeasurer passing PEMS and OBD arrays for the selected listbox column. plot_alignment applies the float value from the input entry to shift the OBD x-axis (x_obd + align_val), plotting lines and instantiating ZoomManager.

Options Integration: on_option_double_click processes .xlsx (extracts 'Settings' sheet to CSV), .m (parses to CSV), and .mlx (exports to .txt). on_reportPEMS_double_click extracts the first sheet of an .xlsx file into self.df_report and saves it as a CSV. Wrap all in try/except blocks with messagebox notifications.