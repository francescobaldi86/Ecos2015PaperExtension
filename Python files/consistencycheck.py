def enginesCheck(data, status, CONSTANTS):
    # This function checks that all relative values are consistent
    for type in ["MainEngines", "AuxEngines"]:
        for name in CONSTANTS["General"]["NAMES"][type]:
            on = status[name]["OnOff"]
            tot = sum(on)
                # Compressor outlet temperature must be higher than compressor inlet temperature
            temp = sum(data[name]["Comp"]["Air_out"]["T"][on] > data[name]["Comp"]["Air_in"]["T"][on]) / tot * 100
            print(name + " Compressor temperatures are consistent for " + str(temp) + " % of the datapoints")
                # Exhaust temperature should be higher closer to the engine exhaust valve
            temp = sum(data[name]["Cyl"]["EG_out"]["T"][on] > data[name]["TC"]["EG_in"]["T"][on]) / tot * 100
            print(name + " Exhaust temperatures (Cyl->TC are consistent for " + str(temp) + " % of the datapoints")
            temp = sum(data[name]["TC"]["EG_in"]["T"][on] > data[name]["TC"]["EG_out"]["T"][on]) / tot * 100
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
