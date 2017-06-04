import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import os
%pylab
# This is for inline plotting

project_path = os.path.realpath('.')

project_path
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



# Checking the difference between Landsort sea water temperature and the temperature readings
# from MS Birka SW-temp. We have missing data on this point for the first half year.
#

sw_smhi_landsort = pd.read_excel(database_path + '/smhi-open-data/water_T_landsort_smhi-opendata_5_2507_20170602_084638.xlsx',index_col=0)
sw_smhi_landsort.index = pd.to_datetime(sw_smhi_landsort.index)
havstemp=sw_smhi_landsort['Havstemperatur']['2014-06-01':'2014-12-15'].resample('15min').mean()
havstemp=havstemp.interpolate()
havstemp.plot()
i1='SEA_SW_T_'
#i2='SW-ME-AE24_SW_T_IN'

#series1=df[d[i1]]['2014-06-01']
#series2=df[d[i2]]['2014-06-01']

series1=df[d[i1]]['2014-06-01':'2014-12-15'].resample('15min').mean()
#series2=df[d[i2]].resample('D')
#series2= series2[series1 > 0]
#series1= series1[series1 > 0]
series1.plot()
#diff_sq = (((havstemp - series1)**2)**0.5).mean()
#series2.plot()
#plt.plot(series1,linewidth=0,marker='x')
plt.title((d[i1])+' RMS: '+str( ((((havstemp - series1)**2).sum())/len(havstemp))**0.5 ) )
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

diff_sq
diff_sq/len(havstemp)
type(diff_sq)


diff_sq = ((havstemp - series1)**2)**0.5

diff_sq.sum()/len(havstemp)

diff_2 = abs(havstemp-series1).mean()
diff_2

diff_2-diff_sq
diff_2-diff_sq


diff_sq = ((((havstemp - series1)**2).sum())/len(havstemp))**0.5
diff_sq
