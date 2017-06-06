import os

def filenames():
    project_path = os.path.realpath('..')
    output = {}
    # Input files
    output["dataset_raw"] = project_path + '\\Database\\selected_df.h5'
    output["headers_translate"] = project_path + '\\General\\headers_dict.xlsx'
    output["consistency_check_input"] = project_path + '\\Data_Process\\check_input.csv'
    # Output files
    output["dataset_output"] = project_path + '\\Data_Process\\database_out.csv'
    output["consistency_check_report"] = project_path + '\\Data_Process\\check_report.txt'
    return output