import pandas as pd
import numpy as np
from helpers import d2df

def systemCheck(processed, CONSTANTS, dict_structure, dataset_raw):
    enginesCheck(processed, CONSTANTS)
    HTHRcheck(processed, CONSTANTS)
    SteamCheck(processed, CONSTANTS, dict_structure)
    missingValues(processed, dict_structure, CONSTANTS)
    massBalance(processed, dict_structure, CONSTANTS)
    energyBalance(processed, dict_structure, CONSTANTS)

    # Checking the boilers
    boilers_measured = (dataset_raw["Boiler_Port"].resample("D").mean() + dataset_raw["Boiler_starbord"].resample("D").mean()) * CONSTANTS["General"]["HFO"]["LHV"]
    boilers_calculated = processed["Steam:Boiler1:FuelPh_in:mdot"].resample("D").sum() * 60 * 15 * CONSTANTS["General"]["HFO"]["LHV"]
    ((boilers_calculated - boilers_measured) / boilers_measured * 100).describe()



def enginesCheck(processed, CONSTANTS):
    # This function checks that all relative values are consistent
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    print("Started consistency check for the engines...", end="", flush=True)
    text_file.write("\n *** CONSISTENTCY CHECK FOR ENGINES *** \n")
    for type in ["MainEngines", "AuxEngines"]:
        for name in CONSTANTS["General"]["NAMES"][type]:
            on = processed[name+":"+"on"]
            tot = sum(on)
                # Compressor outlet temperature must be higher than compressor inlet temperature
            temp = sum(processed[d2df(name,"Comp","Air_out","T")][on] >= processed[d2df(name,"Comp","Air_in","T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " Compressor temperatures are consistent for " + str(temp) + " % of the datapoints \n")
                # Exhaust temperature should be higher closer to the engine exhaust valve
            temp = sum(processed[d2df(name,"Cyl","EG_out","T")][on] >= processed[d2df(name,"Turbine","Mix_in","T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " Exhaust temperatures (Cyl->TC are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name,"Turbine","Mix_in","T")][on] >= processed[d2df(name,"Turbine","Mix_out","T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " Turbine temperatures are consistent for " + str(temp) + " % of the datapoints \n")
                # Checking the consistency of the LOC temperatures
            temp = sum(processed[d2df(name,"LOC","LubOil_in","T")][on] >= processed[d2df(name,"LOC","LubOil_out","T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " LOC temperatures (oil side) are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name,"LOC","LTWater_out","T")][on] >= processed[d2df(name,"LOC","LTWater_in","T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " LOC temperatures (LT water side) are consistent for " + str(temp) + " % of the datapoints \n")
                # Checking the consistency of the CAC_LT temperatures
            temp = sum(processed[d2df(name,"CAC_LT","Air_in","T")][on] >= processed[d2df(name,"CAC_LT","Air_out","T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " CAC_LT temperatures (air side) are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name,"CAC_LT","LTWater_out","T")][on] >= processed[d2df(name,"CAC_LT","LTWater_in","T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " CAC_LT temperatures (LT water side) are consistent for " + str(temp) + " % of the datapoints \n")
            # Checking the consistency of the CAC_HT temperatures
            temp = sum(processed[d2df(name, "CAC_HT", "Air_in", "T")][on] >= processed[d2df(name, "CAC_HT", "Air_out", "T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " CAC_HT temperatures (air side) are consistent for " + str(temp) + " % of the datapoints \n")
            temp = sum(processed[d2df(name, "CAC_HT", "HTWater_out", "T")][on] >= processed[d2df(name, "CAC_HT", "HTWater_in", "T")][on]) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn+name + " CAC_HT temperatures (HT water side) are consistent for " + str(temp) + " % of the datapoints \n")
            # Checking the overall engine balance
            energyOutput = (
                processed[d2df(name,"Cyl","Power_out","Edot")] +
                processed[d2df(name,"Turbine","Mix_out","Edot")] +
                (processed[d2df(name,"LOC","LTWater_out","Edot")] - processed[d2df(name,"CAC_LT","LTWater_in","Edot")]) +
                (processed[d2df(name, "CAC_HT", "HTWater_out", "Edot")] - processed[d2df(name, "JWC", "HTWater_in", "Edot")]))
            energyInput = (
                processed[d2df(name, "Cyl", "FuelCh_in", "Edot")] +
                processed[d2df(name, "Cyl", "FuelPh_in", "Edot")] +
                processed[d2df(name, "Comp", "Air_in", "Edot")]
            )
            energyBalance = abs(((energyInput - energyOutput)/energyInput))
            temp = sum(energyBalance[processed[name+":on"]] <= 0.01) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn + name + " The overall energy balance of the engine is consistent for " + str(temp) + " % of the datapoints \n")

    text_file.close()
    print("...done!")


def HTHRcheck(processed, CONSTANTS):
    # This function checks that all relative values are consistent
    tot = len(processed.index)
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    print("Started consistency check for the HTHR systems...", end="", flush=True)
    text_file.write("\n *** CONSISTENTCY CHECK FOR THE HTHR SYSTEM *** \n")
    # Checking that the temperature at the end of the circuit is lower than 90 degC
    temp = sum(processed["HTHR:HTHR24:HRWater_in:T"] <= (90 + 273.15)) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " HTHR-24 inlet temperatures on the HR side are consistent for " + str(temp) + " % of the datapoints \n")
    # HTHR 13 Temperature consistency (HT side)
    temp = sum(processed["HTHR:HTHR13:HTWater_in:T"] >= processed["HTHR:HTHR13:HTWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " HTHR-13 (HT side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    # HTHR 13 Temperature consistency (HR side)
    temp = sum(processed["HTHR:HTHR13:HRWater_in:T"] <= processed["HTHR:HTHR13:HRWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " HTHR-13 (HR side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    # HTHR 24 Temperature consistency (HT side)
    temp = sum(processed["HTHR:HTHR24:HTWater_in:T"] >= processed["HTHR:HTHR24:HTWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " HTHR-24 (HT side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    # HTHR 24 Temperature consistency (HR side)
    temp = sum(processed["HTHR:HTHR24:HRWater_in:T"] <= processed["HTHR:HTHR24:HRWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " HTHR-24 (HR side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    # Steam heater Temperature consistency (HR side)
    temp = sum(processed["HTHR:SteamHeater:HRWater_in:T"] <= processed["HTHR:SteamHeater:HRWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " Steam heater (HR side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    # Demands on the HTHR system: HVAC Preheater
    temp = sum(processed["HTHR:HVACpreheater:HRWater_in:T"] >= processed["HTHR:HVACpreheater:HRWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " HVAC-Preheater (HR side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    # Demands on the HTHR system: HVAC Reheater
    temp = sum(processed["HTHR:HVACreheater:HRWater_in:T"] >= processed["HTHR:HVACreheater:HRWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " HVAC-Reheater (HR side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    # Demands on the HTHR system: Hot water heater
    temp = sum(processed["HTHR:HotWaterHeater:HRWater_in:T"] >= processed["HTHR:HotWaterHeater:HRWater_out:T"]) / tot * 100
    warn = "WARNING " if temp < 95 else ""
    text_file.write(warn + " Hot Water Heater (HR side) temperatures are consistent for " + str(temp) + " % of the datapoints \n")
    text_file.close()
    print("...done!")

def SteamCheck(processed, CONSTANTS, dict_structure):
    # This function checks that all relative values are consistent
    tot = len(processed.index)
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    print("Started consistency check for the steam systems...", end="", flush=True)
    text_file.write("\n *** CONSISTENTCY CHECK FOR THE STEAM SYSTEMS *** \n")
    for unit in dict_structure["systems"]["Steam"]["units"]:
        if unit in {"TankHeating", "OtherTanks", "HFOtankHeating", "MachinerySpaceHeaters", "HFOheater", "Galley"}:
            temp = sum(processed[d2df("Steam", unit, "Steam_in", "mdot")] >= 0) / tot * 100
            warn = "WARNING " if temp < 95 else ""
            text_file.write(warn + unit + "Steam mass flows are consistent for " + str(temp) + " % of the datapoints \n")
    text_file.close()
    print("...done!")

def missingValues(processed, dict_structure, CONSTANTS):
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    text_file.write("\n *** LIST OF MISSING VALUES *** \n")
    print("Started looking for missing values...", end="", flush=True)
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                for property in dict_structure["systems"][system]["units"][unit]["flows"][flow]["properties"]:
                    if processed[d2df(system,unit,flow,property)].isnull().sum() == len(processed[system + ":" + "on"]):
                        text_file.write("The field {}:{}:{}:{} is still empty \n".format(system,unit,flow,property))
    text_file.close()
    print("...done!")


def massBalance(processed, dict_structure, CONSTANTS):
    # This function checks that the mass balance is respected.
    # Errors are shown:
    # - On an occurrence basis: every time that the balance is not respected counts as 1
    # - On an "average error" basis
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    text_file.write("\n *** CHECKING THE MASS BALANCE *** \n")
    print("Started checking mass balances...", end="", flush=True)
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            if (system == "Steam" and unit == "SteamDistribution"):
                aaa = 0
            balance = pd.Series(index=processed.index)
            balance[:] = 0
            max_value = 0
            counter = 0
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] in {"CPF" , "IPF", "SF"}:
                    counter = counter + 1
                    balance = balance + processed[d2df(system,unit,flow,"mdot")] * (2 * float("out" not in flow) - 1)
                    max_value = max(max_value,max(processed[d2df(system,unit,flow,"mdot")]))
            balance_occ = np.sum(balance < 0.001*max_value) / len(balance) * 100
            balance_ave = np.sum(balance) / (len(balance) * (100 - balance_occ) / 100) / max_value * 100
            if balance_occ == 100:
                text_file.write("The mass balance is fine for {}_{} unit \n".format(system, unit))
            elif (balance_occ >= 99) or (balance_ave <= 1):
                text_file.write("The mass balance is ALMOST fine for {}_{} unit \n".format(system, unit))
            elif counter == 0:
                text_file.write("There is no mass balance for {}_{} unit \n".format(system, unit))
            else:
                text_file.write("---Mass balance for {}_{} unit is respected {}% of the times, with {}% average error \n".format(system, unit, str(balance_occ), str(balance_ave)))
    print("...done!")
    text_file.close()


def energyBalance(processed, dict_structure, CONSTANTS):
    # This function checks that the mass balance is respected
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    text_file.write("\n *** CHECKING THE ENERGY BALANCE *** \n")
    print("Started checking the energy balances...", end="", flush=True)
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            balance = pd.Series(index=processed.index)
            balance[:] = 0
            max_value = 0
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                balance = balance + processed[d2df(system,unit,flow,"Edot")] * (2 * float("out" not in flow) - 1)
                max_value = max(max_value, max(processed[d2df(system, unit, flow, "Edot")]))
            balance_occ = np.sum(balance < 0.001 * max_value) / max(1, len(balance)) * 100
            balance_ave = np.sum(balance) / (len(balance) * (100 - balance_occ) / 100) / max_value * 100
            if balance_occ == 100:
                text_file.write("The energy balance is fine for {}_{} unit \n".format(system, unit))
            elif (balance_occ >= 99) or (balance_ave <= 1):
                text_file.write("The energy balance is ALMOST fine for {}_{} unit \n".format(system, unit))
            else:
                text_file.write("---energy balance for {}_{} unit is respected {}% of the times, with {}% average error \n".format(system, unit, str(balance_occ), str(balance_ave)))
    print("...done!")
    text_file.close()