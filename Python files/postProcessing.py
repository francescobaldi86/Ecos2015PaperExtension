from helpers import d2df
import pandas as pd
import matplotlib.pylab as plt

def predefinedTables(processed, name, CONSTANTS, dict_structure, system, load_vector):
    file = open(CONSTANTS["filenames"]["latex_table"], "w")
    if name == "MainEnginesModel":
        for unit in dict_structure["systems"]["ME1"]["units"]:
            for flow in dict_structure["systems"]["ME1"]["units"][unit]["flows"]:
                if dict_structure["systems"]["ME1"]["units"][unit]["flows"][flow]["type"] in {"IPF", "CPF"}:
                    for property in {"T", "mdot"}:
                        value = []
                        for load in [0.3, 0.5, 0.7, 0.9]:
                            if property == "T":
                                rounding = 1
                            else:
                                rounding = 2
                            value.append(round(processed[d2df("ME1", unit, flow, property)][
                                                   (processed["ME1:load"] < load + 0.005) & (
                                                   processed["ME1:load"] > load - 0.005)].mean(), rounding))
                        print(property + "_" + unit + "_" + flow + " = " + str(value[0]) + " & " + str(
                            value[1]) + " & " + str(value[2]) + " & " + str(value[3]) + " \\\\ ")

    if name == "MainEnginesEnergyFlows":
        df = pd.DataFrame(index=processed.index)
        df["Wdot_mech"] = processed[d2df(system, "Cyl", "Power_out", "Edot")]
        df["Qdot_eg"] = processed[d2df(system, "Turbine", "Mix_out", "Edot")]
        df["Qdot_jwc"] = processed[d2df(system, "Cyl", "QdotJW_out", "Edot")]
        df["Qdot_loc"] = processed[d2df(system, "LOC", "LTWater_out", "Edot")] - processed[d2df(system, "LOC", "LTWater_in", "Edot")]
        df["Qdot_caclt"] = processed[d2df(system, "CAC_LT", "LTWater_out", "Edot")] - processed[d2df(system, "CAC_LT", "LTWater_in", "Edot")]
        df["Qdot_cacht"] = processed[d2df(system, "CAC_HT", "HTWater_out", "Edot")] - processed[d2df(system, "CAC_HT", "HTWater_in", "Edot")]
        df["Qdot_ht"] = df["Qdot_cacht"] + df["Qdot_jwc"]
        df["Qdot_lt"] = df["Qdot_caclt"] + df["Qdot_loc"]
        output = {}
        load_vector = [0.3, 0.5, 0.7, 0.9]
        for flow in df.keys():
            output[flow] = []
            string = flow + " = "
            for load in load_vector:
                value = round(df[flow][(processed[system+":load"] < load + 0.005) & (processed[system+":load"] > load - 0.005)].mean(), 0)
                output[flow].append(value)
                string = string + " & " + str(value)
            print(string)
        plt.figure()
        for flow in output:
            plt.plot(load_vector, output[flow], label=flow)
        plt.xlabel("Engine load")
        plt.ylabel("Energy flow [kW]")
        plt.legend()
        plt.grid()