import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple


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


def create_label(vehData: List[Dict[str, Any]], setIdx: int,
                 series: np.ndarray, column_name: str) -> None:
    """
    Mimic MATLAB's createLabel by adding/overwriting a column in the pandas DataFrame.
    """
    df = vehData[setIdx]["data"]
    df[column_name] = series


def diesel_bin_calc(setIdx: int,
                    vehData: List[Dict[str, Any]],
                    udp: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Python translation of dieselBinCalc.m

    Parameters:
      setIdx: zero-based index of the dataset in vehData
      vehData: list of dict-like objects with:
        - "data": pandas DataFrame with time-series columns
        - "timeStep": float, sampling period in seconds
        - optionally "units": dict mapping column_name -> unit string
      udp: list of dict-like objects with:
        - "pems": dict of column names for signals used here
        - "bins": dict with keys "eco2fcl", "pmax"

    Returns:
      bin_i_data: list of dicts, one per interval, analogous to MATLAB binIData
      vehData: updated vehData with:
        - vehData[setIdx]["scalarBinData"]: pandas DataFrame
        - vehData[setIdx]["binData"]: pandas DataFrame
        
    % dieselBinCalc.m
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
    % --- Convert coolant temperature to C.

    """
    df: pd.DataFrame = vehData[setIdx]["data"]
    units_map: Dict[str, str] = vehData[setIdx].get("units", {})
    ts = float(vehData[setIdx]["timeStep"])
    pems = udp[setIdx]["pems"]
    bins_cfg = udp[setIdx]["bins"]

    # Helper to fetch units
    def get_unit(col: str) -> str:
        return units_map.get(col, "")

    # 1036.530 (b)(2) - Coolant temp at start < 40 C for at least 5 of first 15 s
    cool_col = pems["coolantT"]
    cool_unit = get_unit(cool_col)
    cool_c = unit_convert(df[cool_col].to_numpy(dtype=float), cool_unit, "C")
    create_label(vehData, setIdx, cool_c, pems["coolantTC"])

    below40_idx = np.where(cool_c <= 40.0)[0]
    if len(below40_idx[below40_idx < 15]) >= 5:
        print("Coolant at start less than 40")
    else:
        print("Coolant at start GREATER than 40")
        print("Bin Emissions cannot be calculated")

    # Excluded Data 1036.530 (c)(3)

    # Zero engine speed
    eng_speed_col = pems["engineSpeed"]
    include_eng_speed = (df[eng_speed_col].to_numpy(dtype=float) > 0.0)
    create_label(vehData, setIdx, include_eng_speed.astype(int), pems["includeEngSpeed"])

    # Infrequent Regeneration
    regen_col = pems["regenStatus"]
    include_regen = (df[regen_col].to_numpy(dtype=float) < 1.0)
    create_label(vehData, setIdx, include_regen.astype(int), pems["includeRegen"])

    # Tambient > Tmax (dependent on altitude)
    amb_col = pems["ambientAirT"]
    amb_unit = get_unit(amb_col)
    amb_c = unit_convert(df[amb_col].to_numpy(dtype=float), amb_unit, "C")

    alt_col = pems["altitude"]
    alt_unit = get_unit(alt_col)
    alt_ft = unit_convert(df[alt_col].to_numpy(dtype=float), alt_unit, "ft")
    create_label(vehData, setIdx, alt_ft, pems["altitudeFt"])

    t_max_c = -0.0014 * alt_ft + 37.78
    include_tmax = (amb_c < t_max_c)
    create_label(vehData, setIdx, include_tmax.astype(int), pems["includeTmax"])
    create_label(vehData, setIdx, t_max_c, pems["tMaxLimit"])

    # Tambient > 5C
    include_ambient_5c = (amb_c > 5.0)
    npts = len(amb_c)
    ambient_5c_line = np.full(npts, 5.0, dtype=float)
    create_label(vehData, setIdx, include_ambient_5c.astype(int), pems["includeAmbient5C"])
    create_label(vehData, setIdx, ambient_5c_line, pems["ambientTLimit"])

    # Altitude < 5500 ft
    include_altitude = (alt_ft < 5500.0)
    alt_5500_line = np.full(npts, 5500.0, dtype=float)
    create_label(vehData, setIdx, include_altitude.astype(int), pems["includeAltitude"])
    create_label(vehData, setIdx, alt_5500_line, pems["altitudeLimit"])

    # Combine included points then remove isolated included points
    include_total = include_eng_speed & include_regen & include_tmax & include_ambient_5c & include_altitude

    # Exclude single point surrounded by exclusions
    if npts >= 3:
        include_total_mod = include_total.copy()
        left = include_total[:-2]
        mid = include_total[1:-1]
        right = include_total[2:]
        isolated = (~left) & mid & (~right)
        include_total_mod[1:-1][isolated] = False
        include_total = include_total_mod

    create_label(vehData, setIdx, include_total.astype(int), pems["includeTotal"])

    # Interval Calculations
    time_col = pems["time"]
    time_vec = df[time_col].to_numpy(dtype=float)
    co2_mf_col = pems["co2MassFlow"]
    co2_mass_flow = df[co2_mf_col].to_numpy(dtype=float)

    idx300s = int(round(300.0 / ts))
    idx_start = 0
    idx_end = 0
    end_test = npts - 1
    end_flag = False

    bin_i_data: List[Dict[str, Any]] = []
    num_int = 0

    def get_win_time(start_idx: int, end_idx: int) -> Tuple[float, np.ndarray]:
        # Boolean include window and time deltas
        move_win = include_total[start_idx:end_idx + 1]
        t_win = time_vec[start_idx:end_idx + 1]
        if len(t_win) < 2:
            return 0.0, move_win
        dt = np.diff(t_win)
        inc_pairs = move_win[1:] & move_win[:-1]
        total_win_time = float(np.sum(dt * inc_pairs))
        return total_win_time, move_win

    while (idx_end < end_test) and (not end_flag):
        # Begin a new interval: initial window with 300 s worth of samples
        idx_end = idx_start + idx300s
        n_con = 0
        n_con_max = 0

        if idx_end > end_test:
            break

        # Start must have two consecutive included points
        if include_total[idx_start] and include_total[idx_start + 1]:
            total_win_time, move_win = get_win_time(idx_start, idx_end)

            while total_win_time < 300.0:
                idx_end += 1
                if idx_end >= end_test:
                    end_flag = True
                    break
                total_win_time, move_win = get_win_time(idx_start, idx_end)

            if not end_flag:
                invert_move = (move_win == 0)

                # Valid if total excluded points in window < 600 (per MATLAB code)
                if invert_move.sum() < 600:
                    bin_valid = 1
                else:
                    # Check for 600 consecutive excluded samples
                    n_con = 0
                    n_con_max = 0
                    for k in range(1, len(invert_move)):
                        if invert_move[k - 1] and invert_move[k]:
                            n_con += 1
                        else:
                            n_con_max = max(n_con_max, n_con)
                            n_con = 0
                    n_con_max = max(n_con_max, n_con)
                    bin_valid = 0 if n_con_max >= 600 else 1

                # Save interval
                num_int += 1
                interval = {
                    "include": move_win.astype(bool),
                    "idx": [idx_start, idx_end],
                    "time_avg": float((time_vec[idx_start] + time_vec[idx_end]) / 2.0),
                    "win_time": float(total_win_time),
                    "valid": int(bin_valid),
                    # Filled later:
                    "n_sub": 0,
                    "sub_idx": None,      # np.ndarray shape (2, n_sub)
                    "mco2_norm": 0.0,
                    "bin": 0,
                }
                bin_i_data.append(interval)

                # Initialize next moving window
                idx_start += 1
                idx_end = idx_start + idx300s
        else:
            idx_start += 1

    # Determine sub-intervals via rising/falling edges of include vector
    for interval in bin_i_data:
        start_idx, end_idx = interval["idx"]
        if interval["valid"] == 0:
            interval["n_sub"] = 0
            interval["sub_idx"] = np.array([[0], [0]], dtype=int)
            continue

        sub_idx_abs = np.arange(start_idx, end_idx + 1, dtype=int)
        inc_vec = interval["include"].astype(bool)
        n_sub = 1
        sub_starts = [sub_idx_abs[0]]
        sub_ends = []

        for ndx in range(1, len(inc_vec)):
            # If last element
            if ndx == len(inc_vec) - 1:
                if inc_vec[ndx]:
                    sub_ends.append(sub_idx_abs[ndx])
                else:
                    sub_ends.append(sub_idx_abs[ndx - 1])
            # Falling edge
            elif inc_vec[ndx] and (not inc_vec[ndx + 1]):
                sub_ends.append(sub_idx_abs[ndx])
            # Rising edge
            elif (not inc_vec[ndx]) and inc_vec[ndx + 1]:
                sub_starts.append(sub_idx_abs[ndx + 1])
                n_sub += 1

        # Align starts and ends
        if len(sub_ends) < len(sub_starts):
            # If interval ends on an included point, ensure final end added
            sub_ends.append(sub_idx_abs[len(inc_vec) - 1])

        sub_idx_mat = np.zeros((2, n_sub), dtype=int)
        sub_idx_mat[0, :] = sub_starts[:n_sub]
        sub_idx_mat[1, :] = sub_ends[:n_sub]

        interval["n_sub"] = int(n_sub)
        interval["sub_idx"] = sub_idx_mat

    # Normalized CO2 mass over intervals and bin assignment
    eco2fcl = float(bins_cfg["eco2fcl"])
    pmax = float(bins_cfg["pmax"])

    for interval in bin_i_data:
        if interval["valid"] == 0:
            interval["mco2_norm"] = 0.0
            interval["bin"] = 0
            continue

        mass_co2_interval = 0.0
        sub_idx_mat = interval["sub_idx"]
        for j in range(sub_idx_mat.shape[1]):
            s = int(sub_idx_mat[0, j])
            e = int(sub_idx_mat[1, j])
            t_sub = time_vec[s:e + 1]
            co2_sub = co2_mass_flow[s:e + 1]
            mass_sub = float(np.trapz(co2_sub, t_sub))
            mass_co2_interval += mass_sub

        time_int_hr = interval["win_time"] / 3600.0
        if time_int_hr <= 0:
            m_co2_norm = 0.0
        else:
            m_co2_norm = 100.0 * mass_co2_interval / (eco2fcl * pmax * time_int_hr)

        m_co2_norm = float(np.round(m_co2_norm, 2))
        interval["mco2_norm"] = m_co2_norm
        interval["bin"] = 1 if m_co2_norm <= 6.0 else 2

    # Assemble scalar stats
    bins_vec = np.array([it["bin"] for it in bin_i_data], dtype=int)
    valid_vec = np.array([it["valid"] for it in bin_i_data], dtype=int)
    num_valid = int(valid_vec.sum())
    num_invalid = int(np.sum(valid_vec == 0))
    num_bin1 = int(np.sum(bins_vec == 1))
    num_bin2 = int(np.sum(bins_vec == 2))
    num_intervals = int(len(bin_i_data))

    scalar_bin_table = pd.DataFrame({
        "Number_Intervals": [num_intervals],
        "NumValid_Intervals": [num_valid],
        "NumInValid_Intervals": [num_invalid],
        "NumBin1_Intervals": [num_bin1],
        "NumBin2_Intervals": [num_bin2],
    })

    # Time bin average vector (for graphing)
    time_bin_avg = np.array([it["time_avg"] for it in bin_i_data], dtype=float)

    # Bin emission mass calculator (subfunction in MATLAB)
    def bin_mass_calc(mass_flow_vec: np.ndarray, bin_number: int) -> Tuple[np.ndarray, float]:
        bin_mass_interval = np.zeros(len(bin_i_data), dtype=float)
        for j_int, it in enumerate(bin_i_data):
            if it["bin"] != bin_number or it["valid"] == 0:
                bin_mass_interval[j_int] = 0.0
                continue
            mass_interval = 0.0
            sub_idx_mat = it["sub_idx"]
            for j_sub in range(sub_idx_mat.shape[1]):
                s = int(sub_idx_mat[0, j_sub])
                e = int(sub_idx_mat[1, j_sub])
                t_sub = time_vec[s:e + 1]
                mf_sub = mass_flow_vec[s:e + 1]
                mass_sub = float(np.trapz(mf_sub, t_sub))
                mass_interval += mass_sub
            bin_mass_interval[j_int] = mass_interval
        return bin_mass_interval, float(bin_mass_interval.sum())

    # Brake emission cumulative calculator (subfunction in MATLAB)
    def brake_em_cu(em_vec: np.ndarray, co2_vec: np.ndarray) -> np.ndarray:
        out = np.zeros_like(em_vec, dtype=float)
        em_cum = 0.0
        co2_cum = 0.0
        for i in range(len(em_vec)):
            em_cum += em_vec[i]
            co2_cum += co2_vec[i]
            if co2_cum > 0:
                out[i] = eco2fcl * em_cum / co2_cum
            else:
                out[i] = 0.0
        return out

    # NOx Bin 1 Mass
    knox_col = pems["kNOxMassFlow"]
    nox_mf = df[knox_col].to_numpy(dtype=float)
    nox_bin1_mass, nox_bin1_mass_total = bin_mass_calc(nox_mf, 1)

    # Bin 1 mass flow (g/hr)
    time_bin1_hr = np.array([(it["win_time"] / 3600.0) if it["bin"] == 1 else 0.0 for it in bin_i_data], dtype=float)
    time_bin1_total = float(time_bin1_hr.sum())
    nox_bin1_mass_flow = 0.0 if time_bin1_total == 0.0 else nox_bin1_mass_total / time_bin1_total

    scalar_bin_table["NOxMassFlow_Bin1"] = [nox_bin1_mass_flow]

    # Initialize binDataTable with Time_BinAvg and NOx_Mass_Bin1
    bin_data_table = pd.DataFrame({
        "Time_BinAvg": time_bin_avg,
        "NOx_Mass_Bin1": nox_bin1_mass
    })

    # Cumulative NOx mass flow for Bin 1
    nox_bin1_mass_flow_cu = np.zeros(len(bin_i_data), dtype=float)
    mass_cum = 0.0
    time_cum = 0.0
    for i in range(len(bin_i_data)):
        mass_cum += nox_bin1_mass[i]
        time_cum += time_bin1_hr[i]
        if time_cum > 0:
            nox_bin1_mass_flow_cu[i] = mass_cum / time_cum
        else:
            nox_bin1_mass_flow_cu[i] = 0.0
    bin_data_table["NOxMassFlow_Bin1_Cummulative"] = nox_bin1_mass_flow_cu

    # NOx Bin 2 (mg/hp*hr)
    nox_bin2_mass, nox_bin2_mass_total = bin_mass_calc(nox_mf, 2)
    nox_bin2_mass_mg = nox_bin2_mass * 1000.0
    # CO2 Bin 2 mass (g)
    co2_bin2_mass, co2_bin2_mass_total = bin_mass_calc(co2_mass_flow, 2)

    if co2_bin2_mass_total > 0:
        nox_bin2_brake = eco2fcl * nox_bin2_mass_total / co2_bin2_mass_total
    else:
        nox_bin2_brake = 0.0
    scalar_bin_table["NOxBrakeSpecific_Bin2"] = [nox_bin2_brake * 1000.0]  # mg/hp*hr

    bin_data_table["NOx_Mass_Bin2"] = nox_bin2_mass_mg

    # Cumulative NOx brake-specific for Bin 2 (mg/hp*hr)
    nox_bin2_brake_cu = brake_em_cu(nox_bin2_mass, co2_bin2_mass) * 1000.0
    bin_data_table["NOx_BrakeSpec_Bin2_Cummulative"] = nox_bin2_brake_cu

    # CO Bin 2 (g/hp*hr)
    co_mf_col = pems["coMassFlow"]
    co_mf = df[co_mf_col].to_numpy(dtype=float)
    co_bin2_mass, co_bin2_mass_total = bin_mass_calc(co_mf, 2)

    if co2_bin2_mass_total > 0:
        co_bin2_brake = eco2fcl * co_bin2_mass_total / co2_bin2_mass_total
    else:
        co_bin2_brake = 0.0
    scalar_bin_table["coBrakeSpecific_Bin2"] = [co_bin2_brake]  # g/hp*hr

    bin_data_table["CO_Mass_Bin2"] = co_bin2_mass
    co_bin2_brake_cu = brake_em_cu(co_bin2_mass, co2_bin2_mass)
    bin_data_table["CO_BrakeSpec_Bin2_Cummulative"] = co_bin2_brake_cu

    # HC Bin 2 (mg/hp*hr)
    hc_mf_col = pems["hcMassFlow"]
    hc_mf = df[hc_mf_col].to_numpy(dtype=float)
    hc_bin2_mass, hc_bin2_mass_total = bin_mass_calc(hc_mf, 2)
    hc_bin2_mass_mg = hc_bin2_mass * 1000.0
    bin_data_table["HC_Mass_Bin_2"] = hc_bin2_mass_mg  # optional extra column

    if co2_bin2_mass_total > 0:
        hc_bin2_brake = eco2fcl * hc_bin2_mass_total / co2_bin2_mass_total
    else:
        hc_bin2_brake = 0.0
    scalar_bin_table["hcBrakeSpecific_Bin2"] = [hc_bin2_brake * 1000.0]  # mg/hp*hr

    hc_bin2_brake_cu = brake_em_cu(hc_bin2_mass, co2_bin2_mass) * 1000.0
    bin_data_table["HC_BrakeSpec_Bin2_Cummulative"] = hc_bin2_brake_cu

    # Save to vehData (to mirror MATLAB)
    vehData[setIdx]["scalarBinData"] = scalar_bin_table
    vehData[setIdx]["binData"] = bin_data_table

    return bin_i_data, vehData