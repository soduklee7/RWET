function [binIData, vehData] = dieselBinCalc(setIdx,vehData,udp)

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


% --- Infrequent Regeneration:  1036.530 (c)(3)(iii)
include.regen=vehData(setIdx).data.(udp(setIdx).pems.regenStatus) < 1;
vehData=createLabel(setIdx,include.regen,udp(setIdx).pems.includeRegen,'(-)',1);


% --- Tambient > Tmax: 1036.530 (c)(3)(iv)
ambientTempUnit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.ambientAirT};
ambientTempC=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.ambientAirT),ambientTempUnit,'C');

altitudeUnit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.altitude};
altitudeFt=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.altitude),altitudeUnit,'ft');
vehData=createLabel(setIdx,altitudeFt,udp(setIdx).pems.altitudeFt,'(ft)',1);

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


% --- Exclude single data point surrounded by excluded points 1036.530(c)(3)(vii)
for n=2:length(include.total)-1
    if include.total(n-1)==0 && include.total(n+1)==0 && include.total(n)==1
        include.total(n)=0;
    end
end
vehData=createLabel(setIdx,include.total, udp(setIdx).pems.includeTotal,'(-)',1);



% ----------------------------------------------------------------------------------------
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
idxStart=1;     % index for start of moving window referenced to entire test.
idxEnd=0;       % index for end of moving window reference to entire test.
numInt=0;                       % Number of Intervals (both valid and invalid)
endTest=length(include.total);  % index for the end of test.
testCycleTime=vehData(setIdx).data.(udp(setIdx).pems.time);  % time associated with Include.Total
testCycleCO2massFlow=vehData(setIdx).data.(udp(setIdx).pems.co2MassFlow); % get CO2 mass flow for entire test cycle
includeTotal=include.total;         % logical for included/excluded (0/1) for entire test

% Variables
% include.total % logical for exluded/included data in the entire test calculated above.
% moveWin       % logical for included/excluded (0/1) in moving window
% invertMoveWin % inverse of moveWin in order to count the number of excluded points
% totalWinTime  % total included time in the window (i.e. must be 300 sec)
% endFlag=1     % window idxEnd has reached the end of the test data.
% nCon          % counter for number of continuous excluded points in window
% nConMax       % max number of continuous exlcuded points in a window.
% nUp:          % For loop counter

% calculate the number of data vector indices which equals 300 s
% for example, if the data time step is 1 (1 HZ) then idx300s = 300.
% divide 300 by the data time period and reound to integer
idx300s=round(300/vehData(setIdx).timeStep,0);
endFlag=0;


% ---------------  Determine the Moving Windows (Intervals)
%  this Whicle statement determines the individual moving windows
%  (intervals) having both 300 seconds of both Included and Valid data.  In
%  addition the window must start and end with two consecutive included data
%  points.
while idxEnd < endTest && endFlag==0

    % --- begin a new interval
    % grab the first 300 sec of data. Data may be included or excluded
    idxEnd=idxStart+idx300s;   
    nCon=0;
    nConMax=0;
    nUp=0;

    % This IF-THEN calculates one interval (moving window) and saves the window details in the binIData cell array
    % The IF-THEN starts with a check if first two points of 300 sec window
    % are Not excluded.  The final two points also must not be excluded.  A
    % check of the last two points is done in the nested function
    % getWinTime.
    if sum(includeTotal(idxStart:idxStart+1)) == 2
        [totalWinTime, moveWin] = getWinTime;  % calculated included window time and update moveWin

        while totalWinTime < 300

            idxEnd=idxEnd+1;  % expand window by one index

            if idxEnd == endTest  % break out of while loop if end of data is reached.
                %  [totalWinTime, moveWin] = getWinTime; --- NO
                endFlag=1;
                break  % break out of While loop
            end

            [totalWinTime, moveWin] = getWinTime;
        end

        % if the end of the test data is reached (endFlag=1)
        % then determine if there are more then 600 seconds of continuous
        % excluded data.  If so, the interval is not used in the emisisons
        % calculation, numInt is not advanced and binValid=0.
        if endFlag ~= 1
            
            invertMoveWin=moveWin==0;  % invertMoveWin is a logical vector with 1 now equalling Excluded data

            if sum(invertMoveWin)<600  % if the total excluded time is less then 600 sec then the window must be valid
                binValid=1;
                
            else  % determine if 600 s of excluded data in window is continuous.
                for nUp=2:length(invertMoveWin)
                    if invertMoveWin(nUp-1) && invertMoveWin(nUp)
                        nCon=nCon+1;
                    else
                        if nCon > nConMax
                            nConMax=nCon;
                            nCon=0;
                        end
                    end
                end
                if nConMax >= 600
                    binValid=0;
                end
            end

            % --- end of data is NOT reached (endFlag=0) and interval may
            %     or may not be valid.
            % increase the number of intervals by 1 and save interval definition to binIData
            numInt=numInt+1;
            binIData{1,numInt}=moveWin;
            binIData{2,numInt}=[idxStart,idxEnd];
            binIData{3,numInt}=mean([testCycleTime(idxStart),testCycleTime(idxEnd)]);
            binIData{4,numInt}=totalWinTime;
            binIData{5,numInt}=binValid;

            % initialize a new moving window
            idxStart=idxStart+1;
            idxEnd=idxStart+idx300s;

        end  
        % nothing happens if the end of data is reached and the window does not have 300 sec of included data
        % No data is recorded to binIData.


    else  % there are exclusions in the first two start points.  Advance start by one index.

        idxStart=idxStart+1;
    end


end  % end of While statement





% ---------------  Nested Function getWinTime
% this function calculates the amount of included time in a proposed window
% the start time (idxStart) and endTime (idxEnd) are input to the function.
% Output to the function is the total included time (totalWinTime) in the window and the
% logical of included data in the window (moveWin).
%
% the total included time is calculated pt by pt using a For statement
% since no assumption is made reagrding the time step between data points
% 
% --- Variables
% totalWinTime: Total Included Time for the window defined by idxStart and idxEnd
% timeWindow:   Time vector of the window from idxStat to idxEnd
% moveWin:      Logical vector of included/excluded (1/0) over the defined window
% includeTime:  time vector, over the window, with excluded time set equal
%               to zero
    function [totalWinTime, moveWin] = getWinTime
        totalWinTime=0;
        timeWindow=transpose(testCycleTime(idxStart):testCycleTime(idxEnd));
        moveWin=includeTotal(idxStart:idxEnd);
        includeTime=timeWindow.*moveWin;
        for nt=2:length(includeTime)
            if includeTime(nt) && includeTime(nt-1) ~= 0
                totalWinTime=totalWinTime+(includeTime(nt)-includeTime(nt-1));
            end
        end
    end




% -------------------------------------- Determine the sub-intervals
% determine the sub-intervals using the rising and falling edge of the
% include.total vector.  The include.total vector is stored in the first
% row of the binIData array i.e. binIData{1,nInt}.

nSub=0;     % number of sub intervals
subStart=0; % index of sub interval start relative to total cycle
subEnd=0;   % index of sub interval end relative to total cycle

% variables
% subIdx:   vector of indices, relative to the total cycle, which defines
%           the interval.

% for each interval in the test cycle, calculate the number of
% sub-intervals and the start and end index for each sub-interval.  
for nInt=1:numInt
    nSub=0;
    subIdx=binIData{2,nInt}(1):binIData{2,nInt}(2);  %get vector of indices for the interval (wrt cycle)

    if binIData{5,nInt} == 0        %if the interval is not valid 
        binIData{6,nInt}=nSub;      %number of sub-intervals is zero
        binIData{7,nInt}(1,1)=0;    %index for start of sub-interval is zero
        binIData{7,nInt}(2,1)=0;    %index for end of sub-interval is zero
    else
        nSub=1;                             % intialize number of sub-intervals to 1
        subStart=subIdx(1);                 % start index of sub-interval equals start of interval
        binIData{7,nInt}(1,nSub)=subStart;  % save start index to binIData

        for ndx=2:length(binIData{1,nInt})        % step through the include vector of current interval
            if ndx==length(binIData{1,nInt})      % if you have reached the end of the interval
                if binIData{1,nInt}(ndx)          % is last point in interval is NOT a falling edge
                    subEnd=subIdx(ndx);           % end index of sub-interval equals end index of interval
                else
                    subEnd=subIdx(ndx-1);         % if the last point is a falling edge then the last 
                                                  % point in the sub-interval is the second-to-last point in the interval
                end
                binIData{7,nInt}(2,nSub)=subEnd;  % save end index to binIData

            elseif binIData{1,nInt}(ndx) && ~binIData{1,nInt}(ndx+1)  % falling edge of interval include vector
                subEnd=subIdx(ndx);                                   % is the end of the sub-interval.
                binIData{7,nInt}(2,nSub)=subEnd;                      % assign subEnd to binIData

            elseif ~binIData{1,nInt}(ndx) && binIData{1,nInt}(ndx+1)  % rising edge of the interval include vector
                subStart=subIdx(ndx+1);                               % start of next sub-interval
                nSub=nSub+1;                                          % increase number of sub-intervals by one
                binIData{7,nInt}(1,nSub)=subStart;                    % assign subStart to binIData

            end

        end  %end of for loop determining sub-intervals.

        binIData{6,nInt}=nSub;      % assign the number of sub-intervals to binIData

    end  % end of if-then determining valid/invalid interval

end  % end of for loop operating on number of intervals






% --------------- Calculate the Normalized CO2 emission mass over the test interval - see 1065.530(e)
% 
subStart=0;  % intialize index at the start of the sub-interval
subEnd=0;    % initalize index at the end of the sub-interval

% variables
%  testCycleTime:  Time vector over the entire cycle
%  mCO2Norm:       Normalized CO2 mass over the test interval in Percent

for jInt=1:numInt  % for each interval

    massCO2sub=0;       % CO2 mass over the sub-interval
    massCO2Interval=0;  % CO2 mass over the interval


    for jSub=1:size(binIData{7,jInt},2)  % cycle thru each of the sub-intervals
        if binIData{5,jInt} ~= 0         % if the interval is Valid
            subStart=binIData{7,jInt}(1,jSub);   % get index to start of sub-interval
            subEnd=binIData{7,jInt}(2,jSub);     % get index to end of sub-interval

            subTime=testCycleTime(subStart:subEnd);   % get the time over the sub-interval
            subCO2massFlow=testCycleCO2massFlow(subStart:subEnd); % get the CO2 mass flow (g/s) over the sub-interval
            massCO2sub=trapz(subTime,subCO2massFlow);  % integrate to get the total CO2 mass over the sub-interval

            massCO2Interval=massCO2Interval+massCO2sub; % calculate the CO2 mass over the interval

            timeIntHr=binIData{4,jInt}/3600;  % Calculate the iterval time (300s), in hours (0.083)

            % calculate the normalized CO2 emission mass over the interval
            % in percent
            mCO2Norm=100.*massCO2Interval./(udp(setIdx).bins.eco2fcl*udp(setIdx).bins.pmax*timeIntHr);

            % save the normalized CO2 to the binIData cell array, round to 0.01%
            % according to 1036.530(e)
            binIData{8,jInt}=round(mCO2Norm,2);

            % bin the data and save to binIData cell array
            if mCO2Norm <= 6
                binIData{9,jInt}=1;
            else
                binIData{9,jInt}=2;
            end

        else
            % for an invalid test interval, set the normalized CO2 to zero
            binIData{8,jInt}=0;
            binIData{9,jInt}=0;

        end

    end  % end for loop cycling thru sub-intervals
    
end  % end of for loop cycling thru intervals

clear jInt jSub



% ----------------------- Assemble data statistics on bin data for report
% data is calculate, assembled into a table and eventually added to the
% vehData database

% variables
% scalarBinTable:  Table of scalar bin data statistics

bins=cell2mat(binIData(9,:));                       % vector of interval bins
validIntervals=sum((cell2mat(binIData(5,:))));      % number of valid intervals
invalidIntervals=sum(cell2mat(binIData(5,:))==0);   % number of invalid intervals
numBin1=sum(bins==1);                               % number of bin 1 intervals
numBin2=sum(bins==2);                               % number of bin 2 intervals

% --- assemble scalar interval data into an table
scalarBinTable=table(numInt,validIntervals,invalidIntervals,numBin1,numBin2);
scalarBinTable.Properties.VariableUnits=["(-)","(-)","(-)","(-)","(-)"];
scalarBinTable.Properties.VariableNames=["Number_Intervals","NumValid_Intervals","NumInValid_Intervals",...
    "NumBin1_Intervals","NumBin2_Intervals"];

% --- assemble bin average time (binIData{3,:}) into a vector, transpose to
%     include in table.  bin average time is used in graphing.
timeBinAvg=transpose(cell2mat(binIData(3,:)));




% ------------------------  Calculate the bin 1 NOx Mass
% Function
% binMassCalc is a nested function (below)
% 
% Variables
% noxBin1Mass:  vector of NOx mass at each bin 1 interval
% noxBin1MassTotal:  sum(noxBin1Mass)
%
[noxBin1Mass, noxBin1MassTotal]=binMassCalc(vehData(setIdx).data.(udp(setIdx).pems.kNOxMassFlow), 1);




% ---------------- Calculation of NOx Mass Flow Offcycle Bin 1 according to 1036.530(g)(2)(i)
bin1Logical=cell2mat(binIData(9,:))==1;                      % logical for bin1 (bin1=1, bin2=0)
timeBin1=(bin1Logical.*cell2mat(binIData(4,:)))./3600;  % bin1 logical * time for each interval in hours
timeBin1=transpose(timeBin1);                           % tranpose the vector 
timeBin1Total=sum(timeBin1);                            % total bin1 interval times in hours

% resolve division by zero if test cycle does not contain a bin 1
if timeBin1Total==0   
    noxBin1MassFlow=0;
else
    noxBin1MassFlow=noxBin1MassTotal/timeBin1Total;
end

% update Scalar Bin Table
scalarBinTable.("NOxMassFlow_Bin1")=noxBin1MassFlow;
scalarBinTable.Properties.VariableUnits("NOxMassFlow_Bin1")="(gm/hr)";

% intialize table of bin vector data
binDataTable=table(timeBinAvg,noxBin1Mass);
binDataTable.Properties.VariableNames=["Time_BinAvg","NOx_Mass_Bin1"];
binDataTable.Properties.VariableUnits=["(sec)","(gms)"];

% calculate cummulative nox bin1 mass flow
% the number of intervals is incremented and the sum of nox mass / sum time is
% calculated.  The sum of nox mass over the discrete intervals is
% calculated as opposed to using a cumtrapz which uses a trapezoidal method
for bInt=1:numInt
    if sum(timeBin1(1:bInt)) ~=0
        noxBin1MassFlowCu(bInt,1)=sum(noxBin1Mass(1:bInt))/sum(timeBin1(1:bInt));
    end
end

% add cummulative nox mass flot to the binDataTable
binDataTable.("NOxMassFlow_Bin1_Cummulative")=noxBin1MassFlowCu;
binDataTable.Properties.VariableUnits("NOxMassFlow_Bin1_Cummulative")="(gm/hr)";



% ---------------- Calculation of NOx Offcycle Bin 2 according to 1036.530(g)(2)(i)

% --- get NOx mass emissions for bin 2
[noxBin2Mass, noxBin2MassTotal]=binMassCalc(vehData(setIdx).data.(udp(setIdx).pems.kNOxMassFlow), 2);
% convert to mg
noxBin2MassTotalMg=noxBin2MassTotal*1000;
noxBin2MassMg=noxBin2Mass.*1000;

% --- get CO2 mass emissions for bin 2
[co2Bin2Mass, co2Bin2MassTotal]=binMassCalc(vehData(setIdx).data.(udp(setIdx).pems.co2MassFlow), 2);

noxBin2Brake=udp(setIdx).bins.eco2fcl*noxBin2MassTotal/co2Bin2MassTotal;  
% convert to mg/hp*hr
noxBin2BrakeMg=noxBin2Brake*1000;

scalarBinTable.("NOxBrakeSpecific_Bin2")=noxBin2BrakeMg;
scalarBinTable.Properties.VariableUnits("NOxBrakeSpecific_Bin2")="(mg/hp*hr)";

% calculate NOx mass for each bin 2 interval
binDataTable.("NOx_Mass_Bin2")=noxBin2MassMg;
binDataTable.Properties.VariableUnits("NOx_Mass_Bin2")="(mg)";


% --- calculate the cummulative NOx off-cycle emissions for bin 2
noxBin2BrakeCu = brakeEmCu(noxBin2Mass, co2Bin2Mass);
% convert to mg/hp*hr
noxBin2BrakeCuMg=noxBin2BrakeCu.*1000;

binDataTable.("NOx_BrakeSpec_Bin2_Cummulative")=noxBin2BrakeCuMg;
binDataTable.Properties.VariableUnits("NOx_BrakeSpec_Bin2_Cummulative")="(mg/hp*hr)";


% ---------------- Calculation of CO Offcycle Bin 2 

% --- get CO mass emissions for bin 2
[coBin2Mass, coBin2MassTotal]=binMassCalc(vehData(setIdx).data.(udp(setIdx).pems.coMassFlow), 2);

% --- calculate CO offcycle bin 2 emissions, add to table
coBin2Brake=udp(setIdx).bins.eco2fcl*coBin2MassTotal/co2Bin2MassTotal;

scalarBinTable.("coBrakeSpecific_Bin2")=coBin2Brake;
scalarBinTable.Properties.VariableUnits("coBrakeSpecific_Bin2")="(gm/hp*hr)";

% calculate CO mass for each bin 2 interval
binDataTable.("CO_Mass_Bin2")=coBin2Mass;
binDataTable.Properties.VariableUnits("CO_Mass_Bin2")="(gm)";

% cummulative brake CO over the test cycle
coBin2BrakeCu = brakeEmCu(coBin2Mass, co2Bin2Mass);

binDataTable.("CO_BrakeSpec_Bin2_Cummulative")=coBin2BrakeCu;
binDataTable.Properties.VariableUnits("CO_BrakeSpec_Bin2_Cummulative")="(gm/hp*hr)";


% ---------------- Calculation of HC Offcycle Bin 2 

% --- get HC mass emissions for bin 2
[hcBin2Mass, hcBin2MassTotal]=binMassCalc(vehData(setIdx).data.(udp(setIdx).pems.hcMassFlow), 2);
% convert to mg
hcBin2MassMg=hcBin2Mass.*1000;
hcBin2MassTotalMg=hcBin2MassTotal*1000;

% --- calculate HC offcycle bin 2 emissions, add to table
hcBin2Brake=udp(setIdx).bins.eco2fcl*hcBin2MassTotal/co2Bin2MassTotal;
% convert to mg
hcBin2BrakeMg=hcBin2Brake*1000;

scalarBinTable.("hcBrakeSpecific_Bin2")=hcBin2BrakeMg;
scalarBinTable.Properties.VariableUnits("hcBrakeSpecific_Bin2")="(mg/hp*hr)";

% calculate HC mass for each bin 2 interval
binDataTable.("HC_Mass_Bin2")=hcBin2MassMg;
binDataTable.Properties.VariableUnits("HC_Mass_Bin2")="(mg)";

% cummulative brake HC over the test cycle
hcBin2BrakeCu = brakeEmCu(hcBin2Mass, co2Bin2Mass);
hcBin2BrakeCuMg=1000.*hcBin2BrakeCu;
binDataTable.("HC_BrakeSpec_Bin2_Cummulative")=hcBin2BrakeCuMg;
binDataTable.Properties.VariableUnits("HC_BrakeSpec_Bin2_Cummulative")="(mg/hp*hr)";



% save scalar interval table data to database vehData
vehData(setIdx).scalarBinData=scalarBinTable;
vehData(setIdx).binData=binDataTable;


% ------------------ Nested Function binEmissionCalc
% ------------------ Calculation of bin emissions mass flow and bin emissions mass
    function [binMassInterval, binMassTotal] = binMassCalc(massFlow, binNumber)

        % for each interval in the test cycle
        subStart=0;
        subEnd=0;
        jInt=0;
        jSub=0;

        for jInt=1:numInt

            massSub=0;       % emission mass over the sub-interval
            massInterval=0;  % emisison mass over the interval

            if binIData{9,jInt} == binNumber
                for jSub=1:size(binIData{7,jInt},2)  % cycle thru each of the sub-intervals
                    if binIData{5,jInt} ~= 0         % if the interval is Valid
                        subStart=binIData{7,jInt}(1,jSub);   % get index to start of sub-interval
                        subEnd=binIData{7,jInt}(2,jSub);     % get index to end of sub-interval

                        subTime=testCycleTime(subStart:subEnd);   % get the time over the sub-interval
                        subMassFlow=massFlow(subStart:subEnd); % get the em mass flow (g/s) over the sub-interval
                        massSub=trapz(subTime,subMassFlow);  % integrate to get the total em mass over the sub-interval

                        massInterval=massInterval+massSub; % calculate the em mass over the interval

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