%% Cooling data analysis
clear;clc
%
% THe role of this script is to analyze the cooling flows based on the
% measured values and on a number of assumptions from MS Birka. 

%% Loading previous calculations
addpath(genpath('D:\BoxSync\baldif\MATLAB\Utility functions'))
load('D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\energy_analysis.mat');
HET_constants
clearvars -except ME_load PARAM ME_mfr_fuel;
load('D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\raw_reading.mat');
clearvars AE_T_fuel_oil AE_T_lub_oil ME_pos_fuel_rack ME_rpm_TC ME_T_fuel_oil ME_T_lub_oil p_steam_boiler p_SWcooling T_fuel_tanks T_fuel_tanks_ref T_hot_water

%% 1 - HT cooling systems, ME
temp.x = [ME_load.ME1 ; ME_load.ME2 ; ME_load.ME3 ; ME_load.ME4] ;
temp.y1 = [T_HTcooling(:,1) ; T_HTcooling(:,2) ; T_HTcooling(:,1) ; T_HTcooling(:,2)] ;
temp.y2 = [ME_T_HTcooling.ME1(:,1) ; ME_T_HTcooling.ME2(:,1) ; ME_T_HTcooling.ME3(:,1) ; ME_T_HTcooling.ME4(:,1)] ;
temp.y3 = [ME_T_HTcooling.ME1(:,2) ; ME_T_HTcooling.ME2(:,2) ; ME_T_HTcooling.ME3(:,2) ; ME_T_HTcooling.ME4(:,2)] ;
store.load_selection = temp.x < 0.1 ;
store.load_ME = temp.x ; store.load_ME(store.load_selection) = [] ;
store.x_reg = 0.1:0.01:1 ;
store.HT(:,1) = temp.y1 ; 
store.HT(:,2) = temp.y2 ;
store.HT(:,3) = temp.y3 ;
store.HT(store.load_selection,:)  = [] ;
    figure
    plot(store.load_ME,store.HT,'x') ; xlabel('Engine load') ; ylabel('HT Temperature [K]') ; legend('Inlet','after JW cooler','after CAC cooler')
    hold on
    plot(store.x_reg,polyval(polyfit(store.load_ME,store.HT(:,1),2),store.x_reg),'k-',store.x_reg,polyval(polyfit(store.load_ME,store.HT(:,2),2),store.x_reg),'k-',store.x_reg,polyval(polyfit(store.load_ME,store.HT(:,3),2),store.x_reg),'k-')
    figure
    plot(store.load_ME,store.HT(:,2)-store.HT(:,1),'bx',store.load_ME,store.HT(:,3)-store.HT(:,2),'rx') ; xlabel('Engine load') ; ylabel('Temperature difference [K]') ; legend('JW cooler','CAC cooler')
    hold on
    plot(store.x_reg,polyval(polyfit(store.load_ME,store.HT(:,2)-store.HT(:,1),2),store.x_reg),'k-',store.x_reg,polyval(polyfit(store.load_ME,store.HT(:,3)-store.HT(:,2),2),store.x_reg),'k-')
clear temp ME_load T_HTcooling ME_T_HTcooling;

%% 2 - LT cooling systems, AE
temp.y1 = [T_LTcooling(:,1) ; T_LTcooling(:,2) ; T_LTcooling(:,1) ; T_LTcooling(:,2)] ;
temp.y2 = [ME_T_LTcooling.ME1(:,1) ; ME_T_LTcooling.ME2(:,1) ; ME_T_LTcooling.ME3(:,1) ; ME_T_LTcooling.ME4(:,1)] ;
store.LT(:,1) = temp.y1 ; 
store.LT(:,2) = temp.y2 ;
store.LT(store.load_selection,:)  = [] ;
    figure
    plot(store.load_ME,store.LT,'x') ; xlabel('Engine load') ; ylabel('LT Temperature [K]') ; legend('Inlet','after engine')
    figure
    plot(store.load_ME,store.LT(:,2)-store.LT(:,1),'bx') ; xlabel('Engine load') ; ylabel('Temperature difference [K]')
clear temp T_LTcooling ME_T_LTcooling;

%% 3 - Waste heat analysis
%% Initializing variables
store.mair = zeros(length(store.load_ME),7) ;
store.Tair = zeros(length(store.load_ME),7) ;

% Measured values
% Charge pressure
temp = [ME_p_charge_air.ME1(:,1) ; ME_p_charge_air.ME2(:,1) ; ME_p_charge_air.ME3(:,1) ; ME_p_charge_air.ME4(:,1)] ; temp(store.load_selection) = [] ;
store.pair = temp ; clear ME_p_charge_air
% Temperature in the engine room
temp = [T_ER ; T_ER ; T_ER ; T_ER] ; temp(store.load_selection) = [] ;
store.Tair(:,1) = temp ; clear T_ER
% Temperature after mixing
temp = [ME_T_eg.ME1(:,2) ; ME_T_eg.ME2(:,2) ; ME_T_eg.ME3(:,2) ; ME_T_eg.ME4(:,2)] ; temp(store.load_selection) = [] ;
store.Tair(:,7) = temp ; 
% Temperature in the exhaust receiver
temp = [ME_T_eg.ME1(:,1) ; ME_T_eg.ME2(:,1) ; ME_T_eg.ME3(:,1) ; ME_T_eg.ME4(:,1)] ; temp(store.load_selection) = [] ;
store.Tair(:,5) = temp ; clear ME_T_eg
% Engine speed (combinator diagram dependent)
temp = [ME_rpm.ME1 ; ME_rpm.ME2 ; ME_rpm.ME3 ; ME_rpm.ME4] ; temp(store.load_selection) = [] ;
store.rpm(:,1) = temp ; clear ME_rpm
% Air temperature in the air receiver
temp = [ME_T_charge_air.ME1 ; ME_T_charge_air.ME2 ; ME_T_charge_air.ME3 ; ME_T_charge_air.ME4] ; temp(store.load_selection) = [] ;
store.Tair(:,4) = temp ; clear ME_T_charge_air
% Fuel flow
temp = [ME_mfr_fuel.ME1 ; ME_mfr_fuel.ME2 ; ME_mfr_fuel.ME3 ; ME_mfr_fuel.ME4] ; temp(store.load_selection) = [] ;
store.mfr_fuel = temp ; clear ME_mfr_fuel

% Calculations
% Temperature after the compressor
store.Tair(:,2) = store.Tair(:,1) .* (1 + (store.pair(:,1).^(0.4/1.4) - 1) ./ polyval(PARAM.ME.POLY_PIN_2_ETA_IS,store.pair)) ;
% Mass flow rate to the engine is calculated based on the approximation of ideal gas conditions in the engine cylinders at max volume
store.mair(:,4) = PARAM.ME.V_MAX .* store.pair(:,1)*1e5 ./ PARAM.THERMO.R_AIR ./ store.Tair(:,4) .* store.rpm / 60 / 2 * PARAM.ETA.VOL * PARAM.ME.N_CYL ;
% Exhaust flow leaving the engine equal to sum of air and fuel flows
store.mair(:,5) = store.mair(:,4) + store.mfr_fuel ;

%     store.mair(:,6) = store.mair(:,5) ;
%     % Final supercalculation
%     store.mair(:,3) = (store.mair(:,6) .* PARAM.THERMO.CP_EG .* (store.Tair(:,5) - store.Tair(:,7)) - PARAM.THERMO.CP_AIR / PARAM.ETA.TC_MECH .* store.mair(:,4) .* (store.Tair(:,2) - store.Tair(:,1))) ./ ...
%         (PARAM.THERMO.CP_EG .* (store.Tair(:,7) - store.Tair(:,3)) + PARAM.THERMO.CP_AIR / PARAM.ETA.TC_MECH .* (store.Tair(:,2) - store.Tair(:,1))) ;
%     store.Tair(:,6) = store.Tair(:,5) - (store.mair(:,3)+store.mair(:,4) .* PARAM.THERMO.CP_AIR .* (store.Tair(:,2) - store.Tair(:,1))) ./ PARAM.ETA.TC_MECH ./ PARAM.THERMO.CP_EG ./ store.mair(:,6) ;
%     store.mair(:,1) = store.mair(:,3) + store.mair(:,4) ;
%     store.mair(:,7) = store.mair(:,3) + store.mair(:,6) ;
%     store.mair(:,2) = store.mair(:,1) ;
%     store.Tair(:,3) = store.Tair(:,2) ; 

store.Tair(:,6) = -(PARAM.THERMO.CP_AIR .* (store.Tair(:,2) - store.Tair(:,1)) .* (store.mair(:,5) .* store.Tair(:,5) - store.mair(:,4) .* store.Tair(:,3)) + store.mair(:,5) .* PARAM.THERMO.CP_EG .* PARAM.ETA.TC_MECH .* store.Tair(:,7) .* (store.Tair(:,5) - store.Tair(:,3))) ./ ...
    (PARAM.THERMO.CP_AIR .* store.mfr_fuel .* (store.Tair(:,2) - store.Tair(:,1)) - PARAM.THERMO.CP_EG .* PARAM.ETA.TC_MECH .* store.mair(:,5) .* (store.Tair(:,5) - store.Tair(:,3))) ;
store.mair(:,3) = (store.Tair(:,5) - store.Tair(:,6)) .* store.mair(:,5) ./ (store.Tair(:,6) - store.Tair(:,3)) ;
store.mair(:,1) = store.mair(:,3) + store.mair(:,4) ;
store.mair(:,6) = store.mair(:,3) + store.mair(:,5) ;
store.mair(:,7) = store.mair(:,6) ;
store.mair(:,2) = store.mair(:,1) ;
store.Tair(:,3) = store.Tair(:,2) ; 
%% Output - 1 Energy in the exhaust gas
Qdot.eg = PARAM.THERMO.CP_EG .* store.mair(:,7) .* (store.Tair(:,7) - store.Tair(:,1)) ;
Qdot.eg_160 = PARAM.THERMO.CP_EG .* store.mair(:,7) .* (store.Tair(:,7) - (273 + 160)) ;

% Charge air cooling, total
Qdot.cac = PARAM.THERMO.CP_AIR .* store.mair(:,4) .* (store.Tair(:,2) - store.Tair(:,4)) ;
% Remaining energy, total. Version 1
% Qdot.cooling = store.mfr_fuel * PARAM.THERMO.LHV - store.load_ME .* PARAM.ME.MCR - PARAM.THERMO.CP_EG .* store.mair(:,5) .* (store.Tair(:,5) - store.Tair(:,4)) ;
% Qdot.ht = Qdot.cooling .* polyval(PARAM.ME.POLY_LOAD_2_QDOT_HT,store.load_ME) ./ (polyval(PARAM.ME.POLY_LOAD_2_QDOT_HT,store.load_ME) + polyval(PARAM.ME.POLY_LOAD_2_QDOT_LT,store.load_ME)) ;
% Qdot.lt = Qdot.cooling - Qdot.ht ;
% Qdot.cac_ht = Qdot.ht .* (store.HT(:,3) - store.HT(:,2)) ./ (store.HT(:,3) - store.HT(:,1)) ;
% Qdot.cac_lt = Qdot.cac - Qdot.cac_ht ;
% Qdot.lo = Qdot.lt - Qdot.cac_lt ; 
% Qdot.jw = Qdot.ht - Qdot.cac_ht ;

% Remainin energy, version 2
Qdot.cac_ht = store.mair(:,4) .* PARAM.THERMO.CP_AIR .* (store.Tair(:,2) - store.HT(:,2)) .* 0.85 ; % Assuming 0.85 effectiveness
Qdot.cac_ht(Qdot.cac_ht < Qdot.cac * 0.05) = 0 ;
Qdot.cac_lt = Qdot.cac - Qdot.cac_ht ;
Qdot.cooling = store.mfr_fuel * PARAM.THERMO.LHV - store.load_ME .* PARAM.ME.MCR - PARAM.THERMO.CP_EG .* store.mair(:,7) .* (store.Tair(:,7) - store.Tair(:,1)) - PARAM.ME.RADIATION ;
Qdot.ht = Qdot.cooling .* polyval(PARAM.ME.POLY_LOAD_2_QDOT_HT,store.load_ME) ./ (polyval(PARAM.ME.POLY_LOAD_2_QDOT_HT,store.load_ME) + polyval(PARAM.ME.POLY_LOAD_2_QDOT_LT,store.load_ME)) ;
Qdot.lt = Qdot.cooling - Qdot.ht ;
Qdot.lo = Qdot.lt - Qdot.cac_lt ; 
Qdot.jw = Qdot.ht - Qdot.cac_ht ;
    figure
    plot(store.load_ME,[Qdot.jw Qdot.lo Qdot.cac_ht Qdot.cac_lt Qdot.eg],'x') ; xlabel('engine load') ; ylabel('Heat loss [kW]') ; legend('Jacke water cooling','Lub oil cooling','CAC (HT)','CAC (LT)','Exhaust gas')
    axis([0.1 1 -200 3000])

%% Output are 0 if engines are off
Qdot_eg_160(load<0.05) = 0 ;
Qdot_ht(load<0.05) = 0 ;

