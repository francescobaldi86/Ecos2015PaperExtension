%%% Database description and data compiling


sheet_names = {'ME1' 'AE1' 'ME2' 'AE2' 'ME3' 'AE3' 'ME4' 'AE4' 'Other'} ;
ME_names = {'ME1' 'ME2' 'ME3' 'ME4'} ;
AE_names = {'AE1' 'AE2' 'AE3' 'AE4'} ;
for i = 1 : length(sheet_names)
    string_evaluate = char(['Main.' char(sheet_names(i)) ' = xlsread(''' char(folder_work) char(filename_input) ''',''' char(sheet_names(i)) ''') ;']) ;
    eval(string_evaluate) ;
    Main.(char(sheet_names(i))) = Main.(char(sheet_names(i)))(11:end,:) ;
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

%%% Main engines
ME_T_eg = structfun(@(x) x(:,1:2)+273.15 , database_ME , 'UniformOutput' , false) ; % Main engines, Exhaust temperatures (before and after TC)
ME_T_HTcooling = structfun(@(x) x(:,3:4)+273.15 , database_ME , 'UniformOutput' , false) ; % Main engines, HT cooling temperatures (before and after engine)
ME_T_LTcooling = structfun(@(x) x(:,5)+273.15 , database_ME , 'UniformOutput' , false) ; % Main engines, LT cooling temperature before the engine
ME_T_fuel_oil = structfun(@(x) x(:,6)+273.15 , database_ME , 'UniformOutput' , false) ; % Main engines, fuel oil temperature
ME_T_lub_oil = structfun(@(x) x(:,7:8)+273.15 , database_ME , 'UniformOutput' , false) ; % Main engines, lub oil temperatures
ME_p_charge_air = structfun(@(x) x(:,9)+1 , database_ME , 'UniformOutput' , false) ; % Main engines, charge air pressure
ME_T_charge_air = structfun(@(x) x(:,10)+273.15 , database_ME , 'UniformOutput' , false) ; % Main engines, charge air temperature (after cooler)
ME_rpm = structfun(@(x) x(:,11) , database_ME , 'UniformOutput' , false) ; % Main engines, engine speed
ME_pos_fuel_rack = structfun(@(x) x(:,12)/100 , database_ME , 'UniformOutput' , false) ; % Main engines, TC speed
ME_rpm_TC = structfun(@(x) x(:,12) , database_ME , 'UniformOutput' , false) ; % Main engines, TC speed
%%% Auxiliary engines
AE_T_eg = structfun(@(x) [mean(x(:,1:2),2) x(:,3)]+273.15 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, exhaust temperature (before and after TC)
AE_T_fuel_oil = structfun(@(x) x(:,4)+273.15 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, fuel oil temperature
AE_T_lub_oil = structfun(@(x) x(:,5)+273.15 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, lubricating oil temperature
AE_T_HTcooling = structfun(@(x) x(:,6:8)+273.15 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, HT cooling temperature
AE_T_LTcooling = structfun(@(x) x(:,9:11)+273.15 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, LT cooling temperature
AE_p_charge_air = structfun(@(x) x(:,12)+1 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, charge air pressure
AE_T_charge_air = structfun(@(x) x(:,13)+273.15 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, charge air temperature
AE_pos_fuel_rack = structfun(@(x) x(:,14)/100 , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, fuel rack position
AE_rpm = structfun(@(x) x(:,15) , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, engine speed
AE_power = structfun(@(x) x(:,16) , database_AE , 'UniformOutput' , false) ; % Auxiliary engines, engine power
%%% Other
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
% Temperatures after ExBo are included in the "exhaust gas temperture"
% structures
ME_T_eg.ME3(:,3) = database_other(:,23)+273.15 ;
AE_T_eg.AE1(:,3) = database_other(:,24)+273.15 ;
AE_T_eg.AE3(:,3) = database_other(:,25)+273.15 ;
ME_T_eg.ME2(:,3) = database_other(:,26)+273.15 ;
AE_T_eg.AE2(:,3) = database_other(:,27)+273.15 ;
AE_T_eg.AE4(:,3) = database_other(:,28)+273.15 ;
T_atm = database_other(:,29)+273.15 ; 
T_ER = mean(database_other(:,30:31),2)+273.15 ;

clear Main
clear database*

n_data = length(ship_speed) ;

%%%%%%%%%%%%%%%%%%%%%%
%%% EARLY ELABORATIONS
%%%%%%%%%%%%%%%%%%%%%%
T0 = T_sea_water ; % Reference temperature
    T0(isnan(T0)==1) = T_atm(isnan(T0)==1) ; % When no seawater temperature is available, reference temperature is the ambient air temperature
P_aux = AE_power.AE1 + AE_power.AE2 + AE_power.AE3 + AE_power.AE4 ; % Total auxiliary power demand

AE_T_eg.AE1(AE_T_eg.AE1(:,1) < 0,1) = 650 ;
AE_T_eg.AE1(AE_T_eg.AE1(:,2) < 0,2) = 550 ;

%% Some assumptions about storage tanks
% Settling tanks
T_fuel_tanks(:,5) = ones(n_data,1) * 85 + 273 ;
T_fuel_tanks(:,6) = ones(n_data,1) * 85 + 273 ;
% Storage tank
T_fuel_tanks(:,7) = ones(n_data,1) * 50 + 273 ;


