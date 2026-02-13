%% User Options File:  Version:  20260112
%% 
% * v20250124:    Original LD Emissions Template
% * v20250520:    Added CAN Data Signals for reading HEMData files
% * Added 1 header row option in File Import Options
% * Re-arranged sections with most commonly changed options closer to top of 
% file
% * v20250605:    Addition of PEMS analog signals for pressure transducer and 
% thermocouples
% * Added enable and slope/int variables to section "PEMS:  Calculation & Analyzer 
% Options"
% * Added measured and calculated labels to section "PEMS Labels"
% * v20250611:    Removal of AVL/Horiba designation and replaced with Raw/Dilute 
% desigination
% * Data Type/Calulation Set drop down menus removed from Import menu.
% * Data type designation moved to options file section "Data Type"
% * v20250724:    Addition of pedal position D to PEMS input labels and LD Emisisons 
% Report
% * Addition of throttle position to PEMS input labels
% * Added options for fill of missing EndValues in File Import Options
% * v20250730:    Added selection of vehicle speed source as either CAN or GPS 
% in "PEMS: Calculation & Analyzer Options" section
% * Removed "reset" and "quit" buttons from Quick menu
% * v20250815:    Added "Drive Mode" and "Emissions Standard" to the Options 
% File, LD Emissions Report and LD Quality Report
% * v20250930:    Addition of 'Time' label definition for dataType='none' to 
% allow for Sync and Merge of data
% * Changes to loadData.m for calculation of timeStep when dataType='none'
% * v20251202:     Changed the Merge/Apply Callback to include an assignin for 
% udp.  
% * Updated the Merge menu to update data lists and Main Menu drop down.
% * v20260105:     Added option in Label/Sync menu to Pad Missing Data With:  
% NaN or Nearest.  Options file was not changed.
% * v20260112:      Addition of FTP weighted emissions calculation.  Use for 
% an A or A3 Cycle with Inside/Outside cold start.
% * Updates added to page 1 and 2 of LD emissions, quality and PM quality reports.
%% Test Log Options
% Data collected either before or after the actual test
% 
% *Note:  If you change or add log data then you need to define the units in 
% "importDataMenu_App.mlapp" starting on line 125*

%  -----  Test Cycle Data
udo.log.dateTime='01/29/2026';            % '7/30/24' or '7-july-2024' or '7-july-2024 13:00' - Reference Only
udo.log.testCycle='A3';             % test cycle (Road A, ftp3bag, US06 ...) - Reference Only
udo.log.startCond='Cold Start Inside';      % Start Conditions, Hot/Cold, Inside/Outside Start
udo.log.startStop='On';             % Auto start/stop on/off
udo.log.airCond='Off';              % Air Condiditioning on/off
udo.log.driver='Scott E.';          % Driver Name
udo.log.equipment='Sensors SCS:Stk4, Gas:Stk4, FID:Stk4, PM2:Stk5';    % SCS/GAS Stack#, FID Stack#, NH3, PM2, CAN, NH3
udo.log.trailer='No';               % is a trailer being pulled yes/no
udo.log.trailerWt='-';              % Trailer+Ballast weight  e.g.  'Trailer 5000lb + Ballast 500lb = 5500 lb Total'

% ----- FTP Weighted Emissions
udo.log.ftpNormCalc=1;             % Calculate FTP Weighted emissions and include in report 0/1 (disable/enable).  
                                   % Use only with cold start test cycles, Typically A or B cycles
% -----  Notes
udo.log.purpose='TATD Vehicle Survey';  % Purpose of test
udo.log.notes=['No Significant Issues.  Weather station not working.  Data was post-processed with scalar humidity and ambient ' ...
    'temperature in the Sensors post processor'];              % additional notes such as data issues, equipment failures

% ----- Vehicle Data
udo.log.oem='Chevy';                    % OEM ('Ford','GM') - Reference Only
udo.log.model='Silverado';                   % vehicle model (Camry, Focus) - Reference Only
udo.log.my='MY23';                      % model year - Reference Only
udo.log.vehicleID='3116';               % EPA vehicle id - Reference Only
udo.log.vin='3GCPDKEK5PG153116';        % VIN - Reference Only
udo.log.odo=26032;                      % odometer (miles) as numeric  - Reference Only
udo.log.testGroup='PGMXT02.7100';       % Test Group
udo.log.disp='2.7L';
udo.log.testLocation='Road';        % test location (Road, CTF, HTF) - Reference Only
udo.log.emStandard='T3B30';         % Emissions Standard:  T3B30, T3B50, T3B70      
udo.log.driveMode='Normal';         % Vehicle Drive Mode:  Normal, Sport, Eco, Hybrid, Electric, ESave

% ----- Fuel
udo.log.fuel='Gasoline';            % e.g. 'Gasoline','Diesel','E10','E15','E85','NaturalGas'.  For report only.                           
udo.log.ftag='Mix of Comm. and FTAG 43732';   % FTAG Number as Text or Commercial Fuel. For report only


%% PEMS:  Span Gas and PM Filter Data


% ------ Span Gas Values - PEMS
udo.log.noRefSpan=1008;         % PEMS NO Span Gas Bottle Conc.  (ppm)
udo.log.no2RefSpan=124;       % PEMS NO2 Span Gas Bottle Conc.  (ppm)
udo.log.coRefSpan=80500;         % PEMS CO Span Gas Bottle Conc.  (ppm)
udo.log.co2RefSpan=15.54;       % PEMS CO2 Span Gas Bottle Conc. (%)
udo.log.thcRefSpan=9876;     % PEMS Propane C1 Span Gas Bottle Conc.  (ppm)


% ------ PEMS Log Data
% --- filter #1, baseline, No Sample Flow
udo.log.filter1ID='0';          % PEMS Filter #1 ID as Text
udo.log.filter1WtPre=0;         % PEMS Filter #1 weight (mg)
udo.log.filter1WtPost=0;        % PEMS Filter #1 weight (mg)

% --- filter #2, Sample Flow
udo.log.filter2ID='222208364';         % PEMS Filter #2 ID as Text
udo.log.filter2WtPre=401.3370;          % PEMS Filter #2 weight (mg)
udo.log.filter2WtPost=401.3716;          % PEMS Filter #2 weight (mg)

% --- tailpipe PM calculated from filter #2:  copied from Sensor PP file
% (not calculated in Matlab)
udo.log.filterPosition=2;               % filter position with sample flow
udo.log.pmTaipipeMass=18.66;             % "Total Tailpipe PM (mg)" from Sensor PP file
udo.log.pmTailpipeDistanceSpec=2.402;   % "Distance-Specific PM2 Mass (mg/mi)" from Sensors PP file

%% PEMS:  Calculation & Analyzer Options


% ---- Vehicle Weight Class:  Determines report emissions in gm/mile or gm/hp-hr
udo.pems.vehWtClass='LD';           % Vehicle Weight Class.  Only use 'LD' or 'HD' (for NonRoad use 'HD')

% ---- HD Bin Emissions Calculations (Vehicle Specific)
udo.bins.enable=0;                  % enable bin calculations
udo.bins.pmax=505;                  % HP, see CFR 1036.530 (e)
udo.bins.eco2fcl=507;               % gm/hp*hr,  see see CFR 1036.530 (e)

% ---- Source of vehicle speed measurment.  Two Options:
%   'can'  ... CAN data, 
%   'gps'  ... GPS data
% HINT:  CAN is normally the default choice since data can be delayed or
% lost with an inside start using GPS.  
udo.pems.speedSource='can';

% ---- PM analyzer results included in report
udo.pems.pm2Active=1;

% ---- NH3 analyzer results included
udo.pems.nh3Active=0;   % currently does nothing

% ---- Dual FID Methane Analyzer
udo.pems.ch4Active=0;   % currently does nothing

% ---- Enable Analog Data using DataTakker
udo.pems.enableAnalog=0;    % enables analog data in report (reportPEMS_LDEmissions)

% ---- Pressure Transducer from DataTakker
udo.pems.enablePrTransducer=0;  % enables calculation of pressure in psi in pemsDataCalc
udo.pems.prTransSlope=5;
udo.pems.prTransInter=-0.15;

%% Fuel Properties

% udo.fuel.nhv  ........ lower (net) heating value (BTU/lb)
% udo.fuel.cwf  ........ carbon weight fraction  (-)
% udo.fuel.sg   ........ specific gravity (-)


% ------------------------------------------ Fuel Properties
% % ---- fuel tag 28879 - Cert Diesel 2007
% udo.fuel.nhv=18396;   % lower (net) heating value
% udo.fuel.cwf=0.8686;  % carbon weight fraction
% udo.fuel.sg = 0.8581;  % specific gravity

% ---- fuel tag 29351  - Tier 2 Cert Fuel - Gasoline (Indolene)
% udo.fuel.nhv = 18439.0;   % lower (net) heating value
% udo.fuel.cwf = 0.8665;    % carbon weight fraction
% udo.fuel.sg = 0.7421;     % specific gravity

% ---- fuel tag 28637  - Tier 3 Cert Gas 9PSI E10 Reg
% ---- Replaced with ftag 43732 in July 2025
% udo.fuel.nhv = 17894.0;   % lower (net) heating value
% udo.fuel.cwf = 0.8253;    % carbon weight fraction
% udo.fuel.sg = 0.7497;     % specific gravity

% ---- fuel tag 43732  - Tier 3 Cert Gas 9PSI E10 Reg
udo.fuel.nhv = 17885.0;   % lower (net) heating value
udo.fuel.cwf = 0.8282;    % carbon weight fraction
udo.fuel.sg = 0.7494;     % specific gravity


%% Data Type



% ---- Data type determines the calculation set
%   'pems':     PEMS calculation set
%   'dilute':   Chassis Dyno continuous dilute calculation set
%   'raw'       Chassis dyno continuous raw calculation set
%   'miniRoad'  Mini-PEMS used on the road (vehicle speed from GPS)
%   'miniDyno'  Mini-PEMS used on the dyno (vehicle speed from dyno analog signal)
%   'can'       CAN dataset (only checks the time step - no calculations)
%   'none'      No calculation set
udo.log.dataType='pems';


%% File Import Options

% ---------- Fill value for missing data which is not at beginning or end
% ---------- of the data column (aka label).  Not EndValues.
% 'previous'    ...previous non-missing value
% 'next'        ...fill missing data with next non-missing value
% 'nearest'     ...nearest non-missing value 
% 'linear'      ...linear interpolation of neighboring data.  Only works if all data is numerical (no string data)
% 'zero'        ...fill missing data with zero.  Only works if all data is numerical (no string data)
udo.import.missingData='nearest';

% ------------------------------------------  Fill value for End Values
% 'none'     ...Endvalues are filled with NaN
% 'previous' ...previous value which is not missing
% 'next'     ...Next value which is not missing
% 'extrap'   ...Extrapolate missing end values
% 'nearest'  ...Nearest missing end value
% 'zero'     ...fill missing data with zero.  Only works if all data is numerical (no string data)
%  HINT:  Use 'Nearest' if you have blank values at the start of the data.
%         Using 'none' will fill blanks with NaN which cannot be integrated (i.e.
%         vehicle speed cannot be integrated to get distance).
udo.import.endValues='nearest';

% -----------------------------------------  Number of Header Rows
%   3 ... three header rows (PEMS):  1) VariableName, 2) VariableDescription, 3) VariableUnits
%   2 ... two header rows (Dyno):  1) VariableName, 2) VariableUnits
%   1 ... one header row (CAN):  1) VariableName   (works for HEMData)
udo.import.numHeaderRows=3; 

%% Humidity Correction Factor

% ------------------------------------------- Humidity correction factor
% Method of calculation
%       0:  No correction
%       1:  CFR 1066.615 Vehicles at or below 14,000 lbs GVWR (use for SC03 and 1066 testing)
%       2:  CFR 1065.670 SI  
%       3:  CFR 1065.670 Diesel
udo.log.kh = 2;
%% PEMS:  File Import Options

% ------------------  PEMS Import Options
% loadData.m can be modified to load the data "As Is" directly from the
% Sensors post-processor.  This requires the data to be post-processed to
% contain only the SAMPLE data using the correct Markers.  However, there
% are two "Vehicle Speed" labels and one must be modified, by hand, to read
% "Vehicle SpeedMPH".
% 
% or "Hand" which is hand manipulated with first row
% being label name, second row being units and data starting on third line.
% The "Vehicle Speed" must also be modified.

% --- Keep Rows
% Keep only rows, in a particular label (CharLabel), which matches the char array (Char) given.
% All other rows will be deleted.  The char array much be an exact match.
% Example:  In the column labelled 'GasPath" delete all rows which are Not 'SAMPLE'
% i.e. delete all rows for 'STANDBY' or 'CALIBRATION'
udo.pems.editRowKeepChar=1;               % turn on/off this feature with 1/0
udo.pems.rowKeepCharLabel='GasPath';  % Label Name with rows to keep
udo.pems.rowKeepChar='SAMPLE';        % Char array of rows to keep

% --- Remove Rows Equal to Zero 
% Remove rows (i.e. engine speed) when a particular label is equal to zero 
% within the first N seconds of measurement.  
% N should be small (20 sec) to avoid removing start-stop data.
udo.pems.editRowRemoveZero=0;          % turn on/off this feature with 1/0
udo.pems.rowRemoveZero='EngineRPM';  % Label Name with rows to remove
udo.pems.rowRemoveSec=20;          % within first N seconds

% --- Remove columns
% Remove all columns with a label name containing the char array
udo.pems.editColRemove=1;
udo.pems.colRemoveCharLabel='NotAvailable';

% --- PEMs Time
% Convert PEMS to a datetime variable and convert to a numeric sample time
% beginning with zero.  Use this option when importing a Sensor PP (Post-Processing)
% file directly.
% Use udo.pems.editPemsTime=1 when the Time has a format hh:mm:ss.xxx such as 12:31:48.906
% Use udo.pems.editPemsTime=0 when the Time is simply in seconds such as [0 1 2 3 4 5 ...]
udo.pems.editPemsTime=1;


%% Chassis Dyno:  Raw and Dilute Options

% -------------------------- Ambient Conditions - Dyno Dilute Only
udo.log.thcAmbCorr=0;           % ambient THC (ppm) for dilute dyno calculations
udo.log.noxAmbCorr=0;           % ambient NOx (ppm) for dilute dyno calculations
udo.log.coAmbCorr=0;            % ambient CO (ppm) for dilute dyno calculation
udo.log.co2AmbCorr=0;           % ambient CO2 (ppm) for dilute dyno calculation


% -------------------------- Is SC03 Cycle:  Raw and Dilute
% If the cycle is an SC03, the calculation of the humidity correction
% factor changes according to 1066.615(a)(2).  Hs = 0.8825
% Method of calculation must be udo.sd.kh=1
%       0:  Cycle is NOT SC03
%       1:  Cycle IS SC03
udo.dyno.isSC03 = 0;

% -------------------------  Dilution Factor Calculation:  Dyno Dilute Only
%       1: calculate DF using only CO2 (use when HC or CO data is bad)
%       2: calculate using CO2, CO and HC (best method)
udo.dyno.dfMethod = 2;

%% Mini-PEMS Options

% -------------------------------------------- Mini-PEMS Sensors Installed
udo.sensors.noxt=0;
udo.sensors.noxf=0;
udo.sensors.nh3=0;
udo.sensors.co2=0;
udo.sensors.massFlow=0;
udo.sensors.gps=0;

% ------------- Ambient Conditions - Mini-PEMS Only - Backup for weather station failure
udo.log.ambientT=20;           % Ambient Temperature (C)  - backup for mini-pems weather station
udo.log.rHumidity=40;          % relative humidity (%)  - backup for mini-pems weather station
udo.log.baro=1000;             % barometric pressure (mbar)  -- backup for mini-pems weather station

% ------------------------------------------- Weather Station
% Only used on mini-PEMS calculation (sdDataCalc.m)
%       0:  Use scalar data from log file
%       1:  Use vector data from measurement file
udo.sensors.weather=1; 

% ------------------------------------------- Analog dyno speed
% ---------------------------------  Used when mini-PEMS is run on the dyno
%   0:  not included in measurement
%   1:  included in measurement
udo.sd.analogInput=0;

% ----------------------------------------- Volts to dyno speed conversion
% --------------------------------------  Dyno analog speed volts to speed
% udo.sd.analogToMph=10;  % CTF and HTF
udo.dyno.analogToMph=20; % dyno 5

% ------------------------------------------- Ratio of molecular weights
% for calculation of emissions mass flow according to:    40CFR 90.419
% 40CFR 90.419 has since been replaced.  See previous versions of the CFR
% dating back to 1/1/2018 to view the calculations related to emissions
% mass flow.
 udo.sd.mwRatioNOx=46.01/28.97;   % ratio of molecular weight NO2/air
 udo.sd.mwRatioNH3=17.031/28.97;  % ratio of molecular weight NH3/air
 udo.sd.mwRatioCO2=44.01/28.97;   % ratio of molecular weight CO2/air

% ------------------------------------------- Mass Flow Ks Factor 
% Ks Factor Setup11, Adapter J02, LFE M6, Sensors 1234, FlowMaster Muffler,
% 40" Before Adapter, 2.5" adapter diameter
udo.sensors.ksFlow=[   19.2,  37.8,  59.3,  78.8,  98.3, 120.2, 142.3, 195.6, 240.8, 308.8, 359.0, 411.7, 469.9, 525.8, 580.7];
udo.sensors.ksFactor=[1.398, 1.057, 0.916, 0.887, 0.876, 0.858, 0.847, 0.849, 0.885, 0.846, 0.864, 0.873, 0.869, 0.871, 0.872];

%% Trace Options
% Dyno Trace Options including Grade.  Only necessary if creating a trace on 
% the road which is later used on the dyno.

udo.trace.speedUnits='km/hr';               % units required for AVL dyno trace file
udo.trace.speedLabel='VehicleSpeed_Trace';  % vehicle speed trace written to Excel file and Vehicle Trace
udo.trace.altitudeLabel='Altitude_Trace';   % altitude in meters used to calculate Road_Grade written to Excel
udo.trace.gradeLabel='Road_Grade';  % road grade written to Excel file and Vehicle Trace
udo.trace.phaseLabel='Phase';       % dyno phase written to Vehicle Trace and Excel file
udo.trace.distanceLabel='Cumlative_Distance'; % cumlative distance written to Excel file

% udo.trace.gradeWindow=50;    % moving avg window size in # of points (i.e. 50=5sec for 10 hz data)
% udo.trace.gradeRateLimit=1;  % rate limit for filtering grade
% udo.trace.gradeDistance=50;  % distance over which to calculate grade (m)

udo.trace.gradeWindow=30;    % moving avg window size in # of points (i.e. 50=5sec for 10 hz data)
udo.trace.gradeRateLimit=5;  % rate limit for filtering grade
udo.trace.gradeDistance=50;  % distance over which to calculate grade (m)
%% Display Options
% Default Line Color and Line Width

 udo.display.lineColor = [0, 0, 0;...  % black 1
    .85, .33, 0.1;...     % orange 2
     0, 0, 1;...          % blue 3
     1, 0, 1;...          % magenta 4
    .2, .49, .16;...      % green 5
    .53, .02, .02;...     % blood red 6
     .49, .18, .56;...    % purple 7
     .58, .31, 0];        % copper 8
 
% default options
set(groot,'defaultLineLineWidth',1.5)
set(groot,'DefaultAxesColorOrder',udo.display.lineColor)
%% GPS Locations
% GPS Locations for use in Trace definition on PEMS and Mini-PEMS data

% location1 and location2 are diagonals of a rectangle defining an area
udo.gps(1).name='Location:  EPA Lab Front Gate';
udo.gps(1).location1=[42.302541 -83.710924];
udo.gps(1).location2=[42.302770 -83.710608];

%% Mini-PEMS Labels
% Options for measured and calculated label names

% ----------- Mini-PEMS Input
udo.sd.time='Time';           % input label name for time
udo.sd.speed='Speed_mph';  % input label name for vehicle speed
udo.sd.noxT='NOXT';            % Tailpipe NOx Wet Uncorrected
udo.sd.noxF='NOXF';           % Filtered Tailpipe NOx Wet Uncorrected
udo.sd.nh3='NH3';             % NH3 (ppm)
udo.sd.altitude='Altitude';   % input label name for altitude
udo.sd.texhaust='Texh1';      % input label name for exhaust temperature
udo.sd.lambda='Lambda';       % input label name for lambda
udo.sd.latitude='Latitude';   % input label name for Latitude
udo.sd.longitude='Longitude'; % input label name for Longitude
udo.sd.analogSpeed='AnalogSpeed'; % input label for analog speed (Volts)
udo.sd.co2w='CO2W';           % input label for CO2 Wet
udo.sd.tambient='TAmbient';   % ambient temperature from weather station
udo.sd.baro='PKPA';           % barometric pressure from weather station
udo.sd.rh='RH';               % relative humidity from weather station

% --------- SD Calculations - Vector
udo.sd.mph='VehicleSpeed_MPH';                 % Vehicle speed in mph
udo.sd.kph='VehicleSpeed_KPH';                 % Vehicle speed in kph
udo.sd.kNOxT='kNOxT';                     % Tailpipe NOx corrected for humidity (ppm)
udo.sd.kNOxF='kNOxF';                     % Tailpipe Filtered NOx Corrected (ppm)
udo.sd.co2WetPpm='co2Wet_PPM';            % CO2 Wet PPM
udo.sd.estNH3='estNH3';                   % estimated NH3 (=kNOxT-kNOxF) (ppm)
udo.sd.massFlowUn='exhMassFlowTCorr';     % mass Flow Uncorrected
udo.sd.massFlowCorr='massFlowKsCorr';     % mass Flow Corrected for Ks
udo.sd.noxTMassFlow='noxTMassFlow';       % corrected NOxT mass flow (gms/sec)
udo.sd.noxFMassFlow='noxFMassFlow';       % corrected NOxF mass flow (gms/sec)
udo.sd.co2MassFlow='co2MassFlow';         % co2 wet mass flow (gms/sec)
udo.sd.nh3MassFlow='nh3MassFlow';         % NH3 mass flow (gms/sec)
udo.sd.estNH3MassFlow='estNH3MassFlow';   % estimated NH3 mass flow (gms/sec)
udo.sd.sumNOxT='Cummulative_NOxT';        % Cummulative corrected NOxT (gms)
udo.sd.sumNOxF='Cummulative_NOxF';        % Cummulative corrected NOxF (gms)
udo.sd.sumCO2='Cummulative_CO2';          % Cummulative wet CO2 (gms)
udo.sd.sumNH3='Cummulative_NH3';          % Cummulative NH3 (gms)
udo.sd.sumEstNH3='Cummulative_estNH3';    % Cummulative estimated NH3 (gms)
udo.sd.noxTSumGmMile='Cummulative_NOxT_gmMile';   % Cummumlative NOxT gms/mile
udo.sd.noxFSumGmMile='Cummulative_NOxF_gmMile';   % Cummumlative NOxF gms/mile
udo.sd.distSumKm='Cummulative_Distance_Km';       % Cummulative distance in km
udo.sd.distSumMile='Cummulative_Distance_Miles';  % Cummulative Distance in miles

% --------- SD Calculations - Scalar
udo.sd.kHumidity='NOx_Correction_Factor'; %NOx correction factor for humidity (scalar and vector)
udo.sd.distanceKm='Distance_Km';          % total distance in km
udo.sd.distanceMile='Distance_Mile';      % total distance in miles
udo.sd.totalMassFlow='totalMassFlow_KsCorr';     % total mass flow corr for Ks (kg)
udo.sd.totalNOxT='totalNOxT';             % total corrected NOxT (gms)
udo.sd.totalNOxF='totalNOxF';             % total corrected NOxF  (gms)
udo.sd.totalCO2='totalCO2';               % total wet CO2 (gms)
udo.sd.totalNH3='totalNH3';               % total NH3 mass (gms)
udo.sd.totalEstNH3='totalEstNH3';         % total estimated NH3 mass (gms)
udo.sd.noxTGmMile='noxTGmMile';           % corrected NOxT gm/mile
udo.sd.noxFGmMile='noxFGmMile';           % corrected NOxF gm/mile
udo.sd.co2GmMile='co2GmMile';             % CO2 Wet gm/mile
udo.sd.nh3GmMile='nh3GmMile';             % NH3 gm/mile
udo.sd.estNH3GmMile='estNH3GmMile';       % estimated NH3 gm/mile
udo.sd.fuelEconomy='FuelEconomy';         % Fuel Economy (mpg)
%% Chassis Dyno Labels:  Dilute

if strcmp(udo.log.dataType,'dilute')

    % -------------------------------------------------------------------------
    % -------------------------------------------------------------------------
    % -------------------------------------------------------------------------
    % ---- Dyno Continuous (Modal) Data - AVL Dyno
    
    % ----------- Dyno Input (AVL)
    % Note: udo.dyno.noxDiluteCorr=udo.dyno.noxDilute since AVL measures
    %       NOx as wet (Horiba meas. dry but the input labels are common)
    udo.dyno.time='Time';                % Time
    udo.dyno.speed='V_ACT';                       % Vehicle Speed
    udo.dyno.phase='DYSPHASE';                    % Cycle Phase (e.g. ftp phase 1, 2, 3 )
    udo.dyno.exhaustFlow='VolFlow_Gas_TailPipe';  % Volumetric exhaust gas flow
    udo.dyno.ambientAirT='T_AIR';                 % dyno - input label name for ambient air temperature
    udo.dyno.ambientAirP='P_AIR';                 % dyno - input label name for ambient air pressure
    udo.dyno.rHumidity='PHI';                     % dyno - input label name for relative humidity
    udo.dyno.cvsAirT ='T_CVS';                    % dyno - temperature at the CVS
    udo.dyno.cvsAirP='P_CVS';                     % dyno - pressure at the CVS
    udo.dyno.noxDilute='Conc_NOX_Diluted';        % Dilute NOx Wet
    udo.dyno.noxDiluteCorr='Conc_NOX_Diluted';    % Dilute NOx shifted and dry/wet correction applied (kH not applied)
    udo.dyno.co2Dilute='Conc_CO2_Diluted';        % Dilute CO2 Wet
    udo.dyno.thcDilute='Conc_HC_Diluted';          % dyno (dilute) - input label name for total HC dilute
    udo.dyno.coDilute='Conc_CO_Diluted';          % dyno (dilute) - input label name for CO dilute
    udo.dyno.cvsFlow='Q_CVS';                     % dyno (dilute) - input label name for CVS volumetric flow
    
    
end
%% Chassis Dyno Labels:  Raw

if strcmp(udo.log.dataType,'raw')

    %
    % --- Note:  Horiba analyzers for NOx, CO, and CO2 have chillers and
    % measure Dry emissions.  The raw measurement from the analyzer is
    % labelled x_PstNOx_meas (for example) and is a dry measurement
    % which has already been shifted for transfer delay.  The calculated 
    % result x_PstNOx is the measured result (x_PstNOx_meas) with the 
    % dry/wet correction applied and, in the case of NOx, the humidity 
    % correction is also applied.  THC and CH4 are measured on a wet basis 
    % for the Horiba.

    % All raw emissions concentrations are assumed to be time-aligned (shifted) to
    % the exhaust flow and corrected for dry/wet.  NOx correction factor
    % can be applied with udo.log.kh=1 as needed.
    
    udo.dyno.time='Time';                       % Time
    udo.dyno.speed='ActSpeed';                  % Vehicle Speed
    udo.dyno.phase='Phase';                     % Cycle Phase (e.g. ftp phase 1, 2, 3 )
    udo.dyno.exhaustFlow='ExhFlow';             % Volumetric exhaust gas flow (m3/min) Dilute or Raw
    udo.dyno.ambientAirT='Temp';                % dyno - ambient air temperature
    udo.dyno.ambientAirP='Baro';                % dyno - ambient air pressure
    udo.dyno.rHumidity='RelHum';                % dyno - relative humidity
    udo.dyno.cvsAirT ='CVSTemp';                % dyno - temperature at the CVS
    udo.dyno.cvsAirP='CVSPressure';             % dyno - pressure at the CVS
    udo.dyno.cvsFlow='CVSFlowCorr';             % CVS Flow in (m3/min)
    udo.dyno.dilAirFlow='DilAir';               % Dilution Air Flow in (m3/min)
    udo.dyno.noxRawCorr = 'NOX';                % NOx dry to wet corr (ppm)
    udo.dyno.co2RawCorr = 'CO2';                % CO2 dry to wet corr (ppm)
    udo.dyno.thcRawCorr = 'HC';                 % THC dry to wet corr (ppm) 
    udo.dyno.coRawCorr = 'COL';                 % CO dry to wet corr (ppm)


end

%% Chassis Dyno Labels:  Calculated

% -------------------------------------------------------------------------
% ------------- Calculated Dyno Labels - AVL and Horiba

% --- Cycle based calculations
udo.dyno.df='DilutionFactor';               % dyno (dilute) - label name for calculated dilution factor
udo.dyno.DFAvgPh1='DF_AvgPh1';              % Average value of continuous DF calculation phase 1
udo.dyno.mph='VehicleSpeed_MPH';            % Vehicle speed in mph
udo.dyno.kph='VehicleSpeed_KPH';              % Vehicle speed in kph
udo.dyno.vMixCVS='Cummulative_Volume_CVS';    % cummulative volume at CVS (not adding sample back in)
udo.dyno.distSumKm='Cummulative_Distance_Km'; % Cummulative distance in km
udo.dyno.distSumMile='Cummulative_Distance_Miles';  % Cummulative Distance in miles
udo.dyno.sumExhFlow='Cummulative_Exhaust_Flow';     % Cummulative exhaust flow (m3)
udo.dyno.exhMassFlow='Exhaust_Mass_Flow';           % Exhaust Mass Flow (kg/hr)
udo.dyno.distanceKm='Distance_Km'; % total distance in km
udo.dyno.distanceMile='Distance_Mile'; % total distance in miles
udo.dyno.distancePh1='Distance_MilePh1'; % Phase 1 distance (miles)
udo.dyno.distancePh2='Distance_MilePh2'; % Phase 2 distance (miles)
udo.dyno.distancePh3='Distance_MilePh3'; % Phase 3 distance (miles)
udo.dyno.distancePh4='Distance_MilePh4'; % Phase 4 distance (miles)
udo.dyno.totalExhFlow='Total_Exhaust_Flow'; % total exhaust flow (m3)
udo.dyno.massTotalExhFlow='Mass_Total_Exhaust_Flow'; % total mass exhaust flow (kg)
udo.dyno.kvolstd="Corr. Factor Std Volume";     % corr for std reference volume (calc but not used)

%--- NOx calculations
udo.dyno.noxTailpipeShift='NOx_Tailpipe_Shift';  % NOx tailpipe shifted/aligned with mass flow rate (ppm)
udo.dyno.knoxTailpipeShift='kNOx_Tailpipe_Shift';  % NOx tailpipe shifted and corrected for humidity
udo.dyno.noxDiluteShift='NOx_Dilute_Shift';      % NOx shifted/aligned to mass flow rate (ppm)
udo.dyno.knoxDiluteShift='kNOx_Dilute_Shift';      % NOx corrected for humidity (ppm)
udo.dyno.kHumidity='NOx_Correction_Factor';   % NOx correction factor for humidity
udo.dyno.noxMassFlow='NOx_Mass_Flow';         % NOx mass flow (corrected for humidity)(gm/sec)
udo.dyno.knoxMassTotal='kNOx_Mass_Total';     % NOx total mass (gms)
udo.dyno.knoxMassPh1='kNOx_Mass_Phase1';  % NOx total mass in Phase 1 (gms)
udo.dyno.knoxMassPh2='kNOx_Mass_Phase2';  % NOx total mass in Phase 2 (gms)
udo.dyno.knoxMassPh3='kNOx_Mass_Phase3';  % NOx total mass in Phase 3 (gms)
udo.dyno.knoxMassPh4='kNOx_Mass_Phase4';  % NOx total mass in Phase 4 (gms)
udo.dyno.noxSum='Cummulative_NOx_Mass';       % Cummulative NOx (gms)
udo.dyno.noxGpmTotal='NOx_Gms_Per_Mile'; % nox in gms/mile
udo.dyno.noxGpmPh1='NOx_Gms_Per_Mile_Ph1';  % NOx ph1 (gms/mile)
udo.dyno.noxGpmPh2='NOx_Gms_Per_Mile_Ph2';  % NOx ph2 (gms/mile)
udo.dyno.noxGpmPh3='NOx_Gms_Per_Mile_Ph3';  % NOx ph3 (gms/mile)
udo.dyno.noxGpmPh4='NOx_Gms_Per_Mile_Ph4';  % NOx ph4 (gms/mile)

%  dilute to raw calculations
udo.dyno.knoxDil2Raw='kNOx_Dilute2Raw';     % kNOx ppm converted from dilute to raw using DF
udo.dyno.coDil2Raw='CO_Dilute2Raw';         % CO ppm converted from dilute to raw using DF
udo.dyno.thcDil2Raw='THC_Dilute2Raw';       % THC ppm converted from dilute to raw using DF
udo.dyno.co2Dil2Raw='CO2_Dilute2Raw';       % CO ppm converted from dilute to raw using DF


% --- CO2 calculations
udo.dyno.co2TailpipeShift='CO2_Tailpipe_Shift';  % CO2 tailpipe shifted
udo.dyno.co2MassFlow='CO2_Mass_Flow';           % gm/sec
udo.dyno.co2Sum='Cummulative_CO2_Mass';         % gm
udo.dyno.co2MassTotal='CO2_Mass_Total';         % CO2 total mass (gms) for total cycle distance
udo.dyno.co2GpmTotal='CO2_gmsPerMile_Total';    % co2 in gms/mile for total cycle distance
udo.dyno.co2MassPh1='CO2_Mass_Phase1';          % co2 mass phase 1 (gms)
udo.dyno.co2MassPh2='CO2_Mass_Phase2';          % co2 mass phase 2 (gms)
udo.dyno.co2MassPh3='CO2_Mass_Phase3';          % co2 mass phase 3 (gms)
udo.dyno.co2MassPh4='CO2_Mass_Phase4';          % co2 mass phase 4 (gms)
udo.dyno.co2GpmPh1='CO2_Gms_Per_Mile_Ph1';      % CO2 grams/mile ph1 (gms/mile)
udo.dyno.co2GpmPh2='CO2_Gms_Per_Mile_Ph2';      % CO2 grams/mile ph2 (gms/mile)
udo.dyno.co2GpmPh3='CO2_Gms_Per_Mile_Ph3';      % CO2 grams/mile ph3 (gms/mile)
udo.dyno.co2GpmPh4='CO2_Gms_Per_Mile_Ph4';      % CO2 grams/mile ph4 (gms/mile)


% --- THC calculations
udo.dyno.thcTailpipeShift='THC_Tailpipe_Shift';  % THC tailpipe shifted
udo.dyno.thcMassFlow='THC_Mass_Flow';           % gm/sec
udo.dyno.thcSum='Cummulative_THC_Mass';         % gm
udo.dyno.thcMassTotal='THC_Mass_Total';         % THC total mass (gms)
udo.dyno.thcGpmTotal='THC_Gms_Per_Mile';         % THC in gms/mile
udo.dyno.thcMassPh1='THC_Mass_Phase1';          % THC mass phase 1 (gms)
udo.dyno.thcMassPh2='THC_Mass_Phase2';          % THC mass phase 2 (gms)
udo.dyno.thcMassPh3='THC_Mass_Phase3';          % THC mass phase 3 (gms)
udo.dyno.thcMassPh4='THC_Mass_Phase4';          % THC mass phase 4 (gms)
udo.dyno.thcGpmPh1='THC_Gms_Per_Mile_Ph1';      % THC grams/mile ph1 (gms/mile)
udo.dyno.thcGpmPh2='THC_Gms_Per_Mile_Ph2';      % THC grams/mile ph2 (gms/mile)
udo.dyno.thcGpmPh3='THC_Gms_Per_Mile_Ph3';      % THC grams/mile ph3 (gms/mile)
udo.dyno.thcGpmPh4='THC_Gms_Per_Mile_Ph4';      % THC grams/mile ph4 (gms/mile)


% --- CO calculations
udo.dyno.coTailpipeShift='CO_Tailpipe_Shift';  % CO tailpipe shifted
udo.dyno.coMassFlow='CO_Mass_Flow';             % gm/sec
udo.dyno.coSum='Cummulative_CO_Mass';           % gm
udo.dyno.coMassTotal='CO_Mass_Total';           % CO total mass (gms)
udo.dyno.coGpmTotal='CO_Gms_Per_Mile';          % CO in gms/mile
udo.dyno.coMassPh1='CO_Mass_Phase1';            % CO mass phase 1 (gms)
udo.dyno.coMassPh2='CO_Mass_Phase2';            % CO mass phase 2 (gms)
udo.dyno.coMassPh3='CO_Mass_Phase3';            % CO mass phase 3 (gms)
udo.dyno.coMassPh4='CO_Mass_Phase4';            % CO mass phase 4 (gms)
udo.dyno.coGpmPh1='CO_Gms_Per_Mile_Ph1';        % CO grams/mile ph1 (gms/mile)
udo.dyno.coGpmPh2='CO_Gms_Per_Mile_Ph2';        % CO grams/mile ph2 (gms/mile)
udo.dyno.coGpmPh3='CO_Gms_Per_Mile_Ph3';        % CO grams/mile ph3 (gms/mile)
udo.dyno.coGpmPh4='CO_Gms_Per_Mile_Ph4';        % CO grams/mile ph4 (gms/mile)


% ++ Dilute
udo.dyno.co2WetPercent='CO2Wet_Percent'; % (percent)
udo.dyno.co2WetPpm='CO2Wet_Ppm';  % (ppm)
udo.dyno.co2WetPercentShift='CO2Wet_Percent_Shift';  % transport delay shift (percent)
%% PEMS:  Input Labels


% ******  Note:  Calculations are applied only to the Input labels.  For
% example, if you where to sync (time align) the label for NOx or kNOx and
% then re-calculate the dataset - nothing will happen since calculations do
% not operate on these labels.  Calculations begin with concentations which
% have already been corrected for humidity (NOx) and dry-to-wet
% correction factor.


% ------------------- PEMS Input Labels
udo.pems.time='TIME';                   % Time
udo.pems.speedCAN='VehicleSpeed';       % Vehicle Speed CAN
udo.pems.speedGPS='LimitAdjustedIGPS_GROUND_SPEED';  % Vehicle Speed GPS
udo.pems.NO='NO';             % NO Dry
udo.pems.NO2='NO2';             % NO2 Dry
udo.pems.CO='CO';             % CO Dry
udo.pems.CO2='CO2';             % CO2 Dry
udo.pems.HC='THCConcentration'; % HC Dry
udo.pems.wetkNOx='WetKNOx';             % NOx Wet Corr for humidity
udo.pems.wetkNOxDrift='WetKNOx_drift_';  % NOx Wet Corr for humidity and drift
udo.pems.corrCuNOxGmPerMile='CorrectedCumulativeMassNOx';  % Corr. cummulative NOx in gm/mile
udo.pems.cuHCGmPerMile='CumulativeMassHC';  % Cummulative HC in gm/mile
udo.pems.cuCOGmPerMile='CumulativeMassCO';  % Cummulative CO in gm/mile
udo.pems.cuCO2GmPerMile='CumulativeMassCO2';  % Cummulative CO2 in gm/mile
udo.pems.wetNO='WetNO';                       % NO Wet
udo.pems.wetNODrift='WetNO_drift_';         % NO wet corr. for Drift
udo.pems.wetNO2='WetNO2';                   % NO2 wet
udo.pems.wetNO2Drift='WetNO2_drift_';       % NO2 wet corr. for Drift
udo.pems.wetCO='WetCO';                     % CO Wet
udo.pems.wetCODrift='WetCO_drift_';         % CO Wet corr. for Drift
udo.pems.wetCO2='WetCO2';                   % CO2 Wet
udo.pems.wetCO2Drift='WetCO2_drift_';       % CO2 Wet corr. for Drift
udo.pems.wetHC='WetHC';                     % HC Wet
udo.pems.wetHCDrift='WetHC_drift_';         % HC Wet corr. for Drift
udo.pems.altitude='LimitAdjustedIGPS_ALT';      % Altitude
udo.pems.texhaust='ExhaustTemperature';         % Exhaust Temperature
udo.pems.lambda='Lambda';                       % lambda
udo.pems.latitude='GPSLatitude';                % Latitude
udo.pems.longitude='GPSLongitude';              % Longitude
udo.pems.ambientAirT='LimitAdjustedISCB_LAT';   % ambient air temperature Weather Station
udo.pems.ambientAirTCAN='Amb_AirTemp_';         % ambient air temperature CAN (C)
udo.pems.ambientAirP='AmbientPressure';         % ambient air pressure (F)
udo.pems.rHumidity='LimitAdjustedISCB_RH';      % relative humidity
udo.pems.scfm='ExhaustVolumetricFlowRate_SCFM'; % Exhaust Volumetric Flow Rate at STP (ft3/min)
udo.pems.engineSpeed='EngineRPM';               % Engine speed from CAN
udo.pems.coolantT='EngineCoolantTemperature';   % Engine Coolant Temperature
udo.pems.pedalPosD='Accel_PostnD';              % Accel Pedal Position D (%)
udo.pems.throttleAbs='AbsThrottlePostn';        % Absolute throttle position
udo.pems.throttleRel='Rel_ThrottlePostn';       % Relative throttle position


udo.pems.regenStatus='DPFRegenStatus';          % Regen Status (0/1)
udo.pems.dpfTrigPct='Norm_DPFTrig_Pct';         % DPF Trigger Percent (%)
udo.pems.egt11='Exh_GasTemp_1_1';               % Exhaust Gas Temp 11
udo.pems.egt12='Exh_GasTemp_1_2';               % Exhaust Gas Temp 12
udo.pems.egt13='Exh_GasTemp_1_3';               % Exhaust Gas Temp 13
udo.pems.egt14='Exh_GasTemp_1_4';               % Exhaust Gas Temp 14
udo.pems.reagentLevel='ReagentTankLvl_';        % DEF tank Level (%)
udo.pems.kNOx11='Corr_NOx1_1';                  % NOx sensor corrected 11
udo.pems.kNOx12='Corr_NOx1_2';                  % NOx sensor corrected 12

udo.pems.noxHumidCorrFac='NOxHumidityCorrectionFactor'; % NOx Humidity Corr Factor Calculated by PEMS unit
udo.pems.dryWetCorrFac='Dry_to_WetCorrectionFactor';      % Dry to Wet Correction Factor
udo.pems.lambda='Lambda';                       % Lambda
udo.pems.FAEquivRatio='F_AEquiv_Ratio';         % Fuel Air Equivalence Ratio (from CAN)
udo.pems.pmMassTailpipe='PM2MassAtTailpipe';    % PM mass at tailpipe (corr. for filter weights)

udo.pems.sampleFlow='SampleFlow';               % Sample Flow (lpm)
udo.pems.sampleH='SampleHumidity';              % Sample Humidity
udo.pems.sampleT='SampleTemperature';           % Sample Temperature
udo.pems.heatedFilterT='HeatedFilterTemperature';     % Heated Filter Temperature
udo.pems.faults='Faults';                       % Power distribution faults
udo.pems.batt2Voltage='Battery2Voltage';        % Battery 2 Voltage (volts)
udo.pems.batt1Voltage='Battery1Voltage';        % Battery 1 Voltage (volts)
udo.pems.numOfDTC='No_OfDTCs';                  % Number of DTCs
udo.pems.blockT='BlockTemperature';             % Block Temperature (C)
udo.pems.filterBlockT='FilterBlockTemp';        % Filter Block Temperature (C)
udo.pems.filter1Active='Filter1Active';         % Filter 1 Active
udo.pems.filter2Active='Filter2Active';         % Filter 2 Active
udo.pems.filterByActive='FilterBypassActive';   % Filter Bypass Active

udo.pems.pmDR='DilutionRatio';                  % PM2 Dilution Ratio
udo.pems.pmDRPegasor='PegasorDilutionRatio';    % Pegasor Dilution Ratio
udo.pems.pmDilSampleFlow='DiluterSampleFlow';   % PM2 Diluter Sample Flow
udo.pems.pmDilAirFlow='DilutionAirFlow';        % PM2 Dilution Air Flow
udo.pems.pmSampleInletPr='SampleInletPressure'; % PM2 Sample Inlet Pressure
udo.pems.pmSampleInletT='SampleInletTemp';      % PM2 Sample Inlet Temperature
udo.pems.pmMakeupFlow='MakeupFlow';             % PM2 Makeup Flow
udo.pems.pmFilterFlow='FilterFlow';             % PM2 Filter Flow
udo.pems.pmFilterFlowT='FilterFlowTemp';        % PM2 Filter Flow Temperaure
udo.pems.pmFilterBlockT='FilterBlockTemp';      % PM2 Filter Block Temperature
udo.pems.pmFilterOutletPr='FilterOutletPressure';  % PM2 Filter Outlet Pressure
udo.pems.pmInletPr='InletPressure';             % PM2 Inlet Pressure
udo.pems.pmInletFlow='InletFlow';               % PM2 Inlet Flow

% Input or Calculated
udo.pems.enginePowerKw='calculatedEnginePowerKW';       % Engine power for HD emissions gm/kw-hr
udo.pems.enginePowerHp='calculatedEnginePowerHP';     % Engine power for HD emissions gm/hp-hr
udo.pems.engineTorque='CAN_calculatedEngineTorque';    %  engine torque in N-m  (torque inputed from CAN)

% Analog Signals
udo.pems.prTransducer='PressureTransducer';    % Measured Pressure in Volts
udo.pems.tcTemp1='PreCatTempTC';
udo.pems.tcTemp2='PostCatTempTC';
udo.pems.tcTemp3='TransducerTC';

%% PEMS:  Calculated Labels


% ----------------- PEMS Calculated Labels - Vector
udo.pems.mph='VehicleSpeed_MPH';         % Vehicle speed in mph
udo.pems.kph='VehicleSpeed_KPH';         % Vehicle speed in kph
udo.pems.kNOxMassFlow='kNOx_MassFlow';               % NOx mass flow (wet, corrected for humidity)(gm/sec)
udo.pems.kNOxMassFlowDrift='kNOx_MassFlow_Drift';    % NOx mass flow (wet, corr for humidity and drift) (gm/sec)
udo.pems.kNOxSum='Cumulative_kNOx_Mass';            % Cummulative humidity corr. NOx mass (gms)
udo.pems.kNOxSumDrift='Cumulative_kNOx_Mass_Drift'; % Cummulative humidity and drift corr. NOx mass (gms)
udo.pems.coMassFlow='CO_MassFlow';                  % instantaneous CO wet Mass Flow (gm/sec)
udo.pems.coMassFlowDrift='CO_MassFlow_Drift';       % instantaneous CO wet Mass Flow corr. for drift (gm/sec)
udo.pems.coSum='Cumulative_CO_Mass';               % Cummulative CO mass (gms)
udo.pems.coSumDrift='Cumulative_CO_Mass_Drift';    % Cummulative CO drift corr. mass (gms)
udo.pems.co2MassFlow='CO2_MassFlow';                % instantaneous CO2 wet mass flow  (gm/sec)
udo.pems.co2MassFlowDrift='CO2_MassFlow_Drift';     % instantaneous CO2 wet Mass Flow corr. for drift (gm/sec)
udo.pems.co2Sum='Cumulative_CO2_Mass';             % Cummulative CO2 mass (gms)
udo.pems.co2SumDrift='Cumulative_CO2_Mass_Drift';  % Cummulative CO2 drift corr. mass (gms)
udo.pems.hcMassFlow='HC_MassFlow';                  % instantaneous HC wet mass flow (gm/sec)
udo.pems.hcMassFlowDrift='HC_MassFlow_Drift';       % instantaneous HC wet mass flow corr. for drift (gm/sec)
udo.pems.hcSum='Cumulative_HC_Mass';               % Cummulative HC mass (gms)
udo.pems.hcSumDrift='Cumulative_HC_Mass_Drift';    % Cummulative HC drift corr. mass (gms
udo.pems.distSumKm='Cumulative_Distance_Km';       % Cummulative distance in km
udo.pems.distSumMile='Cumulative_Distance_Miles';  % Cummulative Distance in miles
udo.pems.exhaustFlow='VolFlow_Gas_TailPipe';        % Volumetric exhaust gas flow (m3/min)
udo.pems.sumExhFlow='Cumulative_Exhaust_Flow';     % Cummulative exhaust flow (m3)
udo.pems.coolantTC='EngineCoolantTemperature_C';    % Engine coolant temperature (C)
udo.pems.includeEngSpeed='Include_EngSpeed';        % Included points for bin calc.  EngSpeed > 0
udo.pems.includeRegen='Include_Regen';              % Included points for bin calc. DPF not in regen, regenStatus=0
udo.pems.includeTmax='Include_Tmax';                % Included points for bin calc., Tambient < Tmax
udo.pems.includeAmbient5C='Include_Ambient5C';      % Included points for bin calc.; Tambient > 5
udo.pems.includeAltitude='Include_Altitude';        % Boolean of ex/included pts for bins, Altitude>5500 ft
udo.pems.includeTotal='Include_Total';              % Boolean showing All excluded/included (0/1) pts according to 1036.530
udo.pems.tMaxLimit='TMax_ExcludeLimit';             % Tmax for determining bin excluded points in 1036.530(c)(3)(iv)
udo.pems.ambientTLimit='AmbientT_ExcludeLimit';     % Ambient 5C limit of bin excluded points
udo.pems.altitudeLimit='Altitude_ExcludeLimit';     % Altitude limit for bin excluded points (5500 ft)
udo.pems.altitudeFt='Altitude_Ft';                  % Altitude in Ft
udo.pems.pmSum='Cumulative_PM_Mass';                % Cumulative PM mass at tailpipe (corr. for filter wts)
udo.pems.kNOxBrakeSpec='BrakeSpecificHP_kNOx';       % Brake Specific corr. NOx (gm/hp-hr)
udo.pems.coBrakeSpec='BrakeSpecificHP_CO';           % Brake Specific CO (gm/hp-hr)
udo.pems.co2BrakeSpec='BrakeSpecificHP_CO2';           % Brake Specific CO2 (gm/hp-hr)
udo.pems.hcBrakeSpec='BrakeSpecificHP_HC';           % Brake Specific HC (gm/hp-hr)

udo.pems.kNOxBrakeSpecKw='BrakeSpecificKW_kNOx';       % Brake Specific corr. NOx (gm/hp-hr)
udo.pems.coBrakeSpecKw='BrakeSpecificKW_CO';           % Brake Specific CO (gm/hp-hr)
udo.pems.co2BrakeSpecKw='BrakeSpecificKW_CO2';           % Brake Specific CO2 (gm/hp-hr)
udo.pems.hcBrakeSpecKw='BrakeSpecificKW_HC';           % Brake Specific HC (gm/hp-hr)

udo.pems.knoxInstantBhp='InstantBrakeSpecificBhp_NOx';  % instantaneous brake specific NOx (gm/hp-hr)
udo.pems.knoxInstantBkw='InstantBrakeSpecificBkw_NOx';  % instantaneous brake specific NOx (gm/kw-hr)
udo.pems.knoxMovMeanBhp='MovMeanBrkSpecificBhp_NOx';    % 120s Trailing moving mean brake specific NOx (gm/hp-hr)
udo.pems.knoxMovMeanBkw='MovMeanBrkSpecificBkw_NOx';    % 120s Trailing moving mean brake specific NOx (gm/kw-hr)

udo.pems.prTransPsi='Pressure Post CAT';            % Pressure Transducer (psi)


% --------- PEMS Calculations - Scalar
udo.pems.kNOxMassTotal='kNOx_Mass_Total';               % total mass of NOx corr. for humidity (gms)
udo.pems.kNOxMassTotalDrift='kNOx_Mass_Total_Drift';    % total mass of NOx corr. for humidity and Drift (gms)
udo.pems.kNOxGmsPerMile='kNOx_Gms_Per_Mile';            % kNOx (gms/mile)
udo.pems.kNOxMgPerMile='kNOx_Mg_Per_Mile';              % kNOx (mg/mile)  for report
udo.pems.kNOxGmsPerMileFTP='kNOx_Gms_Per_Mile_FTPEquiv';    % kNOx (gms/mile) FTP equivalent
udo.pems.kNOxMgPerMileFTP='kNOx_Mg_Per_Mile_FTPEquiv';      % kNOx (mg/mile) FTP equivalent
udo.pems.kNOxGmsPerMileDrift='kNOx_Gms_Per_Mile_Drift'; % NOx (gms/mile) corr. for drift

udo.pems.coMassTotal='CO_Mass_Total';                   % total mass of CO (gms)
udo.pems.coMassTotalDrift='CO_Mass_Total_Drift';        % total mass of CO corr for Drift (gms)
udo.pems.coGmsPerMile='CO_Gms_Per_Mile';                % CO (gms/mile)
udo.pems.coGmsPerMileFTP='CO_Gms_Per_Mile_FTPEquiv';    % CO (gms/mile) FTP equivalent
udo.pems.coMgPerMileFTP='CO_Mg_Per_Mile_FTPEquiv';      % CO (mg/mile) FTP equivalent
udo.pems.coGmsPerMileDrift='CO_Gms_Per_Mile_Drift';     % CO (gms/mile) corr. for drift

udo.pems.co2MassTotal='CO2_Mass_Total';                 % total mass of CO2 (gms)
udo.pems.co2MassTotalDrift='CO2_Mass_Total_Drift';      % total mass of CO2 corr. for drift (gms)
udo.pems.co2GmsPerMile='CO2_Gms_Per_Mile';              % CO2 (gms/mile)
udo.pems.co2GmsPerMileFTP='CO2_Gms_Per_Mile_FTPEquiv';  % CO2 (gms/mile) FTP equivalent
udo.pems.co2MgPerMileFTP='CO2_Mg_Per_Mile_FTPEquiv';    % CO2 (mg/mile) FTP equivalent
udo.pems.co2GmsPerMileDrift='CO2_Gms_Per_Mile_Drift';   % CO2 (gms/mile) corr. for drift

udo.pems.hcMassTotal='HC_Mass_Total';                   % total mass of HC (gms)
udo.pems.hcMassTotalDrift='HC_Mass_Total_Drift';        % total mass of HC corr. for drift (gms)
udo.pems.hcGmsPerMile='HC_Gms_Per_Mile';                % THC (gms/mile)
udo.pems.hcMgPerMile='HC_Mg_Per_Mile';                  % THC (mg/mile) for report
udo.pems.hcGmsPerMileFTP='HC_Gms_Per_Mile_FTPEquiv';    % THC (gms/mile) FTP equivalent
udo.pems.hcMgPerMileFTP='HC_Mg_Per_Mile_FTPEquiv';      % THC (mg/mile) FTP equivalent
udo.pems.hcGmsPerMileDrift='HC_Gms_Per_Mile_Drift';     % THC (gms/mile) corr. for drift

udo.pems.nmhcMassTotal='NMHC_Mass_Total';               % total mass of NMHC (gms):  NMHC = 0.98 * THC: CFR1065.650(c)(5)
udo.pems.nmhcGmsPerMile='NMHC_Gms_Per_Mile';            % NMHC (gm/mile)
udo.pems.nmhcMgPerMile='NMHC_Mg_Per_Mile';              % NMHC (mg/mile)
udo.pems.nmhcGmsPerMileFTP='NMHC_Gms_Per_Mile_FTPEquiv';    % NMHC (gms/mile) FTP equivalent
udo.pems.nmhcMgPerMileFTP='NMHC_Mg_Per_Mile_FTPEquiv';      % NMHC (mg/mile) FTP equivalent

udo.pems.noxPlusMassTotal='NOxPlusNMHC_Mass_Total';     % kNOx+NMHC Mass Total (gms)
udo.pems.noxPlusGmsPerMile='NOxPlusNMHC_Gms_Per_Mile';  % kNOx+NMHC (gm/mile)
udo.pems.noxPlusMgPerMile='NOxPlusNMHC_Mg_Per_Mile';    % kNOx + NMHC (mg/miles)
udo.pems.noxPlusGmsPerMileFTP='NOxPlusNMHC_Gms_Per_Mile_FTPEquiv';    % kNOx+NMHC (gm/mile) FTP equivalent
udo.pems.noxPlusMgPerMileFTP='NOxPlusNMHC_Mg_Per_Mile_FTPEquiv';      % kNOx + NMHC (mg/miles) FTP equivalent

udo.pems.distanceKm='Distance_Km';                      % total distance in km
udo.pems.distanceMile='Distance_Mile';                  % total distance in miles
udo.pems.totalExhFlow='Total_Exhaust_Flow';             % total exhaust flow (m3)
udo.pems.fuelEconomy='Fuel_Economy';                    % fuel economy in mpg
udo.pems.avgAmbT='Avg_Ambient_Temperature';             % average ambient temperature after initial 300 seconds
udo.pems.avgAmbRH='Avg_Ambient_RelativeHumidity';       % average ambient relative humitidy after initial 300 seconds
udo.pems.workTotalBHP='Total_Work_BHP';                 % total work for HD calc of emissions in gm/hp-hr

udo.pems.idleStartTime='Idle_Time_At_Start';            % Idle time at start= (vehSpd>0 - engSpd>0)  (sec)
udo.pems.coolantStartT='Coolant_T_At_Start';            % Coolant temperature at start (F)
udo.pems.ambientStartT='Ambient_T_At_Start';            % Ambient Air Temperature at Start (F)

%% CAN Data Signals

% CAN data signals.
% There are no CAN data calculations.  Only the time signal is needed to
% calculate the time step when the data is imported
% all other signals are just for report creation

udo.can.time='Time';
udo.can.engSpeed='CAN_Engine_speed_rpm_';  % engine speed from CAN HEMData
udo.can.coolantT='CAN_Engine_water_temperature_degC_';   % Coolant Temperature
udo.can.engTorque='CAN_calculatedEngineTorque';  % torque in N-m for forklift calculations
udo.can.engPower='CAN_calculatedEnginePower';    % power in kW
udo.can.workTotal='CAN_workTotal';              % total work in kW-hr for brake specific emisisons



%% None Label

% 'None' data type still needs to have a time label to calculate the time 
% step and is necessary to syn the data.
% 'None' data type may be used if you only want to sync the data by not do
% any emissions calculations.


udo.none.time='TIME';