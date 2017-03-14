
%% Initializing some variables
temp_mfr_fuel = zeros(n_data,4) ;

%% Engine group 1
    %% ME 1
    engine_index = 1 ; % Number of the engine. ME1 has engine index = 1. AE2 has 2, etc.
    local_index = 1 ; % This is just to create a vector. ME1 has local index 1, ME3 has local index 2, AE1 has local index 3 and AE3 has local index 4
    temp_load(:,local_index) = fuelRackEngineSpeed2loadfuel(ME_pos_fuel_rack.(char(ME_names(engine_index))) , ME_rpm.(char(ME_names(engine_index))))  .* ME_on.(char(ME_names(engine_index))) ;
    temp_bsfc_iso(:,local_index) = polyval(ME_POLY_FUEL_LOAD_2_BSFC_ISO,temp_load(:,local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_iso(:,local_index) , ME_T_LTcooling.(char(ME_names(engine_index))) , ME_T_charge_air.(char(ME_names(engine_index))) , LHV , 0.8)  .* ME_on.(char(ME_names(engine_index))) ;
    temp_mfr_fuel(:,local_index) = temp_load(:,local_index) .* temp_bsfc(:,local_index) ./ temp_bsfc_iso(:,local_index) .* ME_MFR_FUEL_DES_ISO ;
    %% ME 3
    engine_index = 3 ;
    local_index = 2 ; 
    temp_load(:,local_index) = fuelRackEngineSpeed2loadfuel(ME_pos_fuel_rack.(char(ME_names(engine_index))) , ME_rpm.(char(ME_names(engine_index)))) .* ME_on.(char(ME_names(engine_index)))  ;
    temp_bsfc_iso(:,local_index) = polyval(ME_POLY_FUEL_LOAD_2_BSFC_ISO,temp_load(:,local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_iso(:,local_index) , ME_T_LTcooling.(char(ME_names(engine_index))) , ME_T_charge_air.(char(ME_names(engine_index))) , LHV , 0.8)  .* ME_on.(char(ME_names(engine_index))) ;
    temp_mfr_fuel(:,local_index) = temp_load(:,local_index) .* temp_bsfc(:,local_index) ./ temp_bsfc_iso(:,local_index) .* ME_MFR_FUEL_DES_ISO ;
    %% AE 1
    engine_index = 1 ;
    local_index = 3 ;
    temp_load(:,local_index) = AE_power.(char(AE_names(engine_index))) / MCR_AE  .* AE_on.(char(AE_names(engine_index))) ;
    temp_bsfc_ISO(:,local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(:,1) , AE_T_charge_air.(char(AE_names(engine_index))) , LHV , 0.8) ;
    temp_mfr_fuel(:,local_index) = AE_power.(char(AE_names(engine_index))) .* temp_bsfc(:,local_index) ./ 3.6e6  .* AE_on.(char(AE_names(engine_index))) ;
    %% AE 3
    engine_index = 3 ;
    local_index = 4 ;
    temp_load(:,local_index) = AE_power.(char(AE_names(engine_index))) / MCR_AE  .* AE_on.(char(AE_names(engine_index))) ;
    temp_bsfc_ISO(:,local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(:,1) , AE_T_charge_air.(char(AE_names(engine_index))) , LHV , 0.8) ;
    % temp_mfr_fuel(:,local_index) = 0 ;
    temp_mfr_fuel(:,local_index) = AE_power.(char(AE_names(engine_index))) .* temp_bsfc(:,local_index) ./ 3.6e6  .* AE_on.(char(AE_names(engine_index))) ;

    temp_mfr_fuel_calc = sum(temp_mfr_fuel,2) * 15 * 60 ;

%% Creating a super-big vector with index for the end of each day of the year, with the corresponding fuel consumption. 
day_limits = (0 : 1 : sum(MONTH_DAYS)) * 24 * 4 ;
day_limits(1) = 1 ;
day_limits(end) = day_limits(end) - 1 ;
MONTH_NAMES = {'Februari' 'Mars' 'April' 'Maj' 'Juni' 'Juli' 'Augusti' 'September' 'Oktober' 'November' 'December'} ;
temp_mfr_fuel_daily_mes = [] ;
for idx_month = 1 : length(MONTH_DAYS)
    range_fuel_consumption_excel = char(['b10' , ':b' num2str(floor(MONTH_DAYS(idx_month)+10-1))]) ;
    temp_mfr_fuel_daily_mes = [temp_mfr_fuel_daily_mes ; xlsread(char(['C:\Users\baldif\Dropbox\ECOS - Exergy Cruise Ship\Logdata 1 year\2014\förbrukningar och timmar ' char(MONTH_NAMES(idx_month)) ' 2014.xlsx']),'Bunker och timmar',range_fuel_consumption_excel)] ;
end

for idx_day = 1 : length(day_limits)-1
    temp_mfr_fuel_daily_calc(idx_day) = sum(temp_mfr_fuel_calc(day_limits(idx_day):day_limits(idx_day+1))) ;
    corr_factor(idx_day) = min(max(temp_mfr_fuel_daily_mes(idx_day) / temp_mfr_fuel_daily_calc (idx_day),0.85),1.3) ;
    correction_factor.ME1(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
    correction_factor.AE1(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
    correction_factor.ME3(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
    correction_factor.AE3(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
end

clear temp*
clear corr_factor

%% Initializing some variables
temp_mfr_fuel = zeros(n_data,4) ;

%% Engine group 2
   
    %% ME 2
    engine_index = 2 ; % Number of the engine. ME1 has engine index = 1. AE2 has 2, etc.
    local_index = 1 ; % This is just to create a vector. ME1 has local index 1, ME3 has local index 2, AE1 has local index 3 and AE3 has local index 4
    temp_load(:,local_index) = fuelRackEngineSpeed2loadfuel(ME_pos_fuel_rack.(char(ME_names(engine_index))) , ME_rpm.(char(ME_names(engine_index))))  .* ME_on.(char(ME_names(engine_index))) ;
    temp_bsfc_iso(:,local_index) = polyval(ME_POLY_FUEL_LOAD_2_BSFC_ISO,temp_load(:,local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_iso(:,local_index) , ME_T_LTcooling.(char(ME_names(engine_index))) , ME_T_charge_air.(char(ME_names(engine_index))) , LHV , 0.8)  .* ME_on.(char(ME_names(engine_index))) ;
    temp_mfr_fuel(:,local_index) = temp_load(:,local_index) .* temp_bsfc(:,local_index) ./ temp_bsfc_iso(:,local_index) .* ME_MFR_FUEL_DES_ISO ;
    %% ME 4
    engine_index = 4 ;
    local_index = 2 ; 
    temp_load(:,local_index) = fuelRackEngineSpeed2loadfuel(ME_pos_fuel_rack.(char(ME_names(engine_index))) , ME_rpm.(char(ME_names(engine_index))))  .* ME_on.(char(ME_names(engine_index))) ;
    temp_bsfc_iso(:,local_index) = polyval(ME_POLY_FUEL_LOAD_2_BSFC_ISO,temp_load(:,local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_iso(:,local_index) , ME_T_LTcooling.(char(ME_names(engine_index))) , ME_T_charge_air.(char(ME_names(engine_index))) , LHV , 0.8)  .* ME_on.(char(ME_names(engine_index))) ;
    temp_mfr_fuel(:,local_index) = temp_load(:,local_index) .* temp_bsfc(:,local_index) ./ temp_bsfc_iso(:,local_index) .* ME_MFR_FUEL_DES_ISO ;
    %% AE 2
    engine_index = 2 ;
    local_index = 3 ;
    temp_load(:,local_index) = AE_power.(char(AE_names(engine_index))) / MCR_AE  .* AE_on.(char(AE_names(engine_index))) ;
    temp_bsfc_ISO(:,local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(:,1) , AE_T_charge_air.(char(AE_names(engine_index))) , LHV , 0.8) ;
    temp_mfr_fuel(:,local_index) = AE_power.(char(AE_names(engine_index))) .* temp_bsfc(:,local_index) ./ 3.6e6  .* AE_on.(char(AE_names(engine_index))) ;
    %% AE 4
    engine_index = 4 ;
    local_index = 4 ;
    temp_load(:,local_index) = AE_power.(char(AE_names(engine_index))) / MCR_AE  .* AE_on.(char(AE_names(engine_index))) ;
    temp_bsfc_ISO(:,local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
    temp_bsfc(:,local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(:,1) , AE_T_charge_air.(char(AE_names(engine_index))) , LHV , 0.8) ;
    temp_mfr_fuel(:,local_index) = AE_power.(char(AE_names(engine_index))) .* temp_bsfc(:,local_index) ./ 3.6e6  .* AE_on.(char(AE_names(engine_index))) ;
    
    temp_mfr_fuel_calc = sum(temp_mfr_fuel,2) * 15 * 60 ;

    %% Creating a super-big vector with index for the end of each day of the year, with the corresponding fuel consumption. 
temp_mfr_fuel_daily_mes = [] ;
for idx_month = 1 : length(MONTH_DAYS)
    range_fuel_consumption_excel = char(['f10' , ':f' num2str(floor(MONTH_DAYS(idx_month)+10-1))]) ;
    temp_mfr_fuel_daily_mes = [temp_mfr_fuel_daily_mes ; xlsread(char(['C:\Users\baldif\Dropbox\ECOS - Exergy Cruise Ship\Logdata 1 year\2014\förbrukningar och timmar ' char(MONTH_NAMES(idx_month)) ' 2014.xlsx']),'Bunker och timmar',range_fuel_consumption_excel)] ;
end

for idx_day = 1 : length(day_limits)-1
    temp_mfr_fuel_daily_calc(idx_day) = sum(temp_mfr_fuel_calc(day_limits(idx_day):day_limits(idx_day+1))) ;
    corr_factor(idx_day) = min(max(temp_mfr_fuel_daily_mes(idx_day) / temp_mfr_fuel_daily_calc (idx_day),0.8),1.5) ;
    correction_factor.ME2(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
    correction_factor.AE2(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
    correction_factor.ME4(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
    correction_factor.AE4(day_limits(idx_day):day_limits(idx_day+1),1) = corr_factor(idx_day) ;
end

clear temp*
clear corr_factor
        
        
            
            
