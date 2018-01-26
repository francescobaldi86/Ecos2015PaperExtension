import pandas as pd
import numpy as np
import csv

def exportEfficiecies(processed, CONSTANTS, dict_structure):
    # This function writes out the CSV file with the processed, aggregated data about efficiencies and such for the
    # whole operating period
    text_file = open(CONSTANTS["filenames"]["aggregated_efficiencies"], "w")
    text_file.write("Variable name,EnergyEfficiency,ExergyEfficiency,EfficiencyDefect,IrreversibilityShare\n")
    for system in ["ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4", "CoolingSystems", "HTHR", "Steam"]:
        text_file.write("\n")
        text_file.write(system+", , , ," + str(processed[system+":"+"delta"].mean()) + "\n")
        for unit in dict_structure["systems"][system]["units"]:
            text_file.write(unit)
            for efficiency in ["eta", "eps", "lambda", "delta"]:
                if system + ":" + unit + ":" + efficiency in processed.columns:
                    text_file.write("," + str(dict_structure["systems"][system]["units"][unit][efficiency]))
                else:
                    text_file.write(",")
            text_file.write("\n")
    text_file.close()

def exportClusteringFlows(processed, CONSTANTS, dict_structure):
    # This function exports the most flows that might be interesting for clustering purposes
    output = pd.DataFrame(index=processed.index)
    output["electricPowerDemand"] = processed["Demands:Electricity:Total:Edot"]
    output["mechanicalPowerDemand"] = processed["Demands:Mechanical:Total:Edot"]
    output["totalElectricDemand"] = processed["Demands:Mechanical:Total:Edot"] + processed["Demands:Electricity:Total:Edot"]
    output["heatDemandLowTemperature"] = processed["Demands:Heat:HVACpreheater:Edot"]
    output["heatDemandHighTemperature"] = processed["Demands:Heat:Total:Edot"] - processed["Demands:Heat:HVACpreheater:Edot"] - processed["Demands:Heat:HFOheater:Edot"]
    output["totalExergyDestruction"] = sum(processed[system + ":" + unit + ":" + "Idot"]
                          for system in dict_structure["systems"] for unit in dict_structure["systems"][system]["units"])
    output["totalExergyDestructionMinusEngines"] = output["totalExergyDestruction"] - sum(processed[system + ":" + unit + ":" + "Idot"]
                          for system in {"ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4"}
                          for unit in {"Comp", "Turbine", "BPsplit", "BPmerge", "BPvalve", "TCshaft"})
    output["relativeExergyDestruction"] = output["totalExergyDestruction"] / sum(processed[system + ":" + "Cyl" + ":" "FuelCh_in" + ":" + "Bdot"]
                 for system in {"ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4"})
    output["shipSpeed"] = processed["ShipSpeed"]
    output["nPassengers"] = processed["Passengers_calc"]
    output.to_csv(CONSTANTS["filenames"]["flows_clustering"])
    return output


def exportClusteringFlowsFB(processed, CONSTANTS, dict_structure):
    # This function exports the most flows that might be interesting for clustering purposes
    output = pd.DataFrame(index=processed.index)
    output["totalElectricDemand"] = processed["Demands:Mechanical:Total:Edot"] + processed["Demands:Electricity:Total:Edot"]
    output["heatDemand"] = processed["Demands:Heat:Total:Edot"] - processed["Demands:Heat:HFOheater:Edot"] - processed["Demands:Heat:HFOtankHeating:Edot"]
    output.to_csv(CONSTANTS["filenames"]["flows_clustering"]+"FB")
    return output


def exportAggregatedEyergyFlows(processed, CONSTANTS, dict_structure):
    # This function exports all energy and exergy flows in two separate csv files
    # These are later processed and used for tables and plotting
    # Values are given for
    # - Total
    # - For each sailing mode
    # - For each season
    operationalModeNames = processed["OperationalMode"].unique()
    seasonNames = processed["Season"].unique()
    headerString = "VariableName,Total"
    energyFlows = ""
    exergyFlows = ""
    for idOpMode in operationalModeNames:
        headerString = headerString + "," + idOpMode
    for idSeason in seasonNames:
        headerString = headerString + "," + idSeason
    energyFlows = energyFlows + headerString + '\n'
    exergyFlows = exergyFlows + headerString + '\n'
    for flow in processed.keys():
        # Saving aggregated ENERGY flows:
        if flow[-4:] == "Edot":
            energyFlows = energyFlows + flow
            energyFlows = energyFlows + "," + str(processed[flow].sum()) # Total
            for idOpMode in operationalModeNames: # Based on operational mode
                energyFlows = energyFlows + "," + str(processed[flow][processed["OperationalMode"]==idOpMode].sum())
            for idSeason in seasonNames: # Based on season
                energyFlows = energyFlows + "," + str(processed[flow][processed["Season"] == idSeason].sum())
            energyFlows = energyFlows + "\n"
        if flow[-4:] == "Bdot":
            exergyFlows = exergyFlows + flow
            exergyFlows = exergyFlows + "," + str(processed[flow].sum())  # Total
            for idOpMode in operationalModeNames:  # Based on operational mode
                exergyFlows = exergyFlows + ","+ str(processed[flow][processed["OperationalMode"] == idOpMode].sum())
            for idSeason in seasonNames:  # Based on season
                exergyFlows = exergyFlows + "," + str(processed[flow][processed["Season"] == idSeason].sum())
            exergyFlows = exergyFlows + "\n"
    with open(CONSTANTS["filenames"]["aggregated_flows_energy"], "w") as text_file:
        print(energyFlows, file=text_file)
    with open(CONSTANTS["filenames"]["aggregated_flows_exergy"], "w") as text_file:
        print(exergyFlows, file=text_file)