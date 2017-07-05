import numpy as np
import pandas as pd
from helpers import d2df


def auxPowerAnalysis(processed, CONSTANTS, dict_structure):
    # Calculating the total auxiliary power demand
    processed = auxPowerTotalDemand(processed)
    # Calculating the contribution from the thrusters
    #processed = thrusters(processed, CONSTANTS)  # The second method works better. But I still keep it
    processed = thrusters2(processed, CONSTANTS)
    processed = HVAC(processed, CONSTANTS)
    processed = heatDemand(processed, CONSTANTS, dict_structure)
    processed = HTHR(processed, CONSTANTS)
    processed = steamSystems(processed, CONSTANTS)
    return processed



def auxPowerTotalDemand(processed):
    processed["Demands:Electricity:Total:Edot"] = processed["AE1:AG:Power_out:Edot"]+processed["AE2:AG:Power_out:Edot"]+processed["AE3:AG:Power_out:Edot"]+processed["AE4:AG:Power_out:Edot"]
    # We also need to store (for further use) a series made of the daily averages
    processed["Demands:Electricity:Total:Edot1D"] = processed["Demands:Electricity:Total:Edot"].resample('1D').mean().reindex(processed["Demands:Electricity:Total:Edot"].index, method='ffill')
    processed["Demands:Electricity:Other:Edot"] = processed["Demands:Electricity:Total:Edot"]
    return processed



def HVAC(processed, CONSTANTS):
    # The idea of the calculation of the HVAC demand, very much simplified, lies in saying that during the summer monhs
    # the HVAC demand is the difference between the average consumption before summer AND the instananteous one.
    mask = (processed.index > CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_START"]) & (processed.index <= CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_END"])
    processed["Demands:Electricity:HVAC:Edot"] = processed["Demands:Electricity:Total:Edot1D"] - (processed["Demands:Electricity:Total:Edot1D"][processed.index < CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_START"]]).mean()/2 - (processed["Demands:Electricity:Total:Edot1D"][processed.index > CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_END"]]).mean()/2
    processed.loc[~mask,"Demands:Electricity:HVAC:Edot"] = 0
    processed["Demands:Electricity:Other:Edot"] = processed["Demands:Electricity:Other:Edot"] - processed["Demands:Electricity:HVAC:Edot"]
    return processed


def thrusters(processed, CONSTANTS):
    aaa = 0 # This is only defined as a trick for the cases when there are two consecutive time steps with thrusters on
    for idx in range(len(processed.index)):
        if aaa == 1:
            aaa = 0
            continue
        idt = processed.index[idx]
        if idx > len(processed.index) - 2:
            processed.loc[idt, "Demands:Electricity:Thrusters:Edot"] = 0
        else:
            if processed["Demands:Electricity:Total:Edot"][processed.index[idx]] - processed["Demands:Electricity:Total:Edot"][processed.index[idx-1]] > 240:
                if abs(processed["Demands:Electricity:Total:Edot"][processed.index[idx+1]] - processed["Demands:Electricity:Total:Edot"][processed.index[idx]]) < 50:
                    processed.loc[processed.index[idx], "Demands:Electricity:Thrusters:Edot"] = processed["Demands:Electricity:Total:Edot"][processed.index[idx]] - (processed["Demands:Electricity:Total:Edot"][processed.index[idx - 1]] + (processed["Demands:Electricity:Total:Edot"][processed.index[idx + 2]] - processed["Demands:Electricity:Total:Edot"][processed.index[idx-1]]) / 3)
                    processed.loc[processed.index[idx+1], "Demands:Electricity:Thrusters:Edot"] = processed["Demands:Electricity:Total:Edot"][processed.index[idx+1]] - (processed["Demands:Electricity:Total:Edot"][processed.index[idx - 1]] + (processed["Demands:Electricity:Total:Edot"][processed.index[idx + 2]] - processed["Demands:Electricity:Total:Edot"][processed.index[idx-1]]) * 2 / 3)
                    aaa = 1  # Setting aaa=1 here makes us skip the next iteration
                else:
                    processed.loc[processed.index[idx], "Demands:Electricity:Thrusters:Edot"] = processed["Demands:Electricity:Total:Edot"][processed.index[idx]] - processed["Demands:Electricity:Total:Edot"][processed.index[idx-1]]/2 - processed["Demands:Electricity:Total:Edot"][processed.index[idx+1]]/2
            else:
                processed.loc[idt, "Demands:Electricity:Thrusters:Edot"] = 0
    return processed


def thrusters2(processed, CONSTANTS):
    # The principle of this function is to divide the instanteneous value of total power consumption by the daily average.
    # Then, we take the first day as reference, we manually select the "thruster" values, and we take the difference as
    # the expected "no-thrusters" instantaneous consumption

    # Division of the instantaneous power demand by the daily average
    temp = np.ndarray.tolist((processed["Demands:Electricity:Total:Edot"] / processed["Demands:Electricity:Total:Edot1D"]).values)
    # Selection of the first cycle (just representative as any other)
    temp = temp[0:96]
    # Re-assignment of the datapoints with the thrusters on
    temp[28] = temp[27] + (temp[30] - temp[27]) * 1 / 3
    temp[29] = temp[27] + (temp[30] - temp[27]) * 2 / 3
    temp[35] = temp[34] + (temp[36] - temp[34]) * 1 / 2
    temp[61] = temp[60] + (temp[63] - temp[60]) * 1 / 3
    temp[62] = temp[60] + (temp[63] - temp[60]) * 2 / 3
    temp[80] = temp[79] + (temp[82] - temp[79]) * 1 / 3
    temp[81] = temp[79] + (temp[82] - temp[79]) * 2 / 3
    # Generation of the repeated-series, with the base power demand repeated for the whole duration
    temp = temp * round(37000/96)
    temp = temp[0:len(processed)]
    repeated = pd.Series(temp, index=processed.index)
    # The ratio between actual consumption and "predicted-normal" consumtpion is used as reference.
    temp = (processed["Demands:Electricity:Total:Edot"] / processed["Demands:Electricity:Total:Edot1D"]) / repeated
    processed["Demands:Electricity:Thrusters:Edot"] = processed["Demands:Electricity:Total:Edot"] - repeated * processed["Demands:Electricity:Total:Edot1D"]
    # The "repeated" values are only used when the ratio is larger than 1.1, that is assumed to be when the thrusters are on
    processed.loc[temp<1.1, "Demands:Electricity:Thrusters:Edot"] = 0
    processed["Demands:Electricity:Other:Edot"] = processed["Demands:Electricity:Other:Edot"] - processed["Demands:Electricity:Thrusters:Edot"]
    return processed



def heatDemand(processed, CONSTANTS, dict_structure):
    # This function calculates the heat demand from the on board systems
    db_index = processed.index
    processed["Demands:Heat:HotWaterHeater:Edot"] = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HOT_WATER_HEATER"] * pd.Series((round(len(processed)/96)*np.ndarray.tolist(np.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HWH_HOURLY"],4)))[:len(processed)], index=db_index)
    processed["Demands:Heat:HVACpreheater:Edot"] = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"] * (CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_INSIDE"] - processed["T_air"]) / (CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_INSIDE"] - CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_AIR_REF"])
    processed.loc[processed["Demands:Heat:HVACpreheater:Edot"] < 0.1 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"], "Demands:Heat:HVAC_preheater:Edot"] = 0 # The pre-heater is not working during summer
    processed["Demands:Heat:HVACreheater:Edot"] = processed["Demands:Electricity:HVAC:Edot"]
    processed["Demands:Heat:TankHeating:Edot"] = 0.5 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["TANK_HEATING"]
    processed.loc[:,"Demands:Heat:OtherTanks:Edot"] = 0.5 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["OTHER_TANKS"]
    processed.loc[:,"Demands:Heat:HFOtankHeating:Edot"] = 0.5 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HFO_TANK_HEATING"]
    processed["Demands:Heat:MachinerySpaceHeaters:Edot"] = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["MACHINERY_SPACE_HEATERS"] * (CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_INSIDE"] - processed["T_air"]) / (CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_INSIDE"] - CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_AIR_REF"])
    processed.loc[processed["Demands:Heat:HVACpreheater:Edot"] < 0.1 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"], "Demands:Heat:Machinery_space_heaters:Edot"] = 0  # The pre-heater is not working during summer
    processed["Demands:Heat:HFOheater:Edot"] = CONSTANTS["General"]["HFO"]["CP"] * (
        processed["AE1:Cyl:FuelPh_in:mdot"]+processed["AE2:Cyl:FuelPh_in:mdot"]+processed["AE3:Cyl:FuelPh_in:mdot"]+processed["AE4:Cyl:FuelPh_in:mdot"]+
        processed["ME1:Cyl:FuelPh_in:mdot"]+processed["ME2:Cyl:FuelPh_in:mdot"]+processed["ME3:Cyl:FuelPh_in:mdot"]+processed["ME4:Cyl:FuelPh_in:mdot"]) * 100
    processed["Demands:Heat:Galley:Edot"] = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY"] * pd.Series((round(len(processed) / 96) * np.ndarray.tolist(np.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY_HOURLY"], 4)))[:len(processed)],index=db_index)
    processed["Demands:Heat:Total:Edot"] = pd.Series(index=db_index)
    for flow in dict_structure["systems"]["Demands"]["units"]["Heat"]["flows"]:
        processed["Demands:Heat:Total:Edot"] = processed["Demands:Heat:Total:Edot"] + processed[d2df("Demands", "Heat", flow, "Edot")]
        if flow in dict_structure["systems"]["Steam"]["units"]:
            processed[d2df("Steam", flow, "Steam_in", "mdot")] = processed[d2df("Demands", "Heat", flow, "Edot")] / CONSTANTS["Steam"]["DH_STEAM"]
        elif flow in dict_structure["systems"]["HTHR"]["units"]:
            processed[d2df("HTHR", flow, "Qdot_out", "Edot")] = processed[d2df("Demands", "Heat", flow, "Edot")]
    return processed


def HTHR(processed, CONSTANTS):
    # Calculation of the total amount of heat available from the HRSGs
    # Calculation of the total amount of heat available from the HT systems (maybe useless)
    #heat_in_HT = pd.Series(index=processed.index)
    #for system in {"ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4"}:
    #    heat_in_HT = heat_in_HT + processed[d2df(system,"CAC_HT","HTWater_out","Edot")] - processed[d2df(system,"JWC","HTWater_in","Edot")]
    # Calculation of the conditions at the HTHR inlet, from the HT water side
    ER13set = {"AE1", "AE3", "ME1", "ME3"}
    ER24set = {"AE2", "AE4", "ME2", "ME4"}
    ER13off = ~processed["ME1:on"] & ~processed["ME3:on"] & ~processed["AE1:on"] & ~processed["AE3:on"]
    ER24off = ~processed["ME2:on"] & ~processed["ME4:on"] & ~processed["AE2:on"] & ~processed["AE4:on"]
    processed[d2df("CoolingSystems", "HTcollector13", "HTWater_out", "T")] = (
        sum(processed[d2df("CoolingSystems", "HTcollector13", "HTWater_" + idx + "_in", "T")] *
            processed[d2df("CoolingSystems", "HTcollector13", "HTWater_" + idx + "_in", "mdot")] for idx in ER13set) /
        sum(processed[d2df("CoolingSystems", "HTcollector13", "HTWater_" + idx + "_in", "mdot")] for idx in ER13set))
    # When all engines are off, there is no flow, so the temperature calculated above is NaN. Hence, we set it to T0
    processed.loc[ER13off,"CoolingSystems:HTcollector13:HTWater_out:T"] = processed["T_0"][ER13off]

    # Same thing for the HT collector, ER 2/4
    processed["CoolingSystems:HTcollector24:HTWater_out:T"] = (
        sum(processed[d2df("CoolingSystems", "HTcollector24", "HTWater_" + idx + "_in", "T")] *
            processed[d2df("CoolingSystems", "HTcollector24", "HTWater_" + idx + "_in", "mdot")] for idx in ER24set) /
        sum(processed[d2df("CoolingSystems", "HTcollector24", "HTWater_" + idx + "_in", "mdot")] for idx in ER24set))
    processed.loc[ER24off, "CoolingSystems:HTcollector24:HTWater_out:T"] = processed["T_0"][ER24off]

    # Now we need to calculate the conditions after the heat is given to the hot water heater, preheater, reheater
    processed["HTHR:HTHR24:HRWater_in:T"] = processed["HTHR:SteamHeater:HRWater_out:T"] - (
        processed["Demands:Heat:HotWaterHeater:Edot"] + processed["Demands:Heat:HVACreheater:Edot"] + processed["Demands:Heat:HVACpreheater:Edot"]
        ) / processed["HTHR:SteamHeater:HRWater_out:mdot"] / CONSTANTS["General"]["CP_WATER"]

    # Now, the conditions at the HTHR inputs from the HT side are given, so we can calculate the heat flow using the eps NTU method
    qdot_HTHR24 = CONSTANTS["MainEngines"]["EPS_CAC_HTSTAGE"] * processed["CoolingSystems:HTcollector24:HTWater_out:mdot"] * CONSTANTS["General"]["CP_WATER"] * (
        processed["CoolingSystems:HTcollector24:HTWater_out:T"] - processed[d2df("HTHR", "HTHR24", "HRWater_in", "T")])
    # Once again, to avoid risks, when all engines of the ER 24 are off, the heat flow here is 0
    qdot_HTHR24[ER24off] = 0
    qdot_HTHR24[qdot_HTHR24 < 0] = 0  # we assume that there is no possibility of back flow
    processed["HTHR:HTHR24:HRWater_out:T"] = processed["HTHR:HTHR24:HRWater_in:T"] + qdot_HTHR24 / processed["HTHR:SteamHeater:HRWater_out:mdot"] / CONSTANTS["General"]["CP_WATER"]
    processed["HTHR:HTHR24:HTWater_out:T"] = processed["CoolingSystems:HTcollector24:HTWater_out:T"] + qdot_HTHR24 / processed["HTHR:HTHR24:HTWater_in:mdot"] / CONSTANTS["General"]["CP_WATER"]

    # Finally, we can do the same for the HTHR 13 exchanger
    qdot_HTHR13 = CONSTANTS["MainEngines"]["EPS_CAC_HTSTAGE"] * processed["CoolingSystems:HTcollector13:HTWater_out:mdot"] * CONSTANTS["General"]["CP_WATER"] * (
        processed["CoolingSystems:HTcollector13:HTWater_out:T"] - processed[d2df("HTHR", "HTHR24", "HRWater_out", "T")])
    qdot_HTHR13[ER13off] = 0
    qdot_HTHR13[qdot_HTHR13 < 0] = 0
    processed["HTHR:HTHR13:HRWater_out:T"] = processed["HTHR:HTHR24:HRWater_out:T"] + qdot_HTHR13 / processed["HTHR:SteamHeater:HRWater_out:mdot"] / CONSTANTS["General"]["CP_WATER"]
    processed["HTHR:HTHR13:HTWater_out:T"] = processed["CoolingSystems:HTcollector13:HTWater_out:T"] + qdot_HTHR13 / processed["HTHR:HTHR13:HTWater_in:mdot"] / CONSTANTS["General"]["CP_WATER"]

    # Now, we know that the HR water before the users must be at 90 degrees
    processed["HTHR:SteamHeater:Steam_in:mdot"] = processed["HTHR:SteamHeater:HRWater_out:mdot"] * CONSTANTS["General"]["CP_WATER"] * (
        processed["HTHR:SteamHeater:HRWater_out:T"] - processed["HTHR:HTHR13:HRWater_out:T"]) / CONSTANTS["Steam"]["DH_STEAM"]

    # Now, what happens after the three heat exchangers? We assume equal temperature drop
    processed.loc[:,"HTHR:HTHRmerge:HRWater_HWH_in:T"] = processed["HTHR:HTHR24:HRWater_in:T"]
    processed.loc[:, "HTHR:HTHRmerge:HRWater_PreH_in:T"] = processed["HTHR:HTHR24:HRWater_in:T"]
    processed.loc[:, "HTHR:HTHRmerge:HRWater_ReH_in:T"] = processed["HTHR:HTHR24:HRWater_in:T"]

    # The so that the mass flow can easily be determined
    processed.loc[:, "HTHR:HTHRmerge:HRWater_HWH_in:mdot"] = processed["Demands:Heat:HotWaterHeater:Edot"] / (
        processed["HTHR:HTHRmerge:HRWater_HWH_in:T"] - processed["HTHR:HTHR24:HRWater_in:T"]) / CONSTANTS["General"]["CP_WATER"]
    processed.loc[:, "HTHR:HTHRmerge:HRWater_PreH_in:mdot"] = processed["Demands:Heat:HVACpreheater:Edot"] / (
        processed["HTHR:HTHRmerge:HRWater_PreH_in:T"] - processed["HTHR:HTHR24:HRWater_in:T"]) / CONSTANTS["General"]["CP_WATER"]
    processed.loc[:, "HTHR:HTHRmerge:HRWater_ReH_in:mdot"] = processed["Demands:Heat:HVACreheater:Edot"] / (
        processed["HTHR:HTHRmerge:HRWater_ReH_in:T"] - processed["HTHR:HTHR24:HRWater_in:T"]) / CONSTANTS["General"]["CP_WATER"]
    return processed



def steamSystems(processed, CONSTANTS):
    # This function assigns all calculations to the steam systems
    # First, we see how much heat is provided by the HRSGs
    heat_from_HRSG = pd.Series(index=processed.index)
    heat_from_HRSG[:] = 0
    for system in {"ME2", "ME3", "AE1", "AE2", "AE3", "AE4"}:
        heat_from_HRSG = heat_from_HRSG + processed[d2df(system,"HRSG","Steam_in","mdot")] * CONSTANTS["Steam"]["DH_STEAM"]
    # Then, we calculate the total demand of heat that needs to be fulfilled by the steam systems
    heat_steam = (processed["Demands:Heat:TankHeating:Edot"] + processed["Demands:Heat:OtherTanks:Edot"] +
                  processed["Demands:Heat:HFOtankHeating:Edot"] + processed["Demands:Heat:MachinerySpaceHeaters:Edot"] +
                  processed["Demands:Heat:HFOheater:Edot"] + processed["Demands:Heat:Galley:Edot"] +
                  processed["HTHR:SteamHeater:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
    # The auxiliary boilers must provide the difference between the demand and the available heat
    processed["Steam:Boiler1:Steam_in:mdot"] = (heat_steam - heat_from_HRSG) / CONSTANTS["Steam"]["DH_STEAM"]
    processed["Steam:Boiler1:FuelCh_in:Edot"] = processed["Steam:Boiler1:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] / CONSTANTS["OtherUnits"]["BOILER"]["ETA_DES"]
    processed["Steam:Boiler1:FuelPh_in:mdot"] = processed["Steam:Boiler1:FuelCh_in:Edot"] / CONSTANTS["General"]["HFO"]["LHV"]

    return processed