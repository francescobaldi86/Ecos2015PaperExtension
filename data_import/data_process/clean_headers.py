import pandas as pd
import numpy as np

data_path = '/Users/fredde/Database/'

df_load = pd.read_hdf(data_path + 'birka_all_data_numeric.h5','table')

# Lets take care of the header names. Some of them are pretty messed up, and also
# a bit inconsistent. Remove the irrelevant information and make it consistent.
# 'MAIN.MAS_MAIN.pr:1749_AE1 EMERGENCY LO SHD_-_Raw data_900'
# 'MAIN.MAS_MAIN.pr:1342:av_ME1 CA PRESS COOL OU_bar_Raw data_900'


#
new_names = list(df_load)

# I am doint the conversion in several steps as it is more readable.
# First step is to filter out the MAIN.MAS_MAIN is it is in all headers. Not
# any use.

for i in range(len(new_names)):
    new_names[i] = '_'.join(list(df_load)[i].split('.')[2].split(':')[1:])

# We now have a list with names like this: '4343_av_ME4 CA TEMP COOL OUT_C_Raw data_900'
# or '1749_AE1 EMERGENCY LO SHD_-_Raw data_900'
# There is a little difference in how the data point is presented, some of them have a sub-category
# like 'av' which should be a part of the ID:nr.

for i in range(len(new_names)):
    new_names[i] = '_'.join(new_names[i].split('.')[2].split(':')[1:])


print(new_names)
