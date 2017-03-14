%%% Script name: BirkaEA_xlsave_energy_analysis
%
% This script saves the results of the energy analysis in an excel file
% that can then be used for plotting and further analysis

operational_mode_names = {'HSS' , 'LSS' , 'MAN' , 'POR'} ;
analysis_types = {'energy' , 'exergy'} ;
analysis_statistical = {'ave' , '25prctile' , '75prctile'} ;
structure_fields = fields(exergy) ; % Note that the only different field is the field "losses" in the energy analysis, that only contains 2-3 elements and can be ignored as it can be easily recalculated

for id_case = 1 : length(operational_mode_names)
    output_file_fullname2 = char([char(folder_output) 'Post_processing_STAT_' char(operational_mode_names(id_case)), '.xlsx']) ; %Writing a different ouput file for each of the four cases
    for id_analysis = 1 : length(analysis_types)
        sheet_name = char([char(operational_mode_names(id_case)) ' ' char(analysis_types(id_analysis))]) ;
        start_row = 2 ; number_fields = 0 ;
        for id_field = 1 : length(structure_fields)
            start_row = start_row + number_fields ;
            eval(char(['temp1 = ',char(analysis_types(id_analysis)),'_ave_',char(operational_mode_names(id_case)),'.',char(structure_fields(id_field)) ' ;'])) ;
            eval(char(['temp2 = ',char(analysis_types(id_analysis)),'_25prctile_',char(operational_mode_names(id_case)),'.',char(structure_fields(id_field)) ' ;'])) ;
            eval(char(['temp3 = ',char(analysis_types(id_analysis)),'_75prctile_',char(operational_mode_names(id_case)),'.',char(structure_fields(id_field)) ' ;'])) ;
            struct2xls(output_file_fullname2,temp1,'Sheet',sheet_name,'Row',start_row,'Col','B')
            struct2xls(output_file_fullname2,temp2,'Sheet',sheet_name,'Row',start_row,'Col','I')
            struct2xls(output_file_fullname2,temp3,'Sheet',sheet_name,'Row',start_row,'Col','P')
            eval(char(['number_fields = length(fields(' char(analysis_types(id_analysis)) '_ave_HSS.' char(structure_fields(id_field)) ')) + 1 ;'])) ;
        end
    end
end


    
    
    
    
    
    
    
%% High Speed Sailing (HSS) Case
output_file_fullname2 = char([char(folder_output) 'Post_processing_2STAT.xlsx']) ;
% Energy

struct2xls(output_file_fullname2,energy_ave_HSS.ME,'Sheet','EN-HSS','Row',2,'Col','B')
% struct2xls(output_file_fullname,exergy_sum_OM,'Sheet','OperationalMode','Row',2,'Col','G')






