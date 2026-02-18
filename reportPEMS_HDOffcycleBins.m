function reportPEMS_HDOffcycleBins(setIdx,filename,vehData,udp,binData)

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
pageLayoutObj.PageMargins.Top = '0.25in';
pageLayoutObj.PageMargins.Bottom = '0in';
pageLayoutObj.PageMargins.Header = '0.5in';
pageLayoutObj.PageMargins.Footer = '0.5in';
pageLayoutObj.FirstPageNumber=1;
append(rpt,pageLayoutObj);


% --------------- create footer with horizontal rule and page number
footer = PDFPageFooter("default");
rpt.CurrentPageLayout.PageFooters = footer;

pagePara = Paragraph("Page ");
pagePara.FontSize="9pt";
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
S="NVFEL Laboratory:  PEMS Test Report:  ";
A=string(vehData(setIdx).logData.oem);
B=string(vehData(setIdx).logData.model);
C=string(vehData(setIdx).logData.my);
headerTitle=sprintf(fspec,S,A,B,C);
fspec='%s %s %s';
vehModel=sprintf(fspec,A,B,C);

paraHeader=Paragraph(headerTitle);
paraHeader.HAlign="center";
paraHeader.FontSize="9pt";
append(header,paraHeader);
append(header,hrHeader);



% ------------------------------- Page 1, Table 1 - Test Information  (Tf)
%
pg1HdTf=Heading2("Test Information");
append(rpt,pg1HdTf);

pg1Tab1(1,1)={"Date and Time"};
pg1Tab1(1,2)={string(vehData(setIdx).logData.dateTime)};
pg1Tab1(2,1)={"Vehicle Model"};
pg1Tab1(2,2)={vehModel};
pg1Tab1(3,1)={"Vehicle ID"};
pg1Tab1(3,2)={string(vehData(setIdx).logData.vehid)};
pg1Tab1(4,1)={"File Name"};
pg1Tab1(4,2)={string(vehData(setIdx).filename)};


pg1Tab1Obj = Table(pg1Tab1);
pg1Tab1Obj.TableEntriesStyle = ...
    [pg1Tab1Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];

pg1Tab1Obj.Width="7in";
pg1Tab1Obj.Border="Solid";
pg1Tab1Obj.BorderColor="silver";
pg1Tab1Obj.RowSep="Solid";
pg1Tab1Obj.RowSepColor="Silver";
pg1Tab1Obj.ColSep="Solid";
pg1Tab1Obj.ColSepColor="Silver";

append(rpt,pg1Tab1Obj);
clear fspec S A B C


% -------------------- Page1, Table 2 - Vehicle and Cycle (Vc)
pg1HdVc=Heading2("Vehicle and Cycle");
append(rpt,pg1HdVc);

pg1Tab2(1,1)={"Test Cycle"};
pg1Tab2(1,2)={string(vehData(setIdx).logData.testCycle)};

A=vehData(setIdx).scalarData.Distance_Mile;
S=string(vehData(setIdx).scalarData.Properties.VariableUnits("Distance_Mile"));
fspec='%10.2f %s';
cycleDistance=sprintf(fspec,A,S);

pg1Tab2(2,1)={"Cycle Distance"};
pg1Tab2(2,2)={cycleDistance};
pg1Tab2(3,1)={"Odometer"};
pg1Tab2(3,2)={string(vehData(setIdx).logData.odo)};
pg1Tab2(1,3)={"       "};
pg1Tab2(2,3)={"       "};
pg1Tab2(3,3)={"       "};
pg1Tab2(1,4)={"Fuel"};
pg1Tab2(1,5)={string(vehData(setIdx).logData.fuel)};
pg1Tab2(2,4)={"VIN"};
pg1Tab2(2,5)={string(vehData(setIdx).logData.vin)};
pg1Tab2(3,4)={"Notes"};
pg1Tab2(3,5)={string(vehData(setIdx).logData.notes)};

pg1Tab2Obj = Table(pg1Tab2);
pg1Tab2Obj.TableEntriesStyle = ...
    [pg1Tab2Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];

pg1Tab2Obj.Width="7in";
pg1Tab2Obj.Border="Solid";
pg1Tab2Obj.BorderColor="silver";
pg1Tab2Obj.RowSep="Solid";
pg1Tab2Obj.RowSepColor="Silver";
pg1Tab2Obj.ColSep="Solid";
pg1Tab2Obj.ColSepColor="Silver";


append(rpt,pg1Tab2Obj);

clear A S fspec cycleDistance



% ---------------------------- Page1, Table 3 - Mass Emissions  (Me)
%
pg1HdMe = Heading2("Test Cycle Mass Emissions");
append(rpt, pg1HdMe);

A=vehData(setIdx).scalarData.kNOx_Gms_Per_Mile;
strNOx1=string(vehData(setIdx).scalarData.Properties.VariableUnits("kNOx_Gms_Per_Mile"));
strNOx2=sprintf('%8.4f',A);

A=vehData(setIdx).scalarData.CO_Gms_Per_Mile;
strCO=string(vehData(setIdx).scalarData.Properties.VariableUnits("CO_Gms_Per_Mile"));
fspec='%8.4f';
strCO1=sprintf(fspec,A);

A=vehData(setIdx).scalarData.HC_Gms_Per_Mile;
strHCa=string(vehData(setIdx).scalarData.Properties.VariableUnits("HC_Gms_Per_Mile"));
strHCb=sprintf(fspec,A);

A=vehData(setIdx).scalarData.CO2_Gms_Per_Mile;
strCO2a=string(vehData(setIdx).scalarData.Properties.VariableUnits("CO2_Gms_Per_Mile"));
strCO2b=sprintf(fspec,A);


pg1Tab3(1,1)={"NOx"};
pg1Tab3(2,1)={strNOx1};
pg1Tab3(3,1)={strNOx2};
pg1Tab3(1,2)={"CO"};
pg1Tab3(2,2)={strCO};
pg1Tab3(3,2)={strCO1};
pg1Tab3(1,3)={"HC"};
pg1Tab3(2,3)={strHCa};
pg1Tab3(3,3)={strHCb};
pg1Tab3(1,4)={"CO2"};
pg1Tab3(2,4)={strCO2a};
pg1Tab3(3,4)={strCO2b};

pg1Tab3Obj = Table(pg1Tab3);
pg1Tab3Obj.TableEntriesStyle = ...
    [pg1Tab3Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];

pg1Tab3Obj.Width="7in";
pg1Tab3Obj.Border="Solid";
pg1Tab3Obj.BorderColor="silver";
pg1Tab3Obj.RowSep="Solid";
pg1Tab3Obj.RowSepColor="Silver";
pg1Tab3Obj.ColSep="Solid";
pg1Tab3Obj.ColSepColor="Silver";
pg1Tab3Obj.TableEntriesHAlign="center";

append(rpt, pg1Tab3Obj);



% ---------------------------- Page1, Table 4 - Particulates (Pe)
pg1HdPe = Heading2("Particulate Emissions");
append(rpt, pg1HdPe);

pg1Tab4(1,1)={"Filter Number"};
pg1Tab4(2,1)={"(-)"};
pg1Tab4(3,1)={" "};
pg1Tab4(1,2)={"Pre-Weight"};
pg1Tab4(2,2)={"(mg)"};
pg1Tab4(3,2)={" "};
pg1Tab4(1,3)={"Post-Weight"};
pg1Tab4(2,3)={"(mg)"};
pg1Tab4(3,3)={" "};
pg1Tab4(1,4)={"Net Total Mass"};
pg1Tab4(2,4)={"(mg)"};
pg1Tab4(3,4)={" "};
pg1Tab4(1,4)={"Total Mass/Dis"};
pg1Tab4(2,4)={"(gm/mile)"};
pg1Tab4(3,4)={" "};


pg1Tab4Obj = Table(pg1Tab4);
pg1Tab4Obj.TableEntriesStyle = ...
    [pg1Tab4Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];

pg1Tab4Obj.Width="7in";
pg1Tab4Obj.Border="Solid";
pg1Tab4Obj.BorderColor="silver";
pg1Tab4Obj.RowSep="Solid";
pg1Tab4Obj.RowSepColor="Silver";
pg1Tab4Obj.ColSep="Solid";
pg1Tab4Obj.ColSepColor="Silver";
pg1Tab4Obj.TableEntriesHAlign="center";

append(rpt, pg1Tab4Obj);


% ---------------------------- Page1, Table 5 - Fuel Economy (Fe)
%
pg1HdFe = Heading2("Fuel Economy");
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
    [pg1Tab5Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];

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


% ---------- Page1, Table 6 - Off-Cycle Emissions:  Intervals (Int)
pg1HdInt = Heading2("Off-Cycle Emissions - Intervals");
append(rpt, pg1HdInt);

% tab4=table(1,4)
pg1Tab6(1,1)={"Total Intervals"};
pg1Tab6(2,1)={vehData(setIdx).scalarBinData.Number_Intervals};
pg1Tab6(1,2)={"Valid Intervals"};
pg1Tab6(2,2)={vehData(setIdx).scalarBinData.NumValid_Intervals};
pg1Tab6(1,3)={"Invalid Intervals"};
pg1Tab6(2,3)={vehData(setIdx).scalarBinData.NumInValid_Intervals};
pg1Tab6(1,4)={"Bin 1 Intervals"};
pg1Tab6(2,4)={vehData(setIdx).scalarBinData.NumBin1_Intervals};
pg1Tab6(1,5)={"Bin 2 Intervals"};
pg1Tab6(2,5)={vehData(setIdx).scalarBinData.NumBin2_Intervals};



pg1Tab6Obj = Table(pg1Tab6);
pg1Tab6Obj.TableEntriesStyle = ...
    [pg1Tab6Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];


pg1Tab6Obj.Width="7in";
pg1Tab6Obj.Border="Solid";
pg1Tab6Obj.BorderColor="silver";
pg1Tab6Obj.RowSep="Solid";
pg1Tab6Obj.RowSepColor="Silver";
pg1Tab6Obj.ColSep="Solid";
pg1Tab6Obj.ColSepColor="Silver";
pg1Tab6Obj.TableEntriesHAlign="center";


append(rpt, pg1Tab6Obj);


% --------------------- Page1, Table 7 - Bin1 NOx Emissions (Bnx)

pg1HdBnx = Heading2("Bin 1 NOx Emissions");
append(rpt, pg1HdBnx);

bin1NOx=vehData(setIdx).scalarBinData.NOxMassFlow_Bin1;
noxBin1Unit=string(vehData(setIdx).scalarBinData.Properties.VariableUnits("NOxMassFlow_Bin1"));
noxBin1Value=sprintf('%8.4f',bin1NOx);

pg1Tab7(1,1)={"NOx Bin 1"};
pg1Tab7(2,1)={noxBin1Unit};
pg1Tab7(3,1)={noxBin1Value};

pg1Tab7Obj = Table(pg1Tab7);
pg1Tab7Obj.TableEntriesStyle = ...
    [pg1Tab7Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];


pg1Tab7Obj.Width="2in";
pg1Tab7Obj.Border="Solid";
pg1Tab7Obj.BorderColor="silver";
pg1Tab7Obj.RowSep="Solid";
pg1Tab7Obj.RowSepColor="Silver";
pg1Tab7Obj.ColSep="Solid";
pg1Tab7Obj.ColSepColor="Silver";
pg1Tab7Obj.TableEntriesHAlign="center";


append(rpt, pg1Tab7Obj);


% --------------------- Page1, Table 8 - Bin2 Emissions (B2e)

pg1HdB2e = Heading2("Bin 2 NOx Emissions");
append(rpt, pg1HdB2e);

bin2NOx=vehData(setIdx).scalarBinData.NOxBrakeSpecific_Bin2;
noxBin2Unit=string(vehData(setIdx).scalarBinData.Properties.VariableUnits("NOxBrakeSpecific_Bin2"));
noxBin2Value=sprintf('%8.4f',bin2NOx);

bin2HC=vehData(setIdx).scalarBinData.hcBrakeSpecific_Bin2;
hcBin2Unit=string(vehData(setIdx).scalarBinData.Properties.VariableUnits("hcBrakeSpecific_Bin2"));
hcBin2Value=sprintf('%8.4f',bin2HC);

bin2CO=vehData(setIdx).scalarBinData.coBrakeSpecific_Bin2;
coBin2Unit=string(vehData(setIdx).scalarBinData.Properties.VariableUnits("coBrakeSpecific_Bin2"));
coBin2Value=sprintf('%8.4f',bin2CO);


pg1Tab8(1,1)={"NOx Bin 2"};
pg1Tab8(2,1)={noxBin2Unit};
pg1Tab8(3,1)={noxBin2Value};

pg1Tab8(1,2)={"HC Bin 2"};
pg1Tab8(2,2)={hcBin2Unit};
pg1Tab8(3,2)={hcBin2Value};

pg1Tab8(1,3)={"PM Bin 2"};
pg1Tab8(2,3)={"--"};
pg1Tab8(3,3)={"--"};

pg1Tab8(1,4)={"CO Bin 2"};
pg1Tab8(2,4)={coBin2Unit};
pg1Tab8(3,4)={coBin2Value};



pg1Tab8Obj = Table(pg1Tab8);
pg1Tab8Obj.TableEntriesStyle = ...
    [pg1Tab8Obj.TableEntriesStyle {FontFamily("Arial"),FontSize("11pt"),InnerMargin("2pt")}];


pg1Tab8Obj.Width="7in";
pg1Tab8Obj.Border="Solid";
pg1Tab8Obj.BorderColor="silver";
pg1Tab8Obj.RowSep="Solid";
pg1Tab8Obj.RowSepColor="Silver";
pg1Tab8Obj.ColSep="Solid";
pg1Tab8Obj.ColSepColor="Silver";
pg1Tab8Obj.TableEntriesHAlign="center";


append(rpt, pg1Tab8Obj);




% -----------------------------------------------------------------------
% ----------------------- Figure:  Included Intervals
append(rpt, PageBreak());

% --------------- Table - Test Information Header
incTotalHd=Heading2("Test Information");
append(rpt,incTotalHd);

incTotalTabObj=headerTable;  % nested function
append(rpt,incTotalTabObj);

% --- Heading for Included Intervals
incHdFig=Heading2("Figure:  Included Intervals");
append(rpt,incHdFig);



% -----1---------------  Figure:  Included Intervals
lineWid=3;

figinclude = figure('Position',[563,50,942,982]);

tiledlayout(6,1,"TileSpacing","loose","Padding","compact");
[xData,xDataC]=getData(setIdx,udp(setIdx).pems.time);

bx1=nexttile;
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.includeEngSpeed);
plot(xData,yData,'LineWidth',lineWid,'Color',[0 0 1])
% xlabel(xDataC{1,2})
ylabel(yDataC{1,2},'Interpreter','none')
%title(yDataC{1,3},'Interpreter','none')
hold on
yyaxis right
bx1.YGrid='on';
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.engineSpeed);
plot(xData,yData,'LineWidth',1.5)
ylabel(yDataC{1,2},'Interpreter','none')

bx2=nexttile;
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.includeRegen);
plot(xData,yData,'LineWidth',lineWid,'Color',[0 0 1])
% xlabel(xDataC{1,2})
ylabel(yDataC{1,2},'Interpreter','none')
% title(yDataC{1,3},'Interpreter','none')
hold on
yyaxis right
bx2.YGrid='on';
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.regenStatus);
plot(xData,yData,'LineWidth',1.5)
ylabel(yDataC{1,2},'Interpreter','none')

bx3=nexttile;
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.includeTmax);
plot(xData,yData,'LineWidth',lineWid,'Color',[0 0 1])
ylabel(yDataC{1,2},'Interpreter','none')

hold on
yyaxis right
bx3.YGrid='on';
[yData,yDataC1]=getData(setIdx,udp(setIdx).pems.tMaxLimit);
plot(xData,yData,'LineWidth',1.5)
ylabel(yDataC1{1,2},'Interpreter','none')
[yData,yDataC2]=getData(setIdx,udp(setIdx).pems.ambientAirT);
plot(xData,yData,'LineWidth',1.5,'Color',[0.1608    0.4784    0.0431],'LineStyle','-')
legend(yDataC{1,2},yDataC1{1,2},yDataC2{1,2},'Interpreter','none','Location','northeastoutside')

% Ambient Temperature > 5 C
bx4=nexttile;
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.includeAmbient5C);
plot(xData,yData,'LineWidth',lineWid,'Color',[0 0 1])
ylabel(yDataC{1,2},'Interpreter','none')

hold on
yyaxis right
[yData,yDataC1]=getData(setIdx, udp(setIdx).pems.ambientTLimit);
plot(xData,yData,'LineWidth',1.5)

[yData,yDataC2]=getData(setIdx, udp(setIdx).pems.ambientAirT);
plot(xData,yData,'LineWidth',1.5,'Color',[0.1608    0.4784    0.0431],'LineStyle','-')
ylabel(yDataC1{1,2},'Interpreter','none')
legend(yDataC{1,2},yDataC1{1,2},yDataC2{1,2},'Interpreter','none','Location','northeastoutside')


% Altitude < 5500 ft
bx5=nexttile;
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.includeAltitude);
plot(xData,yData,'LineWidth',lineWid,'Color',[0 0 1])
ylabel(yDataC{1,2},'Interpreter','none')

hold on
yyaxis right
bx5.YGrid='on';
[yData,yDataC1]=getData(setIdx, udp(setIdx).pems.altitudeLimit);
plot(xData,yData,'LineWidth',1.5)
ylabel(yDataC1{1,2},'Interpreter','none')

[yData,yDataC2]=getData(setIdx, udp(setIdx).pems.altitudeFt);
plot(xData,yData,'LineWidth',1.5,'Color',[0.1608    0.4784    0.0431],'Marker','none','LineStyle','-')
ylabel(yDataC1{1,2},'Interpreter','none')

legend(yDataC{1,2},yDataC1{1,2},yDataC2{1,2},'Interpreter','none','Location','northeastoutside')


bx6=nexttile;
[yData,yDataC]=getData(setIdx, udp(setIdx).pems.includeTotal);
plot(xData,yData,'LineWidth',lineWid,'Color',[0 0 1])
xlabel(xDataC{2})
ylabel(yDataC{2},'Interpreter','none')


linkaxes([bx1 bx2 bx3 bx4 bx5 bx6],'x')


% generate the image from figure, append to report
saveas(gcf,"include_image.png");

includeImg = Image("include_image.png");
includeImg.Width = "7.5in";
includeImg.Height = "7.75in";
includeImg.Style = [includeImg.Style {ScaleToFit}];

append(rpt, includeImg);




% ------2-----------------------------------------------------------------
% ----------------------- Header:  Invalid Intervals
append(rpt, PageBreak());

% --------------- Table - Test Information Header
invalidHd=Heading2("Test Information");
append(rpt,invalidHd);

invalidTabObj=headerTable;  % nested function
append(rpt,invalidTabObj);


% --- Heading for Invalid Intervals
invalidFig=Heading2("Figure:  Invalid Intervals");
append(rpt,invalidFig);



% ------------------------  Figure:  Invalid Intervals
figure2=figure('Position',[563,100,942,982]);

tx2=tiledlayout(2,1,"TileSpacing","loose","Padding","compact");
dx1=nexttile;

[yData,yDataC]=getData(setIdx, udp(setIdx).pems.includeTotal);
plot(xData,yData,'LineWidth',lineWid,'Color',[0 0 1])

ylabel(yDataC{2},'Interpreter','none')

dx2=nexttile;
x1data=cell2mat(binData(3,:));
y1data=cell2mat(binData(5,:));
plot(x1data,y1data,'Color',[0 0 0])
ylabel('Invalid_Intervals','Interpreter','none')
xlabel(xDataC{2})

% generate the image from figure, append to report
saveas(gcf,"incTotal_image.png");

incTotalImg = Image("incTotal_image.png");
incTotalImg.Width = "7.5in";
incTotalImg.Height = "8in";
incTotalImg.Style = [includeImg.Style {ScaleToFit}];

append(rpt, incTotalImg);




% -----3------------------------------------------------------------------
% ----------------------- Header:  Bin 1 NOx
append(rpt, PageBreak());

% --------------- Table - Test Information Header
bin1Hd=Heading2("Test Information");
append(rpt,bin1Hd);

bin1TabObj=headerTable;  % nested function
append(rpt,bin1TabObj);


% --- Heading for Invalid Intervals
invalidFig=Heading2("Figure:  Bin 1 NOx");
append(rpt,invalidFig);

% ---------------------------  Figure:  Bin 1 NOx
figure3 = figure('Position',[563,100,942,982]);


tiledlayout(3,1,"TileSpacing","loose","Padding","compact");

ax1=nexttile;

plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.speed),'Color',[0 0 1])
ax1.YColor=[0 0 0];
ax1.YGrid="on";
ylabel('Vehicle Speed (mph)')

yyaxis right
plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.engineSpeed),'Color',[.7 .7 .7])
ax1.YColor=[0 0 0];
ylabel('Engine Speed (rpm)')


ax2=nexttile;

% --- kNOx mass flow
[yData,yDataC]=getData(setIdx,udp(setIdx).pems.kNOxMassFlow);
plot(xData,yData)
ylabel(yDataC{2},'Interpreter','none')


ax3=nexttile;

plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.NOx_Mass_Bin1)
ylabel('NOx_Mass_Bin1  (gm)','Interpreter','none')
xlabel(xDataC{2})
ax3.YGrid='on';

hold on
yyaxis right
plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.NOxMassFlow_Bin1_Cummulative)
ylabel('NOxMassFlow_Bin1_Cummulative (gm/hr)')


% % number of bin1 intervals
% logicBin1=cell2mat(binIData(9,:))==1;
% cumNumBin1=cumtrapz(vehData(setIdx).binData.Time_BinAvg,logicBin1);
% plot(vehData(setIdx).binData.Time_BinAvg,cumNumBin1)
% ylabel('Number of Bin1 Intervals')


%
linkaxes([ax1 ax2 ax3],'x')

% generate the image from figure, append to report
saveas(gcf,"bin1Nox_image.png");

normCO2Img = Image("bin1Nox_image.png");
normCO2Img.Width = "7.5in";
normCO2Img.Height = "8in";
normCO2Img.Style = [includeImg.Style {ScaleToFit}];

append(rpt, normCO2Img);


% ---4--------------------------------------------------------------------
% ----------------------- Header:  Normalized CO2 (norm)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
normHd=Heading2("Test Information");
append(rpt,normHd);

normTabObj=headerTable;  % nested function
append(rpt,normTabObj);


% --- Heading for Invalid Intervals
normFig=Heading2("Figure:  Normalized CO2");
append(rpt,normFig);

% ----------------------  Figure:  Normalized CO2

figure4 = figure('Position',[563,100,942,982]);

tiledlayout(3,1,"TileSpacing","loose","Padding","compact");

cx1=nexttile;

yyaxis right
plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.engineSpeed),'Color',[.7 .7 .7])
cx1.YColor=[0 0 0];
ylabel('Engine Speed (rpm)')

yyaxis left
plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.speed),'Color',[0 0 1])
cx1.YColor=[0 0 0];
cx1.YGrid="on";
ylabel('Vehicle Speed (mph)')


cx2=nexttile;

% --- CO2 mass flow
[xTime,xTimeCell]=getData(setIdx,udp(setIdx).pems.time);
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.co2MassFlow);
plot(xTime,ydata)
ylabel(ydataC{2},'Interpreter','none')


cx3=nexttile;

% --- mCO2, Norm
x1=cell2mat(binData(3,:));  % avg interval time
x2=cell2mat(binData(8,:));  % CO2 norm
plot(x1,x2,'Color',[0.4941    0.1843    0.5569])
cx3.YLim=[0,80];

% --- 6% CO2 norm limit
hold on
cycleIdx=cell2mat(binData(2,:));  %start and end indices
minIdx=min(cycleIdx);
maxIdx=max(cycleIdx);
timeMin=vehData(setIdx).data.(udp(setIdx).pems.time)(minIdx);
timeMax=vehData(setIdx).data.(udp(setIdx).pems.time)(maxIdx);
plot([timeMin,timeMax],[6 6],'Color',[0.8510    0.3255    0.0980],'LineStyle','-','LineWidth',2)
ax3.YColor=[0 0 0];

ylabel('Normalized CO2 (%)')
xlabel('Time (s)')

% ---- Bin Number
yyaxis right
xx1=cell2mat(binData(3,:));  % avg interval time
xx2=cell2mat(binData(9,:));  % Bins
plot(xx1,xx2,'Color',[0.4667    0.6745    0.1882])
cx3.YLim=[-10,4];
cx3.YColor=[0.4667    0.6745    0.1882];
ylabel('Bin Number')

%
linkaxes([cx1 cx2 cx3],'x')
cx3.YLim=[-10,4];
legend('Normalized CO2','6% Bin 1 Limit','Bin Number','Interpreter','none','Location','northeastoutside')

% generate the image from figure, append to report
saveas(gcf,"normCO2_image.png");

normCO2Img = Image("normCO2_image.png");
normCO2Img.Width = "7.5in";
normCO2Img.Height = "8in";
normCO2Img.Style = [includeImg.Style {ScaleToFit}];

append(rpt, normCO2Img);



% ---5--------------------------------------------------------------------
% ----------------------- Header:  Bin2 NOx (b2nox)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
b2noxHd=Heading2("Test Information");
append(rpt,b2noxHd);

b2noxTabObj=headerTable;  % nested function
append(rpt,b2noxTabObj);


% --- Heading for Invalid Intervals
b2noxFig=Heading2("Figure:  Bin 2 NOx");
append(rpt,b2noxFig);



% -------------------------------------------- figure 5, NOx Bin 2
figure5 = figure('Position',[563,100,942,982]);

tiledlayout(3,1,"TileSpacing","loose","Padding","compact");

ex1=nexttile;

plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.speed),'Color',[0 0 1])
ex1.YColor=[0 0 0];
ex1.YGrid="on";
ylabel('Vehicle Speed (mph)')

yyaxis right
plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.engineSpeed),'Color',[.7 .7 .7])
ex1.YColor=[0 0 0];
ylabel('Engine Speed (rpm)')


ex2=nexttile;

% --- kNOx mass flow
[xTime,xTimeCell]=getData(setIdx,udp(setIdx).pems.time);
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.kNOxMassFlow);
plot(xTime,ydata)
ylabel(ydataC{2},'Interpreter','none')
ex2.YGrid='on';


ex3=nexttile;

% --- NOx Mass Bin 2
plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.NOx_Mass_Bin2)
ylabel('NOx_Mass_Bin2  (gm)','Interpreter','none')
ex3.YGrid='on';

hold on

% ---
yyaxis right
plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.NOx_BrakeSpec_Bin2_Cummulative)
ylabel('NOx_BrakeSpec_Bin2_Cummulative  (gm/hp*hr)','Interpreter','none')


linkaxes([ex1 ex2 ex3],'x')
% cx3.YLim=[-10,4];
% legend('Normalized CO2','6% Bin 1 Limit','Bin Number','Interpreter','none','Location','northeastoutside')

% generate the image from figure, append to report
saveas(gcf,"bin2NOx_image.png");

bin2NOxImg = Image("bin2NOx_image.png");
bin2NOxImg.Width = "7.5in";
bin2NOxImg.Height = "8in";
bin2NOxImg.Style = [includeImg.Style {ScaleToFit}];

append(rpt, bin2NOxImg);



% ---6--------------------------------------------------------------------
% ----------------------- Header:  Bin2 CO (b2co)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
b2coHd=Heading2("Test Information");
append(rpt,b2coHd);

b2coTabObj=headerTable;  % nested function
append(rpt,b2coTabObj);


% --- Heading for Invalid Intervals
b2coFig=Heading2("Figure:  Bin 2 CO");
append(rpt,b2coFig);




% -------------------------------------------- figure 6  -- CO Bin 2
figure6 = figure('Position',[563,100,942,982]);

tiledlayout(3,1,"TileSpacing","loose","Padding","compact");

fx1=nexttile;

plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.speed),'Color',[0 0 1])
fx1.YColor=[0 0 0];
fx1.YGrid="on";
ylabel('Vehicle Speed (mph)')

yyaxis right
plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.engineSpeed),'Color',[.7 .7 .7])
fx1.YColor=[0 0 0];
ylabel('Engine Speed (rpm)')


fx2=nexttile;

% --- CO mass flow
[xTime,xTimeCell]=getData(setIdx,udp(setIdx).pems.time);
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.coMassFlow);
plot(xTime,ydata)
ylabel(ydataC{2},'Interpreter','none')
fx2.YGrid='on';


fx3=nexttile;

% --- CO Mass Bin 2
plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.CO_Mass_Bin2)
ylabel('CO_Mass_Bin2  (gm)','Interpreter','none')
fx3.YGrid='on';

hold on

% ---
yyaxis right
plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.CO_BrakeSpec_Bin2_Cummulative)
ylabel('CO_BrakeSpec_Bin2_Cummulative  (gm/hp*hr)','Interpreter','none')


linkaxes([fx1 fx2 fx3],'x')
% cx3.YLim=[-10,4];
% legend('Normalized CO2','6% Bin 1 Limit','Bin Number','Interpreter','none','Location','northeastoutside')

% generate the image from figure, append to report
saveas(gcf,"bin2CO_image.png");

bin2COImg = Image("bin2CO_image.png");
bin2COImg.Width = "7.5in";
bin2COImg.Height = "8in";
bin2COImg.Style = [includeImg.Style {ScaleToFit}];

append(rpt, bin2COImg);



% ---7--------------------------------------------------------------------
% ----------------------- Header:  Bin2 HC (b2hc)
append(rpt, PageBreak());

% --------------- Table - Test Information Header
b2hcHd=Heading2("Test Information");
append(rpt,b2hcHd);

b2hcTabObj=headerTable;  % nested function
append(rpt,b2hcTabObj);


% --- Heading for Invalid Intervals
b2hcFig=Heading2("Figure:  Bin 2 HC");
append(rpt,b2hcFig);




% -------------------------------------------- figure 7  -- HC Bin 2
figure7 = figure('Position',[563,100,942,982]);

tiledlayout(3,1,"TileSpacing","loose","Padding","compact");

gx1=nexttile;

plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.speed),'Color',[0 0 1])
gx1.YColor=[0 0 0];
gx1.YGrid="on";
ylabel('Vehicle Speed (mph)')

yyaxis right
plot(vehData(1).data.(udp(setIdx).pems.time),vehData(1).data.(udp(setIdx).pems.engineSpeed),'Color',[.7 .7 .7])
gx1.YColor=[0 0 0];
ylabel('Engine Speed (rpm)')


gx2=nexttile;

% --- HC mass flow
[xTime,xTimeCell]=getData(setIdx,udp(setIdx).pems.time);
[ydata,ydataC]=getData(setIdx,udp(setIdx).pems.hcMassFlow);
plot(xTime,ydata)
ylabel(ydataC{2},'Interpreter','none')
gx2.YGrid='on';


gx3=nexttile;

% --- HC Mass Bin 2
plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.HC_Mass_Bin2)
ylabel('HC_Mass_Bin2  (gm)','Interpreter','none')
gx3.YGrid='on';

hold on

% ---
yyaxis right
plot(vehData(setIdx).binData.Time_BinAvg,vehData(setIdx).binData.HC_BrakeSpec_Bin2_Cummulative)
ylabel('HC_BrakeSpec_Bin2_Cummulative  (mg/hp*hr)','Interpreter','none')


linkaxes([gx1 gx2 gx3],'x')
% cx3.YLim=[-10,4];
% legend('Normalized CO2','6% Bin 1 Limit','Bin Number','Interpreter','none','Location','northeastoutside')

% generate the image from figure, append to report
saveas(gcf,"bin2HC_image.png");

bin2HCImg = Image("bin2HC_image.png");
bin2HCImg.Width = "7.5in";
bin2HCImg.Height = "8in";
bin2HCImg.Style = [includeImg.Style {ScaleToFit}];

append(rpt, bin2HCImg);





% ---------------  Close the report
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
        cellTab(3,2)={string(vehData(setIdx).logData.vehid)};
        cellTab(4,1)={"File Name"};
        cellTab(4,2)={string(vehData(setIdx).filename)};

        tabObj = Table(cellTab);
        tabObj.TableEntriesStyle = ...
            [tabObj.TableEntriesStyle {FontFamily("Arial"),FontSize("10pt"),InnerMargin("2pt")}];

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
%  end of main function testReportBin
end