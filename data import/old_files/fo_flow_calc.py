
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np

#Import data into Pandas Data Frame
#The first column is data type, index col is time series Excel.
#I am using ME.XLSX and AE.XLSX, 15 min interval data.
ME = pd.read_excel('ME.xlsx',index_col=0)
AE = pd.read_excel('AE.xlsx',index_col=0)


# In[2]:

list(ME) # List all the variables in the Data Frame Main Engines.


# In[3]:

list(AE) # List AE Vars


# In[24]:

list(FO) # List vars in FO, fuel oil and tanks.


# In[19]:

# Define funcion for engine load. Fuel rack pos. i percent * 100.

def ME_Load(fuel_rack, rpm):
    load = (fuel_rack / 100.) * (rpm / 500.)**2
    return load

# Define function for Fuel Oil. The constant 0.323129514 is derived from
# linear regression of the mean values from all engines test protocol data.
# Intercept is set to zero, R^2 = 0.9938. Max engine RPM = 500.

def FRP(load):
    FRP = 0.7807 * load + 0.2129
    return FRP

def ME_FO_flow(load, rpm):
    FRP = 0.7807 * (load / 100.) + 0.2129
    ME_FO_flow = 0.04716 * FRP * rpm / 60 # För att rapportera i kg/s
    return ME_FO_flow

# * 1.268029

# For the Auxiliary Engines. Value in kg/s
# linear regression of the mean values from all engines test protocol data. * 1.268029 is the correction factor when validated
# against the mass flow meters. Max electrial Power is 2680 kW.
# Intercept is set to zero, R^2 = 0.9949.
 
def AE_FO_flow(electrical_power):
    AE_FO_flow = (electrical_power / 2680.) * 0.142732820019249
    return AE_FO_flow

# * 1.268029


# In[25]:

# Calculate the flows from all ME and AE. Data is in Pandas Time Series.
# The data is in 15 minute interval, and 15 min * 60 s is for integrating from the average of kg/s to kg for a 15 min interval.

me1_flow = ME_FO_flow(ME['ME1 FUEL RACK POSIT'],ME['ME1 ENGINE SPEED']) * 15
me2_flow = ME_FO_flow(ME['ME2 FUEL RACK POSIT'],ME['ME2 ENGINE SPEED']) * 15
me3_flow = ME_FO_flow(ME['ME3 FUEL RACK POSIT'],ME['ME3 ENGINE SPEED']) * 15
me4_flow = ME_FO_flow(ME['ME4 FUEL RACK POSIT'],ME['ME4 ENGINE SPEED']) * 15
ae1_flow = AE_FO_flow(AE['AE1 POWER']) * 15 * 60
ae2_flow = AE_FO_flow(AE['AE2 POWER']) * 15 * 60
#ae3_flow = AE_FO_flow(AE['AE3 POWER']) * 15 * 60
ae4_flow = AE_FO_flow(AE['AE4 POWER']) * 15 * 60


# In[26]:

# Generate sums for each month, total in FO consumption

tot_ME_month = [0]
tot_AE_month = [0]

for i in range(12):
    tot_ME_month.append(sum(
                    me1_flow['2014-'+str(i+1)]+
                    me2_flow['2014-'+str(i+1)]+
                    me3_flow['2014-'+str(i+1)]+
                    me4_flow['2014-'+str(i+1)]))

for i in range(12):
    tot_AE_month.append(sum(
                    ae1_flow['2014-'+str(i+1)]+
                    ae2_flow['2014-'+str(i+1)]+
                    ae4_flow['2014-'+str(i+1)]))
    
    #ae3_flow['2014-'+str(i+1)]+


# In[27]:

tot_ME_month = np.array(tot_ME_month)
list(tot_ME_month / 1000) # Present the values in tonnes


# In[28]:

tot_AE_month = np.array(tot_AE_month)
list(tot_AE_month / 1000) # tonnes


# In[18]:

total = tot_AE_month + tot_ME_month
list(total / 1000) # total in tonnes for each month


# In[11]:

plot(total)


# In[12]:

x = np.array(range(101))
y1 = AE_FO_flow((x*27.80)) # The function is based on 2780 kW as 100 % load, therefore 2780 / 100.
y2 = ME_FO_flow(x,500)
plot(x,y1)
plot(x,y2)


# In[103]:

exh_temp = pd.DataFrame[{'AE1' : AE['AE1 EXH CA OUTET 1'].values,
                        'AE2' : AE['AE2 EXH CA OUTET 1'].values}]


# In[102]:

AE['AE1 EXH CA OUTET 1'].values


# In[ ]:



