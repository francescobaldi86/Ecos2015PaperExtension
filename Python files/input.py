import os

def filenames():
    project_path = os.path.realpath('.')
    output = {}
    # Input files
    output["dataset_raw"] = project_path + os.sep + 'Database' + os.sep +'selected_df.h5'
    output["headers_translate"] = project_path + os.sep + 'General' + os.sep +'headers_dict.xlsx'
    output["consistency_check_input"] = project_path + os.sep + 'Data_Process'+ os.sep +'check_input.csv'
    # Output files
    output["dataset_output"] = project_path + os.sep +'Data_Process' + os.sep + 'database_out.csv'
    output["consistency_check_report"] = project_path + os.sep + 'Data_Process' + os.sep + 'check_report.txt'
    return output
