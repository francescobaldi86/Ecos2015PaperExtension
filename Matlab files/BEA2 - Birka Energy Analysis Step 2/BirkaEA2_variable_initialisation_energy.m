%%% MS/Birka Stockholm variable initialization file

    %% Main Engines
    ME_power = zeros(n_data,4) ;
    ME_load = zeros(n_data,4) ;
    ME_bsfc = zeros(n_data,4) ;
    ME_bsfc_ISO = zeros(n_data,4) ;
    ME_Mfuel = zeros(n_data,4) ;
    ME_Mfuel_ISO = zeros(n_data,4) ;
    ME_Tca_acomp = zeros(n_data,4) ;
    ME_Mca_2eng = zeros(n_data,4) ;
    ME_Meg_aeng = zeros(n_data,4) ;
    ME_Mca_bypass = zeros(n_data,4) ;
    ME_Meg_TC = zeros(n_data,4) ;
    ME_Mca_bcomp = zeros(n_data,4) ;
    ME_Teg_bTC = zeros(n_data,4) ;
    %% Auxiliary Engines
    AE_load = zeros(n_data,1) ;
    AE_bsfc = zeros(n_data,1) ;
    AE_mfr_fuel = zeros(n_data,1) ;
    AE_mfr_air = zeros(n_data,1) ;
    AE_T_air = zeros(n_data,3) ;
    AE_mfr_eg = zeros(n_data,1) ;
    AE_tc_eta_is = zeros(n_data,1) ;
    AE_mfr_eg_bypass = zeros(n_data,1) ;
    AE_mfr_eg_tc = zeros(n_data,1) ;

energy_field_names = {'ME' 'AE'} ;
% for i = 1 : 2
%     energy.(char(energy_field_names(i))).power = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).fuel_ch = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).fuel_th = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).fuel = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).air_1 = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).air_2 = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).air_3 = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).eg_1 = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).eg_2 = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).eg_3 = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).cac = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).ht = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).ht_lt = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).lt = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).cac_ht = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).cac_lt = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).jw = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).jw_ht = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).lo = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).lo_lt = zeros(n_data,4) ;
%     energy.(char(energy_field_names(i))).hrsg = zeros(n_data,4) ;
% end

