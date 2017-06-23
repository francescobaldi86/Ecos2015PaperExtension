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
    structure = {"systems": {"ME1": {}, "ME2": {}, "ME3": {}, "ME4": {}, "AE1": {}, "AE2": {}, "AE3": {}, "AE4": {}, "Other": {}}}
    for system in structure["systems"]:
        structure["systems"][system]["equations"] = {}
        if system[1] == "E":  # This basically means that this operation is only done if the system is an engine
            structure["systems"][system]["units"] = {"Comp": {}, "Turbine": {}, "BPsplit": {}, "BPmerge": {}, "BPvalve": {},
                                                     "CAC_HT": {}, "CAC_LT": {}, "LOC": {}, "JWC": {}, "Cyl": {},
                                                     "HTsplit": {}, "HTmerge": {}, "LTsplit": {}}
            # Compressor
            structure["systems"][system]["units"]["Comp"]["flows"] = {"Air_in": {"type": "CPF"}, "Air_out": {"type": "CPF"}} # TC compressor
            structure["systems"][system]["units"]["Comp"]["equations"] = ["MassBalance"]
            # Bypass Split
            structure["systems"][system]["units"]["BPsplit"]["flows"] = {"Air_in": {"type": "CPF"}, "Air_out": {"type": "CPF"}, "BP_out": {"type": "CPF"}}  # Bypass valve
            structure["systems"][system]["units"]["BPsplit"]["equations"] = ["MassBalance", "ConstantPressure", "ConstantTemperature"]
            # Bypass Merge
            structure["systems"][system]["units"]["BPmerge"]["flows"] = {"EG_in": {"type": "CPF"}, "Mix_out": {"type": "CPF"}, "BP_in": {"type": "CPF"}}
            structure["systems"][system]["units"]["BPmerge"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Bypass Valve
            structure["systems"][system]["units"]["BPvalve"]["flows"] = {"BP_in": {"type": "CPF"}, "BP_out": {"type": "CPF"}}
            structure["systems"][system]["units"]["BPvalve"]["equations"] = ["MassBalance", "ConstantTemperature"]
            # Turbine
            structure["systems"][system]["units"]["Turbine"]["flows"] = {"Mix_in": {"type": "CPF"}, "Mix_out": {"type": "CPF"}}  # Turbocharger turbine
            structure["systems"][system]["units"]["Turbine"]["equations"] = ["MassBalance"]
            # Charge air cooler, HT side
            structure["systems"][system]["units"]["CAC_HT"]["flows"] = {"Air_in": {"type": "CPF"}, "HTWater_in": {"type": "IPF"},
                                        "Air_out": {"type": "CPF"}, "HTWater_out": {"type": "IPF"}}  # Charge air
            structure["systems"][system]["units"]["CAC_HT"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Charge air cooler, LT stage
            structure["systems"][system]["units"]["CAC_LT"]["flows"] = {"Air_in": {"type": "CPF"}, "LTWater_in": {"type": "IPF"},
                                        "Air_out": {"type": "CPF"}, "LTWater_out": {"type": "IPF"}}  # Charge air
            structure["systems"][system]["units"]["CAC_LT"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Lubricating oil cooler
            structure["systems"][system]["units"]["LOC"]["flows"] = {"LubOil_in": {"type": "IPF"}, "LTWater_in": {"type": "IPF"},
                                     "LubOil_out": {"type": "IPF"}, "LTWater_out": {"type": "IPF"}}  # Lubricating oil
            structure["systems"][system]["units"]["LOC"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Jacket water cooler
            structure["systems"][system]["units"]["JWC"]["flows"] = {"QdotJW_in": {"type": "Qdot"}, "HTWater_in": {"type": "IPF"},
                                                                    "HTWater_out": {"type": "IPF"}}  # Jacket water
            structure["systems"][system]["units"]["JWC"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Engine cylinders
            structure["systems"][system]["units"]["Cyl"]["flows"] = {"Air_in": {"type": "CPF"},  "FuelPh_in": {"type": "CPF"}, "EG_out": {"type":"CPF"},
                                     "Power_out": {"type": "Wdot"}, "FuelCh_in": {"type": "Wdot"}, "QdotJW_out": {"type":"Qdot"},
                                     "LubOil_in": {"type": "IPF"}, "LubOil_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["Cyl"]["equations"] = ["MassBalance"]
            # HT cooling systems split
            structure["systems"][system]["units"]["HTsplit"]["flows"] = {"HTWater_in": {"type": "IPF"}, "HTWater_out": {"type": "IPF"}, "LTWater_out": {"type": "IPF"}}  # Bypass valve
            structure["systems"][system]["units"]["HTsplit"]["equations"] = ["MassBalance", "ConstantPressure", "ConstantTemperature"]
            # HT cooling systems merge
            structure["systems"][system]["units"]["HTmerge"]["flows"] = {"HTWater_in": {"type": "IPF"}, "HTWater_out": {"type": "IPF"}, "LTWater_in": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTmerge"]["equations"] = ["MassBalance", "ConstantPressure"]
            # LT cooling systems split
            structure["systems"][system]["units"]["LTsplit"]["flows"] = {"LTWater_in": {"type": "IPF"}, "HTWater_out": {"type": "IPF"}, "LTWater_out": {"type": "IPF"}}  # Bypass valve
            structure["systems"][system]["units"]["LTsplit"]["equations"] = ["MassBalance", "ConstantPressure", "ConstantTemperature"]
            # Only auxiliary engines AND main engines 2/3 have the exhaust gas boiler
            if system[0] == "A" or system[2] == "2" or system[2] == "3":
                # Heat recovery steam generator
                structure["systems"][system]["units"].update({"HRSG": {}})
                structure["systems"][system]["units"]["HRSG"]["flows"] = {"Mix_in": {"type": "CPF"}, "Mix_out": {"type": "CPF"},
                                          "Steam_in": {"type": "CPF"}, "Steam_out": {"type": "CPF"}}
                structure["systems"][system]["units"]["HRSG"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Auxiliary engines also have electric generators connected
            if system[0] == "A":
                structure["systems"][system]["units"].update({"AG": {}})
                structure["systems"][system]["units"]["AG"]["flows"] = {"Power_in": {"type": "Wdot"}, "Power_out": {"type": "Wdot"}, "Losses": {"type": "Qdot"}}
                structure["systems"][system]["units"]["AG"]["equations"] = []
        elif system == "Other":
            structure["systems"][system]["units"] = {"Boiler": {}, "SWC13": {}, "SWC24": {},
                                                     "LTcollector13": {}, "LTcollector24": {}, "LTdistribution13": {}, "LTdistribution24": {}}
            # Auxiliary boiler
            structure["systems"][system]["units"]["Boiler"]["flows"] = {"Air_in": {"type": "CPF"}, "EG_out": {"type": "CPF"},
                                        "Steam_in": {"type": "CPF"}, "Steam_out": {"type": "CPF"}}
            structure["systems"][system]["units"]["Boiler"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Seawater cooler, ER 1/3
            structure["systems"][system]["units"]["SWC13"]["flows"] = {"SeaWater_in": {"type": "IPF"}, "LTWater_in": {"type": "IPF"},
                                     "SeaWater_out": {"type": "IPF"}, "LTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["SWC13"]["equations"] = ["MassBalance", "ConstantPressure"]
            # Seawater cooler, ER 2/4
            structure["systems"][system]["units"]["SWC24"]["flows"] = {"SeaWater_in": {"type": "IPF"}, "LTWater_in": {"type": "IPF"},
                                       "SeaWater_out": {"type": "IPF"}, "LTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["SWC24"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["LTcollector13"]["flows"] = {
                "LTWater_AE1_in": {"type": "IPF"}, "HTWater_AE1_in": {"type": "IPF"},
                "LTWater_AE3_in": {"type": "IPF"}, "HTWater_AE3_in": {"type": "IPF"},
                "LTWater_ME1_in": {"type": "IPF"}, "HTWater_ME1_in": {"type": "IPF"},
                "LTWater_ME3_in": {"type": "IPF"}, "HTWater_ME3_in": {"type": "IPF"},
                "LTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTcollector13"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["LTcollector24"]["flows"] = {
                "LTWater_AE2_in": {"type": "IPF"}, "HTWater_AE2_in": {"type": "IPF"},
                "LTWater_AE4_in": {"type": "IPF"}, "HTWater_AE4_in": {"type": "IPF"},
                "LTWater_ME2_in": {"type": "IPF"}, "HTWater_ME2_in": {"type": "IPF"},
                "LTWater_ME4_in": {"type": "IPF"}, "HTWater_ME4_in": {"type": "IPF"},
                "LTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTcollector24"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["LTdistribution13"]["flows"] = {
                "LTWater_in": {"type": "IPF"},
                "LTWater_AE3_out": {"type": "IPF"}, "LTWater_AE1_out": {"type": "IPF"},
                "LTWater_ME1_out": {"type": "IPF"}, "LTWater_ME3_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTdistribution13"]["equations"] = ["MassBalance", "ConstantPressure"]
            structure["systems"][system]["units"]["LTdistribution24"]["flows"] = {
                "LTWater_in": {"type": "IPF"},
                "LTWater_AE2_out": {"type": "IPF"}, "LTWater_AE4_out": {"type": "IPF"},
                "LTWater_ME2_out": {"type": "IPF"}, "LTWater_ME4_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["LTdistribution24"]["equations"] = ["MassBalance", "ConstantPressure"]
            # HT - LT central mixer
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
            elif any(x in unit for x in {"split", "merge", "distribution", "collector"}):
                streams["Total"] = []
                for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                    #if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] == "CPF":
                    streams["Total"].append(d2df(system, unit, flow, ""))
            else:
                for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                    if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] in {"CPF", "IPF"}:
                        temp = flow.split(sep="_")
                        if temp[0] not in streams:
                            streams[temp[0]] = [d2df(system, unit, flow, "")]
                        elif temp[0] in streams:
                            streams[temp[0]].append(d2df(system, unit, flow, ""))
                        else:
                            print("Something very weird happened")
            dict_structure["systems"][system]["units"][unit]["streams"] = streams
    return dict_structure



def flowPreparation(structure, database_index, CONSTANTS):
    print("Start preparing the Pandas dataframe with all inputs...", end="")
    structure["property_list"] = []
    dataframe = pd.DataFrame(index=database_index)
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
                    dataframe[flow_ID] = pd.Series(index=database_index)
    print("...done!")
    return (structure, dataframe)


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
            # The other inlet of the HT water merge is from the "hotter" side of the LT water
            structure["systems"][system]["units"]["HTmerge"]["flows"]["LTWater_in"]["Connections"] = [system + ":" + "LTsplit" + ":" + "HTWater_out"]
            structure["systems"][system]["units"]["LTsplit"]["flows"]["HTWater_out"]["Connections"] = [system + ":" + "HTmerge" + ":" + "LTWater_in"]
            # The LOC outlet goes into the LTsplit
            structure["systems"][system]["units"]["LOC"]["flows"]["LTWater_out"]["Connections"] = [system + ":" + "LTsplit" + ":" + "LTWater_in"]
            structure["systems"][system]["units"]["LTsplit"]["flows"]["LTWater_in"]["Connections"] = [system + ":" + "LOC" + ":" + "LTWater_out"]
            # Inserting connections to the central components: LT collector and LT splitter. Separated for different engine rooms
            if system[2] in {"1","3"}:
                # HT water from the HT splitter goes into the LT collector
                structure["systems"][system]["units"]["HTsplit"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "LTcollector13" + ":" + "HTWater_"+system+"_in"]
                structure["systems"]["Other"]["units"]["LTcollector13"]["flows"]["HTWater_"+system+"_in"]["Connections"] = [system + ":" + "HTsplit" + ":" + "LTWater_out"]
                # LT water from the LT split goes into the LT collector
                structure["systems"][system]["units"]["LTsplit"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "LTcollector13" + ":" + "LTWater_"+system+"_in"]
                structure["systems"]["Other"]["units"]["LTcollector13"]["flows"]["LTWater_"+system+"_in"]["Connections"] = [system + ":" + "LTsplit" + ":" + "LTWater_out"]
                # LT water from the LT distribution goes into the charge air cooler
                structure["systems"]["Other"]["units"]["LTdistribution13"]["flows"]["LTWater_"+system+"_out"]["Connections"] = [system + ":" + "CAC_LT" + ":" + "LTWater_in"]
                structure["systems"][system]["units"]["CAC_LT"]["flows"]["LTWater_in"]["Connections"] = ["Other" + ":" + "LTdistribution13" + ":" + "LTWater_"+system+"_out"]
            if system[2] in {"2", "4"}:
                # HT water from the HT splitter goes into the LT collector
                structure["systems"][system]["units"]["HTsplit"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "LTcollector24" + ":" + "HTWater_" + system + "_in"]
                structure["systems"]["Other"]["units"]["LTcollector24"]["flows"]["HTWater_" + system + "_in"]["Connections"] = [system + ":" + "HTsplit" + ":" + "LTWater_out"]
                # LT water from the LT split goes into the LT collector
                structure["systems"][system]["units"]["LTsplit"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "LTcollector24" + ":" + "LTWater_" + system + "_in"]
                structure["systems"]["Other"]["units"]["LTcollector24"]["flows"]["LTWater_" + system + "_in"]["Connections"] = [system + ":" + "LTsplit" + ":" + "LTWater_out"]
                # LT water from the LT distribution goes into the charge air cooler
                structure["systems"]["Other"]["units"]["LTdistribution24"]["flows"]["LTWater_" + system + "_out"]["Connections"] = [system + ":" + "CAC_LT" + ":" + "LTWater_in"]
                structure["systems"][system]["units"]["CAC_LT"]["flows"]["LTWater_in"]["Connections"] = ["Other" + ":" + "LTdistribution24" + ":" + "LTWater_" + system + "_out"]
            if system[0] == "A" or system[2] == "2" or system[2] == "3":
                # The HRSG inlet is connected to the engine turbine outlet
                structure["systems"][system]["units"]["HRSG"]["flows"]["Mix_in"]["Connections"] = [system + ":" + "Turbine" + ":" + "Mix_out"]
                structure["systems"][system]["units"]["Turbine"]["flows"]["Mix_out"]["Connections"] = [system + ":" + "HRSG" + ":" + "Mix_in"]
            if system[0] == "A":
                structure["systems"][system]["units"]["AG"]["flows"]["Power_in"]["Connections"] = [system + ":" + "Cyl" + ":" + "Power_out"]
                structure["systems"][system]["units"]["Cyl"]["flows"]["Power_out"]["Connections"] = [system + ":" + "AG" + ":" + "Power_in"]
        elif system == "Other":
            # The LT water from the collector goes to the sea water cooler, for both engine rooms
            structure["systems"]["Other"]["units"]["SWC13"]["flows"]["LTWater_in"]["Connections"] = ["Other" + ":" + "LTcollector13" + ":" + "LTWater_out"]
            structure["systems"]["Other"]["units"]["LTcollector13"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "SWC13" + ":" + "LTWater_in"]
            structure["systems"]["Other"]["units"]["SWC24"]["flows"]["LTWater_in"]["Connections"] = ["Other" + ":" + "LTcollector24" + ":" + "LTWater_out"]
            structure["systems"]["Other"]["units"]["LTcollector24"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "SWC24" + ":" + "LTWater_in"]
            # The LT water from the sea water cooler goes to the LT distribution, for both engine rooms
            structure["systems"]["Other"]["units"]["SWC13"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "LTdistribution13" + ":" + "LTWater_in"]
            structure["systems"]["Other"]["units"]["LTdistribution13"]["flows"]["LTWater_in"]["Connections"] = ["Other" + ":" + "SWC13" + ":" + "LTWater_out"]
            structure["systems"]["Other"]["units"]["SWC24"]["flows"]["LTWater_out"]["Connections"] = ["Other" + ":" + "LTdistribution24" + ":" + "LTWater_in"]
            structure["systems"]["Other"]["units"]["LTdistribution24"]["flows"]["LTWater_in"]["Connections"] = ["Other" + ":" + "SWC24" + ":" + "LTWater_out"]
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






