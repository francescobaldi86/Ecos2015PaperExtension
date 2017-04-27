import pandas as pd
import glob as glob
import csv

database = '/Users/fredde/Database/all_data_1year_comp.h5'
headers_out = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/data_import/headers_out.csv'
headers_dict = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/data_import/headers_dict.csv'

# Load headers name, save these to a .csv file for manual processing.

df = pd.read_hdf(database, 'table')

#%%

headers = list(df)

header_file = open(headers_out,'w')
for item in headers:
    header_file.write('\n' + item)

#%%

# Now it is manual processing in a text-editor. The output will be a file
# which has two columns, with the

#%%


# Load the headers file. Excel seems to save with ; as the delimiter, but it is easy
# fixed below. This creates as dictonary which then can be used as the translation.


with open(headers_dict, 'r') as f:
    d={}
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        k, v = row
        d[k] = v


d[headers[0]]


#%%
