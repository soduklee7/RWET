import numpy as np
import pandas as pd
import warnings
from typing import Any, Dict, List, Tuple


def unit_convert(values: np.ndarray, from_unit: str, to_unit: str) -> np.ndarray:
    """
    Minimal unit conversion helper for units used in pemsDataCalc:
      - Temperature: C <-> F
      - Distance: km <-> mile
      - Speed: mph <-> km/hr (kph)
      - Gas conc: ppm/ppb/% -> mole fraction 'conc'
    If units are identical or from_unit is missing, returns input unchanged.
    """
    if values is None:
        return None
    if from_unit is None:
        from_unit = ""
    if to_unit is None:
        to_unit = ""

    f = from_unit.strip().lower()
    t = to_unit.strip().lower()

    # no-op
    if f == t or f == "":
        return values

    # Temperature
    if f in ("c", "degc") and t in ("f", "degf"):
        return values * 9.0 / 5.0 + 32.0
    if f in ("f", "degf") and t in ("c", "degc"):
        return (values - 32.0) * 5.0 / 9.0

    # Distance
    if f in ("km",) and t in ("mile", "mi", "miles"):
        return values / 1.609344
    if f in ("mile", "mi", "miles") and t in ("km", "kilometer", "kilometers"):
        return values * 1.609344

    # Speed
    # Normalize synonyms
    if f in ("kph", "km/h", "km/hr"):
        f = "km/hr"
    if t in ("kph", "km/h", "km/hr"):
        t = "km/hr"
    if f == "mph" and t == "km/hr":
        return values * 1.609344
    if f == "km/hr" and t == "mph":
        return values / 1.609344

    # Concentration to mole fraction 'conc'
    if t == "conc":
        if f in ("ppm",):
            return values * 1e-6
        if f in ("ppb",):
            return values * 1e-9
        if f in ("percent", "%"):
            return values * 1e-2
        if f in ("conc",):
            return values
        # Unknown conversion to conc
        return values

    # If no rule matched, return unchanged
    return values


def _get_units(vehData: List[Dict[str, Any]], setIdx: int, col: str) -> str:
    return vehData[setIdx].get("units", {}).get(col, "")


def _get_data(vehData: List[Dict[str, Any]], setIdx: int, col: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Emulate MATLAB getData: returns (values, meta), where meta['unit'] is the column unit.
    """
    df: pd.DataFrame = vehData[setIdx]["data"]
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in vehData[{setIdx}]['data']")
    values = df[col].to_numpy()
    unit = _get_units(vehData, setIdx, col)
    return values, {"unit": unit}


def _create_label(vehData: List[Dict[str, Any]], setIdx: int, values: np.ndarray, col: str, unit: str) -> None:
    """
    Emulate MATLAB createLabel for time-series: add/update a column with units.
    """
    df: pd.DataFrame = vehData[setIdx]["data"]
    df[col] = values
    units_map = vehData[setIdx].setdefault("units", {})
    units_map[col] = unit


def _create_label_scalar(vehData: List[Dict[str, Any]], setIdx: int, value: float, name: str, unit: str) -> None:
    """
    Emulate MATLAB createLabelScalar for scalar entries.
    """
    scalars = vehData[setIdx].setdefault("scalarData", {})
    scalar_units = vehData[setIdx].setdefault("scalarUnits", {})
    scalars[name] = float(value) if np.ndim(value) == 0 else float(np.asarray(value).item())
    scalar_units[name] = unit


def pemsDataCalc(setIdx: int, vehData: List[Dict[str, Any]], udp: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Python translation of pemsDataCalc.m

    Modifies vehData[setIdx] in place by adding derived columns and scalar data.
    Also updates udp[setIdx]['pems']['speed'] based on 'speedSource' (can/gps).

    Returns:
      vehData (same object, updated).
    """
    df: pd.DataFrame = vehData[setIdx]["data"]
    ts = float(vehData[setIdx]["timeStep"])
    pems = udp[setIdx]["pems"]

    # ------------------------------ Time (sec)
    x_time, x_time_meta = _get_data(vehData, setIdx, pems["time"])
    time_unit = x_time_meta.get("unit", "s")

    # ------------ Select vehicle speed source (CAN or GPS)
    src = str(pems.get("speedSource", "")).strip().lower()
    if src == "can":
        pems["speed"] = pems["speedCAN"]
    elif src == "gps":
        pems["speed"] = pems["speedGPS"]
    else:
        # keep existing pems["speed"]
        pass

    # --------------------------------------------------- Vehicle Speed - KPH
    veh_spd, veh_spd_meta = _get_data(vehData, setIdx, pems["speed"])
    veh_spd_kph = unit_convert(veh_spd.astype(float), veh_spd_meta.get("unit", ""), "km/hr")
    _create_label(vehData, setIdx, veh_spd_kph, pems["kph"], "(km/hr)")

    # ---------------------------------------------------- Vehicle Speed - MPH
    veh_spd_mph = unit_convert(veh_spd.astype(float), veh_spd_meta.get("unit", ""), "mph")
    _create_label(vehData, setIdx, veh_spd_mph, pems["mph"], "(mph)")

    # NaN handling for speed KPH (warn and zero only the local array for distance calc)
    if np.isnan(veh_spd_kph).any():
        warnings.warn("Vehicle Speed contains NaN values. Blanks set to zero for distance calculations.")
        veh_spd_kph = veh_spd_kph.copy()
        veh_spd_kph[np.isnan(veh_spd_kph)] = 0.0

    # ----------------------------------------------- Cumulative Distance (km)
    veh_spd_kps = veh_spd_kph / 3600.0  # km/s
    dist_cum_km = np.cumtrapz(veh_spd_kps, x_time, initial=0.0)
    _create_label(vehData, setIdx, dist_cum_km, pems["distSumKm"], "(km)")

    # -------------------------------------------- Cumulative Distance (miles)
    dist_cum_mi = unit_convert(dist_cum_km, "km", "mile")
    _create_label(vehData, setIdx, dist_cum_mi, pems["distSumMile"], "(mile)")

    # ---------------- FTP-equivalent distances and indices
    dist_cold_trans = 3.5909
    dist_stabil = 3.8594
    idx_cold_trans = np.where(dist_cum_mi < dist_cold_trans)[0]
    idx_stabilized = np.where(dist_cum_mi >= dist_cold_trans)[0]

    dist_cold_trans_km = np.trapz(veh_spd_kps[idx_cold_trans], x_time[idx_cold_trans]) if idx_cold_trans.size > 0 else 0.0
    dist_cold_trans_mi = unit_convert(np.array([dist_cold_trans_km]), "km", "mile")[0]

    dist_stabilized_km = np.trapz(veh_spd_kps[idx_stabilized], x_time[idx_stabilized]) if idx_stabilized.size > 0 else 0.0
    dist_stabilized_mi = unit_convert(np.array([dist_stabilized_km]), "km", "mile")[0]

    # ----------------------------------------------------------- Distance (km) scalar
    dist_km = np.trapz(veh_spd_kps, x_time)
    _create_label_scalar(vehData, setIdx, dist_km, pems["distanceKm"], "km")

    # -------------------------------------------------------- Distance (miles) scalar
    dist_mi = unit_convert(np.array([dist_km]), "km", "mile")[0]
    _create_label_scalar(vehData, setIdx, dist_mi, pems["distanceMile"], "mile")

    # ------------------------------------------- Engine Speed (rpm)
    eng_spd, _ = _get_data(vehData, setIdx, pems["engineSpeed"])

    # Light-duty specific
    if str(pems.get("vehWtClass", "")).upper() == "LD":
        # Idle time at start
        idle_start_idx = np.where(eng_spd > 0.0)[0]
        if idle_start_idx.size == 0:
            idle_start_time = np.nan
            warnings.warn("Engine speed is zero.")
        else:
            idle_start_time = x_time[idle_start_idx[0] if idle_start_idx[0] == 0 else idle_start_idx[0] - 1]

        veh_speed_vals, _ = _get_data(vehData, setIdx, pems["speed"])
        drive_start_idx = np.where(veh_speed_vals > 0.0)[0]
        if drive_start_idx.size == 0:
            drive_start_time = np.nan
            warnings.warn("Vehicle speed is zero.")
        else:
            drive_start_time = x_time[drive_start_idx[0] if drive_start_idx[0] == 0 else drive_start_idx[0] - 1]

        if np.isnan(idle_start_time) or np.isnan(drive_start_time):
            idle_time = np.nan
        else:
            idle_time = float(drive_start_time - idle_start_time)

        _create_label(vehData, setIdx, np.array([idle_time]), pems["idleStartTime"], time_unit)

        # Coolant temperature at start (F)
        cool_t, cool_t_meta = _get_data(vehData, setIdx, pems["coolantT"])
        cool_f = unit_convert(cool_t.astype(float), cool_t_meta.get("unit", ""), "F")
        c1 = cool_f[0] if cool_f.size > 0 else np.nan
        c5 = cool_f[4] if cool_f.size > 4 else c1
        cool_start = c1 if (np.isnan(c1) or np.isnan(c5) or (c5 - c1) < 1.0) else c5
        _create_label(vehData, setIdx, np.array([cool_start]), pems["coolantStartT"], "F")

        # Ambient temperature at start (F)
        amb_t, amb_t_meta = _get_data(vehData, setIdx, pems["ambientAirT"])
        amb_f = unit_convert(amb_t.astype(float), amb_t_meta.get("unit", ""), "F")
        a1 = amb_f[0] if amb_f.size > 0 else np.nan
        a5 = amb_f[4] if amb_f.size > 4 else a1
        amb_start = a1 if (np.isnan(a1) or np.isnan(a5) or (a5 - a1) < 1.0) else a5
        _create_label(vehData, setIdx, np.array([amb_start]), pems["ambientStartT"], "F")

    # ---------------- Total Work using torque (HD path)
    if str(pems.get("vehWtClass", "")).upper() == "HD":
        can = udp[setIdx]["can"]
        eng_spd_can, _ = _get_data(vehData, setIdx, can["engSpeed"])
        torq_nm, _ = _get_data(vehData, setIdx, can["engTorque"])

        # Power (kW) = 2*pi*Torque(Nm)*Speed(rpm)/60000
        power_kw = 2.0 * np.pi * torq_nm * eng_spd_can / 60000.0
        power_hp = 1.341 * power_kw

        # Work in hp-hr and kW-hr
        work_total = np.trapz(power_hp, x_time) / 3600.0
        work_total_kwh = np.trapz(power_kw, x_time) / 3600.0

        # Note: MATLAB labels '(kW-hr)' for can.workTotal even though it stores hp-hr. Preserve label for parity.
        _create_label(vehData, setIdx, np.array([work_total]), can["workTotal"], "(kW-hr)")
        _create_label(vehData, setIdx, power_kw, pems["enginePowerKw"], "(kW)")
        _create_label(vehData, setIdx, power_hp, pems["enginePowerHp"], "(HP)")

    # -------------------------------------------------------------- Vmix, STD (scfm)
    v_std = df[pems["scfm"]].to_numpy(dtype=float)  # ft^3 / min

    # -------------------------- Average ambient T and RH after 300 seconds
    t300_idx = int(round(300.0 / ts))
    amb_air_t, amb_air_t_meta = _get_data(vehData, setIdx, pems["ambientAirT"])
    amb_air_f = unit_convert(amb_air_t.astype(float), amb_air_t_meta.get("unit", ""), "F")
    avg_amb_air_t = float(np.mean(amb_air_f[t300_idx:])) if amb_air_f.size > t300_idx else float(np.nan)
    _create_label(vehData, setIdx, np.array([avg_amb_air_t]), pems["avgAmbT"], "(F)")

    amb_rh, amb_rh_meta = _get_data(vehData, setIdx, pems["rHumidity"])
    avg_rh = float(np.mean(amb_rh[t300_idx:])) if amb_rh.size > t300_idx else float(np.nan)
    _create_label(vehData, setIdx, np.array([avg_rh]), pems["avgAmbRH"], amb_rh_meta.get("unit", ""))

    # ------------------------- Pressure transducer (V -> psi)
    if bool(pems.get("enablePrTransducer", False)):
        pr_v, _ = _get_data(vehData, setIdx, pems["prTransducer"])
        pr_psi = float(pems["prTransSlope"]) * pr_v + float(pems["prTransInter"])
        _create_label(vehData, setIdx, pr_psi, pems["prTransPsi"], "psi")

    # ------------------------- PM optional flows (if active)
    if bool(pems.get("pm2Active", False)):
        # vSTD in m^3/s
        v_std_m3ps = v_std * (0.3048 ** 3) / 60.0
        v_std_total_m3 = float(np.trapz(v_std_m3ps, x_time))

        filter_flow = df[pems["pmFilterFlow"]].to_numpy(dtype=float)  # SLPM
        filter_m3ps = filter_flow / 1000.0 / 60.0
        filter_total_m3 = float(np.trapz(filter_m3ps, x_time))

        makeup_flow = df[pems["pmMakeupFlow"]].to_numpy(dtype=float)  # SLPM
        makeup_m3ps = makeup_flow / 1000.0 / 60.0
        makeup_total_m3 = float(np.trapz(makeup_m3ps, x_time))

        # pmTotal not stored in MATLAB, computed here for parity (unused)
        if filter_total_m3 > 0:
            pm_total = 0.012 * v_std_total_m3 / filter_total_m3
        else:
            pm_total = np.nan
        # pm_total is not assigned to vehData, matching MATLAB behavior

    # ================================================================  kNOx
    # NOx density at STD (g/ft^3)
    density_nox_std = 54.156

    # Concentration -> mole fraction 'conc'
    wet_knox = df[pems["wetkNOx"]].to_numpy(dtype=float)
    wet_knox_unit = _get_units(vehData, setIdx, pems["wetkNOx"])
    knox_conc = unit_convert(wet_knox, wet_knox_unit, "conc")

    # Mass flow (g/s): conc * Vstd(ft^3/min) * density(g/ft^3) / 60
    knox_mf = knox_conc * v_std * density_nox_std / 60.0
    _create_label(vehData, setIdx, knox_mf, pems["kNOxMassFlow"], "gm/s")

    # Cumulative kNOx (g)
    knox_sum = np.cumtrapz(knox_mf, x_time, initial=0.0)
    _create_label(vehData, setIdx, knox_sum, pems["kNOxSum"], "(gm)")

    # Total kNOx (g)
    knox_mass_tot = float(np.trapz(knox_mf, x_time))
    _create_label_scalar(vehData, setIdx, knox_mass_tot, pems["kNOxMassTotal"], "gm")

    # kNOx (g/mile)
    knox_gpm = (knox_mass_tot / dist_mi) if dist_mi > 0 else np.nan
    _create_label_scalar(vehData, setIdx, knox_gpm, pems["kNOxGmsPerMile"], "gm/mile")

    # kNOx mg/mile (LD only)
    if str(pems.get("vehWtClass", "")).upper() == "LD":
        knox_mgpm = knox_gpm * 1000.0 if np.isfinite(knox_gpm) else np.nan
        _create_label(vehData, setIdx, np.array([knox_mgpm]), pems["kNOxMgPerMile"], "(mg/mile)")

    # FTP-equivalent emissions for NOx
    def nest_ftp_equiv(em_mass_flow: np.ndarray) -> Tuple[float, float]:
        if idx_cold_trans.size == 0:
            y_ct = 0.0
        else:
            y_ct = float(np.trapz(em_mass_flow[idx_cold_trans], x_time[idx_cold_trans]))
        if idx_stabilized.size == 0:
            y_s = 0.0
        else:
            y_s = float(np.trapz(em_mass_flow[idx_stabilized], x_time[idx_stabilized]))
        # Proportion stabilized by actual stabilized distance
        ds = dist_stabil  # target stabilized distance (mi) for UDDS
        if dist_stabilized_mi > 0:
            y_s = y_s * (ds / dist_stabilized_mi)
        # CFR 86.144-94 weighting
        y_ht = 0.0
        d_ct = dist_cold_trans_mi
        d_ht = d_ct
        gpm = 0.43 * ((y_ct + y_s) / (d_ct + ds)) + 0.57 * ((y_ht + y_s) / (d_ht + ds)) if (d_ct + ds) > 0 else np.nan
        mgpm = 1000.0 * gpm if np.isfinite(gpm) else np.nan
        return gpm, mgpm

    knox_gpm_ftp, knox_mgpm_ftp = nest_ftp_equiv(knox_mf)
    _create_label(vehData, setIdx, np.array([knox_gpm_ftp]), pems["kNOxGmsPerMileFTP"], "gm/mile")
    _create_label(vehData, setIdx, np.array([knox_mgpm_ftp]), pems["kNOxMgPerMileFTP"], "mg/mile")

    if str(pems.get("vehWtClass", "")).upper() == "HD":
        # kNOx Brake-specific
        knox_bhp = (knox_mass_tot / work_total) if "work_total" in locals() and work_total > 0 else np.nan
        knox_kw = (knox_mass_tot / work_total_kwh) if "work_total_kwh" in locals() and work_total_kwh > 0 else np.nan
        _create_label(vehData, setIdx, np.array([knox_bhp]), pems["kNOxBrakeSpec"], "(gm/hp-hr)")
        _create_label(vehData, setIdx, np.array([knox_kw]), pems["kNOxBrakeSpecKw"], "(gm/kw-hr)")

        # Instantaneous brake-specific NOx (1 Hz only)
        if abs(ts - 1.0) < 1e-6:
            bhp, _ = _get_data(vehData, setIdx, pems["enginePowerHp"])
            kw, _ = _get_data(vehData, setIdx, pems["enginePowerKw"])
            with np.errstate(divide="ignore", invalid="ignore"):
                knox_inst_bhp = 3600.0 * (knox_mf / bhp)
                knox_inst_bkw = 3600.0 * (knox_mf / kw)
                # Trailing 200-sample moving average (equivalent to movmean(x,[199 0]))
                s_bhp = pd.Series(knox_inst_bhp)
                s_bkw = pd.Series(knox_inst_bkw)
                knox_movmean_bhp = s_bhp.rolling(window=200, min_periods=1).mean().to_numpy()
                knox_movmean_bkw = s_bkw.rolling(window=200, min_periods=1).mean().to_numpy()

            _create_label(vehData, setIdx, knox_inst_bhp, pems["knoxInstantBhp"], "(gm/hp-hr)")
            _create_label(vehData, setIdx, knox_inst_bkw, pems["knoxInstantBkw"], "(gm/kw-hr)")
            _create_label(vehData, setIdx, knox_movmean_bhp, pems["knoxMovMeanBhp"], "(gm/hp-hr)")
            _create_label(vehData, setIdx, knox_movmean_bkw, pems["knoxMovMeanBkw"], "(gm/kw-hr)")

    # ============================================================  kNOx Drift
    wet_knox_drift = df[pems["wetkNOxDrift"]].to_numpy(dtype=float)
    wet_knox_drift_unit = _get_units(vehData, setIdx, pems["wetkNOxDrift"])
    knox_conc_drift = unit_convert(wet_knox_drift, wet_knox_drift_unit, "conc")
    knox_mf_drift = knox_conc_drift * v_std * density_nox_std / 60.0
    _create_label(vehData, setIdx, knox_mf_drift, pems["kNOxMassFlowDrift"], "gm/s")

    knox_sum_drift = np.cumtrapz(knox_mf_drift, x_time, initial=0.0)
    _create_label(vehData, setIdx, knox_sum_drift, pems["kNOxSumDrift"], "(gm)")

    knox_mass_tot_drift = float(np.trapz(knox_mf_drift, x_time))
    _create_label_scalar(vehData, setIdx, knox_mass_tot_drift, pems["kNOxMassTotalDrift"], "gm")

    knox_gpm_drift = (knox_mass_tot_drift / dist_mi) if dist_mi > 0 else np.nan
    _create_label_scalar(vehData, setIdx, knox_gpm_drift, pems["kNOxGmsPerMileDrift"], "gm/mile")

    # =================================================================   CO
    density_co_std = 32.9725  # g/ft^3
    wet_co = df[pems["wetCO"]].to_numpy(dtype=float)
    wet_co_unit = _get_units(vehData, setIdx, pems["wetCO"])
    co_conc = unit_convert(wet_co, wet_co_unit, "conc")
    co_mf = co_conc * v_std * density_co_std / 60.0
    _create_label(vehData, setIdx, co_mf, pems["coMassFlow"], "gm/s")

    co_sum = np.cumtrapz(co_mf, x_time, initial=0.0)
    _create_label(vehData, setIdx, co_sum, pems["coSum"], "(gm)")

    co_mass_tot = float(np.trapz(co_mf, x_time))
    _create_label_scalar(vehData, setIdx, co_mass_tot, pems["coMassTotal"], "gm")

    co_gpm = (co_mass_tot / dist_mi) if dist_mi > 0 else np.nan
    _create_label_scalar(vehData, setIdx, co_gpm, pems["coGmsPerMile"], "gm/mile")

    co_gpm_ftp, co_mgpm_ftp = nest_ftp_equiv(co_mf)
    _create_label(vehData, setIdx, np.array([co_gpm_ftp]), pems["coGmsPerMileFTP"], "gm/mile")
    _create_label(vehData, setIdx, np.array([co_mgpm_ftp]), pems["coMgPerMileFTP"], "mg/mile")

    if str(pems.get("vehWtClass", "")).upper() == "HD":
        co_bhp = (co_mass_tot / work_total) if "work_total" in locals() and work_total > 0 else np.nan
        _create_label(vehData, setIdx, np.array([co_bhp]), pems["coBrakeSpec"], "(gm/hp-hr)")

    # ============================================================  CO Drift
    wet_co_drift = df[pems["wetCODrift"]].to_numpy(dtype=float)
    wet_co_drift_unit = _get_units(vehData, setIdx, pems["wetCODrift"])
    co_conc_drift = unit_convert(wet_co_drift, wet_co_drift_unit, "conc")
    co_mf_drift = co_conc_drift * v_std * density_co_std / 60.0
    _create_label(vehData, setIdx, co_mf_drift, pems["coMassFlowDrift"], "gm/s")

    co_sum_drift = np.cumtrapz(co_mf_drift, x_time, initial=0.0)
    _create_label(vehData, setIdx, co_sum_drift, pems["coSumDrift"], "(gm)")

    co_mass_tot_drift = float(np.trapz(co_mf_drift, x_time))
    _create_label_scalar(vehData, setIdx, co_mass_tot_drift, pems["coMassTotalDrift"], "gm")

    co_gpm_drift = (co_mass_tot_drift / dist_mi) if dist_mi > 0 else np.nan
    _create_label_scalar(vehData, setIdx, co_gpm_drift, pems["coGmsPerMileDrift"], "gm/mile")

    # =================================================================   CO2
    density_co2_std = 51.8064  # g/ft^3
    wet_co2 = df[pems["wetCO2"]].to_numpy(dtype=float)
    wet_co2_unit = _get_units(vehData, setIdx, pems["wetCO2"])
    co2_conc = unit_convert(wet_co2, wet_co2_unit, "conc")
    co2_mf = co2_conc * v_std * density_co2_std / 60.0
    _create_label(vehData, setIdx, co2_mf, pems["co2MassFlow"], "gm/s")

    co2_sum = np.cumtrapz(co2_mf, x_time, initial=0.0)
    _create_label(vehData, setIdx, co2_sum, pems["co2Sum"], "(gm)")

    co2_mass_tot = float(np.trapz(co2_mf, x_time))
    _create_label(vehData, setIdx, np.array([co2_mass_tot]), pems["co2MassTotal"], "(gm)")

    co2_gpm = (co2_mass_tot / dist_mi) if dist_mi > 0 else np.nan
    _create_label(vehData, setIdx, np.array([co2_gpm]), pems["co2GmsPerMile"], "(gm/mile)")

    if str(pems.get("vehWtClass", "")).upper() == "HD":
        co2_bhp = (co2_mass_tot / work_total) if "work_total" in locals() and work_total > 0 else np.nan
        _create_label(vehData, setIdx, np.array([co2_bhp]), pems["co2BrakeSpec"], "(gm/hp-hr)")

    co2_gpm_ftp, co2_mgpm_ftp = nest_ftp_equiv(co2_mf)
    _create_label(vehData, setIdx, np.array([co2_gpm_ftp]), pems["co2GmsPerMileFTP"], "gm/mile")
    _create_label(vehData, setIdx, np.array([co2_mgpm_ftp]), pems["co2MgPerMileFTP"], "mg/mile")

    # ============================================================  CO2 Drift
    wet_co2_drift = df[pems["wetCO2Drift"]].to_numpy(dtype=float)
    wet_co2_drift_unit = _get_units(vehData, setIdx, pems["wetCO2Drift"])
    co2_conc_drift = unit_convert(wet_co2_drift, wet_co2_drift_unit, "conc")
    co2_mf_drift = co2_conc_drift * v_std * density_co2_std / 60.0
    _create_label(vehData, setIdx, co2_mf_drift, pems["co2MassFlowDrift"], "gm/s")

    co2_sum_drift = np.cumtrapz(co2_mf_drift, x_time, initial=0.0)
    _create_label(vehData, setIdx, co2_sum_drift, pems["co2SumDrift"], "(gm)")

    co2_mass_tot_drift = float(np.trapz(co2_mf_drift, x_time))
    _create_label(vehData, setIdx, np.array([co2_mass_tot_drift]), pems["co2MassTotalDrift"], "(gm)")

    co2_gpm_drift = (co2_mass_tot_drift / dist_mi) if dist_mi > 0 else np.nan
    _create_label(vehData, setIdx, np.array([co2_gpm_drift]), pems["co2GmsPerMileDrift"], "(gm/mile)")

    # =================================================================   HC
    density_hc_std = 16.3336  # g/ft^3
    wet_hc = df[pems["wetHC"]].to_numpy(dtype=float)
    wet_hc_unit = _get_units(vehData, setIdx, pems["wetHC"])
    hc_conc = unit_convert(wet_hc, wet_hc_unit, "conc")
    hc_mf = hc_conc * v_std * density_hc_std / 60.0
    _create_label(vehData, setIdx, hc_mf, pems["hcMassFlow"], "gm/s")

    hc_sum = np.cumtrapz(hc_mf, x_time, initial=0.0)
    _create_label(vehData, setIdx, hc_sum, pems["hcSum"], "(gm)")

    hc_mass_tot = float(np.trapz(hc_mf, x_time))
    _create_label(vehData, setIdx, np.array([hc_mass_tot]), pems["hcMassTotal"], "(gm)")

    hc_gpm = (hc_mass_tot / dist_mi) if dist_mi > 0 else np.nan
    _create_label(vehData, setIdx, np.array([hc_gpm]), pems["hcGmsPerMile"], "(gm/mile)")

    if str(pems.get("vehWtClass", "")).upper() == "LD":
        hc_mgpm = hc_gpm * 1000.0 if np.isfinite(hc_gpm) else np.nan
        _create_label(vehData, setIdx, np.array([hc_mgpm]), pems["hcMgPerMile"], "(mg/mile)")

    hc_gpm_ftp, hc_mgpm_ftp = nest_ftp_equiv(hc_mf)
    _create_label(vehData, setIdx, np.array([hc_gpm_ftp]), pems["hcGmsPerMileFTP"], "gm/mile")
    _create_label(vehData, setIdx, np.array([hc_mgpm_ftp]), pems["hcMgPerMileFTP"], "mg/mile")

    if str(pems.get("vehWtClass", "")).upper() == "HD":
        hc_bhp = (hc_mass_tot / work_total) if "work_total" in locals() and work_total > 0 else np.nan
        _create_label(vehData, setIdx, np.array([hc_bhp]), pems["hcBrakeSpec"], "(gm/hp-hr)")

    if str(pems.get("vehWtClass", "")).upper() == "LD":
        # NMHC (mg/mile)
        nmhc_mgpm = hc_mgpm * 0.98 if "hc_mgpm" in locals() and np.isfinite(hc_mgpm) else np.nan
        _create_label(vehData, setIdx, np.array([nmhc_mgpm]), pems["nmhcMgPerMile"], "(mg/mile)")

        nmhc_mgpm_ftp = hc_mgpm_ftp * 0.98 if np.isfinite(hc_mgpm_ftp) else np.nan
        _create_label(vehData, setIdx, np.array([nmhc_mgpm_ftp]), pems["nmhcMgPerMileFTP"], "(mg/mile)")

        # NOx + NMHC (mg/mile)
        knox_mgpm = vehData[setIdx]["data"].get(pems["kNOxMgPerMile"], pd.Series([np.nan])).to_numpy()
        knox_mgpm_val = float(knox_mgpm[0]) if knox_mgpm.size > 0 else np.nan
        nox_plus = (knox_mgpm_val + nmhc_mgpm) if np.isfinite(knox_mgpm_val) and np.isfinite(nmhc_mgpm) else np.nan
        _create_label(vehData, setIdx, np.array([nox_plus]), pems["noxPlusMgPerMile"], "(mg/mile)")

        knox_mgpm_ftp_val = float(vehData[setIdx]["data"].get(pems["kNOxMgPerMileFTP"], pd.Series([np.nan])).to_numpy()[0])
        nox_plus_ftp = (knox_mgpm_ftp_val + nmhc_mgpm_ftp) if np.isfinite(knox_mgpm_ftp_val) and np.isfinite(nmhc_mgpm_ftp) else np.nan
        _create_label(vehData, setIdx, np.array([nox_plus_ftp]), pems["noxPlusMgPerMileFTP"], "(mg/mile)")

    # ============================================================  HC Drift
    wet_hc_drift = df[pems["wetHCDrift"]].to_numpy(dtype=float)
    wet_hc_drift_unit = _get_units(vehData, setIdx, pems["wetHCDrift"])
    hc_conc_drift = unit_convert(wet_hc_drift, wet_hc_drift_unit, "conc")
    hc_mf_drift = hc_conc_drift * v_std * density_hc_std / 60.0
    _create_label(vehData, setIdx, hc_mf_drift, pems["hcMassFlowDrift"], "gm/s")

    hc_sum_drift = np.cumtrapz(hc_mf_drift, x_time, initial=0.0)
    _create_label(vehData, setIdx, hc_sum_drift, pems["hcSumDrift"], "(gm)")

    hc_mass_tot_drift = float(np.trapz(hc_mf_drift, x_time))
    _create_label(vehData, setIdx, np.array([hc_mass_tot_drift]), pems["hcMassTotalDrift"], "(gm)")

    hc_gpm_drift = (hc_mass_tot_drift / dist_mi) if dist_mi > 0 else np.nan
    _create_label(vehData, setIdx, np.array([hc_gpm_drift]), pems["hcGmsPerMileDrift"], "(gm/mile)")

    # =================================================================   PM
    if bool(pems.get("pm2Active", False)):
        pm_mf = df[pems["pmMassTailpipe"]].to_numpy(dtype=float)  # ug/s
        pm_sum = np.cumtrapz(pm_mf, x_time, initial=0.0)          # ug
        _create_label(vehData, setIdx, pm_sum, pems["pmSum"], "(ug)")

    # ======= Exhaust Flow
    # Exhaust Vol Flow STP (m^3/min) from scfm
    scfm = df[pems["scfm"]].to_numpy(dtype=float)
    exh_flow_m3pm = scfm * 0.0283168  # ft^3/min -> m^3/min
    _create_label(vehData, setIdx, exh_flow_m3pm, pems["exhaustFlow"], "(m3/min)")

    # Cumulative Exhaust Flow (m^3) with flow per second
    flow_per_sec = exh_flow_m3pm / 60.0
    sum_flow = np.cumtrapz(flow_per_sec, x_time, initial=0.0)
    _create_label(vehData, setIdx, sum_flow, pems["sumExhFlow"], "(m3)")

    total_flow = float(np.trapz(flow_per_sec, x_time))
    _create_label_scalar(vehData, setIdx, total_flow, pems["totalExhFlow"], "m3")

    # ====== Fuel Economy (CFR 600.113-12 (h)(1))
    fuel_cfg = udp[setIdx]["fuel"]
    cwf = float(fuel_cfg["cwf"])
    sg = float(fuel_cfg["sg"])
    nhv = float(fuel_cfg["nhv"])

    # FE using CO2 only
    num_mpg_co2 = 5174e4 * cwf * sg
    den_mpg_co2 = (0.273 * co2_gpm) * ((0.6 * sg * nhv) + 5471.0) if np.isfinite(co2_gpm) else np.nan
    fe_co2 = num_mpg_co2 / den_mpg_co2 if np.isfinite(den_mpg_co2) and den_mpg_co2 != 0 else np.nan
    _create_label_scalar(vehData, setIdx, fe_co2, "Fuel_Economy_C02", "(mpg)")

    # FE using HC/CO/CO2
    num_mpg = 5174e4 * cwf * sg
    den_mpg = ((cwf * hc_gpm) + (0.429 * co_gpm) + (0.273 * co2_gpm)) * ((0.6 * sg * nhv) + 5471.0)
    fe = num_mpg / den_mpg if np.isfinite(den_mpg) and den_mpg != 0 else np.nan
    _create_label_scalar(vehData, setIdx, fe, pems["fuelEconomy"], "(mpg)")

    return vehData