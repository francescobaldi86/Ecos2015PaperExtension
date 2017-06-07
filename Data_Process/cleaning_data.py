import pandas as pd
import numpy as np
import os
import datetime

project_path = os.path.realpath('.')
database_path = project_path + os.sep + 'Database' + os.sep
log_path = project_path + os.sep + 'Log' + os.sep
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

# Function for checking if the value is a NaN or not.
# Needed to be sure that the script works if not all fields
# in the excel-file are filled.

def isNaN(num):
    return num != num

# Duplicate the original dataset so it can be used for comparison
df_filtered = df.copy()

run_log = list()

for i in list(index_selected.index):
    # In the headers_dict file there are values and relations stored for
    # each data-point. Most of them does not contain anything but those that
    # are needs to be put back in to the data-set.

    name = headers_dict.loc[i]['ORIGINAL_HEADER']

    # If a relation is used the following code is executed...

    if ( headers_dict.loc[i]['REL'] == "<") | ( headers_dict.loc[i]['REL'] == ">" ) & \
    ( (isinstance(headers_dict.loc[i]['VALUE'],float)) | (isinstance(headers_dict.loc[i]['VALUE'],int)) ) & \
    ( (isinstance(headers_dict.loc[i]['HIGH_BOUND'],float)) | (isinstance(headers_dict.loc[i]['HIGH_BOUND'],int)) ) & \
    ( (isinstance(headers_dict.loc[i]['LOW_BOUND'],float)) | (isinstance(headers_dict.loc[i]['LOW_BOUND'],int)) ) & \
    (isNaN(headers_dict.loc[i]['VAR']) == False):

        value = headers_dict.loc[i]['VALUE']
        rel = headers_dict.loc[i]['REL']
        var = headers_dict.loc[i]['VAR']
        high_bound = headers_dict.loc[i]['HIGH_BOUND']
        low_bound =headers_dict.loc[i]['LOW_BOUND']

        # For debugging ....

        exec("df_filtered[name][(df_filtered[hd[var]] "+ rel +" value) & (df_filtered[name] > high_bound)] = np.nan")
        exec("df_filtered[name][(df_filtered[hd[var]] "+ rel +" value) & (df_filtered[name] < low_bound)] = np.nan")

        values_removed = len(df_filtered[name])-df_filtered[name].count()
        df_filtered[name] = df_filtered[name].interpolate()
        diff_abs = abs( (df_filtered[name] - df[name]) ).sum()

        a = ('Index:' + str(i) +\
        ' ;Name: '+ hd[name]+\
        ' ;Relation: '+ rel + \
        ' ;Value: '+ str(value) +\
        ' ;Var: '+ var +\
        ' ;High: '+ str(high_bound) +\
        ' ;Low: '+ str(low_bound) +\
        ' ;Values filtered: '+ str(values_removed) +\
        ' ;Absolute sum: '+ str(diff_abs) +\
        ' ;Average/point: '+ str(diff_abs/values_removed))

        run_log.append(a)



# If no relation is used...
    if ( (isinstance(headers_dict.loc[i]['HIGH_BOUND'],float)) | (isinstance(headers_dict.loc[i]['HIGH_BOUND'],int)) ) & \
        ( (isinstance(headers_dict.loc[i]['LOW_BOUND'],float)) | (isinstance(headers_dict.loc[i]['LOW_BOUND'],int)) ) & \
        (isNaN(headers_dict.loc[i]['HIGH_BOUND']) == False) & \
        (isNaN(headers_dict.loc[i]['LOW_BOUND']) == False) & \
        (isNaN(headers_dict.loc[i]['VAR']) == True):

        high_bound = headers_dict.loc[i]['HIGH_BOUND']
        low_bound = headers_dict.loc[i]['LOW_BOUND']

        df_filtered[name][df_filtered[name] > high_bound] = np.nan
        df_filtered[name][df_filtered[name] < low_bound] = np.nan

        values_removed = len(df_filtered[name])-df_filtered[name].count()
        df_filtered[name] = df_filtered[name].interpolate()
        diff_abs = abs( (df_filtered[name] - df[name]) ).sum()

        a = ('Index:' + str(i) +\
        ' ;Name: '+ hd[name]+\
        ' ;Relation: NONE'+\
        ' ;Value: NONE' +\
        ' ;Var: NONE' +\
        ' ;High: '+ str(high_bound) +\
        ' ;Low: '+ str(low_bound) +\
        ' ;Values filtered: '+ str(values_removed) +\
        ' ;Absolute sum: '+ str(diff_abs) +\
        ' ;Average/point: '+ str(diff_abs/values_removed))

        run_log.append(a)



    #df_filtered[name] = df_filtered[name].interpolate()




log_file = open(log_path + 'log_file.txt','w')

log_file.write(str(datetime.datetime.now()) + '\n')
for item in run_log:
    log_file.write('\n'+item)
log_file.close()

df_filtered.to_hdf(database_path + 'filtered_df.h5','table',complevel=9,complib='blosc')

#%%

#df_filtered = df_filtered.interpolate()

df_filtered[hd['AE1-CAC_AIR_P_OUT']].count()-df_filtered[hd['AE1-CAC_AIR_P_OUT']].count()


name=hd['SHIP_SPEED_KNOT_']
name

df[name]

df_filtered[name][df_filtered[name]==0]

df_filtered[name][df_filtered[name]>-1e-6]

df_filtered[hd['AE1-CAC_AIR_P_OUT']] = 0
len(df_filtered[hd['AE1-CAC_AIR_P_OUT']])

len(df[hd['AE1-CAC_AIR_P_OUT']])



df[hd['SHIP_SPEED_KNOT_']][df[hd['SHIP_SPEED_KNOT_']]>0]



[df[hd['SHIP_SPEED_KNOT_']<0]]

#%%
#################################################################
#################################################################
#################################################################


# Testing if everything works

df = pd.read_hdf(database_path + 'selected_df.h5','table')

df[name][(df[hd[var]] > value) & (df[name] > 3.7)]




df[name].count()-len(df[name])

# Here we have some datapoints which are high

df[name]['2014-07-10 18' : '2014-07-10 23']

# I will put in NaN in those places which are higher than 3.4

df[name][(df[hd[var]] > value) & (df[name] > 3.4)] = np.nan

# Now it looks a bit different with NaN for everything above 3.4

df[name]['2014-07-10 18' : '2014-07-10 23']

# Do an interpolate which should fill in the NaN.
df[name] = df[name].interpolate()
df[name]['2014-07-10 18' : '2014-07-10 23']


# Load the original dataset and compare with the interpolated one for the same time period

df2 = pd.read_hdf(database_path + 'selected_df.h5','table')
df[name]['2014-07-10 18' : '2014-07-10 23']-df2[name]['2014-07-10 18' : '2014-07-10 23']

# Tot total difference is:

(df[name]-df2[name]).sum()





# Testing if it works ...
# Loading the original DF again for comparison..








df_original = pd.read_hdf(database_path + 'selected_df.h5','table')
