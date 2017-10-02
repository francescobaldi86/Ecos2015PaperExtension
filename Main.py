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


do_processed_data_preparation = "no"
do_data_processing = "yes"




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
import fillerfunctions as ff
import consistencycheck as cc
import preprocessingAE as ppa
import preprocessingME as ppm
import preprocessingO as ppo
import energyanalysis as ea
import auxiliaryDemand as aux
import coolingsystems as cs
from helpers import d2df
import export as ex

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
processed = kk.seasons(dataset_raw, processed, CONSTANTS)
erase_old_file = "yes"
try:
    processed_temp = pd.read_hdf(CONSTANTS["filenames"]["dataset_output"], 'processed')
except FileNotFoundError:
    if do_data_processing == "no":
        do_data_processing = "yes"
    erase_old_file = "no"

# Running the code
if do_data_processing == "no":
    # If the file exists AND we want to use it, we just assign the "processed" variable to it
    processed = processed_temp
elif do_data_processing == "yes":
    # Otherwise, we simply do as if it didn't exist
    if erase_old_file != "no":
        os.remove(CONSTANTS["filenames"]["dataset_output"])
    # First updating the "CONSTANTS" dictionary with the some additional information
    processed = input.assumptions(dataset_raw, processed, CONSTANTS, header_names)
    # Updating the fields of the MainEngines and the auxiliary engines
    processed = ppm.mainEngineProcessing(dataset_raw, processed, dict_structure, CONSTANTS, header_names)
    processed = ppa.auxEngineProcessing(dataset_raw, processed, dict_structure, CONSTANTS, header_names)
    processed = ff.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-1")
    # Calculating the auxiliary power demands: heating and electric power
    processed = aux.auxPowerAnalysis(processed, CONSTANTS, dict_structure)
    processed = ff.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-2")
    processed = ff.systemFill(processed, dict_structure, CONSTANTS, "Demands", "Demands-1")
    # Calculating the central cooling systems
    processed = cs.centralCoolingSystems(processed, CONSTANTS)
    processed = ff.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-3")
    # Assigning defined values to all flows for engines off
    processed = ea.energyAnalysisLauncher(processed, dict_structure, CONSTANTS)
    # Re-doing the calculation of the connected points
    processed = ff.systemFill(processed, dict_structure, CONSTANTS, "Other", "Other-4")
    processed = ff.systemFill(processed, dict_structure, CONSTANTS, "Other", "Demands-2")

    # Saving the processed data
    processed.to_hdf(CONSTANTS["filenames"]["dataset_output"], "processed", format='fixed', mode='w')


######################################
## RESULTS CHECK                	##
######################################
cc.systemCheck(processed, CONSTANTS, dict_structure, dataset_raw)
######################################
## EXPORT EFFICIENCIES                	##
######################################
ex.exportEfficiecies(processed, CONSTANTS, dict_structure)

#%%
######################################
## PLOTTING	##
######################################

plot.predefinedPlots(processed, dataset_raw, CONSTANTS, dict_structure, ["TimeSeries:Heat_vs_time"])
# plot.plotMain("prompt", dict_structure, processed)







## PLAYGROUND ##
#%%

import matplotlib
matplotlib.style.use('ggplot')


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