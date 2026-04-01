% MATLAB script converted from the provided R code
% Implements windowing and emissions calculations per 40 CFR 1036.530
function [binIData, vehData] = Diesel_twoBinWithDT(setIdx,vehData,udp)

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
% binIData{8,n}: row 8:  mco2,norm,testinterval, Normalized CO2 mass over a
%                       300 second test interval according to 1036.530(e)
% binIData{9,n}: row 9:  bin number (1,2 or 0 for invalid)
tic

% --------------------------------------------------------------------------------
% 1036.530 (b)(2) - Engine coolant temperature at start
% Check the engine coolant temperature in the first 15 seconds at start is
% less than 40 C.
% --- Convert coolant temperature to C.
coolantTempUnit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.coolantT};
coolantTempC=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.coolantT),coolantTempUnit,'C');
vehData=createLabel(setIdx,coolantTempC,udp(setIdx).pems.coolantTC,'(C)',1);

% check if the temperature is below 40 in first 15 seconds of testing
coolantT15=coolantTempC(1:15);
below40Idx=find(coolantTempC<=40);

% check if 5 of the first 15 seconds is less than 40 C
if length(below40Idx) >=5
    disp('Coolant at start less than 40')
else
    disp('Coolant at start GREATER than 40')
    disp('Bin Emissions cannot be calculated')
end

% ------------------------------- Excluded Data 1036.530 (c)(3)

% --- Zero engine speed:  1036.530 (c)(3)(ii)
% No excection is made for 1036.415(g) start-stop and automatic engine
% shutdown systems.  Result is a logical which can be used as an index into
% engine speed.
include.engSpeed=vehData(setIdx).data.(udp(setIdx).pems.engineSpeed) > 0;
vehData=createLabel(setIdx,include.engSpeed,udp(setIdx).pems.includeEngSpeed,'(-)',1);

% udo.pems.regenStatus
% --- Infrequent Regeneration:  1036.530 (c)(3)(iii)
if ismember(udp(setIdx).pems.regenStatus, vehData(setIdx).data.Properties.VariableNames) == 0
    include.regen = false(height(vehData(setIdx).data), 1);
    vehData=createLabel(setIdx,include.regen,udp(setIdx).pems.regenStatus,'(-)',1);
    include.regen = false(height(vehData(setIdx).data), 1) < 1;
else
    include.regen=vehData(setIdx).data.(udp(setIdx).pems.regenStatus) < 1;
end
% endinclude.regen=vehData(setIdx).data.(udp(setIdx).pems.regenStatus) < 1;
vehData=createLabel(setIdx,include.regen,udp(setIdx).pems.includeRegen,'(-)',1);
% sum([include.regen] == 1)
%     'DPFRegenStatus'
% --- Tambient > Tmax: 1036.530 (c)(3)(iv)
ambientTempUnit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.ambientAirT};
ambientTempC=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.ambientAirT),ambientTempUnit,'C');
% 'LimitAdjustediSCB_LAT'
altitudeUnit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.altitude};
altitudeFt=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.altitude),altitudeUnit,'ft');
vehData=createLabel(setIdx,altitudeFt,udp(setIdx).pems.altitudeFt,'(ft)',1);
% LimitAdjustediGPS_ALT
TmaxC=-0.0014.*altitudeFt+37.78;
TmaxF=unitConvert(TmaxC,'C','F');

include.tMax=ambientTempC < TmaxC;
vehData=createLabel(setIdx,include.tMax,udp(setIdx).pems.includeTmax,'(-)',1);
vehData=createLabel(setIdx,TmaxC,udp(setIdx).pems.tMaxLimit,'(-)',1);


% --- Tambient > 5C: 1036.530 (c)(3)(iv)
include.ambient5C=ambientTempC > 5;
npts=length(vehData(setIdx).data.(udp(setIdx).pems.ambientAirT));
ambient5C=ones(npts,1).*5;

vehData=createLabel(setIdx,include.ambient5C,udp(setIdx).pems.includeAmbient5C,'(-)',1);
vehData=createLabel(setIdx,ambient5C,udp(setIdx).pems.ambientTLimit,'(-)',1);


% --- Altitude < 5500 ft  (1676.4 m)
include.altitude = altitudeFt < 5500;
altitude5500=ones(npts,1).*5500;

vehData=createLabel(setIdx,include.altitude,udp(setIdx).pems.includeAltitude,'(-)',1);
vehData=createLabel(setIdx,altitude5500,udp(setIdx).pems.altitudeLimit,'(-)',1);

% --- Combine all the Included points before checking for excluded points
% according to 1066.530(c)(3)(vii) when one good point is surrounded by two
% excluded points.
% Combine all the included points so far
include.total=include.engSpeed.*include.regen.*include.tMax.*include.ambient5C.*include.altitude;
% include.total=include.engSpeed.*include.tMax.*include.ambient5C.*include.altitude;
if sum(include.total > 0) == 0
    error('BIN:InvalidData', 'Cannot calculate BIN emission /w ALL invalid data');
end

% --- Exclude single data point surrounded by excluded points 1036.530(c)(3)(vii)
% (vii) A single data point does not meet any of the conditions specified in paragraphs (c)(3)(i) through (vi) of this section, 
% but it is preceded and followed by data points that both meet one or more of the specified exclusion conditions.
for n=2:length(include.total)-1
    if include.total(n-1)==0 && include.total(n+1)==0 && include.total(n)==1
        include.total(n)=0;
    end
end
vehData=createLabel(setIdx,include.total, udp(setIdx).pems.includeTotal,'(-)',1);

%% ==========================================
%% EPA MAW Emissions Analysis - MATLAB Script
%% Converted from Python
%% ==========================================

% clc; clear; close all;

%% ==========================================
%% 4. EXECUTION BLOCK (Main Script)
%% ==========================================

% rng(42);
% time_sec = 1200;

% --- Build base signal profiles via interpolation ---
raw = vehData.data;
rawCols = string(raw.Properties.VariableNames);
rawCols1 = rawCols.';
targets = ["LimitAdjustediSCB_LAT","LimitAdjusted iSCB_LAT","Temp_Amb"];
[tf, loc] = ismember(lower(targets), lower(rawCols));

foundNames   = targets(tf);
foundIdx     = loc(tf);
missingNames = targets(~tf);

% idx = find(contains(rawCols, "LimitAdjusted", 'IgnoreCase', true));
% matches = rawCols(idx);

% Find column name containing both substrings (case-insensitive)
idx = find(contains(rawCols, "LimitAdjusted", "IgnoreCase", true) & ...
           contains(rawCols, "_LAT",          "IgnoreCase", true), 1);

if isempty(idx)
    error('No column name contains both "LimitAdjusted" and "_LAT".');
end

% Set the column name to ambTempC (store the matched name)
AmbTempC_col = rawCols(idx);

% ---- Extract needed variables with flexible name handling ----
data.Time      = getColumn(raw, {'TIME'});
data.AmbTempC  = getColumn(raw, {AmbTempC_col, 'Temp_Amb'}); % ambientTempC
data.instCO    = getColumn(raw, {'CO_MassFlow','CO_Mass_Sec'});
data.instCO2   = getColumn(raw, {'CO2_MassFlow','CO2_Mass_Sec'});
data.instPM    = getColumn(raw, {'PM_Mass_Sec_Final','PM_Mass_sec_Final','PM_Mass_Sec','PM_Mass_sec'});
% PM: default to zeros if empty/omitted
if isempty(data.instPM)
    data.instPM = zeros(height(raw),1);
end
havePM = true;

data.instHC   = getColumn(raw, {'HC_MassFlow', 'THC_Mass_Sec'});
data.instNOx   = getColumn(raw, {'kNOx_MassFlow','NOX_Mass_sec_Final','NOX_Mass_Sec','NOX_Mass_sec'});
data.In_Regen     = toNumeric(getTextColumn(raw, {'DPFRegenStatus','Regen'}));
% ZeroCheck = getTextColumn(raw, {'Zero_Check_Flag','Zero_Check'});
data.Altitude_m = getColumn(raw, {'Altitude_Ft','Alt'})/3.28084;
data.Engine_RPM       = getColumn(raw, {'EngineRPM'});
data.Engine_Torque_Nm = getColumn(raw, {'DerivedEngineTorque'}); % DerivedEngineTorque_1
data.Engine_Torque_lb_ft = getColumn(raw, {'DerivedEngineTorque_1'}); % DerivedEngineTorque_1
data.Distance  = getColumn(raw, {'Cumulative_Distance_Miles', 'Distance'});
data.v_mph = getColumn(raw, {'Vehicle Speed', 'VehicleSpeedMPH', 'Veh_Speed'});

% t = (0:time_sec-1)';

% rpm_base    = interp1([0, 600, 1200], [1500, 600, 1500], t);
% torque_base = interp1([0, 600, 1200], [500,   20,  450], t);
% speed_base  = interp1([0, 600, 1200], [60,     0,   55], t);

% --- Build data table ---
% data.instNOx          = rand(time_sec,1) .* (0.02-0.005)  + 0.005;
% data.instNOx          = data.instNOx .* (torque_base/500 + 0.1);
% 
% data.instPM           = rand(time_sec,1) .* (0.001-0.0001) + 0.0001;
% data.instPM           = data.instPM  .* (torque_base/500 + 0.1);
% 
% data.instHC           = rand(time_sec,1) .* (0.005-0.001)  + 0.001;
% data.instHC           = data.instHC  .* (torque_base/500 + 0.1);
% 
% data.instCO           = rand(time_sec,1) .* (0.1-0.01)     + 0.01;
% data.instCO           = data.instCO  .* (torque_base/500 + 0.1);
% 
% data.instCO2          = rand(time_sec,1) .* (25.0-10.0)    + 10.0;
% data.instCO2          = data.instCO2 .* (torque_base/500 + 0.1);

% data.Engine_RPM       = max(rpm_base    + randn(time_sec,1)*20,  0);
% data.Engine_Torque_Nm = max(torque_base + randn(time_sec,1)*10,  0);
% data.v_mph            = max(speed_base  + randn(time_sec,1)*1,   0);
% data.AmbTempC         = repmat(20.0, time_sec, 1);
% data.Altitude_m       = repmat(200.0, time_sec, 1);
% data.In_Regen         = false(time_sec, 1);

% Simulate regen event between seconds 400-549
% data.In_Regen(401:550) = true;

% Convert struct to table
df = struct2table(data);

% --- Run Calculations ---
eco2_g_hp_hr = 507.0;
pmax_hp      = 505.0;

    % % Flag Excluded Data
    % df.Excluded_Data = (df.AmbTempC < -5) | (df.AmbTempC > (-0.0014*df.Altitude_ft)+37.78) | ...
    %                    (df.Altitude_ft > 5500) | (df.Engine_RPM < 1) | df.In_Regen; % df.In_Calibration
                   
% Define Regulatory Limits (Updated per user request)
epa_limits = struct();
epa_limits.Bin1_NOx_g_hr = 10.4;
epa_limits.Bin2_NOx_mg_hp_hr = 63.0;
epa_limits.Bin2_HC_mg_hp_hr = 130.0;
epa_limits.Bin2_PM_mg_hp_hr = 5.0;
epa_limits.Bin2_CO_g_hp_hr = 9.25;
epa_limits.Bin2_CO2_g_hp_hr = 600.0;

%% 2. RUN CALCULATIONS
[df, summary_df, windows_df, sub_interval_df, Invalid_count] = calculate_maw_and_subintervals(df, eco2_g_hp_hr, pmax_hp);

%% 3. EVALUATE COMPLIANCE & EXPORT
if ~isempty(summary_df)
    fprintf('\nTotal Invalid Windows (>599s Excluded): %d\n\n', Invalid_count);
    
    % Masks for explicit console printing
    bin1_mask = (windows_df.Bin == 1);
    bin2_mask = (windows_df.Bin == 2);
    
    fprintf('Explicit Bin 1 Averages (Bin == 1):\n');
    fprintf('NOx (g/hr): %.3f g/hr\n\n', mean(windows_df.Bin1_NOx_g_hr(bin1_mask), 'omitnan'));
    
    fprintf('Explicit Bin 2 Averages (Bin == 2):\n');
    fprintf('NOx: %.3f mg/hp-hr\n', mean(windows_df.Bin2_NOx_mg_hp_hr(bin2_mask), 'omitnan'));
    fprintf('HC:  %.3f mg/hp-hr\n', mean(windows_df.Bin2_HC_mg_hp_hr(bin2_mask), 'omitnan'));
    fprintf('PM:  %.3f mg/hp-hr\n', mean(windows_df.Bin2_PM_mg_hp_hr(bin2_mask), 'omitnan'));
    fprintf('CO:  %.3f g/hp-hr\n\n',  mean(windows_df.Bin2_CO_g_hp_hr(bin2_mask), 'omitnan'));
    
    overall_nox_mg_mi = (sum(df.instNOx) * 1000) / sum(df.Distance_mi);
    fprintf('Overall Dataset Averages (All Data Points):\n');
    fprintf('NOx (Distance): %.3f mg/mi\n\n', overall_nox_mg_mi);
    
    compliance_results = evaluate_compliance(summary_df, epa_limits);
    disp('--- EPA MAW Compliance Report ---');
    disp(compliance_results);
    
    % Export to CSV
    writetable(windows_df, 'maw_detailed_windows.csv');
    writetable(summary_df, 'maw_summary_averages.csv');
    writetable(compliance_results, 'maw_compliance_report.csv');
    writetable(sub_interval_df, 'sub_intervals_summary.csv');
    disp('✅ Success: Data exported to CSV files in the current directory.');
else
    disp('Error: No valid MAW data could be generated.');
end

%% 4. GENERATE PLOTS
disp('Generating visual analytics...');
plot_shift_day_emissions(df);
plot_cumulative_emissions(df);


% =========================================================================
% FUNCTIONS
% =========================================================================

function [df, summary, windows_df, sub_summary, Invalid_count] = calculate_maw_and_subintervals(df, eco2_g_hp_hr, pmax_hp)
    % Base Engine Calculations
    df.EnginePower_hp = (df.Engine_Torque_Nm .* df.Engine_RPM) / 7120.8;
    df.Altitude_ft = df.Altitude_m * 3.28084;
    df.Distance_mi = df.v_mph / 3600.0;
    
    % Flag Excluded Data
    df.Excluded_Data = (df.AmbTempC < -5) | (df.AmbTempC > (-0.0014*df.Altitude_ft)+37.78) | ...
                       (df.Altitude_ft > 5500) | (df.Engine_RPM < 1) | df.In_Regen; % df.In_Calibration
               
    % Identify and re-classify isolated valid points (surrounded by excluded data)
    excl = df.Excluded_Data;
    shift_fwd = [true; excl(1:end-1)]; % True at start to handle boundary
    shift_bwd = [excl(2:end); true];   % True at end to handle boundary
    isolated_valid = shift_fwd & shift_bwd & ~excl;
    df.Excluded_Data(isolated_valid) = true;
                   
    % Grouping continuous sub-intervals
    df.Sub_Interval_ID = cumsum(df.Excluded_Data);
    
    % Extract valid data for sub-interval summary
    valid_idx_list = find(~df.Excluded_Data);
    valid_df = df(valid_idx_list, :);
    valid_df.Original_Time_Sec = valid_idx_list;
    
    if isempty(valid_df)
        summary = table(); windows_df = table(); sub_summary = table(); Invalid_count = 0;
        return;
    end
    
    % Sub-Interval Summary Calculation
    [Grp, sub_IDs] = findgroups(valid_df.Sub_Interval_ID);
    Duration_sec = splitapply(@numel, valid_df.EnginePower_hp, Grp);
    Avg_Power_hp = splitapply(@mean, valid_df.EnginePower_hp, Grp);
    Work_hp_hr   = splitapply(@(x) sum(x)/3600, valid_df.EnginePower_hp, Grp);
    Distance_mi  = splitapply(@sum, valid_df.Distance_mi, Grp);
    NOx_g        = splitapply(@sum, valid_df.instNOx, Grp);
    PM_g         = splitapply(@sum, valid_df.instPM, Grp);
    HC_g         = splitapply(@sum, valid_df.instHC, Grp);
    CO_g         = splitapply(@sum, valid_df.instCO, Grp);
    CO2_g        = splitapply(@sum, valid_df.instCO2, Grp);
    
    sub_summary = table(sub_IDs, Duration_sec, Avg_Power_hp, Work_hp_hr, Distance_mi, ...
                        NOx_g, PM_g, HC_g, CO_g, CO2_g);
    sub_summary.Properties.VariableNames{1} = 'Sub_Interval_ID';

    % MAW Window Generation 
    total_points = height(df);
    num_valid = length(valid_idx_list);
    
    if num_valid < 300
        summary = table(); windows_df = table(); Invalid_count = 0;
        warning('Dataset too short. Need at least 300 valid seconds.');
        return;
    end
    
    % Create reverse mapping: chrono_to_valid maps chronological index -> valid position index
    chrono_to_valid = zeros(total_points, 1);
    chrono_to_valid(valid_idx_list) = 1:num_valid;
    
    max_possible_windows = total_points;
    
    % Preallocate Arrays for MAW Windows (Numeric Bin array)
    Window_Index = zeros(max_possible_windows, 1);
    Window_Start_Time = zeros(max_possible_windows, 1);
    Window_End_Time = zeros(max_possible_windows, 1);
    Excluded_Samples_Count = zeros(max_possible_windows, 1);
    Total_Work_hp_hr = zeros(max_possible_windows, 1);
    Total_Distance_mi = zeros(max_possible_windows, 1);
    eCO2norm_percent = zeros(max_possible_windows, 1);
    Bin = zeros(max_possible_windows, 1); % 0=Invalid, 1=Bin1, 2=Bin2
    Bin1_NOx_g_hr = NaN(max_possible_windows, 1);
    Bin2_NOx_mg_hp_hr = NaN(max_possible_windows, 1);
    Bin2_HC_mg_hp_hr = NaN(max_possible_windows, 1);
    Bin2_PM_mg_hp_hr = NaN(max_possible_windows, 1);
    Bin2_CO_g_hp_hr = NaN(max_possible_windows, 1);
    Bin2_CO2_g_hp_hr = NaN(max_possible_windows, 1);
    NOx_mg_mi = NaN(max_possible_windows, 1);
    HC_mg_mi = NaN(max_possible_windows, 1);
    PM_mg_mi = NaN(max_possible_windows, 1);
    CO_g_mi = NaN(max_possible_windows, 1);
    CO2_g_mi = NaN(max_possible_windows, 1);
    
    bin2_denom = eco2_g_hp_hr * pmax_hp;
    Invalid_count = 0; 
    w_idx = 0; % Track actual stored windows
    
    for i = 1:(total_points - 1)
        % Ensure the window starts with two consecutive VALID points
        if df.Excluded_Data(i) || df.Excluded_Data(i+1)
            continue; 
        end
        
        % Map chronological index 'i' to its valid_idx position
        v_start = chrono_to_valid(i);
        
        % Ensure there are at least 300 valid points remaining
        if v_start + 299 > num_valid
            break; % Stop loop if we can no longer form a 300-point valid window
        end
        
        % Find the chronological index of the 300th valid point
        j = valid_idx_list(v_start + 299);
        valid_end = false;
        valid_samples_count = 300;
        
        % Check if 300th valid point is preceded by a valid point (j-1 is valid)
        if ~df.Excluded_Data(j-1)
            valid_end = true;
        
        % If not, check if we can extend to 301 valid points to end on a consecutive pair
        elseif (v_start + 300 <= num_valid)
            j_301 = valid_idx_list(v_start + 300);
            if ~df.Excluded_Data(j_301-1)
                j = j_301;
                valid_end = true;
                valid_samples_count = 301;
            end
        end
        
        if valid_end
            w_idx = w_idx + 1;
            
            % Extract the chronological window
            window_full = df(i : j, :);
            
            % Isolate only the valid points for the emissions summations
            win_valid = window_full(~window_full.Excluded_Data, :);
            
            time_start = i;
            time_end = j;
            excluded_count = sum(window_full.Excluded_Data);
            
            t_CO2 = sum(win_valid.instCO2);
            t_NOx = sum(win_valid.instNOx);
            t_PM  = sum(win_valid.instPM);
            t_HC  = sum(win_valid.instHC);
            t_CO  = sum(win_valid.instCO);
            
            t_work = sum(win_valid.EnginePower_hp) / 3600.0;
            t_dist = sum(win_valid.Distance_mi);
            
            eCO2norm_pct = (t_CO2 / bin2_denom * valid_samples_count/3600) * 100;
            
            if t_dist > 0
                n_mi = (t_NOx * 1000) / t_dist;
                h_mi = (t_HC * 1000) / t_dist;
                p_mi = (t_PM * 1000) / t_dist;
                c_mi = t_CO / t_dist;
                c2_mi = t_CO2 / t_dist;
            else
                n_mi = NaN; h_mi = NaN; p_mi = NaN; c_mi = NaN; c2_mi = NaN;
            end
            
            % Binning logic (Using Integers: 0=Invalid, 1=Bin1, 2=Bin2)
            if excluded_count > 599
                bin_label = 0; 
                Invalid_count = Invalid_count + 1; 
            else
                % Calculate NOx (g/hr) universally for all valid windows                
                if eCO2norm_pct < 6.0
                    bin_label = 1; 
                    Bin1_NOx_g_hr(w_idx) = t_NOx * (3600.0 / valid_samples_count);
                else
                    bin_label = 2; 
                    Bin2_NOx_mg_hp_hr(w_idx) = (t_NOx * 1000) / t_CO2 * eco2_g_hp_hr;
                    Bin2_HC_mg_hp_hr(w_idx)  = (t_HC * 1000) / t_CO2 * eco2_g_hp_hr;
                    Bin2_PM_mg_hp_hr(w_idx)  = (t_PM * 1000) / t_CO2 * eco2_g_hp_hr;
                    Bin2_CO_g_hp_hr(w_idx)   = t_CO / t_CO2 * eco2_g_hp_hr;
                    Bin2_CO2_g_hp_hr(w_idx)  = t_CO2 / t_CO2 * eco2_g_hp_hr;
                end
            end
            
            % Store
            Window_Index(w_idx) = i; Window_Start_Time(w_idx) = time_start; Window_End_Time(w_idx) = time_end;
            Excluded_Samples_Count(w_idx) = excluded_count; Total_Work_hp_hr(w_idx) = t_work;
            Total_Distance_mi(w_idx) = t_dist; eCO2norm_percent(w_idx) = eCO2norm_pct; Bin(w_idx) = bin_label;
            NOx_mg_mi(w_idx) = n_mi; HC_mg_mi(w_idx) = h_mi; PM_mg_mi(w_idx) = p_mi; CO_g_mi(w_idx) = c_mi; CO2_g_mi(w_idx) = c2_mi;
        end
    end
    
    if w_idx == 0
        summary = table(); windows_df = table();
        warning('No valid windows found that met the boundary criteria.');
        return;
    end
    
    % Truncate preallocated arrays to actual size
    windows_df = table(Window_Index(1:w_idx), Window_Start_Time(1:w_idx), Window_End_Time(1:w_idx), Excluded_Samples_Count(1:w_idx), ...
                       Total_Work_hp_hr(1:w_idx), Total_Distance_mi(1:w_idx), eCO2norm_percent(1:w_idx), Bin(1:w_idx), ...
                       Bin1_NOx_g_hr(1:w_idx), Bin2_NOx_mg_hp_hr(1:w_idx), Bin2_HC_mg_hp_hr(1:w_idx), Bin2_PM_mg_hp_hr(1:w_idx), ...
                       Bin2_CO_g_hp_hr(1:w_idx), Bin2_CO2_g_hp_hr(1:w_idx), NOx_mg_mi(1:w_idx), HC_mg_mi(1:w_idx), PM_mg_mi(1:w_idx), ...
                       CO_g_mi(1:w_idx), CO2_g_mi(1:w_idx));
                   
    % Rename columns automatically generated by MATLAB array truncation
    windows_df.Properties.VariableNames = {'Window_Index', 'Window_Start_Time', 'Window_End_Time', 'Excluded_Samples_Count', ...
                                           'Total_Work_hp_hr', 'Total_Distance_mi', 'eCO2norm_percent', 'Bin', ...
                                           'Bin1_NOx_g_hr', 'Bin2_NOx_mg_hp_hr', 'Bin2_HC_mg_hp_hr', 'Bin2_PM_mg_hp_hr', ...
                                           'Bin2_CO_g_hp_hr', 'Bin2_CO2_g_hp_hr', 'NOx_mg_mi', 'HC_mg_mi', 'PM_mg_mi', 'CO_g_mi', 'CO2_g_mi'};
                   
    % Filter out InValid (0) for summary averages
    valid_wins = windows_df(windows_df.Bin ~= 0, :);
    
    if isempty(valid_wins)
        summary = table();
        return;
    end
    
    % Aggregation for Summary Table
    [G_bin, Bin_Labels] = findgroups(valid_wins.Bin);
    
    % Standard Grouped Metrics using splitapply
    Total_Windows = splitapply(@numel, valid_wins.eCO2norm_percent, G_bin);
    Avg_eCO2norm_Percent = splitapply(@(x) mean(x,'omitnan'), valid_wins.eCO2norm_percent, G_bin);
    
    Avg_HC_mg_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.HC_mg_mi, G_bin);
    Avg_PM_mg_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.PM_mg_mi, G_bin);
    Avg_CO_g_mi  = splitapply(@(x) mean(x,'omitnan'), valid_wins.CO_g_mi, G_bin);
    Avg_CO2_g_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.CO2_g_mi, G_bin);

    % =====================================================================
    % Explicit Calculations using Bin mapping
    % =====================================================================
    num_groups = length(Bin_Labels);
    Avg_Bin1_NOx_g_hr     = NaN(num_groups, 1);
    Avg_Bin2_NOx_mg_hp_hr = NaN(num_groups, 1);
    Avg_Bin2_HC_mg_hp_hr  = NaN(num_groups, 1);
    Avg_Bin2_PM_mg_hp_hr  = NaN(num_groups, 1);
    Avg_Bin2_CO_g_hp_hr   = NaN(num_groups, 1);
    Avg_Bin2_CO2_g_hp_hr  = NaN(num_groups, 1);
    
    % Global calculation for NOx_mg_mi using ALL dataset points (including excluded/invalid)
    overall_nox_mg_mi = (sum(df.instNOx) * 1000) / sum(df.Distance_mi);
    Avg_NOx_mg_mi = repmat(overall_nox_mg_mi, num_groups, 1); 
    
    % Create explicit mask for Bin == 1
    idx_bin1 = find(Bin_Labels == 1);
    if ~isempty(idx_bin1)
        bin1_mask = (valid_wins.Bin == 1);
        Avg_Bin1_NOx_g_hr(idx_bin1) = mean(valid_wins.Bin1_NOx_g_hr(bin1_mask), 'omitnan');
    end

    % Create explicit mask for Bin == 2
    idx_bin2 = find(Bin_Labels == 2);
    if ~isempty(idx_bin2)
        bin2_mask = (valid_wins.Bin == 2);
        Avg_Bin2_NOx_mg_hp_hr(idx_bin2) = mean(valid_wins.Bin2_NOx_mg_hp_hr(bin2_mask), 'omitnan');
        Avg_Bin2_HC_mg_hp_hr(idx_bin2)  = mean(valid_wins.Bin2_HC_mg_hp_hr(bin2_mask), 'omitnan');
        Avg_Bin2_PM_mg_hp_hr(idx_bin2)  = mean(valid_wins.Bin2_PM_mg_hp_hr(bin2_mask), 'omitnan');
        Avg_Bin2_CO_g_hp_hr(idx_bin2)   = mean(valid_wins.Bin2_CO_g_hp_hr(bin2_mask), 'omitnan');
        Avg_Bin2_CO2_g_hp_hr(idx_bin2)  = mean(valid_wins.Bin2_CO2_g_hp_hr(bin2_mask), 'omitnan');
    end
    % =====================================================================
    
    summary = table(Bin_Labels, Total_Windows, Avg_eCO2norm_Percent, Avg_Bin1_NOx_g_hr, ...
                    Avg_Bin2_NOx_mg_hp_hr, Avg_Bin2_HC_mg_hp_hr, Avg_Bin2_PM_mg_hp_hr, ...
                    Avg_Bin2_CO_g_hp_hr, Avg_Bin2_CO2_g_hp_hr, Avg_NOx_mg_mi, Avg_HC_mg_mi, ...
                    Avg_PM_mg_mi, Avg_CO_g_mi, Avg_CO2_g_mi);
    summary.Properties.VariableNames{1} = 'Bin';
end

function comp_table = evaluate_compliance(summary_df, limits)
    Bin_Str = strings(0,1); Metric = strings(0,1); 
    Actual_Average = []; Regulatory_Limit = []; Status = strings(0,1);
    
    idx = 1;
    for i = 1:height(summary_df)
        b_label = summary_df.Bin(i);
        if b_label == 1
            Bin_Str(idx,1) = "Bin 1"; Metric(idx,1) = "NOx (g/hr)";
            Actual_Average(idx,1) = summary_df.Avg_Bin1_NOx_g_hr(i);
            Regulatory_Limit(idx,1) = limits.Bin1_NOx_g_hr;
            if Actual_Average(idx,1) <= Regulatory_Limit(idx,1), Status(idx,1) = "PASS"; else, Status(idx,1) = "FAIL"; end
            idx = idx + 1;
        elseif b_label == 2
            mets = {"NOx (mg/hp-hr)", "Avg_Bin2_NOx_mg_hp_hr", limits.Bin2_NOx_mg_hp_hr;
                    "HC (mg/hp-hr)",  "Avg_Bin2_HC_mg_hp_hr",  limits.Bin2_HC_mg_hp_hr;
                    "PM (mg/hp-hr)",  "Avg_Bin2_PM_mg_hp_hr",  limits.Bin2_PM_mg_hp_hr;
                    "CO (g/hp-hr)",   "Avg_Bin2_CO_g_hp_hr",   limits.Bin2_CO_g_hp_hr;
                    "CO2 (g/hp-hr)",  "Avg_Bin2_CO2_g_hp_hr",  limits.Bin2_CO2_g_hp_hr};
            for k = 1:size(mets, 1) 
                Bin_Str(idx,1) = "Bin 2"; Metric(idx,1) = mets{k,1};
                Actual_Average(idx,1) = summary_df.(mets{k,2})(i);
                Regulatory_Limit(idx,1) = mets{k,3};
                if Actual_Average(idx,1) <= Regulatory_Limit(idx,1), Status(idx,1) = "PASS"; else, Status(idx,1) = "FAIL"; end
                idx = idx + 1;
            end
        end
    end
    comp_table = table(Bin_Str, Metric, round(Actual_Average,3), Regulatory_Limit, Status, ...
        'VariableNames', {'Bin', 'Metric', 'Actual_Average', 'Regulatory_Limit', 'Status'});
end

function plot_shift_day_emissions(df)
    time_sec = height(df);
    t = 1:time_sec;
    
    figure('Position', [100, 100, 1000, 600], 'Name', 'Shift-Day Emissions');
    
    % Helper to draw red exclusion zones
    function draw_excluded(ax)
        hold(ax, 'on');
        diff_excl = diff([0; double(df.Excluded_Data); 0]);
        start_idx = find(diff_excl == 1);
        end_idx = find(diff_excl == -1) - 1;
        y_lims = ylim(ax);
        for k = 1:length(start_idx)
            patch(ax, [start_idx(k)-0.5, end_idx(k)+0.5, end_idx(k)+0.5, start_idx(k)-0.5], ...
                  [y_lims(1), y_lims(1), y_lims(2), y_lims(2)], ...
                  'r', 'FaceAlpha', 0.2, 'EdgeColor', 'none', 'HandleVisibility', 'off');
        end
    end

    % SUBPLOT 1: Engine Power & Excluded Regions
    ax1 = subplot(2,1,1);
    plot(ax1, t, df.EnginePower_hp, 'Color', '#0072BD', 'LineWidth', 1.5, 'DisplayName', 'Engine Power (hp)');
    ylabel('Engine Power (hp)'); title('Engine Test Data: Valid vs. Excluded Regions');
    grid on; xlim([0 time_sec]);
    draw_excluded(ax1);
    
    % Dummy patch for legend
    patch(NaN, NaN, 'r', 'FaceAlpha', 0.2, 'EdgeColor', 'none', 'DisplayName', 'Excluded Data');
    legend('Location', 'northeast');
    
    % SUBPLOT 2: Vehicle Speed and Instantaneous CO2 (Dual Axis)
    ax2 = subplot(2,1,2);
    yyaxis(ax2, 'left');
    plot(ax2, t, df.v_mph, 'Color', '#77AC30', 'LineWidth', 2, 'DisplayName', 'Vehicle Speed (mph)');
    ylabel('Vehicle Speed (mph)');
    ax2.YColor = '#77AC30';
    
    yyaxis(ax2, 'right');
    plot(ax2, t, df.instCO2, 'Color', '#D95319', 'LineWidth', 1.5, 'DisplayName', 'Inst. CO2 (g/s)');
    ylabel('Instantaneous CO2 (g/s)');
    ax2.YColor = '#D95319';
    
    xlabel('Time (seconds)'); grid on; xlim([0 time_sec]);
    draw_excluded(ax2);
    legend('Location', 'northwest');
end

function plot_cumulative_emissions(df)
    valid_df = df(~df.Excluded_Data, :);
    
    valid_df.Cum_NOx_g = cumsum(valid_df.instNOx);
    valid_df.Cum_CO2_g = cumsum(valid_df.instCO2);
    valid_df.Cum_Work_hp_hr = cumsum(valid_df.EnginePower_hp / 3600.0);
    
    % Calculate running Brake-Specific NOx (g/hp-hr)
    bs_nox = zeros(height(valid_df), 1);
    idx_pos = valid_df.Cum_Work_hp_hr > 0;
    bs_nox(idx_pos) = valid_df.Cum_NOx_g(idx_pos) ./ valid_df.Cum_Work_hp_hr(idx_pos);
    valid_df.BS_NOx_g_hp_hr = bs_nox;
    
    t_valid = find(~df.Excluded_Data);
    
    figure('Position', [150, 150, 1000, 600], 'Name', 'Cumulative Emissions');
    
    % SUBPLOT 1: Cumulative Mass (Grams)
    ax1 = subplot(2,1,1);
    yyaxis(ax1, 'left');
    plot(ax1, t_valid, valid_df.Cum_NOx_g, 'Color', '#A2142F', 'LineWidth', 2, 'DisplayName', 'Cumulative NOx (g)');
    ylabel('Cumulative NOx (g)'); ax1.YColor = '#A2142F';
    title('Cumulative Emissions Accrual During Valid Testing');
    
    yyaxis(ax1, 'right');
    plot(ax1, t_valid, valid_df.Cum_CO2_g, '--', 'Color', '#7E2F8E', 'LineWidth', 2, 'DisplayName', 'Cumulative CO2 (g)');
    ylabel('Cumulative CO2 (g)'); ax1.YColor = '#7E2F8E';
    grid on; legend('Location', 'northwest');
    
    % SUBPLOT 2: Cumulative Brake-Specific Running Average
    ax2 = subplot(2,1,2);
    plot(ax2, t_valid, valid_df.BS_NOx_g_hp_hr, 'Color', '#0072BD', 'LineWidth', 2, 'DisplayName', 'Running Avg BS NOx');
    hold on;
    final_avg = valid_df.BS_NOx_g_hp_hr(end);
    yline(ax2, final_avg, 'k:', 'LineWidth', 1.5, 'DisplayName', sprintf('Final Avg: %.3f g/hp-hr', final_avg));
    
    xlabel('Time (Original Second of Shift)'); ylabel('Cum. BS NOx (g/hp-hr)');
    grid on; legend('Location', 'northeast');
end

function A = trapz_omitnan(x, y)
    if nargin < 2
        y = x;
        x = (1:numel(y))';
    end
    x = x(:); y = y(:);
    mask = isfinite(x) & isfinite(y);
    ok = mask(1:end-1) & mask(2:end);
    A = sum(0.5 .* (y(1:end-1) + y(2:end)) .* diff(x) .* ok);
end

% --------------------------------------
% ----------------------------------------   Interval Calculations

% intervals defined in CFR 1036.530(c)(2) must be 300 second of Not
% excluded (included) data and must begin and end with two consecutive
% points of included data.  Intervals are determined using a
% moving/expanding window.  The window is initialized with 300 seconds of
% data containing potentially both excluded and included data.  The window
% moves forward until two consecutive included points are found.  The end
% point of the window then expands until the window includes 300 seconds of
% included data.  A nested function (getWinTime) calculates the total time
% of included data in the window.  The calculated total time in the window
% does not increase unless two consective points are included data are found.
% This ensures the end points of the window contains two consecutive points of
% included data.

% --- Initialize Variables
% idxStart=1;     % index for start of moving window referenced to entire test.
% idxEnd=0;       % index for end of moving window reference to entire test.
% numInt=0;                       % Number of Intervals (both valid and invalid)
% endTest=length(include.total);  % index for the end of test.
% testCycleTime=vehData(setIdx).data.(udp(setIdx).pems.time);  % time associated with Include.Total
% testCycleCO2massFlow=vehData(setIdx).data.(udp(setIdx).pems.co2MassFlow); % get CO2 mass flow for entire test cycle
% includeTotal=include.total;         % logical for included/excluded (0/1) for entire test
% 
% % clearvars; clc;
% % 
% % % ---- User inputs ----
% % filename = 'C:\Users\slee02\Matlab\RoadaC\Morgan\2022 0814 101057   hcexh0408bat   255   1hz.csv';
% 
% % Engine-family-specific inputs
% eCO2 = 507;   % g/hp.hr, from 1036.104(a)(3) for heavy heavy duty engines
% PMax = 505;   % hp, from 1036.104(a)(3) for heavy heavy duty engines, also found in PEMS data
% % 
% eCO2 = 900;   % g/hp.hr, from 1036.104(a)(3) for heavy heavy duty engines
% PMax = 430;   % hp, from 1036.104(a)(3) for heavy heavy duty engines, also found in PEMS data
% % eCO2 = udp(setIdx).bins.eco2fcl;
% % PMax = udp(setIdx).bins.pmax;
% % timeIntHr
% 
% % udo.bins.pmax=505;                  % HP, see CFR 1036.530 (e)
% % udo.bins.eco2fcl=507;               % gm/hp*hr,  see see CFR 1036.530 (e)
% 
% % Convert 300 s to hours for calculations (Eq. 1036.530-2)
% tInt = 300/3600;
% 
% raw = vehData.data;
% 
% % ---- Read data ----
% % hdr = readcell(filename, 'Range', '2:2');
% % hdr = string(hdr);
% % hdr = matlab.lang.makeValidName(hdr); % ensure valid variable names
% % 
% % % Read data from row 3 onward without using file headers
% % opts = detectImportOptions(filename);
% % opts.DataLines = [3, Inf];
% % raw = readtable(filename, opts, 'ReadVariableNames', false);
% % 
% % % Assign the headers from row 2
% % raw.Properties.VariableNames = cellstr(hdr);
% 
% % raw = readtable(filename, opts);
% 
% % If first column name isn't "Local_Time", mimic R logic to adjust headers
% if ~strcmp(raw.Properties.VariableNames{1}, 'TIME')
%     % Remove first row
%     if height(raw) < 2
%         error('File is too short to adjust headers.');
%     end
%     raw(1,:) = [];
%     % Set names from (new) first row
%     newNames = cellstr(string(raw{1,:}));
%     raw.Properties.VariableNames = matlab.lang.makeValidName(newNames);
%     % Remove that header row
%     raw(1,:) = [];
% end
% 
% % Get the column names from a table
% rawCols = string(raw.Properties.VariableNames);
% rawCols1 = rawCols.';
% targets = ["LimitAdjustediSCB_LAT","LimitAdjusted iSCB_LAT","Temp_Amb"];
% [tf, loc] = ismember(lower(targets), lower(rawCols));
% 
% foundNames   = targets(tf);
% foundIdx     = loc(tf);
% missingNames = targets(~tf);
% 
% % idx = find(contains(rawCols, "LimitAdjusted", 'IgnoreCase', true));
% % matches = rawCols(idx);
% 
% % Find column name containing both substrings (case-insensitive)
% idx = find(contains(rawCols, "LimitAdjusted", "IgnoreCase", true) & ...
%            contains(rawCols, "_LAT",          "IgnoreCase", true), 1);
% 
% if isempty(idx)
%     error('No column name contains both "LimitAdjusted" and "_LAT".');
% end
% 
% % Set the column name to ambTempC (store the matched name)
% AmbTempC_col = rawCols(idx);
% 
% % ---- Extract needed variables with flexible name handling ----
% Time      = getColumn(raw, {'TIME'});
% AmbTempC  = getColumn(raw, {AmbTempC_col, 'Temp_Amb'}); % ambientTempC
% InstCO    = getColumn(raw, {'CO_MassFlow','CO_Mass_Sec'});
% InstCO2   = getColumn(raw, {'CO2_MassFlow','CO2_Mass_Sec'});
% % InstPM    = getColumn(raw, {'PM_Mass_Sec_Final','PM_Mass_sec_Final','PM_Mass_Sec','PM_Mass_sec'});
% InstTHC   = getColumn(raw, {'HC_MassFlow', 'THC_Mass_Sec'});
% InstNOx   = getColumn(raw, {'kNOx_MassFlow','NOX_Mass_sec_Final','NOX_Mass_Sec','NOX_Mass_sec'});
% Regen     = getTextColumn(raw, {'DPFRegenStatus','Regen'});
% % ZeroCheck = getTextColumn(raw, {'Zero_Check_Flag','Zero_Check'});
% ElevationFt = getColumn(raw, {'Altitude_Ft','Alt'});
% RPM       = getColumn(raw, {'EngineRPM'});
% Distance  = getColumn(raw, {'Cumulative_Distance_Miles', 'Distance'});
% v_mph = getColumn(raw, {'Vehicle Speed', 'VehicleSpeedMPH', 'Veh_Speed'});
% 
% % Time      = getColumn(raw, {'Local_Time'});
% % AmbTempF  = getColumn(raw, {'Temp_Amb'});
% % InstCO    = getColumn(raw, {'CO_Mass_Sec','CO_Mass_sec'});
% % InstCO2   = getColumn(raw, {'CO2_Mass_sec','CO2_Mass_Sec'});
% % InstPM    = getColumn(raw, {'PM_Mass_Sec_Final','PM_Mass_sec_Final','PM_Mass_Sec','PM_Mass_sec'});
% % InstTHC   = getColumn(raw, {'THC_Mass_Sec','THC_Mass_sec'});
% % InstNOx   = getColumn(raw, {'NOX_Mass_Sec_Final','NOX_Mass_sec_Final','NOX_Mass_Sec','NOX_Mass_sec'});
% % Regen     = getTextColumn(raw, {'Regen_Signal','Regen'});
% % ZeroCheck = getTextColumn(raw, {'Zero_Check_Flag','Zero_Check'});
% % AltitudeM = getColumn(raw, {'Altitude','Alt'});
% % RPM       = getColumn(raw, {'RPM'});
% % Distance  = getColumn(raw, {'Distance'});
% 
% 
% n = height(raw);
% 
% % % ---- Unit conversions ----
% % AmbTempC = (toNumeric(AmbTempF) - 32) * (5/9);
% % ElevationFt = toNumeric(AltitudeM) * 3.281;
% % 
% % % Compute Tamb (used for temperature adjustment)
% Tamb = mean(AmbTempC, 'omitnan');
% % 
% % Ensure numeric
% InstCO2 = toNumeric(InstCO2);
% InstNOx = toNumeric(InstNOx);
% InstCO  = toNumeric(InstCO);
% % InstPM  = toNumeric(InstPM);
% InstTHC = toNumeric(InstTHC);
% RPM     = toNumeric(RPM);
% % 
% % % ---- Exclusion logic per 40 CFR 1036.530(c)(3)(i–vii) ----
% ShouldExclude = false(n,1);
% % 
% % % Zero check = "Y"
% % ShouldExclude(strcmpi(strtrim(ZeroCheck),'Y')) = true;
% % 
% % % RPM < 1 or NaN
% ShouldExclude(RPM < 1 | isnan(RPM)) = true;
% vehData.data.('~ShouldExclude_RPM') = false(n,1);
% vehData.data.('~ShouldExclude_RPM') = ~ShouldExclude;
% 
% % 
% % % InstCO2 NaN
% ShouldExclude(isnan(InstCO2)) = true;
% vehData.data.('~ShouldExclude_CO2') = false(n,1);
% vehData.data.('~ShouldExclude_CO2') = ~isnan(InstCO2);
% % 
% % % Regen = "Y"
% ShouldExclude(strcmpi(strtrim(Regen),'1')) = true;
% vehData.data.('~ShouldExclude_Regen') = false(n,1);
% vehData.data.('~ShouldExclude_Regen') = ~strcmpi(strtrim(Regen),'1');
% 
% % 
% % % Ambient temperature outside valid band: [5 C, (-0.0014*ElevationFt)+37.78]
% ambLow = AmbTempC < 5;
% ambTmax = ((-0.0014 .* ElevationFt) + 37.78); % altitudeFt
% ambHigh = AmbTempC > ((-0.0014 .* ElevationFt) + 37.78);
% ShouldExclude(ambLow | ambHigh) = true;
% 
% vehData.data.('ambTmax') = ambTmax;
% vehData.data.('~ShouldExclude_ambTemp') = false(n,1);
% vehData.data.('~ShouldExclude_ambTemp') = ~(ambLow | ambHigh);
% 
% % 
% % % Elevation > 5500 ft
% ShouldExclude(ElevationFt > 5500) = true;
% vehData.data.('~ShouldExclude_ALT') = false(n,1);
% vehData.data.('~ShouldExclude_ALT') = ~(ElevationFt > 5500);
% 
% vehData.data.('~ShouldExclude0') = ~ShouldExclude;
% 
% % --- Exclude single data point surrounded by excluded points 1036.530(c)(3)(vii)
% for n=2:length(ShouldExclude)-1
%     if ShouldExclude(n-1) && ShouldExclude(n+1) && ~ShouldExclude(n)
%         ShouldExclude(n) = true;
%     end
% end
% 
% vehData.data.('ShouldExclude') = ShouldExclude;
% vehData.data.('~ShouldExclude') = ~ShouldExclude;
% 
% % Total Distance (mi)
% % dt = 1.0;
% % dt_miles =  toNumeric(v_mph)/3600*dt;
% % % DistanceNum = toNumeric(Distance);
% % % totalMiles = sum(DistanceNum, 'omitnan') / 5280;
% % totalMiles = sum(dt_miles, 'omitnan');
% 
% % 
% % % Also exclude a single included second flanked by excluded seconds
% % prevEx = [false; ShouldExclude(1:end-1)];
% % nextEx = [ShouldExclude(2:end); false];
% % flankedIncluded = ~ShouldExclude & prevEx & nextEx;
% % ShouldExclude(flankedIncluded) = true;
% % 
% % % Replace remaining NaNs in numeric signals with 0 (after Tamb computed)
% InstCO2(isnan(InstCO2)) = 0;
% InstNOx(isnan(InstNOx)) = 0;
% InstCO(isnan(InstCO))   = 0;
% % InstPM(isnan(InstPM))   = 0;
% InstTHC(isnan(InstTHC)) = 0;
% % 
% % % ---- Windowing logic ----
% WindowCounter = 0;
% invalidCounter = 0;
% % 
% % set_Gasoline_fuel = false;
% 
% if (isequal(udp(setIdx).log.fuel, 'Gasoline'))
%     vehData.data(vehData.data.("ShouldExclude") == 1, :) = [];
% 
%     % vehData.data = vehData.data(ShouldExclude(:) == 0, : );
%     ShouldExclude = vehData.data.("ShouldExclude");
% 
%     % ---- Extract needed variables with flexible name handling ----
%     n = height(vehData.data);             % number of rows
%     vehData.data.("eTIME") = (0:n-1).'; 
% 
%     raw = vehData.data;
%     Time      = getColumn(raw, {'TIME'});
%     AmbTempC  = getColumn(raw, {AmbTempC_col, 'Temp_Amb'}); % ambientTempC
%     InstCO    = getColumn(raw, {'CO_MassFlow','CO_Mass_Sec'});
%     InstCO2   = getColumn(raw, {'CO2_MassFlow','CO2_Mass_Sec'});
%     % InstPM    = getColumn(raw, {'PM_Mass_Sec_Final','PM_Mass_sec_Final','PM_Mass_Sec','PM_Mass_sec'});
%     InstTHC   = getColumn(raw, {'HC_MassFlow', 'THC_Mass_Sec'});
%     InstNOx   = getColumn(raw, {'kNOx_MassFlow','NOX_Mass_sec_Final','NOX_Mass_Sec','NOX_Mass_sec'});
%     Regen     = getTextColumn(raw, {'DPFRegenStatus','Regen'});
%     % ZeroCheck = getTextColumn(raw, {'Zero_Check_Flag','Zero_Check'});
%     ElevationFt = getColumn(raw, {'Altitude_Ft','Alt'});
%     RPM       = getColumn(raw, {'EngineRPM'});
%     Distance  = getColumn(raw, {'Cumulative_Distance_Miles', 'Distance'});
%     v_mph = getColumn(raw, {'Vehicle Speed', 'VehicleSpeedMPH', 'Veh_Speed'});
% 
%     InstCO2 = toNumeric(InstCO2);
%     InstNOx = toNumeric(InstNOx);
%     InstCO  = toNumeric(InstCO);
%     % InstPM  = toNumeric(InstPM);
%     InstTHC = toNumeric(InstTHC);
%     RPM     = toNumeric(RPM);
% 
%     [totalMiles, totalDistanceMi] = cumulativeMilesFromSpeed(vehData.data.("eTIME"), v_mph);
%     [NOx_gph, NOx_mg_per_hp_hr, THC_gph, THC_mg_per_hp_hr, CO_gph, CO_g_per_hp_hr, ...
%     PM_gph, PM_mg_per_hp_hr, mCO2norm, BIN, NOx_mg_per_mile, THC_mg_per_mile, PM_mg_per_mile, CO_g_per_mile, CO2_g_per_mile, binData, vehData] = ...
%         SI_MAW_300s(vehData, InstNOx, eCO2, PMax, InstCO2, InstTHC, InstCO, [], totalMiles, v_mph); %"InstPM");
% 
%     % Masks for bins (ignore NaNs)
%     idxBIN1 = BIN == 1;
%     idxBIN2 = BIN == 2;
% 
%     % BIN 1: total (overall) moving-average NOx in g/hr (mean across BIN 1)
%     % NOx_gph_BIN1 = mean(NOx_gph(idxBIN1), 'omitnan');
%     NOx_gph_BIN2 = mean(NOx_gph(idxBIN2), 'omitnan');
% 
%     % BIN 1: total (overall) NOx in mg/mile
%     % NOx_mg_mile_BIN1 = mean(NOx_mg_per_mile(idxBIN1), 'omitnan');
% 
%     % BIN 2: total (overall) moving-average metrics (means across BIN 2)
%     NOx_mg_hp_hr_BIN2 = mean(NOx_mg_per_hp_hr(idxBIN2), 'omitnan');
%     THC_mg_hp_hr_BIN2 = mean(THC_mg_per_hp_hr(idxBIN2), 'omitnan');
%     PM_mg_hp_hr_BIN2  = mean(PM_mg_per_hp_hr(idxBIN2), 'omitnan');
%     CO_g_hp_hr_BIN2   = mean(CO_g_per_hp_hr(idxBIN2), 'omitnan');
% 
%     % BIN 2: total (overall) distance-normalized metrics
%     NOx_mg_mile_BIN2  = mean(NOx_mg_per_mile(idxBIN2), 'omitnan');
%     THC_mg_mile_BIN2  = mean(THC_mg_per_mile(idxBIN2), 'omitnan');
%     PM_mg_mile_BIN2   = mean(PM_mg_per_mile(idxBIN2), 'omitnan');
%     CO_g_mile_BIN2    = mean(CO_g_per_mile(idxBIN2), 'omitnan');
% 
%     % (Optional) Report counts of contributing points and aggregates
%     nBIN1 = nnz(idxBIN1);
%     nBIN2 = nnz(idxBIN2);
%     disp(struct('nBIN1',nBIN1,'nBIN2',nBIN2, ...
%                 'NOx_gph_BIN2',NOx_gph_BIN2, ...
%                 'NOx_mg_per_hp_hr_BIN2',NOx_mg_hp_hr_BIN2, ...
%                 'THC_mg_per_hp_hr_BIN2',THC_mg_hp_hr_BIN2, ...
%                 'PM_mg_hp_hr_BIN2',PM_mg_hp_hr_BIN2, ...
%                 'CO_g_per_hp_hr_BIN2',CO_g_hp_hr_BIN2, ...
%                 'NOx_mg_per_mile_BIN2',NOx_mg_mile_BIN2, ...
%                 'THC_mg_per_mile_BIN2',THC_mg_mile_BIN2, ...
%                 'PM_mg_per_mile_BIN2',PM_mg_mile_BIN2, ...
%                 'CO_g_per_mile_BIN2',CO_g_mile_BIN2));
% 
%     disp(size(binData));
%     % binIData{1,n}: row 1:  boolean of exluded/included data in interval
%     % binIData{2,n}: row 2:  start and end indices of interval relative to entire
%     %                        test cycle.  (1x2 vector)
%     % binIData{3,n}: row 3:  Average time for the test inerval (scalar).  Used
%     %                        for graphing
%     % binIData{4,n}: row 4:  total included time for the interval (i.e. 300 sec)
%     % binIData{5,n}: row 5:  valid/invalid (1/0) data.  interval is invalid if
%     %                        the number of exluded pts > 600  (Scalar)
%     % binIData{6,n}: row 6:  number of sub intervals within the interval
%     % binIData{7,n}: row 7:  indices of the sub-intervals relative to the entire
%     %                        test
%     % binIData{8,n}: row 8:  mco2,norm,testinterval, Normalized CO2 mass over a
%     %                       300 second test interval according to 1036.530(e)
%     % binIData{9,n}: row 9:  bin number (1,2 or 0 for invalid)
% 
% else
% 
%     % % Emissions store
%     Emissions = struct('Window',{},'Start',{},'End',{},'Bin',{}, ...
%                        'mCO2',{},'mNOxBin1',{},'mNOxBin2',{}, ...
%                        'mCO',{},'mPM',{},'mTHC',{},'mCO2norm',{});
%     rowCounter = 1;
%     % j_pre = 0;
%     start_row = 0;
%     % total_ExcludeCounter = 0;
%     % % For i controls window start; for j controls window end
%     count_invalid = 0;
% 
%     for i = 1:(n-300)
%     % i = 1;
%     % endFlag = 0;
%     % while i < (n-300) && endFlag==0
% 
%         % vehData.data.('invalidCounter')(i) = invalidCounter;
%         if ~ShouldExclude(i) && ~ShouldExclude(i+1)
%             DTCopy = ShouldExclude(i:(i+298));
%             IncludeCounter = sum(~DTCopy);
%             ExcludeCounter = 0;
% 
%             % Trailing excluded count at bottom of DTCopy
%             for p = 299:-1:1
%                 if DTCopy(p)
%                     ExcludeCounter = ExcludeCounter + 1;
%                     % start_row = TimeValue(Time, p)+1;
%                     % vehData.data.('invalidCounter')(start_row) = invalidCounter;
%                 else
%                     break;
%                 end
%             end
% 
%             for j = (i+299):n
%                 if ~ShouldExclude(j)
%                     IncludeCounter = IncludeCounter + 1;
%                     ExcludeCounter = 0;
%                 else
%                     ExcludeCounter = ExcludeCounter + 1;
%                     start_row = TimeValue(Time, j)+1;
%                     % vehData.data.('invalidCounter')(start_row) = invalidCounter;
%                     % total_ExcludeCounter = total_ExcludeCounter + ExcludeCounter;
%                 end
% 
%                 % If >599 continuous excluded seconds, abandon this start
%                 if ExcludeCounter > 599
%                     invalidCounter = invalidCounter + 1;
%                     % start_row = TimeValue(Time, j)+1;
%                     % vehData.data.('invalid_start')(j) = j-600;
%                     % vehData.data.('invalidCounter')(j) = invalidCounter;
%                     break;
%                 end
% 
%                 % Valid window: 300 included seconds found and ends with 2 included seconds
%                 if IncludeCounter > 299 && ~ShouldExclude(j-1)
%                     WindowCounter = WindowCounter + 1;
%                     winName = sprintf('Window%d', WindowCounter);
% 
%                     idxRange = i:j;
%                     incMask = ~ShouldExclude(idxRange);
%                     subIdx = idxRange(incMask);
% 
%                     SumTime = (1:numel(subIdx)).';
%                     SumCO2  = InstCO2(subIdx);
%                     SumNOx  = InstNOx(subIdx);
%                     SumCO_  = InstCO(subIdx);
%                     % SumPM_  = InstPM(subIdx);
%                     SumTHC_ = InstTHC(subIdx);
% 
%                     mCO2 = trapz(SumTime, SumCO2);
%                     mNOx = trapz(SumTime, SumNOx);
%                     mCO  = trapz(SumTime, SumCO_);
%                     % mPM  = trapz(SumTime, SumPM_);
%                     mTHC = trapz(SumTime, SumTHC_);
% 
%                     mCO2norm = round((mCO2)/(PMax * eCO2 * tInt), 4);
%                     % Bin assignment (1036.530(e) and (f))
%                     if mCO2norm > 0.06
%                         % Bin 2
%                         Emissions(rowCounter).Bin       = 2;
%                         Emissions(rowCounter).mNOxBin1  = 0;
%                         Emissions(rowCounter).mNOxBin2  = mNOx;
%                         Emissions(rowCounter).mCO       = mCO;
%                         % Emissions(rowCounter).mPM       = mPM;
%                         Emissions(rowCounter).mTHC      = mTHC;
%                     else
%                         % Bin 1
%                         Emissions(rowCounter).Bin       = 1;
%                         Emissions(rowCounter).mNOxBin1  = mNOx;
%                         Emissions(rowCounter).mNOxBin2  = 0;
%                         Emissions(rowCounter).mCO       = 0;
%                         % Emissions(rowCounter).mPM       = 0;
%                         Emissions(rowCounter).mTHC      = 0;
%                     end
% 
%                     % Store shared fields
%                     Emissions(rowCounter).Window   = winName;
%                     Emissions(rowCounter).Start    = TimeValue(Time, i);
%                     Emissions(rowCounter).End      = TimeValue(Time, j);
%                     Emissions(rowCounter).mCO2     = mCO2;
%                     Emissions(rowCounter).mCO2norm = mCO2norm;
% 
%                     start_row = TimeValue(Time, i)+1;
%                     vehData.data.('Bin')(start_row) = Emissions(rowCounter).Bin;
%                     vehData.data.('WindowCounter')(start_row) = WindowCounter;
%                     vehData.data.('Start')(start_row) = TimeValue(Time, i);
%                     vehData.data.('End')(start_row) = TimeValue(Time, j);
%                     vehData.data.('mCO2')(start_row) = mCO2;
%                     vehData.data.('mCO2norm')(start_row) = mCO2norm;
%                     vehData.data.('mNOx')(start_row) = mNOx;
%                     vehData.data.('mTHC')(start_row) = mTHC;
%                     vehData.data.('mCO')(start_row) = mCO;
%                     end0 = TimeValue(Time, j);
%                     vehData.data.('End-Start')(start_row) = end0 - Time(start_row) + 1;
%                     vehData.data.('Count_Included')(start_row) = sum(~ShouldExclude(start_row:end0));
% 
%                     % vehData.data.('invalidCounter')(i) = invalidCounter;
% 
%                     rowCounter = rowCounter + 1;
%                     break;
%                 end
%             end
%         end
%         i = i + 1;
%     end
% 
%     % ---- Off-cycle emissions (1036.530(i)) ----
%     if isempty(Emissions)
%         error('No valid windows were found.');
%     end
% 
%     Bins = [Emissions.Bin].';
%     mNOxBin1_all = [Emissions.mNOxBin1].';
%     mNOxBin2_all = [Emissions.mNOxBin2].';
%     mCO2_all     = [Emissions.mCO2].';
%     mCO_all      = [Emissions.mCO].';
%     mTHC_all     = [Emissions.mTHC].';
%     % mPM_all      = [Emissions.mPM].';
% 
%     numBin1 = sum(Bins == 1);
%     numBin2 = sum(Bins == 2);
% 
%     % % Avoid division by zero
%     NOxBin1 = NaN;
%     if numBin1 > 0
%         NOxBin1 = (sum(mNOxBin1_all(Bins==1)) / (300 * numBin1)) * 3600; % g/hr
%     end
% 
%     NOxBin2 = NaN; COBin2 = NaN; HCBin2 = NaN; PMBin2 = NaN;
%     sumCO2_Bin2 = sum(mCO2_all(Bins==2));
%     if numBin2 > 0 && sumCO2_Bin2 > 0
%         NOxBin2 = (sum(mNOxBin2_all(Bins==2)) / sumCO2_Bin2) * eCO2 * 1000; % mg/hp*hr
%         COBin2  = (sum(mCO_all(Bins==2))      / sumCO2_Bin2) * eCO2;         % g/hp*hr
%         HCBin2  = (sum(mTHC_all(Bins==2))     / sumCO2_Bin2) * eCO2 * 1000;  % mg/hp*hr
%     end
%         % PMBin2  = (sum(mPM_all(Bins==2))      / sumCO2_Bin2) * eCO2 * 1000;  % mg/hp*hr
% 
%     % ---- Standards (1036.104(a)(3) and 1036.420(a)) with temperature adjustment ----
%     if Tamb < 25
%         NOxBin1Std = 10.4 + ((25 - Tamb) * 0.25);
%         NOxBin2Std = 63   + ((25 - Tamb) * 2.2);
%     else
%         NOxBin1Std = 10.4;
%         NOxBin2Std = 63;
%     end
% 
%     % ---- Format and display results ----
%     NOxBin1Str = sprintf('%.4f g/hr', NOxBin1);
%     NOxBin2Str = sprintf('%.2f mg/hp*hr', NOxBin2);
%     HCBin2Str  = sprintf('%.3f mg/hp*hr', HCBin2);
%     % PMBin2Str  = sprintf('%.2f mg/hp*hr', PMBin2);
%     COBin2Str  = sprintf('%.4f g/hp*hr', COBin2);
% 
%     NOxBin1StdStr = sprintf('%.1f g/hr', NOxBin1Std);
%     NOxBin2StdStr = sprintf('%.0f mg/hp*hr', round(NOxBin2Std));
% 
%         % string({'13.5 mg/hp*hr'; PMBin2Str}), ...
%     Final_tbl = table( ...
%         string({'Standard'; 'Value from Test'}), ...
%         string({NOxBin1StdStr; NOxBin1Str}), ...
%         string({NOxBin2StdStr; NOxBin2Str}), ...
%         string({'130 mg/hp*hr'; HCBin2Str}), ...
%         string({'9.25 g/hp*hr'; COBin2Str}), ...
%         'VariableNames', {'Label','Bin1_NOx','Bin2_NOx','Bin2_HC','Bin2_CO'});
%         % 'VariableNames', {'Label','Bin1_NOx','Bin2_NOx','Bin2_HC','Bin2_PM','Bin2_CO'});
% 
%     disp(Final_tbl);
% 
%     % ---- Quick checks ----
%     fprintf('Number of Valid Intervals: %d\n', WindowCounter);
%     fprintf('Number of Bin 1 windows: %d\n', numBin1);
%     fprintf('Number of Bin 2 windows: %d\n', numBin2);
%     fprintf('Number of included data points: %d\n', sum(~ShouldExclude));
%     fprintf('Number of invalidCounter: %d\n', invalidCounter);
%     fprintf('Number of ExcludeCounter: %d\n', ExcludeCounter);
%     fprintf('Time Included (hr): %.3f\n', sum(~ShouldExclude)/3600);
%     fprintf('Test Time (hr): %.3f\n', n/3600);
% end
% 
% fprintf('Total Distance (mi): %.3f\n', totalDistanceMi);
% 
% vehData_data_to_CSV(vehData(setIdx).pathname, vehData(setIdx).filename, vehData(setIdx).data);
% 
    % ---- Helper functions ----
    % function col = getColumn(T, candidates)
    %     % Return numeric column from table based on any of the candidate names
    %     for k = 1:numel(candidates)
    %         name = candidates{k};
    %         if ismember(lower(string(name)), lower(string(T.Properties.VariableNames))); % ismember(name, T.Properties.VariableNames)
    %             col = T.(name);
    %             return;
    %         end
    %         % Try valid-name variant
    %         vName = matlab.lang.makeValidName(name);
    %         if ismember(lower(string(vName)), lower(string(T.Properties.VariableNames))); % ismember(vName, T.Properties.VariableNames)
    %             col = T.(vName);
    %             return;
    %         end
    %     end
    %     error('None of the candidate columns found: %s', strjoin(candidates, ', '));
    % end

    function v = getColumn(T, candidates)
        names = string(T.Properties.VariableNames);
        cand  = string(candidates);
        idx = find(ismember(lower(names), lower(cand)), 1, 'first');
        if isempty(idx)
            v = [];
        else
            v = T.(names(idx));
        end
    end

    function col = getTextColumn(T, candidates)
        % Return text column (cellstr) from table based on candidates
        colRaw = getColumn(T, candidates);
        if iscellstr(colRaw)
            col = colRaw;
        elseif isstring(colRaw)
            col = cellstr(colRaw);
        elseif iscell(colRaw)
            col = cellfun(@(x) string(x), colRaw, 'UniformOutput', false);
            col = cellstr(string(col));
        else
            % Fallback: convert to string
            try
                col = cellstr(string(colRaw));
            catch
                col = repmat({''}, height(T), 1);
            end
        end
    end

    function v = toNumeric(x)
        if isnumeric(x)
            v = x;
        elseif iscell(x)
            v = str2double(string(x));
        elseif isstring(x)
            v = str2double(x);
        elseif ischar(x)
            v = str2double(string(x));
        else
            v = double(x);
        end
    end

    function t = TimeValue(TimeCol, idx)
        % Preserve time type (datetime/string/char) for Start/End reporting
        if iscell(TimeCol)
            t = TimeCol{idx};
        elseif isstring(TimeCol)
            t = TimeCol(idx);
        else
            t = TimeCol(idx);
        end
    end
% 
%     function [NOx_gph, NOx_mg_per_hp_hr, ...
%               THC_gph, THC_mg_per_hp_hr, ...
%               CO_gph,  CO_g_per_hp_hr, ...
%               PM_gph,  PM_mg_per_hp_hr, ...
%               mCO2norm, BIN, ...
%               NOx_mg_per_mile, THC_mg_per_mile, PM_mg_per_mile, ...
%               CO_g_per_mile, CO2_g_per_mile, binData, vehData] = SI_MAW_300s( ...
%                   vehData, instNOx, eCO2_g_per_hp_hr, PMax_hp, ...
%                   instCO2, instTHC, instCO, instPM, ...
%                   totalMiles, v_mph)
%     % SI_MAW_300s (300-sample windows i:i+299; all outputs stored at window start index i)
%     % Computes moving-average emissions over 300 samples:
%     % - g/hr for NOx, THC, CO, PM (CO2-independent)
%     % - Work-specific (CO2-based only): NOx,THC,PM in mg/hp-hr; CO in g/hp-hr
%     % - mCO2norm = round(mCO2/(PMax*eCO2*winHr), 4), with winHr = 300/3600 hr
%     % - BIN: 2 when mCO2norm >= 0.06; 1 when mCO2norm < 0.06; NaN otherwise
%     % - Distance-normalized (over same window):
%     %     NOx, THC, PM in mg/mile; CO and CO2 in g/mile
%     %
%     % Inputs (all instantaneous rates in g/s; time in data.eTIME):
%     %   data        table/timetable with eTIME (seconds, duration, or datetime)
%     %   instNOx     NOx instantaneous rate (g/s), numeric vector (required)
%     %   eCO2_g_per_hp_hr  scalar eCO2 in g/hp-hr
%     %   PMax_hp     scalar rated power in hp
%     %   instCO2     CO2 instantaneous rate (g/s), numeric vector or [] (required for work-specific and CO2-based metrics)
%     %   instTHC     THC instantaneous rate (g/s), numeric vector or [] (optional)
%     %   instCO      CO  instantaneous rate (g/s), numeric vector or [] (optional)
%     %   instPM      PM  instantaneous rate (g/s), numeric vector or [] (optional -> defaults to 0)
%     %   totalMiles  cumulative miles (mi), numeric vector or [] (preferred for distance)
%     %   v_mph       vehicle speed (mph), numeric vector or [] (used if totalMiles empty)
%     %
%     % Outputs (n-by-1; indices <300 are NaN; index i is window start):
%     %   *_gph, *_mg_per_hp_hr, CO_g_per_hp_hr, mCO2norm, BIN
%     %   *_per_mile as specified above
% 
%         % Window constants
%         winSamples = 300;
%         winSec = 300;
%         winHr  = winSec / 3600;
%         data = vehData.data;
% 
%         % eTIME -> seconds (column)
%         if ~(istable(data) || istimetable(data))
%             error('SI_MAW_300s:BadInput', 'First input must be a table or timetable.');
%         end
%         if ~ismember('eTIME', data.Properties.VariableNames)
%             error('SI_MAW_300s:MissingTIME', 'Input table must contain an eTIME variable.');
%         end
%         tRaw = data.("eTIME");
%         if isdatetime(tRaw) || isduration(tRaw)
%             ts = seconds(tRaw - tRaw(1));
%         else
%             ts = tRaw(:);
%         end
%         n = numel(ts);
%         binData = NaN(9, n);
% 
%         % Ensure column vectors and sizes (all inputs are g/s)
%         instNOx = ensureVec(instNOx, 'instNOx', n);
% 
%         haveCO2 = ~isempty(instCO2);
%         if haveCO2, instCO2 = ensureVec(instCO2, 'instCO2', n); end
% 
%         haveTHC = ~isempty(instTHC);
%         if haveTHC, instTHC = ensureVec(instTHC, 'instTHC', n); end
% 
%         haveCO  = ~isempty(instCO);
%         if haveCO,  instCO  = ensureVec(instCO,  'instCO',  n); end
% 
%         % PM: default to zeros if empty/omitted
%         if nargin < 8 || isempty(instPM)
%             instPM = zeros(n,1);
%         else
%             instPM = ensureVec(instPM, 'instPM', n);
%         end
%         havePM = true;
% 
%         % Distance inputs
%         haveMiles = (nargin >= 9) && ~isempty(totalMiles);
%         if haveMiles, totalMiles = ensureVec(totalMiles, 'totalMiles', n); end
% 
%         haveVmph = (nargin >= 10) && ~isempty(v_mph);
%         if haveVmph, v_mph = ensureVec(v_mph, 'v_mph', n); end
% 
%         % Initialize outputs (stored at i for valid windows; others remain NaN)
%         NOx_gph = NaN(n,1); NOx_mg_per_hp_hr = NaN(n,1);
%         THC_gph = NaN(n,1); THC_mg_per_hp_hr = NaN(n,1);
%         CO_gph  = NaN(n,1); CO_g_per_hp_hr   = NaN(n,1);
%         PM_gph  = NaN(n,1); PM_mg_per_hp_hr  = NaN(n,1);
%         mCO2norm = NaN(n,1);
%         BIN      = NaN(n,1);
% 
%         NOx_mg_per_mile = NaN(n,1);
%         THC_mg_per_mile = NaN(n,1);
%         PM_mg_per_mile  = NaN(n,1);
%         CO_g_per_mile   = NaN(n,1);
%         CO2_g_per_mile  = NaN(n,1);
% 
%         % Forward 300-sample windows: i .. k=i+winSamples-1
%         lastStart = n - (winSamples - 1);
%         if lastStart < 1
%             return; % not enough samples for a full 300-sample window
%         end
% 
%         % variables
%         % scalarBinTable:  Table of scalar bin data statistics
% 
%         for i = 1:lastStart
%             k = i + (winSamples - 1);
% 
%             % Slice window by samples
%             twin = ts(i:k);
%             yNOx = instNOx(i:k);
%             if haveCO2, yCO2 = instCO2(i:k); end
%             if haveTHC, yTHC = instTHC(i:k); end
%             if haveCO,  yCO  = instCO(i:k);  end
%             if havePM,  yPM  = instPM(i:k);  end
% 
%             binIData{1,i} = false;
%             binIData{2,i} = [i, k];
%             binIData{3,i} = mean(twin);
%             binIData{4,i} = winSamples/3600;
%             binIData{5,i} = 1;      %if the interval is not valid 
%             binIData{6,i}=length(twin);      %number of sub-intervals is zero
%             % binIData{7,i}(1,1)=0;    %index for start of sub-interval is zero
%             % binIData{7,i}(2,1)=0;  
%             binIData{7,i}(1,1)=i; %index for start of sub-interval is zero
%             binIData{7,i}(2,1)=k; % assign subEnd to binIData
% 
%             % Integrate grams over the window; store g/hr at i
%             gNOx = trapz(twin, yNOx); NOx_gph(i) = gNOx / winHr;
%             if haveTHC
%                 gTHC = trapz(twin, yTHC); THC_gph(i) = gTHC / winHr;
%             end
%             if haveCO
%                 gCO  = trapz(twin, yCO);  CO_gph(i)  = gCO  / winHr;
%             end
%             if havePM
%                 gPM  = trapz(twin, yPM);  PM_gph(i)  = gPM  / winHr; % 0 if PM defaulted to zeros
%             end
% 
%             NOx_gph(isnan(NOx_gph)) = 0;
%             THC_gph(isnan(THC_gph)) = 0;
%             PM_gph(isnan(PM_gph)) = 0;
%             CO_gph(isnan(CO_gph)) = 0;
% 
%             % CO2-based work-specific metrics (no fallback)
%             if haveCO2
%                 gCO2 = trapz(twin, yCO2); % grams over window
% 
%                 if gCO2 > 0 && eCO2_g_per_hp_hr > 0
%                     % Work-specific metrics at i
%                     if haveCO
%                         CO_g_per_hp_hr(i)   =        (gCO  / gCO2) * eCO2_g_per_hp_hr;    % g/hp-hr
%                     end
%                     NOx_mg_per_hp_hr(i) = 1000 * (gNOx / gCO2) * eCO2_g_per_hp_hr;        % mg/hp-hr
%                     if haveTHC, THC_mg_per_hp_hr(i) = 1000 * (gTHC / gCO2) * eCO2_g_per_hp_hr; end
%                     if havePM,  PM_mg_per_hp_hr(i)  = 1000 * (gPM  / gCO2) * eCO2_g_per_hp_hr; end
%                 end
% 
%                 % Normalized CO2 mass and BIN (at i)
%                 if PMax_hp > 0 && eCO2_g_per_hp_hr > 0
%                     mCO2norm(i) = round( gCO2 / (PMax_hp * eCO2_g_per_hp_hr * winHr), 4 );
%                     if ~isnan(mCO2norm(i))
%                         BIN(i) = 2; % 1 + (mCO2norm(i) >= 0.06); % no BIN 1 and BIN 2 for SI engines
%                     end
%                 end
% 
%                 binIData{8,i}=round(mCO2norm(i),2);
%                 binIData{9,i}=BIN(i);
%                 data.("BIN")(i) = BIN(i);
%                 data.("mCO2norm")(i) = mCO2norm(i);
%                 data.("gCO2")(i) = gCO2;
%                 data.("NOx_gph")(i) = NOx_gph(i);
%                 data.("NOx_mg_hp_hr")(i) = NOx_mg_per_hp_hr(i);
%                 data.("HC_mg_hp_hr")(i) = THC_mg_per_hp_hr(i);
%                 data.("PM_mg_hp_hr")(i) = PM_mg_per_hp_hr(i);
%                 data.("CO_g_hp_hr")(i) = CO_g_per_hp_hr(i);
%             end
% 
%             % Distance over the window (miles)
%             distMiles = NaN;
%             if haveMiles
%                 distMiles = totalMiles(k) - totalMiles(i);
%             elseif haveVmph
%                 yV = v_mph(i:k);
%                 distMiles = trapz(twin, yV) / 3600; % mph * hr = mi; dt in s -> divide by 3600
%             end
% 
%             % Distance-normalized metrics (store at i when distance > 0)
%             if isfinite(distMiles) && distMiles > 0
%                 NOx_mg_per_mile(i) = 1000 * gNOx / distMiles;          % mg/mi
%                 if haveTHC, THC_mg_per_mile(i) = 1000 * gTHC / distMiles; end
%                 if havePM,  PM_mg_per_mile(i)  = 1000 * gPM  / distMiles; end
%                 if haveCO,  CO_g_per_mile(i)   =        gCO  / distMiles; end
%                 if haveCO2, CO2_g_per_mile(i)  =        gCO2 / distMiles; end
% 
%                 data.("CO2_g_mile")(i) = CO2_g_per_mile(i);
%                 data.("NOx_mg_mile")(i) = NOx_mg_per_mile(i);
%                 data.("HC_mg_mile")(i) = THC_mg_per_mile(i);
%                 data.("PM_mg_mile")(i) = PM_mg_per_mile(i);
%                 data.("CO_g_mile")(i) = CO_g_per_mile(i);
%             end
%         end
% 
%         % mask = data.("BIN") == 1;
%         % NOx_gph_BIN1 = mean(data.("NOx_gph")(mask), 'omitnan');
%         mask = data.("BIN") == 2;
%         NOx_gph_BIN2 = mean(data.("NOx_gph")(mask), 'omitnan');
%         NOx_mg_hp_hr_BIN2 = mean(data.("NOx_mg_hp_hr")(mask), 'omitnan');
% 
%         bins=cell2mat(binIData(9,:));                       % vector of interval bins
%         validIntervals=sum((cell2mat(binIData(5,:))));      % number of valid intervals
%         invalidIntervals=sum(cell2mat(binIData(5,:))==0);   % number of invalid intervals
%         numBin1=sum(bins==1);                               % number of bin 1 intervals
%         numBin2=sum(bins==2);                               % number of bin 2 intervals
% 
%         % --- assemble scalar interval data into an table
%         scalarBinTable=table(lastStart,validIntervals,invalidIntervals,numBin1,numBin2);
%         scalarBinTable.Properties.VariableUnits=["(-)","(-)","(-)","(-)","(-)"];
%         scalarBinTable.Properties.VariableNames=["Number_Intervals","NumValid_Intervals","NumInValid_Intervals",...
%             "NumBin1_Intervals","NumBin2_Intervals"];
% 
%         % --- assemble bin average time (binIData{3,:}) into a vector, transpose to
%         %     include in table.  bin average time is used in graphing.
%         timeBinAvg=transpose(cell2mat(binIData(3,:)));
% 
%         % ---------------- Calculation of NOx Mass Flow Offcycle Bin 1 according to 1036.530(g)(2)(i)
%         bin1Logical=cell2mat(binIData(9,:))==1;                      % logical for bin1 (bin1=1, bin2=0)
%         timeBin1=(bin1Logical.*cell2mat(binIData(4,:)))./3600;  % bin1 logical * time for each interval in hours
%         timeBin1=transpose(timeBin1);                           % tranpose the vector 
%         timeBin1Total=sum(timeBin1);                            % total bin1 interval times in hours
%         % nnz(timeBin1 > 0)
%         % sum(timeBin1(:) > 0)
% 
%         numInt = lastStart;
%         [noxBin1Mass, noxBin1MassTotal]=binMassCalc(vehData(setIdx).data.(udp(setIdx).pems.kNOxMassFlow), 1);
% 
%         % resolve division by zero if test cycle does not contain a bin 1
%         if timeBin1Total==0   
%             noxBin1MassFlow=0;
%         else
%             noxBin1MassFlow=noxBin1MassTotal/timeBin1Total;
%         end
% 
%         % update Scalar Bin Table
%         scalarBinTable.("NOxMassFlow_Bin1")=noxBin1MassFlow;
%         scalarBinTable.Properties.VariableUnits("NOxMassFlow_Bin1")="(gm/hr)";
% 
%         % intialize table of bin vector data
%         binDataTable=table(timeBinAvg,noxBin1Mass);
%         binDataTable.Properties.VariableNames=["Time_BinAvg","NOx_Mass_Bin1"];
%         binDataTable.Properties.VariableUnits=["(sec)","(gms)"];
% 
%         % calculate cummulative nox bin1 mass flow
%         % the number of intervals is incremented and the sum of nox mass / sum time is
%         % calculated.  The sum of nox mass over the discrete intervals is
%         % calculated as opposed to using a cumtrapz which uses a trapezoidal method
%         for bInt=1:numInt
%             if sum(timeBin1(1:bInt)) ~=0
%                 noxBin1MassFlowCu(bInt,1)=sum(noxBin1Mass(1:bInt))/sum(timeBin1(1:bInt));
%             end
%         end
% 
%         % add cummulative nox mass flot to the binDataTable
%         if (sum(timeBin1 > 0) == 0)
%             binDataTable.("NOxMassFlow_Bin1_Cummulative") = false(height(binDataTable), 1);
%         else
%             binDataTable.("NOxMassFlow_Bin1_Cummulative")=noxBin1MassFlowCu;
%         end
%         binDataTable.Properties.VariableUnits("NOxMassFlow_Bin1_Cummulative")="(gm/hr)";
% 
%         % save scalar interval table data to database vehData
%         vehData(setIdx).scalarBinData=scalarBinTable;
%         vehData(setIdx).binData=binDataTable;
%         vehData.data = data;
%     end

    function x = ensureVec(x, name, n)
    % Ensure numeric column vector of length n
        if ~isnumeric(x)
            error('SI_MAW_300s:TypeError', '%s must be a numeric vector.', name);
        end
        x = x(:);
        if numel(x) ~= n
            error('SI_MAW_300s:SizeMismatch', '%s must have %d elements.', name, n);
        end
    end

    function [totalMiles, totalDistanceMi] = cumulativeMilesFromSpeed(eTIME, v_mph)
    % cumulativeMilesFromSpeed Compute per-sample cumulative miles and total miles.
    %
    % Usage:
    %   [totalMiles, totalDistanceMi] = cumulativeMilesFromSpeed(eTIME, v_mph)
    %
    % Inputs:
    %   eTIME  - time stamps (same length as v_mph), can be:
    %              * numeric seconds (vector)
    %              * duration array
    %              * datetime array
    %   v_mph  - vehicle speed in mph (numeric vector, same length as eTIME)
    %
    % Outputs:
    %   totalMiles      - cumulative miles at each sample (n-by-1)
    %   totalDistanceMi - total distance in miles (scalar) = totalMiles(end)
    %
    % Notes:
    % - Handles irregular sampling by using per-sample dt from eTIME.
    % - NaN/Inf speeds are treated as zero; negative or invalid dt are zeroed.
    % - If eTIME is datetime/duration, conversion to seconds uses seconds(eTIME - eTIME(1)).
    %   (Subtracting the first sample doesn't affect the dt but keeps values well-scaled.)

        % Validate inputs
        if nargin < 2
            error('cumulativeMilesFromSpeed:NotEnoughInputs', ...
                  'Provide both eTIME and v_mph.');
        end

        % Convert eTIME to seconds
        if isdatetime(eTIME) || isduration(eTIME)
            ts = seconds(eTIME - eTIME(1));
        else
            ts = double(eTIME(:));
        end

        % Ensure v_mph is a numeric column vector
        v = double(v_mph(:));
        if numel(ts) ~= numel(v)
            error('cumulativeMilesFromSpeed:SizeMismatch', ...
                  'eTIME and v_mph must have the same number of elements.');
        end

        % Compute per-sample time deltas (seconds)
        dt_s = [0; diff(ts)];
        % Guard against non-finite or negative time steps
        dt_s(~isfinite(dt_s) | dt_s < 0) = 0;

        % Treat non-finite speeds as zero
        v(~isfinite(v)) = 0;

        % Miles added each sample: mph * (dt in hours) = mph * dt_s/3600
        mi_inc = v ./ 3600 .* dt_s;

        % Cumulative miles and total distance
        totalMiles = cumsum(mi_inc);
        if isempty(totalMiles)
            totalDistanceMi = 0;
        else
            totalDistanceMi = totalMiles(end);
        end
    end

    % ------------------ Nested Function binEmissionCalc
    % ------------------ Calculation of bin emissions mass flow and bin emissions mass
    function [binMassInterval, binMassTotal] = binMassCalc(massFlow, binNumber)

        % for each interval in the test cycle
        subStart=0;
        subEnd=0;
        jInt=0;
        jSub=0;
        dt = 1;

        for jInt=1:numInt

            massSub=0;       % emission mass over the sub-interval
            massInterval=0;  % emisison mass over the interval
            massInterval1=0;  % emisison mass over the interval

            if binIData{9,jInt} == binNumber
                for jSub=1:size(binIData{7,jInt},2)  % cycle thru each of the sub-intervals
                    if binIData{5,jInt} ~= 0         % if the interval is Valid
                        subStart=binIData{7,jInt}(1,jSub);   % get index to start of sub-interval
                        subEnd=binIData{7,jInt}(2,jSub);     % get index to end of sub-interval

                        % if jInt == numInt
                        %     disp([jInt, subStart, subEnd])
                        % end
                        subTime=testCycleTime(subStart:subEnd);   % get the time over the sub-interval
                        subMassFlow=massFlow(subStart:subEnd); % get the em mass flow (g/s) over the sub-interval
                        % massSub=trapz(subTime,subMassFlow);  % integrate to get the total em mass over the sub-interval
                        
                        t  = (0:numel(subMassFlow)-1)*dt;
                        % subMassFlow(subMassFlow < 0) = 0; % (ii) Disregard the provision in 40 CFR 1065.650(g) for setting negative emission mass to zero for test intervals and subintervals.
                        massSub = trapz(t, subMassFlow);

                        massInterval=massInterval+massSub; % calculate the em mass over the interval

                        % if length(subTime) > 300 || (min(subMassFlow) < 0) % || (abs(massInterval - massInterval1) >= eps)
                        %     disp(jSub)
                        %     disp(length(subTime))
                        % end
                    end
                end
            end
            binMassInterval(jInt)=massInterval;

        end
        binMassTotal=sum(binMassInterval);
        binMassInterval=transpose(binMassInterval);  % transpose binMass for saving in table
    
    end  % end of nested function binMassCalc


    % --------------------- Nested Function brakeEmCu
    % calculates the cummulative NOx off-cycle emission over the test cycle
    function brakeEmission = brakeEmCu(emVector, co2vector) 
        for pInt=1:numInt
            brakeEmission(pInt)=udp(setIdx).bins.eco2fcl*sum(emVector(1:pInt))/sum(co2vector(1:pInt));
        end

        brakeEmission=transpose(brakeEmission);
    end

toc

% ----------------------------
% ------- end of main function
end
