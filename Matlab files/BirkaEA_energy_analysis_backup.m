%% BirkaEA_main_engines_efficiency %%

% Initialising variables for speed
BirkaEA_variable_initialisation_energy 

% Correction factor for main / auxiliary engines power and load based on
% the comparison with the fuel meter
% BirkaEA_fuel_consumption_correction_AE3onDiesel
%% NOTE: THE CORRECTION IS FIXED TO 1.15 TO AVOID STRANGE THINGS
%% THE ANALYSIS IS BASED ON THE ABOVE SCRIPT
% See the constant ME_ETA_CORR, AE_ETA_CORR

for i = 1 : 4
    %% Main engines
    %% Power - fuel flow - efficiency
    ME_load_fuel.(char(ME_names(i))) = ME_pos_fuel_rack.(char(ME_names(i))) .* ME_rpm.(char(ME_names(i))) ./ polyval(polyfit([0.295 0.515 0.735 0.835 1],[315 397 454 474 500],2),ME_pos_fuel_rack.(char(ME_names(i)))) .* ME_on.(char(ME_names(i))) ;
    ME_mfr_fuel_iso = ME_load_fuel.(char(ME_names(i))) * ME_MFR_FUEL_DES_ISO .* ME_on.(char(ME_names(i))) ;
    ME_bsfc_ISO = polyval(ME_POLY_FUEL_LOAD_2_BSFC_ISO,ME_load_fuel.(char(ME_names(i)))) ;
                        ME_bsfc.(char(ME_names(i))) = bsfcISOCorrection(ME_bsfc_ISO , ME_T_LTcooling.(char(ME_names(i)))(:,1) , ME_T_charge_air.(char(ME_names(i))) , LHV , 0.8) * ME_ETA_CORR ;
    ME_mfr_fuel.(char(ME_names(i))) = ME_mfr_fuel_iso .* ME_bsfc.(char(ME_names(i))) ./ ME_bsfc_ISO ; 
    ME_power.(char(ME_names(i))) = ME_mfr_fuel.(char(ME_names(i))) ./ ME_bsfc.(char(ME_names(i))) * 3.6e6 ;
    ME_load.(char(ME_names(i))) = ME_power.(char(ME_names(i))) / MCR_ME ;
                energy.ME.power(:,i) = ME_power.(char(ME_names(i))) ;
                energy.ME.fuel_ch(:,i) = ME_mfr_fuel.(char(ME_names(i))) * LHV ; 
                energy.ME.fuel_th(:,i) = ME_mfr_fuel.(char(ME_names(i))) .* CP_HFO .* (ME_T_fuel_oil.(char(ME_names(i))) - T0) ;
                energy.ME.fuel(:,i) = energy.ME.fuel_ch(:,i) + energy.ME.fuel_th(:,i) ;
    %% Air flow 
    ME_rho_air = ME_p_charge_air.(char(ME_names(i))).*1e5 ./ R_AIR ./ ME_T_charge_air.(char(ME_names(i))) .* ME_on.(char(ME_names(i))) ;
    ME_mfr_air.(char(ME_names(i))) = ME_V_MAX .* ME_rho_air .* ME_rpm.(char(ME_names(i))) / 60 / 2 * ETA_VOL * ME_N_CYL ;
    ME_T_air.(char(ME_names(i)))(:,1) = T_ER ;
    ME_eta_tc_is.(char(ME_names(i))) = polyval(ME_POLY_PIN_2_ETA_IS,ME_p_charge_air.(char(ME_names(i)))) ;
    ME_T_air.(char(ME_names(i)))(:,2) = T_ER + T_ER .* (ME_p_charge_air.(char(ME_names(i))) .^ ((K_AIR - 1) / K_AIR) - 1) ./ ME_eta_tc_is.(char(ME_names(i))) ;                  
    ME_T_air.(char(ME_names(i)))(:,3) = ME_T_charge_air.(char(ME_names(i))) ;
                energy.ME.air_1(:,i) = ME_mfr_air.(char(ME_names(i))) .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,1) - T0) ;
                energy.ME.air_2(:,i) = ME_mfr_air.(char(ME_names(i))) .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,2) - T0) ;
                energy.ME.air_3(:,i) = ME_mfr_air.(char(ME_names(i))) .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,3) - T0) ;
    %% Exhaust flow
    ME_mfr_eg.(char(ME_names(i))) = ME_mfr_air.(char(ME_names(i))) + ME_mfr_fuel.(char(ME_names(i))) ;
    ME_mfr_eg_tc.(char(ME_names(i))) = ME_mfr_air.(char(ME_names(i))) .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,2) - ME_T_air.(char(ME_names(i)))(:,1)) ./ ...
                (ETA_MECH_TC * CP_EG * (ME_T_eg.(char(ME_names(i)))(:,1) - ME_T_eg.(char(ME_names(i)))(:,2))) ;
    ME_mfr_eg_bypass.(char(ME_names(i))) = ME_mfr_eg.(char(ME_names(i))) - ME_mfr_eg_tc.(char(ME_names(i))) ;
                energy.ME.eg_1(:,i) = ME_mfr_eg.(char(ME_names(i))) .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,1) - T0) ; % 1 - after engine, before TC
                energy.ME.eg_2tc(:,i) =     ME_mfr_eg_tc.(char(ME_names(i))) .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,2) - T0) ; % 3 - after ExBo
                energy.ME.eg_2bypass(:,i) = ME_mfr_eg_bypass.(char(ME_names(i))) .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,1) - T0) ; % 3 - after ExBo
                energy.ME.eg_2(:,i) = energy.ME.eg_2tc(:,i) + energy.ME.eg_2bypass(:,i) ;
    if (i == 2) || (i == 3)
                energy.ME.eg_3(:,i) = ME_mfr_eg.(char(ME_names(i))) .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,3) - T0) ; % 2 - after TC, before ExBo
                energy.ME.hrsg(:,i) = energy.ME.eg_2(:,i) - energy.ME.eg_3(:,i) ;
    else
                energy.ME.eg_3(:,i) = energy.ME.eg_2(:,i) ;
                energy.ME.hrsg(:,i) = 0 ;
    end
    %% Charge air cooling, total
                energy.ME.cac(:,i) = energy.ME.air_2(:,i) - energy.ME.air_3(:,i) ;
    %% Remaining energy, total
                energy_2_cooling = energy.ME.fuel(:,i) - energy.ME.power(:,i) - energy.ME.eg_2(:,i) + energy.ME.air_1(:,i) ;
    %% HT and LT cooling
    energy_2_ht_th(:,1) = polyval(ME_POLY_LOAD_2_QDOT_HT,ME_load.(char(ME_names(i)))) ;
    energy_2_lt_th(:,1) = polyval(ME_POLY_LOAD_2_QDOT_LT,ME_load.(char(ME_names(i)))) ;
    energy_2_cooling_correction(:,1) = energy_2_cooling ./ (energy_2_ht_th + energy_2_lt_th) ; % Correction so to respect the engine energy balance
                energy.ME.ht(:,i) = energy_2_ht_th .* energy_2_cooling_correction ;
                energy.ME.lt(:,i) = energy_2_lt_th .* energy_2_cooling_correction ;
            ME_mfr_ht(:,i) = ME_MFR_HT .* ME_load.(char(ME_names(i))) ; % Here we make the assumption that the mass flow rate of HT cooling water in the main engines is linearly proportional to the engine laod...
            ME_mfr_lt(:,i) = ME_MFR_LT .* ME_load.(char(ME_names(i))) ; % Here we make the assumption that the mass flow rate of LT cooling water in the main engines is linearly proportional to the engine laod...
            %% Charge air cooling, HT stage
                energy.ME.cac_ht(:,i) = energy.ME.cac(:,i) .* polyval(AE_POLY_LOAD_2_SHARE_CAC,ME_load.(char(ME_names(i)))) ;
            %% Charge air cooling, LT stage
                energy.ME.cac_lt(:,i) = energy.ME.cac(:,i) - energy.ME.cac_ht(:,i) ;
            %% Jacket water
                energy.ME.jw(:,i) = energy.ME.ht(:,i) - energy.ME.cac_ht(:,i) ;
                energy.ME.jw_ht(:,i) = energy.ME.jw(:,i) ;
            %% Lubricating Oil
                energy.ME.lo(:,i) = energy.ME.lt(:,i) - energy.ME.cac_lt(:,i) ;
                energy.ME.lo_lt(:,i) = energy.ME.lo(:,i) ;
            ME_mfr_lo(:,i) = energy.ME.lo(:,i) ./ CP_LO ./ (ME_T_lub_oil.(char(ME_names(i)))(:,2) - ME_T_lub_oil.(char(ME_names(i)))(:,1)) ;            
            %% Cooling temperatures
            ME_T_LTcooling.(char(ME_names(i)))(:,2) = ME_T_LTcooling.(char(ME_names(i)))(:,1) + energy.ME.cac_lt(:,i) ./ CP_W ./ ME_mfr_lt(:,i) ; % Temperature before the LO cooler
            ME_T_LTcooling.(char(ME_names(i)))(:,3) = ME_T_LTcooling.(char(ME_names(i)))(:,2) + energy.ME.lo(:,i) ./ CP_W ./ ME_mfr_lt(:,i) ; % Temperature before mixing with the HT
            ME_T_LTcooling.(char(ME_names(i)))(:,4) = ME_T_LTcooling.(char(ME_names(i)))(:,3) + energy.ME.ht(:,i) ./ CP_W ./ ME_mfr_lt(:,i) ; % Temperature after mixing with the HT
            ME_T_HTcooling.(char(ME_names(i)))(:,2) = ME_T_HTcooling.(char(ME_names(i)))(:,1) + energy.ME.cac_ht(:,i) ./ CP_W ./ ME_mfr_ht(:,i) ; % Temperature before the JW cooler
            ME_T_HTcooling.(char(ME_names(i)))(:,3) = ME_T_HTcooling.(char(ME_names(i)))(:,2) + energy.ME.jw(:,i) ./ CP_W ./ ME_mfr_ht(:,i) ; % Temperature after the JW cooler
        
        
        
        
        
    %% Auxiliary engines
    %% Power - fuel flow - efficiency
    AE_load.(char(AE_names(i))) = AE_power.(char(AE_names(i))) ./ MCR_AE  .* AE_on.(char(AE_names(i))) ;
    AE_bsfc_ISO = polyval(AE_POLY_LOAD_2_ISO_BSFC,AE_load.(char(AE_names(i)))) ;
    if i == 3
        AE_bsfc.(char(AE_names(i))) = bsfcISOCorrection(AE_bsfc_ISO , AE_T_LTcooling.(char(AE_names(i)))(:,1) , AE_T_charge_air.(char(AE_names(i))) , LHV_MDO , 0.8) * AE_ETA_CORR ;
    else
        AE_bsfc.(char(AE_names(i))) = bsfcISOCorrection(AE_bsfc_ISO , AE_T_LTcooling.(char(AE_names(i)))(:,1) , AE_T_charge_air.(char(AE_names(i))) , LHV , 0.8) * AE_ETA_CORR ;
    end
    AE_mfr_fuel.(char(AE_names(i))) = AE_power.(char(AE_names(i))) .* AE_bsfc.(char(AE_names(i))) ./ 3.6e6  .* AE_on.(char(AE_names(i))) ;
                energy.AE.power(:,i) = AE_power.(char(AE_names(i))) ;
    if i==3
        % The engine number 3 runs on gas oil
                energy.AE.fuel_ch(:,i) = AE_mfr_fuel.(char(AE_names(i))) .* LHV_MDO ; 
                energy.AE.fuel_th(:,i) = AE_mfr_fuel.(char(AE_names(i))) .* CP_HFO .* (303 - T0) ;
    else
                energy.AE.fuel_ch(:,i) = AE_mfr_fuel.(char(AE_names(i))) * LHV ; 
                energy.AE.fuel_th(:,i) = AE_mfr_fuel.(char(AE_names(i))) .* CP_HFO .* (AE_T_fuel_oil.(char(AE_names(i))) - T0) ;
    end
                energy.AE.fuel(:,i) = energy.AE.fuel_ch(:,i) + energy.AE.fuel_th(:,i) ;
            %% Air flow 
    AE_rho_air = AE_p_charge_air.(char(AE_names(i))) .*1e5 ./ R_AIR ./ AE_T_charge_air.(char(AE_names(i)))  .* AE_on.(char(AE_names(i)))  ;
    AE_mfr_air.(char(AE_names(i))) = AE_V_SW .* AE_rho_air .* AE_rpm.(char(AE_names(i))) ./ 60 ./ 2 .* ETA_VOL .* AE_N_CYL ;
    AE_T_air.(char(AE_names(i)))(:,1) = T_ER ;
    AE_eta_tc_is.(char(AE_names(i))) = polyval(AE_POLY_PIN_2_ETA_IS,AE_p_charge_air.(char(AE_names(i)))) ;
    AE_T_air.(char(AE_names(i)))(:,3) = AE_T_charge_air.(char(AE_names(i))) ;
    AE_T_air.(char(AE_names(i)))(:,2) = T_ER + T_ER .* (AE_p_charge_air.(char(AE_names(i))) .^ ((K_AIR - 1) / K_AIR) - 1) ./ AE_eta_tc_is.(char(AE_names(i))) ;                  
                energy.AE.air_1(:,i) = AE_mfr_air.(char(AE_names(i))) .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,1) - T0) ;
                energy.AE.air_2(:,i) = AE_mfr_air.(char(AE_names(i))) .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,2) - T0) ;
                energy.AE.air_3(:,i) = AE_mfr_air.(char(AE_names(i))) .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,3) - T0) ;
            %% Exhaust flow
    AE_mfr_eg.(char(AE_names(i))) = AE_mfr_air.(char(AE_names(i))) + AE_mfr_fuel.(char(AE_names(i))) ;
    AE_mfr_eg_tc.(char(AE_names(i))) = AE_mfr_air.(char(AE_names(i))) .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,2) - AE_T_air.(char(AE_names(i)))(:,1)) ./ ...
        (ETA_MECH_TC .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,1) - AE_T_eg.(char(AE_names(i)))(:,2))) ;
    AE_mfr_eg_bypass.(char(AE_names(i))) = AE_mfr_eg.(char(AE_names(i))) - AE_mfr_eg_tc.(char(AE_names(i))) ;
                energy.AE.eg_1(:,i) = AE_mfr_eg.(char(AE_names(i))) .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,1) - T0) ; % 1 - after engine, before TC
                energy.AE.eg_2tc(:,i) =  AE_mfr_eg_tc.(char(AE_names(i))) .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,2) - T0) ; % 3 - after ExBo
                energy.AE.eg_2bypass(:,i) = AE_mfr_eg_bypass.(char(AE_names(i))) .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,1) - T0) ; % 3 - after ExBo
                energy.AE.eg_2(:,i) = energy.AE.eg_2tc(:,i) + energy.AE.eg_2bypass(:,i) ;
                energy.AE.eg_3(:,i) = AE_mfr_eg.(char(AE_names(i))) .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,3) - T0) ; % 2 - after TC, before ExBo
                energy.AE.hrsg(:,i) = energy.AE.eg_2(:,i) - energy.AE.eg_3(:,i) ;
            %% Charge air cooling, total
                energy.AE.cac(:,i) = energy.AE.air_2(:,i) - energy.AE.air_3(:,i) ;
            %% Remaining energy, total
                energy_2_cooling = energy.AE.fuel(:,i) - energy.AE.power(:,i) - energy.AE.eg_2(:,i) + energy.AE.air_1(:,i) ;
            %% HT and LT cooling
    energy_2_ht_th(:,1) = polyval(AE_POLY_LOAD_2_QDOT_HT,AE_load.(char(AE_names(i)))) ;
    energy_2_lt_th(:,1) = polyval(AE_POLY_LOAD_2_QDOT_LT,AE_load.(char(AE_names(i)))) ;
    energy_2_cooling_correcction(:,1) = energy_2_cooling ./ (energy_2_ht_th + energy_2_lt_th) ; % Correction so to respect the engine energy balance
                energy.AE.ht(:,i) = energy_2_ht_th .* energy_2_cooling_correcction ;
                energy.AE.lt(:,i) = energy_2_lt_th .* energy_2_cooling_correcction ;
    AE_mfr_ht(:,i) = AE_MFR_HT .* AE_load.(char(AE_names(i))) ; % Here we make the assumption that the mass flow rate of HT cooling water in the main engines is linearly proportional to the engine laod...
    AE_mfr_lt(:,i) = AE_MFR_LT .* AE_load.(char(AE_names(i))) ; % Here we make the assumption that the mass flow rate of LT cooling water in the main engines is linearly proportional to the engine laod...
    %% Charge air cooling, calculating ratio
                energy.AE.cac_ht(:,i) = energy.AE.cac(:,i) .* polyval(AE_POLY_LOAD_2_SHARE_CAC,ME_load.(char(ME_names(i)))) ;
                energy.AE.cac_lt(:,i) = energy.AE.cac(:,i) - energy.AE.cac_ht(:,i) ;
    %% Jacket water
                energy.AE.jw(:,i) = energy.AE.ht(:,i) - energy.AE.cac_ht(:,i) ;
                energy.AE.jw_ht(:,i) = energy.AE.jw(:,i) ;
    %% Lubricating Oil
                energy.AE.lo(:,i) = energy.AE.lt(:,i) - energy.AE.cac_lt(:,i) ;
                energy.AE.lo_lt(:,i) = energy.AE.lo(:,i) ;
    AE_mfr_lo(:,i) = AE_MFR_LO * AE_load.(char(AE_names(i))) ;
    %% Cooling temperatures
    AE_T_LTcooling.(char(AE_names(i)))(:,2) = AE_T_LTcooling.(char(AE_names(i)))(:,1) + energy.AE.cac_lt(:,i) ./ CP_W ./ AE_mfr_lt(:,i) ; % Temperature before the LO cooler
    AE_T_LTcooling.(char(AE_names(i)))(:,3) = AE_T_LTcooling.(char(AE_names(i)))(:,2) + energy.AE.lo(:,i) ./ CP_W ./ AE_mfr_lt(:,i) ; % Temperature before mixing with the HT
    AE_T_LTcooling.(char(AE_names(i)))(:,4) = AE_T_LTcooling.(char(AE_names(i)))(:,3) + energy.AE.ht(:,i) ./ CP_W ./ AE_mfr_lt(:,i) ; % Temperature after mixing with the HT
    AE_T_HTcooling.(char(AE_names(i)))(:,2) = AE_T_HTcooling.(char(AE_names(i)))(:,1) + energy.AE.cac_ht(:,i) ./ CP_W ./ AE_mfr_ht(:,i) ; % Temperature before the JW cooler
    AE_T_HTcooling.(char(AE_names(i)))(:,3) = AE_T_HTcooling.(char(AE_names(i)))(:,2) + energy.AE.jw(:,i) ./ CP_W ./ AE_mfr_ht(:,i) ; % Temperature after the JW cooler      
        
    
    
    %% Eliminating NaN values from when the engine is off
        energy_ME_fieldnames = fieldnames(energy.ME) ;
        for k = 1 : length(energy_ME_fieldnames)
            energy.ME.(char(energy_ME_fieldnames(k)))(ME_on.(char(ME_names(i))) == 0,i) = 0 ;
        end
        energy_AE_fieldnames = fieldnames(energy.AE) ;
        for k = 1 : length(energy_AE_fieldnames)
            energy.AE.(char(energy_AE_fieldnames(k)))(AE_on.(char(AE_names(i))) == 0,i) = 0 ;
        end
    
        
end






        