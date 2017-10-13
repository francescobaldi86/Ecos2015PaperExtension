import os
from helpers import d2df
import numpy as np



def filenames(project_path):
    #project_path = os.path.realpath('..')
    #project_path = os.path.dirname(os.path.realpath(__file__))
    #project_path = project_path + os.sep + ".."
    output = {}
    # Input files
    output["dataset_raw"] = project_path + os.sep + 'Database' + os.sep +'selected_df.h5'
    output["headers_translate"] = project_path + os.sep + 'General' + os.sep +'headers_dict.xlsx'
    output["consistency_check_input"] = project_path + os.sep + 'Data_Process'+ os.sep +'check_input.csv'
    # Output files
    output["dataset_output_empty"] = project_path + os.sep +'Data_Process' + os.sep + 'database_out_empty.h5'
    output["dataset_output"] = project_path + os.sep +'Data_Process' + os.sep + 'database_out.h5'
    output["consistency_check_report"] = project_path + os.sep + 'Data_Process' + os.sep + 'check_report.txt'
    output["aggregated_efficiencies"] = project_path + os.sep + 'Results' + os.sep + 'aggregated_efficiencies.csv'
    output["aggregated_flows_total"] = project_path + os.sep + 'Results' + os.sep + 'aggregated_flows_total.csv'
    output["aggregated_flows_opmode"] = project_path + os.sep + 'Results' + os.sep + 'aggregated_flows_opmode.csv'
    output["latex_table"] = project_path + os.sep + 'Manuscript' + os.sep + 'Figures' + os.sep + 'table.tex'
    # opening the report file and inititing it
    text_file = open(output["consistency_check_report"],"w") # Cleaning the file
    text_file.write("=== STARTING THE REPORT FILE === \n \n")
    text_file.close()
    return output




def assumptions(raw, processed, CONSTANTS, hd):
    # This function includes generic assumed values in the main structure
    # ALL ENGINES
    for system in {"ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4"}:
        # The pressure at the turbocharger air inlet and exhaust outlet is equal to the atmospheric pressure
        processed.loc[:,d2df(system,"Comp","Air_in","p")] = CONSTANTS["General"]["P_ATM"]
        processed.loc[:,d2df(system, "Turbine", "Mix_out", "p")] = CONSTANTS["General"]["P_ATM"]
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[d2df(system, "Comp", "Air_in", "T")] = raw[hd["ER_AIR_T_"]] + 273.15
        # Assuming that the pressure in the exhaust gas is 90% of the pressure in the inlet manifold. Somewhat reasonable
        processed[d2df(system, "Cyl", "EG_out", "p")] = (0.9 * raw[hd[system + "-CAC_AIR_P_OUT"]] + 1.01325) * 100000
        # Assuming the pressure of the fuel to be around 9 barg, based on measurements from ME4
        processed.loc[:,d2df(system, "Cyl", "FuelPh_in", "p")] = (9 + 1.01325) * 10e5
        # Assuming the temperature of the cylinder wall to be 150 degC
        processed.loc[:,d2df(system, "Cyl", "QdotJW_out", "T")] = 150 + 273.15
        processed.loc[:,d2df(system, "JWC", "QdotJW_in", "T")] = 150 + 273.15
        # Assuming a temperature of 100 degC for heat losses from the TC shaft
        processed.loc[:,d2df(system, "TCshaft", "Losses_out", "T")] = 100 + 273.15
        # We assume the mixgin temperature at the LT inlet of the HT mixer to be constant
        processed.loc[:,d2df(system, "HTmerge", "LTWater_in", "T")] = CONSTANTS["MainEngines"]["T_COOLING_MIX"]
        if system in {"ME1", "ME2", "ME3", "ME4"}:
            processed.loc[:,d2df(system, "Cyl", "QdotRad_out", "Edot")] = 0.01 * CONSTANTS["MainEngines"]["MCR"]
        # Assuming the steam pressure and temperature in the HRSG to be constant...
        hrsg_pressure_assumption = (6 + 1.01325) * 100000
        # Adding radiative losses
        processed.loc[:, d2df(system, "Cyl", "QdotRad_out", "T")] = 100 + 273.15
        if system in {"AE1", "AE2", "AE3", "AE4"}:
            processed.loc[:,d2df(system, "AG", "Losses_out", "T")] = 100 + 273.15
            processed.loc[:,d2df(system, "Cyl", "Power_out", "omega")] = 750
            processed.loc[:, d2df(system, "Cyl", "QdotRad_out", "Edot")] = 0.01 * CONSTANTS["AuxEngines"]["MCR"]
    # Others
    processed.loc[:,"T_0"] = raw[hd["water_T_forsmark_smhi-opendata"]] + 273.15
    processed.loc[:,"T_air"] = raw[hd["air_T_sv_hogarna_smhi-opendata"]] + 273.15
    processed[d2df("CoolingSystems","SWC13","SeaWater_out","T")] = raw[hd["SWC13_SW_T_OUT"]] + 273.15 # CHECK IF IT IS IN OR OUT
    processed[d2df("CoolingSystems","SWC24","SeaWater_out","T")] = raw[hd["SWC24_SW_T_OUT"]] + 273.15 # CHECK IF IT IS IN OR OUT
    # Boilers
    processed.loc[:, "Steam:Boiler1:EG_out:p"] = 101325 + 10000
    processed.loc[:, "Steam:Boiler1:Air_in:T"] = raw[hd["ER_AIR_T_"]] + 273.15
    processed.loc[:, "Steam:Boiler1:Air_in:p"] = 101325
    # HTHR system
    processed.loc[:,"HTHR:SteamHeater:HRWater_out:T"] = 90 + 273.15 # From the heat balance, the temperature needs to rise at 90 degrees
    # processed.loc[:,"HTHR:SteamHeater:HRWater_out:mdot"] = 298 / 3600 * CONSTANTS["General"]["RHO_W"] # the original value is in m3/h
    processed.loc[:,"HTHR:HTHR24:HRWater_in:T"] = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HTHR_INLET_TEMPERATURE"] # Assumption on the Temperature at the HTHR-24 inlet (HT side)
    processed.loc[:, "HTHR:HVACpreheater:Qdot_out:T"] = (50 - 23) / np.log((50+273.15)/(23+273.15))
    processed.loc[:, "HTHR:HVACreheater:Qdot_out:T"] = (80 - 60) / np.log((80 + 273.15) / (60 + 273.15))
    processed.loc[:, "HTHR:HotWaterHeater:Qdot_out:T"] = 70 + 273.15
    processed.loc[:, "Steam:TankHeating:Qdot_out:T"] = 60 + 273.15
    processed.loc[:, "Steam:MachinerySpaceHeaters:Qdot_out:T"] = processed["HTHR:HVACpreheater:Qdot_out:T"]
    processed.loc[:, "Steam:Galley:Qdot_out:T"] = 90 + 273.15
    processed.loc[:, "Steam:OtherTanks:Qdot_out:T"] = 60 + 273.15
    processed.loc[:, "Steam:HFOtankHeating:Qdot_out:T"] = 75 + 273.15 # some sort of average value...
    processed.loc[:, "Steam:HFOheater:Qdot_out:T"] = (110 - 75) / np.log((110 + 273.15) / (75 + 273.15))
    return processed
