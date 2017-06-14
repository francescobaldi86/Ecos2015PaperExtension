import pandas as pd
from helpers import d2df

def enginesCheck(processed, CONSTANTS, filenames):
    # This function checks that all relative values are consistent
    text_file = open(filenames["consistency_check_report"], "w")
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
            text_file.write(name + " CAC-LT temperatures (air side) are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name,"CAC_LT","LTWater_out","T")][on] > processed[d2df(name,"LOC","LTWater_in","T")][on]) / tot * 100
            text_file.write(name + " CAC-LT temperatures (LT water side) are consistent for " + str(temp) + " % of the datapoints \n")
    print("...done!")


def missingValues(processed, dict_structure, filenames):
    text_file = open(filenames["consistency_check_report"], "a")
    text_file.write("\n *** LIST OF MISSING VALUES *** \n")
    print("Started looking for missing values...")
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                for property in dict_structure["systems"][system]["units"][unit]["flows"][flow]["properties"]:
                    if processed[d2df(system,unit,flow,property)].isnull().sum() == len(processed[d2df(system,unit,flow,property)]):
                        text_file.write("The field {}_{}_{}_{} is still empty \n".format(system,unit,flow,property))


def massBalance(processed, dict_structure, CONSTANTS):
    # This function checks that the mass balance is respected
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            balance = pd.Series()
            flow_ref = 0
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] in {"CPF" , "IPF"}:
                    balance = balance + processed[d2df(system,unit,flow,"mdot")]
                    flow_ref = max(flow_ref, processed[d2df(system,unit,flow,"mdot")].max())
            if balance.sum() > 0.0001 * len(balance) * flow_ref:
                print("The mass balance is not respected for the {}_{} unit".format(system, unit))


#def energyBalance(processed, dict_structure, CONSTANTS, system, unit):