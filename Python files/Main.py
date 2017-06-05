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
import pandas as pd
import input
import os
import plotting as plot


filenames = input.filenames() # Note: this is just a test



#%%
######################################
## DATA READING			##
######################################

# Responsible: FA

import datareading as dr

project_path = os.path.realpath('..')
translate_filename = project_path + '\\General\\headers_dict.xlsx'

#dataset_raw = pd.read_hdf(project_path + '\\Database\\selected_data_1year_comp.h5' ,'table')
dataset_raw = pd.read_hdf(project_path + '\\Database\\selected_df.h5' ,'table')

header_names = dr.keysRenaming(dataset_raw, translate_filename)
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
