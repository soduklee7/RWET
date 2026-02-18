function reportPEMS_PMQuality(setIdx,filename,vehData,udp)

tic

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
S="EPA NVFEL Laboratory:  PEMS PM Quality Test Report:  ";
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
pg1Tab2(3,1)={"Odometer (miles)"};
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
switch udp.log.kh
    case 0
        tabAno(3,2)={"No Correction"};
    case 1
        tabAno(3,2)={"CFR 1066.615 Vehicles at or below 14,000 lbs GVWR"};
    case 2
        tabAno(3,2)={"CFR 1065.670 SI"};
    case 3
        tabAno(3,2)={"CFR 1065.670 Diesel"};
end

if strcmp(udp.log.dataType,'pems') 
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
strCO1=sprintf('%8.4f',A);

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
% ----------------------- Figure:  Dilution Ratio Check (dr) ppm
append(rpt, PageBreak());

% --------------- Table - Test Information Header
drHd=Heading2("Test Information");
append(rpt,drHd);

drTabObj=headerTable;  % nested function
append(rpt,drTabObj);


% -------------- Figure:  Dilution Ratio Check (dr)

% --- Heading for Drift Che
drHdFig=Heading3("Figure:  PM Dilution Ratio Check");
append(rpt,drHdFig);

%  --- Create the figure 
drFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
drFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% Label the X and Y axis
[xdata,xdataC]=getData(setIdx,udp(setIdx).pems.time);


% ------- vehicle speed (vs)
vsAx=nexttile;
vsAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);


% ------ Dilution Ratio (dr)
drAx=nexttile;
drAx.YGrid="on";
drAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmDR);
line(drAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata);
ylabel(ydataC{2},'Interpreter','none')
drAx.YLim=[0 30];

hold on
yyaxis right
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmDRPegasor);
line(drAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata);
% line at 15:1 DR
line(drAx,[0 drAx.XLim(2)],[15 15],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
ylabel(ydataC{2},'Interpreter','none')
drAx.YLim=[0 30];

legend(udp(setIdx).pems.pmDR,udp(setIdx).pems.pmDRPegasor,'Nominal 15:1 Dilution Ratio','Location','best','Interpreter','none')


% ------------ PM Diluter Sample Flow (dsDr)
dsDrAx=nexttile;
dsDrAx.YGrid="on";
dsDrAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataDs,ydataC]=getData(setIdx,udp(setIdx).pems.pmDilSampleFlow);
line(dsDrAx, xdata, ydataDs);

hold on
% llimit line at 1 LPM
line(dsDrAx,[0 dsDrAx.XLim(2)],[1 1],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

ylabel(ydataC{2},'Interpreter','none')

legend(udp(setIdx).pems.pmDilSampleFlow,'Nominal 1 LPM Diluter Sample Flow','Location','best','Interpreter','none')


% ------------ PM Dilution Air Flow (daDr)
daDrAx=nexttile;
daDrAx.YGrid="on";
daDrAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataDa,ydataC]=getData(setIdx,udp(setIdx).pems.pmDilAirFlow);
line(daDrAx, xdata, ydataDa);

hold on
% limit nominal 15 lpm
line(daDrAx,[0 daDrAx.XLim(2)],[15 15],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

ylabel(ydataC{2},'Interpreter','none')

legend(udp(setIdx).pems.pmDilAirFlow,'Nominal 15 LPM Dilution Air Flow','Location','best','Interpreter','none')


% generate the image from figure, append to report
saveas(gcf,"drRatio_image.png");

drRatioImg = Image("drRatio_image.png");
drRatioImg.Width = "7in";
drRatioImg.Height = "7.25in";
drRatioImg.Style = [drRatioImg.Style {ScaleToFit}];

append(rpt, drRatioImg);


%%
%
% -----------------------------------------------------------------------
% ----------------------- Figure:  Sample Inlet Pressure/Temperaure and Makeup Flow (mf)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
mfHd=Heading2("Test Information");
append(rpt,mfHd);

mfTabObj=headerTable;  % nested function
append(rpt,mfTabObj);



% --- Heading
mfHdFig=Heading3("Figure:  PM Dilution Ratio Check");
append(rpt,mfHdFig);

%  --- Create the figure 
mfFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
mfFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% get the X axis (time)
[xdata,xdataC]=getData(setIdx,udp(setIdx).pems.time);


% ------- vehicle speed (vsMf)
vsMfAx=nexttile;
vsMfAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsMfAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);


% ------ SampleInletPressure (ipMf)
ipMfAx=nexttile;
ipMfAx.YGrid="on";
ipMfAx.ColorOrder=udp(setIdx).display.lineColor;
[ydataIp,ydataC]=getData(setIdx,udp(setIdx).pems.pmSampleInletPr);
line(ipMfAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydataIp);

ylabel(ydataC{2},'Interpreter','none')


% ------------ SampleInletTemperature (itMf)
itMfAx=nexttile;
itMfAx.YGrid="on";
itMfAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmSampleInletT);
line(itMfAx, xdata, ydata);

ylabel(ydataC{2},'Interpreter','none')



% ------------ Makeup Flow (mf)
mfAx=nexttile;
mfAx.YGrid="on";
mfAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmMakeupFlow);
line(mfAx, xdata, ydataDa);

hold on
line(mfAx,[0 mfAx.XLim(2)],[5 5],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(mfAx,[0 mfAx.XLim(2)],[0 0],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

ylabel(ydataC{2},'Interpreter','none')

legend(udp(setIdx).pems.pmMakeupFlow,'Limit 0-5 LPM','Location','best','Interpreter','none')


% generate the image from figure, append to report
saveas(gcf,"mfRatio_image.png");

mfRatioImg = Image("mfRatio_image.png");
mfRatioImg.Width = "7in";
mfRatioImg.Height = "7.25in";
mfRatioImg.Style = [mfRatioImg.Style {ScaleToFit}];

append(rpt, mfRatioImg);


%%

%
% -----------------------------------------------------------------------
% ------------ Figure:  Filter Flow, Filter Flow Temp, Filter Block Temp (ff)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
ffHd=Heading2("Test Information");
append(rpt,ffHd);

ffTabObj=headerTable;  % nested function
append(rpt,ffTabObj);



% --- Heading
ffHdFig=Heading3("Figure:  PM Dilution Ratio Check");
append(rpt,ffHdFig);

%  --- Create the figure 
ffFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
ffFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% get the X axis (time)
[xdata,xdataC]=getData(setIdx,udp(setIdx).pems.time);


% ------- vehicle speed (vs)
vsAx=nexttile;
vsAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);


% ------ Filter Flow (ff)
ffAx=nexttile;
ffAx.YGrid="on";
ffAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmFilterFlow);
line(ffAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata);

line(ffAx,[0 ffAx.XLim(2)],[30 30],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

ylabel(ydataC{2},'Interpreter','none')
legend(udp(setIdx).pems.pmFilterFlow,'Nominal 30 LPM','Location','best','Interpreter','none')


% ------------ Filter Flow Temp (ft)
ftAx=nexttile;
ftAx.YGrid="on";
ftAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmFilterFlowT);
line(ftAx, xdata, ydata);

hold on
line(ftAx,[0 ftAx.XLim(2)],[30 30],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(ftAx,[0 ftAx.XLim(2)],[50 50],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

ylabel(ydataC{2},'Interpreter','none')
legend(udp(setIdx).pems.pmFilterFlowT,'Limit 30-50 C','Location','best','Interpreter','none')



% ------------ Filter Block Temperature (fb)
fbAx=nexttile;
fbAx.YGrid="on";
fbAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmFilterBlockT);
line(fbAx, xdata, ydata);

hold on
line(fbAx,[0 fbAx.XLim(2)],[47 47],'Color',[0.3020    0.7451    0.9333],'linestyle','--')


ylabel(ydataC{2},'Interpreter','none')

legend(udp(setIdx).pems.pmFilterBlockT,'Setpoint 47 C','Location','best','Interpreter','none')


% generate the image from figure, append to report
saveas(gcf,"ffRatio_image.png");

ffRatioImg = Image("ffRatio_image.png");
ffRatioImg.Width = "7in";
ffRatioImg.Height = "7.25in";
ffRatioImg.Style = [ffRatioImg.Style {ScaleToFit}];

append(rpt, ffRatioImg);


%%

%
% -----------------------------------------------------------------------
% ------------ Figure:  Filter outlet pressure, inlet pressure and inlet flow  (if)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
ifHd=Heading2("Test Information");
append(rpt,ifHd);

ifTabObj=headerTable;  % nested function
append(rpt,ifTabObj);



% --- Heading
ifHdFig=Heading3("Figure:  PM Dilution Ratio Check");
append(rpt,ifHdFig);

%  --- Create the figure 
ifFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
ifFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% get the X axis (time)
[xdata,xdataC]=getData(setIdx,udp(setIdx).pems.time);


% ------- vehicle speed (vs)
vsAx=nexttile;
vsAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);


% ------ Filter Outlet Pressure (op)
opAx=nexttile;
opAx.YGrid="on";
opAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmFilterOutletPr);
line(opAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata);

hold on
line(opAx,[0 opAx.XLim(2)],[0 0],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(opAx,[0 opAx.XLim(2)],[15 15],'Color',[0.3020    0.7451    0.9333],'linestyle','--')

ylabel(ydataC{2},'Interpreter','none')
legend(udp(setIdx).pems.pmFilterOutletPr,'Limit 0-15 kPa','Location','best','Interpreter','none')



% ------------ Inlet Pressure (inp)
inpAx=nexttile;
inpAx.YGrid="on";
inpAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmInletPr);
line(inpAx, xdata, ydata);

hold on
line(inpAx,[0 inpAx.XLim(2)],[90 90],'Color',[0.3020    0.7451    0.9333],'linestyle','--')


ylabel(ydataC{2},'Interpreter','none')
legend(udp(setIdx).pems.pmInletPr,'Nominal 90 kPa','Location','best','Interpreter','none')



% ------------ Inlet Flow (inf)
infAx=nexttile;
infAx.YGrid="on";
infAx.ColorOrder=udp(setIdx).display.lineColor;
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmInletFlow);
line(infAx, xdata, ydata);

hold on
line(infAx,[0 infAx.XLim(2)],[60 60],'Color',[0.3020    0.7451    0.9333],'linestyle','--')
line(infAx,[0 infAx.XLim(2)],[150 150],'Color',[0.3020    0.7451    0.9333],'linestyle','--')


ylabel(ydataC{2},'Interpreter','none')

legend(udp(setIdx).pems.pmInletFlow,'Limit 60-150 LPM','Location','best','Interpreter','none')



% generate the image from figure, append to report
saveas(gcf,"inletFlow_image.png");

ifImg = Image("inletFlow_image.png");
ifImg.Width = "7in";
ifImg.Height = "7.25in";
ifImg.Style = [ifImg.Style {ScaleToFit}];

append(rpt, ifImg);






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




toc
% -----------------------------------------------------------------------------
%  end of main function
end