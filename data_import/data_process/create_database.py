import pandas as pd
import numpy as np
import glob

data_path = '/Users/fredde/Database/csv/'
database_path = '/Users/fredde/Database/'

#Load all csv filenames
filenames = glob.glob(data_path + '*.csv')

df=pd.DataFrame()
df2=pd.DataFrame()

for filename in filenames:
    df = pd.read_csv(filename,header=0,index_col=0,dtype='a') # a is for int32
    print('Loading: '+str(filename))
    # Append DataFrame
    df2=df2.append(df)

# First sort the DataFrame after Index (time series).
# And save just to be sure not anything goes wrong...
#%%
df2=df2.sort_index()
print('Saving data raw-format....')
df2.to_hdf(database_path + 'birka_all_data_raw.h5','table')

#%%
#Loading the DataBase, creating a new DataFrame for faster processing
df=pd.read_hdf(database_path + 'birka_all_data_raw.h5','table')
df2 = pd.DataFrame()

# First make sure that all the data in the DataBase is in Numeric form.
# errors = ignore is because some of the data is in Boolean values.

print('Making the data numeric...')
for i in range(len(list(df))):
    df2[list(df)[i]] = pd.to_numeric(df[list(df)[i]],errors='ignore')

len(list(df))
df2[list(df2)[1]].head()
df2.to_csv('df2_data.csv')

df2=df2.sort_index()        # sort the index once again. Shoudnt be needed...
df2.to_hdf(database_path + 'birka_all_data_numeric.h5','table')   # save to a new HDF5-file

Write all the new headers to a csv-file

headers = open(database_path + 'headers.csv','w')
a = list(df)
for item in a:
    headers.write('\n' + item)
