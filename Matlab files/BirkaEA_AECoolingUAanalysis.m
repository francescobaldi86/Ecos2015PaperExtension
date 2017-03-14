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
mfr_fuel = polyval(PARAM.AE.POLY_LOAD_2_ISO_BSFC,load) * 1.05^2 .* load * PARAM.AE.MCR / 3.6e6 ; 
[Q_eg , Q_ht , mfr_air , T_air] = HET_auxiliaryEngineWasteHeat(PARAM,load,mfr_fuel,running) ;

