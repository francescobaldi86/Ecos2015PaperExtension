import pandas as pd
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import os
import unicodedata
import re
%pylab
# This is for inline plotting

project_path = os.path.realpath('.')

project_path
database_path = project_path + os.sep + 'Database' + os.sep
graph_path = project_path + os.sep + 'Analyse' + os.sep + 'Graph' + os.sep

df = pd.read_hdf(database_path + 'selected_df.h5','table')

def slugify(value):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)

    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)

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

df


list(df)[2]

df[list(df)[2]]['2014-02']


plot(df[list(df)[2]]['2014-02-11'])



#%%

# creating histograms for all Datapoints and saving them

nr_bin=60

for i in list(df):
    series1 = df[i]
    plt.hist(series1,bins=nr_bin)
    plt.title((d[i]))
    plt.xlabel('Datapoints: ' + str(len(series1)) + ', bins: ' + str(nr_bin))
    plt.figtext(0.13,0.66,series1.describe(),alpha=0.8,fontsize=8)
    plt.savefig(graph_path + slugify(d[i]))
    fig = matplotlib.pyplot.gcf() # higher res
    fig.set_size_inches(10,5) #higher res
    plt.clf()


#%%


# creating histograms for all Datapoints filtering only engine ON and saving

nr_bin=60

for i in list(df):
    if (d[i][:2] == 'AE') | (d[i][:2] == 'ME'):
        series1 = df[i][df[d[d[i][:3]+'-TC__RPM_']] > 5000]
    else:
        series1 = df[i]

    plt.hist(series1,bins=nr_bin)
    plt.title((d[i]) + 'filtered TC > 5000')
    plt.xlabel('Datapoints: ' + str(len(series1)) + ', bins: ' + str(nr_bin))
    plt.figtext(0.13,0.66,series1.describe(),alpha=0.8,fontsize=8)
    plt.savefig(graph_path + '/eng_on/' + slugify(d[i]))
    fig = matplotlib.pyplot.gcf() # higher res
    fig.set_size_inches(10,5) #higher res
    plt.clf()


#%%
# full year time series plotting for ship speed. resampling to one hour.

i1='SHIP_SPEED_KNOT_'
series1=df[d[i1]]
series1 = series1.resample('H').mean()
series1.plot(linewidth=0,marker='o')
plt.title(i1)
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%

# ships speed time series for each day average and both max and mean

i1='SHIP_SPEED_KNOT_'
series1=df[d[i1]]
speed_av = series1.resample('M').mean()
speed_max = series1.resample('M').max()
speed_av.plot(linewidth=0,marker='o')
speed_max.plot(linewidth=0,marker='*')
plt.title(i1 + ' average and maximum, Month')
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%
# Resample the speed for hour and make histogram over a year

nr_bin=linspace(0,21,22)
i1='SHIP_SPEED_KNOT_'
series1=df[d[i1]]
speed_av = series1.resample('H').mean()
plt.hist(speed_av,bins=nr_bin)
plt.title(i1)
plt.figtext(0.13,0.66,speed_av.describe(),alpha=0.8,fontsize=8)
plt.show()

#%%

# the total elecrical power in percentage of maximum capacity

nr_bin=50
i1='AE1_POWER_Wdot_OUT'
i2='AE2_POWER_Wdot_OUT'
i3='AE3_POWER_Wdot_OUT'
i4='AE4_POWER_Wdot_OUT'
series1=df[d[i1]]
series2=df[d[i2]]
series3=df[d[i3]]
series4=df[d[i4]]

tot_aux_power = (series1 + series2 + series3 + series4) / (2760 * 4)

plt.hist(tot_aux_power,bins=nr_bin)
#tot_aux_power = tot_aux_power.resample('H').mean()
#plt.hist(tot_aux_power,bins=nr_bin)

plt.title('total aux power percentage')
plt.figtext(0.13,0.66,tot_aux_power.describe(),alpha=0.8,fontsize=8)
plt.show()


#%%
# Time series plotting of total aux power

i1='AE1_POWER_Wdot_OUT'
i2='AE2_POWER_Wdot_OUT'
i3='AE3_POWER_Wdot_OUT'
i4='AE4_POWER_Wdot_OUT'
series1=df[d[i1]]
series2=df[d[i2]]
series3=df[d[i3]]
series4=df[d[i4]]

tot_aux_power = (series1 + series2 + series3 + series4) / (2760 * 4)
tot_aux_power_av = tot_aux_power.resample('D').mean()
tot_aux_power_max = tot_aux_power.resample('D').max()
tot_aux_power_av.plot(linewidth=0,marker='x')
tot_aux_power_max.plot(linewidth=0,marker='_')
plt.title('total aux power average and max/day')
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%

month='2014-04'

i1='AE1_POWER_Wdot_OUT'
i2='AE2_POWER_Wdot_OUT'
i3='AE3_POWER_Wdot_OUT'
i4='AE4_POWER_Wdot_OUT'
series1_mean=df[d[i1]].resample('D').mean()/2760
series2_mean=df[d[i2]].resample('D').mean()/2760
series3_mean=df[d[i3]].resample('D').mean()/2760
series4_mean=df[d[i4]].resample('D').mean()/2760

series1_max=df[d[i1]].resample('D').max()/2760
series2_max=df[d[i2]].resample('D').max()/2760
series3_max=df[d[i3]].resample('D').max()/2760
series4_max=df[d[i4]].resample('D').max()/2760

series1_mean[month].plot(marker='x',label=i1)
series2_mean[month].plot(marker='x',label=i2)
series3_mean[month].plot(marker='x',label=i3)
series4_mean[month].plot(marker='x',label=i4)

series1_max[month].plot(linewidth=0,marker='o',label=i1+' max')
series2_max[month].plot(linewidth=0,marker='o',label=i2+' max')
series3_max[month].plot(linewidth=0,marker='o',label=i3+' max')
series4_max[month].plot(linewidth=0,marker='o',label=i4+' max')

plt.legend(bbox_to_anchor=(0, 1), loc=2, borderaxespad=0.)

plt.title('aux engine average and max/day')
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()


#%%
nr_bin=50
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


#comparing static head

nr_bin=100
i1='AE1-HT_FW_P_IN'
i2='AE2-HT_FW_P_IN'
i3='AE3-HT_FW_P_IN'
i4='AE4-HT_FW_P_IN'

series1=df[d[i1]][df[d['AE1-TC__RPM_']] < 5000.]
series2=df[d[i2]][df[d['AE2-TC__RPM_']] < 5000.]
series3=df[d[i3]][df[d['AE3-TC__RPM_']] < 5000.]
series4=df[d[i4]][df[d['AE4-TC__RPM_']] < 5000.]

series1= series1[(series1 >0.8) & (series1 < 1.2)]
series2= series2[(series2 >0.8) & (series2 < 1.2)]
series3= series3[(series3 >0.8) & (series3 < 1.2)]
series4= series4[(series4 >0.8) & (series4 < 1.2)]

plt.hist(series1,bins=nr_bin,alpha=0.5,color='r')
plt.hist(series2,bins=nr_bin,alpha=0.5)
plt.hist(series3,bins=nr_bin,alpha=0.5,color='b')
plt.hist(series4,bins=nr_bin,alpha=0.5)

plt.title(i1 +' and ' + i2)
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series1.describe(),alpha=0.8,fontsize=8)
plt.figtext(0.13,0.42,series2.describe(),alpha=0.8,fontsize=8)
plt.figtext(0.65,0.66,series3.describe(),alpha=0.8,fontsize=8)
plt.figtext(0.65,0.42,series4.describe(),alpha=0.8,fontsize=8)
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%




#%%


i1='AE1-TC_EG_T_IN1'
i2='AE1-TC_EG_T_IN2'

series1=df[d[i1]]['2014-01-10']
series2=df[d[i2]]['2014-01-10']
series2= series2[series2 > 40]
series1= series1[series1 > 40]

plot(series1)
plot(series2)

#plt.hist(series1,bins=nr_bin,alpha=0.5,color='r')
#plt.hist(series2,bins=nr_bin,alpha=0.5)

plt.title(i1 +' and ' + i2)
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series2.describe(),alpha=0.8,fontsize=8)
plt.figtext(0.13,0.42,series2.describe(),alpha=0.8,fontsize=8)
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

plt.figure()

i3='AE1-TC__RPM_'
series3=df[d[i3]]['2014-01-10']
plot(series3)

#plt.hist(series1,bins=nr_bin,alpha=0.5,color='r')
#plt.hist(series2,bins=nr_bin,alpha=0.5)

plt.title(i1 +' and ' + i2)
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series3.describe(),alpha=0.8,fontsize=8)
#plt.figtext(0.13,0.42,series2.describe(),alpha=0.8,fontsize=8)
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

i1='AE2-LT-LOC_FW_T_OUT'
i2='AE2-LOC_OIL_T_OUT'


#series1=df[d[i1]]['2014-06-01']
#series2=df[d[i2]]['2014-06-01']


series1=df[d[i1]].resample('D')
series2=df[d[i2]].resample('D')
#series2= series2[series1 > 0]
#series1= series1[series1 > 0]
series1.plot()
series2.plot()
#plt.plot(series1,linewidth=0,marker='x')
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%

i1='AE2-LT-CAC_FW_T_IN'
i2='AE1-LT-CAC_FW_T_IN'
i1='AE2-LT-CAC_FW_T_IN'
i2='AE1-LT-CAC_FW_T_IN'

series1=df[d[i1]]
series2=df[d[i2]]
series1=df[d[i1]]
series2=df[d[i2]]


series2= series2[series2 > 40]
series1= series1[series1 > 40]
series2= series2[series2 > 40]
series1= series1[series1 > 40]



plt.hist(series1,bins=nr_bin,alpha=0.5,color='r')
plt.hist(series2,bins=nr_bin,alpha=0.5)

plt.title((d[i]))
plt.xlabel('Datapoints: ' + str(len(series2)) + ', bins: ' + str(nr_bin))
plt.figtext(0.13,0.66,series2.describe(),alpha=0.8,fontsize=8)
plt.figtext(0,0.66,series2.describe(),alpha=0.8,fontsize=8)
#plt.savefig(graph_path + d[i])
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%

# Checking the difference between Landsort sea water temperature and the temperature readings
# from MS Birka SW-temp. We have missing data on this point for the first half year.
#

sw_smhi_landsort = pd.read_excel(database_path + '/smhi-open-data/water_T_landsort_smhi-opendata_5_2507_20170602_084638.xlsx',index_col=0)
sw_smhi_landsort.index = pd.to_datetime(sw_smhi_landsort.index)
havstemp=sw_smhi_landsort['Havstemperatur']['2014-06-01':'2014-12-15'].resample('15min').mean()
havstemp=havstemp.interpolate()
havstemp.plot()
i1='SEA_SW_T_'


series1=df[d[i1]]['2014-06-01':'2014-12-15'].resample('15min').mean()
series1.plot()
plt.title((d[i1])+' RMS: '+str( ((((havstemp - series1)**2).sum())/len(havstemp))**0.5 ) )
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

# The RMS difference
diff_sq = ((((havstemp - series1)**2).sum())/len(havstemp))**0.5
print(diff_sq)

# The absolute difference
diff_2 = abs(havstemp-series1).mean()
print(diff_2)


#%%

# Checking the difference between Landsort sea water temperature and the temperature readings
# from MS Birka air-temp.
#

air_T_smhi = pd.read_excel(database_path + '/smhi-open-data/air_T_sv_hogarna_smhi-opendata_1_99270_20170604_094558.xlsx',index_col=0)
air_T_smhi.index = pd.to_datetime(air_T_smhi.index)
#%%

lufttemp=air_T_smhi['Lufttemperatur']['2014-01-01':'2014-12-15'].resample('D').mean()
lufttemp=lufttemp.interpolate()
lufttemp.plot()
i1='ER_AIR_T_'


series1=df[d[i1]]['2014-01-01':'2014-12-15'].resample('D').mean()
series1.plot()
plt.title((d[i1])+' RMS: '+str( ((((lufttemp - series1)**2).sum())/len(lufttemp))**0.5 ) )
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

# The RMS difference
#diff_sq = ((((lufttemp - series1)**2).sum())/len(lufttemp)**0.5
#print(diff_sq)

# The absolute difference
#diff_2 = abs(lufttemp-series1).mean()
#print(diff_2)


#%%


# Checking the difference between Landsort sea water temperature and the temperature readings
# from MS Birka outside air-temp which are missing for the half year
#

air_T_smhi = pd.read_excel(database_path + '/smhi-open-data/air_T_sv_hogarna_smhi-opendata_1_99270_20170604_094558.xlsx',index_col=0)
air_T_smhi.index = pd.to_datetime(air_T_smhi.index)
#%%

lufttemp=air_T_smhi['Lufttemperatur']['2014-06-01':'2014-12-15'].resample('15min').mean().interpolate(method='linear')
#lufttemp = lufttemp['2014-06-01':'2014-12-15']

lufttemp.plot(marker='x')
i1='OUTSIDE_AIR_T_'


series1=df[d[i1]]['2014-06-01':'2014-12-15'].resample('15min').mean()
series1.plot()
plt.title((d[i1])+' RMS: '+str( ((((lufttemp - series1)**2).sum())/len(lufttemp))**0.5 ) )
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

# The RMS difference
RMS = ((((lufttemp - series1)**2).sum())/len(lufttemp))**0.5
print(RMS)

# The absolute difference
diff_2 = abs(lufttemp-series1).mean()
print(diff_2)


#%%





# Both time series of outside air and sea water temp seems to be missing
# in the first part of the year. This is why we need to use the smhi-open data
#

i1='OUTSIDE_AIR_T_'
i2='SEA_SW_T_'


#series1=df[d[i1]]['2014-06-01']
#series2=df[d[i2]]['2014-06-01']


series1=df[d[i1]].resample('D').mean()
series2=df[d[i2]].resample('D').mean()
#series2= series2[series1 > 0]
#series1= series1[series1 > 0]
series1.plot()
series2.plot()
#plt.plot(series1,linewidth=0,marker='x')
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%

# Check time series of hot water heater temperature

i1='__T_'

series1=df[d[i1]].resample('D').mean()
series1.plot()
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()
#%%

#%%

#
#
#

rho_do = 800
i1='DO DAY TANK T32C:6111:m3:Average:900'
i2='DO STORAGE TK T22P:6112:m3:Average:900'

series1=df[d[i1]].resample('H').mean()
series2=df[d[i2]].resample('H').mean()


mass_flow_tank = (series1.diff()-series2.diff())*rho_do
mass_flow_tank
mass_flow_tank.plot()

#series1.plot()
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()
#%%

i1='FO BOOST 1 CONSUMPT:6165:m3:Average:900'

series1=df[d[i1]]#.resample('H').mean()

series1.plot()
plt.title((d[i1]))
fig = matplotlib.pyplot.gcf() # higher res
fig.set_size_inches(10,5) #higher res
plt.show()

#%%
