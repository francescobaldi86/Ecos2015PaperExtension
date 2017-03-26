import pandas as pd
import numpy as np
# Import all data into a DataFrame
#
df = pd.read_excel('all_data.xlsx',index_col=0)


# Exploring the dataset
print(df.head())
print(df.tail())
# The dataset is betwen 13-12-01 to 14-12-17, which is slightly more than one year.
print(list(df))
print(str(len(list(df))) + ' number of columns')
# It contains 183 datapoints, with a 15-minute interval of logging.

#%%
