
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np

#Import data into Pandas Data Frame
#The first column is data type, index col is time series Excel.
# 15 min interval data.
ME = pd.read_excel('ME.xlsx',index_col=0)
AE = pd.read_excel('AE.xlsx',index_col=0)
FO = pd.read_excel('FO.xlsx',index_col=0)
Mass_flow = pd.read_excel('Mass_flowmeters.xlsx',index_col=0)


# In[2]:

list(ME) # List all the variables in the Data Frame Main Engines.


# In[12]:

get_ipython().magic('pylab')


# In[3]:

list(AE) # List AE Vars


# In[4]:

list(FO) # List vars in FO, fuel oil and tanks.


# In[5]:

list(Mass_flow)


# In[6]:

# Define funcion for engine load. Fuel rack pos. i percent * 100.

#def ME_Load(fuel_rack, rpm):
#    load = (fuel_rack / 100.) * (rpm / 500.)
#    return load

# Define function for Fuel Oil. The constant 0.323129514 is derived from
# linear regression of the mean values from all engines test protocol data.
# Intercept is set to zero, R^2 = 0.9938. Max engine RPM = 500.

def ME_FO_flow(load, rpm):
    FRP = 0.7807 * (load / 100.) + 0.2129
    ME_FO_flow = 0.04445 * FRP * rpm / 60 * 1.1262  # FO_flow in kg/s
    return ME_FO_flow

#def ME_FO_flow(fuel_rack, rpm):
#    ME_FO_flow = (fuel_rack / 100.) * (rpm / 500.) * 0.323129514
#    return ME_FO_flow

# For the Auxiliary Engines. Value in kg/s
# linear regression of the mean values from all engines test protocol data. * 1.268029 is the correction factor when validated
# against the mass flow meters. Max electrial Power is 2680 kW.
# Intercept is set to zero, R^2 = 0.9949.
 
def AE_FO_flow(electrical_power):
    AE_FO_flow = (electrical_power / 2680.) * 0.142732820019249
    return AE_FO_flow


# In[7]:

# Calculate the flows from all ME and AE. Data is in Pandas Time Series.
# The data is in 15 minute interval, and 15 min * 60 s is for integrating from the average of kg/s to kg for a 15 min interval.

me1_flow = ME_FO_flow(ME['ME1 FUEL RACK POSIT'],ME['ME1 ENGINE SPEED']) * 15 * 60
me2_flow = ME_FO_flow(ME['ME2 FUEL RACK POSIT'],ME['ME2 ENGINE SPEED']) * 15 * 60 
me3_flow = ME_FO_flow(ME['ME3 FUEL RACK POSIT'],ME['ME3 ENGINE SPEED']) * 15 * 60
me4_flow = ME_FO_flow(ME['ME4 FUEL RACK POSIT'],ME['ME4 ENGINE SPEED']) * 15 * 60
ae1_flow = AE_FO_flow(AE['AE1 POWER']) * 15 * 60
ae2_flow = AE_FO_flow(AE['AE2 POWER']) * 15 * 60
ae3_flow = AE_FO_flow(AE['AE3 POWER']) * 15 * 60
ae4_flow = AE_FO_flow(AE['AE4 POWER']) * 15 * 60

# Calculate running time of each engine, in fraction of other engine. First
# for 1 and 3 engines.


# In[13]:

# Compare the model with the mass flow meters for each day. After each day
# a new constant is calculated and each individual engine is accounting
# for the fault in percentage of the total coefficient. In this way the
# coefficients gets a higher fraction for the engine that is most in use.


c = 0
eng1_3 = []
eng2_4 = []
me1_const = [1] # Coefficients for each individual engine.
me2_const = [1]
me3_const = [1]
me4_const = [1]
ae1_const = [1]
ae2_const = [1]
ae3_const = [1]
ae4_const = [1]

months = [2,3,4,5,6,7,8,9,10] # January is exluded, lack of data.
days = range(1,29)

for m in months:
    for d in days:
        
        eng1_3.insert(c,(
                    sum(
                    me1_flow['2014-'+str(m)+'-'+str(d)] * me1_const[c] +
                    me3_flow['2014-'+str(m)+'-'+str(d)] * me3_const[c] +
                    ae1_flow['2014-'+str(m)+'-'+str(d)] * ae1_const[c])
                    #ae3_flow['2014-'+str(m)+'-'+str(d)] * ae3_const[c])
                    /1000)/
                    Mass_flow.loc['2014-'+str(m)+'-'+str(d),['FO_day_engine_1_3']].values)
        
        eng2_4.insert(c,(
                    sum(
                    me2_flow['2014-'+str(m)+'-'+str(d)] * me2_const[c] +
                    me4_flow['2014-'+str(m)+'-'+str(d)] * me4_const[c] +
                    ae2_flow['2014-'+str(m)+'-'+str(d)] * ae2_const[c] +
                    ae4_flow['2014-'+str(m)+'-'+str(d)] * ae4_const[c])
                    /1000)/
                    Mass_flow.loc['2014-'+str(m)+'-'+str(d),['FO_day_engine_2_4']].values)
        
        eng1_3_const = 1 / eng1_3[c]
        eng2_4_const = 1 / eng2_4[c]
        
        #me1_const.insert(c+1,1+(eng1_3_const - me1_const[c]) * me1_frac['2014-'+str(m)+'-'+str(d)])
        #me2_const.insert(c+1,1+(eng2_4_const - me2_const[c]) * me2_frac['2014-'+str(m)+'-'+str(d)])
        #me3_const.insert(c+1,1+(eng1_3_const - me3_const[c]) * me3_frac['2014-'+str(m)+'-'+str(d)])
        #me4_const.insert(c+1,1+(eng2_4_const - me4_const[c]) * me4_frac['2014-'+str(m)+'-'+str(d)])
        #ae1_const.insert(c+1,1+(eng1_3_const - ae1_const[c]) * ae1_frac['2014-'+str(m)+'-'+str(d)])
        #ae2_const.insert(c+1,1+(eng2_4_const - ae2_const[c]) * ae2_frac['2014-'+str(m)+'-'+str(d)])
        #ae3_const.insert(c+1,1+(eng1_3_const - ae3_const[c]) * ae3_frac['2014-'+str(m)+'-'+str(d)])
        #ae4_const.insert(c+1,1+(eng2_4_const - ae4_const[c]) * ae4_frac['2014-'+str(m)+'-'+str(d)])
        c = c + 1
        
        


# In[14]:

b = 50
pyplot.hist(me1_const,bins=b)


# In[ ]:

me1_const = sum(me1_const)/len(me1_const)
me2_const = sum(me2_const)/len(me2_const)
me3_const = sum(me3_const)/len(me3_const)
me4_const = sum(me4_const)/len(me4_const)
ae1_const = sum(ae1_const)/len(ae1_const)
ae2_const = sum(ae2_const)/len(ae2_const)
ae3_const = sum(ae3_const)/len(ae3_const)
ae4_const = sum(ae4_const)/len(ae4_const)
print me1_const, me2_const, me3_const, me4_const
print ae1_const, ae2_const, ae3_const, ae4_const


# In[ ]:

# Generate sums for each month, total in FO consumption

tot_ME_month = []
tot_AE_month = []
tot_measured_1_3 = []
tot_measured_2_4 = []

for i in months:
    tot_ME_month.append(sum(
                    me1_flow['2014-'+str(i)] * me1_const+
                    me2_flow['2014-'+str(i)] * me2_const+
                    me3_flow['2014-'+str(i)] * me3_const+
                    me4_flow['2014-'+str(i)] * me4_const))
    tot_AE_month.append(sum(
                    ae1_flow['2014-'+str(i+1)] * ae1_const+
                    ae2_flow['2014-'+str(i+1)] * ae2_const+
                    ae4_flow['2014-'+str(i+1)] * ae4_const))
    tot_measured_1_3.append(sum(
                    Mass_flow.loc['2014-'+str(i),['FO_day_engine_1_3']].values))
    tot_measured_2_4.append(sum(
                    Mass_flow.loc['2014-'+str(i),['FO_day_engine_2_4']].values))

    #ae3_flow['2014-'+str(i+1)]+


# In[ ]:

tot_ME_month = np.array(tot_ME_month)
tot_AE_month = np.array(tot_AE_month)
tot_measured_1_3 = np.array(tot_measured_1_3)
tot_measured_2_4 = np.array(tot_measured_2_4)
list(tot_ME_month / 1000) # Present the values in tonnes


# In[ ]:

tot_AE_month = np.array(tot_AE_month)
list(tot_AE_month / 1000) # tonnes


# In[ ]:

total = tot_AE_month + tot_ME_month
list(total / 1000) # total in tonnes for each month


# In[ ]:

list((tot_ME_month/1000 + tot_AE_month/1000) / (tot_measured_1_3 + tot_measured_2_4))


# In[ ]:

coeff = sum((tot_ME_month/1000 + tot_AE_month/1000) / (tot_measured_1_3 + tot_measured_2_4)) / len(tot_AE_month)
print coeff
print 1/coeff


# In[ ]:

plot(total)


# In[ ]:




# In[88]:

x = np.array(range(101))
y1 = AE_FO_flow((x*27.80)) # The function is based on 2780 kW as 100 % load, therefore 2780 / 100.
y2 = ME_FO_flow(x,500)
plot(x,y1)
plot(x,y2)


# In[89]:

exh_temp = pd.DataFrame[{'AE1' : AE['AE1 EXH CA OUTET 1'].values,
                        'AE2' : AE['AE2 EXH CA OUTET 1'].values}]


# In[ ]:

AE['AE1 EXH CA OUTET 1'].values


# In[ ]:



