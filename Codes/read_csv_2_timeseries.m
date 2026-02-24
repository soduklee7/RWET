T = readtable('veh_accel.csv');
t = T.Time;
if isdatetime(t) || isduration(t)
    t = seconds(t - t(1));
else
    t = double(t) - double(t(1));
end
y = T.Data;     % single column

veh_accel_in = timeseries(y, t);  % or S.time = t; S.signals(1).values = y; S.signals(1).dimensions = 1;

T = readtable('vehspd.csv');
t = T.Time;
if isdatetime(t) || isduration(t)
    t = seconds(t - t(1));
else
    t = double(t) - double(t(1));
end
y = T.Data;     % single column

vehspd_in = timeseries(y, t);  % or S.time = t; S.signals(1).values = y; S.signals(1).dimensions = 1;


% T = readtable('input.csv');
% 
% % Time to seconds, starting at zero
% if isdatetime(T.Time)
%     t = seconds(T.Time - T.Time(1));
% elseif isduration(T.Time)
%     t = seconds(T.Time - T.Time(1));
% else
%     t = double(T.Time);
%     t = t - t(1);
% end
% 
% % Data columns
% vars = T.Properties.VariableNames;
% dataCols = setdiff(vars, {'Time'});
% D = T{:, dataCols};           % N×M
% 
% % Build structure with time
% S.time = t(:);
% S.signals(1).values = D;
% S.signals(1).dimensions = size(D, 2);
% S.signals(1).label = 'Data';  % optional
% 
% % Use in Simulink:
% % - Set From Workspace "Variable name" to S
% % - Sample time: -1