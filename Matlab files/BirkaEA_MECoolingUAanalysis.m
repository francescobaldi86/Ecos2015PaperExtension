clear; clc

%% SCRIPT SUMMARY
% This script is meant for analysing the heat loss to the charge air cooler
% in the case of the Main engines of MS Birka. In this way, it is possible
% to estimate the NTU of the exchangers
%
% The analysis is based on the following hypothesis:
% - MOSTLY: That the UA value is the same for the two stages of the charge
% air cooler. 

%% Defining initial consants
load('D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\energy_analysis.mat') ;
HET_CalculatesRegressionsEngines ;
HET_constants ; 
clearvars -except PARAM
plot_yes = [1] ; % For saying which figures are going to be plotted
load = 0.1 : 0.01 : 1 ; load = load' ;
running = 1 ;
mfr_fuel = polyval(PARAM.ME.POLY_LOAD_2_ISO_BSFC,load) *1.05^2 .* load * PARAM.ME.MCR / 3.6e6 ; 
[Q_eg , Q_ht , mfr_air , T_air] = HET_mainEngineWasteHeat(PARAM,load,mfr_fuel,running) ;

%% Reading from the engine test protocol:
temp_HT_in = [
    78 83 84 83 78 ;
    80 86 82 75 86 ;
    81 82 78 87 86 ;
    78 85 84 77 82
] ;
temp_HT_out = [
    78 84 87 86 82 ;
    79 87 85 81 90 ;
    81 83 83 91 91 ;
    78 86 87 81 87
] ;
temp_LT_in = [
    35 36 36 32 32 ;
    34 35 33 36 32 ;
    32 35 34 35 34 ;
    32 36 34 34 34
] ;
temp_LT_out = [
    35 36 37 33 34 ;
    34 36 34 38 33 ;
    32 36 34 36 35 ;
    32 36 35 35 36
] ;
temp_air_in = [
    55 139 178 196 212 ;
    0 0 0 0 0 ;
    60 136 179 200 216 ;
    66 142 176 197 212
] ;
temp_air_out = [
    38 39 40 40 41 ;
    0 0 0 0 0 ;
    37 40 40 42 42 ;
    37 40 40 42 42 ;
] ; 
load_MES = [0.25 0.5 0.75 0.85 1] ;
mfr_air_ref  = [mfr_air(16,4) mfr_air(41,4) mfr_air(66,4) mfr_air(76,4) mfr_air(91,4)] ; 
if plot_yes(1) == 1
    plot(load,T_air(:,2)-273,'k-',load_MES,temp_air_in,'rx')
end    

for idx_1 = [1 3 4] ;
    for idx_2 = 2 : length(load_MES) 
        funzione = @(x) [mfr_air_ref(idx_2) * 1040 * (temp_air_in(idx_1,idx_2) - x(1)) - ...
            x(2) * (temp_air_in(idx_1,idx_2) - temp_HT_out(idx_1,idx_2) - x(1) + temp_HT_in(idx_1,idx_2)) / log((temp_air_in(idx_1,idx_2) - temp_HT_out(idx_1,idx_2)) / (x(1) - temp_HT_in(idx_1,idx_2))) ;
                mfr_air_ref(idx_2) * 1040 * (x(1) - temp_air_out(idx_1,idx_2)) - ...
            x(2) * (x(1) - temp_LT_out(idx_1,idx_2) - temp_air_out(idx_1,idx_2) + temp_LT_in(idx_1,idx_2)) / log((x(1) - temp_LT_out(idx_1,idx_2)) / (temp_air_out(idx_1,idx_2) - temp_LT_in(idx_1,idx_2))) 
            ] ;
        out = fsolve(funzione,[temp_HT_in(idx_1,idx_2)+5 , 600]) ;
        temp_air_mid(idx_1,idx_2) = out(1) ;
        UAcalc_HTstage(idx_1,idx_2) = out(2) ;
        UAcalc_LTstage(idx_1,idx_2) = (mfr_air_ref(idx_2) * PARAM.THERMO.CP_AIR * (temp_air_mid(idx_1,idx_2) - temp_air_out(idx_1,idx_2))) / ...
            ((temp_air_mid(idx_1,idx_2) - temp_LT_out(idx_1,idx_2) - temp_air_out(idx_1,idx_2) + temp_LT_in(idx_1,idx_2)) / log((temp_air_mid(idx_1,idx_2) - temp_LT_out(idx_1,idx_2)) / (temp_air_out(idx_1,idx_2) - temp_LT_in(idx_1,idx_2)))) ;
        mfr_HT(idx_1,idx_2) = (mfr_air_ref(idx_2) * PARAM.THERMO.CP_AIR * (temp_air_in(idx_1,idx_2) - temp_air_mid(idx_1,idx_2))) / ...
            (4.187 * (temp_HT_out(idx_1,idx_2) - temp_HT_in(idx_1,idx_2))) ;
        mfr_LT(idx_1,idx_2) = (mfr_air_ref(idx_2) * PARAM.THERMO.CP_AIR * (temp_air_mid(idx_1,idx_2) - temp_air_out(idx_1,idx_2))) / ...
            (4.187 * (temp_LT_out(idx_1,idx_2) - temp_LT_in(idx_1,idx_2))) ;
        eps_HT(idx_1,idx_2) = (temp_air_in(idx_1,idx_2) - temp_air_mid(idx_1,idx_2)) / (temp_air_in(idx_1,idx_2) - temp_HT_in(idx_1,idx_2)) ; 
        eps_LT(idx_1,idx_2) = (temp_air_mid(idx_1,idx_2) - temp_air_out(idx_1,idx_2)) / (temp_air_mid(idx_1,idx_2) - temp_LT_in(idx_1,idx_2)) ;
    end
end

        
    
    