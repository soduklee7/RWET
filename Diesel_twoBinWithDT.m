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

%% ==========================================
%% 4. EXECUTION BLOCK (Main Script)
%% ==========================================

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

idx = find(contains(rawCols, "Vehicle", "IgnoreCase", true) & ...
           contains(rawCols, "Speed",          "IgnoreCase", true), 1);

if isempty(idx)
    error('No column name contains both "LimitAdjusted" and "_LAT".');
end

% Set the column name to ambTempC (store the matched name)
VehSpd_col = rawCols(idx);

idx = find(contains(rawCols, "Engine", "IgnoreCase", true) & ...
           contains(rawCols, "FuelRate",          "IgnoreCase", true), 1);

if isempty(idx)
    error('No column name contains both "LimitAdjusted" and "_LAT".');
end

% Set the column name to ambTempC (store the matched name)
fuelrate_col = rawCols(idx);

df = table();
% ---- Extract needed variables with flexible name handling ----
df.Time      = toNumeric(getColumn(raw, {'TIME'}));
df.AmbTempC  = toNumeric(getColumn(raw, {AmbTempC_col, 'Temp_Amb'})); % ambientTempC
df.instCO    = toNumeric(getColumn(raw, {'CO_MassFlow','CO_Mass_Sec'}));
df.instCO2   = toNumeric(getColumn(raw, {'CO2_MassFlow','CO2_Mass_Sec'}));
instPM    = (getColumn(raw, {'PM_Mass_Sec_Final','PM_Mass_sec_Final','PM_Mass_Sec','PM_Mass_sec'}));
% PM: default to zeros if empty/omitted
if isempty(instPM)
    df.instPM = zeros(height(raw),1);
end
havePM = true;

df.instHC   = toNumeric(getColumn(raw, {'HC_MassFlow', 'THC_Mass_Sec'}));
df.instNOx   = toNumeric(getColumn(raw, {'kNOx_MassFlow','NOX_Mass_sec_Final','NOX_Mass_Sec','NOX_Mass_sec'}));
df.In_Regen     = toNumeric(getColumn(raw, {'DPFRegenStatus','Regen'}));
% ZeroCheck = getTextColumn(raw, {'Zero_Check_Flag','Zero_Check'});
df.Altitude_m = toNumeric(getColumn(raw, {'Altitude_Ft','Alt'}))/3.28084;
df.Engine_RPM       = toNumeric(getColumn(raw, {'EngineRPM'}));
df.Engine_Torque_Nm = toNumeric(getColumn(raw, {'DerivedEngineTorque'})); % DerivedEngineTorque_1
df.Engine_Torque_lb_ft = toNumeric(getColumn(raw, {'DerivedEngineTorque_1'})); % DerivedEngineTorque_1
df.Distance  = toNumeric(getColumn(raw, {'Cumulative_Distance_Miles', 'Distance'}));
df.v_mph = toNumeric(getColumn(raw, {VehSpd_col, 'Vehicle Speed', 'VehicleSpeedMPH', 'Veh_Speed'}));
% df.EngineFuelRate = toNumeric(getColumn(raw, {fuelrate_col, 'Fuel Rate', 'Engine FuelRate', 'Engine Fuel Rate'})); % gal/s
df.instFuelRate = toNumeric(getColumn(raw, {'InstantaneousFuelFlow', 'Instantaneous Fuel Flow'})); % g/s
% if isempty(In_Regen)
%     df.In_Regen = false(height(raw),1); false(n,1);
% end
% havePM = true;
% df = struct2table(data);

% --- Run Calculations ---
eCO2_g_hp_hr = udp(setIdx).bins.eco2fcl; % 507.0; 
pmax_hp      = udp(setIdx).bins.pmax; % 505.0;
MPG = vehData(setIdx).scalarData.Fuel_Economy;
fuel_density = udp(setIdx).fuel.sg;

% Define Regulatory Limits
epa_limits = struct();
epa_limits.Bin1_NOx_g_hr = 10.4;
epa_limits.Bin2_NOx_mg_hp_hr = 63.0;
epa_limits.Bin2_HC_mg_hp_hr = 130.0;
epa_limits.Bin2_PM_mg_hp_hr = 5.0;
epa_limits.Bin2_CO_g_hp_hr = 9.25;
epa_limits.Bin2_CO2_g_hp_hr = 600.0;

filename_udp = regexprep(vehData.filename, '_Matlab[^.]*\.xlsx$', '_udp.xlsx');
excelFile = saveVehUdpToExcel(setIdx, vehData, udp, filename_udp);

if (isequal(udp(setIdx).log.fuel, 'Diesel')) %
    %% 2. RUN CALCULATIONS
    [df, summary_df, windows_df, sub_interval_df, Invalid_count] = calculate_maw_and_subintervals(df, eCO2_g_hp_hr, pmax_hp);
    
    %% 3. EVALUATE COMPLIANCE & EXPORT
    if ~isempty(summary_df)
        fprintf('\nTotal Invalid Windows (>599s Excluded): %d\n\n', Invalid_count);
        
        compliance_results = evaluate_compliance(summary_df, epa_limits);
        disp('--- EPA MAW Compliance Report ---');
        disp(compliance_results);
        
        % excelFile = 'MAW_outputs.xlsx';
        excelFile = regexprep(vehData.filename, '_MatlabBinCalc\.xlsx.*$', '_MAW_outputs.xlsx');

        if isfile(excelFile)
            delete(excelFile);
        end
        
        writetable(windows_df,        excelFile, 'Sheet', 'maw_detailed_windows');
        writetable(summary_df,        excelFile, 'Sheet', 'maw_summary_averages');
        writetable(compliance_results,excelFile, 'Sheet', 'maw_compliance_report');
        writetable(sub_interval_df,   excelFile, 'Sheet', 'sub_intervals_summary');
        
        fprintf('Excel workbook written: %s\n', excelFile);
        % % Export to CSV
        % writetable(windows_df, 'maw_detailed_windows.csv');
        % writetable(summary_df, 'maw_summary_averages.csv');
        % writetable(compliance_results, 'maw_compliance_report.csv');
        % writetable(sub_interval_df, 'sub_intervals_summary.csv');
        % disp('✅ Success: Data exported to CSV files in the current directory.');
    else
        disp('Error: No valid MAW data could be generated.');
    end
elseif (isequal(udp(setIdx).log.fuel, 'Gasoline'))
    %% 2. RUN CALCULATIONS
    [df, final_emissions, sub_interval_df] = calculate_shift_day_emissions(df, eCO2_g_hp_hr, pmax_hp);
    
    %% 3. PRINT DATA QUALITY SUMMARY
    total_sec = final_emissions.Total_Shift_Seconds;
    valid_sec = final_emissions.Total_Valid_Seconds;
    excluded_sec = final_emissions.Total_Excluded_Seconds;
    
    fprintf('--- Data Quality & Exclusion Summary ---\n');
    fprintf('Total Shift Duration : %d seconds\n', total_sec);
    fprintf('Valid Data Points    : %d seconds (%.1f%%)\n', valid_sec, (valid_sec/total_sec)*100);
    fprintf('Excluded Data Points : %d seconds (%.1f%%)\n\n', excluded_sec, (excluded_sec/total_sec)*100);
    
    %% 4. PRINT OVERALL RESULTS
    fprintf('--- Shift-Day Overall Results ---\n');
    fields = fieldnames(final_emissions);
    for i = 1:numel(fields)
        val = final_emissions.(fields{i});
        if mod(val, 1) == 0 % If it's effectively an integer
            fprintf('%s: %d\n', fields{i}, val);
        else
            fprintf('%s: %.3f\n', fields{i}, val);
        end
    end
    
    df.total_fuel_gals = gramsToGallons(df.instFuelRate, fuel_density);
    total_fuel_gals = sum(df.total_fuel_gals);
    MPG_est = sum(df.Distance_mi)/total_fuel_gals;
    fprintf('MPG @ pems    : %.2f , MPG_est %.2f%\n', MPG, MPG_est);

    %% 5. PRINT SIDE-BY-SIDE DISTANCE COMPARISON
    fprintf('\n--- Distance-Specific Emissions Discrepancy (Total vs. Valid) ---\n');
    fprintf('%-12s | %-22s | %-18s | %s\n', 'Metric', 'Total Dist (All Data)', 'Valid Dist Only', '% Difference');
    fprintf('---------------------------------------------------------------------------\n');
    comparison_metrics = {'NOx_mg_mi', 'PM_mg_mi', 'HC_mg_mi', 'CO_g_mi', 'CO2_g_mi'};
    
    for m = 1:length(comparison_metrics)
        metric = comparison_metrics{m};
        val_total = final_emissions.([metric '_TotalDist']);
        val_valid = final_emissions.([metric '_ValidDist']);
        
        % Calculate percentage difference
        if val_valid > 0
            pct_diff = ((val_total - val_valid) / val_valid) * 100;
        else
            pct_diff = 0.0;
        end
        
        fprintf('%-12s | %-22.3f | %-18.3f | %+9.2f%%\n', metric, val_total, val_valid, pct_diff);
    end
    
    %% 5. Print Side-by-Side Brake-Specific Comparison
    fprintf('\n--- Brake-Specific Emissions Discrepancy (Work vs. eCO2 Method) ---\n');
    fprintf('%-15s | %-20s | %-18s | %s\n', 'Metric', 'Work Method', 'Pmax/eCO2 Method', '% Difference');
    fprintf('%s\n', repmat('-', 1, 75));
    
    bs_metrics = {'NOx_mg_hp_hr', 'PM_mg_hp_hr', 'HC_mg_hp_hr', 'CO_g_hp_hr', 'CO2_g_hp_hr'};
    
    for m = 1:length(bs_metrics)
        metric = bs_metrics{m};
        
        % Map user's display strings to the corresponding struct fields
        work_key = [metric, '_Work'];
        eco2_key = [strrep(metric, '_hp_hr', ''), '_Pmax_eCO2'];  
        
        % Extract values using dynamic field names
        val_work = final_emissions.(work_key);
        val_eco2 = final_emissions.(eco2_key);
        
        % Calculate percentage difference safely
        if val_work > 0
            pct_diff = ((val_eco2 - val_work) / val_work) * 100;
        else
            pct_diff = 0.0;
        end
        
        % Print formatted row
        fprintf('%-15s | %-20.3f | %-18.3f | %+9.2f%%\n', metric, val_work, val_eco2, pct_diff);
    end
    
    % %% 6. EXPORT TO CSV
    % if ~isempty(sub_interval_df)
    %     csv_filename = 'sub_intervals_summary.csv';
    %     writetable(sub_interval_df, csv_filename);
    %     fprintf('\n✅ Success: Sub-interval summary saved to ''%s''\n', csv_filename);
    % end
    
    % %% 7. GENERATE VISUAL PLOT
    % plot_shift_day_emissions(df);
end

%% 4. GENERATE PLOTS
disp('Generating visual analytics...');
plot_shift_day_emissions(df);
plot_cumulative_emissions(df, eCO2_g_hp_hr);

% =========================================================================
% FUNCTIONS
% =========================================================================

function [df, summary, windows_df, sub_summary, Invalid_count] = calculate_maw_and_subintervals(df, eCO2_g_hp_hr, pmax_hp)
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
    
    % Preallocate Arrays for MAW Windows
    Window_Index = zeros(max_possible_windows, 1);
    Window_Start_Time = zeros(max_possible_windows, 1);
    Window_End_Time = zeros(max_possible_windows, 1);
    Excluded_Samples_Count = zeros(max_possible_windows, 1);
    Total_Work_hp_hr = zeros(max_possible_windows, 1);
    Total_Distance_mi = zeros(max_possible_windows, 1);
    Total_Fuelrate_g = zeros(max_possible_windows, 1);
    eCO2norm_percent = zeros(max_possible_windows, 1);
    % Bin = strings(max_possible_windows, 1);
    Bin = zeros(max_possible_windows, 1); % 0=Invalid, 1=Bin1, 2=Bin2
    Bin1_NOx_g_hr = NaN(max_possible_windows, 1);
    massNOx = NaN(max_possible_windows, 1);
    massHC = NaN(max_possible_windows, 1);
    massPM = NaN(max_possible_windows, 1);
    massCO = NaN(max_possible_windows, 1);
    massCO2 = NaN(max_possible_windows, 1);
    NOx_mg_mi = NaN(max_possible_windows, 1);
    HC_mg_mi = NaN(max_possible_windows, 1);
    PM_mg_mi = NaN(max_possible_windows, 1);
    CO_g_mi = NaN(max_possible_windows, 1);
    CO2_g_mi = NaN(max_possible_windows, 1);
    
    bin2_denom = eCO2_g_hp_hr * pmax_hp * 300/3600;
    Invalid_count = 0; 
    w_idx = 0; % Track actual stored windows
    
    for i = 1:(total_points - 1)
        % Ensure the window starts with two consecutive VALID points
        
        if df.Excluded_Data(i) || df.Excluded_Data(i+1)
            continue; 
        end

        % if ~df.Excluded_Data(i) && ~df.Excluded_Data(i+1) && (i == 4962)
        %     disp(i) 
        % end
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
            
            % Extract the chronological window (which may span thousands of points)
            window_full = df(i : j, :);
            
            % Isolate only the valid points for the emissions summations
            win_valid = window_full(~window_full.Excluded_Data, :);
            
            time_start = i;
            time_end = j;
            excluded_count = sum(window_full.Excluded_Data);
            
            t_CO2 = trapz(win_valid.instCO2);
            t_NOx = trapz(win_valid.instNOx);
            t_PM  = trapz(win_valid.instPM);
            t_HC  = trapz(win_valid.instHC);
            t_CO  = trapz(win_valid.instCO);
            
            % t_NOx1 = trapz(win_valid.instNOx .* ~df.Excluded_Data(i:j));
            % if (abs(t_NOx - t_NOx1) > eps) || (i == 10)
            %     disp(i)
            % end
            t_work = trapz(win_valid.EnginePower_hp) / 3600.0;
            t_dist = trapz(win_valid.Distance_mi);
            t_fuelrate = trapz(win_valid.instFuelRate);
            
            eCO2norm_pct = (t_CO2 / bin2_denom) * 100;
            
            if t_dist > 0
                n_mi = (t_NOx * 1000) / t_dist;
                h_mi = (t_HC * 1000) / t_dist;
                p_mi = (t_PM * 1000) / t_dist;
                c_mi = t_CO / t_dist;
                c2_mi = t_CO2 / t_dist;
            else
                n_mi = NaN; h_mi = NaN; p_mi = NaN; c_mi = NaN; c2_mi = NaN;
            end
            
            % Binning logic
            if excluded_count > 599
                bin_label = 0; % "InValid (Excluded > 599s)";
                Invalid_count = Invalid_count + 1;
                massNOx(w_idx) = NaN ; % (t_NOx * 1000) / t_CO2 * eCO2_g_hp_hr;
                massHC(w_idx)  = NaN; %  * 1000) /  t_CO2 * eCO2_g_hp_hr;
                massPM(w_idx)  = NaN; %  * 1000) /  t_CO2 * eCO2_g_hp_hr;
                massCO(w_idx)   = NaN; %  /  t_CO2 * eCO2_g_hp_hr;
                massCO2(w_idx)  = NaN; %  /  t_CO2 * eCO2_g_hp_hr;
                break;
            end

            if eCO2norm_pct < 6.0
                bin_label = 1; % "Bin 1 (Idle/Low)";
                % Scale NOx using exact valid samples in the window (300 or 301)
                % Bin1NOx_g_hr(w_idx) = t_NOx * (3600.0 / valid_samples_count);
            else
                bin_label = 2; % "Bin 2 (Non-Idle)";
            end
            massNOx(w_idx) = t_NOx ; % (t_NOx * 1000) / t_CO2 * eCO2_g_hp_hr;
            massHC(w_idx)  = t_HC; %  * 1000) /  t_CO2 * eCO2_g_hp_hr;
            massPM(w_idx)  = t_PM; %  * 1000) /  t_CO2 * eCO2_g_hp_hr;
            massCO(w_idx)   = t_CO; %  /  t_CO2 * eCO2_g_hp_hr;
            massCO2(w_idx)  = t_CO2; %  /  t_CO2 * eCO2_g_hp_hr;

            % Store
            Window_Index(w_idx) = i; Window_Start_Time(w_idx) = time_start; Window_End_Time(w_idx) = time_end;
            Excluded_Samples_Count(w_idx) = excluded_count; Total_Work_hp_hr(w_idx) = t_work;
            Total_Distance_mi(w_idx) = t_dist; Total_Fuelrate_g(w_idx) = t_fuelrate; eCO2norm_percent(w_idx) = eCO2norm_pct; Bin(w_idx) = bin_label;
            NOx_mg_mi(w_idx) = n_mi; HC_mg_mi(w_idx) = h_mi; PM_mg_mi(w_idx) = p_mi; CO_g_mi(w_idx) = c_mi; CO2_g_mi(w_idx) = c2_mi;
        end
    end
    
    % y = Bin2_NOx_mg_hp_hr;          % your signal
    % mask = (Bin == "2") & isfinite(y);% keep only Bin==2 and finite values
    % A = trapz(y(mask));  
    % % A = trapz_omitnan(Bin2_NOx_mg_hp_hr);

    if w_idx == 0
        summary = table(); windows_df = table();
        warning('No valid windows found that met the boundary criteria.');
        return;
    end
    
    % Truncate preallocated arrays to actual size
    if w_idx > length(massNOx)
        w_idx = length(massNOx);
    end
    % df.Total_Fuelrate_g = Total_Fuelrate_g;
    windows_df = table(Window_Index(1:w_idx), Window_Start_Time(1:w_idx), Window_End_Time(1:w_idx), Excluded_Samples_Count(1:w_idx), ...
                       Total_Work_hp_hr(1:w_idx), Total_Distance_mi(1:w_idx), Total_Fuelrate_g(1:w_idx), eCO2norm_percent(1:w_idx), Bin(1:w_idx) , ...
                       massNOx(1:w_idx), massHC(1:w_idx), massPM(1:w_idx), massCO(1:w_idx), massCO2(1:w_idx) , ...
                       NOx_mg_mi(1:w_idx), HC_mg_mi(1:w_idx), PM_mg_mi(1:w_idx), CO_g_mi(1:w_idx), CO2_g_mi(1:w_idx));
                   
    % Rename columns automatically generated by MATLAB array truncation
    windows_df.Properties.VariableNames = {'Window_Index', 'Window_Start_Time', 'Window_End_Time', 'Excluded_Samples_Count', ...
                                           'Total_Work_hp_hr', 'Total_Distance_mi', 'Total_Fuelrate_g', 'eCO2norm_percent', 'Bin', ...
                                           'massNOx', 'massHC', 'massPM', ...
                                           'massCO', 'massCO2', 'NOx_mg_mi', 'HC_mg_mi', 'PM_mg_mi', 'CO_g_mi', 'CO2_g_mi'};
                   
    % Filter out InValid for summary averages
    valid_wins = windows_df(windows_df.Bin ~= 0, :);
    
    if isempty(valid_wins)
        summary = table();
        return;
    end
    
    % Aggregation for Summary
    [G_bin, Bin_Labels] = findgroups(valid_wins.Bin);
    Total_Windows = splitapply(@numel, valid_wins.eCO2norm_percent, G_bin);
    Avg_eCO2norm_Percent = splitapply(@(x) mean(x,'omitnan'), valid_wins.eCO2norm_percent, G_bin);
    % Avg_Bin1_NOx_g_hr = splitapply(@(x) mean(x,'omitnan'), valid_wins.Bin1_NOx_g_hr, G_bin);
    % Avg_Bin2_NOx_mg_hp_hr = splitapply(@(x) mean(x,'omitnan'), valid_wins.Bin2_NOx_mg_hp_hr, G_bin);
    % Avg_Bin2_HC_mg_hp_hr = splitapply(@(x) mean(x,'omitnan'), valid_wins.Bin2_HC_mg_hp_hr, G_bin);
    % Avg_Bin2_PM_mg_hp_hr = splitapply(@(x) mean(x,'omitnan'), valid_wins.Bin2_PM_mg_hp_hr, G_bin);
    % Avg_Bin2_CO_g_hp_hr = splitapply(@(x) mean(x,'omitnan'), valid_wins.Bin2_CO_g_hp_hr, G_bin);
    % Avg_Bin2_CO2_g_hp_hr = splitapply(@(x) mean(x,'omitnan'), valid_wins.Bin2_CO2_g_hp_hr, G_bin);
    Avg_NOx_mg_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.NOx_mg_mi, G_bin);
    Avg_HC_mg_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.HC_mg_mi, G_bin);
    Avg_PM_mg_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.PM_mg_mi, G_bin);
    Avg_CO_g_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.CO_g_mi, G_bin);
    Avg_CO2_g_mi = splitapply(@(x) mean(x,'omitnan'), valid_wins.CO2_g_mi, G_bin);
    
        % =====================================================================
    % Explicit Calculations using Bin mapping, length(valid_wins.Bin)
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
    
    % Create explicit mask for Bin == 1, sum(valid_wins.Bin==1) 
    idx_bin1 = find(Bin_Labels == 1);
    if ~isempty(idx_bin1)
        bin1_mask = (valid_wins.Bin == 1);
        numBin1 = sum(bin1_mask);
        NOxBin1 = (sum(massNOx(bin1_mask)) / (300 * numBin1)) * 3600; % g/hr
        Avg_Bin1_NOx_g_hr(idx_bin1) = NOxBin1; % mean(valid_wins.Bin1_NOx_g_hr(bin1_mask), 'omitnan');
    end

    % Create explicit mask for Bin == 2, sum(valid_wins.Bin==2)
    idx_bin2 = find(Bin_Labels == 2);
    if ~isempty(idx_bin2)
        bin2_mask = (valid_wins.Bin == 2);
        numBin2 = sum(bin2_mask);
        sumCO2_Bin2 = sum(massCO2(bin2_mask));
        % Avg_Bin2_NOx_mg_hp_hr(idx_bin2) = mean(valid_wins.Bin2_NOx_mg_hp_hr(bin2_mask), 'omitnan');
        % Avg_Bin2_HC_mg_hp_hr(idx_bin2)  = mean(valid_wins.Bin2_HC_mg_hp_hr(bin2_mask), 'omitnan');
        % Avg_Bin2_PM_mg_hp_hr(idx_bin2)  = mean(valid_wins.Bin2_PM_mg_hp_hr(bin2_mask), 'omitnan');
        % Avg_Bin2_CO_g_hp_hr(idx_bin2)   = mean(valid_wins.Bin2_CO_g_hp_hr(bin2_mask), 'omitnan');
        % Avg_Bin2_CO2_g_hp_hr(idx_bin2)  = mean(valid_wins.Bin2_CO2_g_hp_hr(bin2_mask), 'omitnan');
        NOxBin2 = (sum(massNOx(bin2_mask)) / sumCO2_Bin2) * eCO2_g_hp_hr * 1000; % mg/hp*hr
        COBin2  = (sum(massCO(bin2_mask))     / sumCO2_Bin2) * eCO2_g_hp_hr;         % g/hp*hr
        HCBin2  = (sum(massHC(bin2_mask))    / sumCO2_Bin2) * eCO2_g_hp_hr * 1000;  % mg/hp*hr
        PMBin2  = (sum(massPM(bin2_mask))    / sumCO2_Bin2) * eCO2_g_hp_hr * 1000;  % mg/hp*hr

        Avg_Bin2_NOx_mg_hp_hr(idx_bin2) = NOxBin2;
        Avg_Bin2_HC_mg_hp_hr(idx_bin2)  = HCBin2;
        Avg_Bin2_PM_mg_hp_hr(idx_bin2)  =PMBin2;
        Avg_Bin2_CO_g_hp_hr(idx_bin2)   =COBin2;
        Avg_Bin2_CO2_g_hp_hr(idx_bin2)  = eCO2_g_hp_hr;
    end

    % numBin1 = sum(Bins == 1);
    % numBin2 = sum(Bins == 2);
    % 
    % % % Avoid division by zero
    % NOxBin1 = NaN;
    % if numBin1 > 0
    %     NOxBin1 = (sum(mNOxBin1_all(Bins==1)) / (300 * numBin1)) * 3600; % g/hr
    % end
    
    % NOxBin2 = NaN; COBin2 = NaN; HCBin2 = NaN; PMBin2 = NaN;
    % sumCO2_Bin2 = sum(mCO2_all(Bins==2));
    % if numBin2 > 0 && sumCO2_Bin2 > 0
    %     NOxBin2 = (sum(mNOxBin2_all(Bins==2)) / sumCO2_Bin2) * eCO2 * 1000; % mg/hp*hr
    %     COBin2  = (sum(mCO_all(Bins==2))      / sumCO2_Bin2) * eCO2;         % g/hp*hr
    %     HCBin2  = (sum(mTHC_all(Bins==2))     / sumCO2_Bin2) * eCO2 * 1000;  % mg/hp*hr
    % end
    %     % PMBin2  = (sum(mPM_all(Bins==2))      / sumCO2_Bin2) * eCO2 * 1000;  % mg/hp*hr
    
    % ---- Standards (1036.104(a)(3) and 1036.420(a)) with temperature adjustment ----
    Tamb = mean(df.AmbTempC);
    if Tamb < 25
        NOxBin1Std = 10.4 + ((25 - Tamb) * 0.25);
        NOxBin2Std = 63   + ((25 - Tamb) * 2.2);
    else
        NOxBin1Std = 10.4;
        NOxBin2Std = 63;
    end
    
    % ---- Format and display results ----
    NOxBin1Str = sprintf('%.4f g/hr', NOxBin1);
    NOxBin2Str = sprintf('%.3f mg/hp*hr', NOxBin2);
    HCBin2Str  = sprintf('%.4f mg/hp*hr', HCBin2);
    PMBin2Str  = sprintf('%.4f mg/hp*hr', PMBin2);
    COBin2Str  = sprintf('%.4f g/hp*hr', COBin2);
    
    NOxBin1StdStr = sprintf('%.1f g/hr', NOxBin1Std);
    NOxBin2StdStr = sprintf('%.0f mg/hp*hr', round(NOxBin2Std));
    
        % string({'13.5 mg/hp*hr'; PMBin2Str}), ...
    Final_tbl = table( ...
        string({'Standard'; 'Value from Test'}), ...
        string({NOxBin1StdStr; NOxBin1Str}), ...
        string({NOxBin2StdStr; NOxBin2Str}), ...
        string({'130 mg/hp*hr'; HCBin2Str}), ...
        string({'9.25 g/hp*hr'; COBin2Str}), ...
        'VariableNames', {'Label','Bin1_NOx','Bin2_NOx','Bin2_HC','Bin2_CO'});
        % 'VariableNames', {'Label','Bin1_NOx','Bin2_NOx','Bin2_HC','Bin2_PM','Bin2_CO'});
    
    disp(Final_tbl);

    summary = table(Bin_Labels, Total_Windows, Avg_eCO2norm_Percent, Avg_Bin1_NOx_g_hr, ...
                    Avg_Bin2_NOx_mg_hp_hr, Avg_Bin2_HC_mg_hp_hr, Avg_Bin2_PM_mg_hp_hr, ...
                    Avg_Bin2_CO_g_hp_hr, Avg_Bin2_CO2_g_hp_hr, Avg_NOx_mg_mi, Avg_HC_mg_mi, ...
                    Avg_PM_mg_mi, Avg_CO_g_mi, Avg_CO2_g_mi);
    summary.Properties.VariableNames{1} = 'Bin';
end

function comp_table = evaluate_compliance(summary_df, limits)
    Bin = strings(0,1); Metric = strings(0,1); 
    Actual_Average = []; Regulatory_Limit = []; Status = strings(0,1);
    
    idx = 1;
    for i = 1:height(summary_df)
        b_label = summary_df.Bin(i);
        if b_label == 1
            Bin(idx,1) = b_label; Metric(idx,1) = "NOx (g/hr)";
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
                Bin(idx,1) = b_label; Metric(idx,1) = mets{k,1};
                Actual_Average(idx,1) = summary_df.(mets{k,2})(i);
                Regulatory_Limit(idx,1) = mets{k,3};
                if Actual_Average(idx,1) <= Regulatory_Limit(idx,1), Status(idx,1) = "PASS"; else, Status(idx,1) = "FAIL"; end
                idx = idx + 1;
            end
        end
    end
    comp_table = table(Bin, Metric, round(Actual_Average,3), Regulatory_Limit, Status, ...
        'VariableNames', {'Bin', 'Metric', 'Actual_Average', 'Regulatory_Limit', 'Status'});
end

function plot_shift_day_emissions(df)
    time_sec = height(df);
    t = 1:time_sec;
    
    figure('Position', [100, 100, 1000, 600], 'Name', 'Shift-Day Emissions', 'Color', 'w');

    % Tiled layout with compact spacing
    tl = tiledlayout(gcf, 2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
    
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
    
    % TILE 1: Engine Power & Excluded Regions
    ax1 = nexttile(tl, 1);
    plot(ax1, t, df.EnginePower_hp, 'Color', '#0072BD', 'LineWidth', 1.5, 'DisplayName', 'Engine Power (hp)');
    ylabel(ax1, 'Engine Power (hp)');
    title(ax1, 'Engine Test Data: Valid vs. Excluded Regions');
    grid(ax1, 'on'); xlim(ax1, [0 time_sec]);
    draw_excluded(ax1);
    
    % Dummy patch for legend
    patch(ax1, NaN, NaN, 'r', 'FaceAlpha', 0.2, 'EdgeColor', 'none', 'DisplayName', 'Excluded Data');
    legend(ax1, 'Location', 'northeast');
    % Remove x-axis tick labels (keeps grid lines)
    ax1.XTickLabel = [];

    % TILE 2: Vehicle Speed and Instantaneous CO2 (Dual Axis)
    ax2 = nexttile(tl, 2);
    yyaxis(ax2, 'left');
    plot(ax2, t, df.v_mph, 'Color', '#77AC30', 'LineWidth', 2, 'DisplayName', 'Vehicle Speed (mph)');
    ylabel(ax2, 'Vehicle Speed (mph)');
    ax2.YColor = '#77AC30';
    
    yyaxis(ax2, 'right');
    plot(ax2, t, df.instCO2, 'Color', '#D95319', 'LineWidth', 1.5, 'DisplayName', 'Inst. CO2 (g/s)');
    ylabel(ax2, 'Instantaneous CO2 (g/s)');
    ax2.YColor = '#D95319';
    
    xlabel(ax2, 'Time (seconds)');
    grid(ax2, 'on'); xlim(ax2, [0 time_sec]);
    draw_excluded(ax2);
    legend(ax2, 'Location', 'northwest');
end

function plot_cumulative_emissions(df, eCO2_g_hp_hr)
    valid_df = df(~df.Excluded_Data, :);
    
    valid_df.Cum_NOx_g = cumsum(valid_df.instNOx);
    valid_df.Cum_CO2_g = cumsum(valid_df.instCO2);
    valid_df.Cum_Work_hp_hr = cumsum(valid_df.EnginePower_hp / 3600.0);
    
    % Calculate running Brake-Specific NOx (g/hp-hr)
    bs_nox = zeros(height(valid_df), 1);
    idx_pos = valid_df.Cum_Work_hp_hr > 0;
    bs_nox(idx_pos) = valid_df.Cum_NOx_g(idx_pos) ./ valid_df.Cum_Work_hp_hr(idx_pos);
    valid_df.BS_NOx_g_hp_hr = bs_nox;
    
    bs_nox_eCO2 = valid_df.Cum_NOx_g./ valid_df.Cum_CO2_g * eCO2_g_hp_hr;
    valid_df.bs_nox_eCO2 = zeros(height(bs_nox_eCO2), 1);
    valid_df.bs_nox_eCO2 = bs_nox_eCO2;

    t_valid = find(~df.Excluded_Data);
    
    fig = figure('Position', [150, 150, 1000, 600], 'Name', 'Cumulative Emissions', 'Color', 'w');
    
    tl = tiledlayout(fig, 2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');  % small gap
    
    % TILE 1: Cumulative Mass (Grams)
    ax1 = nexttile(tl, 1);
    yyaxis(ax1, 'left');
    plot(ax1, t_valid, valid_df.Cum_NOx_g, 'Color', '#A2142F', 'LineWidth', 2, 'DisplayName', 'Cumulative NOx (g)');
    ylabel('Cumulative NOx (g)'); ax1.YColor = '#A2142F';
    title('Cumulative Emissions Accrual During Valid Testing');
    
    yyaxis(ax1, 'right');
    plot(ax1, t_valid, valid_df.Cum_CO2_g, '--', 'Color', '#7E2F8E', 'LineWidth', 2, 'DisplayName', 'Cumulative CO2 (g)');
    ylabel('Cumulative CO2 (g)'); ax1.YColor = '#7E2F8E';
    grid on; legend(ax1, 'Location', 'best');
    ax1.XTickLabel = [];  % hide top x labels to reduce crowding
    
    % TILE 2: Cumulative Brake-Specific Running Average
    ax2 = nexttile(tl, 2);
    plot(ax2, t_valid, valid_df.BS_NOx_g_hp_hr, 'Color', '#0072BD', 'LineWidth', 2, 'DisplayName', 'Brake Specific NOx /w Engine hp');
    hold(ax2, 'on');
    plot(ax2, t_valid, valid_df.bs_nox_eCO2, 'Color', '#77AC30', 'LineWidth', 2, 'DisplayName', 'Brake Specific NOx /w eCO2 & Pmax');
    final_avg = valid_df.BS_NOx_g_hp_hr(end);
    yline(ax2, final_avg, 'k:', 'LineWidth', 1.5, 'DisplayName', sprintf('Final Avg: %.3f g/hp-hr /w Engine hp', final_avg));
    ylim(ax2, [0 1.25*max(valid_df.BS_NOx_g_hp_hr)]);
    xlabel(ax2, 'Time (Original Second of Shift)'); ylabel(ax2, 'Cum. BS NOx (g/hp-hr)');
    grid(ax2, 'on'); legend(ax2, 'Location', 'best');
    
    % figure('Position', [150, 150, 1000, 600], 'Name', 'Cumulative Emissions', 'Color', 'w');
    % 
    % % SUBPLOT 1: Cumulative Mass (Grams)
    % ax1 = subplot(2,1,1);
    % yyaxis(ax1, 'left');
    % plot(ax1, t_valid, valid_df.Cum_NOx_g, 'Color', '#A2142F', 'LineWidth', 2, 'DisplayName', 'Cumulative NOx (g)');
    % ylabel('Cumulative NOx (g)'); ax1.YColor = '#A2142F';
    % title('Cumulative Emissions Accrual During Valid Testing');
    % 
    % yyaxis(ax1, 'right');
    % plot(ax1, t_valid, valid_df.Cum_CO2_g, '--', 'Color', '#7E2F8E', 'LineWidth', 2, 'DisplayName', 'Cumulative CO2 (g)');
    % ylabel('Cumulative CO2 (g)'); ax1.YColor = '#7E2F8E';
    % grid on; legend('Location', 'best'); % 'northwest');
    % 
    % % SUBPLOT 2: Cumulative Brake-Specific Running Average
    % ax2 = subplot(2,1,2);
    % plot(ax2, t_valid, valid_df.BS_NOx_g_hp_hr, 'Color', '#0072BD', 'LineWidth', 2, 'DisplayName', 'Brake Specific NOx /w Engine hp');
    % hold on;
    % plot(ax2, t_valid, valid_df.bs_nox_eCO2, 'Color', '#77AC30', 'LineWidth', 2, 'DisplayName', 'Brake Specific NOx /w eCO2 & Pmax');
    % final_avg = valid_df.BS_NOx_g_hp_hr(end);
    % yline(ax2, final_avg, 'k:', 'LineWidth', 1.5, 'DisplayName', sprintf('Final Avg: %.3f g/hp-hr /w Engine hp', final_avg));
    % 
    % % max(valid_df.BS_NOx_g_hp_hr)
    % ylim(ax2, [0 1.1*max(valid_df.BS_NOx_g_hp_hr)]);
    % 
    % xlabel('Time (Original Second of Shift)'); ylabel('Cum. BS NOx (g/hp-hr)');
    % grid on; legend('Location', 'best');
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

% =========================================================================
% FUNCTIONS
% =========================================================================

function [df, results, sub_summary] = calculate_shift_day_emissions(df, ftp_eco2_g_hp_hr, pmax_hp)
    % Calculate Engine Power (hp), Altitude (ft), and Distance (mi)
    df.EnginePower_hp = (df.Engine_Torque_Nm .* df.Engine_RPM) / 7120.8;
    df.Altitude_ft = df.Altitude_m * 3.28084;
    df.Distance_mi = df.v_mph / 3600.0;
    
    % Total distance including all valid and excluded points
    total_distance_mi = sum(df.Distance_mi);
    % df.total_fuel_gals = gramsToGallons(df.instFuelRate, fuel_density);
    % total_fuel_gals = sum(df.total_fuel_gals);
    % MPG_est = total_distance_mi/total_fuel_gals;

    % Calculate Total Mass from ALL data for TotalDist metrics
    total_all_NOx_g = sum(df.instNOx);
    total_all_PM_g  = sum(df.instPM);
    total_all_HC_g  = sum(df.instHC);
    total_all_CO_g  = sum(df.instCO);
    total_all_CO2_g = sum(df.instCO2);
    
    % Master flag for excluded data points
    df.Excluded_Data = (df.AmbTempC < -5) | (df.AmbTempC > -0.0014.*df.Altitude_ft+37.78) | ...
                       (df.Altitude_ft > 5500) | (df.Engine_RPM < 1) | ...
                       df.In_Regen; % df.In_Calibration | 
                   
    % Create Sub-Interval IDs
    df.Sub_Interval_ID = cumsum(df.Excluded_Data);
    
    % Filter out excluded data
    valid_idx = ~df.Excluded_Data;
    valid_df = df(valid_idx, :);
    
    if isempty(valid_df)
        error('Error: No valid data points found.');
    end
    
    total_sub_intervals = numel(unique(valid_df.Sub_Interval_ID));
    
    % CREATE SUB-INTERVAL SUMMARY DATAFRAME
    [G, sub_IDs] = findgroups(valid_df.Sub_Interval_ID);
    Duration_sec = splitapply(@numel, valid_df.EnginePower_hp, G);
    Avg_Power_hp = splitapply(@mean, valid_df.EnginePower_hp, G);
    Work_hp_hr   = splitapply(@(x) sum(x)/3600, valid_df.EnginePower_hp, G);
    Distance_mi  = splitapply(@sum, valid_df.Distance_mi, G);
    NOx_g        = splitapply(@sum, valid_df.instNOx, G);
    PM_g         = splitapply(@sum, valid_df.instPM, G);
    HC_g         = splitapply(@sum, valid_df.instHC, G);
    CO_g         = splitapply(@sum, valid_df.instCO, G);
    CO2_g        = splitapply(@sum, valid_df.instCO2, G);
    
    sub_summary = table(sub_IDs, Duration_sec, Avg_Power_hp, Work_hp_hr, ...
                        Distance_mi, NOx_g, PM_g, HC_g, CO_g, CO2_g);
    sub_summary.Properties.VariableNames{1} = 'Sub_Interval_ID';
    
    % Calculate Total Valid Metrics
    total_valid_NOx_g = sum(valid_df.instNOx);
    total_valid_PM_g  = sum(valid_df.instPM);
    total_valid_HC_g  = sum(valid_df.instHC);
    total_valid_CO_g  = sum(valid_df.instCO);
    total_valid_CO2_g = sum(valid_df.instCO2);
    
    total_work_hp_hr = sum(valid_df.EnginePower_hp) / 3600.0;
    valid_distance_mi = sum(valid_df.Distance_mi);

    % Multipliers
    bs_multiplier_work = 1.0 / total_work_hp_hr;
    bs_multiplier_pmax = pmax_hp / ftp_eco2_g_hp_hr;

    % Compile Overall Results
    results = struct();
    results.Total_Shift_Seconds = height(df);
    results.Total_Valid_Seconds = height(valid_df);
    results.Total_Excluded_Seconds = sum(df.Excluded_Data);
    results.Total_Sub_Intervals_Stitched = total_sub_intervals;
    results.Total_Work_hp_hr = total_work_hp_hr;
    results.Total_Distance_mi = total_distance_mi;
    results.Valid_Distance_mi = valid_distance_mi;
    
    % Brake-Specific Emissions (Work Method - VALID ONLY)
    results.NOx_mg_hp_hr_Work = (total_valid_NOx_g * 1000) * bs_multiplier_work;
    results.PM_mg_hp_hr_Work  = (total_valid_PM_g * 1000) * bs_multiplier_work;
    results.HC_mg_hp_hr_Work  = (total_valid_HC_g * 1000) * bs_multiplier_work;
    results.CO_g_hp_hr_Work   = total_valid_CO_g * bs_multiplier_work;
    results.CO2_g_hp_hr_Work  = total_valid_CO2_g * bs_multiplier_work;
    
    % Brake-Specific Emissions (Pmax/eCO2 Method - VALID ONLY)
    results.NOx_mg_Pmax_eCO2 = (total_valid_NOx_g/total_valid_CO2_g * 1000) * ftp_eco2_g_hp_hr;
    results.PM_mg_Pmax_eCO2  = (total_valid_PM_g/total_valid_CO2_g * 1000) * ftp_eco2_g_hp_hr;
    results.HC_mg_Pmax_eCO2  = (total_valid_HC_g/total_valid_CO2_g * 1000) * ftp_eco2_g_hp_hr;
    results.CO_g_Pmax_eCO2   = total_valid_CO_g/total_valid_CO2_g * ftp_eco2_g_hp_hr;
    results.CO2_g_Pmax_eCO2  = ftp_eco2_g_hp_hr;
    
    % Distance-Specific (Total Distance - USES ALL VALID & EXCLUDED DATA)
    results.NOx_mg_mi_TotalDist = (total_all_NOx_g * 1000) / total_distance_mi;
    results.PM_mg_mi_TotalDist  = (total_all_PM_g * 1000) / total_distance_mi;
    results.HC_mg_mi_TotalDist  = (total_all_HC_g * 1000) / total_distance_mi;
    results.CO_g_mi_TotalDist   = total_all_CO_g / total_distance_mi;
    results.CO2_g_mi_TotalDist  = total_all_CO2_g / total_distance_mi;
    
    % Distance-Specific (Valid Distance - VALID ONLY)
    results.NOx_mg_mi_ValidDist = (total_valid_NOx_g * 1000) / valid_distance_mi;
    results.PM_mg_mi_ValidDist  = (total_valid_PM_g * 1000) / valid_distance_mi;
    results.HC_mg_mi_ValidDist  = (total_valid_HC_g * 1000) / valid_distance_mi;
    results.CO_g_mi_ValidDist   = total_valid_CO_g / valid_distance_mi;
    results.CO2_g_mi_ValidDist  = total_valid_CO2_g / valid_distance_mi;
end

function plot_shift_day_emissions_SI(df)
    % Calculate statistics for the plot overlay
    time_sec = height(df);
    t = 1:time_sec;
    
    excluded_sec = sum(df.Excluded_Data);
    valid_sec = time_sec - excluded_sec;
    pct_excluded = (excluded_sec / time_sec) * 100;

    figure('Position', [100, 100, 1000, 600], 'Name', 'Shift-Day Emissions');

    % Helper to draw red exclusion zones
    function draw_excluded(ax)
        hold(ax, 'on');
        % Find where excluded data starts and ends
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
    ylabel('Engine Power (hp)'); 
    title('Shift-Day Off-Cycle Emissions: Valid vs. Excluded Sub-Intervals');
    grid on; xlim([0 time_sec]);
    draw_excluded(ax1);

    % Dummy patch for the legend
    patch(NaN, NaN, 'r', 'FaceAlpha', 0.2, 'EdgeColor', 'none', 'DisplayName', 'Excluded Data');
    legend('Location', 'northeast');

    % Add Data Quality Annotation Box
    txt = sprintf('Data Quality Overview\nValid Data: %ds\nExcluded Data: %ds (%.1f%%)', ...
                  valid_sec, excluded_sec, pct_excluded);
    annotation('textbox', [0.15, 0.8, 0.15, 0.1], 'String', txt, 'FitBoxToText', 'on', ...
               'BackgroundColor', 'w', 'FaceAlpha', 0.9, 'EdgeColor', [0.5 0.5 0.5]);

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

function gal = gramsToGallons(mass_g, fuelOrDensity)
% Convert fuel mass (grams) to US gallons.
% fuelOrDensity can be:
%   - string/char: 'gasoline','e10','e85','diesel'
%   - numeric: density in kg/L
% Default is gasoline (0.745 kg/L at ~15°C).

    if nargin < 2 || isempty(fuelOrDensity)
        rho = 0.745; % kg/L (gasoline E0)
    elseif isnumeric(fuelOrDensity)
        rho = fuelOrDensity; % kg/L
    else
        switch lower(strtrim(string(fuelOrDensity)))
            case {"gasoline", "Gasoline", "petrol","e0"}
                rho = 0.745;
            case "e10"
                rho = 0.750;
            case "e85"
                rho = 0.785;
            case {"diesel","d2"}
                rho = 0.832;
            otherwise
                error('Unknown fuel type. Provide density (kg/L) or a known fuel string.');
        end
    end

    % Convert grams -> kg -> liters -> gallons
    liters = (mass_g ./ 1000) ./ rho;
    gal = liters ./ 3.785411784;
end

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

function T = struct2table_flat(S)
% Flatten a (scalar or array) struct S to a table suitable for CSV.
% Nested structs/tables become prefixed columns. Non-scalar values are serialized to strings.

    if ~isstruct(S)
        error('Input must be a struct or struct array.');
    end

    % Flatten each element of the struct array into a scalar struct
    flatElems = arrayfun(@(s) flattenStructScalar(s, ''), S, 'UniformOutput', false);
    % Merge fields across elements (ensure each element has same field set)
    allFields = unique(vertcat(fieldnames(flatElems{:})));
    for i = 1:numel(flatElems)
        missing = setdiff(allFields, fieldnames(flatElems{i}));
        for k = 1:numel(missing)
            flatElems{i}.(missing{k}) = missingValue();
        end
    end
    % Convert to table
    T = struct2table([flatElems{:}].');
end

function Sflat = flattenStructScalar(S, prefix)
    Sflat = struct();
    fn = fieldnames(S);
    for i = 1:numel(fn)
        name = fn{i};
        val  = S.(name);
        newName = name;
        if ~isempty(prefix), newName = [prefix '_' name]; end

        if isstruct(val)
            sub = flattenStructScalar(val, newName);
            Sflat = catstruct_local(Sflat, sub);
        elseif istable(val)
            vnames = val.Properties.VariableNames;
            for j = 1:numel(vnames)
                col = val.(vnames{j});
                Sflat.([newName '_' vnames{j}]) = serializeValue(col);
            end
        else
            Sflat.(newName) = serializeValue(val);
        end
    end
end

function v = serializeValue(val)
% Return a scalar suitable for a table variable:
% - numeric/logical/char/string scalars kept as-is
% - non-scalars are serialized with mat2str into a string
% - cellstr -> join with space
    if ischar(val) || (isstring(val) && isscalar(val))
        v = string(val);
    elseif isnumeric(val) || islogical(val)
        if isscalar(val)
            v = val;
        else
            v = string(mat2str(val));
        end
    elseif iscellstr(val)
        v = strjoin(val, ' ');
    elseif isstring(val)
        v = strjoin(cellstr(val), ' ');
    else
        % Fallback: try to stringify
        try
            v = string(mat2str(val));
        catch
            v = "";
        end
    end
end

function S = catstruct_local(A, B)
% Merge two scalar structs (B fields overwrite A on conflict)
    S = A;
    fb = fieldnames(B);
    for i = 1:numel(fb)
        S.(fb{i}) = B.(fb{i});
    end
end

function v = missingValue()
    v = NaN;  % choose placeholder for missing. Could be "" for string columns.
end

function excelFile = saveVehUdpToExcel(setIdx, vehData, udp, excelFile)
% saveVehUdpToExcel(setIdx, vehData, udp)
% Creates an Excel file with one worksheet per output that your CSV code produced.
%
% Returns:
%   excelFile - the full filename of the generated .xlsx

    if nargin < 3
        error('Usage: saveVehUdpToExcel(setIdx, vehData, udp)');
    end

    % Choose an output filename
    % excelFile = sprintf('veh_udp_export_set%d.xlsx', setIdx);

    % Remove existing file for a clean write (optional)
    if exist(excelFile, 'file')
        delete(excelFile);
    end

    %------------------------------------------------------------
    % Build all tables as in your original CSV-producing code
    %------------------------------------------------------------
    % vehData_data
    t_data = vehData(setIdx).data;

    % vehData_scalar
    x = vehData(setIdx).scalarData;
    if isstruct(x)
        t_scalar = struct2table(x(:), 'AsArray', true);
    elseif istable(x)
        t_scalar = x;
    else
        % Fallback if any2table is unavailable
        try
            t_scalar = any2table(x, 'scalarData');
        catch
            t_scalar = table(x, 'VariableNames', {'scalarData'});
        end
    end

    % udp_top and udp sub-structs
    % t_udp_top = struct2table(udp(setIdx), 'AsArray', true);
    t_pems    = struct2table(udp(setIdx).pems, 'AsArray', true);
    t_bins    = struct2table(udp(setIdx).bins, 'AsArray', true);

    % fuel may or may not exist; handle gracefully
    if isfield(udp(setIdx), 'fuel')
        t_fuel = struct2table(udp(setIdx).fuel, 'AsArray', true);
    else
        t_fuel = table(); % empty table if not available
    end

    t_log     = struct2table(udp(setIdx).log, 'AsArray', true);

    % Flattened udp(setIdx)
    % try
    %     T_udp = struct2table_flat(udp(setIdx));
    % catch
    %     warning('struct2table_flat not found. Using struct2table(AsArray=true) as a fallback for T_udp.');
    %     T_udp = struct2table(udp(setIdx), 'AsArray', true);
    % end

    % Flattened vehData(setIdx) metadata (excluding large "data" table)
    try
        T_meta = struct2table_flat(rmfield(vehData(setIdx), {'data'}));
    catch
        warning('struct2table_flat not found. Using struct2table(AsArray=true) as a fallback for T_meta.');
        tmp   = rmfield(vehData(setIdx), {'data'});
        T_meta = struct2table(tmp, 'AsArray', true);
    end

    %------------------------------------------------------------
    % Map of sheet names (based on your CSVs) to tables
    %------------------------------------------------------------
    sheets = {
        'vehData_data',            t_data
        'vehData_scalar',          t_scalar
        'udp_pems',                t_pems
        'udp_bins',                t_bins
        'udp_fuel',                t_fuel
        'udp_log',                 t_log
        'vehData_meta_flattened',  T_meta
    };

    %------------------------------------------------------------
    % Write each table to its own sheet, with name sanitization
    %------------------------------------------------------------
    usedNames = string.empty(0,1);
    for i = 1:size(sheets,1)
        sheetNameRaw = sheets{i,1};
        T            = sheets{i,2};

        if ~(istable(T) && ~isempty(T))
            % Skip empty or non-table outputs
            continue;
        end

        % Respect Excel limits (1,048,576 rows; 16,384 columns)
        [nRows, nCols] = size(T);
        if nRows > 1048576 || nCols > 16384
            warning('Table "%s" (%dx%d) exceeds Excel sheet limits; skipping.', sheetNameRaw, nRows, nCols);
            continue;
        end

        % Sanitize and uniquify the sheet name
        sheetName = sanitizeSheetName(sheetNameRaw);
        sheetName = uniquifySheetName(sheetName, usedNames);
        usedNames(end+1) = string(sheetName);

        % Write the table to the specified sheet
        writetable(T, excelFile, 'Sheet', sheetName);
    end

    fprintf('Excel export complete: %s\n', excelFile);
end

%-----------------------------
% Local helper: sanitizeSheetName
% Removes invalid characters and enforces Excel's 31-char limit.
%-----------------------------
function nameOut = sanitizeSheetName(nameIn)
    % Remove invalid characters: : \ / ? * [ ]
    nameOut = regexprep(nameIn, '[:\\/\?\*\[\]]', '');
    % Trim leading/trailing apostrophes
    nameOut = regexprep(nameOut, '^''+|''+$', '');
    % Replace empty with a safe default
    if isempty(nameOut)
        nameOut = 'Sheet';
    end
    % Truncate to 31 characters
    nameOut = nameOut(1:min(31, numel(nameOut)));
end

%-----------------------------
% Local helper: uniquifySheetName
% Ensures the sheet name is unique in the workbook context.
%-----------------------------
function uniqueName = uniquifySheetName(baseName, usedNames)
    uniqueName = baseName;
    k = 1;
    while any(usedNames == string(uniqueName))
        suffix = sprintf('_%d', k);
        % Ensure suffix fits within 31 characters
        maxBaseLen = 31 - numel(suffix);
        uniqueName = [baseName(1:min(maxBaseLen, numel(baseName))), suffix];
        k = k + 1;
    end
end