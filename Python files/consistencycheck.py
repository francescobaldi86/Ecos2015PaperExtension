import pandas as pd

def enginesCheck(data, status, CONSTANTS):
    # This function checks that all relative values are consistent
    print("Started consistency check...")
    for type in ["MainEngines", "AuxEngines"]:
        for name in CONSTANTS["General"]["NAMES"][type]:
            on = status[name]["OnOff"]
            tot = sum(on)
                # Compressor outlet temperature must be higher than compressor inlet temperature
            temp = sum(data[name]["Comp"]["Air_out"]["T"][on] > data[name]["Comp"]["Air_in"]["T"][on]) / tot * 100
            print(name + " Compressor temperatures are consistent for " + str(temp) + " % of the datapoints")
                # Exhaust temperature should be higher closer to the engine exhaust valve
            temp = sum(data[name]["Cyl"]["EG_out"]["T"][on] > data[name]["Turbine"]["Mix_in"]["T"][on]) / tot * 100
            print(name + " Exhaust temperatures (Cyl->TC are consistent for " + str(temp) + " % of the datapoints")
            temp = sum(data[name]["Turbine"]["Mix_in"]["T"][on] > data[name]["Turbine"]["Mix_out"]["T"][on]) / tot * 100
            print(name + " Turbine temperatures are consistent for " + str(temp) + " % of the datapoints")
                # Checking the consistency of the LOC temperatures
            temp = sum(data[name]["LOC"]["LubOil_in"]["T"][on] > data[name]["LOC"]["LubOil_out"]["T"][on]) / tot * 100
            print(name + " LOC temperatures (oil side) are consistent for " + str(temp) + " % of the datapoints")
            temp = sum(data[name]["LOC"]["LTWater_out"]["T"][on] > data[name]["LOC"]["LTWater_in"]["T"][on]) / tot * 100
            print(name + " LOC temperatures (LT water side) are consistent for " + str(temp) + " % of the datapoints")
                # Checking the consistency of the CAC_LT temperatures
            temp = sum(data[name]["CAC_LT"]["Air_in"]["T"][on] > data[name]["CAC_LT"]["Air_out"]["T"][on]) / tot * 100
            print(name + " CAC-LT temperatures (air side) are consistent for " + str(temp) + " % of the datapoints")
            temp = sum(data[name]["CAC_LT"]["LTWater_out"]["T"][on] > data[name]["LOC"]["LTWater_in"]["T"][on]) / tot * 100
            print(name + " CAC-LT temperatures (LT water side) are consistent for " + str(temp) + " % of the datapoints")
    print("...done!")


def missingValues(data):
    print("Started looking for missing values...")
    for system in data:
        for unit in data[system]:
            for flow in data[system][unit]:
                for property in data[system][unit][flow]:
                    if type(data[system][unit][flow][property]) == pd.Series:
                        if data[system][unit][flow][property].isnull().sum() == len(data[system][unit][flow][property]):
                            print("The field {}_{}_{}_{} is still empty".format(system,unit,flow,property))