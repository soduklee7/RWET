Update Windows11-style, colorful, 3-D-looking 600x700 size 2-tabs which have the "Main" and "Options/Report" in the PEMSAnalysisGUI(object) GUI using tkinter, pillow icons, and default "Arial" font size 12, and the Python code here.
1) Add "from PEMS_GUI_utils import ensure_eTIME, IconFactory, ImageDistanceMeasurer, read_m_file_to_df, read_mlx_content".
Without loading a '.png' file for icons, create the "create_icons" method to create the 40x40 size "folder", "truck", "plot", "import" and "format: icons using Pillow and call the method in the __init__ function.
1) Create a text box with a "PEMS File" label and the "Select" button to select a CSV file in the "Main" tab. 
Display the "Press a PEMS button to select a PEMS file" when placing a mouse pointer on the "PEMS File" text box. 
Display the "Select PEMS file" when placing a mouse pointer on the "Select" button.
Read the selected file using "self.df = pd.read_csv with encoding='utf-8', low_memory=False, skiprows=0, header=0" and skipping first 0 rows in the “read_file” fuction when clicking the " Select " button. 
2)  Replace the "Select" button with the self.icon_folder for a “Folder” large color icon. 
Display the "Select a file" when placing a mouse pointer on the "Select" icon. 
Adjust the width of the "PEMS File" label to tightly fit with the "Select" button horizontally.
Adjust the width of the "self.ent_pems_file" text box to tightly fit with the "btn_select" button horizontally.
3)  Remove columns with "Not Available" or "Unnamed" in the self.df.columns.
4)  Add the following code before assigning columns_row, vars_row and units_row.
if 'eTIME' not in self.df.columns:
self.df.insert(1, 'eTIME', None)
self.df.loc[0, 'eTIME'] = 'eTIME'
self.df.loc[1, 'eTIME'] = 's'
5)  Assign columns_row = self.df.columns, vars_row = self.df.loc[0, :] and units_row = self.df.loc[1, :]. Update self.df = self.df.loc[2:, :].
6)  Create self.df_summary data frame starting from the row that contains the "Summary Information:" in the first column of self.df data frame using the summary_row_idx = pd.Index(self.df[first_col]).get_loc("Summary Information:") in the “read_file” function.
7)  Save self.df_summary using self.df_summary.to_csv(). 
Remove all NaN rows using df.dropna(how='all', inplace=True) and filter only df['Gas Path'] == 'SAMPLE' rows.
8)  Create self.df = self.df.loc[2:summary_row_idx-1, :].copy()
9)  Update the “read_file” fuction by create eTIME by converting hh:mm:s.xxx format data in self.df['TIME] in seconds using the ensure_eTIME(self.df) function after reading the file.
10) Create pre_select_columns = ['eTIME', 'Gas Path', 'Catalyst Temperature', 'Limit Adjusted iSCB_RH', 'Ambient Pressure', 'Limit Adjusted iSCB_LAT', 'Load Percent',  'Limit Adjusted iCOOL_TEMP', 'Engine RPM', 'Vehicle Speed', 'Mass Air Flow Rate', 'Catalyst Temp. 1-1', 'F/A Equiv. Ratio', 'Engine Fuel Rate',  'Eng. Exh. Flow Rate', 'GPS Latitude', 'GPS Longitude', 'Limit Adjusted iGPS_ALT', 'Limit Adjusted iGPS_GROUND_SPEED', 'Fuel Rate', 'Instantaneous Fuel Flow',  'Derived Engine Torque.1', 'Derived Engine Power.1', 'Instantaneous Mass CO2', 'Instantaneous Mass CO', 'Instantaneous Mass NO', 'Instantaneous Mass NO2',  'Instantaneous Mass NOx', 'Corrected Instantaneous Mass NOx', 'Instantaneous Mass HC', 'Instantaneous Mass CH4', 'Instantaneous Mass NMHC', 'Instantaneous Mass O2', 'Air/Fuel Ratio at stoichiometry', 'Air/Fuel Ratio of Sample', 'Lambda', 'Ambient Temperature', 'AMB Ambient Temperature', 'Brake Specific Fuel Consumption', 'Mass Air Flow Rate.1'] in the “read_file” function.
11) Create  pre_select_vars = [ 'eTIME', 'sSTATUS_PATH', 'CatalystTemp', 'iSCB_RH', 'iSCB_LAP', 'iSCB_LAT', 'iENG_LOAD',  'iCOOL_TEMP', 'iENG_SPEED', 'iVEH_SPEED', 'CATEMP11', 'LAMBDA', 'ENG_FUEL_RATE', 'icMASS_FLOWx', 'EXH_RATE',  'iGPS_LAT', 'iGPS_LON', 'iGPS_ALT', 'iGPS_GROUND_SPEED', 'iWfgps', 'iWf', 'iPPTorq', 'iBhp', 'iCALCRT_CO2m', 'iCALCRT_COm', 'iCALCRT_NOm', 'iCALCRT_NO2m', 'iCALCRT_NOxm', 'iCALCRT_kNOxm', 'iCALCRT_HCm', 'iCALCRT_CH4m', 'iCALCRT_NMHCm', 'iCALCRT_O2m', 'AF_Stoich', 'AF_Calc', 'Lambda', 'AmbientTemp', 'AvgTemp.1', 'AmbTemp', 'iBSFC', 'iMAF', 'iMAP' ] in the “read_file” function
12) Create an "Input_file_dir" checkbox labeled "Process all CSV files in a Folder" in the "Main" tab. 
Create the "Input_file_dir_checked" variable to pass the status. 
Create the "pre_selected_columns" checkbox button labeled the “Display Selected Data Fields only” in the "Main" tab. 
Locate an "Input_file_dir" checkbox and the “pre_selected_columns” checkbox horizontally.
13) After clicking the "btn_select" icon, select the pre_select_columns in the columns_listbox.  When you click the “btn_select” button, the items in pre_select_columns are selected in the columns_listbox.
14) Create a 10-row scrollable "columns_listbox" list box labeled the the "Data Fields" in the "Main" tab to display self.df.columns. 
Enable multiple selection in the "columns_listbox" list box by clicking mouse pointers. 
15) Empty the "columns_listbox" list box before clicking the "btn_select" icon. 
Select additional df.columns items in the columns_listbox after clicking the "btn_select" icon. 
When you click the “btn_select” button, the items in pre_select_columns are selected in the columns_listbox.
Adjust the width of the "columns_listbox" list box to tightly fit with the location of the "btn_select" button at the btn_select.winfo_x().
16) Create the “selected_columns_list” list to store additionally selected items in the “columns_listbox” list box. 
Show only the selected_columns_list in the “columns_listbox” list box when the “pre_selected_columns” checkbox is checked. 
Update the refresh_columns_listbox method so that when “Display Selected Data Fields only” is not checked, the listbox shows self.columns_row and then select any items that match selected_columns_list. 
17) Create a 5-row scrollable list boxes labeled the "Time Alignment" in the "Main" tab.  
Create a 5-row scrollable list boxes labeled the "Data Format" in the "Main" tab. 
Locate the "Time Alignment" and the "Data Format" list boxes horizontally.
Display the scrollbar for the "Time Alignment" and the "Data Format" list boxes when the number of items exceeds the visible area.
18) Display the 'Vehicle Speed', 'Engine RPM', 'Exhaust Mass Flow Rate', 'iBAT_CURR', and 'Total Current' in the "Time Alignment" list box. Enable single selection in the list box by clicking a mouse pointer. 
Display the 'EPA PEMS', 'EPA Dyno', 'EPA SD', 'EPA BEV', 'FEV PEMS' and 'Custom' in the "Data Format" list box. Select the 'EPA PEMS' in the "Data Format" list box.
19) Adjust the "Time Alignment" label and "Data Format" label to tightly fit with the "btn_select" button horizontally.
Pre-select the 'Vehicle Speed' in the "Time Alignment" listbox. Pre-select the 'EPA PEMS' in the "Data Format" listbox.
20) Create the "Alignment" and "Report" check boxes just below the "Time Alignment" and "Data Format" list boxes in the "Main" tab.
Check the "Report" check box. Adjust "Alignment" and "Report" check boxes to tightly fit with the "Select" button horizontally.
21) Create a text box with an "OBD File" label just below the "Alignment" and "Report" check boxes in the "Main" tab. 
Display the "Press a OBD button to select an OBD/HEMDATA file" when placing a mouse pointer on the "OBD File" text box.
22) Create an "OBD" button in the "Main" tab. Replace the "OBD" button with the self.icon_truck for a "Truck" icon to select a CSV file. 
Display the "Select OBD file" when placing a mouse pointer on the "OBD" icon. 
Only Enable the "OBD File" text box and "OBD" button when the "Alignment" checkbox is True.
24) Call the select_obd_file function to read the OBD file when clicking the "OBD" button. Read the selected file using 'tmp = pd.read_csv(file, encoding='utf-8', low_memory=False, skiprows=0, header=0)'. Remove columns with "Not Available" or "Unnamed" in the tmp.columns
25) Add the following code before assigning columns_row, vars_row and units_row.
if 'eTIME' not in tmp.columns:
tmp.insert(1, 'eTIME', None)
tmp.loc[0, 'eTIME'] = 'eTIME'
tmp.loc[1, 'eTIME'] = 's'
26) Assign columns_row = tmp.columns, vars_row = tmp.loc[0, :] and units_row = tmp.loc[1, :]. Update tmp = tmp.loc[2:, :]. 
Remove all NaN rows using tmp.dropna(how='all', inplace=True) and filter only tmp['Gas Path'] == 'SAMPLE' rows.
27) Create self.obd_df_summary data frame starting from the row that contains the "Summary Information:" in the first column of tmp data frame using the summary_row_idx = pd.Index(tmp[first_col]).get_loc("Summary Information:") in the “select_obd_file” function.
Create self.obd_df = tmp.loc[2:summary_row_idx-1, :].copy()
28) Save self.obd_df_summary using self.obd_df_summary.to_csv().
29) Convert hh:mm:s.xxx format data in tmp['TIME] in seconds using the ensure_eTIME(self.obd_df) function after reading the file and then add the following code part.
30) Adjust the width of the "OBD File" label, "OBD File" text box and "OBD" button to tightly fit with the "Select" button horizontally.
31) Adjust the width of the "OBD" button to tightly fit with the "btn_select" button horizontally.
32) Create the "“btn_check_align“" button labeled the "Check Alignment" in the "Main" tab. 
Create a “ent_align_input” input textbox next to the "Check Alignment" button in the "Main" tab to input alignment values.
Display the “Check/Plot Alignment” and the "Type Alignment Values to OBD" when placing a mouse pointer on the "Check Alignment" button and 
the “ent_align_input” input textbox respectively. 
Create the “frame_check_align” frame using tk.Frame and pack(fill="x", padx=20, pady=10). 
33) Enable the “ent_align_input“ input textbox if the “btn_check_align” alignment checkbox is True and “OBD File” text box is not empty.
34) Create a "Plot" button in the "Main" tab next to the “ent_align_input“ input textbox to call back the "plot_alignment” function. 
Enable only the "Plot" button when the “ent_align_input“ alignment input textbox is not empty.
35) Replace the "Plot" button labeled “btn_plot” using the self.icon_figure in the following code.
36) Adjust the width of the "Check Alignment" label, "Check Alignment" text box and "Plot" button to tightly fit with the "Select" button horizontally.
Adjust the width of the "ent_align_input" input text box to tightly fit with the "btn_select" button horizontally.
Adjust the width of the "btn_plot" button to tightly fit with the "btn_select" button horizontally.
37) Display the "Plot Alignments" when placing a mouse pointer on the " btn_plot " button.
Adjust the width of the "Check Alignment" text box to tightly fit with the "Plot" button horizontally.
Adjust the width of the "Check Alignment" label, "Check Alignment" text box, and "Plot" button to tightly fit with the "btn_select" button horizontally.
38) Create the "plot_check_alignment" function to plot the selected alignment column in the "align_listbox" list box when clicking the "Check Alignment" button. 
39) Call back the plot_check_alignment when clicking the “btn_check_align“  button.
40) Close all opened figures using “if plt.get_fignums(): plt.close('all')” before calling the ImageDistanceMeasurer class in the “plot_check_alignment” function.
Add zoom and pan functionality to the ImageDistanceMeasurer class to allow users to zoom in and out of the plot using mouse scroll and Ctrl + '+'/'-' keys.
41) Create the “check_alignment_view” function to call back the “plot_alignment” function when clicking the self.btn_plot button. 
self.plot_alignment(
pems_df,
data_to_align,
align_col)
42) Set the "Check Alignment" button with a light magenta-color background to call back "check_alignment()" function with the selected items in the "align_listbox".
43) Add the self.ent_pems.get(), self.ent_obd.get(), self.ent_align_input.get() arguments the plot_alignment function. 
44) Create a "big_bold_font" "Arial" font size 20, black bold font, "RUN" big button with a light blue-color background to call back the "run_analysis()" function in the "Main" tab.
45) Assign Alignment_checked and Report_checked variables to pass the "Alignment" and "Report" Checkbox check status.
47) Fix the _tkinter.TclError: expected integer but got "UI"
48) Enable to select multiple items in both the columns_listbox. Enable to select a single item in the align_listbox.
49) Print the obd_ent, pems_ent, "Alignment", "Report", "Input_file_dir" checkbox status, "Check Alignment" button, align_values_ent textbox values, and the index of 'Vehicle Speed' in df.columns when clicking the "RUN" button. 
Keep current run_analysis() function in the code.
50) Fix automatically deselecting an item in a listbox while selecting an item in another listbox.
51)	Update that converts the GUI to use two tabs labeled “Main” and “Options/Report” a "Arial" BLUE bold font size 12, while preserving all existing functionality. 
The “Main” tab contains PEMS/OBD, "Process all CSV files in a Folder" check box, Data Fields, Alignment, Report checkbox, and RUN controls. Change the “Options/Report” tab using blue color font.
52)	Create a text box labeled the "Options/Controls:" and the "Import" button in the “Options/Report” tab to select a folder directory.
Locate the “Options/Controls:” label, “Options/Controls:” input text box and the “Import” button just above the "options_listbox" list box in the “Options/Report” tab. 
53)	Create a 10-row scrollable "options_listbox" list box labeled “Options Lists” in the “Options/Report” tab to display the Excel and matlab .mlx files in the selected folder. 
Enable single selection in the “Options Lists” list box by clicking a mouse pointer. Locate the "options_listbox" list box just below the “Import” button. 
Create self.df_options for reading data in the “Settings” worksheet of the double-clicked Excel file which contains the “RDE_Settings_” file name. 
Read a matlab .m and .mlx files when double-clicking the .m and .mlx file using the "read_m_file_to_df" function and the "read_mlx_content" function, respectively. 
Save the content of the .m and .mlx files using df.to_csv().
54)	Create a 10-row scrollable "reportPMS_listbox" list box labeled “Report PDF” in the “Options/Report” tab. Enable single selection in the list box by clicking a mouse pointer. 
55)	Create a text box labeled the "Options/Controls:" and the "Import" button in the “Options/Report” tab to select a folder directory.
Adjust the width of the "Options/Controls:" text box to tightly fit with the "Import" button horizontally.
Adjust the width of the "options_listbox" list box to tightly fit with the "Import" button horizontally.
Adjust the width of the "reportPMS_listbox" list box to tightly fit with the "Import" button horizontally.
56)	Draw a blue solid line between the "options_listbox"  and the "reportPMS_listbox" list box.
57)	Create the “lbl_report_fmt” text box labeled “Report Format:”, “self.ent_report_format” input text box and the “self.btn_format” button labeled “Format” to select a folder directory just above the "reportPMS_listbox" list box in the “Options/Report” tab. 
Replace the “self.btn_format” button with the “PEMSreport.png” icon. Display the Excel and “.mlx” matlab files in the "reportPMS_listbox" list box in the selected folder when clicking the “self.btn_format” button.
58)	Remove self.align_map.get(selected_value, selected_value) in the code and set align_col = selected_value.
59)	Locate the “lbl_report_fmt” text box, “self.ent_report_format” input text box and the “self.btn_format” button just above the "reportPMS_listbox" list box in the “Options/Report” tab. 
60)	Change the "Report Format:" label to blue color font and bold font style. Change the "Format" button to the “PEMSreport” icon. 
Display the Excel and “.mlx” matlab files in the "reportPMS_listbox" list box in the selected folder when clicking the “self.btn_format” button.
Adjust the width of the "btn_plot" button to tightly fit with the "btn_select" button horizontally.
Adjust the width of the “ent_align_input“ input textbox to tightly fit with the "btn_plot" button.
61) Remove the "self.ent_pems" and "self.ent_obd" related code in the "Main" tab. Remove the 'use real_col' and 'use_col' in the "plot_alignment" function. 
Plot df[align_col] in the self.ent_pems.get() and self.obd_df[align_col] in the self.ent_obd.get().
Locate the "btn_plot" button to tightly fit with the "btn_select" button horizontally.
Adjust the width of the “ent_align_input“ input textbox to tightly fit with x coordinate of the "btn_plot" button.
62) Remove the "self.ent_pems" and "self.ent_obd" related code in the "Main" tab. 
Use align_col without using the 'use real_col' and 'use_col' in the "plot_alignment" function.