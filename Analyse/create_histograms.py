import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import os
%pylab
# This is for inline plotting

project_path = os.path.realpath('')

database_path = project_path + os.sep + 'Database' + os.sep
graph_path = project_path + os.sep + 'Analyse' + os.sep + 'Graph' + os.sep

df = pd.read_hdf(database_path + 'selected_df.h5','table')


#%%
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
nr_bin=60

for i in list(df):
    series1 = df[i].dropna()
    series2 = series1[~series1.index.duplicated(keep='first')]
    plt.hist(series2,bins=nr_bin)
    plt.title((d[i]))
    plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
    plt.figtext(0.13,0.66,series2.describe(),alpha=0.8,fontsize=8)
    plt.savefig(graph_path + d[i])
    fig = matplotlib.pyplot.gcf() # higher res
    fig.set_size_inches(10,5) #higher res
    plt.clf()


#%%

i='AE1-TC_EG_T_OUT'

series2=df[d[i]]
series2 = series2[series2 > 0]
plt.hist(series2,bins=nr_bin)
plt.title((d[i]))
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series2.describe(),alpha=0.8,fontsize=8)
plt.savefig(graph_path + d[i])
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()


#%%



i1='AE1-HT_FW_T_IN'
i2='AE1_POWER_Wdot_OUT'

series1=df[d[i1]]
series2=df[d[i2]]
series2= series2[series1 > 60]
series1= series1[series1 > 60]

plt.plot(series2,series1,linewidth=0,marker='x')
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()


#%%


i1='AE1-LOC_OIL_P_IN'
i2='AE1-LOC_OIL_T_OUT'

series1=df[d[i1]]
series2=df[d[i2]]
series2= series2[series1 > 0]
series1= series1[series1 > 0]
plt.plot(series2,series1,linewidth=0,marker='x')
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()


#%%



i='AE2-LT-CAC_FW_T_IN'

series2=df[d[i]]
series2 = series2[series2 > 0]
plt.hist(series2,bins=nr_bin)
plt.title((d[i]))
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series2.describe(),alpha=0.8,fontsize=8)
plt.savefig(graph_path + d[i])
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()


#%%



i1='AE2-LT-CAC_FW_T_IN'
i2='AE1-LT-CAC_FW_T_IN'

series1=df[d[i1]]
series2=df[d[i2]]
series2= series2[series2 > 40]
series1= series1[series1 > 40]

plt.hist(series1,bins=nr_bin,alpha=0.5,color='r')
plt.hist(series2,bins=nr_bin,alpha=0.5)

plt.title((d[i]))
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series2.describe(),alpha=0.8,fontsize=8)
plt.figtext(0,0.66,series2.describe(),alpha=0.8,fontsize=8)
plt.savefig(graph_path + d[i])
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()




#%%

#%%


i1='ER13-HT_FW_T_1'
i2='AE2-HT_FW_T_IN'

series1=df[d[i1]]
series2=df[d[i2]]
series2= series2[series2 > 40]
series1= series1[series1 > 40]

plt.hist(series1,bins=nr_bin,alpha=0.5,color='r')
plt.hist(series2,bins=nr_bin,alpha=0.5)

plt.title(i1 +' and ' + i2)
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series2.describe(),alpha=0.8,fontsize=8)
plt.figtext(0.13,0.42,series2.describe(),alpha=0.8,fontsize=8)
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%






i1='AE1-LT-CAC_FW_T_IN'
i2='AE1-CAC_AIR_T_OUT'

series1=df[d[i1]]
series2=df[d[i2]]
series2= series2[series1 > 0]
series1= series1[series1 > 0]
plt.plot(series2,series1,linewidth=0,marker='x')
plt.plot(series1,series1)
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()




#%%
s1 = df[list(df)[4]]
plt.hist(s1,bins=50)
plt.title(d[list(df)[4]])
#plt.text(-10,-10,s1.describe(),fontsize=10)
plt.figtext(0.13,0.66,s1.describe(),alpha=0.8,fontsize=8)
#plt.suptitle(s1.describe())
#plt.title(s1.describe())

#fig = matplotlib.pyplot.gcf()
#fig.set_size_inches(18,10)
plt.show


s1.describe()



#%%
s1 = df[list(df)[2]]

s2 = s1.dropna()



len(s2)


df2 = pd.DataFrame()

s3 = s2[~s2.index.duplicated(keep='first')]

len(s3)

s2.drop_duplicates(subset='index',keep='last')

series = df[list(df)[0]].dropna().drop_duplicates()

len(series)


s1 = s1.drop_duplicates().dropna()

plt.hist(s1,bins=50)
plt.xlabel(d[list(df)[3]]+ 'testing testing')
plt
plt.show()
