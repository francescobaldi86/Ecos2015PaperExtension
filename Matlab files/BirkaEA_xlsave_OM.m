%%% Script name: BirkaEA_xlsave_energy_analysis
%
% This script saves the results of the energy analysis in an excel file
% that can then be used for plotting and further analysis

% Writing the full name of the output file
output_file_fullname = char([char(folder_output) char(filename_output)]) ;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ENERGY %%%%%%%%%%%%
%% Main engines, energy
fieldnames_OM = fieldnames(energy.ME) ;
for i = 1 : length(fieldnames_OM)
    temp1 = sum(energy.ME.(char(fieldnames_OM(i))),2) ;   
    temp21 = temp1 .* (OM == 1) ; % Sailing
    temp22 = temp1 .* (OM == 2) ; % Maneuvring
    temp23 = temp1 .* (OM == 3) ; % Port Stay
    energy_sum_OM_temp1.([char(fieldnames_OM(i)) '_ME']) = [sum(temp21,1) sum(temp22,1) sum(temp23,1)] * 15 * 60 * 1e-9;
end
%% Auxiliary engines, energy
fieldnames_OM = fieldnames(energy.AE) ;
for i = 1 : length(fieldnames_OM)
    temp1 = sum(energy.AE.(char(fieldnames_OM(i))),2) ;   
    temp21 = temp1 .* (OM == 1) ; % Sailing
    temp22 = temp1 .* (OM == 2) ; % Maneuvring
    temp23 = temp1 .* (OM == 3) ; % Port Stay
    energy_sum_OM_temp2.([char(fieldnames_OM(i)) '_AE']) = [sum(temp21,1) sum(temp22,1) sum(temp23,1)] * 15 * 60 * 1e-9;
end
%% Demands
fieldnames_OM = fieldnames(energy.demand) ;
for i = 1 : length(fieldnames_OM)
    temp1 = sum(energy.demand.(char(fieldnames_OM(i))),2) ;   
    temp21 = temp1 .* (OM == 1) ; % Sailing
    temp22 = temp1 .* (OM == 2) ; % Maneuvring
    temp23 = temp1 .* (OM == 3) ; % Port Stay
    energy_sum_OM_temp3.(char(fieldnames_OM(i))) = [sum(temp21,1) sum(temp22,1) sum(temp23,1)] * 15 * 60 * 1e-9 ;  
end
names = [fieldnames(energy_sum_OM_temp1); fieldnames(energy_sum_OM_temp2); fieldnames(energy_sum_OM_temp3)];
energy_sum_OM = cell2struct([struct2cell(energy_sum_OM_temp1); struct2cell(energy_sum_OM_temp2); struct2cell(energy_sum_OM_temp3)], names, 1); 
%%




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% EXERGY %%%%%%%%%%%%
%% Main engines, exergy
fieldnames_OM = fieldnames(exergy.ME) ;
for i = 1 : length(fieldnames_OM)
    temp1 = sum(exergy.ME.(char(fieldnames_OM(i))),2) ;   
    temp21 = temp1 .* (OM == 1) ; % Sailing
    temp22 = temp1 .* (OM == 2) ; % Maneuvring
    temp23 = temp1 .* (OM == 3) ; % Port Stay
    exergy_sum_OM_temp1.([char(fieldnames_OM(i)) '_ME']) = [sum(temp21,1) sum(temp22,1) sum(temp23,1)] * 15 * 60 * 1e-9;
end
%% Auxiliary engines, exergy
fieldnames_OM = fieldnames(exergy.AE) ;
for i = 1 : length(fieldnames_OM)
    temp1 = sum(exergy.AE.(char(fieldnames_OM(i))),2) ;   
    temp21 = temp1 .* (OM == 1) ; % Sailing
    temp22 = temp1 .* (OM == 2) ; % Maneuvring
    temp23 = temp1 .* (OM == 3) ; % Port Stay
    exergy_sum_OM_temp2.([char(fieldnames_OM(i)) '_aE']) = [sum(temp21,1) sum(temp22,1) sum(temp23,1)] * 15 * 60 * 1e-9;
end
%% Demands, exergy
fieldnames_OM = fieldnames(exergy.demand) ;
for i = 1 : length(fieldnames_OM)
    temp1 = sum(exergy.demand.(char(fieldnames_OM(i))),2) ;   
    temp21 = temp1 .* (OM == 1) ; % Sailing
    temp22 = temp1 .* (OM == 2) ; % Maneuvring
    temp23 = temp1 .* (OM == 3) ; % Port Stay
    exergy_sum_OM_temp3.([char(fieldnames_OM(i))]) = [sum(temp21,1) sum(temp22,1) sum(temp23,1)] * 15 * 60 * 1e-9 ;  
end
names = [fieldnames(exergy_sum_OM_temp1); fieldnames(exergy_sum_OM_temp2); fieldnames(exergy_sum_OM_temp3)];
exergy_sum_OM = cell2struct([struct2cell(exergy_sum_OM_temp1); struct2cell(exergy_sum_OM_temp2); struct2cell(exergy_sum_OM_temp3)], names, 1); 
%%




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Writing

% Writing the files
struct2xls(output_file_fullname,energy_sum_OM,'Sheet','OperationalMode','Row',2,'Col','B')
struct2xls(output_file_fullname,exergy_sum_OM,'Sheet','OperationalMode','Row',2,'Col','G')






