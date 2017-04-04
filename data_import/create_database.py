import pandas as pd
import numpy as np
import glob

data_path = '/Users/fredde/Database/csv/'

filenames = glob.glob(data_path + '*.csv')

df=pd.DataFrame()


#%%
# Playing

#df = pd.read_csv(filenames[0],header=0,index_col=0,dtype='a')
#df.head()

#%%
# First this creates a large DataFrame, one which contain everything.

#all_data=pd.DataFrame()

for filename in filenames:
    df = pd.read_csv(filename,header=0,index_col=0,dtype='a')
    print('Loading: '+str(filename))
    df=df.append(df)
    # The last part is about appending the new DataFrame 2 (df2) to the all_data DataFrame.

#    all_data=all_data.append(df2)

df=df.sort_index()
df.to_hdf(data_path + 'all_data.h5','table')

# First sort the DataFrame after Index (time series). Then save it in HDF.

#print('Writing HDF data with Pandas')
#all_data=all_data.sort_index()
#all_data.to_hdf(data_path + 'all_data.h5','table')

# Write all the new headers to a csv-file

#headers = open(data_path + 'headers.csv','w')
#a = list(all_data)
#for item in a:
#    headers.write('\n' + item)
