%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% HET_mainEngineWasteHeat_test
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% This script is made for testing the "HET_mainEngineWasteHeat" functions
% quicker.
clear ; clc ;

addpath(genpath('D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis'))
addpath(genpath('D:\BoxSync\baldif\MATLAB\Utility functions'))

load('D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\energy_analysis.mat') ;
        HET_constants % Loading constants
        HET_CalculatesRegressionsEngines % Generates the required regressions
clearvars -except PARAM
load_eng = [0.2:0.02:1]' ;
% Calculating the BSFC of the engines
bsfc_me_iso = polyval(PARAM.ME.POLY_LOAD_2_ISO_BSFC,load_eng) ;
bsfc_ae_iso = polyval(PARAM.ME.POLY_LOAD_2_ISO_BSFC,load_eng) ;
bsfc_me = bsfc_me_iso * 1.05 ;
bsfc_ae = bsfc_ae_iso * 1.05 ;
mfr_fuel_me = bsfc_me .* load_eng .* PARAM.ME.MCR / 3.6e6 ;
mfr_fuel_ae = bsfc_ae .* load_eng .* PARAM.AE.MCR / 3.6e6 ;

% Running the calculations for various energy flows
[qdot_eg_me , qdot_ht_me , m_me , T_me] = HET_mainEngineWasteHeat(PARAM,load_eng,mfr_fuel_me,1) ;
[qdot_eg_ae , qdot_ht_ae , m_ae , T_ae] = HET_auxiliaryEngineWasteHeat(PARAM,load_eng,mfr_fuel_ae,1) ;

%% Writing an output XLS file
output_me = [bsfc_me , qdot_eg_me , qdot_ht_me , T_me(:,5:7)] ;
output_ae = [bsfc_ae , qdot_eg_ae , qdot_ht_ae , T_ae(:,3:4)] ;
xlswrite('D:\BoxSync\baldif\Writing\Work in progress\Paper - 06 - Optimisation of the energy generation system of a cruise ship\Figures\source_file.xlsx',output_me,'MainEngines','B2') ;
xlswrite('D:\BoxSync\baldif\Writing\Work in progress\Paper - 06 - Optimisation of the energy generation system of a cruise ship\Figures\source_file.xlsx',output_ae,'AuxEngines','B2') ;


