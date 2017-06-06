##
##
## Analyse the fuel flow meters. Comparison with the fuel flow mass meters
# which are used as the calibration, the "true" measurement.
import pandas as pd
import numpy as np
import os
%pylab

#%%

project_path = os.path.realpath('.')
database_path = project_path + os.sep + 'Database' + os.sep
df = pd.read_hdf(database_path + 'selected_df.h5','table')

df_flow_meters = pd.read_excel(project_path + os.sep + 'Analyse' + os.sep + 'Mass_flowmeters.xlsx',index_col=0)
df_flow_meters.index = pd.to_datetime(df_flow_meters.index)

FO1_flow = df['FO BOOST 1 CONSUMPT:6165:m3/h:Average:900']/3600*15*60
FO1_flow = FO1_flow.resample('D').sum()
FO2_flow = df['FO BOOST 2 CONSUMPT:6166:m3/h:Average:900']/3600*15*60
FO2_flow = FO2_flow.resample('D').sum()
s1 = (FO1_flow/df_flow_meters['FO_engine_1_3'])
s2 = (FO2_flow/df_flow_meters['FO_engine_2_4'])

# This counts the length and the nr of floats. As there are some missing data
# already at the beginning it is essential that we save this variable.

s1_missing_before = len(s1)-s1.count()
s2_missing_before = len(s2)-s2.count()


# Remove the 5% top and low quantiles so the outliers are removed
# quantiles

q_high = 0.9
q_low = 0.1

# First export and merge the index of each series, also a total merge
# some of them are overlapping. This creates three DatetimeIndex which
# hopefully can be used for knowing where the data is invalid....

removed_s1 = s1[( s1 > s1.quantile(q_high) ) | ( s1 < s1.quantile(q_low) )].index
removed_s2 = s2[( s2 > s2.quantile(q_high) ) | ( s2 < s2.quantile(q_low) )].index
removed_index = pd.DatetimeIndex.join(removed_s1,removed_s2)

# Remove and replace with NaN

s1[( s1 > s1.quantile(q_high) ) | ( s1 < s1.quantile(q_low) )] = np.nan
s2[( s2 > s2.quantile(q_high) ) | ( s2 < s2.quantile(q_low) )] = np.nan

# This counts the missing NaN after the filter.

s1_missing_after = len(s1)-s1.count()
s2_missing_after = len(s2)-s2.count()

# This is if we want to normalize around the mean which can
# give an indication in percent of how much it varies

#s1 = s1 / s1.mean()
#s2 = s2 / s2.mean()


print('Removed points 1/3: ' + str(s1_missing_after-s1_missing_before) + ' of: '+str(len(s1)))
print('Removed points 2/4: ' + str(s2_missing_after-s2_missing_before) + ' of: '+str(len(s2)))
#print(removed_s1)
#print(removed_s2)

print('Standard deviation 1/3 :'+str(s1.std()))
print('Standard deviation 2/4 :'+str(s2.std()))

print('Constant 1/3 :'+str((1/s1.mean())))
print('Constant 2/4 :'+str((1/s2.mean())))


s1.mean()

s1.describe()
s1.plot(linewidth=0,marker='x')
s2.plot(linewidth=0,marker='x')

removed_index
#####
#####
#####
#%%
# Using the counters to see if that is better..


FO1_counter = df['FO BOOST 1 CONSUMPT:6165:m3:Average:900']
FO2_counter = df['FO BOOST 2 CONSUMPT:6166:m3:Average:900']

FO1_counter_max = FO_1_counter.resample('D').max()
FO2_counter_max = FO_2_counter.resample('D').max()
FO1_counter_day = pd.Series(index=FO1_counter_max.index)
FO2_counter_day = pd.Series(index=FO2_counter_max.index)

for i in range(1,len(FO1_counter_max)):
    FO1_counter_day[i] = FO1_counter_max[i]-FO1_counter_max[i-1]
    FO2_counter_day[i] = FO2_counter_max[i]-FO2_counter_max[i-1]

a = FO1_counter_day-df_flow_meters['FO_engine_1_3']
b = FO2_counter_day-df_flow_meters['FO_engine_2_4']

a[( a > a.quantile(q_high) ) | ( a < a.quantile(q_low) )] = np.nan
b[( b > b.quantile(q_high) ) | ( b < b.quantile(q_low) )] = np.nan

a=a/a.mean()
b=b/b.mean()

a.plot()
b.plot()
