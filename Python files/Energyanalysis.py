## BirkaEA_main_engines_efficiency ##

# Initialising variables for speed
BirkaEA_variable_initialisation_energy 

# Correction factor for main / auxiliary engines power and load based on
# the comparison with the fuel meter
# BirkaEA_fuel_consumption_correction_AE3onDiesel
## NOTE: THE CORRECTION IS FIXED TO 1.15 TO AVOID STRANGE THINGS
## THE ANALYSIS IS BASED ON THE ABOVE SCRIPT
# See the constant ME_ETA_CORR, AE_ETA_CORR

# NOTE: THIS SHOULD BE MOVED TO ANOTHER PYTHON FILE
def engineFuelFlowCalculation(dataframe,CONSTANTS):
    # This function is used to calculate the fuel flow of an engine given its fuel rack position and its rotating speed.
    # Inputs are free, as long as the same unit is used for the fuel rack position and the engine speed in both the input and the "design" values in the "CONSTANTS" dictionary
    output = CONSTANTS["MainEngines"]["MFR_FUEL_DES"] * ( (CONSTANTS["MainEngines"]["POLY_FRP_2_MF"][0] + CONSTANTS["MainEngines"]["POLY_FRP_2_MF"][1] * fuel_rack_position) / (CONSTANTS["MainEngines"]["POLY_FRP_2_MF"][0] + CONSTANTS["MainEngines"]["POLY_FRP_2_MF"][1] * CONSTANTS["MainEngines"]["FRP_DES"])) * (engine_speed / CONSTANTS["MainEngines"]["RPM_DES"])
    return output

def powerAndFuel(dataframe,CONSTANTS):
    engine_fuel_flow = dataframe["ME"]
    dataframe

for i = 1 : 4
    ## Main engines
    ## Power - fuel flow - efficiency
    ##ME_load_fuel.(char(ME_names(i))) = ME_pos_fuel_rack.(char(ME_names(i))) .* ME_rpm.(char(ME_names(i))) ./ polyval(polyfit([0.295 0.515 0.735 0.835 1],[315 397 454 474 500],2),ME_pos_fuel_rack.(char(ME_names(i)))) .* ME_on.(char(ME_names(i))) ;
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
    ## Air flows
    ME_T_air.(char(ME_names(i)))(:,1) = T_ER ; # Temperature before compressor is assumed to be constant
    # Temperature after the compressor
    ME_T_air.(char(ME_names(i)))(:,2) = ME_T_air.(char(ME_names(i)))(:,1) .* (1 + (ME_p_charge_air.(char(ME_names(i))).^((K_AIR-1)/K_AIR) - 1) ./ polyval(ME_POLY_PIN_2_ETA_IS,ME_p_charge_air.(char(ME_names(i))))) ;
    # Mass flow rate to the engine is calculated based on the approximation of ideal gas conditions in the engine cylinders at max volume
    mdot_air_2engine = ME_V_MAX .* ME_p_charge_air.(char(ME_names(i)))*1e5 ./ R_AIR ./ ME_T_charge_air.(char(ME_names(i))) .* ME_rpm.(char(ME_names(i))) / 60 / 2 * ETA_VOL * ME_N_CYL .* ME_on.(char(ME_names(i)));
    # Exhaust flow leaving the engine equal to sum of air and fuel flows
    mdot_eg_fromengine = mdot_air_2engine + ME_mfr_fuel.(char(ME_names(i))) ;
    # Final supercalculation
    mdot_air_bypass = (mdot_eg_fromengine .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,1) - ME_T_eg.(char(ME_names(i)))(:,2)) - CP_AIR / ETA_MECH_TC .* mdot_air_2engine .* (ME_T_air.(char(ME_names(i)))(:,2) - ME_T_air.(char(ME_names(i)))(:,1))) ./ ...
        (CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,2) - ME_T_air.(char(ME_names(i)))(:,2)) + CP_AIR / ETA_MECH_TC .* (ME_T_air.(char(ME_names(i)))(:,2) - ME_T_air.(char(ME_names(i)))(:,1))) ;
    T_eg_beforeBypass = ME_T_eg.(char(ME_names(i)))(:,1) - (mdot_air_bypass+mdot_air_2engine .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,2) - ME_T_air.(char(ME_names(i)))(:,1))) ./ ETA_MECH_TC ./ CP_EG ./ mdot_eg_fromengine ;
    ME_mfr_air.(char(ME_names(i))) = mdot_air_bypass + mdot_air_2engine ;
    ME_mfr_eg.(char(ME_names(i))) = mdot_air_bypass + mdot_eg_fromengine ; 
    ## Energy in the air flows
                energy.ME.air_1(:,i) = ME_mfr_air.(char(ME_names(i))) .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,1) - T0) ; # Inlet flow, at Engine Room temperature
                energy.ME.air_2(:,i) = ME_mfr_air.(char(ME_names(i))) .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,2) - T0) ; # After the compressor, at high temperature
                energy.ME.air_3(:,i) = mdot_air_2engine .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,3) - T0) ; # After the CAC, at low temperature again
    ## Energy in the exhaust gas flows
                energy.ME.eg_1(:,i) = ME_mfr_eg.(char(ME_names(i))) .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,1) - T0) ; # 1 - after engine, before TC
                energy.ME.eg_2(:,i) = ME_mfr_eg.(char(ME_names(i))) .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,2) - T0) ; # 1 - after engine, after TC (and after merging with the air bypass)
    if (i == 2) || (i == 3)
                energy.ME.eg_3(:,i) = ME_mfr_eg.(char(ME_names(i))) .* CP_EG .* (ME_T_eg.(char(ME_names(i)))(:,3) - T0) ; # 2 - after TC, before ExBo
                energy.ME.hrsg(:,i) = energy.ME.eg_2(:,i) - energy.ME.eg_3(:,i) ;
    else
                energy.ME.eg_3(:,i) = energy.ME.eg_2(:,i) ;
                energy.ME.hrsg(:,i) = 0 ;
    end
    ## Energy to cooling systems
                energy_2_cooling = energy.ME.fuel(:,i) - energy.ME.power(:,i) - energy.ME.eg_2(:,i) + energy.ME.air_1(:,i) ;            
                # Charge air cooler (total)
                energy.ME.cac(:,i) = energy.ME.air_2(:,i) .* mdot_air_2engine ./ (mdot_air_2engine + mdot_air_bypass) - energy.ME.air_3(:,i) ;
                # HT cooling systems
                energy.ME.ht(:,i) = energy_2_cooling .* polyval(ME_POLY_LOAD_2_QDOT_HT,ME_load.(char(ME_names(i)))) ./ (polyval(ME_POLY_LOAD_2_QDOT_HT,ME_load.(char(ME_names(i)))) + polyval(ME_POLY_LOAD_2_QDOT_LT,ME_load.(char(ME_names(i))))) ;
                # LT cooling systems
                energy.ME.lt(:,i) = energy_2_cooling - energy.ME.ht(:,i) ;
                # Charge air cooling, HT stage
                energy.ME.cac_ht(:,i) = mdot_air_2engine .* CP_AIR .* (ME_T_air.(char(ME_names(i)))(:,2) - ME_T_air.(char(ME_names(i)))(:,1)) .* EPS_CAC_HTSTAGE ; # Assuming 0.85 effectiveness
                # Charge air cooling, LT stage
                energy.ME.cac_lt(:,i) = energy.ME.cac(:,i) - energy.ME.cac_ht(:,i) ;
                # Jacket water
                energy.ME.jw(:,i) = energy.ME.ht(:,i) - energy.ME.cac_ht(:,i) ;
                energy.ME.jw_ht(:,i) = energy.ME.jw(:,i) ;
                # Lubricating Oil
                energy.ME.lo(:,i) = energy.ME.lt(:,i) - energy.ME.cac_lt(:,i) ;
                energy.ME.lo_lt(:,i) = energy.ME.lo(:,i) ;
     ## Details of cooling flows
     # Mass flows. 
        # Calculated assuming that there is a linear relationship with the engine speed (engine driven pumps)
     ME_mfr_ht(:,i) = ME_MFR_HT .* ME_rpm.(char(ME_names(i))) / RPM_DES_ME ; # Here we make the assumption that the mass flow rate of HT cooling water in the main engines is linearly proportional to the engine laod...
     ME_mfr_lt(:,i) = ME_MFR_LT .*  ME_rpm.(char(ME_names(i))) / RPM_DES_ME ; # Here we make the assumption that the mass flow rate of LT cooling water in the main engines is linearly proportional to the engine laod...
     ME_mfr_lo(:,i) = energy.ME.lo(:,i) ./ CP_LO ./ (ME_T_lub_oil.(char(ME_names(i)))(:,2) - ME_T_lub_oil.(char(ME_names(i)))(:,1)) ;                
     # Temperatures 
     ME_T_LTcooling.(char(ME_names(i)))(:,2) = ME_T_LTcooling.(char(ME_names(i)))(:,1) + energy.ME.cac_lt(:,i) ./ CP_W ./ ME_mfr_lt(:,i) ; # Temperature before the LO cooler
     ME_T_LTcooling.(char(ME_names(i)))(:,3) = ME_T_LTcooling.(char(ME_names(i)))(:,2) + energy.ME.lo(:,i) ./ CP_W ./ ME_mfr_lt(:,i) ; # Temperature before mixing with the HT
     ME_T_LTcooling.(char(ME_names(i)))(:,4) = ME_T_LTcooling.(char(ME_names(i)))(:,3) + energy.ME.ht(:,i) ./ CP_W ./ ME_mfr_lt(:,i) ; # Temperature after mixing with the HT
     ME_T_HTcooling.(char(ME_names(i)))(:,2) = ME_T_HTcooling.(char(ME_names(i)))(:,1) + energy.ME.cac_ht(:,i) ./ CP_W ./ ME_mfr_ht(:,i) ; # Temperature before the JW cooler
     ME_T_HTcooling.(char(ME_names(i)))(:,3) = ME_T_HTcooling.(char(ME_names(i)))(:,2) + energy.ME.jw(:,i) ./ CP_W ./ ME_mfr_ht(:,i) ; # Temperature after the JW cooler          
                
     
     
     
     
     
     ## SONO ARRIVATO FIN QUI ##
  ## Auxiliary engines
    ## Power - fuel flow - efficiency
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
        # The engine number 3 runs on gas oil
                energy.AE.fuel_ch(:,i) = AE_mfr_fuel.(char(AE_names(i))) .* LHV_MDO ; 
                energy.AE.fuel_th(:,i) = AE_mfr_fuel.(char(AE_names(i))) .* CP_HFO .* (303 - T0) ;
    else
                energy.AE.fuel_ch(:,i) = AE_mfr_fuel.(char(AE_names(i))) * LHV ; 
                energy.AE.fuel_th(:,i) = AE_mfr_fuel.(char(AE_names(i))) .* CP_HFO .* (AE_T_fuel_oil.(char(AE_names(i))) - T0) ;
    end
                energy.AE.fuel(:,i) = energy.AE.fuel_ch(:,i) + energy.AE.fuel_th(:,i) ;
    ## Air flows
    AE_T_air.(char(AE_names(i)))(:,1) = T_ER ; # Temperature before compressor is assumed to be constant
    # Temperature after the compressor
    AE_T_air.(char(AE_names(i)))(:,2) = AE_T_air.(char(AE_names(i)))(:,1) .* (1 + (AE_p_charge_air.(char(AE_names(i))).^((K_AIR-1)/K_AIR) - 1) ./ polyval(AE_POLY_PIN_2_ETA_IS,AE_p_charge_air.(char(AE_names(i))))) ;
    # Mass flow rate to the engine is calculated based on the approximation of ideal gas conditions in the engine cylinders at max volume
    mdot_air_2engine = AE_V_MAX .* AE_p_charge_air.(char(AE_names(i)))*1e5 ./ R_AIR ./ AE_T_charge_air.(char(AE_names(i))) .* AE_rpm.(char(AE_names(i))) / 60 / 2 * ETA_VOL * AE_N_CYL .* AE_on.(char(AE_names(i)));
    # Exhaust flow leaving the engine equal to sum of air and fuel flows
    mdot_eg_fromengine = mdot_air_2engine + AE_mfr_fuel.(char(AE_names(i))) ;
    # Final supercalculation
    mdot_air_bypass = (mdot_eg_fromengine .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,1) - AE_T_eg.(char(AE_names(i)))(:,2)) - CP_AIR / ETA_MECH_TC .* mdot_air_2engine .* (AE_T_air.(char(AE_names(i)))(:,2) - AE_T_air.(char(AE_names(i)))(:,1))) ./ ...
        (CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,2) - AE_T_air.(char(AE_names(i)))(:,2)) + CP_AIR / ETA_MECH_TC .* (AE_T_air.(char(AE_names(i)))(:,2) - AE_T_air.(char(AE_names(i)))(:,1))) ;
    T_eg_beforeBypass = AE_T_eg.(char(AE_names(i)))(:,1) - (mdot_air_bypass+mdot_air_2engine .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,2) - AE_T_air.(char(AE_names(i)))(:,1))) ./ ETA_MECH_TC ./ CP_EG ./ mdot_eg_fromengine ;
    AE_mfr_air.(char(AE_names(i))) = mdot_air_bypass + mdot_air_2engine ;
    AE_mfr_eg.(char(AE_names(i))) = mdot_air_bypass + mdot_eg_fromengine ; 
    ## Energy in the air flows
                energy.AE.air_1(:,i) = AE_mfr_air.(char(AE_names(i))) .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,1) - T0) ; # Inlet flow, at Engine Room temperature
                energy.AE.air_2(:,i) = AE_mfr_air.(char(AE_names(i))) .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,2) - T0) ; # After the compressor, at high temperature
                energy.AE.air_3(:,i) = mdot_air_2engine .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,3) - T0) ; # After the CAC, at low temperature again
    ## Energy in the exhaust gas flows
                energy.AE.eg_1(:,i) = AE_mfr_eg.(char(AE_names(i))) .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,1) - T0) ; # 1 - after engine, before TC
                energy.AE.eg_2(:,i) = AE_mfr_eg.(char(AE_names(i))) .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,2) - T0) ; # 1 - after engine, after TC (and after merging with the air bypass)
                energy.AE.eg_3(:,i) = AE_mfr_eg.(char(AE_names(i))) .* CP_EG .* (AE_T_eg.(char(AE_names(i)))(:,3) - T0) ; # 2 - after TC, before ExBo
                energy.AE.hrsg(:,i) = energy.AE.eg_2(:,i) - energy.AE.eg_3(:,i) ;
    ## Energy to cooling systems
                energy_2_cooling = energy.AE.fuel(:,i) - energy.AE.power(:,i) - energy.AE.eg_2(:,i) + energy.AE.air_1(:,i) ;            
                # Charge air cooler (total)
                energy.AE.cac(:,i) = energy.AE.air_2(:,i) .* mdot_air_2engine ./ (mdot_air_2engine + mdot_air_bypass) - energy.AE.air_3(:,i) ;
                # HT cooling systems
                energy.AE.ht(:,i) = energy_2_cooling .* polyval(AE_POLY_LOAD_2_QDOT_HT,AE_load.(char(AE_names(i)))) ./ (polyval(AE_POLY_LOAD_2_QDOT_HT,AE_load.(char(AE_names(i)))) + polyval(AE_POLY_LOAD_2_QDOT_LT,AE_load.(char(AE_names(i))))) ;
                # LT cooling systems
                energy.AE.lt(:,i) = energy_2_cooling - energy.AE.ht(:,i) ;
                # Charge air cooling, HT stage
                energy.AE.cac_ht(:,i) = mdot_air_2engine .* CP_AIR .* (AE_T_air.(char(AE_names(i)))(:,2) - AE_T_air.(char(AE_names(i)))(:,1)) .* EPS_CAC_HTSTAGE ; # Assuming 0.85 effectiveness
                # Charge air cooling, LT stage
                energy.AE.cac_lt(:,i) = energy.AE.cac(:,i) - energy.AE.cac_ht(:,i) ;
                # Jacket water
                energy.AE.jw(:,i) = energy.AE.ht(:,i) - energy.AE.cac_ht(:,i) ;
                energy.AE.jw_ht(:,i) = energy.AE.jw(:,i) ;
                # Lubricating Oil
                energy.AE.lo(:,i) = energy.AE.lt(:,i) - energy.AE.cac_lt(:,i) ;
                energy.AE.lo_lt(:,i) = energy.AE.lo(:,i) ;
     ## Details of cooling flows
     # Mass flows. 
        # Calculated assuming that there is a linear relationship with the engine speed (engine driven pumps)
     AE_mfr_ht(:,i) = AE_MFR_HT .* AE_rpm.(char(AE_names(i))) / RPM_DES_AE ; # Here we make the assumption that the mass flow rate of HT cooling water in the main engines is linearly proportional to the engine laod...
     AE_mfr_lt(:,i) = AE_MFR_LT .*  AE_rpm.(char(AE_names(i))) / RPM_DES_AE ; # Here we make the assumption that the mass flow rate of LT cooling water in the main engines is linearly proportional to the engine laod...
     AE_mfr_lo(:,i) = AE_MFR_LO ;
     AE_T_lub_oil.(char(AE_names(i)))(:,2) = AE_T_lub_oil.(char(AE_names(i)))(:,1) + energy.AE.lo(:,i) ./ CP_LO ./ AE_mfr_lo(:,i) ; 

     # Temperatures 
     AE_T_LTcooling.(char(AE_names(i)))(:,2) = AE_T_LTcooling.(char(AE_names(i)))(:,1) + energy.AE.cac_lt(:,i) ./ CP_W ./ AE_mfr_lt(:,i) ; # Temperature before the LO cooler
     AE_T_LTcooling.(char(AE_names(i)))(:,3) = AE_T_LTcooling.(char(AE_names(i)))(:,2) + energy.AE.lo(:,i) ./ CP_W ./ AE_mfr_lt(:,i) ; # Temperature before mixing with the HT
     AE_T_LTcooling.(char(AE_names(i)))(:,4) = AE_T_LTcooling.(char(AE_names(i)))(:,3) + energy.AE.ht(:,i) ./ CP_W ./ AE_mfr_lt(:,i) ; # Temperature after mixing with the HT
     AE_T_HTcooling.(char(AE_names(i)))(:,2) = AE_T_HTcooling.(char(AE_names(i)))(:,1) + energy.AE.cac_ht(:,i) ./ CP_W ./ AE_mfr_ht(:,i) ; # Temperature before the JW cooler
     AE_T_HTcooling.(char(AE_names(i)))(:,3) = AE_T_HTcooling.(char(AE_names(i)))(:,2) + energy.AE.jw(:,i) ./ CP_W ./ AE_mfr_ht(:,i) ; # Temperature after the JW cooler          
                
                
                
                
           
        
        
        
     
    
    
    ## Eliminating NaN values from when the engine is off
        energy_ME_fieldnames = fieldnames(energy.ME) ;
        for k = 1 : length(energy_ME_fieldnames)
            energy.ME.(char(energy_ME_fieldnames(k)))(ME_on.(char(ME_names(i))) == 0,i) = 0 ;
        end
        energy_AE_fieldnames = fieldnames(energy.AE) ;
        for k = 1 : length(energy_AE_fieldnames)
            energy.AE.(char(energy_AE_fieldnames(k)))(AE_on.(char(AE_names(i))) == 0,i) = 0 ;
        end
    
        
end






        