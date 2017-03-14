%% BirkaEA_main_engines_efficiency %%

% Initialising variables for speed
BirkaEA2_variable_initialisation_energy 

% Correction factor for main / auxiliary engines power and load based on
% the comparison with the fuel meter
% BirkaEA_fuel_consumption_correction_AE3onDiesel
%% NOTE: THE CORRECTION IS FIXED TO 1.15 TO AVOID STRANGE THINGS
%% THE ANALYSIS IS BASED ON THE ABOVE SCRIPT
% See the constant ME_ETA_CORR, AE_ETA_CORR

for i = 1 : 4
    %% Main engines
    %% Power - fuel flow - efficiency
    ME_load(:,i) = smoothCircularTransition(ME_POLY_PCA_2_LOAD(1,:),ME_POLY_PCA_2_LOAD(2,:),ME_POLY_PCA_2_LOAD(3,1),ME_pca(:,i)-1,4) * 0.95 ;
    ME_Power(:,i) = ME_load(:,i) * MCR_ME ;
    ME_bsfc_ISO(:,i) = polyval(ME_POLY_LOAD_2_ISO_BSFC,ME_load(:,i)) ;
    ME_bsfc(:,i) = bsfcISOCorrection(ME_bsfc_ISO(:,i) , ME_Tlt_bEng(:,i) , ME_Tca(:,i) , LHV , 0.8) * ME_ETA_CORR ;
    ME_Mfuel(:,i) = ME_Power(:,i) .* ME_bsfc(:,i) ./ 3.6e6 ; % In kg/s
    ME_Mfuel_ISO(:,i) = ME_Power(:,i) .* ME_bsfc_ISO(:,i) ./ 3.6e6 ; % In kg/s
                energy.ME.Power(:,i) = ME_Power(:,i) ;
                energy.ME.fuel_ch(:,i) = ME_Mfuel(:,i) * LHV ; 
                energy.ME.fuel_th(:,i) = ME_Mfuel(:,i) .* CP_HFO .* (ME_Tfuel(:,i) - T0) ;
                energy.ME.fuel(:,i) = energy.ME.fuel_ch(:,i) + energy.ME.fuel_th(:,i) ;
    
    %% Air flows
    ME_Tca_acomp(:,i) = T_ER .* (1 + (ME_pca(:,i).^((K_AIR-1)/K_AIR) - 1) ./ polyval(ME_POLY_PIN_2_ETA_IS,ME_pca(:,i))) ;
    ME_Mca_2eng(:,i) = ME_V_MAX .* ME_pca(:,1)*1e5 ./ R_AIR ./ ME_Tca(:,1) .* ME_rpm(:,i) / 60 / 2 * ETA_VOL * ME_N_CYL .* ME_on(:,i) ; 
    ME_Meg_aEng(:,i) = ME_Mca_2eng(:,i) + ME_Mfuel(:,i) ;
    ME_Mca_bypass(:,i) = (ME_Meg_aEng(:,i) .* CP_EG .* (ME_Teg_aEng(:,i) - ME_Teg_aTC(:,i)) - ME_Mca_2eng(:,i) .* CP_AIR ./ ETA_MECH_TC .* (ME_Tca_acomp(:,i) - T_ER)) ./ ...
        (CP_EG .* ME_Teg_aTC(:,i) - CP_AIR .* T_ER + 298*(CP_AIR-CP_EG)) ;
    ME_Meg_TC(:,i) = ME_Meg_aEng(:,i) + ME_Mca_bypass(:,i) ;
    ME_Mca_bcomp(:,i) = (ME_Mca_2eng(:,i) + ME_Mca_bypass(:,i)) ;
    ME_Teg_bTC(:,i) = ME_Teg_aTC(:,i) + (ME_Mca_bcomp(:,i) .* CP_AIR .* (ME_Tca_acomp(:,i) - T_ER)) ./ ETA_MECH_TC ./ CP_EG ./ ME_Meg_TC(:,i) ;    
    %% Energy in the air flows
            energy.ME.ca_bcomp(:,i) = ME_Mca_bcomp(:,i) .* CP_AIR .* (T_ER - T0) ; % Inlet flow, at Engine Room temperature
            energy.ME.ca_acomp(:,i) = ME_Mca_bcomp(:,i) .* CP_AIR .* (ME_Tca_acomp(:,i) - T0) ; % After the compressor, at high temperature
            energy.ME.ca_2cac(:,i) = ME_Mca_2eng(:,i) .* CP_AIR .* (ME_Tca_acomp(:,i) - T0) ; 
            energy.ME.ca_2eng(:,i) = ME_Mca_2eng(:,i) .* CP_AIR .* (ME_Tca(:,i) - T0) ; % After the CAC, at low temperature again
            energy.ME.air_bypass(:,i) = ME_Mca_bypass(:,i) .* CP_AIR .* (ME_Tca_acomp(:,i) - T0) ; 
    %% Energy in the exhaust gas flows
            energy.ME.eg_aEng(:,i) = ME_Meg_aEng(:,i) .* CP_EG .* (ME_Teg_aEng(:,i) - T0) ; % After engine, before merging
            energy.ME.eg_bTC(:,i) = ME_Meg_TC(:,i) .* CP_EG .* (ME_Teg_bTC(:,i) - T0) ; % After engine, before TC (and after merging with the air bypass)
            energy.ME.eg_aTC(:,i) = ME_Meg_TC(:,i) .* CP_EG .* (ME_Teg_aTC(:,i) - T0) ; % After engine, after TC (and after merging with the air bypass)
    if (i == 2) || (i == 3)
            energy.ME.eg_aHRSG(:,i) = ME_Meg_TC(:,i) .* CP_EG .* (ME_Teg_aHRSG(:,i) - T0) ; % After TC, after ExBo
            energy.ME.hrsg(:,i) = energy.ME.eg_aTC(:,i) - energy.ME.eg_aHRSG(:,i) ;
    else
            energy.ME.eg_aHRSG(:,i) = energy.ME.eg_aTC(:,i) ;
            energy.ME.hrsg(:,i) = zeros(n_data,1) ;
    end
     %% Energy to cooling systems
            energy.ME.cac(:,i) = ME_Mca_2eng(:,i) .* CP_AIR .* (ME_Tca_acomp(:,i) - ME_Tca(:,i)) ;
            energy.ME.cac_ht(:,i) = CP_AIR .* ME_Mca_2eng(:,i) .* (ME_Tca_acomp(:,i) - ME_Tht_bEng(:,i)) .* polyval(ME_POLY_LOAD_2_EPS_CACHT,ME_load(:,i)) ;
    ME_Tca_incac(:,i) = ME_Tca_acomp(:,i) - energy.ME.cac_ht(:,i) ./ ME_Mca_2eng(:,i) ./ CP_AIR ;
    ME_Tca_incac(isnan(ME_Tca_incac(:,i)),i) = 0 ;
            energy.ME.ca_incac(:,i) = ME_Mca_2eng(:,i) .* CP_AIR .* (ME_Tca_incac(:,i) - T0) ; % Intermediate flow, between the HT and LT stage of the CAC
            energy.ME.cac_lt(:,i) = energy.ME.cac(:,i) - energy.ME.cac_ht(:,i) ;
            energy2cooling = energy.ME.fuel(:,i) + energy.ME.ca_bcomp(:,i) - energy.ME.Power(:,i) - energy.ME.eg_aTC(:,i) ;            
            energy.ME.ht(:,i) = energy2cooling .* (polyval(ME_POLY_LOAD_2_QDOT_HT,ME_load(:,i)) ./ (polyval(ME_POLY_LOAD_2_QDOT_HT,ME_load(:,i)) + polyval(ME_POLY_LOAD_2_QDOT_LT,ME_load(:,i))) + 0.1238) ;
            energy.ME.lt(:,i) = energy2cooling - energy.ME.ht(:,i) ;
            energy.ME.jw(:,i) = energy.ME.ht(:,i) - energy.ME.cac_ht(:,i) ;
            energy.ME.lo(:,i) = energy.ME.lt(:,i) - energy.ME.cac_lt(:,i) ;
     %% Cooling systems flows
     ME_Mht(:,i) = ME_MFR_HT .* ME_rpm(:,i) / RPM_DES_ME ; % Here we make the assumption that the mass flow rate of HT cooling water in the main engines is linearly proportional to the engine laod...
     ME_Mlt(:,i) = ME_MFR_LT .* ME_rpm(:,i) / RPM_DES_ME ; % Here we make the assumption that the mass flow rate of LT cooling water in the main engines is linearly proportional to the engine laod...
     ME_Mlo(:,i) = ME_MFR_LO .* ME_rpm(:,i) / RPM_DES_ME ;
     ME_Tht_ajwc(:,i) = ME_Tht_bEng(:,i) + energy.ME.jw(:,i) ./ ME_Mht(:,i) / CP_W ;
        ME_Tht_ajwc(isnan(ME_Tht_ajwc(:,i)),i) = 0 ;
     ME_Tht_acac(:,i) = ME_Tht_ajwc(:,i) + energy.ME.cac_ht(:,i) ./ ME_Mht(:,i) / CP_W ;    
        ME_Tht_acac(isnan(ME_Tht_acac(:,i)),i) = 0 ;
     ME_Tlt_acac(:,i) = ME_Tlt_bEng(:,i) + energy.ME.cac_lt(:,i) ./ ME_Mlt(:,i) / CP_W ;
        ME_Tlt_acac(isnan(ME_Tlt_acac(:,i)),i) = 0 ;
     ME_Tlt_aloc(:,i) = ME_Tlt_acac(:,i) + energy.ME.lo(:,i) ./ ME_Mlt(:,i) / CP_W ;
        ME_Tlt_aloc(isnan(ME_Tlt_aloc(:,i)),i) = 0 ;
     ME_Tlo_aEng(:,i) = ME_Tlo_bEng(:,i) + energy.ME.lo(:,i) ./ ME_Mlo(:,i) / CP_LO ;  
        ME_Tlo_aEng(isnan(ME_Tlo_aEng(:,i)),i) = 0 ;
            energy.ME.ht_bEng(:,i) = ME_Mht(:,i) .* CP_W .* (ME_Tht_bEng(:,i) - T0) ;
            energy.ME.ht_ajwc(:,i) = ME_Mht(:,i) .* CP_W .* (ME_Tht_ajwc(:,i) - T0) ;
            energy.ME.ht_acac(:,i) = ME_Mht(:,i) .* CP_W .* (ME_Tht_acac(:,i) - T0) ;
            energy.ME.lt_bEng(:,i) = ME_Mlt(:,i) .* CP_W .* (ME_Tlt_bEng(:,i) - T0) ;
            energy.ME.lt_acac(:,i) = ME_Mlt(:,i) .* CP_W .* (ME_Tlt_acac(:,i) - T0) ;
            energy.ME.lt_aloc(:,i) = ME_Mlt(:,i) .* CP_W .* (ME_Tlt_aloc(:,i) - T0) ;
            energy.ME.lo_bEng(:,i)= ME_Mlo(:,i) .* CP_LO .* (ME_Tlo_bEng(:,i) - T0) ;
            energy.ME.lo_aEng(:,i)= ME_Mlo(:,i) .* CP_LO .* (ME_Tlo_aEng(:,i) - T0) ;
     %
     %
     %
     %
     %
     %
     %
     %
     %% Auxiliary engines
    AE_Power(:,i) = AE_PowerEl(:,i) / AE_ETA_SG ;
    AE_load(:,i) = AE_Power(:,i) / MCR_AE ;
    AE_bsfc_ISO(:,i) = polyval(AE_POLY_LOAD_2_ISO_BSFC,AE_load(:,i)) ;
    AE_bsfc(:,i) = bsfcISOCorrection(AE_bsfc_ISO(:,i) , AE_Tlt_bEng(:,i) , AE_Tca(:,i) , LHV , 0.8) * AE_ETA_CORR ;
    AE_Mfuel(:,i) = AE_Power(:,i) .* AE_bsfc(:,i) ./ 3.6e6 ; % In kg/s
    AE_Mfuel_ISO(:,i) = AE_Power(:,i) .* AE_bsfc_ISO(:,i) ./ 3.6e6 ; % In kg/s
                energy.AE.Power(:,i) = AE_Power(:,i) ;
                energy.AE.PowerEl(:,i) = AE_PowerEl(:,i) ;
                energy.AE.fuel_ch(:,i) = AE_Mfuel(:,i) * LHV ; 
                energy.AE.fuel_th(:,i) = AE_Mfuel(:,i) .* CP_HFO .* (AE_Tfuel(:,i) - T0) ;
                energy.AE.fuel(:,i) = energy.AE.fuel_ch(:,i) + energy.AE.fuel_th(:,i) ;
    
    %% Air flows
    AE_Tca_acomp(:,i) = T_ER .* (1 + (AE_pca(:,i).^((K_AIR-1)/K_AIR) - 1) ./ polyval(AE_POLY_PIN_2_ETA_IS,AE_pca(:,i))) ;
    AE_Mca_2eng(:,i) = AE_V_MAX .* AE_pca(:,1)*1e5 ./ R_AIR ./ AE_Tca(:,1) .* AE_rpm(:,i) / 60 / 2 * ETA_VOL * AE_N_CYL .* AE_on(:,i) ; 
    AE_Meg_aEng(:,i) = AE_Mca_2eng(:,i) + AE_Mfuel(:,i) ;
    AE_Mca_bypass(:,i) = (AE_Meg_aEng(:,i) .* CP_EG .* (AE_Teg_aEng(:,i) - AE_Teg_aTC(:,i)) - AE_Mca_2eng(:,i) .* CP_AIR ./ ETA_MECH_TC .* (AE_Tca_acomp(:,i) - T_ER)) ./ ...
        (CP_EG .* AE_Teg_aTC(:,i) - CP_AIR .* T_ER + 298*(CP_AIR-CP_EG)) ;
    AE_Meg_TC(:,i) = AE_Meg_aEng(:,i) + AE_Mca_bypass(:,i) ;
    AE_Mca_bcomp(:,i) = (AE_Mca_2eng(:,i) + AE_Mca_bypass(:,i)) ;
    AE_Teg_bTC(:,i) = AE_Teg_aTC(:,i) + (AE_Mca_bcomp(:,i) .* CP_AIR .* (AE_Tca_acomp(:,i) - T_ER)) ./ ETA_MECH_TC ./ CP_EG ./ AE_Meg_TC(:,i) ;    
    %% Energy in the air flows
            energy.AE.ca_bcomp(:,i) = AE_Mca_bcomp(:,i) .* CP_AIR .* (T_ER - T0) ; % Inlet flow, at Engine Room temperature
            energy.AE.ca_acomp(:,i) = AE_Mca_bcomp(:,i) .* CP_AIR .* (AE_Tca_acomp(:,i) - T0) ; % After the compressor, at high temperature
            energy.AE.ca_2eng(:,i) = AE_Mca_2eng(:,i) .* CP_AIR .* (AE_Tca(:,i) - T0) ; % After the CAC, at low temperature again
            energy.AE.ca_2cac(:,i) = AE_Mca_2eng(:,i) .* CP_AIR .* (AE_Tca_acomp(:,i) - T0) ; 
            energy.AE.air_bypass(:,i) = AE_Mca_bypass(:,i) .* CP_AIR .* (AE_Tca_acomp(:,i) - T0) ; 
    %% Energy in the exhaust gas flows
            energy.AE.eg_aEng(:,i) = AE_Meg_aEng(:,i) .* CP_EG .* (AE_Teg_aEng(:,i) - T0) ; % After engine, before merging
            energy.AE.eg_bTC(:,i) = AE_Meg_TC(:,i) .* CP_EG .* (AE_Teg_bTC(:,i) - T0) ; % After engine, before TC (and after merging with the air bypass)
            energy.AE.eg_aTC(:,i) = AE_Meg_TC(:,i) .* CP_EG .* (AE_Teg_aTC(:,i) - T0) ; % After engine, after TC (and after merging with the air bypass)
    if (i == 2) || (i == 3)
            energy.AE.eg_aHRSG(:,i) = AE_Meg_TC(:,i) .* CP_EG .* (AE_Teg_aHRSG(:,i) - T0) ; % After TC, after ExBo
            energy.AE.hrsg(:,i) = energy.AE.eg_aTC(:,i) - energy.AE.eg_aHRSG(:,i) ;
    else
            energy.AE.eg_aHRSG(:,i) = energy.AE.eg_aTC(:,i) ;
            energy.AE.hrsg(:,i) = zeros(n_data,1) ;
    end
     %% Energy to cooling systems
            energy.AE.cac(:,i) = AE_Mca_2eng(:,i) .* CP_AIR .* (AE_Tca_acomp(:,i) - AE_Tca(:,i)) ;
            energy.AE.cac_ht(:,i) = CP_AIR .* AE_Mca_2eng(:,i) .* (AE_Tca_acomp(:,i) - AE_Tht_bEng(:,i)) .* polyval(ME_POLY_LOAD_2_EPS_CACHT,AE_load(:,i)) ;
    AE_Tca_incac(:,i) = AE_Tca_acomp(:,i) - energy.AE.cac_ht(:,i) ./ AE_Mca_2eng(:,i) ./ CP_AIR ;
        AE_Tca_incac(isnan(AE_Tca_incac(:,i)),i) = 0 ;
            energy.AE.ca_incac(:,i) = AE_Mca_2eng(:,i) .* CP_AIR .* (AE_Tca_incac(:,i) - T0) ; % After the CAC, at low temperature again        
            energy.AE.cac_lt(:,i) = energy.AE.cac(:,i) - energy.AE.cac_ht(:,i) ;
            energy2cooling = energy.AE.fuel(:,i) + energy.AE.ca_bcomp(:,i) - energy.AE.Power(:,i) - energy.AE.eg_aTC(:,i) ;            
            energy.AE.ht(:,i) = energy2cooling .* (polyval(AE_POLY_LOAD_2_QDOT_HT,AE_load(:,i)) ./ (polyval(AE_POLY_LOAD_2_QDOT_HT,AE_load(:,i)) + polyval(AE_POLY_LOAD_2_QDOT_LT,AE_load(:,i))) + 0.1238) ;
            energy.AE.lt(:,i) = energy2cooling - energy.AE.ht(:,i) ;
            energy.AE.jw(:,i) = energy.AE.ht(:,i) - energy.AE.cac_ht(:,i) ;
            energy.AE.lo(:,i) = energy.AE.lt(:,i) - energy.AE.cac_lt(:,i) ;
     %% Cooling systems flows
     AE_Mht(:,i) = AE_MFR_HT .* AE_rpm(:,i) / RPM_DES_AE ; % Here we make the assumption that the mass flow rate of HT cooling water in the main engines is linearly proportional to the engine laod...
     AE_Mlt(:,i) = AE_MFR_LT .* AE_rpm(:,i) / RPM_DES_AE ; % Here we make the assumption that the mass flow rate of LT cooling water in the main engines is linearly proportional to the engine laod...
     AE_Mlo(:,i) = AE_MFR_LO .* AE_rpm(:,i) / RPM_DES_AE ;
     AE_Tht_ajwc(:,i) = AE_Tht_bEng(:,i) + energy.AE.jw(:,i) ./ AE_Mht(:,i) / CP_W ;
        AE_Tht_ajwc(isnan(AE_Tht_ajwc(:,i)),i) = 0 ;
     AE_Tht_acac(:,i) = AE_Tht_ajwc(:,i) + energy.AE.cac_ht(:,i) ./ AE_Mht(:,i) / CP_W ; 
        AE_Tht_ajwc(isnan(AE_Tht_ajwc(:,i)),i) = 0 ;
     AE_Tlt_acac(:,i) = AE_Tlt_bEng(:,i) + energy.AE.cac_lt(:,i) ./ AE_Mlt(:,i) / CP_W ;
        AE_Tht_ajwc(isnan(AE_Tht_ajwc(:,i)),i) = 0 ;
     AE_Tlt_aloc(:,i) = AE_Tlt_acac(:,i) + energy.AE.lo(:,i) ./ AE_Mlt(:,i) / CP_W ;
        AE_Tht_ajwc(isnan(AE_Tht_ajwc(:,i)),i) = 0 ;
     AE_Tlo_bEng(:,i) = AE_Tlo_aEng(:,i) - energy.AE.lo(:,i) ./ AE_Mlo(:,i) / CP_LO ;
        AE_Tht_ajwc(isnan(AE_Tht_ajwc(:,i)),i) = 0 ;
            energy.AE.ht_bEng(:,i) = AE_Mht(:,i) .* CP_W .* (AE_Tht_bEng(:,i) - T0) ;
            energy.AE.ht_ajwc(:,i) = AE_Mht(:,i) .* CP_W .* (AE_Tht_ajwc(:,i) - T0) ;
            energy.AE.ht_acac(:,i) = AE_Mht(:,i) .* CP_W .* (AE_Tht_acac(:,i) - T0) ;
            energy.AE.lt_bEng(:,i) = AE_Mlt(:,i) .* CP_W .* (AE_Tlt_bEng(:,i) - T0) ;
            energy.AE.lt_acac(:,i) = AE_Mlt(:,i) .* CP_W .* (AE_Tlt_acac(:,i) - T0) ;
            energy.AE.lt_aloc(:,i) = AE_Mlt(:,i) .* CP_W .* (AE_Tlt_aloc(:,i) - T0) ;
            energy.AE.lo_bEng(:,i)= AE_Mlo(:,i) .* CP_LO .* (AE_Tlo_bEng(:,i) - T0) ;
            energy.AE.lo_aEng(:,i)= AE_Mlo(:,i) .* CP_LO .* (AE_Tlo_aEng(:,i) - T0) ;
            

            
            
       
%     %% Eliminating NaN values from when the engine is off
%         energy_ME_fieldnames = fieldnames(energy.ME) ;
%         for k = 1 : length(energy_ME_fieldnames)
%             energy.ME.(char(energy_ME_fieldnames(k)))(ME_on.(char(ME_names(i))) == 0,i) = 0 ;
%         end
%         energy_AE_fieldnames = fieldnames(energy.AE) ;
%         for k = 1 : length(energy_AE_fieldnames)
%             energy.AE.(char(energy_AE_fieldnames(k)))(AE_on.(char(AE_names(i))) == 0,i) = 0 ;
%         end
%     
%         
end

%% Some cleaning
cleaning_function_ME = @(x) structure_binary_cleaning(x,ME_on(:,1:4)) ;
cleaning_function_AE = @(x) structure_binary_cleaning(x,AE_on(:,1:4)) ;
energy.ME = structfun(cleaning_function_ME , energy.ME , 'UniformOutput' , false) ; % Setting to zero all energy flows when the engines are off 
energy.AE = structfun(cleaning_function_AE , energy.AE , 'UniformOutput' , false) ; % Setting to zero all energy flows when the engines are off

%% Various energy losses
energy.Losses.gearBox = sum(energy.ME.Power,2) * (1 - ETA_GB) ;
energy.Losses.generators = sum(energy.AE.Power,2) - sum(energy.AE.PowerEl,2) ;
energy.Losses.shaft = sum(energy.ME.Power,2) * ETA_GB * (1 - ETA_SHAFT) ;

%% For all energy flow values, the 5th column represents the sum of all the previous ones
temp_function = @(x) [x sum(x,2)] ;
energy = structfunL2(energy,temp_function) ;











        