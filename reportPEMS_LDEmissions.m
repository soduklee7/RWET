function reportPEMS_LDEmissions(setIdx,filename,vehData,udp)

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
S="EPA NVFEL Laboratory:  PEMS Emissions Test Report:  ";
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


hdVc=Heading3("Vehicle and Cycle");
append(rpt,hdVc);

% -- row 1
tabVC(1,1)={"Test Cycle"};
tabVC(1,2)={string(vehData(setIdx).logData.testCycle)};
tabVC(1,3)={"  ---  "};
tabVC(1,4)={"Fuel"};
tabVC(1,5)={strcat(string(vehData(setIdx).logData.fuel))};
% -- row 2
tabVC(2,1)={"Cycle Distance"};
tabVC(2,2)={cycleDistance};
tabVC(2,3)={"  ---  "};
tabVC(2,4)={"VIN"};
tabVC(2,5)={string(vehData(setIdx).logData.vin)};
% -- row 3
tabVC(3,1)={"Odometer (miles)"};
tabVC(3,2)={string(vehData(setIdx).logData.odo)};
tabVC(3,3)={"  ---  "};
tabVC(3,4)={"Start Conditions"};
tabVC(3,5)={string(vehData(setIdx).logData.startCond)};
% -- row 4
tabVC(4,1)={"Test Group"};
tabVC(4,2)={string(vehData(setIdx).logData.testGroup)};
tabVC(4,3)={"  ---  "};
tabVC(4,4)={"Displacement"};
tabVC(4,5)={string(vehData(setIdx).logData.disp)};
% -- row 5
tabVC(5,1)={"Drive Mode"};
tabVC(5,2)={string(vehData(setIdx).logData.driveMode)};
tabVC(5,3)={"  ---  "};
tabVC(5,4)={"Emissons Standard"};
tabVC(5,5)={string(vehData(setIdx).logData.emStandard)};
% -- row 6
tabVC(6,1)={"Start/Stop"};
tabVC(6,2)={string(vehData(setIdx).logData.startStop)};
tabVC(6,3)={"  ---  "};
tabVC(6,4)={"Air Conditioning"};
tabVC(6,5)={string(vehData(setIdx).logData.airCond)};
% -- row 7
tabVC(7,1)={"Driver"};
tabVC(7,2)={string(vehData(setIdx).logData.driver)};
tabVC(7,3)={"  ---  "};
tabVC(7,4)={"Equipment"};
tabVC(7,5)={string(vehData(setIdx).logData.equipment)};
% -- row 8
tabVC(8,1)={"Trailer"};
tabVC(8,2)={string(vehData(setIdx).logData.trailer)};
tabVC(8,3)={"  ---  "};
tabVC(8,4)={"Trailer + Ballast Wt."};
tabVC(8,5)={string(vehData(setIdx).logData.trailerWt)};



tabVCObj = Table(tabVC); 
tabVCObj.TableEntriesStyle = ...
    [tabVCObj.TableEntriesStyle {FontFamily("Arial"),FontSize("9pt"),InnerMargin("2pt")}];

% cell = tabVCObj.getCell(1, 3);
% cell.BackgroundColor = 'yellow'; % Set the background color


tabVCObj.Width="7.5in";
tabVCObj.Border="Solid";
tabVCObj.BorderColor="silver";
tabVCObj.RowSep="Solid";
tabVCObj.RowSepColor="Silver";
tabVCObj.ColSep="Solid";
tabVCObj.ColSepColor="Silver";


append(rpt,tabVCObj);

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
% ----------------------- Figure:  Ambient Conditions (ac)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
acHd=Heading2("Test Information");
append(rpt,acHd);

acTabObj=headerTable;  % nested function
append(rpt,acTabObj);

% -------------- Figure:  Ambient Conditions (ac)

% --- Heading for Ambient Conditions
acHdFig=Heading3("Figure:  Ambient Conditions");
append(rpt,acHdFig);

%  --- Create the figure 
acFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
acFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');

% --- vehicle speed (vsAc)
vsAcAx=nexttile;
vsAcAx.YGrid="on";
vsAcAx.YLim=[0 80];
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speedCAN);
line(vsAcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);


yyaxis(vsAcAx,'right')
vsAcAx.YLim=[0 80];
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speedGPS);
line(vsAcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.8510    0.3255    0.0980],'LineStyle','-');
ylabel(ydataC{2},'Interpreter','none')

legend('CAN','GPS','Location','northeast','Interpreter','none')

% --- ambient Temperature (amb)
ambAx=nexttile;
ambAx.YGrid="on";
[ydata,ambLega]=getData(setIdx,udp(setIdx).pems.ambientAirT);
yunit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.ambientAirT};
ydata=unitConvert(ydata,yunit,'F');
line(ambAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', 'k', 'LineWidth',1);

hold on
[ydata,ambLegb]=getData(setIdx,udp(setIdx).pems.ambientAirTCAN);
yunit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).pems.ambientAirTCAN};
ydata=unitConvert(ydata,yunit,'F');
line(ambAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.3098    0.5098    0.0471], ...
    'LineWidth',1,'LineStyle','-');
ylabel('Ambient Temperature (F)','Interpreter','none')
legend(udp(setIdx).pems.ambientAirT,udp(setIdx).pems.ambientAirTCAN,'Location','northwest','Interpreter','none')

% ---- relative humidity (rh) and drytowet corr factor
rhAx=nexttile;
rhAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.rHumidity);
line(rhAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},"Interpreter","none")

yyaxis(rhAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.dryWetCorrFac);
line(rhAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
rhAx.YLim=[0.5,1];
ylabel(ydataC{2},'Interpreter','none')

% ---- barometric pressure and altitude  (bar)
barAx=nexttile;
barAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.ambientAirP);
line(barAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},'Interpreter','none')

yyaxis(barAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.altitude);
line(barAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},'Interpreter','none')

[xdata,xdataC]=getData(setIdx,udp(setIdx).pems.time);
xlabel(xdataC{2},"Interpreter","none")


% --- link axes in X direction
linkaxes([vsAcAx,ambAx,rhAx,barAx],'x')
rhAx.YLim=[0.5,1];  %matlab bug - linkaxes resets YLim


% generate the image from figure, append to report
saveas(gcf,"ambient_image.png");

ambImg = Image("ambient_image.png");
ambImg.Width = "7in";
ambImg.Height = "7.25in";
ambImg.Style = [ambImg.Style {ScaleToFit}];

append(rpt, ambImg);



%%
% -----------------------------------------------------------------------
% ----------------------- Figure:  Exhaust Flow (exh)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
exhHd=Heading2("Exhaust Flow");
append(rpt,exhHd);

exhTabObj=headerTable;
append(rpt,exhTabObj);

% -------------- Figure:  Exhaust Flow (exh)

% --- Heading for Ambient Conditions
exhHdFig=Heading3("Figure:  Exhaust Flow");
append(rpt,exhHdFig);

%  --- Create the figure 
exhFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
exhFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% --- vehicle speed (vs)
vsExhAx=nexttile;
vsExhAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsExhAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);


% --- engine speed (eng)
engExhAx=nexttile;
engExhAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.engineSpeed);
line(engExhAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.3098    0.5098    0.0471], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

exfAx=nexttile;
exfAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.scfm);
line(exfAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},"Interpreter","none")

texExhAx=nexttile;
texExhAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.texhaust);
line(texExhAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2})

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

% --- link axes in X direction
linkaxes([vsExhAx,engExhAx,exfAx,texExhAx],'x')

% generate the image from figure, append to report
saveas(gcf,"exhFlow_image.png");

exhImg = Image("exhFlow_image.png");
exhImg.Width = "7in";
exhImg.Height = "7.25in";
exhImg.Style = [exhImg.Style {ScaleToFit}];

append(rpt, exhImg);



%%
% -----------------------------------------------------------------------
% -------------------------Figure:  Lambda and Coolant Temp (lam)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
lamHd=Heading2("Lambda and Coolant Temperature");
append(rpt,lamHd);

lamTabObj=headerTable;
append(rpt,lamTabObj);

% ---------------- Figure (lam)

% --- Heading for Lambda
lamHdFig=Heading4("Figure:  Lambda and Coolant Temperature");
append(rpt,lamHdFig);

%  --- Create the figure 
lamFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
lamFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');


% --- vehicle speed (vs)
vsLamAx=nexttile;
vsLamAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsLamAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

% --- pedal position D
engLamAx=nexttile;
engLamAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pedalPosD);
line(engLamAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.3098    0.5098    0.0471], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% --- coolant temperaure (col)
colAx=nexttile;
colAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.coolantT);
line(colAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% --- Lambda (lam)
lamAx=nexttile;
lamAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.lambda);
line(lamAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
lamAx.YLim=[0.6,1.6];
ylabel(ydataC{2},"Interpreter","none")
% 
% yyaxis(lamAx,'right')
% [ydata,ydataC]=getData(setIdx,udp(setIdx).pems.FAEquivRatio);
% line(lamAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
%     'LineWidth',1,'LineStyle','-','Color',[0.8510    0.3255    0.0980]);
% ylabel(ydataC{2},"Interpreter","none")


% Label the X axis
xlabel(xdataC{2},"Interpreter","none")


% --- link axes in X direction
linkaxes([vsLamAx,engLamAx,colAx,lamAx],'x')
lamAx.YLim=[0.6,1.6];

% generate the image from figure, append to report
saveas(gcf,"lambda_image.png");

lamImg = Image("lambda_image.png");
lamImg.Width = "7in";
lamImg.Height = "7.25in";
lamImg.Style = [lamImg.Style {ScaleToFit}];

append(rpt, lamImg);


%%


% -----------------------------------------------------------------------
% ------------------------------- New Figure:  NOx Summary (nx)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
nxHd=Heading2("Test Information");
append(rpt,nxHd);

nxTabObj=headerTable;
append(rpt,nxTabObj);


% -------------- Figure:  NOx Summary (nx)

% --- Heading for Figure NOx Summary
nxHdFig=Heading3("Figure:  Test Cycle NOx");
append(rpt,nxHdFig);

%  --- Create the figure for NOx emissions plots
nxFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
nxFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsAx=nexttile;
vsAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

yyaxis(vsAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.distSumMile);
line(vsAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.8510    0.3255    0.0980],'LineStyle','-');
ylabel(ydataC{2},'Interpreter','none')


% --- humidity correction factor (hcf)
hcfAx=nexttile;
hcfAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.noxHumidCorrFac);
line(hcfAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.3098    0.5098    0.0471], 'LineWidth',1);
hcfAx.YLim=[0.6,1.4];
ylabel(ydataC{2},"Interpreter","none")

yyaxis(hcfAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.corrCuNOxGmPerMile);
line(hcfAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},"Interpreter","none")


% --- NOx concentration and Exhaust Temperature (nxc)
nxcAx=nexttile;
nxcAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.wetkNOx);
line(nxcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")


%  --- Cummulative NOx and NOx Mass Flow (nxm)
nxmAx=nexttile;
nxmAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.kNOxSum);
line(nxmAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(nxmAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.kNOxMassFlow);
line(nxmAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (nxmAx,'left')


% --- link axes in X direction
linkaxes([vsAx,hcfAx,nxcAx,nxmAx],'x')
hcfAx.YLim=[0,0.2];    % Normal Nox limit
% hcfAx.YLim=[0,2.0];    % High NOx Limit

% generate the image from figure, append to report
saveas(gcf,"pg2_nox_image.png");

nxImg = Image("pg2_nox_image.png");
nxImg.Width = "7in";
nxImg.Height = "7.25in";
nxImg.Style = [nxImg.Style {ScaleToFit}];

append(rpt,nxImg);



%%

% -----------------------------------------------------------------------
% ------------------------------- Figure:  CO Summary (co)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
coHd=Heading2("Test Information");
append(rpt,coHd);

coTabObj=headerTable;
append(rpt,coTabObj);


% -------------- Figure:  CO Summary (co)

% --- Heading for Figure CO Summary
coHdFig=Heading3("Figure:  Test Cycle CO");
append(rpt,coHdFig);

%  --- Create the figure for CO emissions plots
coFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
coFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsCoAx=nexttile;
vsCoAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsCoAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

yyaxis(vsCoAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.distSumMile);
line(vsCoAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.8510    0.3255    0.0980],'LineStyle','-');
ylabel(ydataC{2},'Interpreter','none')

% --- Cummulative CO Grams Per Mile (coGpm)
coGpmAx=nexttile;
coGpmAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.cuCOGmPerMile);
line(coGpmAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.4667    0.6745    0.1882], 'LineWidth',2);
% coGpmAx.YLim=[0,100];  % High CO Limit
coGpmAx.YLim=[0,10];  % Normal CO Limit
ylabel(ydataC{2},"Interpreter","none")


% --- CO concentration and Lambda (coc)
cocAx=nexttile;
cocAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.wetCO);
line(cocAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',2);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(cocAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.lambda);
line(cocAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},"Interpreter","none")

%  --- Cummulative CO and CO Mass Flow (com)
comAx=nexttile;
comAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.coSum);
line(comAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(comAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.coMassFlow);
line(comAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (comAx,'left')


% --- link axes in X direction
linkaxes([vsCoAx,cocAx,comAx],'x')
cocAx.YLim=[0.6,1.6];


% generate the image from figure, append to report
saveas(gcf,"co_image.png");

coImg = Image("co_image.png");
coImg.Width = "7in";
coImg.Height = "7.25in";
coImg.Style = [coImg.Style {ScaleToFit}];

append(rpt,coImg);


%%
% -----------------------------------------------------------------------
% ------------------------------- Figure:  HC Summary (hc)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
hcHd=Heading2("Test Information");
append(rpt,hcHd);

hcTabObj=headerTable;
append(rpt,hcTabObj);



% -------------- Figure:  HC Summary (hc)

% --- Heading for Figure HC Summary
hcHdFig=Heading3("Figure:  Test Cycle HC");
append(rpt,hcHdFig);

%  --- Create the figure for CO emissions plots
hcFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
hcFig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsHcAx=nexttile;
vsHcAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsHcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

yyaxis(vsHcAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.distSumMile);
line(vsHcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.8510    0.3255    0.0980],'LineStyle','-');
ylabel(ydataC{2},'Interpreter','none')

% --- Cummulative HC Grams Per Mile (hcGpm)
hcGpmAx=nexttile;
hcGpmAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.cuHCGmPerMile);
line(hcGpmAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.4667    0.6745    0.1882], 'LineWidth',2);
% hcGpmAx.YLim=[0,4.0];  % high HC limit  
hcGpmAx.YLim=[0,0.4];  % normal HC Limit

ylabel(ydataC{2},"Interpreter","none")


% --- HC concentration and Lambda (coc)
hcAx=nexttile;
hcAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.wetHC);
line(hcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',2);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(hcAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.lambda);
line(hcAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},"Interpreter","none")


%  --- Cummulative HC and HC Mass Flow (com)
hcmAx=nexttile;
hcmAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.hcSum);
line(hcmAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(hcmAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.hcMassFlow);
line(hcmAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (hcmAx,'left')


% --- link axes in X direction
linkaxes([vsHcAx,hcAx,hcmAx],'x')
hcAx.YLim=[0.6 1.6];


% generate the image from figure, append to report
saveas(gcf,"hc_image.png");

hcImg = Image("hc_image.png");
hcImg.Width = "7in";
hcImg.Height = "7.25in";
hcImg.Style = [hcImg.Style {ScaleToFit}];

append(rpt,hcImg);

%%

% -----------------------------------------------------------------------
% ------------------------------- Figure:  CO2 Summary (co2)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
co2Hd=Heading2("Test Information");
append(rpt,co2Hd);

co2TabObj=headerTable;
append(rpt,co2TabObj);


% -------------- Figure:  CO2 Summary (co2)

% --- Heading for Figure CO Summary
co2HdFig=Heading3("Figure:  Test Cycle CO2");
append(rpt,co2HdFig);

%  --- Create the figure for CO2 emissions plots
co2Fig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
co2Fig1.InvertHardcopy="off";

tiledlayout(4,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsCo2Ax=nexttile;
vsCo2Ax.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
line(vsCo2Ax, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

yyaxis(vsCo2Ax,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.distSumMile);
line(vsCo2Ax, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color',[0.8510    0.3255    0.0980],'LineStyle','-');
ylabel(ydataC{2},'Interpreter','none')

% --- Cummulative CO2 Gms Per Mile (co2Gpm)
co2GpmAx=nexttile;
co2GpmAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.cuCO2GmPerMile);
line(co2GpmAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.4667    0.6745    0.1882], 'LineWidth',1);
% co2GpmAx.YLim=[0,10000];  % High CO2 Limit
co2GpmAx.YLim=[0,1400];  % Normal CO2 Limit
ylabel(ydataC{2},"Interpreter","none")


% --- CO2 concentration and Coolant Temperature (co2)
co2Ax=nexttile;
co2Ax.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.wetCO2);
line(co2Ax, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

%  --- Cummulative CO2 and CO2 Mass Flow (co2m)
co2mAx=nexttile;
co2mAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.co2Sum);
line(co2mAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(co2mAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.co2MassFlow);
line(co2mAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (co2mAx,'left')


% --- link axes in X direction
linkaxes([vsCo2Ax,co2mAx, co2Ax,co2mAx],'x')



% generate the image from figure, append to report
saveas(gcf,"co2_image.png");

co2Img = Image("co2_image.png");
co2Img.Width = "7in";
co2Img.Height = "7.25in";
co2Img.Style = [co2Img.Style {ScaleToFit}];

append(rpt,co2Img);


%%
if udp(setIdx).pems.pm2Active

% -----------------------------------------------------------------------
% ------------------------------- Figure:  PM Summary (pm)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
pmHd=Heading2("Test Information");
append(rpt,pmHd);

pmTabObj=headerTable;
append(rpt,pmTabObj);



% -------------- Figure:  PM Summary (pm)

% --- Heading for Figure PM Summary
pmHdFig=Heading3("Figure:  Test Cycle PM");
append(rpt,pmHdFig);

%  --- Create the figure for CO emissions plots
pmFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
pmFig1.InvertHardcopy="off";

tiledlayout(3,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsPmAx=nexttile;
vsPmAx.YGrid="on";
line(vsPmAx, vehData(setIdx).data.(udp(setIdx).pems.time), vehData(setIdx).data.(udp(setIdx).pems.speed),'Color', 'blue');
ylabel('Vehicle Speed (mph)')
title(vehData(setIdx).figtitle1);

% --- Lambda (lam)
pmLamAx=nexttile;
pmLamAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.lambda);
line(pmLamAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.4667    0.6745    0.1882], 'LineWidth',2);

ylabel(ydataC{2},"Interpreter","none")


%  --- Cummulative PM and PM Mass Flow (pmf)
pmfAx=nexttile;
pmfAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmSum);
line(pmfAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(pmfAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.pmMassTailpipe);
line(pmfAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")


% --- link axes in X direction
linkaxes([vsPmAx,pmLamAx,pmfAx],'x')
pmLamAx.YLim=[0.6,1.6];


% generate the image from figure, append to report
saveas(gcf,"pm_image.png");

pmImg = Image("pm_image.png");
pmImg.Width = "7in";
pmImg.Height = "7.25in";
pmImg.Style = [pmImg.Style {ScaleToFit}];

append(rpt,pmImg);


end



%%

% -----------------------------------------------------------------------
% ------------------------------- Figure:  Analog Signals

if udp(setIdx).pems.enableAnalog

    append(rpt, PageBreak());

    % --------------- Table - Test Information Header
    %
    anaHd=Heading2("Test Information");
    append(rpt,anaHd);

    anaTabObj=headerTable;
    append(rpt,anaTabObj);


    % -------------- Figure:  Analog Signals

    % --- Heading for Figure Analog Signals
    anaHdFig=Heading3("Figure:  Analog Signals");
    append(rpt,anaHdFig);

    %  --- Create the figure for CO2 emissions plots
    anaFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
    anaFig1.InvertHardcopy="off";

    tiledlayout(4,1,'TileSpacing','compact');

    % --- vehicle speed (vs)
    anaVsAx=nexttile;
    anaVsAx.YGrid="on";
    [ydata,ydataC]=getData(setIdx,udp(setIdx).pems.speed);
    line(anaVsAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,'Color', 'blue');
    ylabel(ydataC{2},"Interpreter","none")
    title(vehData(setIdx).figtitle1);


    % --- Pressure Transducer
    anaPrAx=nexttile;
    anaPrAx.YGrid="on";
    [ydata,ydataC]=getData(setIdx,udp(setIdx).pems.prTransPsi);
    line(anaPrAx, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
        'Color', [0.4667    0.6745    0.1882], 'LineWidth',1);
    % anaPrAx.YLim=[0,1000];
    ylabel(ydataC{2},"Interpreter","none")


    % --- Temperature Before and After Cat
    anaT1Ax=nexttile;
    anaT1Ax.YGrid="on";
    [ydata,ydataC]=getData(setIdx,udp(setIdx).pems.tcTemp1);
    line(anaT1Ax, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
        'Color', [0 0 0], 'LineWidth',1);
    ylabel(ydataC{2},"Interpreter","none")

    % yyaxis(anaT1Ax,'right')
    hold on
    [ydata,ydataC]=getData(setIdx,udp(setIdx).pems.tcTemp2);
    line(anaT1Ax, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
        'Color', [0 0 1], 'LineWidth',1);
    ylabel(ydataC{2},"Interpreter","none")

    legend(udp(setIdx).pems.tcTemp1,udp(setIdx).pems.tcTemp2,'Location','northwest','Interpreter','none')



    %  --- Temperature at Pressure Transducer
    anaT2Ax=nexttile;
    anaT2Ax.YGrid="on";
    [ydata,ydataC]=getData(setIdx,udp(setIdx).pems.tcTemp3);
    line(anaT2Ax, vehData(setIdx).data.(udp(setIdx).pems.time), ydata,...
        'Color', [0 0 0], 'LineWidth',1);
    ylabel(ydataC{2},"Interpreter","none")

    % Label the X axis
    xlabel(xdataC{2},"Interpreter","none")


    % --- link axes in X direction
    linkaxes([anaVsAx,anaPrAx, anaT1Ax,anaT2Ax],'x')



    % generate the image from figure, append to report
    saveas(gcf,"ana_image.png");

    anaImg = Image("ana_image.png");
    anaImg.Width = "7in";
    anaImg.Height = "7.25in";
    anaImg.Style = [anaImg.Style {ScaleToFit}];

    append(rpt,anaImg);


end




%%
% -------------------------------------------------------
% ------------ New Figure:   Geographic location (geo)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
geoHd=Heading2("Geogaphic Location");
append(rpt,geoHd);

geoTabObj=headerTable;
append(rpt,geoTabObj);


% --- Heading for Figure NOx Summary
geoHdFig=Heading3("Figure:  GPS Latitude and Longitude Test Route");
append(rpt,geoHdFig);

%  --- Create the figure for NOx emissions plots
geoFig=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
geoFig.InvertHardcopy="off";

latCycle=vehData(setIdx).data.(udp(setIdx).pems.latitude);
longCycle=vehData(setIdx).data.(udp(setIdx).pems.longitude);

geoplot(latCycle,longCycle,'b--')
geobasemap streets

% generate the image from figure, append to report
saveas(gcf,"geo_image.png");

geoImg = Image("geo_image.png");
geoImg.Width = "7in";
geoImg.Height = "7.25in";
geoImg.Style = [geoImg.Style {ScaleToFit}];

append(rpt,geoImg);






%%






% -------------------------------------------------  Close and view report
% ------------ Close the Report
close(rpt);
rptview(rpt);




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
%  end of main function testReportHD
end