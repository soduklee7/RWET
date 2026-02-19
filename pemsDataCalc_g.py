import numpy as np
import pandas as pd
from scipy.integrate import trapezoid, cumulative_trapezoid
import warnings

def pemsDataCalc(setIdx, vehData, udp):
    """
    Python conversion of pemsDataCalc.m
    """
    # -------------------------------------------------------------- Time (sec)
    # Assuming get_data returns (numpy_array, unit_info_list)
    x_time, x_time_cell = get_data(setIdx, udp[setIdx]['pems']['time'], vehData)
    
    # ------------ Set vehicle speed source to CAN or GPS
    speed_source = udp[setIdx]['pems']['speedSource'].lower()
    if speed_source == 'can':
        udp[setIdx]['pems']['speed'] = udp[setIdx]['pems']['speedCAN']
    elif speed_source == 'gps':
        udp[setIdx]['pems']['speed'] = udp[setIdx]['pems']['speedGPS']

    # --------------------------------------------------- Vehicle Speed
    veh_spd, veh_spd_cell = get_data(setIdx, udp[setIdx]['pems']['speed'], vehData)
    
    # KPH
    veh_spd_kph = unit_convert(veh_spd, veh_spd_cell[4], 'km/hr') # Index 4 is MATLAB 5
    vehData = create_label(setIdx, veh_spd_kph, udp[setIdx]['pems']['kph'], '(km/hr)', 1, vehData)
    
    # MPH
    veh_spd_mph = unit_convert(veh_spd, veh_spd_cell[4], 'mph')
    vehData = create_label(setIdx, veh_spd_mph, udp[setIdx]['pems']['mph'], '(mph)', 1, vehData)

    # Handle NaNs
    if np.isnan(veh_spd_kph).any():
        warnings.warn('Vehicle Speed Contains Blank or NaN Values. Blanks set to Zero.')
        veh_spd_kph = np.nan_to_num(veh_spd_kph)

    # ----------------------------------------------- Cumulative Distance (km)
    veh_spd_kps = veh_spd_kph / 3600.0
    # initial=0 makes it the same length as x_time, matching MATLAB's cumtrapz
    dist_cumulative_km = cumulative_trapezoid(veh_spd_kps, x_time, initial=0)
    vehData = create_label(setIdx, dist_cumulative_km, udp[setIdx]['pems']['distSumKm'], '(km)', 1, vehData)

    # -------------------------------------------- Cumulative Distance (miles)
    dist_cumulative_mi = unit_convert(dist_cumulative_km, 'km', 'mile')
    vehData = create_label(setIdx, dist_cumulative_mi, udp[setIdx]['pems']['distSumMile'], '(mile)', 1, vehData)

    # ------------------ FTP phases (Indices)
    dist_cold_trans = 3.5909
    idx_cold_transient = np.where(dist_cumulative_mi < dist_cold_trans)[0]
    idx_stabilized = np.where(dist_cumulative_mi >= dist_cold_trans)[0]

    # Calculate phase distances
    if len(idx_cold_transient) > 0:
        dist_cold_trans_km = trapezoid(veh_spd_kps[idx_cold_transient], x_time[idx_cold_transient])
        dist_cold_trans_mi = unit_convert(dist_cold_trans_km, 'km', 'mile')

    # ----------------------------------------------------------- Total Distance
    dist_km = trapezoid(veh_spd_kps, x_time)
    vehData[setIdx]['scalarData'][udp[setIdx]['pems']['distanceKm']] = dist_km
    
    dist_mi = unit_convert(dist_km, 'km', 'mile')
    vehData[setIdx]['scalarData'][udp[setIdx]['pems']['distanceMile']] = dist_mi

    # ------------------------------------------- Engine Speed (rpm)
    eng_spd, eng_spd_c = get_data(setIdx, udp[setIdx]['pems']['engine_speed'], vehData)

    if udp[setIdx]['pems']['vehWtClass'] == 'LD':
        # Idle Time Calculation
        idle_start_idx = np.where(eng_spd > 0)[0]
        if idle_start_idx.size == 0:
            idle_start_time = np.nan
            warnings.warn('Engine Speed is Zero')
        else:
            # Python index 0 is MATLAB index 1
            idx = idle_start_idx[0]
            idle_start_time = x_time[idx] if idx == 0 else x_time[idx-1]

        # Drive Start Calculation
        veh_speed_raw, _ = get_data(setIdx, udp[setIdx]['pems']['speed'], vehData)
        drive_start_idx = np.where(veh_speed_raw > 0)[0]
        if drive_start_idx.size == 0:
            drive_start_time = np.nan
            warnings.warn('Vehicle Speed is Zero')
        else:
            idx = drive_start_idx[0]
            drive_start_time = x_time[idx] if idx == 0 else x_time[idx-1]

        idle_time = drive_start_time - idle_start_time if not np.isnan([idle_start_time, drive_start_time]).any() else np.nan
        vehData = create_label(setIdx, idle_time, udp[setIdx]['pems']['idleStartTime'], x_time_cell[4], 1, vehData)

    # ------------------------------------------- Work Calculation (HD)
    if udp[setIdx]['pems']['vehWtClass'] == 'HD':
        eng_spd_can, _ = get_data(setIdx, udp[setIdx]['can']['engSpeed'], vehData)
        torq_nm, _ = get_data(setIdx, udp[setIdx]['can']['engTorque'], vehData)
        
        power_kw = 2.0 * np.pi * torq_nm * eng_spd_can / 60000.0
        power_hp = 1.341 * power_kw
        
        work_total_hp_hr = trapezoid(power_hp, x_time) / 3600.0
        vehData = create_label(setIdx, power_kw, udp[setIdx]['pems']['enginePowerKw'], '(kW)', 1, vehData)
        vehData = create_label(setIdx, power_hp, udp[setIdx]['pems']['enginePowerHp'], '(HP)', 1, vehData)

    # ------------------------------------------- Average Weather Data
    time_step = vehData[setIdx]['timeStep']
    t300_idx = int(round(300.0 / time_step)) # Start calc after 300s
    
    amb_air_t_raw, amb_air_tc = get_data(setIdx, udp[setIdx]['pems']['ambientAirT'], vehData)
    amb_air_t_f = unit_convert(amb_air_t_raw, amb_air_tc[4], 'F')
    avg_amb_t = np.mean(amb_air_t_f[t300_idx:])
    vehData = create_label(setIdx, avg_amb_t, udp[setIdx]['pems']['avgAmbT'], '(F)', 1, vehData)

    return vehData, udp

# Placeholder helpers (ensure these are defined in your environment)
def get_data(idx, label, v_data):
    # logic to retrieve data array and units
    return np.array([]), [""]*6

def unit_convert(val, from_u, to_u):
    # logic for unit conversion
    return val

def create_label(idx, data, label, unit, param, v_data):
    # logic to attach new series to vehData
    return v_data
