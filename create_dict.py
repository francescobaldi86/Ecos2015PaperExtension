import csv
headers_dict = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/data_import/headers_dict.csv'

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
