%%% Script name: BirkaEA_xlsave_energy_analysis
%
% This script saves the results of the energy analysis in an excel file
% that can then be used for plotting and further analysis

% Writing the full name of the output file
output_file_fullname = char([char(folder_output) char(filename_output)]) ;
% Doing the sum-up for the main engines
fieldnames_energy = fieldnames(energy.ME) ;
for i = 1 : length(fieldnames_energy) 
    energy_sum.ME.(char(fieldnames_energy(i))) = sum(energy.ME.(char(fieldnames_energy(i))),1) * 15* 60 * 1e-9;
    energy_sum.AE.(char(fieldnames_energy(i))) = sum(energy.AE.(char(fieldnames_energy(i))),1) * 15* 60 * 1e-9;
end
% Doing the sum-up for the auxiliary engines
fieldnames_exergy = fieldnames(exergy.ME) ;
for i = 1 : length(fieldnames_exergy) 
    exergy_sum.ME.(char(fieldnames_exergy(i))) = sum(exergy.ME.(char(fieldnames_exergy(i))),1) * 15* 60 * 1e-9;
    exergy_sum.AE.(char(fieldnames_exergy(i))) = sum(exergy.AE.(char(fieldnames_exergy(i))),1) * 15* 60 * 1e-9;
end
% Doing the sum-up for the rest
fieldnames_demand = fieldnames(energy.demand) ;
for i = 1 : length(fieldnames_demand) 
    energy_sum.demand.(char(fieldnames_demand(i))) = sum(energy.demand.(char(fieldnames_demand(i))),1) * 15* 60 * 1e-9;
    exergy_sum.demand.(char(fieldnames_demand(i))) = sum(exergy.demand.(char(fieldnames_demand(i))),1) * 15* 60 * 1e-9;
end
fieldnames_cooling = fieldnames(energy.cooling) ;
for i = 1 : length(fieldnames_cooling) 
    energy_sum.cooling.(char(fieldnames_cooling(i))) = sum(energy.cooling.(char(fieldnames_cooling(i))),1) * 15* 60 * 1e-9;
end
fieldnames_cooling = fieldnames(exergy.cooling) ;
for i = 1 : length(fieldnames_cooling) 
    exergy_sum.cooling.(char(fieldnames_cooling(i))) = sum(exergy.cooling.(char(fieldnames_cooling(i))),1) * 15* 60 * 1e-9;
end
% Little correction
exergy_sum.cooling.ltgen1 = [0 0 exergy_sum.cooling.ltgen1] ;
exergy_sum.cooling.ltgen2 = [0 0 exergy_sum.cooling.ltgen2] ;
exergy_sum.cooling.ltgen3 = [0 0 exergy_sum.cooling.ltgen3] ;
exergy_sum.cooling.htgen1 = [0 0 exergy_sum.cooling.htgen1] ;
exergy_sum.cooling.htgen2 = [0 0 exergy_sum.cooling.htgen2] ;
exergy_sum.cooling.htgen3 = [0 0 exergy_sum.cooling.htgen3] ;


energy_sum.demand.fuel_tanks = sum(energy_sum.demand.fuel_tanks) ;
exergy_sum.demand.fuel_tanks = sum(exergy_sum.demand.fuel_tanks) ;

% Writing the files
struct2xls(output_file_fullname,energy_sum.ME,'Sheet','MainEngines','Row',2,'Col','B')
struct2xls(output_file_fullname,exergy_sum.ME,'Sheet','MainEngines','Row',2,'Col','H')
struct2xls(output_file_fullname,energy_sum.AE,'Sheet','AuxiliaryEngines','Row',2,'Col','B')
struct2xls(output_file_fullname,exergy_sum.AE,'Sheet','AuxiliaryEngines','Row',2,'Col','H')
struct2xls(output_file_fullname,energy_sum.demand,'Sheet','Demand','Row',2,'Col','B')
struct2xls(output_file_fullname,exergy_sum.demand,'Sheet','Demand','Row',2,'Col','E')
struct2xls(output_file_fullname,energy_sum.cooling,'Sheet','Cooling','Row',2,'Col','B')
struct2xls(output_file_fullname,exergy_sum.cooling,'Sheet','Cooling','Row',2,'Col','H')
