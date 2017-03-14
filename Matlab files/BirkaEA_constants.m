%%%% CONSTANTS %%%%
%
%
%%% NOTES: 
% 1-All regression coefficients are given from the lowest to highest
% order. Therefore a(1) corresponds to a_0, a(2) to a_1 etc..
% 2-If not specified otherwise, values refer to the main engine

%% USER ASSUMPTIONS
HTHR_UTILISATION_FACTOR = 0.9 ; % How much of the heat in the HT cooling systems is actually available to heat recovery

%% GENERAL CONSTANTS
R_AIR = 8314 / 29 ; % Air gas constant
K_AIR = 1.4 ; % Air specific heat ratio
CP_AIR = 1.02 ; % Air specific heat [kJ/kgK] 
CP_EG = 1.08 ; % EG specific heat [kJ/kgK] 
CP_LO = 2.1 ; % Lubricating oil specific heat [kW/kgK]
CP_W = 4.187 ; % Water specifi heat [kW/kgK] 
RHO_W = 1000 ; % Water density [kg/m^3]
RHO_LO = 850 ; % Lubricating oil density, [kg/m3]
LHV = 41170 ; % Fuel energy content, [kJ/kg]
HHV = LHV * (1.0406 + 0.0144 * 0.1185 / 0.8794 * 12)  ;
LHV_MDO = 42230 ;
HHV_MDO = LHV_MDO * (1.0406 + 0.0144 * 0.1185 / 0.8794 * 12) * 1.01 ;
CP_HFO = 1.8 ; % Fuel specific heat, [kJ/kg]
T0_AVE = mean(T0) ; % Average seawater temperature [K]
RHO_HFO = mean([890 919 924 926 925 921 924 918 920 919 933]) ;
AIR_STOIC = 14.7 ;
ETA_VOL = 0.97 ;

%% STEAM PROPERTIES
H_STEAM_LS = 662 ;
H_STEAM_VS = 2754 ;
S_STEAM_LS = 1.9108 ;
S_STEAM_VS = 6.7766 ;
DH_STEAM = H_STEAM_VS - H_STEAM_LS ;
DS_STEAM = S_STEAM_VS - S_STEAM_LS ;
TSAT_STEAM = 430 ;


%% MAIN ENGINES
MCR_ME = 5890 ; % Main engines maximum power [kW]
RPM_DES_ME = 500 ;
ME_MFR_FUEL_DES_ISO = 1165 / 3600 * 186.1 / 197.6 ; % Fuel flow at 100% load at ISO conditions, in [kg/s]
% ME_POLY_FUEL_RACK_2_MFR_FUEL = polyfit([24 31 38 42 46]/46 , [336.3 587.8 836.6 953.1 1141]/3600 , 2) ; % Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
ME_POLY_FUEL_LOAD_2_BSFC_ISO = polyfit([336.3 587.8 836.6 953.1 1141]/1141 , [216.9 187.1 178.5 179.2 181.4] , 2) ; % Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
% ME_POLY_RPM_2_POWER = polyfitZero([315 397 454 474 500 516] , [1463 2925 4388 4973 5890 6435] , 3) ;
ME_POLY_RPM_2_ISO_BSFC = polyfit([315 397 454 474 500 516] , [mean([216.1 207.6 225.5 209.9]) 188.2 179.7 181.6 185 191.1] , 2) ;
ME_POLY_PCA_2_LOAD = [0.25/0.24 , 0     ;   0.2577 , 0.1438     ;   0.5 0] ;
ME_POLY_LOAD_2_ISO_BSFC = polyfit([0.25 0.5 0.75 0.85 1 1.1] , [mean([216.1 207.6 225.5 209.9]) 188.2 179.7 181.6 185 191.1] , 2) ;
ME_POLY_LOAD_2_QDOT_HT = polyfit([0.5 0.75 0.85 1] , [500 1000 1250 1650] , 2) ;
ME_POLY_LOAD_2_QDOT_LT = polyfit([0.5 0.75 0.85 1] , [800 1050 1200 1450] , 2) ;
ME_POLY_LOAD_2_EPS_CACHT = polyfit([0.5 0.75 0.85 1] , [0.922 0.902 0.876 0.871],1) ;
% ME_POLY_FUEL_RACK_2_MASS_FUEL_CYCLE = polyfit([0.233333 , 0.5 , 0.7 , 0.8 , 1],[0.01726 , 0.02435 , 0.03081 , 0.03397 , 0.03869],1) ;
ME_BSFC_ISO_DES = polyval(ME_POLY_LOAD_2_ISO_BSFC,1) ;
% Function handle that allows to calculate the fuel load
fuelRackEngineSpeed2loadfuel = @(r,n) (n / RPM_DES_ME) .* r ;
ME_BORE = 0.46 ; % Main engine bore
ME_STROKE = 0.58 ; % Main engine stroke
ME_N_CYL = 6 ; % Number of cylinders
ME_R_C = 14 ; % Assumption of compression ratio
ME_V_SW = ME_BORE^2 / 4 * pi * ME_STROKE ; % Swept volume
ME_V_MAX = ME_V_SW * ME_R_C / (ME_R_C - 1) ; % Maximum volume 
ME_MFR_LO = 120 * RHO_LO / 3600 ; % Mass flow rate of oil in each main engine
ME_MFR_LT = 120 * RHO_W / 3600 ; % Mass flow rate of LT cooling water
ME_MFR_HT = 120 * RHO_W / 3600 ; % Mass flow rate of LT cooling water
ME_POLY_PIN_2_ETA_IS = [-1.18e-2 , 8.74e-2 , 6.81e-1] ; % Polynoimial regression for isentropic efficiency of the compressor
ME_ETA_CORR = 1.05 ;
ETA_IS_TC_MAX = 0.85 ;
ETA_IS_TC = 0.8 ;
ETA_MECH_TC = 0.98 ; 
EPS_CAC_HTSTAGE = 0.85 ;
ETA_GB = 0.985 ;
ETA_SHAFT = 0.99 ;

%% AUXILIARY ENGINES
MCR_AE = 2760 ; % Auxiliary engines maximum power ;
RPM_DES_AE = 750 ; % Auxiliary engines design speed ;
% AE_POLY_FUEL_RACK_2_MFR_FUEL = polyfit([17 27 37 44.5 46]/46 , [336.3 587.8 836.6 953.1 1141]/3600 , 2) ; % Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
AE_POLY_LOAD_2_ISO_BSFC = polyfit([0.5 0.75 1] , [191 184 183]/183*190.6 , 2) ; % Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
AE_POLY_PIN_2_ETA_IS = [-1.18e-2 , 8.74e-2 , 6.81e-1] ;
AE_BORE = 0.32 ; % Main engine bore
AE_STROKE = 0.40 ; % Main engine stroke
AE_N_CYL = 6 ; % Number of cylinders
AE_V_SW = AE_BORE^2 / 4 * pi * AE_STROKE ; % Swept volume
AE_R_C = 14 ; % Assumption of compression ratio
AE_V_MAX = AE_V_SW * AE_R_C / (AE_R_C - 1) ; % Maximum volume
AE_MFR_LO = 70 * RHO_LO / 3600 ; % Mass flow rate of oil in each auxiliary engine
AE_QDOT_2_CAC_HT_100 = 351 ;
AE_QDOT_2_JW_100 = 414 ;
AE_QDOT_2_CAC_LT_100 = 433 ;
AE_QDOT_2_LOC_100 = 331 ;
AE_POLY_LOAD_2_QDOT_HT = polyfit([0.5 0.75 0.85 1] , [500 1000 1250 1650] * (AE_QDOT_2_CAC_HT_100 + AE_QDOT_2_JW_100) / 1650 , 2) ;
AE_POLY_LOAD_2_QDOT_LT = polyfit([0.5 0.75 0.85 1] , [800 1050 1200 1450] * (AE_QDOT_2_CAC_LT_100 + AE_QDOT_2_LOC_100) / 1450 , 2) ;
AE_POLY_LOAD_2_SHARE_CAC = polyfit([0 1] , [0 AE_QDOT_2_CAC_HT_100/(AE_QDOT_2_CAC_HT_100+AE_QDOT_2_CAC_LT_100)] , 1) ;
AE_MFR_LT = 60 * RHO_W / 3600 ; % Mass flow rate of LT cooling water
AE_MFR_HT = 60 * RHO_W / 3600 ; % Mass flow rate of HT cooling water
AE_ETA_CORR = 1.15 ;
AE_ETA_SG = 0.97 ;
%% MONTH LIMITS
% Months start from 01 December 2013 until 17 December 2014
MONTH_DAYS = [28 31 30 31 30 31 31 30 31 30 (16 + 19/24)] ;
for i = 1 : length(MONTH_DAYS)
    if i == 1
        MONTH_ID_LIMIT(i) = MONTH_DAYS(i) * 24 * 4 ;
    else
        MONTH_ID_LIMIT(i) = MONTH_ID_LIMIT(i-1) + MONTH_DAYS(i) * 24 * 4 ;
    end
end
MONTH_ID_LIMIT(length(MONTH_DAYS)) = MONTH_ID_LIMIT(length(MONTH_DAYS)) - 1 ;
DAY_LIMIT = zeros(floor(sum(MONTH_DAYS)),1) ;
DAY_LIMIT(1) = 1 ;
for idx = 2 : floor(sum(MONTH_DAYS))
    DAY_LIMIT(idx) = DAY_LIMIT(idx-1) + 24*4 ;
end
DAY_LIMIT(end+1) = length(P_aux) ;







%% TANK VOLUMES AND HEAT LOSS COEFFICIENTS
TANK_NAMES = {'A_T32CP' , 'A_T32CS' , 'A_T23P' , 'A_T23S' , 'A_T31CP' , 'A_T31CS' , 'A_T22CP'} ;
TANK_BREADTHS = [5.1 , 4.2 , 6.6 , 6.6 , 3.6 , 4.2 , 6.6] ;
TANK_WIDTHS = [2.4 , 4.2 , 15.24 , 15.24 , 4 , 3.2 , 1.6] ;
TANK_HEIGHS = [3.3 , 3.3 , 4.3 , 4.3 , 3.2 , 3.2 , 3.3] ;
TANK_LAMBDA = 0.1 ;
TANK_DELTA = 0.08 ;
save(char([folder_work 'tank_data.mat']),'TANK*')
for i = 1 : length(TANK_NAMES)
    TANK_HEAT_LOSS_COEFFICIENT(i) = calculatesTankHeatLosses(char(TANK_NAMES(i)),folder_work) ;
end

%% OTHER
ETA_BOILER = 0.9 ;
PHI_BOILER = 1.2 ; % Boiler excess air ratio
T_HT_MAX = 90 + 273 ; % Maximum temperature limit of the HT cooling systems AFTER the engines. 


%% OTHER
Edot_FWgen = 7.5 / 3600 * 2382 * 25 * 2; 


% Shaft generator efficiency regression
a_etaSG = [0.837816 0.429306 -0.531238 0.211382] ; 








%% HEAT DEMAND FROM THE DRAWINGS
HEAT_DEMAND_DESIGN.HOT_WATER = 1200 + 366 ;
HEAT_DEMAND_DESIGN.AC_PREHEAT = 3500 ;
HEAT_DEMAND_DESIGN.AC_REHEAT = 1780 ;
HEAT_DEMAND_DESIGN.HFO_TANK_HEATING_LT = 208 ;
HEAT_DEMAND_DESIGN.OTHER_TANKS = 138 ;
HEAT_DEMAND_DESIGN.SEPARATORS = 94 + 73 ;
HEAT_DEMAND_DESIGN.HFO_TANK_HEATING_HT = 271 ;
HEAT_DEMAND_DESIGN.MACHINERY_SPACE_HEATERS = 281 ;
HEAT_DEMAND_DESIGN.GALLEY = 602 ;

HEAT_DEMAND_CALCULATION.PASSENGERS_MAX = 1800 ;
HEAT_DEMAND_CALCULATION.CREW_MAX = 200 ;
HEAT_DEMAND_CALCULATION.PERSON_FREE_HEAT = 0.23 ;
HEAT_DEMAND_CALCULATION.T_HEAT_MIN = -15 ;
HEAT_DEMAND_CALCULATION.T_HEAT_MAX = 15 ;
    temp = polyfit([HEAT_DEMAND_CALCULATION.T_HEAT_MIN HEAT_DEMAND_CALCULATION.T_HEAT_MAX],[1 0],1) ;
HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M = temp(1) ;
HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q = temp(2) ; 
    clear temp
HEAT_DEMAND_CALCULATION.HOT_WATER_DEMAND_VECTOR = [0.1 , 0.1 , 0.1 , 0.1 , 0.7 , 1 , 1 , 1 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 0.5 , 0.7 , 0.7 , 1 , 1 , 1 , 0.5 , 0.5 , 0.3] ;
HEAT_DEMAND_CALCULATION.GALLEY_DEMAND_VECTOR = [0 , 0 , 0 , 0 ,	0 , 0 , 0.575 , 0.575 , 0.575 , 0.1 , 0.575 , 0.575 , 0.575 , 0.1 , 0.1 , 0.1 , 0.1 , 0.575 , 0.575 , 0.575 , 0.1 , 0.1 , 0.1 , 0.1] ;

%% Creating the time vectors
temp1 = [] ; temp2 = [] ;
for idx = 1 : length(HEAT_DEMAND_CALCULATION.HOT_WATER_DEMAND_VECTOR)
    temp1 = [temp1 ; HEAT_DEMAND_CALCULATION.HOT_WATER_DEMAND_VECTOR(idx) * ones(4,1)] ;
    temp2 = [temp2 ; HEAT_DEMAND_CALCULATION.GALLEY_DEMAND_VECTOR(idx) * ones(4,1)] ;
end
HEAT_DEMAND_CALCULATION.HOT_WATER_DEMAND_VECTOR_FULL = repmat(temp1,365,1) ;
    HEAT_DEMAND_CALCULATION.HOT_WATER_DEMAND_VECTOR_FULL(length(P_aux)+1:end) = [] ; % Eliminating extra values
HEAT_DEMAND_CALCULATION.GALLEY_DEMAND_VECTOR_FULL = repmat(temp2,365,1) ;
    HEAT_DEMAND_CALCULATION.GALLEY_DEMAND_VECTOR_FULL(length(P_aux)+1:end) = [] ; % Eliminating extra values
clear temp*

%% Reading/creating the number of passengers
temp = xlsread(char([folder_main 'Passengers_data.xlsx'])) ;
temp_pass = temp(:,1) ;
temp_crew = temp(:,2) ;
temp1 = temp_pass(1) * ones(4*16,1) ; % The dataset starts from midnight. We assume that passenger numbers change at 16 
temp2 = temp_crew(1) * ones(4*16,1) ; 
for idx = 2 : length(temp_pass)
    temp1 = [temp1 ; temp_pass(idx) * ones(4*24,1)] ;
    temp2 = [temp2 ; temp_crew(idx) * ones(4*24,1)] ;
end
number_passengers = temp1 ; number_passengers(length(P_aux)+1:end) = [] ;
number_crew = temp2 ; number_crew(length(P_aux)+1:end) = [] ;





