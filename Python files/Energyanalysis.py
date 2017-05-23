# Temporarily empty
import CoolProp.CoolProp as cp
import numpy as np
import pandas as pd

def eYergyAnalzsis(structure,T0):
    for system in structure:
        for unit in structure[system]:
            for flow in structure[system][unit]:
                if structure[system][unit][flow]["Type"] == "CPF":
                    # If the specific enthalpy is available already, it needs to be calculated
                    p = structure[system][unit][flow]["p"].values()  # It's not really needed to do it in two steps..
                    T = structure[system][unit][flow]["T"].values()
                    if structure[system][unit][flow]["h"].sum() == 0:
                        structure[system][unit][flow]["h"] = pd.Series(cp.PropSI('H','T',T,'P',p))
                    if structure[system][unit][flow]["s"].sum() == 0:
                        structure[system][unit][flow]["s"] = pd.Series(cp.PropSI('S', 'T', T, 'P', p))
                    structure[system][unit][flow]["h0"] = pd.Series(cp.PropSI('H', 'T', T0, 'P', p))
                    structure[system][unit][flow]["s0"] = pd.Series(cp.PropSI('S', 'T', T0, 'P', p))
                    del p,T  # I am not sure if deleting variables serves a purpose in Python, but it doesn't cost
                    # Calculating the energy flows
                    structure[system][unit][flow]["Edot"] = structure[system][unit][flow]["mdot"] * (
                        structure[system][unit][flow]["h"] - structure[system][unit][flow]["h0"])
                    # Calculating the exergy flows
                    structure[system][unit][flow]["Bdot"] = structure[system][unit][flow]["mdot"] * (
                        (structure[system][unit][flow]["h"] - structure[system][unit][flow]["h0"]) - T0 *
                        (structure[system][unit][flow]["s"] - structure[system][unit][flow]["s0"]))
                elif structure[system][unit][flow]["Type"] == "IPF":
                    # Calculating the energy flows
                    structure[system][unit][flow]["Edot"] = structure[system][unit][flow]["mdot"] * structure[system][unit][flow]["cp"] * (
                        structure[system][unit][flow]["T"] - T0)
                    # Calculating the exergy flows
                    structure[system][unit][flow]["Bdot"] = structure[system][unit][flow]["mdot"] * structure[system][unit][flow]["cp"] * (
                        (structure[system][unit][flow]["T"] - T0) - T0 *
                        np.log(structure[system][unit][flow]["T"] / T0))
                elif structure[system][unit][flow]["Type"] == "Qdot":
                    structure[system][unit][flow]["Edot"] = structure[system][unit][flow]["Qdot"]
                    structure[system][unit][flow]["Bdot"] = structure[system][unit][flow]["Qdot"] / structure[system][unit][flow]["T"]
                elif structure[system][unit][flow]["Type"] == "Wdot":
                    structure[system][unit][flow]["Edot"] = structure[system][unit][flow]["Wdot"]
                    structure[system][unit][flow]["Bdot"] = structure[system][unit][flow]["Wdot"]