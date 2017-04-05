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
# --- Mech/El Power (Wdot)

# For physical flows, the following data Series are initiated:
# --- Inlet mass flow (mdot_in)
# --- Outlet mass flow (mdot_out)
# --- Inlet temperature (T_in)
# --- Outlet temperature (T_out)
# --- Inlet specific enthalpy (h_in)
# --- Outlet specific enthalpy (h_out)
# --- Specific heat (NOTE: CONSTANT, NOT A SERIES) (cp)

# For Heat flows, the following data Series are initiated:
# --- Heat flow (Qdot)    NOTE: I use the convention that the flow is POSITIVE if it is an INPUT
# --- Temperature (T)

# For Mechanical / Electric power flows, the following data series are initiated:
# --- Energy flow (Wdot)     NOTE: I use the convention that the flow is POSITIVE if it is an INPUT


import pandas as pd


def unitStructure():
    structure = {"ME1": {}, "ME2": {}, "ME3": {}, "ME4": {}, "AE1": {}, "AE2": {}, "AE3": {}, "AE4": {}, "Other": {}}
    for idx in structure.keys():
        if idx[1] == "E":  # This basically means that this operation is only done if the system is an engine
            structure[idx] = {"TC": {}, "CAC_HT": {}, "CAC_LT": {}, "LOC": {}, "JWC": {}, "Cyl": {}}
            structure[idx]["TC"] = {"Air": {"type": "PF"}, "EG": {"type": "PF"}}  # Turbocharger
            structure[idx]["BPvalve"] = {"Air": {"type": "PF"}}  # Bypass valve
            structure[idx]["WasteGate"] = {"EG": {"type": "PF"}}  # Waste gate
            structure[idx]["CAC_HT"] = {"Air": {"type": "PF"}, "HTwater": {"type": "PF"}}  # Charge air cooler, HT stage
            structure[idx]["CAC_LT"] = {"Air": {"type": "PF"}, "LTwater": {"type": "PF"}}  # Charge air cooler, LT stage
            structure[idx]["LOC"] = {"LubOil": {"type": "PF"}, "LTwater": {"type": "PF"}}  # Lubricating oil cooler
            structure[idx]["JWC_HT"] = {"QdotJW": {"type": "Qdot"}, "HTwater": {"type": "PF"}}  # Jacket water cooler
            # Cylinders
            structure[idx]["Cyl"] = {"Air": {"type": "PF"}, "HTwater": {"type": "PF"}, "Power": {"type": "Wdot"}}

            # Only auxiliary engines AND main engines 2/3 have the exhaust gas boiler
            if idx[0] == "A" or idx[2] == "2" or idx[2] == "3":
                # Heat recovery steam generator
                structure[idx]["HRSG"] = {"EG": {"type": "PF"}, "Steam": {"type": "PF"}}
        elif idx == "Other":
            structure[idx] = {"Boiler": {}, "SWC": {}, "LTCS": {}, "SWCS": {}}
            structure[idx]["Boiler"] = {"Air": {"type": "PF"}, "EG": {"type": "PF"}, "Steam": {"type": "PF"}}
            structure[idx]["SWC"] = {"SeaWater": {"type": "PF"}, "LTWater": {"type": "PF"}}
            structure[idx]["HTLTMixer"] = {"HTWater": {"type": "PF"}, "LTWater": {"type": "PF"}}
            structure[idx]["HTLTSplitter"] = {"HTWater": {"type": "PF"}, "LTWater": {"type": "PF"}}
        else:
            print("Error! There is an unrecognized element in the unit name structure at system level")
    return structure


def flowPreparation(structure, database_index):
    for system in structure:
        for unit in structure[system]:
            for flow in structure[system][unit]:
                if flow["type"] == "PF":
                    structure[system][unit][flow]["mdot_in"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["mdot_out"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["T_in"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["T_out"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["h_in"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["h_out"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["cp"] = 0
                elif flow["type"] == "Qdot":
                    structure[system][unit][flow]["Qdot_in"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["Qdot_out"] = pd.Series(index=database_index)
                    structure[system][unit][flow]["T"] = pd.Series(index=database_index)
    return structure
