# Temporarily empty
import CoolProp.CoolProp as cp
import numpy as np
import pandas as pd
import preprocessingO as ppo
from helpers import d2df

def propertyCalculator(processed, dict_structure, CONSTANTS):
    print("Started calculating flow properties...")
    df_index = processed.index
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                if dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] == "CPF":
                    # Only doing the calculations if the values for p and T are not NaN
                    if (processed[d2df(system,unit,flow,"p")].isnull().sum() == 0) & (processed[d2df(system,unit,flow,"T")].isnull().sum() == 0):
                        press = processed[d2df(system,unit,flow,"p")]  # .values()
                        temp = processed[d2df(system,unit,flow,"T")]  # .values()
                        # If the specific enthalpy is available already, it needs to be calculated
                        if ("Air" in flow) or ("BP" in flow):
                            print("Calculating properties for " + system + "_" + unit + "_" + flow)
                            # dh = pd.Series(cp.PropsSI('H','T',np.array(temp),'P',np.array(press), 'Air.mix'), index=df_index) - pd.Series(cp.PropsSI('H', 'T', np.array(processed["T_0"]), 'P', CONSTANTS["General"]["P_ATM"], 'Air.mix'), index=df_index)
                            # ds = pd.Series(cp.PropsSI('S', 'T', np.array(temp), 'P', np.array(press), 'Air.mix'), index=df_index) - pd.Series(cp.PropsSI('S', 'T', np.array(processed["T_0"]), 'P', CONSTANTS["General"]["P_ATM"], 'Air.mix'), index=df_index)
                            dh = pd.Series(enthalpyCalculator(np.array(temp), CONSTANTS), index=df_index) - pd.Series(enthalpyCalculator(np.array(processed["T_0"]), CONSTANTS), index=df_index)
                            ds = pd.Series(entropyCalculator(np.array(temp), CONSTANTS), index=df_index) - pd.Series(entropyCalculator(np.array(processed["T_0"]), CONSTANTS),index=df_index)
                            dh.loc[~processed[system + ":on"]] = 0
                            ds.loc[~processed[system + ":on"]] = 0
                        elif ("Mix" in flow) or ("EG" in flow):
                            #dh = pd.Series(index=processed.index)
                            #ds = pd.Series(index=processed.index)
                            mixture = ppo.mixtureCompositionNew(
                                processed[d2df(system,unit,flow,"mdot")],
                                processed[d2df(system,"Cyl","FuelPh_in","mdot")],
                                processed[d2df(system, "Cyl", "FuelPh_in", "T")],
                                CONSTANTS)
                            dh = pd.Series(enthalpyCalculator(np.array(temp), CONSTANTS, mixture), index=df_index) - pd.Series(
                                enthalpyCalculator(np.array(processed["T_0"]), CONSTANTS, mixture), index=df_index)
                            ds = pd.Series(entropyCalculator(np.array(temp), CONSTANTS, mixture), index=df_index) - pd.Series(
                                entropyCalculator(np.array(processed["T_0"]), CONSTANTS, mixture), index=df_index)
                            # for idx in dh.index:
                            #     if "Mix" in flow:
                            #         mixture = processed[system+":Mix_Composition"][idx]
                            #     else:
                            #         mixture = processed[system + ":EG_Composition"][idx]
                            #     if processed[system + ":on"][idx]:
                            #         #dh.loc[idx] = cp.PropsSI('H', 'T', temp[idx], 'P', press[idx], mixture) - cp.PropsSI('H', 'T', processed["T_0"][idx], 'P', CONSTANTS["General"]["P_ATM"], mixture)
                            #         #ds.loc[idx] = cp.PropsSI('S', 'T', temp[idx], 'P', press[idx], mixture) - cp.PropsSI('S', 'T', processed["T_0"][idx], 'P', CONSTANTS["General"]["P_ATM"], mixture)
                            #         dh.loc[idx] = cp.PropsSI('H', 'T', temp[idx], 'P', press[idx], mixture) - cp.PropsSI('H', 'T', CONSTANTS["General"]["T_STANDARD"], 'P', CONSTANTS["General"]["P_ATM"], mixture)
                            #         ds.loc[idx] = cp.PropsSI('S', 'T', temp[idx], 'P', press[idx], mixture) - cp.PropsSI('S', 'T', CONSTANTS["General"]["T_STANDARD"], 'P', CONSTANTS["General"]["P_ATM"], mixture)
                            #     else:
                            #         dh.loc[idx] = 0
                            #         ds.loc[idx] = 0
                            dh = dh * (temp - processed["T_0"]) / (temp - CONSTANTS["General"]["T_STANDARD"])
                            ds = ds * np.log(temp / processed["T_0"]) / np.log((temp - CONSTANTS["General"]["T_STANDARD"]))
                        elif "Steam" in flow:
                            if "in" in flow:
                                dh = CONSTANTS["Steam"]["DH_STEAM"] + CONSTANTS["General"]["CP_WATER"] * (processed[d2df(system, unit, flow, "T")] - processed["T_0"])
                                ds = CONSTANTS["Steam"]["DS_STEAM"] + CONSTANTS["General"]["CP_WATER"] * np.log((processed[d2df(system, unit, flow, "T")] / processed["T_0"]))
                            elif "out" in flow:
                                dh = CONSTANTS["General"]["CP_WATER"] * (processed[d2df(system, unit, flow, "T")] - processed["T_0"])
                                ds = CONSTANTS["General"]["CP_WATER"] * np.log((processed[d2df(system, unit, flow, "T")] / processed["T_0"]))
                    else:
                        print("Couldn't calculate the properies for the {} flow, didn't have all what I needed".format(system+":"+unit+":"+flow))
                    processed[d2df(system, unit, flow, "h")] = dh
                    processed[d2df(system, unit, flow, "b")] = dh - processed["T_0"] * ds
                    processed[d2df(system, unit, flow, "Edot")] = processed[d2df(system, unit, flow, "mdot")] * processed[d2df(system, unit, flow, "h")]
                    processed[d2df(system, unit, flow, "Bdot")] = processed[d2df(system, unit, flow, "mdot")] * processed[d2df(system, unit, flow, "b")]
                elif dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] == "IPF":
                    if processed[d2df(system,unit,flow,"T")].isnull().sum() == 0:
                        if "Water" in flow:
                            dh = CONSTANTS["General"]["CP_WATER"] * processed[d2df(system,unit,flow,"mdot")] * (
                                processed[d2df(system, unit, flow, "T")] - processed["T_0"])
                            ds = CONSTANTS["General"]["CP_WATER"] * processed[d2df(system,unit,flow,"mdot")] * np.log((
                                processed[d2df(system, unit, flow, "T")] / processed["T_0"]))
                    else:
                        print("Couldn't calculate the properies for the {} flow, didn't have all what I needed".format(system + ":" + unit + ":" + flow))
                    processed[d2df(system,unit,flow,"h")] = dh
                    processed[d2df(system,unit,flow,"b")] = dh - processed["T_0"] * ds
                    processed[d2df(system,unit,flow,"Edot")] = processed[d2df(system,unit,flow,"mdot")] * processed[d2df(system,unit,flow,"h")]
                    processed[d2df(system, unit, flow, "Bdot")] = processed[d2df(system, unit, flow, "mdot")] * processed[d2df(system, unit, flow, "b")]
                elif dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] == "Qdot":
                    processed[d2df(system, unit, flow, "Edot")] = processed[d2df(system,unit,flow,"Qdot")]
                    processed[d2df(system, unit, flow, "Bdot")] = processed[d2df(system,unit,flow,"Qdot")] / processed[d2df(system,unit,flow,"T")]
                elif dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"] == "Wdot":
                    processed[d2df(system, unit, flow, "Edot")] = processed[d2df(system, unit, flow, "Wdot")]
                    processed[d2df(system, unit, flow, "Bdot")] = processed[d2df(system, unit, flow, "Wdot")]
    print("...done!")
    return processed


def eYergyAnalysis(processed,T0):
    ("Started with the calculation of energy and exergy flows...")
    for system in processed:
        for unit in processed[system]:
            for flow in processed[system][unit]:
                if processed[system][unit][flow]["Type"] == "IPF":
                    # Calculating the energy flows
                    processed[system][unit][flow]["Edot"] = processed[system][unit][flow]["mdot"] * (
                        processed[system][unit][flow]["h"] - processed[system][unit][flow]["h0"])
                    # Calculating the specific exergy
                    processed[system][unit][flow]["b"] = (
                        processed[system][unit][flow]["h"] - processed[system][unit][flow]["h0"]) - T0 * (
                        processed[system][unit][flow]["s"] - processed[system][unit][flow]["s0"])
                # Calculating the exergy flows
                    processed[system][unit][flow]["Bdot"] = processed[system][unit][flow]["mdot"] * (processed[system][unit][flow]["b"])
                elif processed[system][unit][flow]["Type"] == "IPF":
                    # Calculating the specific exergy
                    processed[system][unit][flow]["b"] = processed[system][unit][flow]["cp"] * (
                        (processed[system][unit][flow]["T"] - T0) - T0 * (
                        np.log(processed[system][unit][flow]["T"] / T0)))
                # Calculating the energy flows
                    processed[system][unit][flow]["Edot"] = processed[system][unit][flow]["mdot"] * processed[system][unit][flow]["cp"] * (
                        processed[system][unit][flow]["T"] - T0)
                # Calculating the exergy flows
                    processed[system][unit][flow]["Bdot"] = processed[system][unit][flow]["mdot"] * processed[system][unit][flow]["b"]
                elif processed[system][unit][flow]["Type"] == "Qdot":
                    processed[system][unit][flow]["Edot"] = processed[system][unit][flow]["Qdot"]
                    processed[system][unit][flow]["Bdot"] = processed[system][unit][flow]["Qdot"] / processed[system][unit][flow]["T"]
                elif processed[system][unit][flow]["Type"] == "Wdot":
                    processed[system][unit][flow]["Edot"] = processed[system][unit][flow]["Wdot"]
                    processed[system][unit][flow]["Bdot"] = processed[system][unit][flow]["Wdot"]
    print("...done!")
    return processed




def enthalpyCalculator(T, CONSTANTS, mass_composition = {"N2": 0.768, "O2": 0.232, "CO2": 0.0, "H2O": 0.0}):
    specific_enthalpy_molar = {}
    for idx in mass_composition:
        specific_enthalpy_molar[idx] = (CONSTANTS["General"]["NASA_POLY"][idx][0] * T +
                CONSTANTS["General"]["NASA_POLY"][idx][1] * T**2 +
                CONSTANTS["General"]["NASA_POLY"][idx][2] * T**3 +
                CONSTANTS["General"]["NASA_POLY"][idx][3] * T**4 +
                CONSTANTS["General"]["NASA_POLY"][idx][4] * T**5 +
                CONSTANTS["General"]["NASA_POLY"][idx][5]) * CONSTANTS["General"]["R_0"] # This result is in J/molK
    specific_enthalpy = (specific_enthalpy_molar["N2"] / CONSTANTS["General"]["MOLAR_MASSES"]["N2"] * mass_composition["N2"] +
                         specific_enthalpy_molar["O2"] / CONSTANTS["General"]["MOLAR_MASSES"]["O2"] * mass_composition["O2"] +
                         specific_enthalpy_molar["CO2"] / CONSTANTS["General"]["MOLAR_MASSES"]["CO2"] * mass_composition["CO2"] +
                         specific_enthalpy_molar["H2O"] / CONSTANTS["General"]["MOLAR_MASSES"]["H2O"] * mass_composition["H2O"])
    return specific_enthalpy


def entropyCalculator(T, CONSTANTS, mass_composition = {"N2": 0.768, "O2": 0.232, "CO2": 0.0, "H2O": 0.0}):
    specific_entropy_molar = {}
    for idx in mass_composition:
        specific_entropy_molar[idx] = (CONSTANTS["General"]["NASA_POLY"][idx][0] * np.log(T) +
                CONSTANTS["General"]["NASA_POLY"][idx][1] * T +
                CONSTANTS["General"]["NASA_POLY"][idx][2] * T**2 +
                CONSTANTS["General"]["NASA_POLY"][idx][3] * T**3 +
                CONSTANTS["General"]["NASA_POLY"][idx][4] * T**4 +
                CONSTANTS["General"]["NASA_POLY"][idx][6]) * CONSTANTS["General"]["R_0"] # This result is in J/molK
    specific_entropy = (specific_entropy_molar["N2"] / CONSTANTS["General"]["MOLAR_MASSES"]["N2"] * mass_composition["N2"] +
                         specific_entropy_molar["O2"] / CONSTANTS["General"]["MOLAR_MASSES"]["O2"] * mass_composition["O2"] +
                         specific_entropy_molar["CO2"] / CONSTANTS["General"]["MOLAR_MASSES"]["CO2"] * mass_composition["CO2"] +
                         specific_entropy_molar["H2O"] / CONSTANTS["General"]["MOLAR_MASSES"]["H2O"] * mass_composition["H2O"])
    return specific_entropy