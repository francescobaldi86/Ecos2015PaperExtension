%% Calculating heat loss coefficients for all tanks
for i = 1 : length(TANK_NAMES)
    heat_loss_coefficients(i) = calculatesTankHeatLosses(char(TANK_NAMES(i)) , folder_work) ;
end
%% Calculating the heat loss for all tanks
for i = 1 : length(TANK_NAMES)
    energy_demand_fuel_tanks(:,i) = heat_loss_coefficients(i) * (T_fuel_tanks(:,i) - T_fuel_tanks_ref) * 1e-3;
    exergy_demand_fuel_tanks(:,i) = zeros(n_data,1) ;
end
energy.Qdem.bottomUp_fuel_tanks_total = sum(energy_demand_fuel_tanks,2) ;

%% Heat required for warming up the fuel
energy.Qdem.bottomUp_fuel_booster = sum(energy.ME.fuel_th,2) + sum(energy.AE.fuel_th,2) ;
exergy.Qdem.bottomUp_fuel_booster = sum(exergy.ME.fuel_th,2) + sum(exergy.AE.fuel_th,2) ;
            
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Heating - Method 2
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
energy.Qdem.bottomUp_hot_water = HEAT_DEMAND_DESIGN.HOT_WATER * (number_passengers / HEAT_DEMAND_CALCULATION.PASSENGERS_MAX + number_crew / HEAT_DEMAND_CALCULATION.CREW_MAX) .* HEAT_DEMAND_CALCULATION.HOT_WATER_DEMAND_VECTOR_FULL ;
%energy.demand.hfo_tank_heating_lt2 = HEAT_DEMAND_DESIGN.HFO_TANK_HEATING_LT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; % TO BE UPDATED
%energy.demand.hfo_tank_heating_ht2 = HEAT_DEMAND_DESIGN.HFO_TANK_HEATING_HT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; % TO BE UPDATED
energy.Qdem.bottomUp_other_tanks = HEAT_DEMAND_DESIGN.OTHER_TANKS * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; % TO BE UPDATED
energy.Qdem.bottomUp_ac_preheat = HEAT_DEMAND_DESIGN.AC_PREHEAT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) - (number_passengers + number_crew) * HEAT_DEMAND_CALCULATION.PERSON_FREE_HEAT - 0.25 * (energy.Qdem.bottomUp_fuel_tanks_total + energy.Qdem.bottomUp_other_tanks) ;
energy.Qdem.bottomUp_ac_preheat(energy.Qdem.bottomUp_ac_preheat<0) = 0 ; % If the calculated demand is below 0, it is assumed equal to 0
energy.Qdem.bottomUp_ac_reheat = HEAT_DEMAND_DESIGN.AC_REHEAT * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; 
energy.Qdem.bottomUp_ac_reheat(energy.Qdem.bottomUp_ac_reheat<0) = 0 ; % If the calculated demand is below 0, it is assumed equal to 0

energy.Qdem.bottomUp_separators = HEAT_DEMAND_DESIGN.SEPARATORS * ones(n_data,1) ; % Constant
energy.Qdem.bottomUp_machinery_space_heaters =HEAT_DEMAND_DESIGN.MACHINERY_SPACE_HEATERS * (HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_Q + HEAT_DEMAND_CALCULATION.TEMPERATURE_REGRESSION_M * (T_atm - 273)) ; 
energy.Qdem.bottomUp_galley = HEAT_DEMAND_DESIGN.GALLEY * (number_passengers / HEAT_DEMAND_CALCULATION.PASSENGERS_MAX + number_crew / HEAT_DEMAND_CALCULATION.CREW_MAX) .* HEAT_DEMAND_CALCULATION.GALLEY_DEMAND_VECTOR_FULL ;
% Total heat demand according to the "new" method
energy.Qdem.bottomUp_total_heat = energy.Qdem.bottomUp_hot_water + energy.Qdem.bottomUp_ac_preheat + energy.Qdem.bottomUp_ac_reheat + energy.Qdem.bottomUp_fuel_booster + energy.Qdem.bottomUp_fuel_tanks_total + energy.Qdem.bottomUp_other_tanks + energy.Qdem.bottomUp_separators + energy.Qdem.bottomUp_machinery_space_heaters + energy.Qdem.bottomUp_galley ;
% The contribution from the HRSG is considered to be the same
energy.Qdem.bottomUp_hrsgME = energy.Qdem.topDown_hrsgME ;
energy.Qdem.bottomUp_hrsgAE = energy.Qdem.topDown_hrsgAE ;
% The remaining part is assumed to be provided by the HRHT, if enough
energy.Qdem.bottomUp_hthr = max(min(energy.Qdem.bottomUp_total_heat-energy.Qdem.bottomUp_hrsgME-energy.Qdem.bottomUp_hrsgAE,((sum(energy.AE.ht,2) + sum(energy.ME.ht,2)) * HTHR_UTILISATION_FACTOR)),0) ; % All the heat from the HT available is used whenever possible
energy.Qdem.bottomUp_AB = max(energy.Qdem.bottomUp_total_heat-energy.Qdem.bottomUp_hrsgME-energy.Qdem.bottomUp_hrsgAE-energy.Qdem.bottomUp_hthr,0) ;