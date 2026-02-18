function reportHoriba_Dilute(setIdx,filename,vehData,udp)

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
pg1Tab1(3,2)={string(vehData(setIdx).logData.vehicleID)};
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
pg1Tab2(1,3)={"  ---  "};
pg1Tab2(2,3)={"  ---  "};
pg1Tab2(3,3)={"  ---  "};
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

A=vehData(setIdx).scalarData.NOx_Gms_Per_Mile;
strNOx1=string(vehData(setIdx).scalarData.Properties.VariableUnits("NOx_Gms_Per_Mile"));
strNOx2=sprintf('%8.4f',A);

A=vehData(setIdx).scalarData.CO_Gms_Per_Mile;
strCO=string(vehData(setIdx).scalarData.Properties.VariableUnits("CO_Gms_Per_Mile"));
fspec='%8.4f';
strCO1=sprintf(fspec,A);

A=vehData(setIdx).scalarData.THC_Gms_Per_Mile;
strHCa=string(vehData(setIdx).scalarData.Properties.VariableUnits("THC_Gms_Per_Mile"));
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


if udp(setIdx).pems.pm2Active

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

end


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
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.speed);
line(vsAcAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

% --- ambient Temperature (amb)
ambAx=nexttile;
ambAx.YGrid="on";
[ydata,ambLega]=getData(setIdx,udp(setIdx).dyno.ambientAirT);
yunit=vehData(setIdx).data.Properties.VariableUnits{udp(setIdx).dyno.ambientAirT};
ydata=unitConvert(ydata,yunit,'F');
line(ambAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0.3098    0.5098    0.0471], 'LineWidth',1);
ylabel(ambLega{2},"Interpreter","none")


% ---- relative humidity (rh) and drytowet corr factor
rhAx=nexttile;
rhAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.rHumidity);
line(rhAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},"Interpreter","none")

yyaxis(rhAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.df);
line(rhAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'LineWidth',1,'LineStyle','-');
% rhAx.YLim=[0.5,1];
ylabel(ydataC{2},'Interpreter','none')

% ---- barometric pressure and altitude  (bar)
barAx=nexttile;
barAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.ambientAirP);
line(barAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},'Interpreter','none')


% --- get the xdata (time) just to get the x axis label xdataC{2}
[xdata,xdataC]=getData(setIdx,udp(setIdx).dyno.time);
xlabel(xdataC{2},"Interpreter","none")


% --- link axes in X direction
linkaxes([vsAcAx,ambAx,rhAx,barAx],'x')
% rhAx.YLim=[0.5,1];  %matlab bug - linkaxes resets YLim


% generate the image from figure, append to report
saveas(gcf,"ambient_image.png");

ambImg = Image("ambient_image.png");
ambImg.Width = "7in";
ambImg.Height = "7.25in";
ambImg.Style = [ambImg.Style {ScaleToFit}];

append(rpt, ambImg);

%%

% -----------------------------------------------------------------------
% ----------------------- New Figure:  Exhaust Flow (exh)
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

tiledlayout(3,1,'TileSpacing','compact');


% --- vehicle speed (vs)
vsExhAx=nexttile;
vsExhAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.speed);
line(vsExhAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);


exfAx=nexttile;
exfAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.cvsFlow);
line(exfAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},"Interpreter","none")

yyaxis(exfAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.dilAirFlow);
line(exfAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'LineWidth',1,'LineStyle','-');
% exfAx.YLim=[0.5,1];
ylabel(ydataC{2},'Interpreter','none')


texExhAx=nexttile;
texExhAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.exhaustFlow);
line(texExhAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'LineWidth',1,'LineStyle','-');
ylabel(ydataC{2},'Interpreter','none')

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

% --- link axes in X direction
linkaxes([vsExhAx,exfAx,texExhAx],'x')

% generate the image from figure, append to report
saveas(gcf,"exhFlow_image.png");

exhImg = Image("exhFlow_image.png");
exhImg.Width = "7in";
exhImg.Height = "7.25in";
exhImg.Style = [exhImg.Style {ScaleToFit}];

append(rpt, exhImg);


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
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.speed);
line(vsAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

% --- humidity correction factor (hcf)
hcfAx=nexttile;
hcfAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.kHumidity);
line(hcfAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0.3098    0.5098    0.0471], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% --- NOx concentration Corr. (nxc)
nxcAx=nexttile;
nxcAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.noxDiluteCorr);
line(nxcAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")


%  --- Cummulative NOx and NOx Mass Flow (nxm)
nxmAx=nexttile;
nxmAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.noxSum);
line(nxmAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(nxmAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.noxMassFlow);
line(nxmAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (nxmAx,'left')


% --- link axes in X direction
linkaxes([vsAx,hcfAx,nxcAx,nxmAx],'x')


% generate the image from figure, append to report
saveas(gcf,"pg2_nox_image.png");

nxImg = Image("pg2_nox_image.png");
nxImg.Width = "7in";
nxImg.Height = "7.25in";
nxImg.Style = [nxImg.Style {ScaleToFit}];

append(rpt,nxImg);



%%

% -----------------------------------------------------------------------
% ------------------------------- New Figure:  CO Summary (co)
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

tiledlayout(3,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsCoAx=nexttile;
vsCoAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.speed);
line(vsCoAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

% --- CO concentration (coc)
cocAx=nexttile;
cocAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.coDilute);
line(cocAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")


%  --- Cummulative CO and CO Mass Flow (com)
comAx=nexttile;
comAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.coSum);
line(comAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(comAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.coMassFlow);
line(comAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (comAx,'left')


% --- link axes in X direction
linkaxes([vsCoAx,cocAx,comAx],'x')


% generate the image from figure, append to report
saveas(gcf,"co_image.png");

coImg = Image("co_image.png");
coImg.Width = "7in";
coImg.Height = "7.25in";
coImg.Style = [coImg.Style {ScaleToFit}];

append(rpt,coImg);


%%
% -------------- Figure:  HC Summary (hc)

append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
hcHd=Heading2("Test Information");
append(rpt,hcHd);

hcTabObj=headerTable;
append(rpt,hcTabObj);



% --- Heading for Figure HC Summary
hcHdFig=Heading3("Figure:  Test Cycle HC");
append(rpt,hcHdFig);

%  --- Create the figure for CO emissions plots
hcFig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
hcFig1.InvertHardcopy="off";

tiledlayout(3,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsHcAx=nexttile;
vsHcAx.YGrid="on";
line(vsHcAx, vehData(setIdx).data.(udp(setIdx).dyno.time), vehData(setIdx).data.(udp(setIdx).dyno.speed),'Color', 'blue');
ylabel('Vehicle Speed (mph)')
title(vehData(setIdx).figtitle1);

% --- HC concentration and Exhaust Temperature (coc)
hcAx=nexttile;
hcAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.thcDilute);
line(hcAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")


%  --- Cummulative HC and HC Mass Flow (com)
hcmAx=nexttile;
hcmAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.thcSum);
line(hcmAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(hcmAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.thcMassFlow);
line(hcmAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (hcmAx,'left')


% --- link axes in X direction
linkaxes([vsHcAx,hcAx,hcmAx],'x')


% generate the image from figure, append to report
saveas(gcf,"hc_image.png");

hcImg = Image("hc_image.png");
hcImg.Width = "7in";
hcImg.Height = "7.25in";
hcImg.Style = [hcImg.Style {ScaleToFit}];

append(rpt,hcImg);

%%


% -------------- Figure:  CO2 Summary (co2)


append(rpt, PageBreak());

% --------------- Table - Test Information Header
% 
co2Hd=Heading2("Test Information");
append(rpt,co2Hd);

co2TabObj=headerTable;
append(rpt,co2TabObj);



% --- Heading for Figure CO Summary
co2HdFig=Heading3("Figure:  Test Cycle CO2");
append(rpt,co2HdFig);

%  --- Create the figure for CO2 emissions plots
co2Fig1=figure('Units','Normalized','Position',[0.00521,0.0392,0.53,0.89]);
co2Fig1.InvertHardcopy="off";

tiledlayout(3,1,'TileSpacing','compact');

% --- vehicle speed (vs)
vsCo2Ax=nexttile;
vsCo2Ax.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.speed);
line(vsCo2Ax, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,'Color', 'blue');
ylabel(ydataC{2},"Interpreter","none")
title(vehData(setIdx).figtitle1);

% --- CO2 concentration and Coolant Temperature (co2)
co2Ax=nexttile;
co2Ax.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.co2Dilute);
line(co2Ax, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")


%  --- Cummulative CO2 and CO2 Mass Flow (co2m)
co2mAx=nexttile;
co2mAx.YGrid="on";
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.co2Sum);
line(co2mAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0 0 0], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

yyaxis(co2mAx,'right')
[ydata,ydataC]=getData(setIdx,udp(setIdx).dyno.co2MassFlow);
line(co2mAx, vehData(setIdx).data.(udp(setIdx).dyno.time), ydata,...
    'Color', [0.8510    0.3255    0.0980], 'LineWidth',1);
ylabel(ydataC{2},"Interpreter","none")

% Label the X axis
xlabel(xdataC{2},"Interpreter","none")

yyaxis (co2mAx,'left')


% --- link axes in X direction
linkaxes([vsCo2Ax,co2Ax,co2mAx],'x')


% generate the image from figure, append to report
saveas(gcf,"co2_image.png");

co2Img = Image("co2_image.png");
co2Img.Width = "7in";
co2Img.Height = "7.25in";
co2Img.Style = [co2Img.Style {ScaleToFit}];

append(rpt,co2Img);



%%

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
%  end of main function testReportHD
end