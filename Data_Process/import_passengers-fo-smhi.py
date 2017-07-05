import pandas as pd
import glob as glob

# **Introduction**
# Fredrik Ahlgren
#
# The dataset from MS Birka Stockholm is in .xls Excel-97 format.
# And the data was gathered in several steps during three different trips.
# Some of the data is overlapping in time-index, and same headers (data points) exist in several files.
# So to be able to filter and consolidate all the data it must be done in several steps.
# As the Excel-97 format is limited in 65k rows and also a limited amount of columns it was needed to
# divide into several files.
#
# Some of the data is in Boolean format, and some have data-points missing but
# the majority should be in numerical format.
#
# In all Excel-files the meta data of each data-point (header) is in the first 14 rows.
# The first step is to make a pre-processing of the .xls files, and filter out non uni-code characters,
# put in a split character between the meta-data and joining everything in the data header.
# Still keeping the index in time-series format.
#

# In[7]:

csv_data_path = '/Users/fredde/Database/csv-1year/'
xls_data_path = '/Users/fredde/Database/data-files/'
database_path = '/Users/fredde/Database/'


df = pd.DataFrame()
all_data = pd.DataFrame()

# As there are non uni-code characters in the original headers file it needs be fixed..
# The following function was found here:
# http://stackoverflow.com/questions/20078816/replace-non-ascii-characters-with-a-single-space
# And replaces all non unicode chars with a space

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

# Clean up csv

#%%
# Doing some manual import of the passengers and crew-lists, so it can be included
# in the DB from a CSV.

df = pd.read_excel(xls_data_path+'2014_crew_pass.xlsx',index_col=0)
df.index = pd.to_datetime(df.index)
df2 = df.resample('15min').pad()
df2.to_csv(csv_data_path+'passengers_2014.csv')

headers = open(database_path + '1_headers.csv','w')
a = list(df)
for item in a:
    headers.write('\n' + item)
headers.close()



#%%

# Doing some manual import of the FO-flow meters and engine readings., so it can be included
# in the DB from a CSV.
# I am resampling it to 15-min before saving it in .csv

df = pd.read_excel(xls_data_path+'Mass_flowmeters.xlsx',index_col=0)
df.index = pd.to_datetime(df.index)
df2 = df.resample('15min').pad()
df2.to_csv(csv_data_path+'Mass_flowmeters.csv')


headers = open(database_path + '2_headers.csv','w')
a = list(df)
for item in a:
    headers.write('\n' + item)
headers.close()


#%%

# Doing some manual import of the SMHI temperature readings., so it can be included
# in the DB from a CSV.
# I am resampling it to 15-min before saving it in .csv

smhifiles = glob.glob(xls_data_path + 'smhi-open-data/*.xlsx')

all_data = pd.DataFrame()

for name in smhifiles:
    df = pd.read_excel(name,index_col=0)
    df.index = pd.to_datetime(df.index)
    all_data = all_data.append(df)

df2 = all_data.resample('15min').mean()
df2 = df2.interpolate(method='linear')

df2.to_csv(csv_data_path+'smhi-opendata.csv')

headers = open(database_path + 'smhi_headers.csv','w')
a = list(df2)
for item in a:
    headers.write('\n' + item)
headers.close()


#%%

df['Boiler_starbord']['2014-03-07']

#%%
