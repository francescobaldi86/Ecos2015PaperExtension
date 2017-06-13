# Temporarily empty
import CoolProp.CoolProp as cp
import numpy as np
import pandas as pd


def propertyCalculator(processed, T0):
    for system in processed:
        for unit in processed[system]:
            for flow in processed[system][unit]:
                if processed[system][unit][flow]["type"] == "CPF":
                    # Only doing the calculations if the values for p and T are not NaN
                    if (processed[system][unit][flow]["p"].isnull().sum() < 1) & (
                        processed[system][unit][flow]["T"].isnull().sum() < 1):
                    # Defining the flow type
                    # If the specific enthalpy is available already, it needs to be calculated
                        print("Calculating properties for " + system + "_" + unit + "_" + flow)
                        if ("Air" in flow) or ("BP" in flow):
                            press = np.array(processed[system][unit][flow]["p"])#.values()  # It's not really needed to do it in two steps..
                            temp = np.array(processed[system][unit][flow]["T"])#.values()
                            if processed[system][unit][flow]["h"].sum() == 0:
                                processed[system][unit][flow]["h"] = pd.Series(cp.PropsSI('H','T',temp,'P',press, 'Air.mix'))
                            if processed[system][unit][flow]["s"].sum() == 0:
                                processed[system][unit][flow]["s"] = pd.Series(cp.PropsSI('S', 'T', temp, 'P', press, 'Air.mix'))
                            if processed[system][unit][flow]["h0"].sum() == 0:
                                processed[system][unit][flow]["h0"] = pd.Series(cp.PropsSI('H', 'T', np.array(T0), 'P', press, 'Air.mix'))
                            if processed[system][unit][flow]["s0"].sum() == 0:
                                processed[system][unit][flow]["s0"] = pd.Series(cp.PropsSI('S', 'T', np.array(T0), 'P', press, 'Air.mix'))
                        elif ("Mix" in flow) or ("EG" in flow):
                            press = np.array(processed[system][unit][flow]["p"])  # .values()  # It's not really needed to do it in two steps..
                            temp = np.array(processed[system][unit][flow]["T"])  # .values()
                            if processed[system][unit][flow]["h"].sum() == 0:
                                for idx in processed[system][unit][flow]["p"].index:
                                    mixture = "HEOS::" + \
                                              "N2[" + str(processed[system][unit][flow]["Composition"]["N2"][idx]) + "]&" \
                                              "O2[" + str(processed[system][unit][flow]["Composition"]["O2"][idx]) + "]&" \
                                              "H2O[" + str(processed[system][unit][flow]["Composition"]["H2O"][idx]) + "]&" \
                                              "CO2[" + str(processed[system][unit][flow]["Composition"]["CO22"][idx]) + "]"
                                    processed[system][unit][flow]["h"] = pd.Series(cp.PropsSI('H','T',temp[idx],'P',press[idx], mixture))
                            if processed[system][unit][flow]["s"].sum() == 0:
                                for idx in processed[system][unit][flow]["p"].index:
                                    mixture = "HEOS::" + \
                                              "N2[" + str(processed[system][unit][flow]["Composition"]["N2"][idx]) + "]&" \
                                              "O2[" + str(processed[system][unit][flow]["Composition"]["O2"][idx]) + "]&" \
                                              "H2O[" + str(processed[system][unit][flow]["Composition"]["H2O"][idx]) + "]&" \
                                              "CO2[" + str(processed[system][unit][flow]["Composition"]["CO22"][idx]) + "]"
                                    processed[system][unit][flow]["s"] = pd.Series(cp.PropsSI('S', 'T', temp[idx], 'P', press[idx], mixture))
                            if processed[system][unit][flow]["h0"].sum() == 0:
                                for idx in processed[system][unit][flow]["p"].index:
                                    mixture = "HEOS::" + \
                                              "N2[" + str(processed[system][unit][flow]["Composition"]["N2"][idx]) + "]&" \
                                              "O2[" + str(processed[system][unit][flow]["Composition"]["O2"][idx]) + "]&" \
                                              "H2O[" + str(processed[system][unit][flow]["Composition"]["H2O"][idx]) + "]&" \
                                              "CO2[" + str(processed[system][unit][flow]["Composition"]["CO22"][idx]) + "]"
                                    processed[system][unit][flow]["h0"] = pd.Series(cp.PropsSI('H', 'T', T0[idx], 'P', press[idx], mixture))
                            if processed[system][unit][flow]["s0"].sum() == 0:
                                for idx in processed[system][unit][flow]["p"].index:
                                    mixture = "HEOS::" + \
                                              "N2[" + str(processed[system][unit][flow]["Composition"]["N2"][idx]) + "]&" \
                                              "O2[" + str(processed[system][unit][flow]["Composition"]["O2"][idx]) + "]&" \
                                              "H2O[" + str(processed[system][unit][flow]["Composition"]["H2O"][idx]) + "]&" \
                                              "CO2[" + str(processed[system][unit][flow]["Composition"]["CO22"][idx]) + "]"
                                    processed[system][unit][flow]["s0"] = pd.Series(cp.PropsSI('S', 'T', T0[idx], 'P', press[idx], mixture))

    return processed


def eYergyAnalysis(processed,T0):
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
    return processed