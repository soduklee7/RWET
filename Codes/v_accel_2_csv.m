% ts is a timeseries with ts.Time (N×1) and ts.Data (N×M)
D = v_accel.Data;
% nCh = size(D, 2);
% names = strcat("veh_accel", string(1:nCh));
names = 'Data'
T = [ table(v_accel.Time(:), 'VariableNames', {'Time'}) , ...
      array2table(D, 'VariableNames', cellstr(names)) ];
writetable(T, 'veh_accel.csv');

% ts is a timeseries with ts.Time (N×1) and ts.Data (N×M)
D = vehspd.Data;
% nCh = size(D, 2);
% names = strcat("vehspd", string(1:nCh));
names = 'Data'
T = [ table(vehspd.Time(:), 'VariableNames', {'Time'}) , ...
      array2table(D, 'VariableNames', cellstr(names)) ];
writetable(T, 'vehspd.csv');

