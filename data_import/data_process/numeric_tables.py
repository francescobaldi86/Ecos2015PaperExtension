import pandas as pd
import numpy as np

data_path = '/Users/fredde/Database/'

df_load = pd.read_hdf(data_path + 'birka_all_data.h5','table')
df2 = pd.DataFrame()
#%%
# First make sure that all the data in the DataBase is in Numeric form.

for i in range(len(list(df_load))):
    df2[list(df_load)[i]] = pd.to_numeric(df_load[list(df_load)[i]])

df2=df2.sort_index()        # sort the index once again. Shoudnt be needed...
df2.to_hdf(data_path + 'birka_all_data_numeric.h5','table')   # save to a new HDF5-file

#%%
