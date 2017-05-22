import pandas as pd
project_path = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/'
headers = pd.read_excel(project_path + 'General/headers_dict.xlsx')
# Load the data from the Excel-file with headers. Please not the project_path

#%%

# Create a list of each column, then a dictonary which is acting as the translotor.

old = headers['ORIGINAL_HEADER']
new = headers['NEW_HEADER']
d = {}
for n in range(len(old)):
    d[new[n]] = old[n]

#%%

# Testing the function . Seems ok!

print(d['AE1-CAC_AIR_P_OUT'])
