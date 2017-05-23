
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





######################################
## INPUT			##
######################################

# Loading appropriate modules
import pandas as pd
import input

filenames = input.filenames() # Note: this is just a test






######################################
## DATA READING			##
######################################

# Responsible: FA

import datareading as dr

data_path = 'C:\\Users\\FrancescoBaldi\\Dropbox\\Energy and exergy analysis of a cruise ship - Journal Extension\\'
dataset_raw = pd.read_hdf(data_path + 'birka_all_data.h5' ,'table')

#N_POINTS = 319* 4 * 24
#temp = CONSTANTS.monthLimits(N_POINTS)
#MONTH_LIMIT_IDX = temp[0]
#DAY_LIMIT_IDX = temp[1]
#dataset_raw = dr.keysRenaming(dataset_raw)

######################################
## DATA CLEANING			##
######################################

# Responsible: FA


######################################
## DATA PROCESSING		##
######################################
# Responsible: FB

# Preparing the data structures
import unitstructures as us
import constants as kk

# Setting the important constants
CONSTANTS = kk.constantsSetting()

dataset_processed = us.flowStructure()  # Here we initiate the structure fields
dataset_processed = us.flowPreparation(dataset_processed,dataset_raw.index)  # Here we create the appropriate empty data series for each field
dataset_status = us.generalStatus() # Here we simply initiate the "status" structure

# Running the pre-processing required for filling in the data structures:
import preprocessing as pp
# First updating the "CONSTANTS" dictionary with the some additional information
CONSTANTS = pp.assumptions(dataset_raw,CONSTANTS)
# Updating the fields of the MainEngines and the auxiliary engines
(dataset_processed, dataset_status) = pp.mainEngineProcessing(dataset_raw, dataset_processed, CONSTANTS, dataset_status)
(dataset_processed, dataset_status) = pp.auxEngineProcessing(dataset_raw, dataset_processed, CONSTANTS, dataset_status)



######################################
## EXPLORATORY DATA ANALYSIS	##
######################################

# Responsible: FB



######################################
## ENERGY ANALYSIS		##
######################################

# Responsible: FB



######################################
## EXERGY ANALYSIS		##
######################################

# Responsible: FB
