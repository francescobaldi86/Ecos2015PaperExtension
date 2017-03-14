%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Database description and data compiling
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% This script reads the original files downloaded by Fredrik Ahlgren on MS
% Birka and puts them into appropriately named variables.
% 
% No pre-processing is done at this stage, apart from converting units of
% measure (degC --> K, barg --> bar)


sheet_names = {'ME1' 'AE1' 'ME2' 'AE2' 'ME3' 'AE3' 'ME4' 'AE4' 'Other'} ;
ME_names = {'ME1' 'ME2' 'ME3' 'ME4'} ;
AE_names = {'AE1' 'AE2' 'AE3' 'AE4'} ;
for i = 1 : length(sheet_names)
    string_evaluate = char(['Main.' char(sheet_names(i)) ' = xlsread(''' char(folder_work) char(filename_input) ''',''' char(sheet_names(i)) ''') ;']) ;
    eval(string_evaluate) ;
    Main.(char(sheet_names(i))) = Main.(char(sheet_names(i)))(11:end,:) ;
end

variable_names = {'ME_Teg_bTC' , 'ME_Teg_aTC' , 'ME_Teg_aHRSG' , 'ME_Tht_bEng' , 'ME_Tht_aEng' , 'ME_Tlt_bEng' , ...
    'ME_Tfuel' , 'ME_Tlo_bEng' , 'ME_Tlo_aEng' , 'ME_pca' , 'ME_Tca' , 'ME_rpm' , 'ME_frp' , 'ME_rpmTC', ...
    'AE_Teg_bTC' , 'AE_Teg_aTC ' , 'AE_Teg_aHRSG' , 'AE_Tfuel' , 'AE_Tlo_aEng' , 'AE_Tht_bEng' , 'AE_Tht_aJWC' , ...
    'AE_Tht_aCAC' ,  'AE_Tlt_bEng' , 'AE_Tlt_aCAC' , 'AE_Tlt_bLOC' , 'AE_pca' , 'AE_Tca' , 'AE_frp' , 'AE_rpm' , 'AE_Power'} ;
for idx = 1 : length(variable_names)
    eval(char([char(variable_names(idx)) '= zeros(length(Main.Other(:,18)),1) ;'])) ;
end
%% Reassigning the original "Main" to three structures: Main engines, auxiliary engines, and "others"
% Other
database_other = Main.Other ;
% Main engines
database_ME.ME1 = Main.ME1 ;
database_ME.ME2 = Main.ME2 ;
database_ME.ME3 = Main.ME3 ;
database_ME.ME4 = Main.ME4 ;
% Auxiliary engines
database_AE.AE1 = Main.AE1 ;
database_AE.AE2 = Main.AE2 ;
database_AE.AE3 = Main.AE3 ;
database_AE.AE4 = Main.AE4 ;

%%%%%%% SELECTION OF FAIL MEASUREMENTS
% Here we take all possible "wrong" values and we eliminate the
% correspondent readings.


%% RAW READINGS
for idx = 1 : 4
    %% Main engines
    ME_Teg_aEng(:,idx) = database_ME.(char(ME_names(idx)))(:,1) + 273.15 ; % 1 - Exhaust gas temperature, before Turbocharger
    ME_Teg_aTC(:,idx) = database_ME.(char(ME_names(idx)))(:,2) + 273.15 ; % 2 - Exhaust gas temperature, after Turbocharger
    if (idx == 2) 
        ME_Teg_aHRSG(:,idx) = database_other(:,26) + 273.15 ; % 2bis - Exhaust gas temperature, after HRSG
    elseif (idx == 3)
        ME_Teg_aHRSG(:,idx) = database_other(:,23) + 273.15 ; % 2bis - Exhaust gas temperature, after HRSG
    else
        ME_Teg_aHRSG(:,idx) = ME_Teg_aTC(:,idx) ; % If there is no HRSG, the temperature before and after the HRSG is the same
    end
    ME_Tht_bEng(:,idx) = database_ME.(char(ME_names(idx)))(:,3) + 273.15 ; % 3 - HT cooling temperature, before the engine
    ME_Tht_aEng_R(:,idx) = database_ME.(char(ME_names(idx)))(:,4) + 273.15 ; % 4 - HT cooling temperature, after the engine
    ME_Tlt_bEng(:,idx) = database_ME.(char(ME_names(idx)))(:,5) + 273.15 ; % 5 - LT cooling temperature, before the engine
    ME_Tfuel(:,idx) = database_ME.(char(ME_names(idx)))(:,6) + 273.15 ; % 6 - Fuel oil temperature
    ME_Tlo_bEng(:,idx) = database_ME.(char(ME_names(idx)))(:,7) + 273.15 ; % 7 - Lubricating oil temperature, before the engine
    ME_Tlo_aEng(:,idx) = database_ME.(char(ME_names(idx)))(:,8) + 273.15 ; % 8 - Lubricating oil temperature, after the engine
    ME_pca(:,idx) = database_ME.(char(ME_names(idx)))(:,9) + 1.01235 ; % 9 - Charge air pressure
    ME_Tca(:,idx) = database_ME.(char(ME_names(idx)))(:,10) + 273.15 ; % 10 - Charge air temperature (after charge air cooler)
    ME_rpm(:,idx) = database_ME.(char(ME_names(idx)))(:,11) ; % 11 - Engine speed [rpm]
    ME_frp(:,idx) = database_ME.(char(ME_names(idx)))(:,12) / 100 ; % 12 - Fuel rack position
    ME_rpmTC(:,idx) = database_ME.(char(ME_names(idx)))(:,13) ; % 13 - Turbochager speed [rpm]
    
    %% Auxiliary engines
    AE_Teg_aEng(:,idx) = 0.5 * database_AE.(char(AE_names(idx)))(:,1) + 0.5 * database_AE.(char(AE_names(idx)))(:,2) + 273.15 ; % 1 - Exhaust gas temperature, before Turbocharger. The temperature is calculated as the average of two measurements
    AE_Teg_aTC(:,idx) = database_AE.(char(AE_names(idx)))(:,3) + 273.15 ; % 2 - Exhaust gas temperature, after Turbocharger
    if (idx == 1) 
        AE_Teg_aHRSG(:,idx) = database_other(:,24) + 273.15 ; % 2bis - Exhaust gas temperature, after HRSG
    elseif (idx == 2)
        AE_Teg_aHRSG(:,idx) = database_other(:,27) + 273.15 ; % 2bis - Exhaust gas temperature, after HRSG
    elseif (idx == 2)
        AE_Teg_aHRSG(:,idx) = database_other(:,25) + 273.15 ; % 2bis - Exhaust gas temperature, after HRSG
    else
        AE_Teg_aHRSG(:,idx) = database_other(:,28) + 273.15 ; % 2bis - Exhaust gas temperature, after HRSG
    end
    AE_Tfuel(:,idx) = database_AE.(char(AE_names(idx)))(:,4) + 273.15 ; % 4 - Fuel oil temperature
    AE_Tlo_aEng(:,idx) = database_AE.(char(AE_names(idx)))(:,5) + 273.15 ; % 5 - Lubricating oil temperature, after the engine
    AE_Tht_bEng(:,idx) = database_AE.(char(AE_names(idx)))(:,6) + 273.15 ; % 6 - HT cooling temperature, before the engine
    AE_Tht_aJWC(:,idx) = database_AE.(char(AE_names(idx)))(:,7) + 273.15 ; % 7 - HT cooling temperature, after the Jacket Water Cooler
    AE_Tht_aCAC(:,idx) = database_AE.(char(AE_names(idx)))(:,8) + 273.15 ; % 8 - HT cooling temperature, after the Charge Air Cooler
    AE_Tlt_bEng(:,idx) = database_AE.(char(AE_names(idx)))(:,9) + 273.15 ; % 9 - LT cooling temperature, before the engine
    AE_Tlt_aCAC(:,idx) = database_AE.(char(AE_names(idx)))(:,10) + 273.15 ; % 10 - LT cooling temperature, after the Charge Air Cooler
    AE_Tlt_bLOC(:,idx) = database_AE.(char(AE_names(idx)))(:,11) + 273.15 ; % 11 - LT cooling temperature, after the Lubricating Oil Cooler
    AE_pca(:,idx) = database_AE.(char(AE_names(idx)))(:,12) + 1.01235 ; % 12 - Charge air pressure
    AE_Tca(:,idx) = database_AE.(char(AE_names(idx)))(:,13) + 273.15 ; % 13 - Charge air temperature (after charge air cooler)
    AE_frp(:,idx) = database_AE.(char(AE_names(idx)))(:,14) / 100 ; % 14 - Fuel rack position
    AE_rpm(:,idx) = database_AE.(char(AE_names(idx)))(:,15) ; % 15 - Engine speed [rpm]
    AE_PowerEl(:,idx) = database_AE.(char(AE_names(idx)))(:,16) ; % 16 - Engine power [kW]
end

%% Other
T_fuel_tanks = database_other(:,1:4)+273.15 ; % Fuel tanks temperature
T_fuel_tanks_ref = database_other(:,5)+273.15 ; % Temperature in the empty fuel tank used as reference for heat losses
mfr_fuel = database_other(:,6:9) ; % Mass flow rate in the two meters (for ER 1/3 and ER 2/4)
p_SWcooling = database_other(:,10:11) ; % SW cooling pressure (1/3 and 2/4)
T_SWcooling = database_other(:,12:13)+273.15 ; % SW cooling temperature (1/3 and 2/4)
T_LTcooling = database_other(:,14:15)+273.15 ; % LT cooling temperature (1/3 and 2/4)
T_HTcooling = database_other(:,16:17)+273.15 ; % HT cooling temperature (1/3 and 2/4)
ship_speed = database_other(:,18) ; % Ship speed, in knots
T_sea_water = database_other(:,19)+273.15 ; % Sea water temperature
T_hot_water = database_other(:,20)+273.15 ; % Temperature of the hot water (???)
p_steam_boiler = database_other(:,21:22) ; % Pressure in the steam boilers
T_atm = database_other(:,29)+273.15 ; 
T_ER = mean(database_other(:,30:31),2)+273.15 ;

clear Main
clear database*

n_data = length(ship_speed) ;

T0 = T_sea_water ; % Reference temperature
    T0(isnan(T0)==1) = T_atm(isnan(T0)==1) ; % When no seawater temperature is available, reference temperature is the ambient air temperature
P_aux = sum(AE_PowerEl,2) ; % Total auxiliary power demand




