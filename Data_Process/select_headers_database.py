import pandas as pd
import glob as glob
import csv

original_database_path = '/Users/fredde/Database/'
database_path = '../Database/'

df = pd.read_hdf(original_database_path + 'all_data_1year_comp.h5','table')


# Load the data from the Excel-file with headers.

headers = pd.read_excel('../General/headers_dict.xlsx')

#%%

# Choose only the one which are marked with x in FB-column
df_headers_chosen = headers.loc[headers['FB'] == 'x']

# Make a standard list of the headers, which can be used later on for selection.
headers_name = df_headers_chosen['ORIGINAL_HEADER'].tolist()


#%%

selected_df = pd.DataFrame()
for i in headers_name:
    selected_df[i] = pd.to_numeric(df[i],errors='ignore')

df_out = pd.DataFrame()
for i in list(selected_df):
    s1 = selected_df[i]
    s1 = s1.dropna()
    s2 = s1[~s1.index.duplicated(keep='first')]
    df_out[i] = s2


df_out.to_hdf(database_path + 'selected_df.h5','table',complevel=9,complib='blosc')

#%%

load_df = pd.read_hdf(database_path + 'selected_df.h5','table')
load_df
