import pandas as pd
import numpy as np
from helpers import d2df

def enginesCheck(processed, CONSTANTS):
    # This function checks that all relative values are consistent
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    print("Started consistency check...")
    text_file.write("\n *** CONSISTENTCY CHECK FOR ENGINES *** \n")
    for type in ["MainEngines", "AuxEngines"]:
        for name in CONSTANTS["General"]["NAMES"][type]:
            on = processed[name+":"+"on"]
            tot = sum(on)
                # Compressor outlet temperature must be higher than compressor inlet temperature
            temp = sum(processed[d2df(name,"Comp","Air_out","T")][on] > processed[d2df(name,"Comp","Air_in","T")][on]) / tot * 100
            text_file.write(name + " Compressor temperatures are consistent for " + str(temp) + " % of the datapoints \n")
                # Exhaust temperature should be higher closer to the engine exhaust valve
            temp = sum(processed[d2df(name,"Cyl","EG_out","T")][on] > processed[d2df(name,"Turbine","Mix_in","T")][on]) / tot * 100
            text_file.write(name + " Exhaust temperatures (Cyl->TC are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name,"Turbine","Mix_in","T")][on] > processed[d2df(name,"Turbine","Mix_out","T")][on]) / tot * 100
            text_file.write(name + " Turbine temperatures are consistent for " + str(temp) + " % of the datapoints \n")
                # Checking the consistency of the LOC temperatures
            temp = sum(processed[d2df(name,"LOC","LubOil_in","T")][on] > processed[d2df(name,"LOC","LubOil_out","T")][on]) / tot * 100
            text_file.write(name + " LOC temperatures (oil side) are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name,"LOC","LTWater_out","T")][on] > processed[d2df(name,"LOC","LTWater_in","T")][on]) / tot * 100
            text_file.write(name + " LOC temperatures (LT water side) are consistent for " + str(temp) + " % of the datapoints \n")
                # Checking the consistency of the CAC_LT temperatures
            temp = sum(processed[d2df(name,"CAC_LT","Air_in","T")][on] > processed[d2df(name,"CAC_LT","Air_out","T")][on]) / tot * 100
            text_file.write(name + " CAC_LT temperatures (air side) are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name,"CAC_LT","LTWater_out","T")][on] > processed[d2df(name,"CAC_LT","LTWater_in","T")][on]) / tot * 100
            text_file.write(name + " CAC_LT temperatures (LT water side) are consistent for " + str(temp) + " % of the datapoints \n")
            # Checking the consistency of the CAC_HT temperatures
            temp = sum(processed[d2df(name, "CAC_HT", "Air_in", "T")][on] >= processed[d2df(name, "CAC_HT", "Air_out", "T")][on]) / tot * 100
            text_file.write(name + " CAC_HT temperatures (air side) are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name, "CAC_HT", "HTWater_out", "T")][on] >= processed[d2df(name, "CAC_HT", "HTWater_in", "T")][on]) / tot * 100
            text_file.write(name + " CAC_HT temperatures (HT water side) are consistent for " + str(temp) + " % of the datapoints \n")
    text_file.close()
    print("...done!")


def missingValues(processed, dict_structure, CONSTANTS):
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    text_file.write("\n *** LIST OF MISSING VALUES *** \n")
    print("Started looking for missing values...")
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                for property in dict_structure["systems"][system]["units"][unit]["flows"][flow]["properties"]:
                    if property not in {"h", "b", "Edot", "Bdot"}:
                        if processed[d2df(system,unit,flow,property)].isnull().sum() == len(processed[system + ":" + "on"]):
                            text_file.write("The field {}:{}:{}:{} is still empty \n".format(system,unit,flow,property))
    text_file.close()
    print("...done!")


def massBalance(processed, dict_structure, CONSTANTS):
    # This function checks that the mass balance is respected
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    text_file.write("\n *** CHECKING THE MASS BALANCE *** \n")
    print("Started checking mass balances...")
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            balance = pd.Series()
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] in {"CPF" , "IPF"}:
                    balance = balance + processed[d2df(system,unit,flow,"mdot")]
            balance_occ = np.sum(balance[processed[system+":on"]] != 0) / len(balance[processed[system+":on"]]) * 100
            balance_ave = np.sum(balance[processed[system+":on"]]) / len(balance[processed[system+":on"]])
            text_file.write("Mass balance for {}_{} unit is not respected {}% of the times, with {} average error \n".format(system, unit, str(balance_occ), str(balance_ave)))
    print("...done!")
    text_file.close()


def energyBalance(processed, dict_structure, CONSTANTS):
    # This function checks that the mass balance is respected
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    text_file.write("\n *** CHECKING THE ENERGY BALANCE *** \n")
    print("Started checking the energy balances...")
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            balance = pd.Series()
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                balance = balance + processed[d2df(system,unit,flow,"Edot")]
            balance_occ = np.sum(balance[processed[system+":on"]] != 0) / len(balance[processed[system+":on"]]) * 100
            balance_ave = np.sum(balance[processed[system+":on"]]) / len(balance[processed[system+":on"]])
            text_file.write("Mass balance for {}_{} unit is not respected {}% of the times, with {} average error".format(system, unit, str(balance_occ), str(balance_ave)))
    print("...done!")
    text_file.close()