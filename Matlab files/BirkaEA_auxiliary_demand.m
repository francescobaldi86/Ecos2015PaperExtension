%%% BirkaEA_auxiliary_demand
%
% This script summarizes the auxiliary power & heat demand

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Heating   %%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Here we have two choices: either we lose heat from the whole tank, or
% just from the part filled in with liquid. 
%% Calculating heat loss coefficients for all tanks
for i = 1 : length(TANK_NAMES)
    heat_loss_coefficients(i) = calculatesTankHeatLosses(char(TANK_NAMES(i)) , folder_work) ;
end
%% Calculating the heat loss for all tanks
for i = 1 : length(TANK_NAMES)
            energy.demand.fuel_tanks(:,i) = heat_loss_coefficients(i) * (T_fuel_tanks(:,i) - T_fuel_tanks_ref) * 1e-3;
            exergy.demand.fuel_tanks(:,i) = zeros(n_data,1) ;
end
%% Heat required for warming up the fuel
            energy.demand.fuel_booster = sum(energy.ME.fuel_th,2) + sum(energy.AE.fuel_th,2) ;
            exergy.demand.fuel_booster = sum(exergy.ME.fuel_th,2) + sum(exergy.AE.fuel_th,2) ;
%% Boilers
% I basically assign the boilers only to time spent in port. Assumption...
load(char([folder_work 'fuel_consumption_daily.mat'])) ;
for i = 1 : length(Daily_fuel_consumption) % the i index is 1 per day
    boiler_running_hours(i) = sum(OM(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) == 1) ; % Amount of hours on the i-th day spent in port
    boiler_mfr(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) = (OM(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) ==1) .* (Daily_fuel_consumption(i,2) + Daily_fuel_consumption(i,4)) / boiler_running_hours(i) / 15 / 60 ;
    heat_total(i) = (Daily_fuel_consumption(i,2) + Daily_fuel_consumption(i,4)) / boiler_running_hours(i) / 15 / 60 * LHV * ETA_BOILER + sum(sum(energy.AE.hrsg(DAY_LIMIT(i) : DAY_LIMIT(i+1),:))) / 15 / 60 + 500 ;
        energy.demand.total_heat(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) = heat_total(i) ;
end

        

%% Total heating
% Sum up of producers
            energy.demand.boiler_heat = boiler_mfr * LHV * ETA_BOILER ;
            energy.demand.hrsg = sum(energy.ME.hrsg,2) + sum(energy.AE.hrsg,2) ;
            energy.demand.boiler_fuel = boiler_mfr * LHV ;
% Calculating energy demand fulfilled by the HT systems
            energy.demand.heat_ht = energy.demand.total_heat - energy.demand.hrsg - energy.demand.boiler_heat ;
% Consumers            
            energy.demand.fuel_tanks_total = sum(energy.demand.fuel_tanks,2) ;
            energy.demand.NOT_fuel_heating = energy.demand.total_heat - energy.demand.fuel_tanks_total - energy.demand.fuel_booster ;           
            energy.demand.boiler_waste = energy.demand.boiler_fuel - energy.demand.boiler_heat ;
     boiler_mfr_air = boiler_mfr * AIR_STOIC * PHI_BOILER ;
     T_after_boiler = T_atm + energy.demand.boiler_waste / CP_EG ./ boiler_mfr_air ;
 % Exergy    
            exergy.demand.boiler_fuel = boiler_mfr * HHV ;
 mfr_steam_boiler = energy.demand.boiler_heat / 2100 ;
            exergy.demand.boiler_heat = mfr_steam_boiler .* ((2754 - 662) - T0 * (6.7766 - 1.9108)) ;
            exergy.demand.hrsg = sum(exergy.ME.hrsg,2) + sum(exergy.AE.hrsg,2) ;
            exergy.demand.boiler_waste = energy.demand.boiler_waste - boiler_mfr_air .* CP_EG .* T0 .* log(T_after_boiler ./ T0) ;
            exergy.demand.boiler_waste(isnan(exergy.demand.boiler_waste)) = 0 ;
% Consumers            
            exergy.demand.fuel_tanks_total = zeros(n_data,1) ;
            exergy.demand.NOT_fuel_heating = zeros(n_data,1) ;
            
            
            
            
            
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Heating - Method 2
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        energy.demand.hot_water2 = HEAT_DEMAND_DESIGN.HOT_WATER * (number_passengers / HEAT_DEMAND_CALCULATION.PASSENGERS_MAX + number_crew / HEAT_DEMAND_CALCULATION.CREW_MAX) .* HEAT_DEMAND_CALCULATION.HOT_WATER_DEMAND_VECTOR_FULL ;
        energy.demand.hfo_tank_heating_lt2 = HEAT_DEMAND_DESIGN.HFO_TANK_HEATING_LT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; % TO BE UPDATED
        energy.demand.hfo_tank_heating_ht2 = HEAT_DEMAND_DESIGN.HFO_TANK_HEATING_HT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; % TO BE UPDATED
        energy.demand.other_tanks2 = HEAT_DEMAND_DESIGN.OTHER_TANKS * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; % TO BE UPDATED
        energy.demand.ac_preheat2 = HEAT_DEMAND_DESIGN.AC_PREHEAT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) - (number_passengers + number_crew) * HEAT_DEMAND_CALCULATION.PERSON_FREE_HEAT - 0.25 * (energy.demand.hfo_tank_heating_lt2 + energy.demand.hfo_tank_heating_ht2 + energy.demand.other_tanks2) ;
            energy.demand.ac_preheat2(energy.demand.ac_preheat2<0) = 0 ; % If the calculated demand is below 0, it is assumed equal to 0
        energy.demand.ac_reheat2 = HEAT_DEMAND_DESIGN.AC_REHEAT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; 
            energy.demand.ac_reheat2(energy.demand.ac_reheat2<0) = 0 ; % If the calculated demand is below 0, it is assumed equal to 0
        
        energy.demand.separators2 = HEAT_DEMAND_DESIGN.SEPARATORS ; % Constant
        energy.demand.machinery_space_heaters2 =HEAT_DEMAND_DESIGN.MACHINERY_SPACE_HEATERS * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; 
        energy.demand.galley2 = HEAT_DEMAND_DESIGN.GALLEY * (number_passengers / HEAT_DEMAND_CALCULATION.PASSENGERS_MAX + number_crew / HEAT_DEMAND_CALCULATION.CREW_MAX) .* HEAT_DEMAND_CALCULATION.GALLEY_DEMAND_VECTOR_FULL ;
        % Total heat demand according to the "new" method
        energy.demand.total_heat2 = energy.demand.hot_water2 + energy.demand.ac_preheat2 + energy.demand.ac_reheat2 + energy.demand.hfo_tank_heating_lt2 + energy.demand.hfo_tank_heating_ht2 + energy.demand.other_tanks2 + energy.demand.separators2 + energy.demand.machinery_space_heaters2 + energy.demand.galley2 ;
        % Heat repartition in this case
        energy.demand.hrsg2 = energy.demand.hrsg ;
        % energy.demand.heat_ht2 = max(sum(energy.ME.ht) ;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Power demand       %%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Propulsion power
            energy.demand.propulsion = sum(energy.ME.power,2) ;
            energy.demand.auxiliary_power = sum(energy.AE.power,2) ;
            energy.demand.thrusters = P_thruster ;
            exergy.demand.propulsion = sum(energy.ME.power,2) ;
            exergy.demand.auxiliary_power = sum(energy.AE.power,2) ;
            exergy.demand.thrusters = P_thruster ;