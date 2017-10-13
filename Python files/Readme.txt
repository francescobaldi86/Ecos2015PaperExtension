This file should serve as documentation for the functioning of the Python program used for the data analysis of the MS Birka Energy-Exergy analysis project. 

The readme file is composed of the following sections:

1 - General structure of the code

2 - How to run it

3 - How to get useful things out of it



1 - General structure of the code

The code is based on the execution in sequence of a number of sub-routines:
1. Loading the main filenames (Line 71)
2. Importing the raw datafile (Line 73)
3. Creating the "header_names" structure for translation from the complex original names in the raw datafile to "usable" names (Line 75)
4. Importing a number of useful constants and information in the "CONSTANTS" python dictionary (Line 84)
5. Creating the Pandas dataframe. This basically pre-allocates the memory. The empty dataset is saved at the end and this step is skipped if no changes in the component names and flows are made (Line 86)
--- CHECK: If the "do_data_processing" variable assigned in the beginning of the code is "no", all following points are skipped
6. Providing some assumptions. (Line 105)
7. Main engine pre-processing (Line 107). This includes:
	7.1. Reading available measurements
	7.2. Determining the engine status (on/off)
	7.3. Calculating cooling mass flows, based on pressure and on pump equations
	7.4. Calculating the fuel flow
	7.5. Calculating the engine power
	7.6. Calculating the engine load
	7.7. Calculating the engine air-exhaust flows
	7.8. Calculating engine heat losses 
8. Auxiliary engine pre-processing (Line 108). Structure similar to the main engine processing. 

--- NOTE: In several parts of the code you will note calls to these "systemFill" subroutine. What it does is simply to use available information to fill in the dataframe. This is based on i. flow connections (e.g. the air flow outlet from the compressor is the same flow as the charge air cooler inlet), ii. mass balances, and iii. isothermal components (e.g. splitters). The information about connections, balances and etc. are provided to the system in the "unitstructures" subroutine

9. Auxiliary power analysis (Line 111). It includes the calculation of the:
	9.1. Total electric power demand
	9.2. Propulsion power demand
	9.3. Thrusters demand
	9.4. Operational mode (High speed sailing, Low speed sailing, Maneuvering, Port/stay)
	9.5. HVAC compressors electric power demand
	9.6. Heating demand
	9.7. Heating generation from the HTHR systems
	9.8. Auxiliary boilers
10. Central cooling systems (Line 115) and sea water coolers (Line 117) processing
11. Energy analysis (Line 119). Based on all the information available from before, it calculates
	- All specific enthalpies
	- All specific entropies
	- All specific exergies
	- All energy flows
	- All exergy flows
	- All energy efficiencies
	- All exergy-based performance indicators (see TV's exergy analysis description in the manuscript)
12. Saves the main dataframe to a .hdf file (Line 124)
13. Performs a number of system checks (Line 126)
	13.1. Main and auxiliary engines for consistency
	13.2. HTHR for consistency
	13.3. Steam systems for consistency
	13.4. Lists missing values
	13.5. Calculates mass balance for all components
	13.6. Calculates energy balance for all components
14. Saving aggregated energy and exergy efficiencies to a .csv output (Line 128)






2 - How to run it

To run the code, you simply need to run the "Main.py" file. 
If you just want to look at / elaborate the results previously calculated, simply keep the "do_data_processing" to "no" (Line 27). 
Otherwise, if you make changes somewhere in the code in such a way that the results are expected to change, change it to "yes".
Please always leave the "do_processed_data_preparation" to "yes". 




3 - How to get useful things out of it

If you want to play with the output results, you have two main ways:
- Using a Python IDE that supports debugging mode (such as PyCharm)
- Running the Main.py, then writing your own script where you load the results and you play with them

Then, there are several ways to get some info out:
- The code automatically generates tables with some aggregate figures. Check the folder "results". 
- In the "plotting" module there are some info on how to plot what you need. For some predefined plot, check the "predefinedPlots" function. You call it by doing:
		plot.predefinedPlots(processed, dataset_raw, CONSTANTS, dict_structure, "NameOfThePredefinedPlot")
		example: plot.predefinedPlots(processed, dataset_raw, CONSTANTS, dict_structure, "Pie:DemandFull")
- If you take whatever field of the output dataframe, you can get quite some useful information by inserting the command:
		processed["fieldName"].describe()
		example: processed["ME1:Cyl:Air_in:T"].describe()
