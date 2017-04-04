import pandas as pd
import numpy as np

data_path = '/Users/fredde/Database/'

df_load = pd.read_hdf(data_path + 'birka_all_data.h5','table')

df_load.head()
list(df_load)


headers = open(data_path + 'headers.csv','w')
a = list(df_load)
for item in a:
    headers.write('\n' + item)
