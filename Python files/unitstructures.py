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


def flowStructure():
    structure = {"ME1": {}, "ME2": {}, "ME3": {}, "ME4": {}, "AE1": {}, "AE2": {}, "AE3": {}, "AE4": {}, "Other": {}}
    for idx in structure.keys():
        if idx[1] == "E":  # This basically means that this operation is only done if the system is an engine
            structure[idx] = {"TC": {}, "CAC_HT": {}, "CAC_LT": {}, "LOC": {}, "JWC": {}, "Cyl": {}}
            structure[idx]["Comp"] = {"Air_in": {"type": "CPF"}, "Air_out": {"type": "CPF"}} # TC compressor
            structure[idx]["BPsplit"] = {"Air_in": {"type": "CPF"}, "Air_out": {"type": "CPF"}, "Air_BP_out": {"type": "CPF"}}  # Bypass valve
            structure[idx]["BPmerge"] = {"EG_in": {"type": "CPF"}, "Mix_out": {"type": "CPF"}, "Air_BP_in": {"type": "CPF"}}
            structure[idx]["Turbine"] = {"Mix_in": {"type": "CPF"}, "Mix_out": {"type": "CPF"}}  # Turbocharger turbine
            # structure[idx]["WasteGate"] = {"EG_in": {"type": "CPF"},"EG_out": {"type": "CPF"}}  # Waste gate
            structure[idx]["CAC_HT"] = {"Air_in": {"type": "CPF"}, "HTWater_in": {"type": "IPF"},
                                        "Air_out": {"type": "CPF"}, "HTWater_out": {"type": "IPF"}}  # Charge air
            # cooler, HT stage
            structure[idx]["CAC_LT"] = {"Air_in": {"type": "CPF"}, "LTWater_in": {"type": "IPF"},
                                        "Air_out": {"type": "CPF"}, "LTWater_out": {"type": "IPF"}}  # Charge air
            # cooler, LT stage
            structure[idx]["LOC"] = {"LubOil_in": {"type": "IPF"}, "LTWater_in": {"type": "IPF"},
                                     "LubOil_out": {"type": "IPF"}, "LTWater_out": {"type": "IPF"}}  # Lubricating oil
            # cooler
            structure[idx]["JWC"] = {"QdotJW_in": {"type": "Qdot"}, "HTWater_in": {"type": "IPF"},
                                                                    "HTWater_out": {"type": "IPF"}}  # Jacket water
            # cooler Cylinders
            structure[idx]["Cyl"] = {"Air_in": {"type": "CPF"},  "FuelPh_in": {"type": "IPF"}, "EG_out": {"type":"CPF"},
                                     "Power_out": {"type": "Wdot"}, "FuelCh_in": {"type": "Wdot"}, "QdotJW_out": {"type":"Qdot"},
                                     "LubOil_in": {"type": "IPF"}, "LubOil_out": {"type": "IPF"}}
            # Only auxiliary engines AND main engines 2/3 have the exhaust gas boiler
            if idx[0] == "A" or idx[2] == "2" or idx[2] == "3":
                # Heat recovery steam generator
                structure[idx]["HRSG"] = {"Mix_in": {"type": "CPF"}, "Mix_out": {"type": "CPF"},
                                          "Steam_in": {"type": "CPF"}, "Steam_out": {"type": "CPF"}}
            # Auxiliary engines also have electric generators connected
            if idx[0] == "A":
                structure[idx]["AG"] = {"Power_in": {"type": "Wdot"}, "Power_out": {"type": "Wdot"}, "Losses": {"type": "Qdot"}}
        elif idx == "Other":
            structure[idx] = {"Boiler": {}, "SWC": {}, "LTCS": {}, "SWCS": {}}
            structure[idx]["Boiler"] = {"Air_in": {"type": "CPF"}, "EG_out": {"type": "CPF"},
                                        "Steam_in": {"type": "CPF"}, "Steam_out": {"type": "CPF"}}
            structure[idx]["SWC"] = {"SeaWater_in": {"type": "IPF"}, "LTWater_in": {"type": "IPF"},
                                     "SeaWater_out": {"type": "IPF"}, "LTWater_out": {"type": "IPF"}}
            structure[idx]["HTLTMixer"] = {"HTWater_in": {"type": "IPF"}, "LTWater_in": {"type": "IPF"},
                                           "HTWater_out": {"type": "IPF"}}
            structure[idx]["HTLTSplitter"] = {"HTWater_in": {"type": "IPF"}, "LTWater_out": {"type": "IPF"},
                                              "HTWater_out": {"type": "IPF"}}
        else:
            print("Error! There is an unrecognized element in the unit name structure at system level")
    return structure


def flowPreparation(structure, database_index, CONSTANTS):
    for system in structure:
        for unit in structure[system]:
            for flow in structure[system][unit]:
                structure[system][unit][flow]["ID"] = system + unit + flow
                for property in CONSTANTS["General"]["PROPERTY_LIST"][flow["type"]]:
                    structure[system][unit][flow][property] = pd.Series(index=database_index)
    return structure


def connectionAssignment(structure):
    for name in structure.keys():
        if name[1] == "E":  # This basically means that this operation is only done if the system is an engine
            # The compressor is connected to the BP valve
            structure[name]["Comp"]["Air_out"]["Connections"] = name + ":" + "BPsplit" + ":" + "Air_in"
            structure[name]["BPsplit"]["Air_in"]["Connections"] = name + ":" + "Comp" + ":" + "Air_out"
            # The BP valve is connected to the CAC-HT cooler
            structure[name]["CAC-HT"]["Air_in"]["Connections"] = name + ":" + "BPsplit" + ":" + "Air_out"
            structure[name]["BPsplit"]["Air_out"]["Connections"] = name + ":" + "CAC-HT" + ":" + "Air_in"
            # The CAC-HT cooler is connected to the CAC-LT cooler
            structure[name]["CAC-HT"]["Air_out"]["Connections"] = name + ":" + "CAC-LT" + ":" + "Air_in"
            structure[name]["CAC-LT"]["Air_in"]["Connections"] = name + ":" + "CAC-HT" + ":" + "Air_out"
            # The CAC-LT cooler is connected to the Cylinder inlet manifold
            structure[name]["Cyl"]["Air_in"]["Connections"] = name + ":" + "CAC-LT" + ":" + "Air_out"
            structure[name]["CAC-LT"]["Air_out"]["Connections"] = name + ":" + "Cyl" + ":" + "Air_in"
            # The cylinder exhaust manifold is connected to the BP valve
            structure[name]["BPmerge"]["EG_in"]["Connections"] = name + ":" + "Cyl" + ":" + "EG_out"
            structure[name]["Cyl"]["EG_out"]["Connections"] = name + ":" + "BPmerge" + ":" + "EG_in"
            # The turbine is connected to the BP valve
            structure[name]["Turbine"]["Mix_in"]["Connections"] = name + ":" + "BPmerge" + ":" + "Mix_out"
            structure[name]["BPmerge"]["Mix_out"]["Connections"] = name + ":" + "Turbine" + ":" + "Mix_in"
            # The CAC-LT cooler water is connected to the LOC
            structure[name]["LOC"]["LTWater_in"]["Connections"] = name + ":" + "CAC-LT" + ":" + "LTWater_out"
            structure[name]["CAC-LT"]["LTWater_out"]["Connections"] = name + ":" + "LOC" + ":" + "LTWater_in"
            # The CAC-HT cooler water is connected to the JWC
            structure[name]["CAC-HT"]["HTWater_in"]["Connections"] = name + ":" + "JWC" + ":" + "HTWater_out"
            structure[name]["JWC"]["HTWater_out"]["Connections"] = name + ":" + "CAC-HT" + ":" + "HTWater_in"
            if idx[0] == "A" or idx[2] == "2" or idx[2] == "3":
                # The HRSG inlet is connected to the engine turbine outlet
                structure[name]["HRSG"]["Mix_in"]["Connections"] = name + ":" + "Turbine" + ":" + "Mix_out"
                structure[name]["Turbine"]["Mix_out"]["Connections"] = name + ":" + "HRSG" + ":" + "Mix_in"
            if idx[0] == "A":
                structure[name]["AG"]["Power_in"]["Connections"] = name + ":" + "Cyl" + ":" + "Power_out"
                structure[name]["Cyl"]["Power_out"]["Connections"] = name + ":" + "AG" + ":" + "Power_in"
    return structure


def generalStatus():
    structure = {"ME1": {}, "ME2": {}, "ME3": {}, "ME4": {}, "AE1": {}, "AE2": {}, "AE3": {}, "AE4": {}, "Boiler": {}}
    for idx in structure.keys():
        # Adding the load and the "on/off"
        structure[idx] = {"Load": {}, "OnOff": {}}
    return structure






