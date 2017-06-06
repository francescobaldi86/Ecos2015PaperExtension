##
##
## Analyse the fuel flow meters. Comparison with the fuel flow mass meters
# which are used as the calibration, the "true" measurement.
import pandas as pd
import numpy as np
import os
%pylab

project_path = os.path.realpath('.')
database_path = project_path + os.sep + 'Database' + os.sep
df = pd.read_hdf(database_path + 'selected_df.h5','table')

df_flow_meters = pd.read_excel(project_path + os.sep + 'Analyse' + os.sep + 'Mass_flowmeters.xlsx',index_col=0)
df_flow_meters.index = pd.to_datetime(df_flow_meters.index)


#%%
FO_1_flow = df['FO BOOST 1 CONSUMPT:6165:m3/h:Average:900'].resample('D').sum()
FO_1_counter = df['FO BOOST 1 CONSUMPT:6165:m3:Average:900']
FO_2_flow = df['FO BOOST 2 CONSUMPT:6166:m3/h:Average:900'].resample('D').sum()
FO_1_counter = df['FO BOOST 2 CONSUMPT:6166:m3:Average:900']

s1 = (df_flow_meters['FO_engine_1_3']/FO_1_flow)
s2 = (df_flow_meters['FO_engine_2_4']/FO_2_flow)

s1[( s1 > s1.quantile(0.95) ) | ( s1 < s1.quantile(0.05) )] = np.nan
s2[( s2 > s2.quantile(0.95) ) | ( s2 < s2.quantile(0.05) )] = np.nan

len(s1)-s1.count()

s1 = s1 / s1.mean()
s2 = s2 / s2.mean()

s1.describe()


s1.plot()
s2.plot()
