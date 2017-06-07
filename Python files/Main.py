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
path_files = 'Python files' + os.sep
sys.path.append(path_files)
import pandas as pd
import input
import plotting as plot


filenames = input.filenames() # Note: this is just a test


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
dataset_processed = ea.eYergyAnalzsis(dataset_processed, CONSTANTS)


#%%
######################################
## EXERGY ANALYSIS		##
######################################

# Responsible: FB



## PLAYGROUND ##
#%%
