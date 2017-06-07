###########################################################################
#
###########		ENERGY AND EXERGY ANALYSIS OF A CRUISE SHIP		###########
#
###########################################################################

# This is the main script of the project "Energy and Exergy analysis of a cruise ship"

# The main objective of this project is to analyze the energy and exergy flows of the cruise ship "MS Birka", selected as case study.

# The main objective of this library of Python scripts is, therefore;
# - Load the data
# - Appropriately filter and clean the dataset
# - Process data so to generate the variables of interest: in particular, energy and exergy flows
# - Statistically analyze the data so to produce appropriate results

# The main.py script calls other scripts and functions. It is divided in the following sections:
# - INPUT
# - DATA READING
# - DATA CLEANING
# - DATA PROCESSING
# - EXPLORATORY DATA ANALYSIS
# - ENERGY ANALYSIS
# - EXERGY ANALYSIS


input_run = "yes"
datareading_run = "yes"



#%%
######################################
## INPUT			##
######################################

# Loading appropriate modules
import sys
import os
import pandas as pd
project_path = os.getcwd()
path_files = project_path + os.sep + 'Python files' + os.sep
sys.path.append(path_files)

# Loading local modules
import input
import plotting as plot
filenames = input.filenames(project_path) # Note: this is just a test


#%%
######################################
## DATA READING			##
######################################

# Responsible: FA

import datareading as dr



dataset_raw = pd.read_hdf(filenames["dataset_raw"] ,'table')

header_names = dr.keysRenaming(dataset_raw, filenames["headers_translate"])
#%%
######################################
## DATA CLEANING			##
######################################

# Responsible: FA

######################################
## DATA PROCESSING		##
######################################
# Responsible: FB
#%%
# Preparing the data structures
import unitstructures as us
import constants as kk
import consistencycheck as cc

# Setting the important constants
CONSTANTS = kk.constantsSetting()

dataset_processed = us.flowStructure()  # Here we initiate the structure fields
dataset_processed = us.flowPreparation(dataset_processed, dataset_raw.index)  # Here we create the appropriate empty data series for each field
dataset_status = us.generalStatus() # Here we simply initiate the "status" structure

# Running the pre-processing required for filling in the data structures:
import preprocessing as pp
# First updating the "CONSTANTS" dictionary with the some additional information
dataset_processed = pp.assumptions(dataset_raw, dataset_processed, CONSTANTS, header_names)
# Updating the fields of the MainEngines and the auxiliary engines
(dataset_processed, dataset_status) = pp.mainEngineProcessing(dataset_raw, dataset_processed, CONSTANTS, dataset_status, header_names)
(dataset_processed, dataset_status) = pp.auxEngineProcessing(dataset_raw, dataset_processed, CONSTANTS, dataset_status, header_names)

# Checking the consistency of the data
cc.enginesCheck(dataset_processed, dataset_status, CONSTANTS)

# Assigning defined values to all flows for engines off

#%%
######################################
## EXPLORATORY DATA ANALYSIS	##
######################################

# Responsible: FB



#%%
######################################
## ENERGY ANALYSIS		##
######################################

# Responsible: FB
import energyanalysis as ea
# dataset_processed = ea.eYergyAnalzsis(dataset_processed, CONSTANTS)


#%%
######################################
## EXERGY ANALYSIS		##
######################################

# Responsible: FB



## PLAYGROUND ##
#%%

%pylab

#%%

k_1_3 = 927.27
k_2_4 = 903.65

ME1_FO = dataset_processed['ME1']['Cyl']['FuelPh_in']['mdot']
ME2_FO = dataset_processed['ME2']['Cyl']['FuelPh_in']['mdot']
ME3_FO = dataset_processed['ME3']['Cyl']['FuelPh_in']['mdot']
ME4_FO = dataset_processed['ME4']['Cyl']['FuelPh_in']['mdot']
AE1_FO = dataset_processed['AE1']['Cyl']['FuelPh_in']['mdot']
AE2_FO = dataset_processed['AE2']['Cyl']['FuelPh_in']['mdot']
AE3_FO = dataset_processed['AE3']['Cyl']['FuelPh_in']['mdot']
AE4_FO = dataset_processed['AE4']['Cyl']['FuelPh_in']['mdot']


dataset_processed['AE1']['Cyl']['FuelPh_in']['mdot'].describe()


FO1_flow = dataset_raw['FO BOOST 1 CONSUMPT:6165:m3/h:Average:900']/3600*k_1_3
FO2_flow = dataset_raw['FO BOOST 2 CONSUMPT:6166:m3/h:Average:900']/3600*k_2_4


tot_ME13 = ME1_FO + ME3_FO + AE1_FO
tot_ME24 = ME2_FO + ME4_FO + AE2_FO + AE4_FO

#tot_ME13_sel = tot_ME13[(dataset_status['ME1']['OnOff'] == 0) & (dataset_status['ME3']['OnOff'] == 0)]
#FO1_flow_sel = FO1_flow[(dataset_status['ME1']['OnOff'] == 0) & (dataset_status['ME3']['OnOff'] == 0)]
tot_ME13_sel = tot_ME13[(dataset_status['AE1']['OnOff'] == 0)]
FO1_flow_sel = FO1_flow[(dataset_status['AE1']['OnOff'] == 0)]
tot_ME13_sel.plot()
FO1_flow_sel.plot(alpha=0.4)

#tot_ME13.plot()
#FO1_flow.plot(alpha=0.4)

tot_ME24.plot()
FO2_flow.plot(alpha=0.4)
