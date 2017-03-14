%%% MS/Birka Stockholm variable initialization file

for i = 1 : 4    
    %% Main Engines
    ME_power.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_load.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_bsfc.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_mfr_fuel.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_mfr_air.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_T_air.(char(ME_names(i))) = zeros(n_data,3) ;
    ME_mfr_eg.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_eta_tc_is.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_mfr_eg_tc.(char(ME_names(i))) = zeros(n_data,1) ;
    ME_mfr_eg_bypass.(char(ME_names(i))) = zeros(n_data,1) ;
    %% Auxiliary Engines
    AE_load.(char(AE_names(i))) = zeros(n_data,1) ;
    AE_bsfc.(char(AE_names(i))) = zeros(n_data,1) ;
    AE_mfr_fuel.(char(AE_names(i))) = zeros(n_data,1) ;
    AE_mfr_air.(char(AE_names(i))) = zeros(n_data,1) ;
    AE_T_air.(char(AE_names(i))) = zeros(n_data,3) ;
    AE_mfr_eg.(char(AE_names(i))) = zeros(n_data,1) ;
    AE_tc_eta_is.(char(AE_names(i))) = zeros(n_data,1) ;
    AE_mfr_eg_bypass.(char(AE_names(i))) = zeros(n_data,1) ;
    AE_mfr_eg_tc.(char(AE_names(i))) = zeros(n_data,1) ;
end

energy_field_names = {'ME' 'AE'} ;
for i = 1 : 2
    energy.(char(energy_field_names(i))).power = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).fuel_ch = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).fuel_th = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).fuel = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).air_1 = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).air_2 = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).air_3 = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).eg_1 = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).eg_2 = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).eg_3 = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).cac = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).ht = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).ht_lt = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).lt = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).cac_ht = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).cac_lt = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).jw = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).jw_ht = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).lo = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).lo_lt = zeros(n_data,4) ;
    energy.(char(energy_field_names(i))).hrsg = zeros(n_data,4) ;
end

