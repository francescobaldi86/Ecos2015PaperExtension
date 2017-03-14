% BirkaEA_cooling_systems
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% ANALYSIS OF THE FLOWS TO THE COOLING SYSTEMS %%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% This script analyses the flows in the cooling systems and stacks them for
% the two separate systems in the two engine rooms. 
%
%% Cooling systems
% The cooling systems are from now on organized as follows:
% Column 1 : Engine Room 1 (Engines 1 and 3)
% Column 2 : Engine Room 2 (Engines 2 and 4)
% Column 3: Sum of the two


%% Calculating the mass flows and fixed temperaturers
% HT cooling
mfr_HT(:,1) = AE_Mht(:,1) + AE_Mht(:,3) + ME_Mht(:,1) + ME_Mht(:,3) ;
mfr_HT(:,2) = AE_Mht(:,2) + AE_Mht(:,4) + ME_Mht(:,2) + ME_Mht(:,4) ;
T_ht_aEng(:,1) = T_HT_MAX * ones(n_data,1) ;
T_ht_aEng(:,2) = T_HT_MAX * ones(n_data,1) ;
% LT cooling
mfr_LT(:,1) = AE_Mlt(:,1) + AE_Mlt(:,3) + ME_Mlt(:,1) + ME_Mlt(:,3) ;
mfr_LT(:,2) = AE_Mlt(:,2) + AE_Mlt(:,4) + ME_Mlt(:,2) + ME_Mlt(:,4) ;
T_lt_bEng(:,1) = T_LTcooling(:,1) ;
T_lt_bEng(:,2) = T_LTcooling(:,2) ;


%% Energy flows for the HT cooling systems
% Net energy flow from the engines
energy.CoolingSystems.ht_eng(:,1) = energy.ME.ht(:,1) + energy.ME.ht(:,3) + energy.AE.ht(:,1) + energy.AE.ht(:,3) ;
energy.CoolingSystems.ht_eng(:,2) = energy.ME.ht(:,2) + energy.ME.ht(:,4) + energy.AE.ht(:,2) + energy.AE.ht(:,4) ;
energy.CoolingSystems.ht_eng(:,3) = energy.CoolingSystems.ht_eng(:,1) + energy.CoolingSystems.ht_eng(:,2) ;
% Net energy flow to the HTHR - NOTE: THE AVERAGE TOP-DOWN FLOW IS USED
energy.CoolingSystems.ht_hthr(:,1) = energy.Qdem.topDown_hthrAve .* energy.CoolingSystems.ht_eng(:,1) ./ energy.CoolingSystems.ht_eng(:,3) ;
energy.CoolingSystems.ht_hthr(:,2) = energy.Qdem.topDown_hthrAve .* energy.CoolingSystems.ht_eng(:,2) ./ energy.CoolingSystems.ht_eng(:,3) ;
energy.CoolingSystems.ht_hthr(:,3) = energy.Qdem.topDown_hthrAve ;
% Net energy flow from HT to LT
energy.CoolingSystems.ht2lt(:,1) = energy.CoolingSystems.ht_eng(:,1) - energy.CoolingSystems.ht_hthr(:,1) ;
energy.CoolingSystems.ht2lt(:,2) = energy.CoolingSystems.ht_eng(:,2) - energy.CoolingSystems.ht_hthr(:,2) ;
energy.CoolingSystems.ht2lt(:,3) = energy.CoolingSystems.ht_eng(:,3) - energy.CoolingSystems.ht_hthr(:,3) ;
% Enthalpy flow, after the engine
energy.CoolingSystems.ht_aEng(:,1) = mfr_HT(:,1) * CP_W .* (T_ht_aEng(:,1) - T0) ;
energy.CoolingSystems.ht_aEng(:,2) = mfr_HT(:,2) * CP_W .* (T_ht_aEng(:,2) - T0) ;
energy.CoolingSystems.ht_aEng(:,3) = energy.CoolingSystems.ht_aEng(:,1) + energy.CoolingSystems.ht_aEng(:,2) ;
% Enthalpy flow, before the engine
energy.CoolingSystems.ht_bEng(:,1) = energy.CoolingSystems.ht_aEng(:,1) - energy.CoolingSystems.ht_eng(:,1) ;
energy.CoolingSystems.ht_bEng(:,2) = energy.CoolingSystems.ht_aEng(:,2) - energy.CoolingSystems.ht_eng(:,2) ;
energy.CoolingSystems.ht_bEng(:,3) = energy.CoolingSystems.ht_bEng(:,1) + energy.CoolingSystems.ht_bEng(:,2) ;
% Enthalpy flow, after the HTHR system
energy.CoolingSystems.ht_aHthr(:,1) = energy.CoolingSystems.ht_aEng(:,1) - energy.CoolingSystems.ht_hthr(:,1) ;
energy.CoolingSystems.ht_aHthr(:,2) = energy.CoolingSystems.ht_aEng(:,2) -  energy.CoolingSystems.ht_hthr(:,2) ; 
energy.CoolingSystems.ht_aHthr(:,3) = energy.CoolingSystems.ht_aHthr(:,1) + energy.CoolingSystems.ht_aHthr(:,2) ;


%% Energy flows for the LT cooling systems
% Net flow from the engines
energy.CoolingSystems.lt_eng(:,1) = energy.AE.lt(:,1) + energy.AE.lt(:,3) + energy.ME.lt(:,1) + energy.ME.lt(:,3) ;
energy.CoolingSystems.lt_eng(:,2) = energy.AE.lt(:,2) + energy.AE.lt(:,4) + energy.ME.lt(:,2) + energy.ME.lt(:,4) ;
energy.CoolingSystems.lt_eng(:,3) = energy.CoolingSystems.lt_eng(:,1) + energy.CoolingSystems.lt_eng(:,2) ;
% Net flow to the Sea water cooling 
energy.CoolingSystems.lt2sw(:,1) = energy.CoolingSystems.lt_eng(:,1) + energy.CoolingSystems.ht2lt(:,1) ;
energy.CoolingSystems.lt2sw(:,2) = energy.CoolingSystems.lt_eng(:,2) + energy.CoolingSystems.ht2lt(:,2) ;
energy.CoolingSystems.lt2sw(:,3) = energy.CoolingSystems.lt_eng(:,3) + energy.CoolingSystems.ht2lt(:,3) ;
% Enthalpy flow, before the engine
energy.CoolingSystems.lt_bEng(:,1) = mfr_LT(:,1) * CP_W .* (T_lt_bEng(:,1) - T0) ;
energy.CoolingSystems.lt_bEng(:,2) = mfr_LT(:,2) * CP_W .* (T_lt_bEng(:,2) - T0) ;
energy.CoolingSystems.lt_bEng(:,3) = energy.CoolingSystems.lt_bEng(:,1) + energy.CoolingSystems.lt_bEng(:,2) ;
% Enthalpy flow, after the engine
energy.CoolingSystems.lt_aEng(:,1) = energy.CoolingSystems.lt_bEng(:,1) + energy.CoolingSystems.lt_eng(:,1) ;
energy.CoolingSystems.lt_aEng(:,2) = energy.CoolingSystems.lt_bEng(:,2) + energy.CoolingSystems.lt_eng(:,2) ;
energy.CoolingSystems.lt_aEng(:,3) = energy.CoolingSystems.lt_aEng(:,1) + energy.CoolingSystems.lt_aEng(:,2) ;
% Enthalpy flow, after the mixing with the HT cooling
energy.CoolingSystems.lt_aMix(:,1) = energy.CoolingSystems.lt_aEng(:,1) + energy.CoolingSystems.ht2lt(:,1) ;
energy.CoolingSystems.lt_aMix(:,2) = energy.CoolingSystems.lt_aEng(:,2) +  energy.CoolingSystems.ht2lt(:,2) ; 
energy.CoolingSystems.lt_aMix(:,3) = energy.CoolingSystems.lt_aMix(:,1) + energy.CoolingSystems.lt_aMix(:,2) ;


%% Intermediate calculations for exergy flows
% HT cooling
T_ht_bEng(:,1) = T_ht_aEng(:,1) - energy.CoolingSystems.ht_eng(:,1) ./ CP_W ./ mfr_HT(:,1) ;
T_ht_bEng(:,2) = T_ht_aEng(:,2) - energy.CoolingSystems.ht_eng(:,2) ./ CP_W ./ mfr_HT(:,2) ;
T_ht_aHthr(:,1) = T_ht_aEng(:,1) + energy.CoolingSystems.ht_hthr(:,1) ./ CP_W ./ mfr_HT(:,1) ;
T_ht_aHthr(:,2) = T_ht_aEng(:,2) + energy.CoolingSystems.ht_hthr(:,2) ./ CP_W ./ mfr_HT(:,2) ;
% LT cooling
T_lt_aEng(:,1) = T_lt_bEng(:,1) + energy.CoolingSystems.lt_eng(:,1) ./ CP_W ./ mfr_LT(:,1) ;
T_lt_aEng(:,2) = T_lt_bEng(:,2) + energy.CoolingSystems.lt_eng(:,2) ./ CP_W ./ mfr_LT(:,2) ;
T_lt_aMix(:,1) = T_lt_aEng(:,1) + energy.CoolingSystems.ht2lt(:,1) ./ CP_W ./ mfr_LT(:,1) ;
T_lt_aMix(:,2) = T_lt_aEng(:,2) + energy.CoolingSystems.ht2lt(:,2) ./ CP_W ./ mfr_LT(:,2) ;

%% Exergy flows, HT cooling
% HT exergy flow, before engine
exergy.CoolingSystems.ht_bEng(:,1) = energy.CoolingSystems.ht_bEng(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht_bEng(:,1) ./ T0) ;
exergy.CoolingSystems.ht_bEng(:,2) = energy.CoolingSystems.ht_bEng(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht_bEng(:,2) ./ T0) ;
    exergy.CoolingSystems.ht_bEng(isnan(exergy.CoolingSystems.ht_bEng(:,1)),1) = 0 ;
    exergy.CoolingSystems.ht_bEng(isnan(exergy.CoolingSystems.ht_bEng(:,2)),2) = 0 ;
exergy.CoolingSystems.ht_bEng(:,3) = exergy.CoolingSystems.ht_bEng(:,1) + exergy.CoolingSystems.ht_bEng(:,2) ;
% HT exergy flow, after engine
exergy.CoolingSystems.ht_aEng(:,1) = energy.CoolingSystems.ht_aEng(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht_aEng(:,1) ./ T0) ;
exergy.CoolingSystems.ht_aEng(:,2) = energy.CoolingSystems.ht_aEng(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht_aEng(:,2) ./ T0) ;
    exergy.CoolingSystems.ht_aEng(isnan(exergy.CoolingSystems.ht_aEng(:,1)),1) = 0 ;
    exergy.CoolingSystems.ht_aEng(isnan(exergy.CoolingSystems.ht_aEng(:,2)),2) = 0 ;
exergy.CoolingSystems.ht_aEng(:,3) = exergy.CoolingSystems.ht_aEng(:,1) + exergy.CoolingSystems.ht_aEng(:,2) ;
% HT exergy flow, after HTHR recovery
exergy.CoolingSystems.ht_aHthr(:,1) = energy.CoolingSystems.ht_aHthr(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht_aHthr(:,1) ./ T0) ;
exergy.CoolingSystems.ht_aHthr(:,2) = energy.CoolingSystems.ht_aHthr(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht_aHthr(:,2) ./ T0) ;
    exergy.CoolingSystems.ht_aHthr(isnan(exergy.CoolingSystems.ht_aHthr(:,1)),1) = 0 ;
    exergy.CoolingSystems.ht_aHthr(isnan(exergy.CoolingSystems.ht_aHthr(:,2)),2) = 0 ;
exergy.CoolingSystems.ht_aHthr(:,3) = exergy.CoolingSystems.ht_aHthr(:,1) + exergy.CoolingSystems.ht_aHthr(:,2) ;
% Net heat flow to the HT
exergy.CoolingSystems.ht_eng(:,1) = energy.CoolingSystems.ht_eng(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht_aEng(:,1) ./ T_ht_bEng(:,1)) ;
exergy.CoolingSystems.ht_eng(:,2) = energy.CoolingSystems.ht_eng(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht_aEng(:,2) ./ T_ht_bEng(:,2)) ;
    exergy.CoolingSystems.ht_eng(isnan(exergy.CoolingSystems.ht_eng(:,1)),1) = 0 ;
    exergy.CoolingSystems.ht_eng(isnan(exergy.CoolingSystems.ht_eng(:,2)),2) = 0 ;
exergy.CoolingSystems.ht_eng(:,3) = exergy.CoolingSystems.ht_eng(:,1) + exergy.CoolingSystems.ht_eng(:,2) ;
% Net HT - HR flow to recovery
exergy.CoolingSystems.ht_hthr(:,1) = energy.CoolingSystems.ht_hthr(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht_aEng(:,1) ./ T_ht_aHthr(:,1)) ;
exergy.CoolingSystems.ht_hthr(:,2) = energy.CoolingSystems.ht_hthr(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht_aEng(:,2) ./ T_ht_aHthr(:,2)) ;
    exergy.CoolingSystems.ht_hthr(isnan(exergy.CoolingSystems.ht_hthr(:,1)),1) = 0 ;
    exergy.CoolingSystems.ht_hthr(isnan(exergy.CoolingSystems.ht_hthr(:,2)),2) = 0 ;
exergy.CoolingSystems.ht_hthr(:,3) = exergy.CoolingSystems.ht_hthr(:,1) + exergy.CoolingSystems.ht_hthr(:,2) ;
% Net HT -> LT flow
exergy.CoolingSystems.ht2lt(:,1) = energy.CoolingSystems.ht2lt(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht_aHthr(:,1) ./ T_ht_bEng(:,1)) ;
exergy.CoolingSystems.ht2lt(:,2) = energy.CoolingSystems.ht2lt(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht_aHthr(:,2) ./ T_ht_bEng(:,2)) ;
exergy.CoolingSystems.ht2lt(isnan(exergy.CoolingSystems.ht2lt(:,1)),1) = 0 ;
exergy.CoolingSystems.ht2lt(isnan(exergy.CoolingSystems.ht2lt(:,2)),2) = 0 ;
exergy.CoolingSystems.ht2lt(:,3) = exergy.CoolingSystems.ht2lt(:,1) + exergy.CoolingSystems.ht2lt(:,2) ;

%% Exergy flows, LT cooling
% Net flow from the main engines
exergy.CoolingSystems.lt_eng(:,1) = energy.CoolingSystems.lt_eng(:,1) - mfr_LT(:,1) .* T0 .* CP_W .* log(T_lt_aEng(:,1) ./ T_lt_bEng(:,1)) ;
exergy.CoolingSystems.lt_eng(:,2) = energy.CoolingSystems.lt_eng(:,2) - mfr_LT(:,2) .* T0 .* CP_W .* log(T_lt_aEng(:,2) ./ T_lt_bEng(:,2)) ;
    exergy.CoolingSystems.lt_eng(isnan(exergy.CoolingSystems.lt_eng(:,1)),1) = 0 ;
    exergy.CoolingSystems.lt_eng(isnan(exergy.CoolingSystems.lt_eng(:,2)),2) = 0 ;
exergy.CoolingSystems.lt_eng(:,3) = exergy.CoolingSystems.lt_eng(:,1) + exergy.CoolingSystems.lt_eng(:,2) ;
% LT exergy flow, engine inlet
exergy.CoolingSystems.lt_bEng(:,1) = energy.CoolingSystems.lt_bEng(:,1) - mfr_LT(:,1) .* T0 .* CP_W .* log(T_lt_bEng(:,1) ./ T0) ;
exergy.CoolingSystems.lt_bEng(:,2) = energy.CoolingSystems.lt_bEng(:,2) - mfr_LT(:,2) .* T0 .* CP_W .* log(T_lt_bEng(:,2) ./ T0) ;
    exergy.CoolingSystems.lt_bEng(isnan(exergy.CoolingSystems.lt_bEng(:,1)),1) = 0 ;
    exergy.CoolingSystems.lt_bEng(isnan(exergy.CoolingSystems.lt_bEng(:,2)),2) = 0 ;
exergy.CoolingSystems.lt_bEng(:,3) = exergy.CoolingSystems.lt_bEng(:,1) + exergy.CoolingSystems.lt_bEng(:,2) ;
% LT exergy flow, engine outlet
exergy.CoolingSystems.lt_aEng(:,1) = energy.CoolingSystems.lt_aEng(:,1) - mfr_LT(:,1) .* T0 .* CP_W .* log(T_lt_aEng(:,1) ./ T0) ;
exergy.CoolingSystems.lt_aEng(:,2) = energy.CoolingSystems.lt_aEng(:,2) - mfr_LT(:,2) .* T0 .* CP_W .* log(T_lt_aEng(:,2) ./ T0) ;
    exergy.CoolingSystems.lt_aEng(isnan(exergy.CoolingSystems.lt_aEng(:,1)),1) = 0 ;
    exergy.CoolingSystems.lt_aEng(isnan(exergy.CoolingSystems.lt_aEng(:,2)),2) = 0 ;
exergy.CoolingSystems.lt_aEng(:,3) = exergy.CoolingSystems.lt_aEng(:,1) + exergy.CoolingSystems.lt_aEng(:,2) ;
% LT exergy flow, after mixing
exergy.CoolingSystems.lt_aMix(:,1) = energy.CoolingSystems.lt_aMix(:,1) - mfr_LT(:,1) .* T0 .* CP_W .* log(T_lt_aMix(:,1) ./ T0) ;
exergy.CoolingSystems.lt_aMix(:,2) = energy.CoolingSystems.lt_aMix(:,2) - mfr_LT(:,2) .* T0 .* CP_W .* log(T_lt_aMix(:,2) ./ T0) ;
    exergy.CoolingSystems.lt_aMix(isnan(exergy.CoolingSystems.lt_aMix(:,1)),1) = 0 ;
    exergy.CoolingSystems.lt_aMix(isnan(exergy.CoolingSystems.lt_aMix(:,2)),2) = 0 ;
exergy.CoolingSystems.lt_aMix(:,3) = exergy.CoolingSystems.lt_aMix(:,1) + exergy.CoolingSystems.lt_aMix(:,2) ;
    
% %% SW cooling
%     energy.cooling.sw(:,1) = energy.cooling.lt_2_sw(:,1) ;
%     energy.cooling.sw(:,2) = energy.cooling.lt_2_sw(:,2) ;
%     energy.cooling.sw(:,3) = energy.cooling.lt_2_sw(:,3) ;
% mfr_SW(:,1) = energy.cooling.sw(:,1) ./ CP_W ./ (T_SWcooling(:,1) - T0) ;
% mfr_SW(:,2) = energy.cooling.sw(:,2) ./ CP_W ./ (T_SWcooling(:,2) - T0) ;
% mfr_SW(:,3) = mfr_SW(:,1)  + mfr_SW(:,2) ;
%     exergy.cooling.sw(:,1) = energy.cooling.sw(:,1) - mfr_SW(:,1) .* T0 .* CP_W .* log(T_SWcooling(:,1) ./ T0) ;
%     exergy.cooling.sw(:,2) = energy.cooling.sw(:,2) - mfr_SW(:,2) .* T0 .* CP_W .* log(T_SWcooling(:,2) ./ T0) ;
%     exergy.cooling.sw(isnan(exergy.cooling.sw(:,1)),1) = 0 ;
%     exergy.cooling.sw(isnan(exergy.cooling.sw(:,2)),2) = 0 ;
%     exergy.cooling.sw(:,3) = exergy.cooling.sw(:,1) + exergy.cooling.sw(:,2) ;
    
%% Concluding the heat demand part
% exergy.demand.heat_ht = energy.CoolingSystems.ht_hthr(:,3) ;
% exergy.demand.total_heat = energy.Qdem.topDown_hrsgME + energy.Qdem.topDown_hrsgAE + energy.Qdem.topDown_AB + energy.Qdem.topDown_hthrAve ;