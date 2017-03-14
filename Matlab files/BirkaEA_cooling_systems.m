% BirkaEA_cooling_systems

%% Cooling systems
% The cooling systems are from now on organized as follows:
% Column 1 : Engine Room 1 (Engines 1 and 3)
% Column 2 : Engine Room 2 (Engines 2 and 4)
% Column 3: Sum of the two

%% HT Cooling
mfr_HT(:,1) = AE_mfr_ht(:,1) + AE_mfr_ht(:,3) + ME_mfr_ht(:,1) + ME_mfr_ht(:,3) ;
mfr_HT(:,2) = AE_mfr_ht(:,2) + AE_mfr_ht(:,4) + ME_mfr_ht(:,2) + ME_mfr_ht(:,4) ;
    energy.cooling.ht(:,1) = energy.AE.ht(:,1) + energy.AE.ht(:,3) + energy.ME.ht(:,1) + energy.ME.ht(:,3) ;
    energy.cooling.ht(:,2) = energy.AE.ht(:,2) + energy.AE.ht(:,4) + energy.ME.ht(:,2) + energy.ME.ht(:,4) ;
    energy.cooling.ht(:,3) = energy.cooling.ht(:,1) + energy.cooling.ht(:,2) ;
    energy.cooling.ht_heat(:,1) = energy.demand.heat_ht .* energy.cooling.ht(:,1) ./ energy.cooling.ht(:,3) ;
    energy.cooling.ht_heat(:,2) = energy.demand.heat_ht .* energy.cooling.ht(:,2) ./ energy.cooling.ht(:,3) ;
    energy.cooling.ht_heat(isnan(energy.cooling.ht_heat(:,1)),1) = 0 ;
    energy.cooling.ht_heat(isnan(energy.cooling.ht_heat(:,2)),2) = 0 ;
    energy.cooling.ht_heat(:,3) = energy.cooling.ht_heat(:,1) + energy.cooling.ht_heat(:,2) ;
    energy.cooling.ht_2_lt(:,1) = energy.cooling.ht(:,1) - energy.cooling.ht_heat(:,1) ;
    energy.cooling.ht_2_lt(:,2) = energy.cooling.ht(:,2) - energy.cooling.ht_heat(:,2) ;
    energy.cooling.ht_2_lt(:,3) = energy.cooling.ht(:,3) - energy.cooling.ht_heat(:,3) ;
T_ht2(:,1) = T_HT_MAX * ones(n_data,1) ;
T_ht2(:,2) = T_HT_MAX * ones(n_data,1) ;
T_ht1(:,1) = T_ht2(:,1) - energy.cooling.ht(:,1) ./ CP_W ./ mfr_HT(:,1) ;
T_ht1(:,2) = T_ht2(:,2) - energy.cooling.ht(:,2) ./ CP_W ./ mfr_HT(:,2) ;
T_ht3(:,1) = T_ht2(:,1) - energy.cooling.ht_heat(:,1) ./ CP_W ./ mfr_HT(:,1) ;
T_ht3(:,2) = T_ht2(:,2) - energy.cooling.ht_heat(:,2) ./ CP_W ./ mfr_HT(:,2) ;
    exergy.cooling.ht(:,1) = energy.cooling.ht(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht2(:,1) ./ T_ht1(:,1)) ;
    exergy.cooling.ht(:,2) = energy.cooling.ht(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht2(:,2) ./ T_ht1(:,2)) ;
    exergy.cooling.ht(isnan(exergy.cooling.ht(:,1)),1) = 0 ;
    exergy.cooling.ht(isnan(exergy.cooling.ht(:,2)),2) = 0 ;
    exergy.cooling.ht(:,3) = exergy.cooling.ht(:,1) + exergy.cooling.ht(:,2) ;
    exergy.cooling.ht_heat(:,1) = energy.cooling.ht_heat(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht2(:,1) ./ T_ht3(:,1)) ;
    exergy.cooling.ht_heat(:,2) = energy.cooling.ht_heat(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht2(:,2) ./ T_ht3(:,2)) ;
    exergy.cooling.ht_heat(isnan(exergy.cooling.ht_heat(:,1)),1) = 0 ;
    exergy.cooling.ht_heat(isnan(exergy.cooling.ht_heat(:,2)),2) = 0 ;
    exergy.cooling.ht_heat(:,3) = exergy.cooling.ht_heat(:,1) + exergy.cooling.ht_heat(:,2) ;
    exergy.cooling.ht_2_lt(:,1) = energy.cooling.ht_2_lt(:,1) - mfr_HT(:,1) .* T0 .* CP_W .* log(T_ht3(:,1) ./ T_ht1(:,1)) ;
    exergy.cooling.ht_2_lt(:,2) = energy.cooling.ht_2_lt(:,2) - mfr_HT(:,2) .* T0 .* CP_W .* log(T_ht3(:,2) ./ T_ht1(:,2)) ;
    exergy.cooling.ht_2_lt(isnan(exergy.cooling.ht_2_lt(:,1)),1) = 0 ;
    exergy.cooling.ht_2_lt(isnan(exergy.cooling.ht_2_lt(:,2)),2) = 0 ;
    exergy.cooling.ht_2_lt(:,3) = exergy.cooling.ht(:,3) - exergy.cooling.ht_heat(:,3) ;

%% LT cooling
mfr_LT(:,1) = AE_mfr_lt(:,1) + AE_mfr_lt(:,3) + ME_mfr_lt(:,1) + ME_mfr_lt(:,3) ;
mfr_LT(:,2) = AE_mfr_lt(:,2) + AE_mfr_lt(:,4) + ME_mfr_lt(:,2) + ME_mfr_lt(:,4) ;
    energy.cooling.lt(:,1) = energy.AE.lt(:,1) + energy.AE.lt(:,3) + energy.ME.lt(:,1) + energy.ME.lt(:,3) ;
    energy.cooling.lt(:,2) = energy.AE.lt(:,2) + energy.AE.lt(:,4) + energy.ME.lt(:,2) + energy.ME.lt(:,4) ;
    energy.cooling.lt(:,3) = energy.cooling.lt(:,1) + energy.cooling.lt(:,2) ;
    energy.cooling.lt_2_sw(:,1) = energy.cooling.lt(:,1) + energy.cooling.ht_2_lt(:,1) ;
    energy.cooling.lt_2_sw(:,2) = energy.cooling.lt(:,2) + energy.cooling.ht_2_lt(:,2) ;
    energy.cooling.lt_2_sw(:,3) = energy.cooling.lt(:,3) + energy.cooling.ht_2_lt(:,3) ;
T_lt1(:,1) = T_LTcooling(:,1) ;
T_lt1(:,2) = T_LTcooling(:,2) ;
T_lt2(:,1) = T_lt1(:,1) + energy.cooling.lt(:,1) ./ CP_W ./ mfr_LT(:,1) ;
T_lt2(:,2) = T_lt1(:,2) + energy.cooling.lt(:,2) ./ CP_W ./ mfr_LT(:,2) ;
T_lt3(:,1) = T_lt2(:,1) + energy.cooling.ht(:,1) ./ CP_W ./ mfr_LT(:,1) ;
T_lt3(:,2) = T_lt2(:,2) + energy.cooling.ht(:,2) ./ CP_W ./ mfr_LT(:,2) ;
    exergy.cooling.lt(:,1) = energy.cooling.lt(:,1) - mfr_LT(:,1) .* T0 .* CP_W .* log(T_lt2(:,1) ./ T_ht1(:,1)) ;
    exergy.cooling.lt(:,2) = energy.cooling.lt(:,2) - mfr_LT(:,2) .* T0 .* CP_W .* log(T_lt2(:,2) ./ T_ht1(:,2)) ;
    exergy.cooling.lt(isnan(exergy.cooling.lt(:,1)),1) = 0 ;
    exergy.cooling.lt(isnan(exergy.cooling.lt(:,2)),2) = 0 ;
    exergy.cooling.lt(:,3) = exergy.cooling.lt(:,1) + exergy.cooling.ht(:,2) ;
    exergy.cooling.lt_2_sw(:,1) = (energy.cooling.lt(:,1) + energy.cooling.ht(:,1)) - mfr_LT(:,1) .* T0 .* CP_W .* log(T_lt3(:,1) ./ T_lt1(:,1)) ;
    exergy.cooling.lt_2_sw(:,2) = (energy.cooling.lt(:,2) + energy.cooling.ht(:,2)) - mfr_LT(:,2) .* T0 .* CP_W .* log(T_lt3(:,2) ./ T_lt1(:,2)) ;
    exergy.cooling.lt_2_sw(isnan(exergy.cooling.lt_2_sw(:,1)),1) = 0 ;
    exergy.cooling.lt_2_sw(isnan(exergy.cooling.lt_2_sw(:,2)),2) = 0 ;
    exergy.cooling.lt_2_sw(:,3) = exergy.cooling.lt_2_sw(:,1) + exergy.cooling.lt_2_sw(:,2) ;

    %% Detailed exergy analysis
    exergy.cooling.ltgen1 = sum(exergy.ME.lt1,2) + sum(exergy.AE.lt1,2) ; 
    exergy.cooling.ltgen2 = sum(exergy.ME.lt3,2) + sum(exergy.AE.lt3,2) ;
    exergy.cooling.ltgen3 = exergy.cooling.ltgen2 + exergy.cooling.ht_2_lt(:,3) ;
    exergy.cooling.htgen1 = sum(exergy.ME.ht1,2) + sum(exergy.AE.ht1,2) ;
    exergy.cooling.htgen2 = sum(exergy.ME.ht3,2) + sum(exergy.AE.ht3,2) ;
    exergy.cooling.htgen3 = exergy.cooling.htgen2 - exergy.cooling.ht_heat(:,3) ;
    
    
    
    
%% SW cooling
    energy.cooling.sw(:,1) = energy.cooling.lt_2_sw(:,1) ;
    energy.cooling.sw(:,2) = energy.cooling.lt_2_sw(:,2) ;
    energy.cooling.sw(:,3) = energy.cooling.lt_2_sw(:,3) ;
mfr_SW(:,1) = energy.cooling.sw(:,1) ./ CP_W ./ (T_SWcooling(:,1) - T0) ;
mfr_SW(:,2) = energy.cooling.sw(:,2) ./ CP_W ./ (T_SWcooling(:,2) - T0) ;
mfr_SW(:,3) = mfr_SW(:,1)  + mfr_SW(:,2) ;
    exergy.cooling.sw(:,1) = energy.cooling.sw(:,1) - mfr_SW(:,1) .* T0 .* CP_W .* log(T_SWcooling(:,1) ./ T0) ;
    exergy.cooling.sw(:,2) = energy.cooling.sw(:,2) - mfr_SW(:,2) .* T0 .* CP_W .* log(T_SWcooling(:,2) ./ T0) ;
    exergy.cooling.sw(isnan(exergy.cooling.sw(:,1)),1) = 0 ;
    exergy.cooling.sw(isnan(exergy.cooling.sw(:,2)),2) = 0 ;
    exergy.cooling.sw(:,3) = exergy.cooling.sw(:,1) + exergy.cooling.sw(:,2) ;

    
%% Concluding the heat demand part
exergy.demand.heat_ht = exergy.cooling.ht_heat(:,3) ;
exergy.demand.total_heat = exergy.demand.hrsg + exergy.demand.boiler_heat + exergy.demand.heat_ht ;