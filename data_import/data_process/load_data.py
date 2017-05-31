import pandas as pd
import numpy as np

data_path = '/Users/fredde/Database/'

df_load = pd.read_hdf(data_path + 'all_data_1year_comp.h5','table')
a = list(df_load)

#%%

df_load.head()
import ftfy
a = list(df_load)
for i in range(len(a)):
    a[i]=ftfy.fix_text(a[i])

print(a)

#%%

df_load[list(df_load)[1]].plot()

#%%

headers = open(data_path + 'headers.csv','w')
for item in a:
    headers.write('\n'+item)
