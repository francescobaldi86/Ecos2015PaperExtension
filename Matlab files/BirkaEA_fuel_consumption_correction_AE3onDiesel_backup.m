
%% Initializing some variables
temp_mfr_fuel = zeros(n_data,4) ;

%% Engine group 1
for j = 1 : n_data    
    %% ME 1
    engine_index = 1 ; % Number of the engine. ME1 has engine index = 1. AE2 has 2, etc.
    local_index = 1 ; % This is just to create a vector. ME1 has local index 1, ME3 has local index 2, AE1 has local index 3 and AE3 has local index 4
    if ME_on.(char(ME_names(engine_index)))(j) > 0  
        temp_load(local_index) = ME_rpm.(char(ME_names(engine_index)))(j) / RPM_DES_ME * ME_pos_fuel_rack.(char(ME_names(engine_index)))(j) ;
        temp_bsfc(local_index) = bsfcISOCorrection(ME_BSFC_ISO_DES , ME_T_LTcooling.(char(ME_names(engine_index)))(j) , ME_T_charge_air.(char(ME_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = temp_load(local_index) * temp_bsfc(local_index) / ME_BSFC_ISO_DES * ME_MFR_FUEL_DES_ISO ;
    end
    %% ME 3
    engine_index = 3 ;
    local_index = 2 ; 
    if ME_on.(char(ME_names(engine_index)))(j) > 0 
        temp_load(local_index) = ME_rpm.(char(ME_names(engine_index)))(j) / RPM_DES_ME * ME_pos_fuel_rack.(char(ME_names(engine_index)))(j) ;
        temp_bsfc(local_index) = bsfcISOCorrection(ME_BSFC_ISO_DES , ME_T_LTcooling.(char(ME_names(engine_index)))(j) , ME_T_charge_air.(char(ME_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = temp_load(local_index) * temp_bsfc(local_index) / ME_BSFC_ISO_DES * ME_MFR_FUEL_DES_ISO ;
    end  
    %% AE 1
    engine_index = 1 ;
    local_index = 3 ;
    if AE_on.(char(AE_names(engine_index)))(j) > 0 
        temp_load(local_index) = AE_power.(char(AE_names(engine_index)))(j) / MCR_AE ;
        temp_bsfc_ISO(local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
        temp_bsfc(local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(j) , AE_T_charge_air.(char(AE_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = AE_power.(char(AE_names(engine_index)))(j) * temp_bsfc(local_index) / 3.6e6 ;
    end
    %% AE 3
    engine_index = 3 ;
    local_index = 4 ;
    if AE_on.(char(AE_names(engine_index)))(j) > 0 
        temp_load(local_index) = AE_power.(char(AE_names(engine_index)))(j) / MCR_AE ;
        temp_bsfc_ISO(local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
        temp_bsfc(local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(j) , AE_T_charge_air.(char(AE_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = 0 ;
    end
    temp_mfr_fuel_calc(j) = sum(temp_mfr_fuel(j,:)) * 15 * 60 ;
    clear temp_load temp_bsfc temp_bsfc_ISO
end
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
    corr_factor(idx_day) = min(max(temp_mfr_fuel_daily_mes(idx_day) / temp_mfr_fuel_daily_calc (idx_day),0.8),1.5) ;
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
for j = 1 : n_data    
    %% ME 2
    engine_index = 2 ; % Number of the engine. ME1 has engine index = 1. AE2 has 2, etc.
    local_index = 1 ; % This is just to create a vector. ME1 has local index 1, ME3 has local index 2, AE1 has local index 3 and AE3 has local index 4
    if ME_on.(char(ME_names(engine_index)))(j) > 0  
        temp_load(local_index) = ME_rpm.(char(ME_names(engine_index)))(j) / RPM_DES_ME * ME_pos_fuel_rack.(char(ME_names(engine_index)))(j) ;
        temp_bsfc(local_index) = bsfcISOCorrection(ME_BSFC_ISO_DES , ME_T_LTcooling.(char(ME_names(engine_index)))(j) , ME_T_charge_air.(char(ME_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = temp_load(local_index) * temp_bsfc(local_index) / ME_BSFC_ISO_DES * ME_MFR_FUEL_DES_ISO ;
    end
    %% ME 4
    engine_index = 4 ;
    local_index = 2 ; 
    if ME_on.(char(ME_names(engine_index)))(j) > 0 
        temp_load(local_index) = ME_rpm.(char(ME_names(engine_index)))(j) / RPM_DES_ME * ME_pos_fuel_rack.(char(ME_names(engine_index)))(j) ;
        temp_bsfc(local_index) = bsfcISOCorrection(ME_BSFC_ISO_DES , ME_T_LTcooling.(char(ME_names(engine_index)))(j) , ME_T_charge_air.(char(ME_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = temp_load(local_index) * temp_bsfc(local_index) / ME_BSFC_ISO_DES * ME_MFR_FUEL_DES_ISO ;
    end  
    %% AE 2
    engine_index = 2 ;
    local_index = 3 ;
    if AE_on.(char(AE_names(engine_index)))(j) > 0 
        temp_load(local_index) = AE_power.(char(AE_names(engine_index)))(j) / MCR_AE ;
        temp_bsfc_ISO(local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
        temp_bsfc(local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(j) , AE_T_charge_air.(char(AE_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = AE_power.(char(AE_names(engine_index)))(j) * temp_bsfc(local_index) / 3.6e6 ;
    end
    %% AE 4
    engine_index = 4 ;
    local_index = 4 ;
    if AE_on.(char(AE_names(engine_index)))(j) > 0 
        temp_load(local_index) = AE_power.(char(AE_names(engine_index)))(j) / MCR_AE ;
        temp_bsfc_ISO(local_index) = polyval(AE_POLY_LOAD_2_ISO_BSFC,temp_load(local_index)) ;
        temp_bsfc(local_index) = bsfcISOCorrection(temp_bsfc_ISO(local_index) , AE_T_LTcooling.(char(AE_names(engine_index)))(j) , AE_T_charge_air.(char(AE_names(engine_index)))(j) , LHV , 0.8) ;
        temp_mfr_fuel(j,local_index) = AE_power.(char(AE_names(engine_index)))(j) * temp_bsfc(local_index) / 3.6e6 ;
    end
    temp_mfr_fuel_calc(j) = sum(temp_mfr_fuel(j,:)) * 15 * 60 ;
end
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
        
        
            
            
            
            
            
            
            


test = 0 ;