# Explain here what this code does

# This code creates a big (too big?) data structure based on dictionaries and Pandas series, where the important data
#  is stored in a way that makes it easier to read and process systematically.

# Basically, the structure is structured as follows:
# --- level 1: system [Main engine/Auxiliary engine/Other system]: The assumption is that every unit is treated as a
# system if it has sub-units. If the unit is not broken down into further subunits, than it is treated as a unit
# --- level 2: unit [e.g. a heat exchanger, cylinder, turbocharger, etc.]
# --- level 3: flow

# For each flow, first a "type" flow is defined. This helps in the calculations and flow definition:
# --- Physical flow (PF)
# --- Heat flow (Qdot)
# --- Mech/El/Ch Power (Wdot)

# For physical flows, the following data Series are initiated:
# --- Mass flow (mdot)
# --- Temperature (T)
# --- Specific enthalpy (h)
# --- Specific entropy (s)
# --- Specific heat (NOTE: CONSTANT, NOT A SERIES) (cp)

# For Heat flows, the following data Series are initiated:
# --- Heat flow (Qdot)    NOTE: I use the convention that the flow is POSITIVE if it is an INPUT
# --- Temperature (T)

# For Mechanical / Electric power flows, the following data series are initiated:
# --- Energy flow (Wdot)     NOTE: I use the convention that the flow is POSITIVE if it is an INPUT


import pandas as pd
from helpers import d2df
import os

def structurePreparation(CONSTANTS, index, empty_dataset_filesystem, data_structure_preparation):
    dict_structure = flowStructure()  # Here we initiate the structure fields

    try:
        processed = pd.read_hdf(empty_dataset_filesystem, 'empty_dataset')
        if data_structure_preparation == "no":
            dict_structure = flowPreparationSimplified(dict_structure, index, CONSTANTS)
        elif data_structure_preparation == "yes":
            os.remove(empty_dataset_filesystem)
            (dict_structure, processed) = flowPreparation(dict_structure, index, CONSTANTS)  # Here we create the appropriate empty data series for each field
        else:
            print("The data_structure_preparation value should either be yes or no")
    except FileNotFoundError:
        (dict_structure, processed) = flowPreparation(dict_structure, index, CONSTANTS)  # Here we create the appropriate empty data series for each field
        processed.to_hdf(empty_dataset_filesystem, "empty_dataset", format='fixed', mode='w')
    dict_structure = streamsAssignment(dict_structure)
    dict_structure = connectionAssignment(dict_structure)
    processed = generalStatus(processed, dict_structure)  # Here we simply initiate the "status" structure
    return dict_structure, processed


def flowStructure():
    print("Started preparing the dataset_processed multi-level dictionary...", end="", flush=True)
    structure = {"systems": {"ME1": {}, "ME2": {}, "ME3": {}, "ME4": {}, "AE1": {}, "AE2": {}, "AE3": {}, "AE4": {},
                             "CoolingSystems": {}, "HTHR":{}, "Steam":{}, "Demands":{}}}
    for system in structure["systems"]:
        structure["systems"][system]["equations"] = {}
        if system[1] == "E":  # This basically means that this operation is only done if the system is an engine
            structure["systems"][system]["units"] = {"Comp": {}, "Turbine": {}, "BPsplit": {}, "BPmerge": {}, "BPvalve": {},
                                                     "CAC_HT": {}, "CAC_LT": {}, "LOC": {}, "JWC": {}, "Cyl": {},
                                                     "HTsplit": {}, "HTmerge": {}, "TCshaft": {}}
            # Compressor
            structure["systems"][system]["units"]["Comp"]["flows"] = {
                "Air_in": {"type": "CPF", "IO": "output"},
                "Air_out": {"type": "CPF", "IO": "output"},
                "Power_in": {"type": "Wdot", "IO": "input"}} # TC compressor
            structure["systems"][system]["units"]["Comp"]["equations"] = ["MassBalance"]
            # Bypass Split
            structure["systems"][system]["units"]["BPsplit"]["flows"] = {
                "Air_in": {"type": "CPF"},
                "Air_out": {"type": "CPF"},
                "BP_out": {"type": "CPF"}}  # Bypass valve
            structure["systems"][system]["units"]["BPsplit"]["equations"] = ["MassBalance", "ConstantPressure", "ConstantTemperature"]
            # Bypass Merge
            structure["systems"][system]["units"]["BPmerge"]["flows"] = {
                "EG_in": {"type": "CPF"},
                "Mix_out": {"type": "CPF"},
                "BP_in": {"type": "CPF"}}
            structure["systems"][system]["units"]["BPmerge"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Bypass Valve
            structure["systems"][system]["units"]["BPvalve"]["flows"] = {
                "BP_in": {"type": "CPF"},
                "BP_out": {"type": "CPF"}}
            structure["systems"][system]["units"]["BPvalve"]["equations"] = ["MassBalance", "ConstantTemperature"]
            # Turbine
            structure["systems"][system]["units"]["Turbine"]["flows"] = {
                "Mix_in": {"type": "CPF", "IO": "input"},
                "Mix_out": {"type": "CPF", "IO": "input"},
                "Power_out": {"type": "Wdot", "IO": "output"}}  # Turbocharger turbine
            structure["systems"][system]["units"]["Turbine"]["equations"] = ["MassBalance"]
            # Turbocharge shaft
            structure["systems"][system]["units"]["TCshaft"]["flows"] = {
                "Power_in": {"type": "Wdot", "IO": "input"},
                "Power_out": {"type": "Wdot", "IO": "output"},
                "Losses_out": {"type": "Qdot"}}
            structure["systems"][system]["units"]["TCshaft"]["equations"] = []
            # Charge air cooler, HT side
            structure["systems"][system]["units"]["CAC_HT"]["flows"] = {
                "Air_in": {"type": "CPF", "IO": "output"},
                "HTWater_in": {"type": "IPF", "IO": "input"},
                "Air_out": {"type": "CPF", "IO": "output"},
                "HTWater_out": {"type": "IPF", "IO": "input"}}  # Charge air
            structure["systems"][system]["units"]["CAC_HT"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Charge air cooler, LT stage
            structure["systems"][system]["units"]["CAC_LT"]["flows"] = {
                "Air_in": {"type": "CPF", "IO": "output"},
                "LTWater_in": {"type": "IPF", "IO": "input"},
                "Air_out": {"type": "CPF", "IO": "output"},
                "LTWater_out": {"type": "IPF", "IO": "input"}}  # Charge air
            structure["systems"][system]["units"]["CAC_LT"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Lubricating oil cooler
            structure["systems"][system]["units"]["LOC"]["flows"] = {
                "LubOil_in": {"type": "IPF", "IO": "output"},
                "LTWater_in": {"type": "IPF", "IO": "input"},
                "LubOil_out": {"type": "IPF", "IO": "output"},
                "LTWater_out": {"type": "IPF", "IO": "input"}}  # Lubricating oil
            structure["systems"][system]["units"]["LOC"]["equations"] = ["MassBalance"]
            # Jacket water cooler
            structure["systems"][system]["units"]["JWC"]["flows"] = {
                "QdotJW_in": {"type": "Qdot", "IO": "output"},
                "HTWater_in": {"type": "IPF", "IO": "input"},
                "HTWater_out": {"type": "IPF", "IO": "input"}}  # Jacket water
            structure["systems"][system]["units"]["JWC"]["equations"] = ["MassBalance"]
            # Engine cylinders
            structure["systems"][system]["units"]["Cyl"]["flows"] = {
                "Air_in": {"type": "CPF", "IO": "input"},
                "FuelPh_in": {"type": "CPF", "IO": "input"},
                "FuelCh_in": {"type": "CEF", "IO": "input"},
                "EG_out": {"type":"CPF"},
                "Power_out": {"type": "Wdot", "IO": "output"},
                "QdotJW_out": {"type":"Qdot"},
                "LubOil_in": {"type": "IPF"},
                "LubOil_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["Cyl"]["equations"] = ["MassBalance"]
            # HT cooling systems split
            structure["systems"][system]["units"]["HTsplit"]["flows"] = {
                "HTWater_in": {"type": "IPF"},
                "HTWater_out": {"type": "IPF"},
                "LTWater_out": {"type": "IPF"}}  # Bypass valve
            structure["systems"][system]["units"]["HTsplit"]["equations"] = ["MassBalance", "ConstantTemperature"]
            # HT cooling systems merge
            structure["systems"][system]["units"]["HTmerge"]["flows"] = {
                "HTWater_in": {"type": "IPF"},
                "HTWater_out": {"type": "IPF"},
                "LTWater_in": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTmerge"]["equations"] = ["MassBalance"]
            # Only auxiliary engines AND main engines 2/3 have the exhaust gas boiler
            if system[0] == "A" or system[2] == "2" or system[2] == "3":
                # Heat recovery steam generator
                structure["systems"][system]["units"].update({"HRSG": {}})
                structure["systems"][system]["units"]["HRSG"]["flows"] = {
                    "Mix_in": {"type": "CPF", "IO": "input"},
                    "Mix_out": {"type": "CPF", "IO": "input"},
                    "Steam_in": {"type": "SF", "state": "SL", "IO": "output"},
                    "Steam_out": {"type": "SF", "state": "SV", "IO": "output"}}
                structure["systems"][system]["units"]["HRSG"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Auxiliary engines also have electric generators connected
            if system[0] == "A":
                structure["systems"][system]["units"].update({"AG": {}})
                structure["systems"][system]["units"]["AG"]["flows"] = {
                    "Power_in": {"type": "Wdot", "IO": "input"},
                    "Power_out": {"type": "CEF", "IO": "output"},
                    "Losses_out": {"type": "Qdot"}}
                structure["systems"][system]["units"]["AG"]["equations"] = []


        elif system == "CoolingSystems":
            structure["systems"][system]["units"] = { "SWC13": {}, "SWC24": {}, "HTcollector13": {}, "HTcollector24": {},
                                                     "LTcollector13": {}, "LTcollector24": {}, "LTdistribution13": {}, "LTdistribution24": {},
                                                      "LTHTmerge13": {}, "LTHTmerge24": {}, "HTsplit13": {}, "HTsplit24":{}}
            # Seawater cooler, ER 1/3
            structure["systems"][system]["units"]["SWC13"]["flows"] = {
                "SeaWater_in": {"type": "IPF", "IO": "input"},
                "LTWater_in": {"type": "IPF", "IO": "output"},
                "SeaWater_out": {"type": "IPF", "IO": "input"},
                "LTWater_out": {"type": "IPF", "IO": "output"},
                "HTWater_in": {"type": "IPF", "IO": "output"}}
            structure["systems"][system]["units"]["SWC13"]["equations"] = ["MassBalance"]
            # Seawater cooler, ER 2/4
            structure["systems"][system]["units"]["SWC24"]["flows"] = {
                "SeaWater_in": {"type": "IPF", "IO": "input"},
                "LTWater_in": {"type": "IPF", "IO": "output"},
                "SeaWater_out": {"type": "IPF", "IO": "input"},
                "LTWater_out": {"type": "IPF", "IO": "output"},
                "HTWater_in": {"type": "IPF", "IO": "output"}}
            structure["systems"][system]["units"]["SWC24"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["LTcollector13"]["flows"] = {
                "LTWater_AE1_in": {"type": "IPF"},
                "LTWater_AE3_in": {"type": "IPF"},
                "LTWater_ME1_in": {"type": "IPF"},
                "LTWater_ME3_in": {"type": "IPF"},
                "LTWater_out": {"type": "IPF"}, "HTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTcollector13"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["LTcollector24"]["flows"] = {
                "LTWater_AE2_in": {"type": "IPF"},
                "LTWater_AE4_in": {"type": "IPF"},
                "LTWater_ME2_in": {"type": "IPF"},
                "LTWater_ME4_in": {"type": "IPF"},
                "LTWater_out": {"type": "IPF"},
                "HTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTcollector24"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["LTdistribution13"]["flows"] = {
                "LTWater_in": {"type": "IPF"},
                "LTWater_AE3_out": {"type": "IPF"},
                "LTWater_AE1_out": {"type": "IPF"},
                "LTWater_ME1_out": {"type": "IPF"},
                "LTWater_ME3_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTdistribution13"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["LTdistribution24"]["flows"] = {
                "LTWater_in": {"type": "IPF"},
                "LTWater_AE2_out": {"type": "IPF"},
                "LTWater_AE4_out": {"type": "IPF"},
                "LTWater_ME2_out": {"type": "IPF"},
                "LTWater_ME4_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTdistribution24"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["LTHTmerge13"]["flows"] = {
                "LTWater_in": {"type": "IPF"},
                "HTWater_in": {"type": "IPF"},
                "HTWater_ME1_out": {"type": "IPF"},
                "HTWater_ME3_out": {"type": "IPF"},
                "HTWater_AE1_out": {"type": "IPF"},
                "HTWater_AE3_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTHTmerge13"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["LTHTmerge24"]["flows"] = {
                "LTWater_in": {"type": "IPF"},
                "HTWater_in": {"type": "IPF"},
                "HTWater_ME2_out": {"type": "IPF"},
                "HTWater_ME4_out": {"type": "IPF"},
                "HTWater_AE2_out": {"type": "IPF"},
                "HTWater_AE4_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTHTmerge24"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["HTcollector13"]["flows"] = {
                "HTWater_AE1_in": {"type": "IPF"},
                "HTWater_AE3_in": {"type": "IPF"},
                "HTWater_ME1_in": {"type": "IPF"},
                "HTWater_ME3_in": {"type": "IPF"},
                "HTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTcollector13"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["HTcollector24"]["flows"] = {
                "HTWater_AE2_in": {"type": "IPF"},
                "HTWater_AE4_in": {"type": "IPF"},
                "HTWater_ME2_in": {"type": "IPF"},
                "HTWater_ME4_in": {"type": "IPF"},
                "HTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTcollector24"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["HTsplit13"]["flows"] = {
                "HTWater_in": {"type": "IPF"},
                "HTWater_out": {"type": "IPF"},
                "LTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTsplit13"]["equations"] = ["MassBalance", "ConstantTemperature"]
            structure["systems"][system]["units"]["HTsplit24"]["flows"] = {
                "HTWater_in": {"type": "IPF"},
                "HTWater_out": {"type": "IPF"},
                "LTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTsplit24"]["equations"] = ["MassBalance", "ConstantTemperature"]

        elif system == "HTHR":
            structure["systems"][system]["units"] = {"HTHR13": {}, "HTHR24": {}, "HTHRsplit": {}, "HTHRmerge": {},
                            "HVACpreheater": {}, "HVACreheater": {}, "SteamHeater": {}, "HotWaterHeater": {}}
            structure["systems"][system]["units"]["HTHR13"]["flows"] = {
                "HTWater_in": {"type": "IPF", "IO": "input"},
                "HTWater_out": {"type": "IPF", "IO": "input"},
                "HRWater_in": {"type": "IPF", "IO": "output"},
                "HRWater_out": {"type": "IPF", "IO": "output"}}
            structure["systems"][system]["units"]["HTHR13"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["HTHR24"]["flows"] = {
                "HTWater_in": {"type": "IPF", "IO": "input"},
                "HTWater_out": {"type": "IPF", "IO": "input"},
                "HRWater_in": {"type": "IPF", "IO": "output"},
                "HRWater_out": {"type": "IPF", "IO": "output"}}
            structure["systems"][system]["units"]["HTHR24"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["SteamHeater"]["flows"] = {
                "Steam_in": {"type": "SF", "state": "SV", "IO": "input"},
                "Steam_out": {"type": "SF", "state": "SL", "IO": "input"},
                "HRWater_in": {"type": "IPF", "IO": "output"},
                "HRWater_out": {"type": "IPF", "IO": "output"}}
            structure["systems"][system]["units"]["SteamHeater"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["HotWaterHeater"]["flows"] = {
                "HRWater_in": {"type": "IPF", "IO": "input"},
                "HRWater_out": {"type": "IPF", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["HotWaterHeater"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["HVACpreheater"]["flows"] = {
                "HRWater_in": {"type": "IPF", "IO": "input"},
                "HRWater_out": {"type": "IPF", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["HVACpreheater"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["HVACreheater"]["flows"] = {
                "HRWater_in": {"type": "IPF", "IO": "input"},
                "HRWater_out": {"type": "IPF", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["HVACreheater"]["equations"] = ["MassBalance"]
            structure["systems"][system]["units"]["HTHRsplit"]["flows"] = {
                "HRWater_in": {"type": "IPF"},
                "HRWater_HWH_out": {"type": "IPF"},
                "HRWater_PreH_out": {"type": "IPF"},
                "HRWater_ReH_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTHRsplit"]["equations"] = ["MassBalance", "ConstantTemperature"]
            structure["systems"][system]["units"]["HTHRmerge"]["flows"] = {
                "HRWater_out": {"type": "IPF"},
                "HRWater_HWH_in": {"type": "IPF"},
                "HRWater_PreH_in": {"type": "IPF"},
                "HRWater_ReH_in": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTHRmerge"]["equations"] = ["MassBalance"]



        elif system == "Steam":
            structure["systems"][system]["units"] = {"Boiler1": {}, "Boiler2": {}, "SteamCollector": {}, "SteamDistribution": {},
                                                     "TankHeating": {}, "OtherTanks": {}, "HFOtankHeating": {}, "MachinerySpaceHeaters": {},
                                                     "HFOheater": {}, "Galley": {}}
            # Auxiliary boiler
            structure["systems"][system]["units"]["Boiler1"]["flows"] = {
                "Air_in": {"type": "CPF", "IO": "input"},
                "EG_out": {"type": "CPF"},
                "FuelCh_in": {"type": "CEF", "IO": "input"},
                "FuelPh_in": {"type": "IPF", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SL", "IO": "output"},
                "Steam_out": {"type": "SF", "state": "SV", "IO": "output"}}
            structure["systems"][system]["units"]["Boiler1"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["Boiler2"]["flows"] = {
                "Air_in": {"type": "CPF", "IO": "input"},
                "EG_out": {"type": "CPF"},
                "FuelCh_in": {"type": "CEF", "IO": "input"},
                "FuelPh_in": {"type": "IPF", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SL", "IO": "output"},
                "Steam_out": {"type": "SF", "state": "SV", "IO": "output"}}
            structure["systems"][system]["units"]["Boiler2"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Steam collector (collects steam in form of saturated liquid from all users)
            structure["systems"][system]["units"]["SteamDistribution"]["flows"] = {
                "Steam_HRSG_ME2_in": {"type": "SF", "state": "SV"},
                "Steam_HRSG_ME3_in": {"type": "SF", "state": "SV"},
                "Steam_AB1_in": {"type": "SF", "state": "SV"},
                "Steam_AB2_in": {"type": "SF", "state": "SV"},
                "Steam_HRSG_AE1_in": {"type": "SF", "state": "SV"},
                "Steam_HRSG_AE2_in": {"type": "SF", "state": "SV"},
                "Steam_HRSG_AE3_in": {"type": "SF", "state": "SV"},
                "Steam_HRSG_AE4_in": {"type": "SF", "state": "SV"},
                "Steam_TH_out": {"type": "SF", "state": "SV"},
                "Steam_MSH_out": {"type": "SF", "state": "SV"},
                "Steam_HTH_out": {"type": "SF", "state": "SV"},
                "Steam_HH_out": {"type": "SF", "state": "SV"},
                "Steam_G_out": {"type": "SF", "state": "SV"},
                "Steam_SH_out": {"type": "SF", "state": "SV"},
                "Steam_OT_out": {"type": "SF", "state": "SV"}}
            structure["systems"][system]["units"]["SteamDistribution"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Steam distribution, sending around saturated vapor to all users
            structure["systems"][system]["units"]["SteamCollector"]["flows"] = {
                "Steam_HRSG_ME2_out": {"type": "SF", "state": "SL"},
                "Steam_HRSG_ME3_out": {"type": "SF", "state": "SL"},
                "Steam_AB1_out": {"type": "SF", "state": "SL"},
                "Steam_AB2_out": {"type": "SF", "state": "SL"},
                "Steam_HRSG_AE1_out": {"type": "SF", "state": "SL"},
                "Steam_HRSG_AE2_out": {"type": "SF", "state": "SL"},
                "Steam_HRSG_AE3_out": {"type": "SF", "state": "SL"},
                "Steam_HRSG_AE4_out": {"type": "SF", "state": "SL"},
                "Steam_TH_in": {"type": "SF", "state": "SL"},
                "Steam_MSH_in": {"type": "SF", "state": "SL"},
                "Steam_HTH_in": {"type": "SF", "state": "SL"},
                "Steam_HH_in": {"type": "SF", "state": "SL"},
                "Steam_G_in": {"type": "SF", "state": "SL"},
                "Steam_SH_in": {"type": "SF", "state": "SL"},
                "Steam_OT_in": {"type": "SF", "state": "SV"}}
            structure["systems"][system]["units"]["SteamCollector"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Users
            structure["systems"][system]["units"]["TankHeating"]["flows"] = {
                "Steam_out": {"type": "SF", "state": "SL", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SV", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["TankHeating"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["OtherTanks"]["flows"] = {
                "Steam_out": {"type": "SF", "state": "SL", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SV", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["OtherTanks"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["HFOtankHeating"]["flows"] = {
                "Steam_out": {"type": "SF", "state": "SL", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SV", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["HFOtankHeating"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["MachinerySpaceHeaters"]["flows"] = {
                "Steam_out": {"type": "SF", "state": "SL", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SV", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["MachinerySpaceHeaters"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["HFOheater"]["flows"] = {
                "Steam_out": {"type": "SF", "state": "SL", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SV", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["HFOheater"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["Galley"]["flows"] = {
                "Steam_out": {"type": "SF", "state": "SL", "IO": "input"},
                "Steam_in": {"type": "SF", "state": "SV", "IO": "input"},
                "Qdot_out": {"type": "Qdot", "IO": "output"}}
            structure["systems"][system]["units"]["Galley"]["equations"] = ["MassBalance", "ConstantPressure"]

        elif system == "Demands":
            structure["systems"][system]["units"] = {"Electricity": {}, "Mechanical": {}, "Heat": {}}
            structure["systems"][system]["units"]["Electricity"]["flows"] = {"Thrusters": {"type": "CEF"}, "HVAC": {"type": "CEF"}, "Other": {"type": "CEF"}}
            structure["systems"][system]["units"]["Mechanical"]["flows"] = {"Propeller1": {"type": "CEF"}, "Propeller2": {"type": "CEF"}, "Total": {"type": "CEF"}}
            structure["systems"][system]["units"]["Heat"]["flows"] = {
                "HotWaterHeater": {"type": "Qdot"}, "HVACpreheater": {"type": "Qdot"}, "HVACreheater": {"type": "Qdot"},
                "TankHeating": {"type": "Qdot"}, "OtherTanks": {"type": "Qdot"}, "HFOtankHeating": {"type": "Qdot"},
                "MachinerySpaceHeaters": {"type": "Qdot"}, "HFOheater": {"type": "Qdot"}, "Galley": {"type": "Qdot"}}
            structure["systems"][system]["units"]["Electricity"]["equations"] = []
            structure["systems"][system]["units"]["Mechanical"]["equations"] = []
            structure["systems"][system]["units"]["Heat"]["equations"] = []
        else:
            print("Error! There is an unrecognized element in the unit system structure at system level")
    print("...done!")
    return structure


def streamsAssignment(dict_structure):
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            streams = {}
            if unit == "Cyl":
                streams["Total"] = []
                for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                    if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] in {"CPF"}:
                        streams["Total"].append(d2df(system, unit, flow, ""))
                    elif dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] in {"IPF"}:
                        temp = flow.split(sep="_")
                        if temp[0] not in streams:
                            streams[temp[0]] = [d2df(system, unit, flow, "")]
                        elif temp[0] in streams:
                            streams[temp[0]].append(d2df(system, unit, flow, ""))
                        else:
                            print("Something very weird happened")
            elif any(x in unit.lower() for x in {"split", "merge", "distribution", "collector"}):
                streams["Total"] = []
                for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                    #if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] == "CPF":
                    streams["Total"].append(d2df(system, unit, flow, ""))
            else:
                for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                    if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] in {"CPF", "IPF", "SF"}:
                        temp = flow.split(sep="_")
                        if temp[0] not in streams:
                            streams[temp[0]] = [d2df(system, unit, flow, "")]
                        elif temp[0] in streams:
                            streams[temp[0]].append(d2df(system, unit, flow, ""))
                        else:
                            print("Something very weird happened")
            dict_structure["systems"][system]["units"][unit]["streams"] = streams
    return dict_structure



def flowPreparation(dict_structure, database_index, CONSTANTS):
    print("Start preparing the Pandas dataframe with all inputs...", end="")
    dict_structure["property_list"] = []
    processed = pd.DataFrame(index=database_index)
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            if any(standard in unit.lower() for standard in CONSTANTS["General"]["UNIT_TYPES"]["STANDARD"]):
                for efficiency in CONSTANTS["General"]["EFFICIENCY_LIST"]["STANDARD"]:
                    eta_ID = system + ":" + unit + ":" + efficiency
                    processed[eta_ID] = pd.Series(index=database_index)
            elif any(mixmerge in unit.lower() for mixmerge in CONSTANTS["General"]["UNIT_TYPES"]["MIXMERGE"]):
                for efficiency in CONSTANTS["General"]["EFFICIENCY_LIST"]["MIXMERGE"]:
                    eta_ID = system + ":" + unit + ":" + efficiency
                    processed[eta_ID] = pd.Series(index=database_index)
            else:
                for efficiency in CONSTANTS["General"]["EFFICIENCY_LIST"]["HEX"]:
                    eta_ID = system + ":" + unit + ":" + efficiency
                    processed[eta_ID] = pd.Series(index=database_index)
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                dict_structure["systems"][system]["units"][unit]["flows"][flow]["ID"] = system + ":" + unit + ":" + flow
                dict_structure["systems"][system]["units"][unit]["flows"][flow]["properties"] = \
                    CONSTANTS["General"]["PROPERTY_LIST"][dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"]]
            # Creating an element of the main structure with the full list of properties in the whole model
                for property in dict_structure["systems"][system]["units"][unit]["flows"][flow]["properties"]:
                    flow_ID = system + ":" + unit + ":" + flow + ":" + property
                    dict_structure["property_list"].append(flow_ID)
                    processed[flow_ID] = pd.Series(index=database_index)
    print("...done!")
    return (dict_structure, processed)


def flowPreparationSimplified(structure, database_index, CONSTANTS):
    print("Start preparing the Pandas dataframe with all inputs...", end="", flush=True)
    structure["property_list"] = []
    for system in structure["systems"]:
        for unit in structure["systems"][system]["units"]:
            for flow in structure["systems"][system]["units"][unit]["flows"]:
                structure["systems"][system]["units"][unit]["flows"][flow]["ID"] = system + ":" + unit + ":" + flow
                structure["systems"][system]["units"][unit]["flows"][flow]["properties"] = \
                    CONSTANTS["General"]["PROPERTY_LIST"][structure["systems"][system]["units"][unit]["flows"][flow]["type"]]
            # Creating an element of the main structure with the full list of properties in the whole model
                for property in structure["systems"][system]["units"][unit]["flows"][flow]["properties"]:
                    flow_ID = system + ":" + unit + ":" + flow + ":" + property
                    structure["property_list"].append(flow_ID)
    print("...done!")
    return structure


def connectionAssignment(structure):
    print("Start assigning connections between components...", end="", flush=True)
    for system in structure["systems"]:
        if system[1] == "E":  # This basically means that this operation is only done if the system is an engine
            # The turbocharger shaft is connected both to the turbine and to the compressor
            structure["systems"][system]["units"]["Comp"]["flows"]["Power_in"]["Connections"] = [system + ":" + "TCshaft" + ":" + "Power_out"]
            structure["systems"][system]["units"]["TCshaft"]["flows"]["Power_out"]["Connections"] = [system + ":" + "Comp" + ":" + "Power_in"]
            structure["systems"][system]["units"]["Turbine"]["flows"]["Power_out"]["Connections"] = [system + ":" + "TCshaft" + ":" + "Power_in"]
            structure["systems"][system]["units"]["TCshaft"]["flows"]["Power_in"]["Connections"] = [system + ":" + "Turbine" + ":" + "Power_out"]
            # The compressor is connected to the BP valve
            structure["systems"][system]["units"]["Comp"]["flows"]["Air_out"]["Connections"] = [system + ":" + "BPsplit" + ":" + "Air_in"]
            structure["systems"][system]["units"]["BPsplit"]["flows"]["Air_in"]["Connections"] = [system + ":" + "Comp" + ":" + "Air_out"]
            # The BP valve is connected to the CAC-HT cooler
            structure["systems"][system]["units"]["CAC_HT"]["flows"]["Air_in"]["Connections"] = [system + ":" + "BPsplit" + ":" + "Air_out"]
            structure["systems"][system]["units"]["BPsplit"]["flows"]["Air_out"]["Connections"] = [system + ":" + "CAC_HT" + ":" + "Air_in"]
            # The CAC-HT cooler is connected to the CAC-LT cooler
            structure["systems"][system]["units"]["CAC_HT"]["flows"]["Air_out"]["Connections"] = [system + ":" + "CAC_LT" + ":" + "Air_in"]
            structure["systems"][system]["units"]["CAC_LT"]["flows"]["Air_in"]["Connections"] = [system + ":" + "CAC_HT" + ":" + "Air_out"]
            # The CAC-LT cooler is connected to the Cylinder inlet manifold
            structure["systems"][system]["units"]["Cyl"]["flows"]["Air_in"]["Connections"] = [system + ":" + "CAC_LT" + ":" + "Air_out"]
            structure["systems"][system]["units"]["CAC_LT"]["flows"]["Air_out"]["Connections"] = [system + ":" + "Cyl" + ":" + "Air_in"]
            # The cylinder exhaust manifold is connected to the BP valve
            structure["systems"][system]["units"]["BPmerge"]["flows"]["EG_in"]["Connections"] = [system + ":" + "Cyl" + ":" + "EG_out"]
            structure["systems"][system]["units"]["Cyl"]["flows"]["EG_out"]["Connections"] = [system + ":" + "BPmerge" + ":" + "EG_in"]
            # The turbine is connected to the BP valve
            structure["systems"][system]["units"]["Turbine"]["flows"]["Mix_in"]["Connections"] = [system + ":" + "BPmerge" + ":" + "Mix_out"]
            structure["systems"][system]["units"]["BPmerge"]["flows"]["Mix_out"]["Connections"] = [system + ":" + "Turbine" + ":" + "Mix_in"]
            # The CAC-LT cooler water is connected to the LOC
            structure["systems"][system]["units"]["LOC"]["flows"]["LTWater_in"]["Connections"] = [system + ":" + "CAC_LT" + ":" + "LTWater_out"]
            structure["systems"][system]["units"]["CAC_LT"]["flows"]["LTWater_out"]["Connections"] = [system + ":" + "LOC" + ":" + "LTWater_in"]
            # The CAC-HT cooler water is connected to the JWC
            structure["systems"][system]["units"]["CAC_HT"]["flows"]["HTWater_in"]["Connections"] = [system + ":" + "JWC" + ":" + "HTWater_out"]
            structure["systems"][system]["units"]["JWC"]["flows"]["HTWater_out"]["Connections"] = [system + ":" + "CAC_HT" + ":" + "HTWater_in"]
            # The oil out from the lub oil cooler is connected to the engine inlet, and vice versa
            structure["systems"][system]["units"]["LOC"]["flows"]["LubOil_in"]["Connections"] = [system + ":" + "Cyl" + ":" + "LubOil_out"]
            structure["systems"][system]["units"]["Cyl"]["flows"]["LubOil_out"]["Connections"] = [system + ":" + "LOC" + ":" + "LubOil_in"]
            structure["systems"][system]["units"]["LOC"]["flows"]["LubOil_out"]["Connections"] = [system + ":" + "Cyl" + ":" + "LubOil_in"]
            structure["systems"][system]["units"]["Cyl"]["flows"]["LubOil_in"]["Connections"] = [system + ":" + "LOC" + ":" + "LubOil_out"]
            # The BP split is also connected to the BP merge
            structure["systems"][system]["units"]["BPsplit"]["flows"]["BP_out"]["Connections"] = [system + ":" + "BPvalve" + ":" + "BP_in"]
            structure["systems"][system]["units"]["BPvalve"]["flows"]["BP_in"]["Connections"] = [system + ":" + "BPsplit" + ":" + "BP_out"]
            structure["systems"][system]["units"]["BPmerge"]["flows"]["BP_in"]["Connections"] = [system + ":" + "BPvalve" + ":" + "BP_out"]
            structure["systems"][system]["units"]["BPvalve"]["flows"]["BP_out"]["Connections"] = [system + ":" + "BPmerge" + ":" + "BP_in"]
            # Inserting connections for HT merge and HT split
            structure["systems"][system]["units"]["HTsplit"]["flows"]["HTWater_out"]["Connections"] = [system + ":" + "HTmerge" + ":" + "HTWater_in"]
            structure["systems"][system]["units"]["HTmerge"]["flows"]["HTWater_in"]["Connections"] = [system + ":" + "HTsplit" + ":" + "HTWater_out"]
            structure["systems"][system]["units"]["HTsplit"]["flows"]["HTWater_in"]["Connections"] = [system + ":" + "CAC_HT" + ":" + "HTWater_out"]
            structure["systems"][system]["units"]["CAC_HT"]["flows"]["HTWater_out"]["Connections"] = [system + ":" + "HTsplit" + ":" + "HTWater_in"]
            structure["systems"][system]["units"]["JWC"]["flows"]["HTWater_in"]["Connections"] = [system + ":" + "HTmerge" + ":" + "HTWater_out"]
            structure["systems"][system]["units"]["HTmerge"]["flows"]["HTWater_out"]["Connections"] = [system + ":" + "JWC" + ":" + "HTWater_in"]
            # Inserting connections to the central components: LT collector and LT splitter. Separated for different engine rooms
            if system[2] in {"1","3"}:
                # HT water from the HT splitter goes into the LT collector
                structure["systems"][system]["units"]["HTsplit"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "HTcollector13" + ":" + "HTWater_"+system+"_in"]
                structure["systems"]["CoolingSystems"]["units"]["HTcollector13"]["flows"]["HTWater_"+system+"_in"]["Connections"] = [system + ":" + "HTsplit" + ":" + "LTWater_out"]
                # LT water from the LOC outlet goes into the LT collector
                structure["systems"][system]["units"]["LOC"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTcollector13" + ":" + "LTWater_"+system+"_in"]
                structure["systems"]["CoolingSystems"]["units"]["LTcollector13"]["flows"]["LTWater_"+system+"_in"]["Connections"] = [system + ":" + "LOC" + ":" + "LTWater_out"]
                # LT water from the LT distribution goes into the charge air cooler
                structure["systems"]["CoolingSystems"]["units"]["LTdistribution13"]["flows"]["LTWater_"+system+"_out"]["Connections"] = [system + ":" + "CAC_LT" + ":" + "LTWater_in"]
                structure["systems"][system]["units"]["CAC_LT"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTdistribution13" + ":" + "LTWater_"+system+"_out"]
                # The other inlet of the HT water merge is from the flow mixed between LT collected and HT
                structure["systems"][system]["units"]["HTmerge"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTHTmerge13" + ":" + "HTWater_" + system + "_out"]
                structure["systems"]["CoolingSystems"]["units"]["LTHTmerge13"]["flows"]["HTWater_" + system + "_out"]["Connections"] = [system + ":" + "HTmerge" + ":" + "LTWater_in"]
            if system[2] in {"2", "4"}:
                # HT water from the HT splitter goes into the LT collector
                structure["systems"][system]["units"]["HTsplit"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "HTcollector24" + ":" + "HTWater_" + system + "_in"]
                structure["systems"]["CoolingSystems"]["units"]["HTcollector24"]["flows"]["HTWater_" + system + "_in"]["Connections"] = [system + ":" + "HTsplit" + ":" + "LTWater_out"]
                # LT water from the LT split goes into the LT collector
                structure["systems"][system]["units"]["LOC"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTcollector24" + ":" + "LTWater_" + system + "_in"]
                structure["systems"]["CoolingSystems"]["units"]["LTcollector24"]["flows"]["LTWater_" + system + "_in"]["Connections"] = [system + ":" + "LOC" + ":" + "LTWater_out"]
                # LT water from the LT distribution goes into the charge air cooler
                structure["systems"]["CoolingSystems"]["units"]["LTdistribution24"]["flows"]["LTWater_" + system + "_out"]["Connections"] = [system + ":" + "CAC_LT" + ":" + "LTWater_in"]
                structure["systems"][system]["units"]["CAC_LT"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTdistribution24" + ":" + "LTWater_" + system + "_out"]
                # The other inlet of the HT water merge is from the flow mixed between LT collected and HT
                structure["systems"][system]["units"]["HTmerge"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTHTmerge24" + ":" + "HTWater_" + system + "_out"]
                structure["systems"]["CoolingSystems"]["units"]["LTHTmerge24"]["flows"]["HTWater_" + system + "_out"]["Connections"] = [system + ":" + "HTmerge" + ":" + "LTWater_in"]
            if system[0] == "A" or system[2] == "2" or system[2] == "3":
                # The HRSG inlet is connected to the engine turbine outlet
                structure["systems"][system]["units"]["HRSG"]["flows"]["Mix_in"]["Connections"] = [system + ":" + "Turbine" + ":" + "Mix_out"]
                structure["systems"][system]["units"]["Turbine"]["flows"]["Mix_out"]["Connections"] = [system + ":" + "HRSG" + ":" + "Mix_in"]
                # On the steam side, the HRSG is connected to the Steam distribution and steam collector
                structure["systems"][system]["units"]["HRSG"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_HRSG_" + system + "_out"]
                structure["systems"][system]["units"]["HRSG"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_HRSG_" + system + "_in"]
                structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_HRSG_" + system + "_out"]["Connections"] = [system + ":" + "HRSG" + ":" + "Steam_in"]
                structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_HRSG_" + system + "_in"]["Connections"] = [system + ":" + "HRSG" + ":" + "Steam_out"]
            if system[0] == "A":
                structure["systems"][system]["units"]["AG"]["flows"]["Power_in"]["Connections"] = [system + ":" + "Cyl" + ":" + "Power_out"]
                structure["systems"][system]["units"]["Cyl"]["flows"]["Power_out"]["Connections"] = [system + ":" + "AG" + ":" + "Power_in"]
        elif system == "Demands":
            for unit in structure["systems"][system]["units"]:
                if unit == "Heat":
                    for flow in structure["systems"][system]["units"][unit]["flows"]:
                        if flow in {"TankHeating", "HFOtankHeating", "Galley", "MachinerySpaceHeaters", "HFOheater", "OtherTanks"}:
                            structure["systems"]["Demands"]["units"]["Heat"]["flows"][flow]["Connections"] = ["Steam" + ":" + flow + ":" + "Qdot_out"]
                            structure["systems"]["Steam"]["units"][flow]["flows"]["Qdot_out"]["Connections"] = ["Demands" + ":" + "Heat" + ":" + flow]
                        elif flow in {"HVACpreheater", "HVACreheater", "HotWaterHeater"}:
                            structure["systems"]["Demands"]["units"]["Heat"]["flows"][flow]["Connections"] = ["HTHR" + ":" + flow + ":" + "Qdot_out"]
                            structure["systems"]["HTHR"]["units"][flow]["flows"]["Qdot_out"]["Connections"] = ["Demands" + ":" + "Heat" + ":" + flow]
        else:
            ############    HIGH TEMPERATURE WATER HEAT RECOVERY  ##########
            # Including the connection between HT collectors and HTHR
            structure["systems"]["HTHR"]["units"]["HTHR13"]["flows"]["HTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "HTcollector13" + ":" + "HTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["HTcollector13"]["flows"]["HTWater_out"]["Connections"] = ["HTHR" + ":" + "HTHR13" + ":" + "HTWater_in"]
            structure["systems"]["HTHR"]["units"]["HTHR24"]["flows"]["HTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "HTcollector24" + ":" + "HTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["HTcollector24"]["flows"]["HTWater_out"]["Connections"] = ["HTHR" + ":" + "HTHR24" + ":" + "HTWater_in"]
            # Then, the outlet of the HTHR is connected to the LT collector
            structure["systems"]["HTHR"]["units"]["HTHR13"]["flows"]["HTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "HTsplit13" + ":" + "HTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["HTsplit13"]["flows"]["HTWater_in"]["Connections"] = ["HTHR" + ":" + "HTHR13" + ":" + "HTWater_out"]
            structure["systems"]["HTHR"]["units"]["HTHR24"]["flows"]["HTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "HTsplit24" + ":" + "HTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["HTsplit24"]["flows"]["HTWater_in"]["Connections"] = ["HTHR" + ":" + "HTHR24" + ":" + "HTWater_out"]
            # On the other side, the HTHR on the HR water side is connected to the rest of the HR systems.
            structure["systems"]["HTHR"]["units"]["HTHR24"]["flows"]["HRWater_in"]["Connections"] = ["HTHR" + ":" + "HTHRmerge" + ":" + "HRWater_out"]
            structure["systems"]["HTHR"]["units"]["HTHRmerge"]["flows"]["HRWater_out"]["Connections"] = ["HTHR" + ":" + "HTHR24" + ":" + "HRWater_in"]
            structure["systems"]["HTHR"]["units"]["HTHR13"]["flows"]["HRWater_in"]["Connections"] = ["HTHR" + ":" + "HTHR24" + ":" + "HRWater_out"]
            structure["systems"]["HTHR"]["units"]["HTHR24"]["flows"]["HRWater_out"]["Connections"] = ["HTHR" + ":" + "HTHR13" + ":" + "HRWater_in"]
            structure["systems"]["HTHR"]["units"]["HTHR13"]["flows"]["HRWater_out"]["Connections"] = ["HTHR" + ":" + "SteamHeater" + ":" + "HRWater_in"]
            structure["systems"]["HTHR"]["units"]["SteamHeater"]["flows"]["HRWater_in"]["Connections"] = ["HTHR" + ":" + "HTHR13" + ":" + "HRWater_out"]
            # On the other side, the Steam heater is connected to the steam distribution system
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_SH_out"]["Connections"] = ["HTHR" + ":" + "SteamHeater" + ":" + "Steam_in"]
            structure["systems"]["HTHR"]["units"]["SteamHeater"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_SH_out"]
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_SH_in"]["Connections"] = ["HTHR" + ":" + "SteamHeater" + ":" + "Steam_out"]
            structure["systems"]["HTHR"]["units"]["SteamHeater"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_SH_in"]
            # Following the HR water, we get to the splitter
            structure["systems"]["HTHR"]["units"]["SteamHeater"]["flows"]["HRWater_out"]["Connections"] = ["HTHR" + ":" + "HTHRsplit" + ":" + "HRWater_in"]
            structure["systems"]["HTHR"]["units"]["HTHRsplit"]["flows"]["HRWater_in"]["Connections"] = ["HTHR" + ":" + "SteamHeater" + ":" + "HRWater_out"]
            # The splitter is connected to the HVAC preheater, the HVAC reheater, and the Hot water heater
            structure["systems"]["HTHR"]["units"]["HTHRsplit"]["flows"]["HRWater_PreH_out"]["Connections"] = ["HTHR" + ":" + "HVACpreheater" + ":" + "HRWater_in"]
            structure["systems"]["HTHR"]["units"]["HVACpreheater"]["flows"]["HRWater_in"]["Connections"] = ["HTHR" + ":" + "HTHRsplit" + ":" + "HRWater_PreH_out"]
            structure["systems"]["HTHR"]["units"]["HTHRsplit"]["flows"]["HRWater_ReH_out"]["Connections"] = ["HTHR" + ":" + "HVACreheater" + ":" + "HRWater_in"]
            structure["systems"]["HTHR"]["units"]["HVACreheater"]["flows"]["HRWater_in"]["Connections"] = ["HTHR" + ":" + "HTHRsplit" + ":" + "HRWater_ReH_out"]
            structure["systems"]["HTHR"]["units"]["HTHRsplit"]["flows"]["HRWater_HWH_out"]["Connections"] = ["HTHR" + ":" + "HotWaterHeater" + ":" + "HRWater_in"]
            structure["systems"]["HTHR"]["units"]["HotWaterHeater"]["flows"]["HRWater_in"]["Connections"] = ["HTHR" + ":" + "HTHRsplit" + ":" + "HRWater_HWH_out"]
            # After each of the three above, they are connected to the HTHR merge
            structure["systems"]["HTHR"]["units"]["HTHRmerge"]["flows"]["HRWater_PreH_in"]["Connections"] = ["HTHR" + ":" + "HVACpreheater" + ":" + "HRWater_out"]
            structure["systems"]["HTHR"]["units"]["HVACpreheater"]["flows"]["HRWater_out"]["Connections"] = ["HTHR" + ":" + "HTHRmerge" + ":" + "HRWater_PreH_in"]
            structure["systems"]["HTHR"]["units"]["HTHRmerge"]["flows"]["HRWater_ReH_in"]["Connections"] = ["HTHR" + ":" + "HVACreheater" + ":" + "HRWater_out"]
            structure["systems"]["HTHR"]["units"]["HVACreheater"]["flows"]["HRWater_out"]["Connections"] = ["HTHR" + ":" + "HTHRmerge" + ":" + "HRWater_ReH_in"]
            structure["systems"]["HTHR"]["units"]["HTHRmerge"]["flows"]["HRWater_HWH_in"]["Connections"] = ["HTHR" + ":" + "HotWaterHeater" + ":" + "HRWater_out"]
            structure["systems"]["HTHR"]["units"]["HotWaterHeater"]["flows"]["HRWater_out"]["Connections"] = ["HTHR" + ":" + "HTHRmerge" + ":" + "HRWater_HWH_in"]
            # The Outlet of each HTHR exchanger is connected to the

            ############    CENTRAL COOLING SYSTEMS  ##########
            # The LT water from the collector goes to the sea water cooler, for both engine rooms
            structure["systems"]["CoolingSystems"]["units"]["SWC13"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTcollector13" + ":" + "LTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["LTcollector13"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "SWC13" + ":" + "LTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["SWC24"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTcollector24" + ":" + "LTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["LTcollector24"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "SWC24" + ":" + "LTWater_in"]
            # The LT water from the sea water cooler goes to the LT distribution, for both engine rooms
            structure["systems"]["CoolingSystems"]["units"]["SWC13"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTdistribution13" + ":" + "LTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["LTdistribution13"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "SWC13" + ":" + "LTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["SWC24"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTdistribution24" + ":" + "LTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["LTdistribution24"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "SWC24" + ":" + "LTWater_out"]
            # The "HT" water from the LT collector goes into the LTHT merge
            structure["systems"]["CoolingSystems"]["units"]["LTHTmerge13"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTcollector13" + ":" + "HTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["LTcollector13"]["flows"]["HTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTHTmerge13" + ":" + "LTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["LTHTmerge24"]["flows"]["LTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "LTcollector24" + ":" + "HTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["LTcollector24"]["flows"]["HTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTHTmerge24" + ":" + "LTWater_in"]
            # The HT water from the HTsplit goes in the the LTHT merge
            structure["systems"]["CoolingSystems"]["units"]["LTHTmerge13"]["flows"]["HTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "HTsplit13" + ":" + "HTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["HTsplit13"]["flows"]["HTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTHTmerge13" + ":" + "HTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["LTHTmerge24"]["flows"]["HTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "HTsplit24" + ":" + "HTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["HTsplit24"]["flows"]["HTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "LTHTmerge24" + ":" + "HTWater_in"]
            # The LT water from the HTsplit goes directly to the SeaWater Cooler
            structure["systems"]["CoolingSystems"]["units"]["SWC13"]["flows"]["HTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "HTsplit13" + ":" + "LTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["HTsplit13"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "SWC13" + ":" + "HTWater_in"]
            structure["systems"]["CoolingSystems"]["units"]["SWC24"]["flows"]["HTWater_in"]["Connections"] = ["CoolingSystems" + ":" + "HTsplit24" + ":" + "LTWater_out"]
            structure["systems"]["CoolingSystems"]["units"]["HTsplit24"]["flows"]["LTWater_out"]["Connections"] = ["CoolingSystems" + ":" + "SWC24" + ":" + "HTWater_in"]
            ############    STEAM SYSTEMS  ##########
            # here we set the connection between the steam collector and the different steam generators
            # With the Auxiliary boiler 1
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_AB1_out"]["Connections"] = ["Steam" + ":" + "Boiler1" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["Boiler1"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_AB1_out"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_AB1_in"]["Connections"] = ["Steam" + ":" + "Boiler1" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["Boiler1"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_AB1_in"]
            # With the Auxiliary boiler 2
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_AB2_out"]["Connections"] = ["Steam" + ":" + "Boiler2" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["Boiler2"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_AB2_out"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_AB2_in"]["Connections"] = ["Steam" + ":" + "Boiler2" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["Boiler2"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_AB2_in"]
            # Now it's the turn of all consumers
            # Let's start with the Tank heating
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_TH_in"]["Connections"] = ["Steam" + ":" + "TankHeating" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["TankHeating"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_TH_in"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_TH_out"]["Connections"] = ["Steam" + ":" + "TankHeating" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["TankHeating"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_TH_out"]
            # Machinery Space Heating (MSH)
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_MSH_in"]["Connections"] = ["Steam" + ":" + "MachinerySpaceHeaters" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["MachinerySpaceHeaters"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_MSH_in"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_MSH_out"]["Connections"] = ["Steam" + ":" + "MachinerySpaceHeaters" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["MachinerySpaceHeaters"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_MSH_out"]
            # HFO Tank Heating (HTH)
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_HTH_in"]["Connections"] = ["Steam" + ":" + "HFOtankHeating" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["HFOtankHeating"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_HTH_in"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_HTH_out"]["Connections"] = ["Steam" + ":" + "HFOtankHeating" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["HFOtankHeating"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_HTH_out"]
            # HFO heater (HH)
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_HH_in"]["Connections"] = ["Steam" + ":" + "HFOheater" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["HFOheater"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_HH_in"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_HH_out"]["Connections"] = ["Steam" + ":" + "HFOheater" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["HFOheater"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_HH_out"]
            # Galley (G)
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_G_in"]["Connections"] = ["Steam" + ":" + "Galley" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["Galley"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_G_in"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_G_out"]["Connections"] = ["Steam" + ":" + "Galley" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["Galley"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_G_out"]
            # Other Tanks (OT)
            structure["systems"]["Steam"]["units"]["SteamCollector"]["flows"]["Steam_OT_in"]["Connections"] = ["Steam" + ":" + "OtherTanks" + ":" + "Steam_out"]
            structure["systems"]["Steam"]["units"]["OtherTanks"]["flows"]["Steam_out"]["Connections"] = ["Steam" + ":" + "SteamCollector" + ":" + "Steam_OT_in"]
            structure["systems"]["Steam"]["units"]["SteamDistribution"]["flows"]["Steam_OT_out"]["Connections"] = ["Steam" + ":" + "OtherTanks" + ":" + "Steam_in"]
            structure["systems"]["Steam"]["units"]["OtherTanks"]["flows"]["Steam_in"]["Connections"] = ["Steam" + ":" + "SteamDistribution" + ":" + "Steam_OT_out"]



    print("...done!")
    return structure


def generalStatus(processed, structure):
    print("Started initializing the --status-- dataset...", end="", flush=True)
    for system in structure["systems"]:
        onoff_ID = system + ":" + "on"
        load_ID = system + ":" + "load"
        processed[onoff_ID] = pd.Series(index=processed.index)
        processed[load_ID] = pd.Series(index=processed.index)
    print("...done!")
    return processed






