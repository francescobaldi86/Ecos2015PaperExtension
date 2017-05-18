# Temporarily empty


def eYergyAnalzsis(structure):
    for system in structure:
        for unit in structure[system]:
            for flow in structure[system][unit]:
                if flow["Type"] == "CPF":
                    # If the specific enthalpy is available already, it needs to be calculated
                    if flow["h"]


                    # Calculating the energy flows
                    structure[system][unit][flow]["Edot"] = structure[system][unit][flow]["mdot"] * (
                        structure[system][unit][flow]["h"] - structure[system][unit][flow]["h0"])
                    # Calculating the exergy flows
                    structure[system][unit][flow]["Bdot"] = structure[system][unit][flow]["mdot"] * (
                        (structure[system][unit][flow]["h"] - structure[system][unit][flow]["h0"]) - T0 *
                        (structure[system][unit][flow]["s"] - structure[system][unit][flow]["s0"]))