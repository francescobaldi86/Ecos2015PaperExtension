import pandas as pd
import glob as glob
import csv

database = '/Users/fredde/Database/all_data_1year_comp.h5'
headers_out = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/data_import/headers_out.csv'
headers_dict = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/data_import/headers_dict.csv'

# Load headers name, save these to a .csv file for manual processing.

df = pd.read_hdf(database, 'table')

#%%

headers = list(df)
df.index.names = ['Time']
# As there are non uni-code characters in the original headers file it needs be fixed..

# The following function was found here:
# http://stackoverflow.com/questions/20078816/replace-non-ascii-characters-with-a-single-space
# And replaces all non unicode chars with a space

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

headers_new = list()
headers[0]

# The rename function is really slow. About 16s just for one header, which means 4 hours for the set!!!
#%timeit df2=df.rename(columns={headers[1]:headers[1]})
#df=df.rename(columns={headers[1]:headers[1]})

print(list(df))

df2=pd.DataFrame() # It is MUCH MUCH faster creating a new DataFrame than using the built in function....
for n in range(len(headers)):
    series = df[headers[n]]
    df2[remove_non_ascii(headers[n])] = series

#%%
# Save the database once again!

df2.to_hdf(database,'table',complevel=9,complib='blosc')

#%%
