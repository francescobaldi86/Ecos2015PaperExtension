<<<<<<< HEAD
import csv
headers_dict = 'C:\\Users\\FrancescoBaldi\\switchdrive\\Work in progress\\Paper 0\\Ecos2015PaperExtension\\data_import\\headers_dict.csv'
=======
import pandas as pd
project_path = '/Users/fredde/Dropbox/GitHub/Ecos2015PaperExtension/'
headers = pd.read_excel(project_path + 'General/headers_dict.xlsx')
# Load the data from the Excel-file with headers. Please not the project_path
>>>>>>> cd83905529f30962e5de0d7255139c4ee02cb730

#%%

# Create a list of each column, then a dictonary which is acting as the translotor.

old = headers['ORIGINAL_HEADER']
new = headers['NEW_HEADER']
d = {}
for n in range(len(old)):
    d[new[n]] = old[n]

#%%

<<<<<<< HEAD
##d[headers[0]]
=======
# Testing the function . Seems ok!
>>>>>>> cd83905529f30962e5de0d7255139c4ee02cb730

input = 'AE1-CAC_AIR_P_OUT'

print('The input:\n'+ input + '\ngives output:\n' + d[input])
