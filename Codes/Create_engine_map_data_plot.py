import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

"""
================================================================================
MASTER AI PROMPT 1: High-Fidelity Data Generation & Export
================================================================================
Act as an automotive engineer. Write a Python script using NumPy, Pandas, and 
SciPy to generate a complete engine map dataset for a Toyota 2.0L M20A-FXS 
Dynamic Force engine.

1. Grid Setup: Create a 100x100 meshgrid for Engine Speed (800 to 6000 RPM) 
   and Torque (0 to 210 Nm).
2. WOT Curve: Define a Wide Open Throttle limit using quadratic interpolation 
   of these points: (800rpm, 120Nm), (1000rpm, 140Nm), (2000rpm, 165Nm), 
   (4400rpm, 188Nm), (5200rpm, 188Nm), and (6000rpm, 178Nm).
3. BSFC Calibration (Crucial): Center the peak efficiency at 2800 RPM and 140 Nm. 
   To ensure the minimum BSFC actually hits 220 g/kWh, calculate the friction 
   penalty at the optimal point: penalty_at_opt = 5800 / (140 + 15). 
   Set the base BSFC: bsfc_min_base = 220 - penalty_at_opt.
4. BSFC Formula: Calculate the grid using: 
   BSFC = bsfc_min_base + 1.4e-5*(RPM-2800)**2 + 0.005*(Torque-140)**2 + 
   0.0001*(RPM-2800)*(Torque-140) + 5800/(Torque+15).
5. Metrics: Calculate Power [kW] ((Torque * RPM) / 9548.8), Power [hp] 
   (kW * 1.34102), and Fuel Flow [g/s] ((BSFC * kW) / 3600).
6. Filter & Save: Flatten the arrays into a DataFrame. Filter out any rows 
   where Torque is greater than the WOT curve limit. Save this cleaned dataset 
   to 'Toyota_Prius_M20A_Engine_Master_Data.csv' and '.json'.
================================================================================
"""

# --- PART 1: DATA GENERATION ---

# 1. Grid Setup
rpm_vec = np.linspace(800, 6000, 100)
torque_vec = np.linspace(0, 210, 100)
rpm_grid, torque_grid = np.meshgrid(rpm_vec, torque_vec)

# 2. WOT Curve
wot_rpm = [800, 1000, 2000, 3000, 4400, 5200, 6000]
wot_torque = [120, 140, 165, 178, 188, 188, 178] 
f_wot = interp1d(wot_rpm, wot_torque, kind='quadratic', fill_value="extrapolate")

# 3. BSFC Calibration
rpm_opt, torque_opt = 2800, 140
penalty_at_opt = 5800 / (torque_opt + 15)
bsfc_min_base = 220 - penalty_at_opt

# 4. BSFC Formula
a, b, c = 1.4e-5, 0.005, 0.0001 
bsfc_vals = bsfc_min_base + a*(rpm_grid-rpm_opt)**2 + b*(torque_grid-torque_opt)**2 + c*(rpm_grid-rpm_opt)*(torque_grid-torque_opt)
bsfc_vals += 5800 / (torque_grid + 15) # Low load friction/pumping penalty

# 5. Metrics
power_kw = (torque_grid * rpm_grid) / 9548.8
power_hp = power_kw * 1.34102
fuel_flow_gs = (bsfc_vals * power_kw) / 3600.0

# 6. Filter & Save
df_master = pd.DataFrame({
    'RPM': rpm_grid.flatten(),
    'Torque_Nm': torque_grid.flatten(),
    'BSFC_g_per_kWh': bsfc_vals.flatten(),
    'Power_kW': power_kw.flatten(),
    'Power_hp': power_hp.flatten(),
    'Fuel_Flow_g_per_s': fuel_flow_gs.flatten()
})

# Filter out unreachable points above WOT
df_master = df_master[df_master['Torque_Nm'] <= df_master['RPM'].apply(f_wot)]

# Save data
csv_filename = "Toyota_Prius_M20A_Engine_Master_Data.csv"
json_filename = "Toyota_Prius_M20A_Engine_Master_Data.json"
df_master.to_csv(csv_filename, index=False)
df_master.to_json(json_filename, orient='records', indent=4)
print(f"Data saved to {csv_filename} and {json_filename}")


"""
================================================================================
MASTER AI PROMPT 2: Plotting the Engine Map from Saved Data
================================================================================
Write a Matplotlib script to plot a professional Engine Map using the 
'Toyota_Prius_M20A_Engine_Master_Data.csv' file generated in the previous step.

1. Data Handling: Load the CSV. Because the data was filtered (removing points 
   above WOT), the grid is no longer perfectly rectangular. You must use 
   `plt.tricontourf` and `plt.tricontour` using the 'RPM', 'Torque_Nm', and 
   'BSFC_g_per_kWh' columns.
2. Contours: Plot levels at exactly [220, 225, 230, 240, 250, 275, 300, 350, 
   400, 450, 500]. Use the 'YlGn_r' colormap for the filled contours and 'blue' 
   for the contour lines.
3. Labeling: Label the contour lines using plt.clabel(inline=True, fontsize=10, 
   colors='navy'). Do not use the 'weight' argument in clabel.
4. WOT Line: Recalculate and plot the red Wide Open Throttle curve over the 
   plot to show the physical upper boundary.
5. Annotation: Place a text label reading '220 g/kWh Best' at the coordinate 
   (2800, 145) with a dark green font and white background box.
6. Formatting: Set X-axis to 800-6000 RPM, Y-axis to 0-210 Nm. Add a colorbar 
   for BSFC, a grid, and save as a high-resolution PNG.
================================================================================
"""

# --- PART 2: PLOTTING FROM CSV ---

# 1. Data Handling
df_plot = pd.read_csv(csv_filename)
x = df_plot['RPM']
y = df_plot['Torque_Nm']
z = df_plot['BSFC_g_per_kWh']

# 2. Contours
plt.figure(figsize=(11, 8))
levels = [220, 225, 230, 240, 250, 275, 300, 350, 400, 450, 500]

# Use tricontourf/tricontour for non-rectangular filtered data
cf = plt.tricontourf(x, y, z, levels=levels, cmap='YlGn_r', alpha=0.4)
contour = plt.tricontour(x, y, z, levels=levels, colors='blue', linewidths=0.8)

# 3. Labeling (No 'weight' argument)
plt.clabel(contour, inline=True, fontsize=10, fmt='%d', colors='navy')

# 4. WOT Line
rpm_line = np.linspace(800, 6000, 200)
wot_line = f_wot(rpm_line)
plt.plot(rpm_line, wot_line, color='red', linewidth=3.5, label='Max Torque (WOT)')

# 5. Annotation
plt.text(2800, 145, "220 g/kWh Best", color='darkgreen', 
         fontsize=12, fontweight='bold', ha='center',
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='darkgreen'))

# 6. Formatting
plt.title("Engine Map: Toyota Prius 2.0L (M20A-FXS)\nBrake Specific Fuel Consumption [g/kWh]", fontsize=15, pad=15)
plt.xlabel("Engine Speed [RPM]", fontsize=12)
plt.ylabel("Engine Torque [Nm]", fontsize=12)
plt.xlim(800, 6000)
plt.ylim(0, 210)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='upper right')

cbar = plt.colorbar(cf)
cbar.set_label('BSFC [g/kWh]', rotation=270, labelpad=20)

plt.tight_layout()
plt.savefig("Toyota_Prius_M20A_Engine_Map_Final.png", dpi=300)
plt.show()

print("Engine map successfully plotted and saved to Toyota_Prius_M20A_Engine_Map_Final.png!")