import pandas as pd
import os
%pylab
# This is for inline plotting

project_path = os.path.realpath('.')

database_path = project_path + os.sep + 'Database' + os.sep

df = pd.read_hdf(database_path + 'selected_df.h5','table')

# Create dictonary translation from original to new! (not the other way around)
headers = pd.read_excel(project_path + os.sep + 'General' + os.sep + 'headers_dict.xlsx')
# Load the data from the Excel-file with headers. Please not the project_path
# Create a list of each column, then a dictonary which is acting as the translotor.
old = headers['ORIGINAL_HEADER']
new = headers['NEW_HEADER']
d = {}
for n in range(len(old)):
    d[old[n]] = new[n]
    d[new[n]] = old[n] # To make it bi-directional

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
