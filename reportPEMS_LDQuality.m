function reportPEMS_LDQuality(setIdx,filename,vehData,udp)

% tic

makeDOMCompilable();

import mlreportgen.report.*
import mlreportgen.dom.*

rpt = Document(filename,'pdf');
open(rpt);


pageLayoutObj = PDFPageLayout;
pageLayoutObj.PageSize.Height = "11in";
pageLayoutObj.PageSize.Width = "8.5in";
pageLayoutObj.PageMargins.Left = '0.5in';
pageLayoutObj.PageMargins.Right = '0.5in';
pageLayoutObj.PageMargins.Top = '0.5in';
pageLayoutObj.PageMargins.Bottom = '0.25in';
pageLayoutObj.PageMargins.Header = '0.5in';
pageLayoutObj.PageMargins.Footer = '0.5in';
pageLayoutObj.FirstPageNumber=1;
append(rpt,pageLayoutObj);



% --------------- create footer with horizontal rule and page number
footer = PDFPageFooter("default");
rpt.CurrentPageLayout.PageFooters = footer;

pagePara = Paragraph("Page ");
pagePara.FontSize="8pt";
pagePara.WhiteSpace = "preserve";
pagePara.HAlign = "center";

pageNum = Page();

hr=HorizontalRule();
append(footer,hr);

append(pagePara,pageNum);
append(footer,pagePara);

% ------------------ create a header with horizontal rule
header=PDFPageHeader("default");
rpt.CurrentPageLayout.PageHeaders=header;
hrHeader=HorizontalRule();

fspec='%s %s %s %s';
S="NVFEL Laboratory:  PEMS Quality Test Report:  ";
A=string(vehData(setIdx).logData.oem);
B=string(vehData(setIdx).logData.model);
C=string(vehData(setIdx).logData.my);
headerTitle=sprintf(fspec,S,A,B,C);
fspec='%s %s %s';
vehModel=sprintf(fspec,A,B,C);

paraHeader=Paragraph(headerTitle);
paraHeader.HAlign="center";
paraHeader.FontSize="8pt";
append(header,paraHeader);
append(header,hrHeader);



% ------------------------------- Page 1, Table 1 - Test Information  (Tf)
% 
pg1HdTf=Heading3("Test Information");
append(rpt,pg1HdTf);

pg1Tab1(1,1)={"Date and Time"};
pg1Tab1(1,2)={string(vehData(setIdx).logData.dateTime)};
pg1Tab1(2,1)={"Vehicle Model"};
pg1Tab1(2,2)={vehModel};
pg1Tab1(3,1)={"Vehicle ID"};
pg1Tab1(3,2)={string(vehData(setIdx).logData.vehicleID)};
pg1Tab1(4,1)={"File Name"};
pg1Tab1(4,2)={string(vehData(setIdx).filename)};


pg1Tab1Obj = Table(pg1Tab1); 
pg1Tab1Obj.TableEntriesStyle = ...
    [pg1Tab1Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

pg1Tab1Obj.Width="7.5in";
pg1Tab1Obj.Border="Solid";
pg1Tab1Obj.BorderColor="silver";
pg1Tab1Obj.RowSep="Solid";
pg1Tab1Obj.RowSepColor="Silver";
pg1Tab1Obj.ColSep="Solid";
pg1Tab1Obj.ColSepColor="Silver";

append(rpt,pg1Tab1Obj);
clear fspec S A B C


% -------------------- Page1, Table 2 - Vehicle and Cycle (Vc)

A=vehData(setIdx).scalarData.Distance_Mile;
S=string(vehData(setIdx).scalarData.Properties.VariableUnits("Distance_Mile"));
fspec='%10.2f %s';
cycleDistance=sprintf(fspec,A,S);


pg1HdVc=Heading3("Vehicle and Cycle");
append(rpt,pg1HdVc);

% -- row 1
pg1Tab2(1,1)={"Test Cycle"};
pg1Tab2(1,2)={string(vehData(setIdx).logData.testCycle)};
pg1Tab2(1,3)={"  ---  "};
pg1Tab2(1,4)={"Fuel"};
pg1Tab2(1,5)={strcat(string(vehData(setIdx).logData.fuel))};
% -- row 2
pg1Tab2(2,1)={"Cycle Distance"};
pg1Tab2(2,2)={cycleDistance};
pg1Tab2(2,3)={"  ---  "};
pg1Tab2(2,4)={"VIN"};
pg1Tab2(2,5)={string(vehData(setIdx).logData.vin)};
% -- row 3
pg1Tab2(3,1)={"Odometer"};
pg1Tab2(3,2)={string(vehData(setIdx).logData.odo)};
pg1Tab2(3,3)={"  ---  "};
pg1Tab2(3,4)={"Start Conditions"};
pg1Tab2(3,5)={string(vehData(setIdx).logData.startCond)};
% -- row 4
pg1Tab2(4,1)={"Test Group"};
pg1Tab2(4,2)={string(vehData(setIdx).logData.testGroup)};
pg1Tab2(4,3)={"  ---  "};
pg1Tab2(4,4)={"Displacement"};
pg1Tab2(4,5)={string(vehData(setIdx).logData.disp)};
% -- row 5
pg1Tab2(5,1)={"Drive Mode"};
pg1Tab2(5,2)={string(vehData(setIdx).logData.driveMode)};
pg1Tab2(5,3)={"  ---  "};
pg1Tab2(5,4)={"Emissons Standard"};
pg1Tab2(5,5)={string(vehData(setIdx).logData.emStandard)};
% -- row 6
pg1Tab2(6,1)={"Start/Stop"};
pg1Tab2(6,2)={string(vehData(setIdx).logData.startStop)};
pg1Tab2(6,3)={"  ---  "};
pg1Tab2(6,4)={"Air Conditioning"};
pg1Tab2(6,5)={string(vehData(setIdx).logData.airCond)};
% -- row 7
pg1Tab2(7,1)={"Driver"};
pg1Tab2(7,2)={string(vehData(setIdx).logData.driver)};
pg1Tab2(7,3)={"  ---  "};
pg1Tab2(7,4)={"Equipment"};
pg1Tab2(7,5)={string(vehData(setIdx).logData.equipment)};
% -- row 8
pg1Tab2(8,1)={"Trailer"};
pg1Tab2(8,2)={string(vehData(setIdx).logData.trailer)};
pg1Tab2(8,3)={"  ---  "};
pg1Tab2(8,4)={"Trailer + Ballast Wt."};
pg1Tab2(8,5)={string(vehData(setIdx).logData.trailerWt)};



pg1Tab2Obj = Table(pg1Tab2); 
pg1Tab2Obj.TableEntriesStyle = ...
    [pg1Tab2Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

pg1Tab2Obj.Width="7.5in";
pg1Tab2Obj.Border="Solid";
pg1Tab2Obj.BorderColor="silver";
pg1Tab2Obj.RowSep="Solid";
pg1Tab2Obj.RowSepColor="Silver";
pg1Tab2Obj.ColSep="Solid";
pg1Tab2Obj.ColSepColor="Silver";


append(rpt,pg1Tab2Obj);

clear A S fspec cycleDistance


% -----------------  Page 1, Table:  Fuel Properties (fuel)

hdFuel=Heading3("Fuel Properties");
append(rpt,hdFuel);

% -- row 1
tabFuel(1,1)={"FTAG"};
tabFuel(1,2)={string(vehData(setIdx).logData.ftag)};
% -- row 2
tabFuel(2,1)={"Lower Heating Value (BTU/lb)"};
tabFuel(2,2)={string(udp(setIdx).fuel.nhv)};
% -- row 3
tabFuel(3,1)={"Carbon Weight Fraction"};
tabFuel(3,2)={string(udp(setIdx).fuel.cwf)};
% -- row 4
tabFuel(4,1)={"Specific Gravity"};
tabFuel(4,2)={string(udp(setIdx).fuel.sg)};

tabFuelObj = Table(tabFuel); 
tabFuelObj.TableEntriesStyle = ...
    [tabFuelObj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

tabFuelObj.Width="7.5in";
tabFuelObj.Border="Solid";
tabFuelObj.BorderColor="silver";
tabFuelObj.RowSep="Solid";
tabFuelObj.RowSepColor="Silver";
tabFuelObj.ColSep="Solid";
tabFuelObj.ColSepColor="Silver";
tabFuelObj.TableEntriesHAlign="center";

append(rpt,tabFuelObj);





% ----------------- Page 1, Table:  Analysis Options  (ano)

anoFuel=Heading3("File Import and Analysis Options");
append(rpt,anoFuel);

% -- row 1
tabAno(1,1)={"File Import: Fill Missing Data"};
tabAno(1,2)={string(udp(setIdx).import.missingData)};
% -- row 2
tabAno(2,1)={"File Import: Fill End Values (extrapolate)"};
tabAno(2,2)={string(udp(setIdx).import.endValues)};

% -- row 3
tabAno(3,1)={"Humidity Correction Factor"};
switch udp(setIdx).log.kh
    case 0
        tabAno(3,2)={"No Correction"};
    case 1
        tabAno(3,2)={"CFR 1066.615 Vehicles at or below 14,000 lbs GVWR"};
    case 2
        tabAno(3,2)={"CFR 1065.670 SI"};
    case 3
        tabAno(3,2)={"CFR 1065.670 Diesel"};
end

if strcmp(udp(setIdx).log.dataType,'pems') 
    % -- row 4
    tabAno(4,1)={"Vehicle Speed Source (CAN or GPS)"};
    tabAno(4,2)={string(udp(setIdx).pems.speedSource)};
end

tabAnoObj = Table(tabAno); 
tabAnoObj.TableEntriesStyle = ...
    [tabAnoObj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

tabAnoObj.Width="7.5in";
tabAnoObj.Border="Solid";
tabAnoObj.BorderColor="silver";
tabAnoObj.RowSep="Solid";
tabAnoObj.RowSepColor="Silver";
tabAnoObj.ColSep="Solid";
tabAnoObj.ColSepColor="Silver";
tabAnoObj.TableEntriesHAlign="center";

append(rpt,tabAnoObj);



% ---------------------------- Page1, Table 6 - Ambient Conditions (amb)
%
pg1HdAmb = Heading3("Ambient and Start Conditions"); 
append(rpt, pg1HdAmb);

T=vehData(setIdx).scalarData.Avg_Ambient_Temperature;
H=vehData(setIdx).scalarData.Avg_Ambient_RelativeHumidity;
fspec='%8.1f';
strAmbT=sprintf(fspec,T);
strAmbH=sprintf(fspec,H);

idleTime=vehData(setIdx).scalarData.Idle_Time_At_Start;
idleTimeUnit=vehData(setIdx).scalarData.Properties.VariableUnits{'Idle_Time_At_Start'};
coolantT=vehData(setIdx).scalarData.Coolant_T_At_Start;
coolantTUnit=vehData(setIdx).scalarData.Properties.VariableUnits{'Coolant_T_At_Start'};
ambientT=vehData(setIdx).scalarData.Ambient_T_At_Start;
ambientTUnit=vehData(setIdx).scalarData.Properties.VariableUnits{'Ambient_T_At_Start'};

tabAmb(1,1)={"Average Ambient Temperature"};
tabAmb(1,2)={'F'};
tabAmb(1,3)={strAmbT};
tabAmb(2,1)={"Average Ambient Relative Humidity"};
tabAmb(2,2)={'%'};
tabAmb(2,3)={strAmbH};
tabAmb(3,1)={"Ambient Temperature At Start"};
tabAmb(3,2)={ambientTUnit};
tabAmb(3,3)={sprintf('%8.1f',ambientT)};
tabAmb(4,1)={"Coolant Temperature At Start"};
tabAmb(4,2)={coolantTUnit};
tabAmb(4,3)={sprintf('%8.1f',coolantT)};
tabAmb(5,1)={"Idle Time At Start"};
tabAmb(5,2)={idleTimeUnit};
tabAmb(5,3)={sprintf('%8.1f',idleTime)};

tabAmbObj = Table(tabAmb); 
tabAmbObj.TableEntriesStyle = ...
    [tabAmbObj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

tabAmbObj.Width="7.5in";
tabAmbObj.Border="Solid";
tabAmbObj.BorderColor="silver";
tabAmbObj.RowSep="Solid";
tabAmbObj.RowSepColor="Silver";
tabAmbObj.ColSep="Solid";
tabAmbObj.ColSepColor="Silver";
tabAmbObj.TableEntriesHAlign="center";

append(rpt, tabAmbObj);



% -------------------- Page1, Table - Purpose and Notes (Pn)
pg1HdPn=Heading3("Test Purpose and Notes");
append(rpt,pg1HdPn);

pg1TabPn(1,1)={"Test Purpose"};
pg1TabPn(1,2)={string(vehData(setIdx).logData.purpose)};

pg1TabPn(2,1)={"Notes and Issues"};
pg1TabPn(2,2)={string(vehData(setIdx).logData.notes)};

pg1TabPnObj = Table(pg1TabPn); 
pg1TabPnObj.TableEntriesStyle = ...
    [pg1TabPnObj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

pg1TabPnObj.Width="7.5in";
pg1TabPnObj.Border="Solid";
pg1TabPnObj.BorderColor="silver";
pg1TabPnObj.RowSep="Solid";
pg1TabPnObj.RowSepColor="Silver";
pg1TabPnObj.ColSep="Solid";
pg1TabPnObj.ColSepColor="Silver";
tabAnoObj.TableEntriesHAlign="center";


append(rpt,pg1TabPnObj);

clear A S fspec cycleDistance


% ---------------------------  Page Break
br = PageBreak();
append(rpt,br);

% --------------- Test Information Header
acHd=Heading2("Test Information");
append(rpt,acHd);

weTabObj=headerTable;  % nested function
append(rpt,weTabObj);

% --------------  Emissions Default Format
fspec='%8.1f';


% ---------------------------- Page1, Table 3 - Mass Emissions  (Me)
% 
pg1HdMe = Heading3("Test Cycle Mass Emissions"); 
append(rpt, pg1HdMe);

A=vehData(setIdx).scalarData.kNOx_Mg_Per_Mile;
strNOx1=string(vehData(setIdx).scalarData.Properties.VariableUnits("kNOx_Mg_Per_Mile"));
strNOx2=sprintf(fspec,A);

A=vehData(setIdx).scalarData.HC_Mg_Per_Mile;
strHC1=string(vehData(setIdx).scalarData.Properties.VariableUnits("HC_Mg_Per_Mile"));
strHC2=sprintf(fspec,A);

A=vehData(setIdx).scalarData.NMHC_Mg_Per_Mile;
strNMHC1=string(vehData(setIdx).scalarData.Properties.VariableUnits("NMHC_Mg_Per_Mile"));
strNMHC2=sprintf(fspec,A);

A=vehData(setIdx).scalarData.NOxPlusNMHC_Mg_Per_Mile;
strPlus1=string(vehData(setIdx).scalarData.Properties.VariableUnits("NOxPlusNMHC_Mg_Per_Mile"));
strPlus2=sprintf(fspec,A);

A=vehData(setIdx).scalarData.CO_Gms_Per_Mile;
strCO=string(vehData(setIdx).scalarData.Properties.VariableUnits("CO_Gms_Per_Mile"));
strCO1=sprintf('%8.2f',A);

A=vehData(setIdx).scalarData.CO2_Gms_Per_Mile;
strCO2a=string(vehData(setIdx).scalarData.Properties.VariableUnits("CO2_Gms_Per_Mile"));
strCO2b=sprintf('%8.1f',A);


pg1Tab3(1,1)={"kNOx"};
pg1Tab3(2,1)={strNOx1};
pg1Tab3(3,1)={strNOx2};
pg1Tab3(1,2)={"THC"};
pg1Tab3(2,2)={strHC1};
pg1Tab3(3,2)={strHC2};
pg1Tab3(1,3)={"NMHC"};
pg1Tab3(2,3)={strNMHC1};
pg1Tab3(3,3)={strNMHC2};
pg1Tab3(1,4)={"kNOx+NMHC"};
pg1Tab3(2,4)={strPlus1};
pg1Tab3(3,4)={strPlus2};
pg1Tab3(1,5)={"CO"};
pg1Tab3(2,5)={strCO};
pg1Tab3(3,5)={strCO1};
pg1Tab3(1,6)={"CO2"};
pg1Tab3(2,6)={strCO2a};
pg1Tab3(3,6)={strCO2b};

pg1Tab3Obj = Table(pg1Tab3); 
pg1Tab3Obj.TableEntriesStyle = ...
    [pg1Tab3Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

pg1Tab3Obj.Width="7.5in";
pg1Tab3Obj.Border="Solid";
pg1Tab3Obj.BorderColor="silver";
pg1Tab3Obj.RowSep="Solid";
pg1Tab3Obj.RowSepColor="Silver";
pg1Tab3Obj.ColSep="Solid";
pg1Tab3Obj.ColSepColor="Silver";
pg1Tab3Obj.TableEntriesHAlign="center";

append(rpt, pg1Tab3Obj);



if udp(setIdx).pems.pm2Active


    % ---------------------------- Page1, Table 4 - Particulates (Pe)
    pg1HdPe = Heading3("Particulate Emissions");
    append(rpt, pg1HdPe);

    pg1Tab4(1,1)={"Filter Position #"};
    pg1Tab4(2,1)={"(-)"};
    pg1Tab4(3,1)={udp(setIdx).log.filterPosition};
    pg1Tab4(1,2)={"Filter ID #"};
    pg1Tab4(2,2)={"(-)"};
    pg1Tab4(3,2)={udp(setIdx).log.filter2ID};
    pg1Tab4(1,3)={"Pre-Weight"};
    pg1Tab4(2,3)={"(mg)"};
    pg1Tab4(3,3)={sprintf('%8.4f',udp(setIdx).log.filter2WtPre)};
    pg1Tab4(1,4)={"Post-Weight"};
    pg1Tab4(2,4)={"(mg)"};
    pg1Tab4(3,4)={sprintf('%8.4f',udp(setIdx).log.filter2WtPost)};
    pg1Tab4(1,5)={"PM Tailpipe Mass"};
    pg1Tab4(2,5)={"(mg)"};
    pg1Tab4(3,5)={sprintf('%8.2f',udp(setIdx).log.pmTaipipeMass)};
    pg1Tab4(1,6)={"PM Tailpipe mg/mile"};
    pg1Tab4(2,6)={"(mg/mile)"};
    pg1Tab4(3,6)={sprintf('%8.2f',udp(setIdx).log.pmTailpipeDistanceSpec)};


    pg1Tab4Obj = Table(pg1Tab4);
    pg1Tab4Obj.TableEntriesStyle = ...
        [pg1Tab4Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

    pg1Tab4Obj.Width="7.5in";
    pg1Tab4Obj.Border="Solid";
    pg1Tab4Obj.BorderColor="silver";
    pg1Tab4Obj.RowSep="Solid";
    pg1Tab4Obj.RowSepColor="Silver";
    pg1Tab4Obj.ColSep="Solid";
    pg1Tab4Obj.ColSepColor="Silver";
    pg1Tab4Obj.TableEntriesHAlign="center";

    append(rpt, pg1Tab4Obj);

end


% ---------------------------- Page1, Table 5 - Fuel Economy (Fe)
%
pg1HdFe = Heading3("Fuel Economy"); 
append(rpt, pg1HdFe);

FE=vehData(setIdx).scalarData.Fuel_Economy;
FEUnits=string(vehData(setIdx).scalarData.Properties.VariableUnits("Fuel_Economy"));
fspec='%8.2f';
strFE=sprintf(fspec,FE);

pg1Tab5(1,1)={"Fuel Economy"};
pg1Tab5(2,1)={FEUnits};
pg1Tab5(3,1)={strFE};

pg1Tab5Obj = Table(pg1Tab5); 
pg1Tab5Obj.TableEntriesStyle = ...
    [pg1Tab5Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

pg1Tab5Obj.Width="2in";
pg1Tab5Obj.Border="Solid";
pg1Tab5Obj.BorderColor="silver";
pg1Tab5Obj.RowSep="Solid";
pg1Tab5Obj.RowSepColor="Silver";
pg1Tab5Obj.ColSep="Solid";
pg1Tab5Obj.ColSepColor="Silver";
pg1Tab5Obj.TableEntriesHAlign="center";

append(rpt, pg1Tab5Obj);
clear FE FEUnits



% --------------------- Page1, Table 7 - Weighted Emissions  (ftp)
% 
if udp(setIdx).log.ftpNormCalc

    pg1Hdftp = Heading3("Test Cycle Mass Emissions:  Weighted to FTP75");
    append(rpt, pg1Hdftp);

    fspec='%8.1f';

    A=vehData(setIdx).scalarData.kNOx_Mg_Per_Mile_FTPEquiv;
    strNOx1=string(vehData(setIdx).scalarData.Properties.VariableUnits("kNOx_Mg_Per_Mile_FTPEquiv"));
    strNOx2=sprintf(fspec,A);

    A=vehData(setIdx).scalarData.HC_Mg_Per_Mile_FTPEquiv;
    strHC1=string(vehData(setIdx).scalarData.Properties.VariableUnits("HC_Mg_Per_Mile_FTPEquiv"));
    strHC2=sprintf(fspec,A);

    A=vehData(setIdx).scalarData.NMHC_Mg_Per_Mile_FTPEquiv;
    strNMHC1=string(vehData(setIdx).scalarData.Properties.VariableUnits("NMHC_Mg_Per_Mile_FTPEquiv"));
    strNMHC2=sprintf(fspec,A);

    A=vehData(setIdx).scalarData.NOxPlusNMHC_Mg_Per_Mile_FTPEquiv;
    strPlus1=string(vehData(setIdx).scalarData.Properties.VariableUnits("NOxPlusNMHC_Mg_Per_Mile_FTPEquiv"));
    strPlus2=sprintf(fspec,A);

    A=vehData(setIdx).scalarData.CO_Gms_Per_Mile_FTPEquiv;
    strCO=string(vehData(setIdx).scalarData.Properties.VariableUnits("CO_Gms_Per_Mile_FTPEquiv"));
    strCO1=sprintf('%8.2f',A);

    A=vehData(setIdx).scalarData.CO2_Gms_Per_Mile_FTPEquiv;
    strCO2a=string(vehData(setIdx).scalarData.Properties.VariableUnits("CO2_Gms_Per_Mile_FTPEquiv"));
    strCO2b=sprintf('%8.1f',A);


    pg1Tab7(1,1)={"kNOx"};
    pg1Tab7(2,1)={strNOx1};
    pg1Tab7(3,1)={strNOx2};
    pg1Tab7(1,2)={"THC"};
    pg1Tab7(2,2)={strHC1};
    pg1Tab7(3,2)={strHC2};
    pg1Tab7(1,3)={"NMHC"};
    pg1Tab7(2,3)={strNMHC1};
    pg1Tab7(3,3)={strNMHC2};
    pg1Tab7(1,4)={"kNOx+NMHC"};
    pg1Tab7(2,4)={strPlus1};
    pg1Tab7(3,4)={strPlus2};
    pg1Tab7(1,5)={"CO"};
    pg1Tab7(2,5)={strCO};
    pg1Tab7(3,5)={strCO1};
    pg1Tab7(1,6)={"CO2"};
    pg1Tab7(2,6)={strCO2a};
    pg1Tab7(3,6)={strCO2b};

    pg1Tab7Obj = Table(pg1Tab7);
    pg1Tab7Obj.TableEntriesStyle = ...
        [pg1Tab7Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

    pg1Tab7Obj.Width="7.5in";
    pg1Tab7Obj.Border="Solid";
    pg1Tab7Obj.BorderColor="silver";
    pg1Tab7Obj.RowSep="Solid";
    pg1Tab7Obj.RowSepColor="Silver";
    pg1Tab7Obj.ColSep="Solid";
    pg1Tab7Obj.ColSepColor="Silver";
    pg1Tab7Obj.TableEntriesHAlign="center";

    append(rpt, pg1Tab7Obj);

end







%%
% -----------------------------------------------------------------------
% ----------------------- Figure:  Drift Check (dc) ppm
append(rpt, PageBreak());

% --------------- Table - Test Information Header
dcHd=Heading2("Test Information");
append(rpt,dcHd);

dcTabObj=headerTable;  % nested function
append(rpt,dcTabObj);


% -------------- Figure:  Drift Check (dc)

% --- Heading for Drift Check
dcHdFig=Heading3("Figure:  Drift Check");
append(rpt,dcHdFig);

%  --- Create the figure 
dcFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
dcFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');

% --- NOx Drift Check (nxDc)
nxDcAx=nexttile;
nxDcAx.YGrid="on";
nxDcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataNOx,ydataC]=getData(setIdx,udp(setIdx).pems.kNOxSum);
line(nxDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataNOx);
title(vehData(setIdx).figtitle1);

hold on
[ydataNOxDrift,ydataC]=getData(setIdx,udp(setIdx).pems.kNOxSumDrift);
line(nxDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataNOxDrift,'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")

% Drift Verification CFR 1065.550(b)(3)(i)(B)
driftNOx=100.*(ydataNOx-ydataNOxDrift)./ydataNOx;

yyaxis(nxDcAx,'right')
line(nxDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), driftNOx)
nxDcAx.YLim=[-10,10];

% line lines at 4%
line(nxDcAx,[0 nxDcAx.XLim(2)],[4 4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(nxDcAx,[0 nxDcAx.XLim(2)],[-4 -4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

ylabel('Drift (% of Uncorr. Mass)','Interpreter','none')

legend(udp(setIdx).pems.kNOxSum,udp(setIdx).pems.kNOxSumDrift,'Drift as % Uncorr. Mass','Limit +/- 4%','Location','northwest','Interpreter','none')


% ------------ THC Drift Check (hcDc)
hcDcAx=nexttile;
hcDcAx.YGrid="on";
hcDcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataHC,ydataC]=getData(setIdx,udp(setIdx).pems.hcSum);
line(hcDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataHC);

hold on
[ydataHCDrift,ydataC]=getData(setIdx,udp(setIdx).pems.hcSumDrift);
line(hcDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataHCDrift,'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")

driftHC=100.*(ydataHC-ydataHCDrift)./ydataHC;

yyaxis(hcDcAx,'right')
line(hcDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), driftHC)
% line lines at 4%
line(hcDcAx,[0 hcDcAx.XLim(2)],[4 4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(hcDcAx,[0 hcDcAx.XLim(2)],[-4 -4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')


hcDcAx.YLim=[-10,10];
% ylabel(strcat('Drift (',ydataC{5},')'),'Interpreter','none')
ylabel('Drift (% of Uncorr. Mass)','Interpreter','none')

legend(udp(setIdx).pems.hcSum,udp(setIdx).pems.hcSumDrift,'Drift as % Uncorr. Mass','Limit +/- 4%','Location','northwest','Interpreter','none')



% --- CO Drift Check (coDc)
coDcAx=nexttile;
coDcAx.YGrid="on";
coDcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataCO,ydataC]=getData(setIdx,udp(setIdx).pems.coSum);
line(coDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataCO);


hold on
[ydataCODrift,ydataC]=getData(setIdx,udp(setIdx).pems.coSumDrift);
line(coDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataCODrift,'Color',[0.8510    0.3255    0.0980])

ylabel(ydataC{2},"Interpreter","none")

driftCO=100.*(ydataCO-ydataCODrift)./ydataCO;


yyaxis(coDcAx,'right')
line(coDcAx, vehData(setIdx).data.(udp(setIdx).pems.time), driftCO)
% line lines at 4%
line(coDcAx,[0 coDcAx.XLim(2)],[4 4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(coDcAx,[0 coDcAx.XLim(2)],[-4 -4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

coDcAx.YLim=[-10,10];

ylabel('Drift (% of Uncorr. Mass)','Interpreter','none')

legend(udp(setIdx).pems.coSum,udp(setIdx).pems.coSumDrift,'Drift as % Uncorr. Mass','Limit +/- 4%','Location','northwest','Interpreter','none')



% --- CO2 Drift Check (co2Dc)
co2DcAx=nexttile;
co2DcAx.YGrid="on";
co2DcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataCO2,ydataC]=getData(setIdx,udp(setIdx).pems.co2Sum);
line(co2DcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataCO2);


hold on
[ydataCO2Drift,ydataC]=getData(setIdx,udp(setIdx).pems.co2SumDrift);
line(co2DcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataCO2Drift,'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")

driftCO2=100.*(ydataCO2-ydataCO2Drift)./ydataCO2;
% driftCO2(find(isnan(driftCO2)))=0;
% driftCO2(find(driftCO2>=99.99))=0;
% driftCO2(find(driftCO2==-100))=0;
% driftCO2(find(ydataCO2 <= 1e-2 & ydataCO2 <= 1e-2))=0;

yyaxis(co2DcAx,'right')
line(co2DcAx, vehData(setIdx).data.(udp(setIdx).pems.time), driftCO2)
% line lines at 4%
line(co2DcAx,[0 co2DcAx.XLim(2)],[4 4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(co2DcAx,[0 co2DcAx.XLim(2)],[-4 -4],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

co2DcAx.YLim=[-10,10];

% Label the X and Y axis
[xdata,xdataC]=getData(setIdx,udp(setIdx).pems.time);
xlabel(xdataC{2},"Interpreter","none")
ylabel('Drift (% of Uncorr. Mass)','Interpreter','none')

legend(udp(setIdx).pems.co2Sum,udp(setIdx).pems.co2SumDrift,'Drift as % Uncorr. Mass','Limit +/- 4%','Location','northwest','Interpreter','none')




% generate the image from figure, append to report
saveas(gcf,"drift_image.png");

driftImg = Image("drift_image.png");
driftImg.Width = "7in";
driftImg.Height = "7.25in";
driftImg.Style = [driftImg.Style {ScaleToFit}];

append(rpt, driftImg);


%%
% -----------------------------------------------------------------------
% ----------------------- New Figure:  Span Gas Limit Check (span)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
spanHd=Heading2("Span Gas Limits");
append(rpt,spanHd);

spanTabObj=headerTable;
append(rpt,spanTabObj);

% -------------- Figure:  Span Gas Limits

% --- Heading for Ambient Conditions
spanHdFig=Heading3("Figure:  Span Gas Limits");
append(rpt,spanHdFig);

%  --- Create the figure 
spanFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
spanFig1.InvertHardcopy="off";

tiledlayout(5,1,'TileSpacing','compact');


% --- NO Span Check (noSp)
noSpAx=nexttile;
noSpAx.YGrid="on";
noSpAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataNO,ydataC]=getData(setIdx,udp(setIdx).pems.NO);
line(noSpAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataNO);
title(vehData(setIdx).figtitle1);

hold on
timeMin=min(vehData(setIdx).data.(udp(setIdx).pems.time));
timeMax=max(vehData(setIdx).data.(udp(setIdx).pems.time));
noSpan=udp(setIdx).log.noRefSpan;
line(noSpAx,[timeMin,timeMax],[noSpan,noSpan],'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")

legend(udp(setIdx).pems.NO,'NO Span','Location','northeast','Interpreter','none')


% --- NO2 Span Check (no2Sp)
no2SpAx=nexttile;
no2SpAx.YGrid="on";
no2SpAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataNO2,ydataC]=getData(setIdx,udp(setIdx).pems.NO2);
line(no2SpAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataNO2);


hold on
no2Span=udp(setIdx).log.no2RefSpan;
line(no2SpAx,[timeMin,timeMax],[no2Span,no2Span],'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")

legend(udp(setIdx).pems.NO2,'NO2 Span','Location','northeast','Interpreter','none')


% --- HC Span Check (hcSp)
hcSpAx=nexttile;
hcSpAx.YGrid="on";
hcSpAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataHC,ydataC]=getData(setIdx,udp(setIdx).pems.HC);
line(hcSpAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataHC);


hold on
hcSpan=udp(setIdx).log.thcRefSpan;
line(hcSpAx,[timeMin,timeMax],[hcSpan,hcSpan],'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")

legend(udp(setIdx).pems.HC,'HC Span','Location','northeast','Interpreter','none')


% --- CO Span Check (hcSp)
coSpAx=nexttile;
coSpAx.YGrid="on";
coSpAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataCO,ydataC]=getData(setIdx,udp(setIdx).pems.CO);
line(coSpAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataCO);


hold on
coSpan=udp(setIdx).log.coRefSpan;
coSpan=unitConvert(coSpan,vehData(setIdx).logData.Properties.VariableUnits{'coRefSpan'},...
    ydataC{5});
line(coSpAx,[timeMin,timeMax],[coSpan,coSpan],'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")

legend(udp(setIdx).pems.CO,'CO Span','Location','northeast','Interpreter','none')


% --- CO2 Span Check (co2Sp)
co2SpAx=nexttile;
co2SpAx.YGrid="on";
co2SpAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataCO2,ydataC]=getData(setIdx,udp(setIdx).pems.CO2);
line(co2SpAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataCO2);


hold on
co2Span=udp(setIdx).log.co2RefSpan;
coSpan=unitConvert(co2Span,vehData(setIdx).logData.Properties.VariableUnits{'co2RefSpan'},...
    ydataC{5});
line(co2SpAx,[timeMin,timeMax],[co2Span,coSpan],'Color',[0.8510    0.3255    0.0980])
ylabel(ydataC{2},"Interpreter","none")
xlabel(xdataC{2},"Interpreter","none")
legend(udp(setIdx).pems.CO2,'CO2 Span','Location','northeast','Interpreter','none')


% 
% generate the image from figure, append to report
saveas(gcf,"spanLimit_image.png");

spanImg = Image("spanLimit_image.png");
spanImg.Width = "7in";
spanImg.Height = "7.25in";
spanImg.Style = [spanImg.Style {ScaleToFit}];

append(rpt, spanImg);


%%

% -----------------------------------------------------------------------
% ----------------------- New Figure:  Sample Flow, Battery Voltage, #DTCs, Block Temp (pqc)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
pqcHd=Heading2("PEMS Quality Checks");
append(rpt,pqcHd);

pqcTabObj=headerTable;
append(rpt,pqcTabObj);

% -------------- Figure:  PEMS Quality Checks

% --- Heading for Sample Flow
pqcHdFig=Heading3("Figure:  Sample Flow");
append(rpt,pqcHdFig);

%  --- Create the figure 
pqcFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
pqcFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% --- Sample Flow (flo)
floQcAx=nexttile;
floQcAx.YGrid="on";
floQcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.sampleFlow);
line(floQcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0 0 1]);
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);
floQcAx.YLim=[2 4];
floQcAx.YTick=2:0.2:4;

% --- Battery 2 Voltage (b2v)
b2vQcAx=nexttile;
b2vQcAx.YGrid="on";
b2vQcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.batt1Voltage);
line(b2vQcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata);
ylabel(ydataC{2},"Interpreter","none")
b2vQcAx.YLim=[0 15];

hold on
yyaxis(b2vQcAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.batt2Voltage);
line(b2vQcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata)
ylabel(ydataC{2},"Interpreter","none")
b2vQcAx.YLim=[0 15];


% --- Number of DTCs (dtc)
dtcQcAx=nexttile;
dtcQcAx.YGrid="on";
dtcQcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.numOfDTC);
line(dtcQcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.8510    0.3255    0.0980]);
ylabel(ydataC{2},"Interpreter","none")


% --- Block Temperature (bkt)
bktQcAx=nexttile;
bktQcAx.YGrid="on";
bktQcAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.blockT);
line(bktQcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.4667    0.6745    0.1882]);
ylabel(ydataC{2},"Interpreter","none")


% 
% generate the image from figure, append to report
saveas(gcf,"qchek_image.png");

qchekImg = Image("qchek_image.png");
qchekImg.Width = "7in";
qchekImg.Height = "7.25in";
qchekImg.Style = [qchekImg.Style {ScaleToFit}];

append(rpt, qchekImg);


%%

% -----------------------------------------------------------------------
% ----------------------- New Figure:  SampleHumidity, SampleTemperature, HeatedFilterTemperature, Faults
append(rpt, PageBreak());

% --------------- Table - Test Information Header
samHd=Heading2("PEMS Quality Checks");
append(rpt,samHd);

samTabObj=headerTable;
append(rpt,samTabObj);

% -------------- Figure:  PEMS Quality Checks

% --- Heading for Sample Flow
samHdFig=Heading3("Figure:  Sample Humidity and Temperature");
append(rpt,samHdFig);

%  --- Create the figure 
samFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
samFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% --- Sample Humidity (samH)
samHAx=nexttile;
samHAx.YGrid="on";
samHAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.sampleH);
line(samHAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0 0 1]);
line(samHAx,[0 samHAx.XLim(2)],[15 15],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);
%samHAx.YLim=[0 20];
legend(udp(setIdx).pems.sampleH,'Sample Humidity Limit < 15%','Location','northwest','Interpreter','none')

% --- Sample Temperature (samT)
samTAx=nexttile;
samTAx.YGrid="on";
samTAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.sampleT);
line(samTAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata);
ylabel(ydataC{2},"Interpreter","none")

% --- Heated Filter Temperature (hft)
hftAx=nexttile;
hftAx.YGrid="on";
hftAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.heatedFilterT);
line(hftAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.8510    0.3255    0.0980]);
ylabel(ydataC{2},"Interpreter","none")


% --- Power Distribution Faults (flt)
fltAx=nexttile;
fltAx.YGrid="on";
fltAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.faults);
line(fltAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.4667    0.6745    0.1882]);
ylabel(ydataC{2},"Interpreter","none")


% 
% generate the image from figure, append to report
saveas(gcf,"qchekSam_image.png");

qchekSamImg = Image("qchekSam_image.png");
qchekSamImg.Width = "7in";
qchekSamImg.Height = "7.25in";
qchekSamImg.Style = [qchekSamImg.Style {ScaleToFit}];

append(rpt, qchekSamImg);





%%

% -------------------------------------------------  Close and view report
% ------------ Close the Report
close(rpt);
rptview(rpt);




%%
% --------------------------------------------------------
% --------------------------- nested fuctions


% -------------------------------- basic info header table
function tabObj = headerTable

cellTab(1,1)={"Date and Time"};
cellTab(1,2)={string(vehData(setIdx).logData.dateTime)};
cellTab(2,1)={"Vehicle Model"};
cellTab(2,2)={vehModel};
cellTab(3,1)={"Vehicle ID"};
cellTab(3,2)={string(vehData(setIdx).logData.vehicleID)};
cellTab(4,1)={"File Name"};
cellTab(4,2)={string(vehData(setIdx).filename)};

tabObj = Table(cellTab); 
tabObj.TableEntriesStyle = ...
    [tabObj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

tabObj.Width="7in";
tabObj.Border="Solid";
tabObj.BorderColor="silver";
tabObj.RowSep="Solid";
tabObj.RowSepColor="Silver";
tabObj.ColSep="Solid";
tabObj.ColSepColor="Silver";

end




% toc
% -----------------------------------------------------------------------------
%  end of main function
end