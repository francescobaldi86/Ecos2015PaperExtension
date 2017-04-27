
# coding: utf-8

# In[6]:

import numpy as np
import pandas as pd
import glob as glob


# **Introduction**
#
# The dataset from MS Birka Stockholm is in .xls Excel-97 format. And the data was gathered in several steps during three different trips. Some of the data is overlapping in time-index, and same headers (data points) exist in several files. So to be able to filter and consolidate all the data it must be done in several steps. As the Excel-97 format is limited in 65k rows and also a limited amount of columns it was needed to divide into several files.
#
# Some of the data is in Boolean format, and some have data-points missing but the majority should be in numerical format.
#
# In all Excel-files the meta data of each data-point (header) is in the first 14 rows. The first step is to make a pre-processing of the .xls files, and filter out non uni-code characters, put in a split character between the meta-data and joining everything in the data header. Still keeping the index in time-series format.
#

# In[7]:

csv_data_path = '/Users/fredde/Database/csv/all/'
xls_data_path = '/Users/fredde/Database/data-files/all/'
database_path = '/Users/fredde/Database/'

xlsfiles = glob.glob(xls_data_path + '*.xls')
print(xlsfiles)
df = pd.DataFrame()
all_data = pd.DataFrame()


# As there are non uni-code characters in the original headers file it needs be fixed..
# The following function was found here:
# http://stackoverflow.com/questions/20078816/replace-non-ascii-characters-with-a-single-space
# And replaces all non unicode chars with a space

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])


# Clean up csv

# In[3]:

# Make CSV-files and clean up headers.

for i in range(len(xlsfiles)):
    df = pd.DataFrame()
    df2 = pd.DataFrame()

    print('Processing: '+str(xlsfiles[i].split('/')[-1].split('.')[0]))
    df = pd.read_excel(xlsfiles[i],index_col=0)

    headers = list(df)
    headers_new = list()

    # And now extract the relevant meta-data in the first couple of rows.
    # Make a new list of headers in the file. Using ':' as a split.

    for head in headers:

        name = str(df[head].iloc[0])
        id_nr = str(head.split('.')[2].split(':')[1])
        unit = str(df[head].iloc[1])
        data_type = str(df[head].iloc[5])
        sample_interval = str(df[head].iloc[8])

        headers_new.append(remove_non_ascii(str(name+':'+id_nr+':'+unit+':'+data_type+':'+sample_interval)))

    for n in range(len(headers_new)):
        series = df[headers[n]].ix[13:]
        df2[headers_new[n]] = series

    # Save in .csv format.
    #df2.to_csv(csv_data_path + xlsfiles[i].split('/')[-1].split('.')[0] + '.csv')
    df2.to_hdf(csv_data_path + xlsfiles[i].split('/')[-1].split('.')[0] + '.h5','table')
    #df2.to_excel(csv_data_path + xlsfiles[i].split('/')[-1].split('.')[0] + '.xls')

    # Clean up memory
    del df2
    del df
    print(str(i+1) + ' done of ' + str(len(xlsfiles)))

print('All done!')


# Time to create a database, joining all the files into one master DataFrame.

# In[3]:

all_data=pd.DataFrame()
csvfiles = glob.glob(csv_data_path + '*.csv')
h5files = glob.glob(csv_data_path + '*.h5')

for i in range(len(csvfiles)):
    df = pd.DataFrame()
    print('Reading... '+str(csvfiles[i].split('/')[-1].split('.')[0]))
    #df = pd.read_csv(csvfiles[i],header=0,index_col=0,dtype='a')
    df = pd.read_hdf(h5files[i],'table')
    print('Making numeric float int32...')
    for n in range(len(list(df))):
        df[list(df)[n]] = pd.to_numeric(df[list(df)[n]],downcast='float',errors='ignore')
    print('Appending...')
    all_data = all_data.append(df)
    print('Sorting index...')
    all_data = all_data.sort_index()
    print('Dropping duplicates...')
    all_data = all_data.drop_duplicates()
    del df # Clean up memory
    print(str(i+1) + ' done of ' + str(len(csvfiles)))

df = all_data.sort_index()

del all_data # Clean memory
df_out = pd.DataFrame() # Make a new DataFrame so the process of converting to numeric goes faster

for i in range(len(list(df))):
    df_out[list(df)[i]] = pd.to_numeric(df[list(df)[i]],errors='ignore')

df_out.to_hdf(database_path + 'all_data_1year.h5','table')

print('All done!')


# Load the data and see if it can be used..

# In[12]:

df = pd.read_hdf(database_path + 'all_data_1year.h5','table')



# In[13]:

df.to_hdf(database_path + 'all_data_1year_comp.h5','table',complevel=9,complib='blosc')


# In[14]:

df2 = pd.read_hdf(database_path + 'all_data_1year_comp.h5','table')


# In[16]:

df2.describe()


# In[20]:

get_ipython().magic("timeit df['AE SCR 2CFC20 ALARM:6854:-:Average:900']")


# In[19]:

get_ipython().magic("timeit df2['AE SCR 2CFC20 ALARM:6854:-:Average:900']")


# In[ ]:
