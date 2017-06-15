# Temporarily empty
import CoolProp.CoolProp as cp
import numpy as np
import pandas as pd
import preprocessingO as ppo
from helpers import d2df

def propertyCalculator(processed, dict_structure, CONSTANTS):
    print("Started calculating flow properties...")
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
                            dh = pd.Series(cp.PropsSI('H','T',np.array(temp),'P',np.array(press), 'Air.mix')) - pd.Series(cp.PropsSI('H', 'T', np.array(processed["T_0"]), 'P', np.array(press), 'Air.mix'))
                            ds = pd.Series(cp.PropsSI('S', 'T', np.array(temp), 'P', np.array(press), 'Air.mix')) - pd.Series(cp.PropsSI('S', 'T', np.array(processed["T_0"]), 'P', np.array(press), 'Air.mix'))
                            dh.loc[~processed[system + ":on"]] = 0
                            ds.loc[~processed[system + ":on"]] = 0
                        elif ("Mix" in flow) or ("EG" in flow):
                            dh = pd.Series(index=processed.index)
                            ds = pd.Series(index=processed.index)
                            for idx in dh.index:
                                if "Mix" in flow:
                                    mixture = processed[system+":Mix_Composition"][idx]
                                else:
                                    mixture = processed[system + ":EG_Composition"][idx]
                                if [processed[system + ":on"]][idx]:
                                    dh.loc[idx] = cp.PropsSI('H','T',temp[idx],'P',press[idx], mixture) - cp.PropsSI('H', 'T', processed["T_0"][idx], 'P', press[idx], mixture)
                                    ds.loc[idx] = cp.PropsSI('S', 'T', temp[idx], 'P', press[idx], mixture) - cp.PropsSI('S', 'T', processed["T_0"][idx], 'P', press[idx], mixture)
                                else:
                                    dh.loc[idx] = 0
                                    ds.loc[idx] = 0
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