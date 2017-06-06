import pandas as pd
import os

project_path = os.path.realpath('.')
database_path = project_path + os.sep + 'Database' + os.sep
df = pd.read_hdf(database_path + 'selected_df.h5','table')

# Create dictonary translation from original to new! (not the other way around)
headers_dict = pd.read_excel(project_path + os.sep + 'General' + os.sep + 'headers_dict.xlsx')
# Load the data from the Excel-file with headers. Please not the project_path
# Create a list of each column, then a dictonary which is acting as the translotor.
old = headers_dict['ORIGINAL_HEADER']
new = headers_dict['NEW_HEADER']
hd = {}
for n in range(len(old)):
    hd[old[n]] = new[n]
    hd[new[n]] = old[n] # To make it bi-directional

#%%
# Load the the values from the xlsx-file which contains information about
# the data cleaning process.
# This section could later on be implemented in the pre-processing code

# We must only work with the rows that are in the selected dataset,
# as the headers_dict contains all data points from the raw database we need
# a new index.

index_selected = headers_dict.loc[headers_dict['FB'] == 'x']

for i in range(len(index_selected)):

    # In the headers_dict file there are values and relations stored for
    # each data-point. Most of them does not contain anything but those that
    # are needs to be put back in to the data-set.

    headers_dict.loc[i]['VALUE']
    headers_dict.loc[i]['REL']
    headers_dict.loc[i]['VAR']
    headers_dict.loc[i]['HIGH_BOUND']
    headers_dict.loc[i]['LOW_BOUND']






#%%


# Testing grounds...
i = 14

name = headers_dict.loc[i]['ORIGINAL_HEADER']
value = headers_dict.loc[i]['VALUE']
rel = headers_dict.loc[i]['REL']
var = hd[headers_dict.loc[i]['VAR']]
high_bound = headers_dict.loc[i]['HIGH_BOUND']
low_bound =headers_dict.loc[i]['LOW_BOUND']

var
eval('df[name]')

df[hd[var]]


eval("df[name][df[var] "+ rel +" value][df[name] > high_bound]")
eval("df[name][df[var] "+ rel +" value][df[name] < low_bound]")





df[name][(df[var] > value) & (df[name] < low_bound)] = 0

df[name][(df[var] > value) & (df[name] < low_bound)]

[df[name] < low_bound] = 0

df[name][df[var] > value][df[name] < low_bound] = s1

s1[]=0

s1

df[name][df[var] > value][df[name] < low_bound]


#%%
header = list(df)[0]
print(header)
s0 = df[header][df[d['AE1-TC__RPM_']] > 5000.]
s1 = df[header][df[d['AE1-TC__RPM_']] > 5000.]
s2 = df[header][df[d['AE1-TC__RPM_']] > 5000.]

s1[s1<s1.quantile(q=0.01)]=s1.quantile(q=0.01)
s2[s2<s2.quantile(q=0.01)]=NaN
s2 = s2.interpolate()
s0[s0<0.1]
s0['2013-12-21'].plot()
ss0 = df[d['AE1-TC__RPM_']][df[d['AE1-TC__RPM_']]>5000.]

df[list(df)[0]][(df[list(df)[0]]>1.3) & (df[list(df)[0]]<1.5)]

a = 'max()'


#%%

name = d['AE1-CAC_AIR_P_OUT']
name1 = d['AE1-TC__RPM_']
name1

df[name][df[name1] > 5000].quantile(q=0.01)






eval('s1.'+a)
s1.max()

df[list(df)[0]][(df[list(df)[0]]>1.3) & ()]


(1 > 0) & (1 > 0)

ss0['2013-12-21'].plot()
sum(s1-s2)
s1.describe()

s2.describe()
s1.describe()
s1[s1<0]=NaN
s1
s2=s1.interpolate()
s2
df[header]
sum(s2 - df[header])
