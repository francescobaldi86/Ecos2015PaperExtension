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

folder_work = 'D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\' ;
folder_main = 'D:\BoxSync\baldif\MATLAB\MS Birka Energy Analysis\' ;
filename_input = 'Ordered_data_feb.xlsx' ;
folder_output = 'C:\Users\baldif\Dropbox\ECOS - Exergy Cruise Ship\Working documents\' ;
filename_output = 'Post_processing_2.xlsx' ;

%% - Reading raw values (if needed)
callsScript('BirkaEA_reading','check&time','raw_reading.mat',folder_work) ;
% callsScript('BirkaEA_reading','time') ;

%% - Constants and Operational mode
% Imports all main constants used in the simulation 
callsScript('BirkaEA_constants','time')
% Define operational mode for each instant
callsScript('BirkaEA_operational_mode','time')


%% - Energy analysis
% Elaborates data for the energy analysis
callsScript('BirkaEA_energy_analysis','check&time','energy_analysis.mat',folder_work)

%% - Exergy analysis
% Elaborates data for the exergy analysis
callsScript('BirkaEA_exergy_analysis','check&time','exergy_analysis.mat',folder_work)

%% - Auxiliary energy (power & heat)
callsScript('BirkaEA_auxiliary_demand','time')

%% - Cooling systems
callsScript('BirkaEA_cooling_systems','time')

% %% Other data elaboration
% callsScript('BirkaEA_other_elaboration','time')

%% - Save and plot
% First, let's plot some of the results so that we see how they look like
% callsScript('BirkaEA_plot_energy_analysis','time')
% Then, let's save the processed result in an excel file

% callsScript('BirkaEA_xlsave_type','time')
% callsScript('BirkaEA_xlsave_OM','time')


