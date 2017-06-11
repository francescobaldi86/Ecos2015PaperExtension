# Temporarily empty
import CoolProp as cp
import numpy as np
import pandas as pd


def propertyCalculator(processed, T0):
    for system in processed:
        for unit in processed[system]:
            for flow in processed[system][unit]:
                if processed[system][unit][flow]["Type"] == "CPF":
                    # Only doing the calculations if the values for p and T are not NaN
                    if (processed[system][unit][flow]["p"].isnan().sum() < 100) & (processed[system][unit][flow]["T"].isnan().sum() < 100):
                        # If the specific enthalpy is available already, it needs to be calculated
                        p = processed[system][unit][flow]["p"].values()  # It's not really needed to do it in two steps..
                        T = processed[system][unit][flow]["T"].values()
                        if processed[system][unit][flow]["h"].sum() == 0:
                            processed[system][unit][flow]["h"] = pd.Series(cp.PropSI('H','T',T,'P',p))
                        if processed[system][unit][flow]["s"].sum() == 0:
                            processed[system][unit][flow]["s"] = pd.Series(cp.PropSI('S', 'T', T, 'P', p))
                        if processed[system][unit][flow]["h0"].sum() == 0:
                            processed[system][unit][flow]["h0"] = pd.Series(cp.PropSI('H', 'T', T0, 'P', p))
                        if processed[system][unit][flow]["s0"].sum() == 0:
                            processed[system][unit][flow]["s0"] = pd.Series(cp.PropSI('S', 'T', T0, 'P', p))
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