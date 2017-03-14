%%% MS/Birka Stockholm variable initialization file

exergy_field_names = {'ME' 'AE'} ;
for i = 1 : 2
    exergy.(char(exergy_field_names(i))).Power = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).fuel_ch = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).fuel_th = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).fuel = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ca_bcomp = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ca_acomp = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ca_2eng = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ca_2cac = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).air_bypass = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ca_incac = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).eg_aEng = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).eg_bTC = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).eg_aTC = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).hrsg = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).steam_in = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).steam_out = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).eg_aHRSG = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).lo_bEng = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).jwEng = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ht_bEng = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ht_ajwc = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).ht_acac = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).lt_bEng = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).lt_acac = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).lo_aEng = zeros(n_data,4) ;
    exergy.(char(exergy_field_names(i))).lt_aloc = zeros(n_data,4) ;    
end