%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% SHIP ENERGY ANALYSIS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% MAIN FILE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%
%%% 1  Main_reading
%%%%%%%%%%%%%%%%%%%
clear
clc
path(path,'D:/BoxSync/baldif/MATLAB/Utility functions')
% Imports input files, if they exist already. If they do not, launch the
% file reading script

fprintf(1,'\n %%%%%%%% Starting "Ship energy analysis" %%%%%%%% \n')
t0 = tic ;

folder_work = 'D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\BEA2 - Birka Energy Analysis Step 2\' ;
folder_main = 'D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\' ;
filename_input = 'Ordered_data_feb.xlsx' ;
folder_output = 'D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\BEA2 - Birka Energy Analysis Step 2\Output\' ;
filename_output = 'Post_processing_2.xlsx' ;
filename_log_file = 'log.txt' ;

%% - Reading raw values (if needed)
callsScript('BirkaEA2_reading','check&time','raw_reading.mat',folder_work) ;


%% - Constants and Operational mode
% Imports all main constants used in the simulation 
callsScript('BirkaEA_constants','time')
% Define operational mode for each instant
callsScript('BirkaEA2_operational_mode','time')
% Pre-processing the data. Identifying corrupted measurements
callsScript('BirkaEA2_dataPreProcessing','time')

%% - Energy analysis
% Elaborates data for the energy analysis
callsScript('BirkaEA2_energy_analysis','check&time','energy_analysis.mat',folder_work)

%% - Exergy analysis
% Elaborates data for the exergy analysis
callsScript('BirkaEA2_exergy_analysis','check&time','exergy_analysis.mat',folder_work)

%% - Auxiliary energy
% Heat, Top Down
callsScript('BirkaEA2_heatDemand_topDown','time')
% % Heat, Bottom Up
callsScript('BirkaEA2_heatDemand_bottomUp','time')
% % Electric
callsScript('BirkaEA2_elDemand','time')

%% - Cooling systems
callsScript('BirkaEA2_cooling_systems','time')

%%
callsScript('BirkaEA2_statistical_analysis','time')

%% - Save results
% callsScript('BirkaEA_xlsave_type','time')
callsScript('BirkaEA2_xlsave_OM','time')


fprintf(1,'\n\n')


