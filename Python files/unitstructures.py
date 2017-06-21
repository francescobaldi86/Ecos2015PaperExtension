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

def structurePreparation(CONSTANTS, index, empty_dataset_filename, data_structure_preparation):
    dict_structure = flowStructure()  # Here we initiate the structure fields

    try:
        processed = pd.read_hdf(empty_dataset_filename, 'empty_dataset')
        if data_structure_preparation == "no":
            dict_structure = flowPreparationSimplified(dict_structure, index, CONSTANTS)
        elif data_structure_preparation == "yes":
            os.remove(empty_dataset_filename)
        else:
            print("The data_structure_preparation value should either be yes or no")
    except FileNotFoundError:
        (dict_structure, processed) = flowPreparation(dict_structure, index, CONSTANTS)  # Here we create the appropriate empty data series for each field
        processed.to_hdf(empty_dataset_filename, "empty_dataset", format='fixed', mode='w')
    dict_structure = streamsAssignment(dict_structure)
    dict_structure = connectionAssignment(dict_structure)
    processed = generalStatus(processed, dict_structure)  # Here we simply initiate the "status" structure
    return dict_structure, processed


def flowStructure():
    print("Started preparing the dataset_processed multi-level dictionary...", end="")
    structure = {"systems": {"ME1": {}, "ME2": {}, "ME3": {}, "ME4": {}, "AE1": {}, "AE2": {}, "AE3": {}, "AE4": {}, "Other": {}}}
    for system in structure["systems"]:
        structure["systems"][system]["equations"] = {}
        if system[1] == "E":  # This basically means that this operation is only done if the system is an engine
            structure["systems"][system]["units"] = {"Comp": {}, "Turbine": {}, "BPsplit": {}, "BPmerge": {}, "BPvalve": {},
                                                     "CAC_HT": {}, "CAC_LT": {}, "LOC": {}, "JWC": {}, "Cyl": {}}
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
            # Only auxiliary engines AND main engines 2/3 have the exhaust gas boiler
            if system[0] == "A" or system[2] == "2" or system[2] == "3":
                # Heat recovery steam generator
                structure["systems"][system]["units"].update({"HRSG": {}})
                structure["systems"][system]["units"]["HRSG"]["flows"] = {"Mix_in": {"type": "CPF"}, "Mix_out": {"type": "CPF"},
                                          "Steam_in": {"type": "CPF"}, "Steam_out": {"type": "CPF"}}
                structure["systems"][system]["units"]["HRSG"]["equations"] = ["MassBalance", "ConstantPressure", "ConstantTemperature"]
            # Auxiliary engines also have electric generators connected
            if system[0] == "A":
                structure["systems"][system]["units"].update({"AG": {}})
                structure["systems"][system]["units"]["AG"]["flows"] = {"Power_in": {"type": "Wdot"}, "Power_out": {"type": "Wdot"}, "Losses": {"type": "Qdot"}}
                structure["systems"][system]["units"]["AG"]["equations"] = []
        elif system == "Other":
            structure["systems"][system]["units"] = {"Boiler": {}, "SWC13": {}, "SWC24": {}, "HTLTMixer":{}, "HTLTSplitter": {}}
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
            # HT - LT central mixer
            structure["systems"][system]["units"]["HTLTMixer"]["flows"] = {"HTWater_in": {"type": "IPF"}, "LTWater_in": {"type": "IPF"},
                                           "HTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTLTMixer"]["equations"] = ["MassBalance", "ConstantPressure"]
            # HT - LT central splitter
            structure["systems"][system]["units"]["HTLTSplitter"]["flows"] = {"HTWater_in": {"type": "IPF"}, "LTWater_out": {"type": "IPF"},
                                              "HTWater_out": {"type": "IPF"}}
            structure["systems"][system]["units"]["HTLTSplitter"]["equations"] = ["MassBalance", "ConstantPressure"]
        else:
            print("Error! There is an unrecognized element in the unit name structure at system level")
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
            elif "BP" in unit:
                streams["Total"] = []
                for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                    if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] == "CPF":
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
    print("Start preparing the Pandas dataframe with all inputs...", end="")
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
    print("Start assigning connections between components...", end="")
    for name in structure["systems"]:
        if name[1] == "E":  # This basically means that this operation is only done if the system is an engine
            # The compressor is connected to the BP valve
            structure["systems"][name]["units"]["Comp"]["flows"]["Air_out"]["Connections"] = [name + ":" + "BPsplit" + ":" + "Air_in"]
            structure["systems"][name]["units"]["BPsplit"]["flows"]["Air_in"]["Connections"] = [name + ":" + "Comp" + ":" + "Air_out"]
            # The BP valve is connected to the CAC-HT cooler
            structure["systems"][name]["units"]["CAC_HT"]["flows"]["Air_in"]["Connections"] = [name + ":" + "BPsplit" + ":" + "Air_out"]
            structure["systems"][name]["units"]["BPsplit"]["flows"]["Air_out"]["Connections"] = [name + ":" + "CAC_HT" + ":" + "Air_in"]
            # The CAC-HT cooler is connected to the CAC-LT cooler
            structure["systems"][name]["units"]["CAC_HT"]["flows"]["Air_out"]["Connections"] = [name + ":" + "CAC_LT" + ":" + "Air_in"]
            structure["systems"][name]["units"]["CAC_LT"]["flows"]["Air_in"]["Connections"] = [name + ":" + "CAC_HT" + ":" + "Air_out"]
            # The CAC-LT cooler is connected to the Cylinder inlet manifold
            structure["systems"][name]["units"]["Cyl"]["flows"]["Air_in"]["Connections"] = [name + ":" + "CAC_LT" + ":" + "Air_out"]
            structure["systems"][name]["units"]["CAC_LT"]["flows"]["Air_out"]["Connections"] = [name + ":" + "Cyl" + ":" + "Air_in"]
            # The cylinder exhaust manifold is connected to the BP valve
            structure["systems"][name]["units"]["BPmerge"]["flows"]["EG_in"]["Connections"] = [name + ":" + "Cyl" + ":" + "EG_out"]
            structure["systems"][name]["units"]["Cyl"]["flows"]["EG_out"]["Connections"] = [name + ":" + "BPmerge" + ":" + "EG_in"]
            # The turbine is connected to the BP valve
            structure["systems"][name]["units"]["Turbine"]["flows"]["Mix_in"]["Connections"] = [name + ":" + "BPmerge" + ":" + "Mix_out"]
            structure["systems"][name]["units"]["BPmerge"]["flows"]["Mix_out"]["Connections"] = [name + ":" + "Turbine" + ":" + "Mix_in"]
            # The CAC-LT cooler water is connected to the LOC
            structure["systems"][name]["units"]["LOC"]["flows"]["LTWater_in"]["Connections"] = [name + ":" + "CAC_LT" + ":" + "LTWater_out"]
            structure["systems"][name]["units"]["CAC_LT"]["flows"]["LTWater_out"]["Connections"] = [name + ":" + "LOC" + ":" + "LTWater_in"]
            # The CAC-HT cooler water is connected to the JWC
            structure["systems"][name]["units"]["CAC_HT"]["flows"]["HTWater_in"]["Connections"] = [name + ":" + "JWC" + ":" + "HTWater_out"]
            structure["systems"][name]["units"]["JWC"]["flows"]["HTWater_out"]["Connections"] = [name + ":" + "CAC_HT" + ":" + "HTWater_in"]
            # The oil out from the lub oil cooler is connected to the engine inlet, and vice versa
            structure["systems"][name]["units"]["LOC"]["flows"]["LubOil_in"]["Connections"] = [name + ":" + "Cyl" + ":" + "LubOil_out"]
            structure["systems"][name]["units"]["Cyl"]["flows"]["LubOil_out"]["Connections"] = [name + ":" + "LOC" + ":" + "LubOil_in"]
            structure["systems"][name]["units"]["LOC"]["flows"]["LubOil_out"]["Connections"] = [name + ":" + "Cyl" + ":" + "LubOil_in"]
            structure["systems"][name]["units"]["Cyl"]["flows"]["LubOil_in"]["Connections"] = [name + ":" + "LOC" + ":" + "LubOil_out"]
            # The BP split is also connected to the BP merge
            structure["systems"][name]["units"]["BPsplit"]["flows"]["BP_out"]["Connections"] = [name + ":" + "BPvalve" + ":" + "BP_in"]
            structure["systems"][name]["units"]["BPvalve"]["flows"]["BP_in"]["Connections"] = [name + ":" + "BPsplit" + ":" + "BP_out"]
            structure["systems"][name]["units"]["BPmerge"]["flows"]["BP_in"]["Connections"] = [name + ":" + "BPvalve" + ":" + "BP_out"]
            structure["systems"][name]["units"]["BPvalve"]["flows"]["BP_out"]["Connections"] = [name + ":" + "BPmerge" + ":" + "BP_in"]
            if name[0] == "A" or name[2] == "2" or name[2] == "3":
                # The HRSG inlet is connected to the engine turbine outlet
                structure["systems"][name]["units"]["HRSG"]["flows"]["Mix_in"]["Connections"] = [name + ":" + "Turbine" + ":" + "Mix_out"]
                structure["systems"][name]["units"]["Turbine"]["flows"]["Mix_out"]["Connections"] = [name + ":" + "HRSG" + ":" + "Mix_in"]
            if name[0] == "A":
                structure["systems"][name]["units"]["AG"]["flows"]["Power_in"]["Connections"] = [name + ":" + "Cyl" + ":" + "Power_out"]
                structure["systems"][name]["units"]["Cyl"]["flows"]["Power_out"]["Connections"] = [name + ":" + "AG" + ":" + "Power_in"]
    print("...done!")
    return structure


def generalStatus(processed, structure):
    print("Started initializing the --status-- dataset...", end="")
    for system in structure["systems"]:
        onoff_ID = system + ":" + "on"
        load_ID = system + ":" + "load"
        processed[onoff_ID] = pd.Series(index=processed.index)
        processed[load_ID] = pd.Series(index=processed.index)
    print("...done!")
    return processed






