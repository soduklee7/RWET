function vehData = pemsDataCalc(setIdx,vehData)

% bring in user options
udp=evalin('base','udp');



%-------------------------------------------------- PEMS data calculations
%
%
% -------------------------------------------------------------- Time (sec)
[xTime,xTimeCell]=getData(setIdx,udp(setIdx).pems.time);


% ------------ Set vehicle speed source to CAN or GPS
lower(udp(setIdx).pems.speedSource);
switch udp(setIdx).pems.speedSource
    case 'can'
        udp(setIdx).pems.speed=udp(setIdx).pems.speedCAN;
    case 'gps'
        udp(setIdx).pems.speed=udp(setIdx).pems.speedGPS;
end
% assignin the new udp label (with udp.pems.speed) into base workspace
assignin('base','udp',udp)

% ---------------------------------------------------  Vehicle Speed - KPH
[vehspd,vehspdCell]=getData(setIdx,udp(setIdx).pems.speed);
vehspdKph=unitConvert(vehspd,vehspdCell{5},'km/hr');
vehData=createLabel(setIdx,vehspdKph,udp(setIdx).pems.kph,'(km/hr)',1);

% ----------------------------------------------------  Vehicle Speed - MPH
vehspdMph=unitConvert(vehspd,vehspdCell{5},'mph');
vehData=createLabel(setIdx,vehspdMph,udp(setIdx).pems.mph,'(mph)',1);

if sum(isnan(vehspdKph))
    warndlg('Vehicle Speed Contains Blank or NaN Values.  Blanks set to Zero.')

    idxSpeedNaN=find(isnan(vehspdKph));
    vehspdKph(idxSpeedNaN)=0;
end


% ----------------------------------------------- Cummulative Distance (km)
% --- vehicle speed km/sec
vehspdKps=vehspdKph./3600;


% --- distance
distCumulativeKm = cumtrapz(xTime,vehspdKps);
vehData=createLabel(setIdx,distCumulativeKm,udp(setIdx).pems.distSumKm,'(km)',1);

% -------------------------------------------- Cummulative Distance (miles)
distCumulativeMi = unitConvert(distCumulativeKm,'km','mile');
vehData=createLabel(setIdx,distCumulativeMi,udp(setIdx).pems.distSumMile,'(mile)',1);


% ------------------  Distances and indices related to FTP normalized emissions
% find the indices for a cold transient and stabilized phases of an FTP75.
distColdTrans=3.5909;
distStabil=3.8594;
idxColdTransient=find(distCumulativeMi < distColdTrans);
idxStabilized=find(distCumulativeMi >= distColdTrans);

distColdTransientKm=trapz(xTime(idxColdTransient),vehspdKps(idxColdTransient));
distColdTransientMi=unitConvert(distColdTransientKm,'km','mile');

distStabilizedKm=trapz(xTime(idxStabilized),vehspdKps(idxStabilized));
distStabilizedMi=unitConvert(distStabilizedKm,'km','mile');


% ----------------------------------------------------------- Distance (km)
distKm=trapz(xTime,vehspdKps);
vehData(setIdx).scalarData.(udp(setIdx).pems.distanceKm)=distKm;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.distanceKm)={'km'};
assignin('base','vehData',vehData)

% -------------------------------------------------------- Distance (miles)
distMi=unitConvert(distKm,'km','mile');
vehData(setIdx).scalarData.(udp(setIdx).pems.distanceMile)=distMi;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.distanceMile)={'mile'};
assignin('base','vehData',vehData)

% -------------------------------------------  Engine Speed (rpm)
[engSpd, engSpdC]=getData(setIdx,udp(setIdx).pems.engineSpeed);


if strcmp(udp(setIdx).pems.vehWtClass,'LD')
    % ------------------------------------------------ Idle Time at Start
    idleStartIndex=find(engSpd>0);
    if isempty(idleStartIndex)
        idleStartTime=NaN;
        warndlg('Engine Speed is Zero');
    else
        if idleStartIndex(1)==1
            idleStartTime=xTime(idleStartIndex(1));
        else
            idleStartTime=xTime(idleStartIndex(1)-1);
        end
    end


    [vehSpeed, vehSpeedC]=getData(setIdx,udp(setIdx).pems.speed);
    driveStartIndex=find(vehSpeed>0);
    if isempty(driveStartIndex)
        driveStartTime=NaN;
        warndlg('Vehicle Speed is Zero');
    else
        if driveStartIndex(1)==1
            driveStartTime=xTime(driveStartIndex(1));
        else
            driveStartTime=xTime(driveStartIndex(1)-1);
        end
    end

    if isnan(idleStartTime) | isnan(driveStartTime)
        idleTime=NaN;
    else
        idleTime=driveStartTime-idleStartTime;
    end

    vehData=createLabel(setIdx, idleTime,udp(setIdx).pems.idleStartTime,xTimeCell{5},1);

   


    % --------------------------------------- Coolant Temperature at Start
    [coolantT,coolantTC]=getData(setIdx,udp(setIdx).pems.coolantT);
    coolantT=unitConvert(coolantT,coolantTC{5},'F');
    coolantTStart1=coolantT(1);
    coolantTStart5=coolantT(5);
    if (coolantTStart5-coolantTStart1) < 1
        coolantTStart=coolantTStart1;
    else
        coolantTStart=coolantTStart5;
    end
    vehData=createLabel(setIdx, coolantTStart,udp(setIdx).pems.coolantStartT,'F',1);

    % --------------------------------------- Ambient Temperature at Start
    [ambientT,ambientTC]=getData(setIdx,udp(setIdx).pems.ambientAirT);
    ambientT=unitConvert(ambientT,ambientTC{5},'F');
    ambientTStart1=ambientT(1);
    ambientTStart5=ambientT(5);
    if (ambientTStart5-ambientTStart1) < 1
        ambientTStart=ambientTStart1;
    else
        ambientTStart=ambientTStart5;
    end
    vehData=createLabel(setIdx, ambientTStart,udp(setIdx).pems.ambientStartT,'F',1);
end


% bookmark

% -------------------------- Total Work (hp-hr) Caclulated Using BHP
% if strcmp(udp(setIdx).pems.vehWtClass,'HD')
%     [bhp, bhpC]=getData(setIdx,udp(setIdx).pems.engPowerHp);  % work instant.
%     workTotal=trapz(xTime,bhp)/3600;                  % total work
%     vehData=createLabel(setIdx,workTotal,udp(setIdx).pems.workTotalBHP,'(bhp-hr)',1);
% end

% % ------------- Total Work (hp-hr) Calculated Using Torque (N-m)
% reference CFR equation 1065.650-11
% written for GECB forklift testing sept 2025
if strcmp(udp(setIdx).pems.vehWtClass,'HD')
    [engSpdCAN, engSpdCANC] = getData(setIdx,udp(setIdx).can.engSpeed);  % get engine speed from CAN
    [torqNM, torqNMC]=getData(setIdx,udp(setIdx).can.engTorque);  % torque in N-m
    powerKW=2.*pi.*torqNM.*engSpdCAN./60000;  % power in kW
    powerHP=1.341.*powerKW;
    workTotal=trapz(xTime,powerHP)/3600; % bhp-hr
    workTotalKwHr=trapz(xTime,powerKW)/3600;  % kW-hr
    vehData=createLabel(setIdx,workTotal,udp(setIdx).can.workTotal,'(kW-hr)',1);
    vehData=createLabel(setIdx,powerKW,udp(setIdx).pems.enginePowerKw,'(kW)',1);
    vehData=createLabel(setIdx,powerHP,udp(setIdx).pems.enginePowerHp,'(HP)',1);
end


% -------------------------------------------------------------- Vmix,STD
% Volumetric flow is taken directly from the PEMS output data
vSTD=vehData(setIdx).data.(udp(setIdx).pems.scfm);  % ft3/min

% -------------------------- Average Air Temperature from Weather Station
[ambAirT,ambAirTC]=getData(setIdx,udp(setIdx).pems.ambientAirT);
ambAirT=unitConvert(ambAirT,ambAirTC{5},'F');
t300Idx=round(300/vehData(setIdx).timeStep,0);  % start calc after 300 seconds, round to integer
avgAmbAirT=mean(ambAirT(t300Idx:end));
vehData=createLabel(setIdx,avgAmbAirT,udp(setIdx).pems.avgAmbT,'(F)',1);

% -------------------------- Average Relative Humidity from Weather Station
[ambRH,ambRHC]=getData(setIdx,udp(setIdx).pems.rHumidity);
avgRH=mean(ambRH(t300Idx:end));
vehData=createLabel(setIdx,avgRH,udp(setIdx).pems.avgAmbRH,ambRHC{5},1);


% ------------------------- Pressure Transducer Volts to PSIG

if udp(setIdx).pems.enablePrTransducer
    [prTrV,prTrVC]=getData(setIdx,udp(setIdx).pems.prTransducer);   % get pressure in volts

    prTrPsi=udp(setIdx).pems.prTransSlope.*prTrV + udp(setIdx).pems.prTransInter;
    vehData=createLabel(setIdx,prTrPsi,udp(setIdx).pems.prTransPsi,'psi',1);

end




if udp(setIdx).pems.pm2Active
    %  ------------------------- Tailpipe PM Calculation
    vSTDmcps=vSTD.*0.3048^3./60;   % SFCM converted to m3/s
    vSTDTotalm3=trapz(xTime,vSTDmcps);  % total vol. flow in m3

    filterFlow=vehData(setIdx).data.(udp(setIdx).pems.pmFilterFlow);  %filter flow in SLPM
    filterFmcps=filterFlow./1000./60;  % filter flow in m3/s
    filterFlowTotalm3=trapz(xTime,filterFmcps);

    makeupFlow=vehData(setIdx).data.(udp(setIdx).pems.pmMakeupFlow);  %Make-Up flow in SLPM
    makeupFlowmcps=makeupFlow./1000./60;  %Make-Up Flow in m3/s
    makeupFlowTotalm3=trapz(xTime,makeupFlowmcps);

    

    % filterFlowlps=filterFlow./60;
    % filterFlowTotall=trapz(xTime,filterFlowlps);

    pmTotal=0.012*vSTDTotalm3/filterFlowTotalm3;
end


% ================================================================  kNOx

% NOx (g/s) = [NOx]k,wet * Vstd * densityNOx,std
% Reference:  1066.605(e) and the Sensors PP User Manual
% Density of NOx taken from CFR 1066.1005 table 6 in g/ft3
% NOx is already calculated in the Sensors software.  However, it is
% calculated here, again, in order to capture any time alignment changes to
% the NOx concentration.
%

% ------------- kNOx Concentration
% convert NOx from (e.g. ppm) to a concentration 
kNOxConc=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetkNOx), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetkNOx},'conc');  % conc

% set density of NOx according to CFR 1066.1005 Table 6
densityNOxSTD=54.156;

% ----------- kNOx mass flow (gm/s)
kNOxMassFlow=kNOxConc.*vSTD.*densityNOxSTD./60;
vehData=createLabel(setIdx, kNOxMassFlow, udp(setIdx).pems.kNOxMassFlow, 'gm/s', 1);

% ----------- Cummulative kNOx (gms)
kNOxSum=cumtrapz(xTime,kNOxMassFlow);
vehData=createLabel(setIdx,kNOxSum,udp(setIdx).pems.kNOxSum,'(gm)',1);

% ----------- kNOx Mass Total  (gms)
kNOxMassTot=trapz(xTime,kNOxMassFlow);
kNOxMassTotSum=sum(kNOxMassFlow);  % this assumes a timeStep=1
vehData(setIdx).scalarData.(udp(setIdx).pems.kNOxMassTotal)=kNOxMassTot;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.kNOxMassTotal)={'gm'};
assignin('base','vehData',vehData)

% ----------- kNOx (gm/mile)
kNOxGmsPerMile=kNOxMassTot./distMi;
vehData(setIdx).scalarData.(udp(setIdx).pems.kNOxGmsPerMile)=kNOxGmsPerMile;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.kNOxGmsPerMile)={'gm/mile'};
assignin('base','vehData',vehData)

% ---------- kNOx (mg/mile)
if strcmp(udp(setIdx).pems.vehWtClass,'LD')
    kNOxMgPerMile=kNOxGmsPerMile.*1000;
    vehData=createLabel(setIdx, kNOxMgPerMile, udp(setIdx).pems.kNOxMgPerMile, '(mg/mile)', 1);
end

% ---------- kNOx FTP equivalent emissions
[kNOxGmsPerMileFTPEq, kNOxMgPerMileFTPEq] = nestFtpEquiv(kNOxMassFlow);
vehData=createLabel(setIdx, kNOxGmsPerMileFTPEq, udp(setIdx).pems.kNOxGmsPerMileFTP, 'gm/mile', 1);
vehData=createLabel(setIdx, kNOxMgPerMileFTPEq, udp(setIdx).pems.kNOxMgPerMileFTP, 'mg/mile', 1);



if strcmp(udp(setIdx).pems.vehWtClass,'HD')

    % ----------- kNOx Brake Specific (gm/hp-hr)
    kNOxBhp=kNOxMassTot/workTotal;
    kNOxKw=kNOxMassTot/workTotalKwHr;
    vehData=createLabel(setIdx,kNOxBhp,udp(setIdx).pems.kNOxBrakeSpec,'(gm/hp-hr)',1);
    vehData=createLabel(setIdx,kNOxKw,udp(setIdx).pems.kNOxBrakeSpecKw,'(gm/kw-hr)',1);


    % instantaneous brake specific NOx
    if vehData(setIdx).timeStep==1
        [bhp, bhpC]=getData(setIdx,udp(setIdx).pems.enginePowerHp);
        [kw, kwC]=getData(setIdx,udp(setIdx).pems.enginePowerKw);
        kNOxInstBhp=3600.*(kNOxMassFlow./bhp);
        kNOxInstBkw=3600.*(kNOxMassFlow./kw);

        win120s=120/vehData(setIdx).timeStep;
        kNOxMovMeanBhp=movmean(kNOxInstBhp,[199 0]);
        kNOxMovMeanBkw=movmean(kNOxInstBkw,[199 0]);

        vehData=createLabel(setIdx, kNOxInstBhp, udp(setIdx).pems.knoxInstantBhp,'(gm/hp-hr)',1);
        vehData=createLabel(setIdx, kNOxInstBkw, udp(setIdx).pems.knoxInstantBkw,'(gm/kw-hr)',1);
        vehData=createLabel(setIdx, kNOxMovMeanBhp, udp(setIdx).pems.knoxMovMeanBhp,'(gm/hp-hr)',1);
        vehData=createLabel(setIdx, kNOxMovMeanBkw, udp(setIdx).pems.knoxMovMeanBkw,'(gm/kw-hr)',1);

    end

end




% ============================================================  kNOx Drift
% ------------- kNOxDrift Concentration
% convert NOx from inputed units (e.g. ppm) to a concentration
kNOxConcDrift=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetkNOxDrift), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetkNOxDrift},'conc');  % conc

% ------------ kNOxDrift Mass Flow (g/s)
kNOxMassFlowDrift=kNOxConcDrift.*vSTD.*densityNOxSTD./60;
vehData=createLabel(setIdx, kNOxMassFlowDrift, udp(setIdx).pems.kNOxMassFlowDrift, 'gm/s', 1);

% ----------- Cummulative kNOxDrift (gms)
kNOxSumDrift=cumtrapz(xTime,kNOxMassFlowDrift);
vehData=createLabel(setIdx,kNOxSumDrift,udp(setIdx).pems.kNOxSumDrift,'(gm)',1);

% ----------- kNOxDrift Mass Total  (gms)
kNOxMassTotalDrift=trapz(xTime,kNOxMassFlowDrift);
vehData(setIdx).scalarData.(udp(setIdx).pems.kNOxMassTotalDrift)=kNOxMassTotalDrift;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.kNOxMassTotalDrift)={'gm'};
assignin('base','vehData',vehData)

% ----------- kNOxDrift (gm/mile)
kNOxGmsPerMileDrift=kNOxMassTotalDrift./distMi;
vehData(setIdx).scalarData.(udp(setIdx).pems.kNOxGmsPerMileDrift)=kNOxGmsPerMileDrift;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.kNOxGmsPerMileDrift)={'gm/mile'};
assignin('base','vehData',vehData)



% =================================================================   CO
% ---------- CO concentration 
coConc=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetCO), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetCO},'conc');  % conc

% set density of CO at STD according to CFR 1066.1005 Table 6
densityCOSTD=32.9725;  % g/ft3

% ----------- CO mass flow (gm/s)
coMassFlow=coConc.*vSTD.*densityCOSTD./60;
vehData=createLabel(setIdx, coMassFlow, udp(setIdx).pems.coMassFlow, 'gm/s', 1);

% ----------- Cummulative CO (gms)
coSum=cumtrapz(xTime,coMassFlow);
vehData=createLabel(setIdx,coSum,udp(setIdx).pems.coSum,'(gm)',1);

% ----------- CO Mass Total  (gms)
coMassTot=trapz(xTime,coMassFlow);
vehData(setIdx).scalarData.(udp(setIdx).pems.coMassTotal)=coMassTot;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.coMassTotal)={'gm'};
assignin('base','vehData',vehData)

% ----------- CO (gm/mile)
coGmsPerMile=coMassTot./distMi;
vehData(setIdx).scalarData.(udp(setIdx).pems.coGmsPerMile)=coGmsPerMile;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.coGmsPerMile)={'(gm/mile)'};
assignin('base','vehData',vehData)

% ---------- CO FTP equivalent emissions
[coGmsPerMileFTPEq, coMgPerMileFTPEq] = nestFtpEquiv(coMassFlow);
vehData=createLabel(setIdx, coGmsPerMileFTPEq, udp(setIdx).pems.coGmsPerMileFTP, 'gm/mile', 1);
vehData=createLabel(setIdx, coMgPerMileFTPEq, udp(setIdx).pems.coMgPerMileFTP, 'mg/mile', 1);

% ----------- CO Brake Specific (gm/hp-hr)
if strcmp(udp(setIdx).pems.vehWtClass,'HD')
    coBhp=coMassTot/workTotal;
    vehData=createLabel(setIdx,coBhp,udp(setIdx).pems.coBrakeSpec,'(gm/hp-hr)',1);
end


% ============================================================  CO Drift
% ------------- CO Drift Concentration
coConcDrift=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetCODrift), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetCODrift},'conc');  % conc

% ------------ CO Drift Mass Flow (g/s)
coMassFlowDrift=coConcDrift.*vSTD.*densityCOSTD./60;
vehData=createLabel(setIdx, coMassFlowDrift, udp(setIdx).pems.coMassFlowDrift, 'gm/s', 1);

% ----------- Cummulative CO Drift (gms)
coSumDrift=cumtrapz(xTime,coMassFlowDrift);
vehData=createLabel(setIdx,coSumDrift,udp(setIdx).pems.coSumDrift,'(gm)',1);

% ----------- CO Drift Mass Total  (gms)
coMassTotalDrift=trapz(xTime,coMassFlowDrift);
vehData(setIdx).scalarData.(udp(setIdx).pems.coMassTotalDrift)=coMassTotalDrift;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.coMassTotalDrift)={'gm'};
assignin('base','vehData',vehData)

% ----------- CO Drift (gm/mile)
coGmsPerMileDrift=coMassTotalDrift./distMi;
vehData(setIdx).scalarData.(udp(setIdx).pems.coGmsPerMileDrift)=coGmsPerMileDrift;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.coGmsPerMileDrift)={'gm/mile'};
assignin('base','vehData',vehData)


% =================================================================   CO2
% ---------- CO2 concentration 
co2Conc=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetCO2), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetCO2},'conc');  % conc

% set density of CO2 at STD according to CFR 1066.1005 Table 6
densityCO2STD=51.8064;  % g/ft3

% ----------- CO2 mass flow (gm/s)
co2MassFlow=co2Conc.*vSTD.*densityCO2STD./60;
vehData=createLabel(setIdx, co2MassFlow, udp(setIdx).pems.co2MassFlow, 'gm/s', 1);

% ----------- Cummulative CO2 (gms)
co2Sum=cumtrapz(xTime,co2MassFlow);
vehData=createLabel(setIdx,co2Sum,udp(setIdx).pems.co2Sum,'(gm)',1);

% ----------- CO2 Mass Total  (gms) (scalar)
co2MassTot=trapz(xTime,co2MassFlow);
vehData=createLabel(setIdx,co2MassTot,udp(setIdx).pems.co2MassTotal,'(gm)',1);

% ----------- CO2 (gm/mile) (scalar)
co2GmsPerMile=co2MassTot./distMi;
vehData=createLabel(setIdx,co2GmsPerMile,udp(setIdx).pems.co2GmsPerMile,'(gm/mile)',1);

% ----------- CO2 Brake Specific (gm/hp-hr)
if strcmp(udp(setIdx).pems.vehWtClass,'HD')
    co2Bhp=co2MassTot/workTotal;
    vehData=createLabel(setIdx,co2Bhp,udp(setIdx).pems.co2BrakeSpec,'(gm/hp-hr)',1);
end

% ---------- CO2 FTP equivalent emissions
[co2GmsPerMileFTPEq, co2MgPerMileFTPEq] = nestFtpEquiv(co2MassFlow);
vehData=createLabel(setIdx, co2GmsPerMileFTPEq, udp(setIdx).pems.co2GmsPerMileFTP, 'gm/mile', 1);
vehData=createLabel(setIdx, co2MgPerMileFTPEq, udp(setIdx).pems.co2MgPerMileFTP, 'mg/mile', 1);




% ============================================================  CO2 Drift
% ------------- CO2 Drift Concentration
co2ConcDrift=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetCO2Drift), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetCO2Drift},'conc');  % conc


% ------------ CO2 Drift Mass Flow (g/s)
co2MassFlowDrift=co2ConcDrift.*vSTD.*densityCO2STD./60;
vehData=createLabel(setIdx, co2MassFlowDrift, udp(setIdx).pems.co2MassFlowDrift, 'gm/s', 1);

% ----------- Cummulative CO2 Drift (gms)
co2SumDrift=cumtrapz(xTime,co2MassFlowDrift);
vehData=createLabel(setIdx,co2SumDrift,udp(setIdx).pems.co2SumDrift,'(gm)',1);

% ----------- CO2 Drift Mass Total  (gms) (scalar)
co2MassTotalDrift=trapz(xTime,co2MassFlowDrift);
vehData=createLabel(setIdx,co2MassTotalDrift,udp(setIdx).pems.co2MassTotalDrift,'(gm)',1);

% ----------- CO2 Drift (gm/mile) (scalar)
co2GmsPerMileDrift=co2MassTotalDrift./distMi;
vehData=createLabel(setIdx,co2GmsPerMileDrift,udp(setIdx).pems.co2GmsPerMileDrift,'(gm/mile)',1);


% =================================================================   HC
% ---------- HC concentration 
hcConc=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetHC), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetHC},'conc');  % conc

% set density of HC at STD according to CFR 1066.1005 Table 6
densityHCSTD=16.3336;  % g/ft3

% ----------- HC mass flow (gm/s)
hcMassFlow=hcConc.*vSTD.*densityHCSTD./60;
vehData=createLabel(setIdx, hcMassFlow, udp(setIdx).pems.hcMassFlow, 'gm/s', 1);

% ----------- Cummulative HC (gms)
hcSum=cumtrapz(xTime,hcMassFlow);
vehData=createLabel(setIdx,hcSum,udp(setIdx).pems.hcSum,'(gm)',1);

% ----------- HC Mass Total  (gms) (scalar)
hcMassTot=trapz(xTime,hcMassFlow);
vehData=createLabel(setIdx,hcMassTot,udp(setIdx).pems.hcMassTotal,'(gm)',1);

% ----------- HC (gm/mile) (scalar)
hcGmsPerMile=hcMassTot./distMi;
vehData=createLabel(setIdx,hcGmsPerMile,udp(setIdx).pems.hcGmsPerMile,'(gm/mile)',1);

if strcmp(udp(setIdx).pems.vehWtClass,'LD')
    % ----------- HC (mg/mile) (scalar)
    hcMgPerMile=hcGmsPerMile.*1000;
    vehData=createLabel(setIdx,hcMgPerMile,udp(setIdx).pems.hcMgPerMile,'(mg/mile)',1);
end

% ---------- HC FTP equivalent emissions
[hcGmsPerMileFTPEq, hcMgPerMileFTPEq] = nestFtpEquiv(hcMassFlow);
vehData=createLabel(setIdx, hcGmsPerMileFTPEq, udp(setIdx).pems.hcGmsPerMileFTP, 'gm/mile', 1);
vehData=createLabel(setIdx, hcMgPerMileFTPEq, udp(setIdx).pems.hcMgPerMileFTP, 'mg/mile', 1);


% ----------- HC Brake Specific (gm/hp-hr)
if strcmp(udp(setIdx).pems.vehWtClass,'HD')
    hcBhp=hcMassTot/workTotal;
    vehData=createLabel(setIdx,hcBhp,udp(setIdx).pems.hcBrakeSpec,'(gm/hp-hr)',1);
end

if strcmp(udp(setIdx).pems.vehWtClass,'LD')
    % ---------- NMHC (mg/mile)  - see 1065.650
    nmhcMgPerMile=hcMgPerMile.*0.98;
    vehData=createLabel(setIdx,nmhcMgPerMile,udp(setIdx).pems.nmhcMgPerMile,'(mg/mile)',1);

    nmhcMgPerMileFTPEq=hcMgPerMileFTPEq.*0.98;
    vehData=createLabel(setIdx,nmhcMgPerMileFTPEq,udp(setIdx).pems.nmhcMgPerMileFTP,'(mg/mile)',1);

    % ---------- NOx + NMHC
    noxPlus=kNOxMgPerMile+nmhcMgPerMile;
    vehData=createLabel(setIdx, noxPlus,udp(setIdx).pems.noxPlusMgPerMile,'(mg/mile)',1);

    noxPlusMgPerMileFTPEq=kNOxMgPerMileFTPEq+nmhcMgPerMileFTPEq;
    vehData=createLabel(setIdx, noxPlusMgPerMileFTPEq,udp(setIdx).pems.noxPlusMgPerMileFTP,'(mg/mile)',1);


end

% ============================================================  HC Drift
% ------------- HC Drift Concentration
hcConcDrift=unitConvert(vehData(setIdx).data.(udp(setIdx).pems.wetHCDrift), ...
    vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.wetHCDrift},'conc');  % conc

% ------------ HC Drift Mass Flow (g/s)
hcMassFlowDrift=hcConcDrift.*vSTD.*densityHCSTD./60;
vehData=createLabel(setIdx, hcMassFlowDrift, udp(setIdx).pems.hcMassFlowDrift, 'gm/s', 1);

% ----------- Cummulative HC Drift (gms)
hcSumDrift=cumtrapz(xTime,hcMassFlowDrift);
vehData=createLabel(setIdx,hcSumDrift,udp(setIdx).pems.hcSumDrift,'(gm)',1);

% ----------- HC Drift Mass Total  (gms) (scalar)
hcMassTotalDrift=trapz(xTime,hcMassFlowDrift);
vehData=createLabel(setIdx,hcMassTotalDrift,udp(setIdx).pems.hcMassTotalDrift,'(gm)',1);

% ----------- HC Drift (gm/mile) (scalar)
hcGmsPerMileDrift=hcMassTotalDrift./distMi;
vehData=createLabel(setIdx,hcGmsPerMileDrift,udp(setIdx).pems.hcGmsPerMileDrift,'(gm/mile)',1);


% =================================================================   PM
if udp(setIdx).pems.pm2Active
    % ---------- PM Mass Flow (ug/s)
    pmMassFlow=vehData(setIdx).data.(udp(setIdx).pems.pmMassTailpipe);

    % ----------- Cummulative PM  (ug)
    pmSum=cumtrapz(xTime,pmMassFlow);
    vehData=createLabel(setIdx,pmSum,udp(setIdx).pems.pmSum,'(ug)',1);
end


% ======= Exhaust Flow
% ------------------------------------------- Exhaust Vol Flow STP (m3/min)
scfm=vehData(setIdx).data.(udp(setIdx).pems.scfm);
exhFlow=scfm.*0.0283168;  % conversion from ft3/min to m3/min
vehData=createLabel(setIdx,exhFlow,udp(setIdx).pems.exhaustFlow,'(m3/min)',1);

% ------------------------------------------ Cummulative Exhaust Flow (m3)
% --- exhaust flow in m3/sec
flowPerSec=exhFlow./60;

sumFlow = cumtrapz(xTime,flowPerSec);
vehData=createLabel(setIdx,sumFlow,udp(setIdx).pems.sumExhFlow,'(m3)',1);

% ------------------------------------------------ Total Exhaust Flow (m3)
totalFlow=trapz(xTime,flowPerSec);
vehData(setIdx).scalarData.(udp(setIdx).pems.totalExhFlow)=totalFlow;
vehData(setIdx).scalarData.Properties.VariableUnits(udp(setIdx).pems.totalExhFlow)={'m3'};
assignin('base','vehData',vehData)


% ====== Fuel Economy
% ---- fuel economy calculation Reference CFR 600.113-12 (h)(1)
cwf=udp(setIdx).fuel.cwf;
sg=udp(setIdx).fuel.sg;
nhv=udp(setIdx).fuel.nhv;

% FE Calculation using CO2 Only
numMPGCO2=5174e4*cwf*sg;              % FE calculation numerator
denMPGCO2= (0.273*co2GmsPerMile)*((0.6*sg*nhv)+5471);  % FE calculation denominator
feCO2=numMPGCO2/denMPGCO2;         % fuel economy in mpg
vehData=createLabelScalar(setIdx, feCO2,'Fuel_Economy_C02','(mpg)', 1);


% FE calculation numerator
numMPG=5174e4*cwf*sg;
% FE calculation denominator
denMPG= (cwf.*hcGmsPerMile + 0.429.*coGmsPerMile + 0.273*co2GmsPerMile)*((0.6*sg*nhv)+5471); 
% Fuel Economy
fuelEconomy=numMPG/denMPG;         % fuel economy in mpg
vehData=createLabelScalar(setIdx,fuelEconomy,udp(setIdx).pems.fuelEconomy,'(mpg)', 1);





% ---------------  Nested Function
% Nested function to calculate the FTP equivalent emissions in gm/mile for
% an A (or A3) cycle.
    function [gmsPerMile, mgPerMile] = nestFtpEquiv(emMassFlow)

        % Calculate an equivalent FTP75 emission
        Yct=trapz(xTime(idxColdTransient),emMassFlow(idxColdTransient));
        Ys=trapz(xTime(idxStabilized),emMassFlow(idxStabilized));

        % The cold transient phase of the UDDS (505s) is approx. 3.59 miles
        % The stabilized phase of the UDDS is approx. 3.86 miles.
        % Assume the PEMS test cycle is at least 3.59 miles such that the calculated
        % cold transient emissions are from the first 3.59 miles of driving
        % However, the stabilized portion of the PEMS may be more or less than 3.91
        % miles.  A proportional calculation is used to calculate the FTP
        % equivalent emissions for the stabilized phase.
        Ys=Ys*distStabil/distStabilizedMi;

        % calculation of FTP equivalent emissions.
        % Reference CFR part 86.144-94
        Yht = 0;
        Dct=distColdTransientMi;
        Dht=Dct;
        Ds=distStabil;

        gmsPerMile=0.43*((Yct+Ys)/(Dct+Ds)) + 0.57*((Yht+Ys)/(Dht+Ds));
        mgPerMile=1000*gmsPerMile;
    end


% End of pemsDataCalc function
end