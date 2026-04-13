import folium
import pandas as pd
import os

# Example: Replace with your actual data loading
os.chdir('C:/Users/slee02/PyCharmProjects/RWET')
# DataFrame should have columns: 'latitude', 'longitude'
print("Current working directory:", os.getcwd())

pp_file = 'pp_2016_Malibu_Blue_LDV_20180328_M1-M9.csv'
# with open(pp_file, 'r') as f:
#     lines = f.readlines()
# columns = lines[1].strip().split(',')
# units = lines[2].strip().split(',')
# data = pd.read_csv('pp_2016_Malibu_Blue_LDV_20180328_M1-M9.csv', skiprows=3, names=columns)

df = pd.read_csv(pp_file, skiprows=1, escapechar='\\', encoding = 'unicode_escape')
# Set variables in the first row to unit columns
# unit_dict = dict(zip(columns, units))
# df.attrs['units'] = unit_dict
columns = list(df.columns)
units = list(df.loc[0, :])
# Delete the second row (index 1)
df = df.drop(df.index[0])
df.dropna(axis=1, how='all', inplace=True)

df.loc[7366, 'sDATE']
summary_idx = df[df['sDATE'].astype(str).str.contains("Summary Information:", na=False)].index
print("Indices containing 'Summary Information':", summary_idx.tolist())

# Remove all rows after summary_idx in df
if len(summary_idx) > 0:
    df = df.loc[:summary_idx[0]-4, :]
# Center the map on the first point
# Drop rows where 'iGPS_LAT' or 'iGPS_LON' are NaN
df = df.dropna(subset=['iGPS_LAT', 'iGPS_LON'])

start_location = [df['iGPS_LAT'].iloc[0], df['iGPS_LON'].iloc[0]]
m = folium.Map(location=start_location, zoom_start=15)

# Add the route as a polyline
route = list(zip(df['iGPS_LAT'].astype(float), df['iGPS_LON'].astype(float)))
folium.PolyLine(route, color='blue', weight=5, opacity=0.7).add_to(m)

# Optionally, add start and end markers
folium.Marker(route[0], tooltip='Start').add_to(m)
folium.Marker(route[-1], tooltip='End').add_to(m)

# Save to HTML and display
m.save('driving_route.html')
print("Map saved as driving_route.html")