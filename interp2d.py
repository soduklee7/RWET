import numpy as np
import csv
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

# Create a 2D grid of data
x = np.linspace(0, 1, 10)
y = np.linspace(0, 2, 20)
xg, yg = np.meshgrid(x, y, indexing='ij')
data = np.sin(xg**2 + yg**2)

# Create the interpolator
interp = RegularGridInterpolator((x, y), data)

# Interpolate at new points
x_new = 0.25 # np.array([0.25]) #, 0.5, 0.75])
y_new = 0.5 # np.array([0.5]) #, 1.0, 1.5])
points = np.array([x_new, y_new]).T
interpolated_values = interp(points)

print(interpolated_values)

def read_excel_to_2d_array(filename, sheet_name=0, header_rows=0):
    """Reads an Excel table into a 2D NumPy array."""
    xls = pd.ExcelFile(filename)
    if sheet_name in xls.sheet_names:
        df = pd.read_excel(filename, sheet_name=sheet_name, header=header_rows)

        return df.to_numpy()

def read_excel_columns(filename, sheet_name=0, header_rows=None):
    xls = pd.ExcelFile(filename)
    if sheet_name in xls.sheet_names:
        df = pd.read_excel(filename, sheet_name=sheet_name, header=header_rows)
        col_trq_Nm = df[df.columns[0]][~np.isnan(df[df.columns[0]])]
        col_spd_radps = df[df.columns[1]][~np.isnan(df[df.columns[1]])]

        return col_trq_Nm, col_spd_radps

filename = 'C:\\Users\\slee02\\PycharmProjects\\vehicle-model-python\\emachine_2018_Chevrolet_Bolt_150kW_400V_FWD_EDU.xlsx'
EM_power_maps = read_excel_to_2d_array(filename, 'Motor Power Maps', 0)
EM_eff_maps = read_excel_to_2d_array(filename, 'Motor Efficiency Maps', 0)
[EM_Torque, EM_Speed] = read_excel_columns(filename, 'Torque & Speed', 0)
print([EM_Torque, EM_Speed])

eng_filename = 'C:\\Users\\slee02\\PycharmProjects\\vehicle-model-python\\engine_Honda_Turbo_1L5_2016_paper_image.xlsx'
eng_fuel_maps = read_excel_to_2d_array(eng_filename, 'engine.fuel_map_gps', 0)
[eng_Torque, eng_Speed] = read_excel_columns(eng_filename, 'Torque & Speed', 0)

print([eng_Torque, eng_Speed])

def remove_blanks(parameter_value):
    ftmp = []
    for k in range(len(parameter_value)):
        try:
            kk = len(str(parameter_value[k]))
            if kk > 0:
                ftmp.append(parameter_value[k])
        except ValueError:
            pass
    return ftmp
    
def read_simulation_parameters(csv_file):
    """Reads simulation parameters from a CSV file.

    Args:
        csv_file: The path to the CSV file.

    Returns:
        A dictionary of parameters.
    """
    # line = 0
    parameters = {}
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row if it exists
        for row in reader:
            if any(row):  # Check if the row is not empty
                # if "electric." in row[0]: row[0] = str(row[0]).strip("electric.")
                if ("%" == str(row[0])[0]): 
                    continue
                if ("if" == str(row[0])[0:2]) or ("function" == str(row[0])[0:8]) or ("class_") in row[0]  or ("end" == str(row[0])[0:3]):
                    continue
                if "," in row[0]: 
                    row = str(row[0]).strip(";").split(',')
                if "=" in row[0]: 
                    row = str(row[0]).strip(" ").split('=')
                    if (";" in row[1]):
                        value_str = row[1]
                        for i in range(len(value_str)):
                            if ";" == value_str[i]:
                                row[1] =row[1][0:i]
                                break
                if len(row) ==1:
                    parameter_value = row[0].strip(";") # .replace(" ", ",")
                    for i in range(len(parameter_value)):
                        if parameter_value[i] != ' ':
                            if "]" in parameter_value: 
                                parameter_value = parameter_value.strip("]")
                            parameter_value = parameter_value[i:].split(" ")
                            if '' in parameter_value: parameter_value = remove_blanks(parameter_value)
                            for j in range(len(parameter_value)):
                                try:
                                    parameter_value[j] = float(parameter_value[j])
                                except ValueError:
                                    pass
                            parameter_value = np.array(parameter_value)
                            break
                    if (parameter_value[0] != ' '):
                        parameters[parameter_name] = np.vstack((parameters[parameter_name], parameter_value))
                    else:
                        print(parameter_value[0], ' in ', row)
                elif len(row) > 1:
                    parameter_name, parameter_value = row[0].strip(" "), row[1]
                    # Convert to appropriate data type if needed
                    try:
                        parameter_value = float(parameter_value)
                    except ValueError:
                        parameter_value = parameter_value.strip(" ")
                        if "[" in parameter_value:
                            if "]" not in parameter_value: 
                                parameter_value = parameter_value.strip("[")
                            if ("[" in parameter_value) and ("]" in parameter_value):
                                parameter_value = parameter_value.replace(" ", ",")
                                parameter_value = np.array(parameter_value)
                            elif ";" in parameter_value:
                                print(parameter_value)
                            else:
                                parameter_value = parameter_value.strip("[").split(" ")
                                if '' in parameter_value: parameter_value = remove_blanks(parameter_value)
                                parameter_value = np.array(parameter_value)

                        pass  # Keep as string

                    parameters[parameter_name] = parameter_value

    return parameters

# Example usage
filename = 'simulation_parameters.csv'
filename = 'battery_M9_EREV_52Ah.m'
parameters = read_simulation_parameters(filename)

for key, value in parameters.items():
    if isinstance(value, str):
        print(value)
        if "()" in value:
            value = value.strip("()")
            filename = value + '.m'
            parameters1 = read_simulation_parameters(filename)

    print(key, value) 
    
print(parameters)

# https://stackoverflow.com/questions/74044628/read-in-csv-and-capture-values-to-use-for-calculation

# from csv import DictReader

# inputfile = DictReader(open('test.csv'))
# for row in inputfile:
#     print(f"{row['client']} profit : {int(row['revenue']) - int(row['expenses'])}")

# import csv

# with open("input.csv", "r") as file:
#     mycsvfile = csv.reader(file, delimiter=",")
    
#     for line, content in enumerate(mycsvfile):
        
#         if line == 0:
#             continue
        
#         print("the client number {} is : {}".format(line, content[0]))
        
#         print("the client number {} earns : {} $".format(line, content[1]))
        
#         print("the client number {} spends {} $".format(line, content[2]))