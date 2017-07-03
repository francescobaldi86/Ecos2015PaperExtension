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


do_processed_data_preparation = "yes"
do_main_engines_analysis = "yes"
do_aux_engines_analysis = "yes"
do_energy_analysis = "yes"




#%%
######################################
## INPUT			##
######################################

# Loading appropriate modules
import sys
import os
import pandas as pd
import matplotlib.pylab as plt
import numpy as np
project_path = os.getcwd()
path_files = project_path + os.sep + 'Python files' + os.sep
sys.path.append(path_files)
# Loading local modules
import input
import plotting as plot
import datareading as dr
import unitstructures as us
import constants as kk
import consistencycheck as cc
import preprocessingAE as ppa
import preprocessingME as ppm
import preprocessingO as ppo
import energyanalysis as ea
import auxiliaryDemand as aux
import coolingsystems as cs

#%%
######################################
## DATA READING			##
######################################
# Responsible: FA
# Setting the filenames
filenames = input.filenames(project_path) # Note: this is just a test
# Reading the input data (measurements)
dataset_raw = pd.read_hdf(filenames["dataset_raw"] ,'table')
# load the dictionary with the header names
header_names = dr.keysRenaming(dataset_raw, filenames["headers_translate"])


######################################
## DATA PROCESSING		##
######################################
# Responsible: FB
#%%
# Setting the important constants
CONSTANTS = kk.constantsSetting()
CONSTANTS["filenames"] = filenames
(dict_structure, processed) = us.structurePreparation(CONSTANTS, dataset_raw.index, CONSTANTS["filenames"]["dataset_output_empty"], do_processed_data_preparation)

# First updating the "CONSTANTS" dictionary with the some additional information
processed = ppo.assumptions(dataset_raw, processed, CONSTANTS, header_names)
# Updating the fields of the MainEngines and the auxiliary engines
if do_main_engines_analysis == "yes":
    processed = ppm.mainEngineProcessing(dataset_raw, processed, dict_structure, CONSTANTS, header_names)
if do_aux_engines_analysis == "yes":
    processed = ppa.auxEngineProcessing(dataset_raw, processed, dict_structure, CONSTANTS, header_names)
processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-1")
# Calculating the auxiliary power demands: heating and electric power
processed = aux.auxPowerAnalysis(processed, CONSTANTS, dict_structure)
# Calculating the central cooling systems
processed = cs.centralCoolingSystems(processed, CONSTANTS)
# Filling in
processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-2")
processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-3")
# Assigning defined values to all flows for engines off
processed = ea.energyAnalysisLauncher(processed, dict_structure, CONSTANTS, do_energy_analysis)
# Re-doing the calculation of the connected points
processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-4")
processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-5")

######################################
## RESULTS CHECK                	##
######################################
cc.enginesCheck(processed, CONSTANTS)
cc.missingValues(processed, dict_structure, CONSTANTS)
cc.massBalance(processed, dict_structure, CONSTANTS)
cc.energyBalance(processed, dict_structure, CONSTANTS)
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
# dataset_processed = ea.eYergyAnalzsis(dataset_processed, CONSTANTS)


#%%
######################################
## EXERGY ANALYSIS		##
######################################

# Responsible: FB



## PLAYGROUND ##
#%%

import matplotlib
matplotlib.style.use('ggplot')
from helpers import d2df

#%%

k_1_3 = 927.27
k_2_4 = 903.65

ME1_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]
ME2_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]
ME3_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]
ME4_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]
AE1_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]
AE2_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]
AE3_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]
AE4_FO = processed[d2df('ME1','Cyl','FuelPh_in','mdot')]



FO1_flow = dataset_raw['FO BOOST 1 CONSUMPT:6165:m3/h:Average:900']/3.600*k_1_3
FO2_flow = dataset_raw['FO BOOST 2 CONSUMPT:6166:m3/h:Average:900']/3.600*k_2_4


tot_ME13 = (ME1_FO + ME3_FO + AE1_FO) * 1000
tot_ME24 = (ME2_FO + ME4_FO + AE2_FO + AE4_FO) * 1000

tot_ME13_sel = tot_ME13[processed['AE1'+":"+"on"] == 0]
FO1_flow_sel = FO1_flow[processed['AE1'+":"+"on"] == 0]
#tot_ME13_sel = tot_ME13[(dataset_status['AE1']['OnOff'] == 0)]
#FO1_flow_sel = FO1_flow[(dataset_status['AE1']['OnOff'] == 0)]
tot_ME13_sel.plot()
FO1_flow_sel.plot(alpha=0.4)

#tot_ME13.plot()
#FO1_flow.plot(alpha=0.4)

tot_ME24.plot()
FO2_flow.plot(alpha=0.4)

import matplotlib.pylab as plt
plt.figure()
plt.plot(tot_ME24, label="Calculated consumption [kg/s]")
plt.plot(FO2_flow, label="Measured consumption [kg/s]")
plt.legend()

plt.figure()
plt.plot(tot_ME13_sel, label="Calculated consumption [kg/s]")
plt.plot(FO1_flow_sel, label="Measured consumption [kg/s]")
plt.legend()

aaa = "end"