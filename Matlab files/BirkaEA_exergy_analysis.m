%%% BirkaEA_exergy_analysis

% Initialising variables for speed
BirkaEA_variable_initialisation_exergy 


for i = 1 : 4
    %% Main engines
        %% Fuel and power
        exergy.ME.power(:,i) = energy.ME.power(:,i) ;
        exergy.ME.fuel_ch(:,i) = energy.ME.fuel_ch(:,i) * HHV / LHV ;
        exergy.ME.fuel_th(:,i) = energy.ME.fuel_th(:,i) - ME_mfr_fuel.(char(ME_names(i))) .* T0 .* CP_HFO .* log(ME_T_fuel_oil.(char(ME_names(i))) ./ T0) ;
        exergy.ME.fuel(:,i) = exergy.ME.fuel_ch(:,i) + exergy.ME.fuel_th(:,i) ;
        %% Charge air
        exergy.ME.air_1(:,i) = energy.ME.air_1(:,i) - ME_mfr_air.(char(ME_names(i))) .* T0 .* CP_AIR .* log(ME_T_air.(char(ME_names(i)))(:,1) ./ T0) ;
        exergy.ME.air_2(:,i) = energy.ME.air_2(:,i) - ME_mfr_air.(char(ME_names(i))) .* T0 .* CP_AIR .* log(ME_T_air.(char(ME_names(i)))(:,2) ./ T0) ;
        exergy.ME.air_3(:,i) = energy.ME.air_3(:,i) - ME_mfr_air.(char(ME_names(i))) .* T0 .* CP_AIR .* log(ME_T_air.(char(ME_names(i)))(:,3) ./ T0) ;
        %% Exhaust gas
        exergy.ME.eg_1(:,i) = energy.ME.eg_1(:,i) - ME_mfr_eg.(char(ME_names(i))) .* T0 .* CP_EG .* log(ME_T_eg.(char(ME_names(i)))(:,1) ./ T0) ;
        exergy.ME.eg_2(:,i) = energy.ME.eg_1(:,i) - ME_mfr_eg.(char(ME_names(i))) .* T0 .* CP_EG .* log(ME_T_eg.(char(ME_names(i)))(:,2) ./ T0) ;
        if (i == 2) || (i == 3) 
            exergy.ME.eg_3(:,i) = energy.ME.eg_3(:,i) - ME_mfr_eg.(char(ME_names(i))) .* T0 .* CP_AIR .* log(ME_T_eg.(char(ME_names(i)))(:,3) ./ T0) ;
                ME_mfr_steam.(char(ME_names(i))) = energy.ME.hrsg(:,i) / DH_STEAM ;
            exergy.ME.hrsg(:,i) = ME_mfr_steam.(char(ME_names(i))) .* ((H_STEAM_VS - H_STEAM_LS) - T0 * (S_STEAM_VS - S_STEAM_LS)) ; % Pressure around 6 bar
        else
            exergy.ME.eg_3(:,i) = exergy.ME.eg_2(:,i) ;
                ME_mfr_steam.(char(ME_names(i))) = 0 ;
            exergy.ME.hrsg(:,i) = 0 ;
        end
        %% Charge air cooling (total)
        exergy.ME.cac_lt(:,i) = energy.ME.cac_lt(:,i) - ME_mfr_lt(:,i) .* T0 .* CP_W .* log(ME_T_LTcooling.(char(ME_names(i)))(:,2) ./ ME_T_LTcooling.(char(ME_names(i)))(:,1)) ;
        exergy.ME.cac_ht(:,i) = energy.ME.cac_ht(:,i) - ME_mfr_ht(:,i) .* T0 .* CP_W .* log(ME_T_HTcooling.(char(ME_names(i)))(:,2) ./ ME_T_HTcooling.(char(ME_names(i)))(:,1)) ;
        exergy.ME.cac(:,i) = exergy.ME.cac_lt(:,i) + exergy.ME.cac_ht(:,i) ;
        %% Jacket water
        exergy.ME.jw(:,i) = energy.ME.jw(:,i) .* (1 - T0 / 423) ; 
        exergy.ME.jw_ht(:,i) = energy.ME.jw_ht(:,i) - ME_mfr_ht(:,i) .* T0 .* CP_W .* log(ME_T_HTcooling.(char(ME_names(i)))(:,3) ./ ME_T_HTcooling.(char(ME_names(i)))(:,2)) ;
        %% Lubricating oil
                ME_T_lub_oil_calc.(char(ME_names(i))) = energy.ME.lo(:,i) ./ ME_mfr_lo(:,i) / CP_LO + ME_T_lub_oil.(char(ME_names(i)))(:,1) ;
        exergy.ME.lo(:,i) = energy.ME.lo(:,i) - ME_mfr_lo(:,i) .* T0 .* CP_LO .* log(ME_T_lub_oil_calc.(char(ME_names(i))) ./ ME_T_lub_oil.(char(ME_names(i)))(:,1)) ;
        exergy.ME.lo_lt(:,i) = energy.ME.lo(:,i) - ME_mfr_lt(:,i) .* T0 .* CP_W .* log(ME_T_LTcooling.(char(ME_names(i)))(:,3) ./ ME_T_LTcooling.(char(ME_names(i)))(:,2)) ;
        %% HT and LT cooling
        exergy.ME.ht(:,i) = exergy.ME.jw_ht(:,i) + exergy.ME.cac_ht(:,i) ;
        exergy.ME.ht_lt(:,i) = energy.ME.ht(:,i) - ME_mfr_lt(:,i) .* T0 .* CP_W .* log(ME_T_LTcooling.(char(ME_names(i)))(:,4) ./ ME_T_LTcooling.(char(ME_names(i)))(:,3)) ;
        exergy.ME.lt(:,i) = exergy.ME.lo_lt(:,i) + exergy.ME.cac_lt(:,i) ;
        %% Exergy destruction
        exergy.ME.exergy_destruction_engine(:,i) = exergy.ME.fuel(:,i) + exergy.ME.air_1(:,i) - exergy.ME.power(:,i) - exergy.ME.eg_2(:,i) - exergy.ME.jw(:,i) - exergy.ME.lo(:,i) - exergy.ME.cac(:,i) ;
        exergy.ME.exergy_destruction_tc(:,i) = exergy.ME.eg_1(:,i) - exergy.ME.eg_2(:,i) + exergy.ME.air_1(:,i) - exergy.ME.air_2(:,i) ; 
        exergy.ME.exergy_destruction_cac(:,i) = exergy.ME.air_2(:,i) - exergy.ME.air_3(:,i) - exergy.ME.cac(:,i) ;
        exergy.ME.exergy_destruction_hrsg(:,i) = exergy.ME.eg_2(:,i) - exergy.ME.eg_3(:,i) - exergy.ME.hrsg(:,i) ;
        %% Detailed exergy flows in the cooling systems
        exergy.ME.lt1(:,i) = CP_W * ME_mfr_lt(:,i) .* ((ME_T_LTcooling.(char(ME_names(i)))(:,1) - T0) - T0 .* log(ME_T_LTcooling.(char(ME_names(i)))(:,1) ./ T0)) ;
        exergy.ME.lt2(:,i) = CP_W * ME_mfr_lt(:,i) .* ((ME_T_LTcooling.(char(ME_names(i)))(:,2) - T0) - T0 .* log(ME_T_LTcooling.(char(ME_names(i)))(:,2) ./ T0)) ;
        exergy.ME.lt3(:,i) = CP_W * ME_mfr_lt(:,i) .* ((ME_T_LTcooling.(char(ME_names(i)))(:,3) - T0) - T0 .* log(ME_T_LTcooling.(char(ME_names(i)))(:,3) ./ T0)) ;
        exergy.ME.ht1(:,i) = CP_W * ME_mfr_ht(:,i) .* ((ME_T_HTcooling.(char(ME_names(i)))(:,1) - T0) - T0 .* log(ME_T_HTcooling.(char(ME_names(i)))(:,1) ./ T0)) ;
        exergy.ME.ht2(:,i) = CP_W * ME_mfr_ht(:,i) .* ((ME_T_HTcooling.(char(ME_names(i)))(:,2) - T0) - T0 .* log(ME_T_HTcooling.(char(ME_names(i)))(:,2) ./ T0)) ;
        exergy.ME.ht3(:,i) = CP_W * ME_mfr_ht(:,i) .* ((ME_T_HTcooling.(char(ME_names(i)))(:,3) - T0) - T0 .* log(ME_T_HTcooling.(char(ME_names(i)))(:,3) ./ T0)) ;
        exergy.ME.lo1(:,i) = CP_LO * ME_mfr_lo(:,i) .* ((ME_T_lub_oil.(char(ME_names(i)))(:,1) - T0) - T0 .* log(ME_T_lub_oil.(char(ME_names(i)))(:,1) ./ T0)) ;
        exergy.ME.lo2(:,i) = CP_LO * ME_mfr_lo(:,i) .* ((ME_T_lub_oil_calc.(char(ME_names(i))) - T0) - T0 .* log(ME_T_lub_oil_calc.(char(ME_names(i))) ./ T0)) ;
        exergy.ME.hrsg1(:,i) = CP_W * ME_mfr_steam.(char(ME_names(i))) .* ((TSAT_STEAM - T0) - T0 .* log(TSAT_STEAM./T0)) ;
        exergy.ME.hrsg2(:,i) = ME_mfr_steam.(char(ME_names(i))) .* ((CP_W * (TSAT_STEAM - T0)) + DH_STEAM - T0 .* (CP_W*log(TSAT_STEAM./T0) + DS_STEAM)) ;
        
        %% Eliminating NaN values from when the engine is off
        exergy_ME_fieldnames = fieldnames(exergy.ME) ;
        for j = 1 : length(exergy_ME_fieldnames)
            exergy.ME.(char(exergy_ME_fieldnames(j)))(ME_on.(char(ME_names(i))) == 0,i) = 0 ;
        end
        
    %% Auxiliary engines
        %% Fuel and power
        exergy.AE.power(:,i) = energy.AE.power(:,i) ;
        if i == 3
            exergy.AE.fuel_ch(:,i) = energy.AE.fuel_ch(:,i) * HHV_MDO / LHV_MDO ;
            exergy.AE.fuel_th(:,i) = energy.AE.fuel_th(:,i) - AE_mfr_fuel.(char(AE_names(i))) .* T0 .* CP_HFO .* log(303 ./ T0) ;
        else
            exergy.AE.fuel_ch(:,i) = energy.AE.fuel_ch(:,i) * HHV / LHV ;
            exergy.AE.fuel_th(:,i) = energy.AE.fuel_th(:,i) - AE_mfr_fuel.(char(AE_names(i))) .* T0 .* CP_HFO .* log(AE_T_fuel_oil.(char(AE_names(i))) ./ T0) ;
        end
        exergy.AE.fuel(:,i) = exergy.AE.fuel_ch(:,i) + exergy.AE.fuel_th(:,i) ;
        %% Charge air
        exergy.AE.air_1(:,i) = energy.AE.air_1(:,i) - AE_mfr_air.(char(AE_names(i))) .* T0 .* CP_AIR .* log(AE_T_air.(char(AE_names(i)))(:,1) ./ T0) ;
        exergy.AE.air_2(:,i) = energy.AE.air_2(:,i) - AE_mfr_air.(char(AE_names(i))) .* T0 .* CP_AIR .* log(AE_T_air.(char(AE_names(i)))(:,2) ./ T0) ;
        exergy.AE.air_3(:,i) = energy.AE.air_3(:,i) - AE_mfr_air.(char(AE_names(i))) .* T0 .* CP_AIR .* log(AE_T_air.(char(AE_names(i)))(:,3) ./ T0) ;
        %% Exhaust gas
        exergy.AE.eg_1(:,i) = energy.AE.eg_1(:,i) - AE_mfr_eg.(char(AE_names(i))) .* T0 .* CP_EG .* log(AE_T_eg.(char(AE_names(i)))(:,1) ./ T0) ;
        exergy.AE.eg_2(:,i) = energy.AE.eg_2(:,i) - AE_mfr_eg.(char(AE_names(i))) .* T0 .* CP_EG .* log(AE_T_eg.(char(AE_names(i)))(:,2) ./ T0) ;
        exergy.AE.eg_3(:,i) = energy.AE.eg_3(:,i) - AE_mfr_eg.(char(AE_names(i))) .* T0 .* CP_AIR .* log(AE_T_eg.(char(AE_names(i)))(:,3) ./ T0) ;
        %% HRSG
            AE_mfr_steam.(char(AE_names(i))) = energy.AE.hrsg(:,i) / 2100 ;
        exergy.AE.hrsg(:,i) = AE_mfr_steam.(char(AE_names(i))) .* ((2754 - 662) - T0 * (6.7766 - 1.9108)) ;
        %% Charge air cooling (total)
        exergy.AE.cac_lt(:,i) = energy.AE.cac_lt(:,i) - AE_mfr_lt(:,i) .* T0 .* CP_W .* log(AE_T_LTcooling.(char(AE_names(i)))(:,2) ./ AE_T_LTcooling.(char(AE_names(i)))(:,1)) ;
        exergy.AE.cac_ht(:,i) = energy.AE.cac_ht(:,i) - AE_mfr_ht(:,i) .* T0 .* CP_W .* log(AE_T_HTcooling.(char(AE_names(i)))(:,2) ./ AE_T_HTcooling.(char(AE_names(i)))(:,1)) ;
        exergy.AE.cac(:,i) = exergy.AE.cac_lt(:,i) + exergy.AE.cac_ht(:,i) ;        
        %% Jacket water
        exergy.AE.jw(:,i) = energy.AE.jw(:,i) .* (1 - T0 / 423) ; 
        exergy.AE.jw_ht(:,i) = energy.AE.jw_ht(:,i) - AE_mfr_ht(:,i) .* T0 .* CP_W .* log(AE_T_HTcooling.(char(AE_names(i)))(:,3) ./ AE_T_HTcooling.(char(AE_names(i)))(:,2)) ;
        %% Lubricating oil
                AE_T_lub_oil_calc.(char(AE_names(i))) = energy.AE.lo(:,i) ./ AE_mfr_lo(:,i) / CP_LO + AE_T_lub_oil.(char(AE_names(i)))(:,1) ;
        exergy.AE.lo(:,i) = energy.AE.lo(:,i) - AE_mfr_lo(:,i) .* T0 .* CP_LO .* log(AE_T_lub_oil_calc.(char(AE_names(i))) ./ AE_T_lub_oil.(char(AE_names(i)))(:,1)) ;
        exergy.AE.lo_lt(:,i) = energy.AE.lo(:,i) - AE_mfr_lt(:,i) .* T0 .* CP_W .* log(AE_T_LTcooling.(char(AE_names(i)))(:,3) ./ AE_T_LTcooling.(char(AE_names(i)))(:,2)) ;
        %% HT and LT cooling
        exergy.AE.ht(:,i) = exergy.AE.jw_ht(:,i) + exergy.AE.cac_ht(:,i) ;
        exergy.AE.ht_lt(:,i) = energy.AE.ht(:,i) - AE_mfr_lt(:,i) .* T0 .* CP_W .* log(AE_T_LTcooling.(char(AE_names(i)))(:,4) ./ AE_T_LTcooling.(char(AE_names(i)))(:,3)) ;
        exergy.AE.lt(:,i) = exergy.AE.lo_lt(:,i) + exergy.AE.cac_lt(:,i) ;        
        %% Exergy destruction
        exergy.AE.exergy_destruction_tc(:,i) = exergy.AE.eg_1(:,i) - exergy.AE.eg_2(:,i) + exergy.AE.air_1(:,i) - exergy.AE.air_2(:,i) ; 
        exergy.AE.exergy_destruction_hrsg(:,i) = exergy.AE.eg_2(:,i) - exergy.AE.eg_3(:,i) - exergy.AE.hrsg(:,i) ;
        exergy.AE.exergy_destruction_engine(:,i) = exergy.AE.fuel(:,i) + exergy.AE.air_1(:,i) - exergy.AE.eg_2(:,i) - exergy.AE.ht(:,i) - exergy.AE.lt(:,i) - exergy.AE.power(:,i) - exergy.AE.cac(:,i);
        exergy.AE.exergy_destruction_cac(:,i) = exergy.AE.air_2(:,i) - exergy.AE.air_3(:,i) - exergy.AE.cac(:,i) ;
        %% Detailed exergy flows in the cooling systems
        exergy.AE.lt1(:,i) = CP_W * AE_mfr_lt(:,i) .* ((AE_T_LTcooling.(char(AE_names(i)))(:,1) - T0) - T0 .* log(AE_T_LTcooling.(char(AE_names(i)))(:,1) ./ T0)) ;
        exergy.AE.lt2(:,i) = CP_W * AE_mfr_lt(:,i) .* ((AE_T_LTcooling.(char(AE_names(i)))(:,2) - T0) - T0 .* log(AE_T_LTcooling.(char(AE_names(i)))(:,2) ./ T0)) ;
        exergy.AE.lt3(:,i) = CP_W * AE_mfr_lt(:,i) .* ((AE_T_LTcooling.(char(AE_names(i)))(:,3) - T0) - T0 .* log(AE_T_LTcooling.(char(AE_names(i)))(:,3) ./ T0)) ;
        exergy.AE.ht1(:,i) = CP_W * AE_mfr_ht(:,i) .* ((AE_T_HTcooling.(char(AE_names(i)))(:,1) - T0) - T0 .* log(AE_T_HTcooling.(char(AE_names(i)))(:,1) ./ T0)) ;
        exergy.AE.ht2(:,i) = CP_W * AE_mfr_ht(:,i) .* ((AE_T_HTcooling.(char(AE_names(i)))(:,2) - T0) - T0 .* log(AE_T_HTcooling.(char(AE_names(i)))(:,2) ./ T0)) ;
        exergy.AE.ht3(:,i) = CP_W * AE_mfr_ht(:,i) .* ((AE_T_HTcooling.(char(AE_names(i)))(:,3) - T0) - T0 .* log(AE_T_HTcooling.(char(AE_names(i)))(:,3) ./ T0)) ;
        exergy.AE.lo1(:,i) = CP_LO * AE_mfr_lo(:,i) .* ((AE_T_lub_oil.(char(AE_names(i)))(:,1) - T0) - T0 .* log(AE_T_lub_oil.(char(AE_names(i)))(:,1) ./ T0)) ;
        exergy.AE.lo2(:,i) = CP_LO * AE_mfr_lo(:,i) .* ((AE_T_lub_oil_calc.(char(AE_names(i))) - T0) - T0 .* log(AE_T_lub_oil_calc.(char(AE_names(i))) ./ T0)) ;
        exergy.AE.hrsg1(:,i) = CP_W * AE_mfr_steam.(char(AE_names(i))) .* ((TSAT_STEAM - T0) - T0 .* log(TSAT_STEAM./T0)) ;
        exergy.AE.hrsg2(:,i) = AE_mfr_steam.(char(AE_names(i))) .* ((CP_W * (TSAT_STEAM - T0)) + DH_STEAM - T0 .* (CP_W*log(TSAT_STEAM./T0) + DS_STEAM)) ;
        
        %% Eliminating NaN values from when the engine is off
        exergy_AE_fieldnames = fieldnames(exergy.AE) ;
        for j = 1 : length(exergy_AE_fieldnames)
            exergy.AE.(char(exergy_AE_fieldnames(j)))(AE_on.(char(AE_names(i))) == 0,i) = 0 ;
        end
end
