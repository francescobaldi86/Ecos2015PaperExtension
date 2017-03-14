% MS Birka data testing
%
% This script plots some data about MS Birka for testing
%
figure

%% 1 - Rack position versus speed
subplot(2,3,1)
plot([ME_rpm.ME1 ; ME_rpm.ME2 ; ME_rpm.ME3 ; ME_rpm.ME4] , [ME_pos_fuel_rack.ME1 ; ME_pos_fuel_rack.ME2 ; ME_pos_fuel_rack.ME3 ; ME_pos_fuel_rack.ME4],'rx')
xlabel('Engine speeed [rpm]')
ylabel('Fuel rack normalised position')

%% 2 - Fuel load versus speed
subplot(2,3,2)
plot([ME_rpm.ME1 ; ME_rpm.ME2 ; ME_rpm.ME3 ; ME_rpm.ME4] , [ME_load_fuel.ME1 ; ME_load_fuel.ME2 ; ME_load_fuel.ME3 ; ME_load_fuel.ME4],'rx')
xlabel('Engine speeed [rpm]')
ylabel('Load factor, fuel based')

%% 3 - Fuel flow versus speed
subplot(2,3,3)
plot([ME_rpm.ME1 ; ME_rpm.ME2 ; ME_rpm.ME3 ; ME_rpm.ME4] , [ME_mfr_fuel.ME1 ; ME_mfr_fuel.ME2 ; ME_mfr_fuel.ME3 ; ME_mfr_fuel.ME4],'rx')
xlabel('Engine speeed [rpm]')
ylabel('Fuel flow [kg/s]')

%% 4 - bsfc versus speed
subplot(2,3,4)
plot([ME_rpm.ME1 ; ME_rpm.ME2 ; ME_rpm.ME3 ; ME_rpm.ME4] , [ME_bsfc.ME1 ; ME_bsfc.ME2 ; ME_bsfc.ME3 ; ME_bsfc.ME4],'rx')
xlabel('Engine speeed [rpm]')
ylabel('BSFC [g/kWh]')

%% 5 - Power versus speed
subplot(2,3,5)
plot([ME_rpm.ME1 ; ME_rpm.ME2 ; ME_rpm.ME3 ; ME_rpm.ME4] , [ME_power.ME1 ; ME_power.ME2 ; ME_power.ME3 ; ME_power.ME4],'rx')
xlabel('Engine speeed [rpm]')
ylabel('Power [kW]')

%% 6 - Engine load versus speed
subplot(2,3,6)
plot([ME_rpm.ME1 ; ME_rpm.ME2 ; ME_rpm.ME3 ; ME_rpm.ME4] , [ME_load.ME1 ; ME_load.ME2 ; ME_load.ME3 ; ME_load.ME4],'rx')
xlabel('Engine speeed [rpm]')
ylabel('Load factor, power based')