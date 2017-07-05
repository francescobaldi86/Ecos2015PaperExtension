import pandas as pd
import glob as glob
import csv

original_database_path = '/Users/fredde/Database/'
database_path = 'Database/'

df = pd.read_hdf(original_database_path + 'all_data_1year_comp.h5','table')


# Load the data from the Excel-file with headers.

headers = pd.read_excel('General/headers_dict.xlsx')

# Choose only the one which are marked with x in FB-column
df_headers_chosen = headers.loc[headers['FB'] == 'x']

# Make a standard list of the headers, which can be used later on for selection.
headers_name = df_headers_chosen['ORIGINAL_HEADER'].tolist()


#%%
# Do a resample of the data to 15-min interval. This will give a -49s offset from the original dataset.

selected_df = pd.DataFrame()
for i in headers_name:
    selected_df[i] = pd.to_numeric(df[i],errors='ignore')

selected_df.index=pd.to_datetime(selected_df.index)
df2 = selected_df.resample('15min').mean()
df_out= df2['2013-12-03':'2014-12-02'] # Choose just one year! This gives 366 days.

df_out.to_hdf(database_path + 'selected_df.h5','table',complevel=9,complib='blosc')

#%%
# # #
# This section is not needed anymore as it is covered by the .resample method above...

# NOT IN USE !

# # #
#
#
# df_out = pd.DataFrame()
# for i in list(selected_df):
#     s1 = selected_df[i]
#     s1 = s1.dropna()
#     s2 = s1[~s1.index.duplicated(keep='first')]
#     s2.index = pd.to_datetime(s2.index)
#     df_out[i] = s2
#
# df_out.to_hdf(database_path + 'selected_df.h5','table',complevel=9,complib='blosc')

#%%
# For testing .
# ...



#load_df = pd.read_hdf(database_path + 'resampled_selected_df.h5','table')
load_df = pd.read_hdf(database_path + 'selected_df.h5','table')

load_df['Boiler_starbord']['2014-02-01'].mean()

load_df.describe()




load_df['Crew']['2014-02']

#newdf = load_df['2013-12-02':'2014-12-02']

newdf.describe()

load_df['SW TEMP TO ME/AE 2/4:6411:C:Average:900']
df['Boiler_starbord']['2014-03-07']
