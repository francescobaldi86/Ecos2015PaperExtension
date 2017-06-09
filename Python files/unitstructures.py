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
            structure[idx]["TC"] = {"Air_in": {"type": "CPF"}, "EG_in": {"type": "CPF"},
                                    "Air_out": {"type": "CPF"}, "EG_out": {"type": "CPF"}}  # Turbocharger
            structure[idx]["Comp"] = {"Air_in": {"type": "CPF"}, "Air_out": {"type": "CPF"}} # TC compressor
            structure[idx]["BPvalve"] = {"Air_in": {"type": "CPF"}, "Air_out": {"type": "CPF"}}  # Bypass valve
            structure[idx]["Turbine"] = {"EG_in": {"type": "CPF"}, "EG_out": {"type": "CPF"}}  # Turbocharger turbine
            structure[idx]["WasteGate"] = {"EG_in": {"type": "CPF"},"EG_out": {"type": "CPF"}}  # Waste gate
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
                structure[idx]["HRSG"] = {"EG_in": {"type": "CPF"}, "EG_out": {"type": "CPF"},
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


def flowPreparation(structure, database_index):
    for system in structure:
        for unit in structure[system]:
            for flow in structure[system][unit]:
                if structure[system][unit][flow]["type"] == "IPF": # Incompressible physical energy flow
                    structure[system][unit][flow]["mdot"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["T"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["cp"] = 0  # Note that the CP is a fixed, individual value
                elif structure[system][unit][flow]["type"] == "CPF": # Compressible physical energy flow
                    structure[system][unit][flow]["mdot"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["T"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["h"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["h0"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["p"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["s"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["s0"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["cp"] = 0  # Note that the CP is a fixed, individual value
                elif structure[system][unit][flow]["type"] == "Qdot": # Heat flow
                    structure[system][unit][flow]["Qdot"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["T"] = pd.Series(index=database_index)
                elif structure[system][unit][flow]["type"] == "Wdot": # Work flow
                    structure[system][unit][flow]["Wdot"] = pd.Series(index=database_index) # in KW
                    structure[system][unit][flow]["omega"] = pd.Series(index=database_index) # In rpm
                    # Note that Wdot flows apply to chemical, electrical and mechanical power
                else:
                    print("Error, input type not recognized")
                structure[system][unit][flow]["Edot"] = pd.Series(index=database_index) # Energy flow
                structure[system][unit][flow]["Bdot"] = pd.Series(index=database_index) # Exergy flow

    return structure



def generalStatus():
    structure = {"ME1": {}, "ME2": {}, "ME3": {}, "ME4": {}, "AE1": {}, "AE2": {}, "AE3": {}, "AE4": {}, "Boiler": {}}
    for idx in structure.keys():
        # Adding the load and the "on/off"
        structure[idx] = {"Load": {}, "OnOff": {}}
    return structure



