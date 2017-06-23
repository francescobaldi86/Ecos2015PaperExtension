import os

def filenames(project_path):
    #project_path = os.path.realpath('..')
    #project_path = os.path.dirname(os.path.realpath(__file__))
    #project_path = project_path + os.sep + ".."
    output = {}
    # Input files
    output["dataset_raw"] = project_path + os.sep + 'Database' + os.sep +'selected_df.h5'
    output["headers_translate"] = project_path + os.sep + 'General' + os.sep +'headers_dict.xlsx'
    output["consistency_check_input"] = project_path + os.sep + 'Data_Process'+ os.sep +'check_input.csv'
    # Output files
    output["dataset_output_empty"] = project_path + os.sep +'Data_Process' + os.sep + 'database_out_empty.h5'
    output["dataset_output"] = project_path + os.sep +'Data_Process' + os.sep + 'database_out.h5'
    output["consistency_check_report"] = project_path + os.sep + 'Data_Process' + os.sep + 'check_report.txt'
    # opening the
    text_file = open(output["consistency_check_report"],"w") # Cleaning the file
    text_file.write("=== STARTING THE REPORT FILE === \n \n")
    text_file.close()

    return output
