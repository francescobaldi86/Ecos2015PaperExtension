import pandas as pd
import numpy as np
import glob

# Where is the data
xlsdata_path = '/Users/fredde/Database/data-files/'
data_path = '/Users/fredde/Database/csv/'

# Load all Excel-file names
filenames = glob.glob(xlsdata_path + '*.xls')



for filename in filenames:
    df=pd.DataFrame()
    df2=pd.DataFrame()
    df = pd.read_excel(filename,index_col=0)
    print('Processing: '+str(filename.split('/')[-1].split('.')[0]))

    headers = list(df)      # Create list of headers

    # And now extract the relevant meta-data in the first couple of rows.

    headers_new = list() # Make a new list of headers in the file. Using '#' as a split.

    for head in headers:
        headers_new.append(str(head)+'#'+str(df[head].iloc[0])+'#'+str(df[head].iloc[1])+
        '#'+str(df[head].iloc[5])+'#'+str(df[head].iloc[8]))

    # Now there is a list of new headers names, and we now want to strip the first 13 rows of each
    # column and adding the relevant meta_data in the header. This is done by creating a new DataFrame.

    for i in range(len(headers_new)):
        series = df[headers[i]].ix[13:]
        df2[headers_new[i]] = series
    # Save the cleaned file as a csv file for later processing.
    df2.to_csv(data_path + filename.split('/')[-1].split('.')[0] + '.csv')
