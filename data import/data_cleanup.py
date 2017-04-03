import pandas as pd
import numpy as np
import timeit
# Import all data into a DataFrame
#

data_path = '/Users/fredde/Dropbox/arbetsprojekt/Birka_data/'

%timeit df = pd.read_excel(data_path + 'ME.xlsx',index_col=0)

df.to_hdf('ME.h5','table',append=True)


# Exploring the dataset
print(df.head())
print(df.tail())
# The dataset is betwen 13-12-01 to 14-12-17, which is slightly more than one year.
print(list(df))
print(str(len(list(df))) + ' number of columns')
# It contains 183 datapoints, with a 15-minute interval of logging.

#%%
1+1
