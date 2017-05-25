import pandas as pd
import glob as glob
import csv

database_path = '/Users/fredde/Database/'
csv_data_path = '/Users/fredde/Database/csv-1year/'
project_path = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/'


# Load the data from the Excel-file with headers. Please not the project_path

headers = pd.read_excel(project_path + 'General/headers_dict.xlsx')

#%%

# Choose only the one which are marked with x in FB-column

df_headers_chosen = headers.loc[headers['FB'] == 'x']

# Make a standard list of the headers, which can be used later on for selection.

headers_name = df_headers_chosen['ORIGINAL_HEADER'].tolist()

#%%

all_data = pd.DataFrame()
# The csv-files which are already pre-processed.

csvfiles = glob.glob(csv_data_path + '*.csv')


# First load one csv-file at a time. Cleaning the temporary DataFrame each loop.

for i in range(len(csvfiles)):
    df = pd.DataFrame() # Reset DF every loop.
    print('Processing: '+str(csvfiles[i].split('/')[-1].split('.')[0]))
    df = pd.read_csv(csvfiles[i],header=0,index_col=0,dtype='a') # a = float64
    df.index = pd.to_datetime(df.index) # Make DateTime-index
    # This part is about selection. As it is now it overwrites an existing header with the same name.
    # I really need to check that up...
    for n in headers_name:
        if n in list(df):
            if n in list(all_data):
                # If the header is already existing it needs to be merged rather than overwrite the existing.
                all_data = pd.concat([all_data, df[n]])
            else:
                all_data[n] = df[n]

    del df # Clean up memory
    print(str(i+1) + ' done of ' + str(len(csvfiles)))

df = all_data.sort_index() # Sort index.
del all_data # Clean memory

df_out = pd.DataFrame() # Make a new DataFrame so the process of converting to numeric goes faster

for i in range(len(list(df))):
    df_out[list(df)[i]] = pd.to_numeric(df[list(df)[i]],errors='ignore')

df_out.to_hdf(database_path + 'selected_data_1year_comp.h5','table',complevel=9,complib='blosc')

print('All done!')




#%%

# Lets make a test loading the database
test_load = pd.read_hdf(database_path + 'selected_data_1year_comp.h5','table')

# Testing to choose a date and also multiplying.

test_load['2013-12-01']*3

#t.dropna()
#t.drop_duplicates().dropna()
