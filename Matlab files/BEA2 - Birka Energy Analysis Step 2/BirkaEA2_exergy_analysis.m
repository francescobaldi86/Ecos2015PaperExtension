%%% BirkaEA_exergy_analysis

% Initialising variables for speed
BirkaEA_variable_initialisation_exergy 


for i = 1 : 4
    %% Main engines
        %% Fuel and power
        exergy.ME.Power(:,i) = energy.ME.Power(:,i) ;
        exergy.ME.fuel_ch(:,i) = energy.ME.fuel_ch(:,i) * HHV / LHV ;
        exergy.ME.fuel_th(:,i) = energy.ME.fuel_th(:,i) - ME_Mfuel(:,i) .* T0 .* CP_HFO .* log(ME_Tfuel(:,i) ./ T0) ;
        exergy.ME.fuel(:,i) = exergy.ME.fuel_ch(:,i) + exergy.ME.fuel_th(:,i) ;
        %% Charge air
        exergy.ME.ca_bcomp(:,i) = energy.ME.ca_bcomp(:,i) - ME_Mca_bcomp(:,i) .* T0 .* CP_AIR .* log(T_ER ./ T0) ;
        exergy.ME.ca_acomp(:,i) = energy.ME.ca_acomp(:,i) - ME_Mca_bcomp(:,i) .* T0 .* CP_AIR .* log(ME_Tca_acomp(:,i) ./ T0) ;
        exergy.ME.ca_2eng(:,i) = energy.ME.ca_2eng(:,i) - ME_Mca_2eng(:,i) .* T0 .* CP_AIR .* log(ME_Tca(:,i) ./ T0) ;
        exergy.ME.ca_2cac(:,i) = energy.ME.ca_2cac(:,i) - ME_Mca_2eng(:,i) .* T0 .* CP_AIR .* log(ME_Tca_acomp(:,i) ./ T0) ;
        exergy.ME.air_bypass(:,i) = energy.ME.air_bypass(:,i) - ME_Mca_bypass(:,i) .* T0 .* CP_AIR .* log(ME_Tca_acomp(:,i) ./ T0) ;
        exergy.ME.ca_incac(:,i) = energy.ME.ca_incac(:,i) - ME_Mca_2eng(:,i) .* T0 .* CP_AIR .* log(ME_Tca_incac(:,i) ./ T0) ;
        %% Exhaust gas
        exergy.ME.eg_aEng(:,i) = energy.ME.eg_aEng(:,i) - ME_Meg_aEng(:,i) .* T0 .* CP_EG .* log(ME_Teg_aEng(:,i) ./ T0) ;
        exergy.ME.eg_bTC(:,i) = energy.ME.eg_bTC(:,i) - ME_Meg_TC(:,i) .* T0 .* CP_EG .* log(ME_Teg_bTC(:,i) ./ T0) ;
        exergy.ME.eg_aTC(:,i) = energy.ME.eg_aTC(:,i) - ME_Meg_TC(:,i) .* T0 .* CP_EG .* log(ME_Teg_aTC(:,i) ./ T0) ;
                ME_Msteam_hrsg(:,i) = energy.ME.hrsg(:,i) ./ DH_STEAM ;
        exergy.ME.hrsg(:,i) = ME_Msteam_hrsg(:,i) .* (DH_STEAM - T0 .* DS_STEAM) ;
        exergy.ME.steam_in(:,i) = ME_Msteam_hrsg(:,i) .* ((H_STEAM_LS - CP_W .* (T0 - 273.15)) - T0 .* (S_STEAM_LS - CP_W .* log(T0./273.15))) ;
        exergy.ME.steam_out(:,i) = ME_Msteam_hrsg(:,i) .* ((H_STEAM_VS - CP_W .* (T0 - 273.15)) - T0 .* (S_STEAM_VS - CP_W .* log(T0./273.15))) ;
        exergy.ME.eg_aHRSG(:,i) = energy.ME.eg_aHRSG(:,i) - ME_Meg_TC(:,i) .* T0 .* CP_EG .* log(ME_Teg_aHRSG(:,i) ./ T0) ;
        %% Cooling systems, source
        exergy.ME.lo_bEng(:,i) = energy.ME.lo_bEng(:,i) - ME_Mlo(:,i) .* CP_LO .* (ME_Tlo_bEng(:,i) ./ T0) ;
        exergy.ME.lo_aEng(:,i) = energy.ME.lo_aEng(:,i) - ME_Mlo(:,i) .* CP_LO .* (ME_Tlo_aEng(:,i) ./ T0) ;
        exergy.ME.jwEng(:,i) = energy.ME.jw(:,i) .* (1 - T0 / 423) ;
        %% Cooling systems, HT and LT
        exergy.ME.ht_bEng(:,i) = energy.ME.ht_bEng(:,i) - ME_Mht(:,i) .* CP_W .* (ME_Tht_bEng(:,i) ./ T0) ;
        exergy.ME.ht_ajwc(:,i) = energy.ME.ht_ajwc(:,i) - ME_Mht(:,i) .* CP_W .* (ME_Tht_ajwc(:,i) ./ T0) ;
        exergy.ME.ht_acac(:,i) = energy.ME.ht_acac(:,i) - ME_Mht(:,i) .* CP_W .* (ME_Tht_acac(:,i) ./ T0) ;
        exergy.ME.lt_bEng(:,i) = energy.ME.lt_bEng(:,i) - ME_Mlt(:,i) .* CP_W .* (ME_Tlt_bEng(:,i) ./ T0) ;
        exergy.ME.lt_acac(:,i) = energy.ME.lt_acac(:,i) - ME_Mlt(:,i) .* CP_W .* (ME_Tlt_acac(:,i) ./ T0) ;
        exergy.ME.lt_aloc(:,i) = energy.ME.lt_aloc(:,i) - ME_Mlt(:,i) .* CP_W .* (ME_Tlt_aloc(:,i) ./ T0) ;
        %% Exergy destruction
        exergy.ME.ExDes_cylinders(:,i) = exergy.ME.fuel(:,i) + exergy.ME.ca_2eng(:,i) - exergy.ME.Power(:,i) - exergy.ME.eg_aEng(:,i) - exergy.ME.jwEng(:,i) - (exergy.ME.lo_aEng(:,i) - exergy.ME.lo_bEng(:,i)) ;
        exergy.ME.ExDes_bypass(:,i) = exergy.ME.air_bypass(:,i) + exergy.ME.eg_aEng(:,i) - exergy.ME.eg_bTC(:,i) ;
        exergy.ME.ExDes_turbocharger(:,i) = exergy.ME.ca_bcomp(:,i) + exergy.ME.eg_bTC(:,i) - exergy.ME.ca_acomp(:,i) - exergy.ME.eg_aTC(:,i) ;
        exergy.ME.ExDes_cac_ht(:,i) = exergy.ME.ca_2cac(:,i) + exergy.ME.ht_ajwc(:,i) - exergy.ME.ca_incac(:,i) - exergy.ME.ht_acac(:,i) ;
        exergy.ME.ExDes_cac_lt(:,i) = exergy.ME.ca_incac(:,i) + exergy.ME.lt_bEng(:,i) - exergy.ME.ca_2eng(:,i) - exergy.ME.air_bypass(:,i) - exergy.ME.lt_acac(:,i) ;
        exergy.ME.ExDes_loc(:,i) = exergy.ME.lo_aEng(:,i) + exergy.ME.lt_acac(:,i) - exergy.ME.lo_bEng(:,i) - exergy.ME.lt_aloc(:,i) ;
        exergy.ME.ExDes_jwc(:,i) = exergy.ME.jwEng(:,i) + exergy.ME.ht_bEng(:,i) - exergy.ME.ht_ajwc(:,i) ;
        exergy.ME.ExDes_hrsg(:,i) = exergy.ME.eg_aTC(:,i) - exergy.ME.hrsg(:,i) - exergy.ME.eg_aHRSG(:,i) ;
        
     
        
    %% Auxiliary engines  
        
        %% Fuel and power
        exergy.AE.Power(:,i) = energy.AE.Power(:,i) ;
        exergy.AE.fuel_ch(:,i) = energy.AE.fuel_ch(:,i) * HHV / LHV ;
        exergy.AE.fuel_th(:,i) = energy.AE.fuel_th(:,i) - AE_Mfuel(:,i) .* T0 .* CP_HFO .* log(AE_Tfuel(:,i) ./ T0) ;
        exergy.AE.fuel(:,i) = exergy.AE.fuel_ch(:,i) + exergy.AE.fuel_th(:,i) ;
        %% Charge air
        exergy.AE.ca_bcomp(:,i) = energy.AE.ca_bcomp(:,i) - AE_Mca_bcomp(:,i) .* T0 .* CP_AIR .* log(T_ER ./ T0) ;
        exergy.AE.ca_acomp(:,i) = energy.AE.ca_acomp(:,i) - AE_Mca_bcomp(:,i) .* T0 .* CP_AIR .* log(AE_Tca_acomp(:,i) ./ T0) ;
        exergy.AE.ca_2eng(:,i) = energy.AE.ca_2eng(:,i) - AE_Mca_2eng(:,i) .* T0 .* CP_AIR .* log(AE_Tca(:,i) ./ T0) ;
        exergy.AE.ca_2cac(:,i) = energy.AE.ca_2cac(:,i) - AE_Mca_2eng(:,i) .* T0 .* CP_AIR .* log(AE_Tca_acomp(:,i) ./ T0) ;
        exergy.AE.air_bypass(:,i) = energy.AE.air_bypass(:,i) - AE_Mca_bypass(:,i) .* T0 .* CP_AIR .* log(AE_Tca_acomp(:,i) ./ T0) ;
        exergy.AE.ca_incac(:,i) = energy.AE.ca_incac(:,i) - AE_Mca_2eng(:,i) .* T0 .* CP_AIR .* log(AE_Tca_incac(:,i) ./ T0) ;
        %% Exhaust gas
        exergy.AE.eg_aEng(:,i) = energy.AE.eg_aEng(:,i) - AE_Meg_aEng(:,i) .* T0 .* CP_EG .* log(AE_Teg_aEng(:,i) ./ T0) ;
        exergy.AE.eg_bTC(:,i) = energy.AE.eg_bTC(:,i) - AE_Meg_TC(:,i) .* T0 .* CP_EG .* log(AE_Teg_bTC(:,i) ./ T0) ;
        exergy.AE.eg_aTC(:,i) = energy.AE.eg_aTC(:,i) - AE_Meg_TC(:,i) .* T0 .* CP_EG .* log(AE_Teg_aTC(:,i) ./ T0) ;
                AE_Msteam_hrsg(:,i) = energy.AE.hrsg(:,i) ./ DH_STEAM ;
        exergy.AE.hrsg(:,i) = AE_Msteam_hrsg(:,i) .* (DH_STEAM - T0 .* DS_STEAM) ;
        exergy.AE.steam_in(:,i) = AE_Msteam_hrsg(:,i) .* ((H_STEAM_LS - CP_W .* (T0 - 273.15)) - T0 .* (S_STEAM_LS - CP_W .* log(T0./273.15))) ;
        exergy.AE.steam_out(:,i) = AE_Msteam_hrsg(:,i) .* ((H_STEAM_VS - CP_W .* (T0 - 273.15)) - T0 .* (S_STEAM_VS - CP_W .* log(T0./273.15))) ;
        exergy.AE.eg_aHRSG(:,i) = energy.AE.eg_aHRSG(:,i) - AE_Meg_TC(:,i) .* T0 .* CP_EG .* log(AE_Teg_aHRSG(:,i) ./ T0) ;
        %% Cooling systems, source
        exergy.AE.lo_bEng(:,i) = energy.AE.lo_bEng(:,i) - AE_Mlo(:,i) .* CP_LO .* (AE_Tlo_bEng(:,i) ./ T0) ;
        exergy.AE.lo_aEng(:,i) = energy.AE.lo_aEng(:,i) - AE_Mlo(:,i) .* CP_LO .* (AE_Tlo_aEng(:,i) ./ T0) ;
        exergy.AE.jwEng(:,i) = energy.AE.jw(:,i) .* (1 - T0 / 423) ;
        %% Cooling systems, HT and LT
        exergy.AE.ht_bEng(:,i) = energy.AE.ht_bEng(:,i) - AE_Mht(:,i) .* CP_W .* (AE_Tht_bEng(:,i) ./ T0) ;
        exergy.AE.ht_ajwc(:,i) = energy.AE.ht_ajwc(:,i) - AE_Mht(:,i) .* CP_W .* (AE_Tht_ajwc(:,i) ./ T0) ;
        exergy.AE.ht_acac(:,i) = energy.AE.ht_acac(:,i) - AE_Mht(:,i) .* CP_W .* (AE_Tht_acac(:,i) ./ T0) ;
        exergy.AE.lt_bEng(:,i) = energy.AE.lt_bEng(:,i) - AE_Mlt(:,i) .* CP_W .* (AE_Tlt_bEng(:,i) ./ T0) ;
        exergy.AE.lt_acac(:,i) = energy.AE.lt_acac(:,i) - AE_Mlt(:,i) .* CP_W .* (AE_Tlt_acac(:,i) ./ T0) ;
        exergy.AE.lt_aloc(:,i) = energy.AE.lt_aloc(:,i) - AE_Mlt(:,i) .* CP_W .* (AE_Tlt_aloc(:,i) ./ T0) ;
        %% Exergy destruction
        exergy.AE.ExDes_cylinders(:,i) = exergy.AE.fuel(:,i) + exergy.AE.ca_2eng(:,i) - exergy.AE.Power(:,i) - exergy.AE.eg_aEng(:,i) - exergy.AE.jwEng(:,i) - (exergy.AE.lo_aEng(:,i) - exergy.AE.lo_bEng(:,i)) ;
        exergy.AE.ExDes_bypass(:,i) = exergy.AE.air_bypass(:,i) + exergy.AE.eg_aEng(:,i) - exergy.AE.eg_bTC(:,i) ;
        exergy.AE.ExDes_turbocharger(:,i) = exergy.AE.ca_bcomp(:,i) + exergy.AE.eg_bTC(:,i) - exergy.AE.ca_acomp(:,i) - exergy.AE.eg_aTC(:,i) ;
        exergy.AE.ExDes_cac_ht(:,i) = exergy.AE.ca_2cac(:,i) + exergy.AE.ht_ajwc(:,i) - exergy.AE.ca_incac(:,i) - exergy.AE.ht_acac(:,i) ;
        exergy.AE.ExDes_cac_lt(:,i) = exergy.AE.ca_incac(:,i) + exergy.AE.lt_bEng(:,i) - exergy.AE.ca_2eng(:,i) - exergy.AE.air_bypass(:,i) - exergy.AE.lt_acac(:,i) ;
        exergy.AE.ExDes_loc(:,i) = exergy.AE.lo_aEng(:,i) + exergy.AE.lt_acac(:,i) - exergy.AE.lo_bEng(:,i) - exergy.AE.lt_aloc(:,i) ;
        exergy.AE.ExDes_jwc(:,i) = exergy.AE.jwEng(:,i) + exergy.AE.ht_bEng(:,i) - exergy.AE.ht_ajwc(:,i) ;
        exergy.AE.ExDes_hrsg(:,i) = exergy.AE.eg_aTC(:,i) - exergy.AE.hrsg(:,i) - exergy.AE.eg_aHRSG(:,i) ;
end

%% For all energy flow values, the 5th column represents the sum of all the previous ones
temp_function = @(x) [x sum(x,2)] ;
exergy = structfunL2(exergy,temp_function) ;

