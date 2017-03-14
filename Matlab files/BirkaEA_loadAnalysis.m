% Cooling data analysis
clear;clc

%% Loading previous calculations
load('D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\raw_reading.mat');
RPM_DES_ME = 500 ;
MCR_AE = 2760 ;

for i = 1 : 4
    ME_rpm.(char(ME_names(i)))(ME_pos_fuel_rack.(char(ME_names(i)))<0.1) = [] ;
    ME_p_charge_air.(char(ME_names(i)))(ME_pos_fuel_rack.(char(ME_names(i)))<0.1) = [] ;
    ME_pos_fuel_rack.(char(ME_names(i)))(ME_pos_fuel_rack.(char(ME_names(i)))<0.1) = [] ;
    ME_load_fuel1.(char(ME_names(i))) = ME_rpm.(char(ME_names(i))) ./ RPM_DES_ME .* ME_pos_fuel_rack.(char(ME_names(i))) ;
    ME_load_fuel2.(char(ME_names(i))) = ME_pos_fuel_rack.(char(ME_names(i))) ;
    ME_load_fuel3.(char(ME_names(i))) = ME_pos_fuel_rack.(char(ME_names(i))) .* ME_rpm.(char(ME_names(i))) ./ polyval(polyfit([0.25 0.5 0.75 0.85 1],[315 397 454 474 500],2),ME_pos_fuel_rack.(char(ME_names(i)))) ;
end
% %% Plot histograms for the fuel rack position of the MEs
% histogram(ME_pos_fuel_rack.ME1,0.1:0.02:1,'Normalization','probability') ; hold on ; histogram(ME_pos_fuel_rack.ME2,0.1:0.02:1,'Normalization','probability') ; histogram(ME_pos_fuel_rack.ME3,0.1:0.02:1,'Normalization','probability') ; histogram(ME_pos_fuel_rack.ME4,0.1:0.02:1,'Normalization','probability')
% xlabel('Fuel rack position') ; ylabel('Probability') ; legend('ME1','ME2','ME3','ME4')

% %% Plot histograms for the fuel rack position of the AEs 
% histogram(AE_pos_fuel_rack.AE1,0.1:0.02:1,'Normalization','probability') ; hold on ; histogram(AE_pos_fuel_rack.AE2,0.1:0.02:1,'Normalization','probability') ; histogram(AE_pos_fuel_rack.AE3,0.1:0.02:1,'Normalization','probability') ; histogram(AE_pos_fuel_rack.AE4,0.1:0.02:1,'Normalization','probability')
% xlabel('Fuel rack position') ; ylabel('Probability') ; legend('AE1','AE2','AE3','AE4')

% %% Plot AE fuel rack position versus load
% figure ; plot(AE_power.AE1/MCR_AE,AE_pos_fuel_rack.AE1,'x',AE_power.AE2/MCR_AE,AE_pos_fuel_rack.AE2,'x',AE_power.AE3/MCR_AE,AE_pos_fuel_rack.AE3,'x',AE_power.AE4/MCR_AE,AE_pos_fuel_rack.AE4,'x') ;
% axis([0 1 0 1]) ; xlabel('Engine load') ; ylabel('Fuel rack position') ; legend('AE1','AE2','AE3','AE4') ;

% %% Plot fuel rack position versus speed
% figure ; hold on ;
% for i = 1 : 4
%     plot(ME_rpm.(char(ME_names(i))),ME_pos_fuel_rack.(char(ME_names(i))),'x')
% end
% ylabel('Fuel rack position') ; xlabel('Engine speed [rpm]') ; legend('ME1','ME2','ME3','ME4')

%% Plot ME calculated load versus charge aire pressure
% % Method 1
% figure ; hold on ;
% for i = 1 : 4
%     plot(ME_load_fuel1.(char(ME_names(i))),ME_p_charge_air.(char(ME_names(i))),'x') ;
% end
% plot([0.25,0.5,0.75,0.85,1],[1.32 2.49 3.43 3.82 4.15],'ro','MarkerSize',20)
% title('Method 1') ;
% % Method 2
% figure ; hold on ;
% for i = 1 : 4
%     plot(ME_load_fuel2.(char(ME_names(i))),ME_p_charge_air.(char(ME_names(i))),'x') ;
% end
% plot([0.25,0.5,0.75,0.85,1],[1.32 2.49 3.43 3.82 4.15],'ro','MarkerSize',20)
% title('Method 2') ;
% % Method 3
% figure ; hold on ;
% for i = 1 : 4
%     plot(ME_load_fuel3.(char(ME_names(i))),ME_p_charge_air.(char(ME_names(i))),'x') ;
% end
% plot([0.25,0.5,0.75,0.85,1],[1.32 2.49 3.43 3.82 4.15],'ro','MarkerSize',20)
% title('Method 3') ;

%% Plot histograms for the newly calculated (method 3) load of the MEs
temp.xx = [ME_load_fuel3.ME1 ; ME_load_fuel3.ME2 ; ME_load_fuel3.ME3 ; ME_load_fuel3.ME4] ; 
temp.yy = [ME_p_charge_air.ME1 ; ME_p_charge_air.ME2 ; ME_p_charge_air.ME3 ; ME_p_charge_air.ME4] ; 
figure
histogram(temp.xx,'Normalization','probability') 
xlabel('Load') ; ylabel('Probability')



