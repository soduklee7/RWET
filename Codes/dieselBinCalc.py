import numpy as np
import pandas as pd
import time

def dieselBinCalc(setIdx, vehData, udp):
    """
    Python version of dieselBinCalc.m    
    % Bin Calculation for off-cycle, diesel testing according to 40CFR 1036.530

    % all interval data for bin calculations is stored in the cell array 'binIData' with each
    % column representing one interval.  Each row represents the following data
    % related to the respective interval (column).

    % binIData{1,n}: row 1:  boolean of exluded/included data in interval
    % binIData{2,n}: row 2:  start and end indices of interval relative to entire
    %                        test cycle.  (1x2 vector)
    % binIData{3,n}: row 3:  Average time for the test inerval (scalar).  Used
    %                        for graphing
    % binIData{4,n}: row 4:  total included time for the interval (i.e. 300 sec)
    % binIData{5,n}: row 5:  valid/invalid (1/0) data.  interval is invalid if
    %                        the number of exluded pts > 600  (Scalar)
    % binIData{6,n}: row 6:  number of sub intervals within the interval
    % binIData{7,n}: row 7:  indices of the sub-intervals relative to the entire
    %                        test
    % binIData{8,n}: row 8:  mco2,norm,testinterval, Normalized C)2 mass over a
    %                       300 second test interval according to 1036.530(e)
    % binIData{9,n}: row 9:  bin number (1,2 or 0 for invalid)
    tic

    % --------------------------------------------------------------------------------
    % 1036.530 (b)(2) - Engine coolant temperature at start
    % Check the engine coolant temperature in the first 15 seconds at start is
    % less than 40 C.
    % --- Convert coolant temperature to C.`

    """
    start_time = time.time()
    
    # Extract references for easier access
    # Assuming vehData is a list of dicts/objects and .data is a pandas DataFrame
    current_veh = vehData[setIdx]
    df = current_veh['data']
    pems = udp[setIdx]['pems']
    
    # -------------------------------------------------------------------------
    # 1036.530 (b)(2) - Engine coolant temperature at start
    # -------------------------------------------------------------------------
    # Note: unit_convert and create_label are assumed helper functions
    cool_temp_unit = df.attrs.get('units', {}).get(pems['coolantT'], 'C') 
    coolant_temp_c = unit_convert(df[pems['coolantT']], cool_temp_unit, 'C')
    vehData = create_label(setIdx, coolant_temp_c, pems['coolantTC'], '(C)', 1)

    # Check first 15 seconds (Python is 0-indexed)
    below_40_idx = np.where(coolant_temp_c <= 40)[0]
    
    # Check if 5 of the first 15 seconds is less than 40 C
    if len(np.where(coolant_temp_c[:15] <= 40)[0]) >= 5:
        print('Coolant at start less than 40')
    else:
        print('Coolant at start GREATER than 40')
        print('Bin Emissions cannot be calculated')

    # -------------------------------------------------------------------------
    # Excluded Data 1036.530 (c)(3)
    # -------------------------------------------------------------------------
    include = {}
    
    # --- Zero engine speed
    include['engSpeed'] = (df[pems['engineSpeed']] > 0).astype(int)
    vehData = create_label(setIdx, include['engSpeed'], pems['includeEngSpeed'], '(-)', 1)

    # --- Infrequent Regeneration
    include['regen'] = (df[pems['regenStatus']] < 1).astype(int)
    vehData = create_label(setIdx, include['regen'], pems['includeRegen'], '(-)', 1)

    # --- Tambient > Tmax
    amb_unit = df.attrs.get('units', {}).get(pems['ambientAirT'], 'C')
    ambient_temp_c = unit_convert(df[pems['ambientAirT']], amb_unit, 'C')

    alt_unit = df.attrs.get('units', {}).get(pems['altitude'], 'ft')
    altitude_ft = unit_convert(df[pems['altitude']], alt_unit, 'ft')
    vehData = create_label(setIdx, altitude_ft, pems['altitudeFt'], '(ft)', 1)

    t_max_c = -0.0014 * altitude_ft + 37.78
    include['tMax'] = (ambient_temp_c < t_max_c).astype(int)
    vehData = create_label(setIdx, include['tMax'], pems['includeTmax'], '(-)', 1)
    vehData = create_label(setIdx, t_max_c, pems['tMaxLimit'], '(-)', 1)

    # --- Tambient > 5C
    include['ambient5C'] = (ambient_temp_c > 5).astype(int)
    n_pts = len(df)
    ambient_5c_limit = np.ones(n_pts) * 5
    vehData = create_label(setIdx, include['ambient5C'], pems['includeAmbient5C'], '(-)', 1)
    vehData = create_label(setIdx, ambient_5c_limit, pems['ambientTLimit'], '(-)', 1)

    # --- Altitude < 5500 ft
    include['altitude'] = (altitude_ft < 5500).astype(int)
    altitude_5500_limit = np.ones(n_pts) * 5500
    vehData = create_label(setIdx, include['altitude'], pems['includeAltitude'], '(-)', 1)
    vehData = create_label(setIdx, altitude_5500_limit, pems['altitudeLimit'], '(-)', 1)

    # --- Combine all Included points
    include_total = (include['engSpeed'] * include['regen'] * include['tMax'] * 
                     include['ambient5C'] * include['altitude'])

    # --- Exclude single data point surrounded by excluded points
    # Vectorized approach using pandas shift
    s = pd.Series(include_total)
    mask = (s.shift(1) == 0) & (s.shift(-1) == 0) & (s == 1)
    s[mask] = 0
    include_total = s.to_numpy()
    
    vehData = create_label(setIdx, include_total, pems['includeTotal'], '(-)', 1)

    # -------------------------------------------------------------------------
    # Interval Calculations
    # -------------------------------------------------------------------------
    idx_start = 0  # Python 0-indexing
    idx_end = 0
    bin_i_data = [] # List to store interval dictionaries
    end_test = len(include_total)
    
    test_cycle_time = df[pems['time']].to_numpy()
    test_cycle_co2 = df[pems['co2MassFlow']].to_numpy()
    
    idx_300s = int(round(300 / current_veh['timeStep']))
    end_flag = False

    while idx_end < end_test and not end_flag:
        idx_end = idx_start + idx_300s
        # ... logic continues for window calculations ...
        
        # (Snippet ends here in original code)
        if idx_end >= end_test:
            end_flag = True

    return bin_i_data, vehData

# def unit_convert(data, from_unit, to_unit):
#     """ Placeholder for your unit conversion logic """
#     return data

# def create_label(idx, data, label_name, unit, some_param):
#     """ Placeholder for your label creation logic """
#     return None # Return updated vehData structure

def create_label(vehData: List[Dict[str, Any]], setIdx: int,
                 series: np.ndarray, column_name: str) -> None:
    """
    Mimic MATLAB's createLabel by adding/overwriting a column in the pandas DataFrame.
    """
    df = vehData[setIdx]["data"]
    df[column_name] = series
    
def unit_convert(values: np.ndarray, from_unit: str, to_unit: str) -> np.ndarray:
    """
    Minimal unit conversion helper for the units used in this function.
    Supports: C <-> F, m <-> ft. If units are the same or from_unit is None/empty,
    returns input unchanged.
    """
    if from_unit is None or from_unit == "" or from_unit == to_unit:
        return values

    from_u = from_unit.strip().lower()
    to_u = to_unit.strip().lower()

    # Temperature
    if from_u in ("c", "degc") and to_u in ("f", "degf"):
        return values * 9.0 / 5.0 + 32.0
    if from_u in ("f", "degf") and to_u in ("c", "degc"):
        return (values - 32.0) * 5.0 / 9.0

    # Length (altitude)
    if from_u in ("m", "meter", "meters") and to_u in ("ft", "feet"):
        return values * 3.280839895
    if from_u in ("ft", "feet") and to_u in ("m", "meter", "meters"):
        return values / 3.280839895

    # If no conversion rule matched, return unchanged
    return values


# def create_label(vehData: List[Dict[str, Any]], setIdx: int,
#                  series: np.ndarray, column_name: str) -> None:
#     """
#     Mimic MATLAB's createLabel by adding/overwriting a column in the pandas DataFrame.
#     """
#     df = vehData[setIdx]["data"]
#     df[column_name] = series
