import numpy as np
import pandas as pd
from helpers import d2df
import datetime as dt
import preprocessingO as ppo


def auxPowerAnalysis(processed, CONSTANTS, dict_structure, dataset_raw, header_names):
    # Calculating the total auxiliary power demand
    processed = auxPowerTotalDemand(processed)
    processed = propPowerDemand(processed, CONSTANTS)
    # Calculating the contribution from the thrusters
    #processed = thrusters(processed, CONSTANTS)  # The second method works better. But I still keep it
    processed = thrusters(processed, CONSTANTS)
    # Assigning the operational mode
    processed = ppo.operationalModeCalculator(processed, dataset_raw, CONSTANTS, header_names)

    processed = HVAC(processed, CONSTANTS)
    processed = heatDemand(processed, CONSTANTS, dict_structure)
    processed = HTHR(processed, CONSTANTS)
    processed = steamSystems(processed, CONSTANTS, dataset_raw, header_names)
    return processed



def auxPowerTotalDemand(processed):
    processed["Demands:Electricity:Total:Edot"] = processed["AE1:AG:Power_out:Edot"]+processed["AE2:AG:Power_out:Edot"]+processed["AE3:AG:Power_out:Edot"]+processed["AE4:AG:Power_out:Edot"]
    # We also need to store (for further use) a series made of the daily averages
    processed["Demands:Electricity:Total:Edot1D"] = processed["Demands:Electricity:Total:Edot"].resample('1D').mean().reindex(processed["Demands:Electricity:Total:Edot"].index, method='ffill')
    processed["Demands:Electricity:Other:Edot"] = processed["Demands:Electricity:Total:Edot"]
    return processed


def propPowerDemand(processed, CONSTANTS):
    # Looking at the first propulsion line, for engines 1 and 2
    processed["Propulsion:Gearbox1:Power_in1:Edot"] = processed["ME1:Cyl:Power_out:Edot"]
    processed["Propulsion:Gearbox1:Power_in2:Edot"] = processed["ME2:Cyl:Power_out:Edot"]
    processed["Propulsion:Gearbox1:Power_out:Edot"] = (processed["Propulsion:Gearbox1:Power_in1:Edot"] + processed["Propulsion:Gearbox1:Power_in2:Edot"]) * CONSTANTS["OtherUnits"]["PROPULSION"]["ETA_GB"]
    processed["Propulsion:Gearbox1:Losses:Edot"] = (processed["Propulsion:Gearbox1:Power_in1:Edot"] + processed["Propulsion:Gearbox1:Power_in2:Edot"]) - processed["Propulsion:Gearbox1:Power_out:Edot"]
    processed["Propulsion:Shaft1:Power_in:Edot"] = processed["Propulsion:Gearbox1:Power_out:Edot"]
    processed["Propulsion:Shaft1:Power_out:Edot"] = processed["Propulsion:Gearbox1:Power_out:Edot"] * CONSTANTS["OtherUnits"]["PROPULSION"]["ETA_SH"]
    processed["Propulsion:Shaft1:Losses:Edot"] = processed["Propulsion:Gearbox1:Power_out:Edot"] * (1- CONSTANTS["OtherUnits"]["PROPULSION"]["ETA_SH"])
    processed["Propulsion:Propeller1:Power_in:Edot"] = processed["Propulsion:Shaft1:Power_out:Edot"]
    processed["Demands:Mechanical:Propeller1:Edot"] = processed["Propulsion:Propeller1:Power_in:Edot"]
    # And now we go to the second propulsion line, engines 3 and 4
    processed["Propulsion:Gearbox2:Power_in1:Edot"] = processed["ME3:Cyl:Power_out:Edot"]
    processed["Propulsion:Gearbox2:Power_in2:Edot"] = processed["ME4:Cyl:Power_out:Edot"]
    processed["Propulsion:Gearbox2:Power_out:Edot"] = (processed["Propulsion:Gearbox2:Power_in1:Edot"] + processed["Propulsion:Gearbox2:Power_in2:Edot"]) * CONSTANTS["OtherUnits"]["PROPULSION"]["ETA_GB"]
    processed["Propulsion:Gearbox2:Losses:Edot"] = (processed["Propulsion:Gearbox2:Power_in1:Edot"] + processed["Propulsion:Gearbox2:Power_in2:Edot"]) - processed["Propulsion:Gearbox2:Power_out:Edot"]
    processed["Propulsion:Shaft2:Power_in:Edot"] = processed["Propulsion:Gearbox2:Power_out:Edot"]
    processed["Propulsion:Shaft2:Power_out:Edot"] = processed["Propulsion:Gearbox2:Power_out:Edot"] * CONSTANTS["OtherUnits"]["PROPULSION"]["ETA_SH"]
    processed["Propulsion:Shaft2:Losses:Edot"] = processed["Propulsion:Gearbox2:Power_out:Edot"] * (1 - CONSTANTS["OtherUnits"]["PROPULSION"]["ETA_SH"])
    processed["Propulsion:Propeller2:Power_in:Edot"] = processed["Propulsion:Shaft2:Power_out:Edot"]
    processed["Demands:Mechanical:Propeller2:Edot"] = processed["Propulsion:Propeller2:Power_in:Edot"]
    # Finally, total mechanical power demand
    processed["Demands:Mechanical:Total:Edot"] = processed["Propulsion:Propeller1:Power_in:Edot"] + processed["Propulsion:Propeller2:Power_in:Edot"]
    return processed



def HVAC(processed, CONSTANTS):
    # The idea of the calculation of the HVAC demand, very much simplified, lies in saying that during the summer monhs
    # the HVAC demand is the difference between the average consumption before summer AND the instananteous one.
    mask = (processed.index > CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SUMMER_START"]) & (processed.index <= CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SUMMER_END"])
    processed["Demands:Electricity:HVAC:Edot"] = processed["Demands:Electricity:Total:Edot1D"] - (processed["Demands:Electricity:Total:Edot1D"][processed.index < CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SUMMER_START"]]).mean()/2 - (processed["Demands:Electricity:Total:Edot1D"][processed.index > CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SUMMER_END"]]).mean()/2
    processed.loc[~mask,"Demands:Electricity:HVAC:Edot"] = 0
    processed["Demands:Electricity:Other:Edot"] = processed["Demands:Electricity:Other:Edot"] - processed["Demands:Electricity:HVAC:Edot"]
    return processed


def thrusters(processed, CONSTANTS):
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

    # Let's make some reasonable assumption on the number of passengers, given the data that we have:
    # - Assumption # 1: during summer, we have a more or less constant number of passengers equal to the average between
    #   midsummer and the 15th of August
    # - During the rest of the season, we take for each day the average number of passengers during that day for the season

    # HVAC Reheater
    processed["Demands:Heat:HVACreheater:Edot"] = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["HVAC_REHEATER"] * (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["HVAC_REHEATER"] * processed["Demands:Electricity:HVAC:Edot"] / processed["Demands:Electricity:HVAC:Edot"].max())
    processed.loc[processed["Demands:Electricity:HVAC:Edot"] <= 0,"Demands:Heat:HVACreheater:Edot"] = 0
    # Hot water heater
    processed["Demands:Heat:HotWaterHeater:Edot"] = (CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["HOT_WATER_HEATER"] * (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["HOT_WATER_HEATER"] * processed["Passengers_calc"] / 1800 * (
        pd.Series((round(len(processed) / 96) *
                   np.ndarray.tolist(np.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HWH_HOURLY"], 4)))[:len(processed)], index=db_index))) +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["OTHER_HTHR"])
    # HVAC Preheater
    temp = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["HVAC_PREHEATER"] * (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["HVAC_PREHEATER"] * (297 - processed["T_air"]) / (297 - 248))  - 0.100 * processed["Passengers_calc"]
    temp[processed["Demands:Electricity:HVAC:Edot"] > 20] = 0  # The preheater is never used when the AC compressors are on
    processed["Demands:Heat:HVACpreheater:Edot"] = temp  # The pre-heater is not working during summer
    # Galley
    processed["Demands:Heat:Galley:Edot"] = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["GALLEY"] * (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["GALLEY"] * pd.Series((round(len(processed) / 96) * np.ndarray.tolist(
        np.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY_HOURLY"], 4)))[:len(processed)], index=db_index))
    # Tank heating
    processed["Demands:Heat:TankHeating:Edot"] = (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["OTHER_STEAM"] / 4 +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["TANK_HEATING"] *
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["OTHER_CONSUMERS"] * processed["T_air"] / 298)
    # Other tanks
    processed["Demands:Heat:OtherTanks:Edot"] = (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["OTHER_STEAM"] / 4 +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["OTHER_TANKS"] *
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["OTHER_CONSUMERS"] * processed["T_air"] / 298)
    # HFO tanks
    processed["Demands:Heat:HFOtankHeating:Edot"] = (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["OTHER_STEAM"] / 4 +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["HFO_TANK_HEATING"] *
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["OTHER_CONSUMERS"] * processed["T_air"] / 298)
    # Machinery space heaters
    processed["Demands:Heat:MachinerySpaceHeaters:Edot"] = (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["OTHER_STEAM"] / 4 +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["DESIGN"]["MACHINERY_SPACE_HEATERS"] *
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["LIN"]["OTHER_CONSUMERS"] * processed["T_air"] / 298)
    # HFO heaters
    processed["Demands:Heat:HFOheater:Edot"] = CONSTANTS["General"]["HFO"]["CP"] * (
        processed["AE1:Cyl:FuelPh_in:mdot"] + processed["AE2:Cyl:FuelPh_in:mdot"] + processed[
            "AE3:Cyl:FuelPh_in:mdot"] + processed["AE4:Cyl:FuelPh_in:mdot"] +
        processed["ME1:Cyl:FuelPh_in:mdot"] + processed["ME2:Cyl:FuelPh_in:mdot"] + processed[
            "ME3:Cyl:FuelPh_in:mdot"] + processed["ME4:Cyl:FuelPh_in:mdot"]) * (150 - 80)

    # Updating the steam mass flows
    processed.loc[:,"Demands:Heat:Total:Edot"] = 0
    for flow in dict_structure["systems"]["Demands"]["units"]["Heat"]["flows"]:
        if flow == "Total":
            pass
        else:
            processed["Demands:Heat:Total:Edot"] = processed["Demands:Heat:Total:Edot"] + processed[d2df("Demands", "Heat", flow, "Edot")]
        if flow in dict_structure["systems"]["Steam"]["units"]:
            processed[d2df("Steam", flow, "Steam_in", "mdot")] = processed[d2df("Demands", "Heat", flow, "Edot")] / CONSTANTS["Steam"]["DH_STEAM"]
        elif flow in dict_structure["systems"]["HTHR"]["units"]:
            processed[d2df("HTHR", flow, "Qdot_out", "Edot")] = processed[d2df("Demands", "Heat", flow, "Edot")]

    # Calculating the total demand
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
    # Case 1: we have made an assumption on the mass flow of water
    if sum(processed["HTHR:HTHR24:HRWater_in:T"].isnull()) == len(processed):
        processed["HTHR:HTHR24:HRWater_in:T"] = processed["HTHR:SteamHeater:HRWater_out:T"] - (
            processed["Demands:Heat:HotWaterHeater:Edot"] + processed["Demands:Heat:HVACreheater:Edot"] + processed["Demands:Heat:HVACpreheater:Edot"]
            ) / processed["HTHR:SteamHeater:HRWater_out:mdot"] / CONSTANTS["General"]["CP_WATER"]
    elif sum(processed["HTHR:SteamHeater:HRWater_out:mdot"].isnull()) == len(processed):
    # Case 2: we have made an assumption on the HTHR inlet temperature
        processed["HTHR:SteamHeater:HRWater_out:mdot"] = (processed["Demands:Heat:HotWaterHeater:Edot"] +
            processed["Demands:Heat:HVACreheater:Edot"] + processed["Demands:Heat:HVACpreheater:Edot"]
            ) / (processed["HTHR:SteamHeater:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"]) / CONSTANTS["General"]["CP_WATER"]
    else:
        print("Error: the two variables that were supposed to be calculated are both available")

    # We should be able to proceed in both cases
    mdot_min24 = pd.concat([processed["HTHR:SteamHeater:HRWater_out:mdot"], processed["CoolingSystems:HTcollector24:HTWater_out:mdot"]], axis=1).min(axis=1)
    mdot_min13 = pd.concat([processed["HTHR:SteamHeater:HRWater_out:mdot"], processed["CoolingSystems:HTcollector13:HTWater_out:mdot"]],axis=1).min(axis=1)
    # Now, the conditions at the HTHR inputs from the HT side are given, so we can calculate the heat flow using the eps NTU method
    qdot_HTHR24 = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HTHR_EPS"] * mdot_min24 * CONSTANTS["General"]["CP_WATER"] * (
        processed["CoolingSystems:HTcollector24:HTWater_out:T"] - processed[d2df("HTHR", "HTHR24", "HRWater_in", "T")])
    # Once again, to avoid risks, when all engines of the ER 24 are off, the heat flow here is 0
    qdot_HTHR24[ER24off] = 0
    qdot_HTHR24[qdot_HTHR24 < 0] = 0  # we assume that there is no possibility of back flow
    processed["HTHR:HTHR24:HRWater_out:T"] = processed["HTHR:HTHR24:HRWater_in:T"] + qdot_HTHR24 / processed["HTHR:SteamHeater:HRWater_out:mdot"] / CONSTANTS["General"]["CP_WATER"]
    processed.loc[ER24off, "HTHR:HTHR24:HRWater_out:T"] = processed["HTHR:HTHR24:HRWater_in:T"]
    processed["HTHR:HTHR24:HTWater_out:T"] = processed["CoolingSystems:HTcollector24:HTWater_out:T"] - qdot_HTHR24 / processed["HTHR:HTHR24:HTWater_in:mdot"] / CONSTANTS["General"]["CP_WATER"]
    processed.loc[ER24off, "HTHR:HTHR24:HTWater_out:T"] = processed["CoolingSystems:HTcollector24:HTWater_out:T"]

    # Finally, we can do the same for the HTHR 13 exchanger
    qdot_HTHR13 = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HTHR_EPS"] * mdot_min13 * CONSTANTS["General"]["CP_WATER"] * (
        processed["CoolingSystems:HTcollector13:HTWater_out:T"] - processed[d2df("HTHR", "HTHR24", "HRWater_out", "T")])
    qdot_HTHR13[ER13off] = 0
    qdot_HTHR13[qdot_HTHR13 < 0] = 0
    processed["HTHR:HTHR13:HRWater_out:T"] = processed["HTHR:HTHR24:HRWater_out:T"] + qdot_HTHR13 / processed["HTHR:SteamHeater:HRWater_out:mdot"] / CONSTANTS["General"]["CP_WATER"]
    processed.loc[ER13off, "HTHR:HTHR13:HRWater_out:T"] = processed["HTHR:HTHR24:HRWater_out:T"]
    processed["HTHR:HTHR13:HTWater_out:T"] = processed["CoolingSystems:HTcollector13:HTWater_out:T"] - qdot_HTHR13 / processed["HTHR:HTHR13:HTWater_in:mdot"] / CONSTANTS["General"]["CP_WATER"]
    processed.loc[ER13off, "HTHR:HTHR13:HTWater_out:T"] = processed["CoolingSystems:HTcollector13:HTWater_out:T"]

    # Now, we know that the HR water before the users must be at 90 degrees
    processed["HTHR:SteamHeater:Steam_in:mdot"] = processed["HTHR:SteamHeater:HRWater_out:mdot"] * CONSTANTS["General"]["CP_WATER"] * (
        processed["HTHR:SteamHeater:HRWater_out:T"] - processed["HTHR:HTHR13:HRWater_out:T"]) / CONSTANTS["Steam"]["DH_STEAM"]
    # Avoiding the case of the steam heater having a negative mass flow
    #processed.loc[processed["HTHR:SteamHeater:Steam_in:mdot"] < 0, "HTHR:SteamHeater:Steam_in:mdot"] = 0

    # Now, what happens after the three heat exchangers? We assume equal temperature drop
    processed["HTHR:HTHRmerge:HRWater_HWH_in:T"] = processed["HTHR:HTHR24:HRWater_in:T"]
    processed["HTHR:HTHRmerge:HRWater_PreH_in:T"] = processed["HTHR:HTHR24:HRWater_in:T"]
    processed["HTHR:HTHRmerge:HRWater_ReH_in:T"] = processed["HTHR:HTHR24:HRWater_in:T"]

    # The so that the mass flow can easily be determined
    processed["HTHR:HTHRmerge:HRWater_HWH_in:mdot"] = processed["Demands:Heat:HotWaterHeater:Edot"] / (
        processed["HTHR:SteamHeater:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"]) / CONSTANTS["General"]["CP_WATER"]
    processed["HTHR:HTHRmerge:HRWater_PreH_in:mdot"] = processed["Demands:Heat:HVACpreheater:Edot"] / (
        processed["HTHR:SteamHeater:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"]) / CONSTANTS["General"]["CP_WATER"]
    processed["HTHR:HTHRmerge:HRWater_ReH_in:mdot"] = processed["Demands:Heat:HVACreheater:Edot"] / (
        processed["HTHR:SteamHeater:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"]) / CONSTANTS["General"]["CP_WATER"]
    return processed



def steamSystems(processed, CONSTANTS, dataset_raw, header_names):
    db_index = processed.index
    # This function assigns all calculations to the steam systems
    Qdot_ab = pd.Series(index=db_index)
    Qdot_ab[:] = 0
    # First, we see how much heat is provided by the HRSGs
    Qdot_hrsg = pd.Series(index=db_index)
    Qdot_hrsg[:] = 0
    for system in {"ME2", "ME3", "AE1", "AE2", "AE3", "AE4"}:
        Qdot_hrsg = Qdot_hrsg + processed[d2df(system,"HRSG","Steam_in","mdot")] * CONSTANTS["Steam"]["DH_STEAM"]
    # Then, we calculate the total demand of heat that needs to be fulfilled by the steam systems
    Qdot_steam = (processed["Demands:Heat:TankHeating:Edot"] + processed["Demands:Heat:OtherTanks:Edot"] +
                  processed["Demands:Heat:HFOtankHeating:Edot"] + processed["Demands:Heat:MachinerySpaceHeaters:Edot"] +
                  processed["Demands:Heat:HFOheater:Edot"] + processed["Demands:Heat:Galley:Edot"] +
                  processed["HTHR:SteamHeater:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])

    Qdot_ab = np.zeros(len(db_index))
    Qboiler = np.zeros(len(db_index) + 1)
    Qboiler[0] = CONSTANTS["OtherUnits"]["BOILER"]["STORAGE_SIZE"]
    Qdot_dumped = np.zeros(len(db_index))
    Qdot_steam = Qdot_steam.values

    for idx in range(len(db_index)):
        if idx == 0:
            pass
        else:
            test = Qboiler[idx] + (Qdot_hrsg[idx] - Qdot_steam[idx]) * 60 * 15
            if Qdot_ab[idx - 1] > 0:
                if test + CONSTANTS["OtherUnits"]["BOILER"]["REFERENCE_POWER"] * 60 * 15 > CONSTANTS["OtherUnits"]["BOILER"]["STORAGE_SIZE"]:
                    Qdot_ab[idx] = 0
                else:
                    Qdot_ab[idx] = CONSTANTS["OtherUnits"]["BOILER"]["REFERENCE_POWER"]
            elif test <= 0:
                Qdot_ab[idx] = CONSTANTS["OtherUnits"]["BOILER"]["REFERENCE_POWER"]
            elif test > CONSTANTS["OtherUnits"]["BOILER"]["STORAGE_SIZE"]:
                Qdot_dumped[idx] = (test - CONSTANTS["OtherUnits"]["BOILER"]["STORAGE_SIZE"]) / 60 / 15
            else:
                pass
        Qboiler[idx + 1] = Qboiler[idx] + (Qdot_hrsg[idx] + Qdot_ab[idx] - Qdot_dumped[idx] - Qdot_steam[idx]) * 60 * 15

    # Converting Numpy arrays into Pandas Series
    Qdot_ab = pd.Series(data=Qdot_ab, index=db_index)
    Qdot_dumped = pd.Series(data=Qdot_dumped, index=db_index)
    Qdot_hrsg = pd.Series(data=Qdot_hrsg, index=db_index)
    Qdot_steam = pd.Series(data=Qdot_steam, index=db_index)

    # Adding the boiler flow
    processed["Steam:Boiler1:Steam_out:mdot"] = (Qdot_steam + Qdot_dumped) / CONSTANTS["Steam"]["DH_STEAM"]
    processed["Steam:Boiler1:Steam_HotWell_in:mdot"] = Qdot_ab / CONSTANTS["Steam"]["DH_STEAM"]
    # Including the "Energy Storage" flows
    Qdot_storage = Qdot_ab + Qdot_hrsg - Qdot_steam - Qdot_dumped
    processed.loc[Qdot_storage >= 0, "Steam:Boiler1:Steam_TES_out:mdot"] = Qdot_storage[Qdot_storage >= 0] / CONSTANTS["Steam"]["DH_STEAM"]  # When there is excess steam, it goes to the storage
    processed.loc[Qdot_storage < 0, "Steam:Boiler1:Steam_TES_out:mdot"] = 0
    processed.loc[Qdot_storage < 0, "Steam:Boiler1:Steam_TES_in:mdot"] = -Qdot_storage[Qdot_storage < 0] / CONSTANTS["Steam"]["DH_STEAM"] # When the steam balance is negative, it becomes an input
    processed.loc[Qdot_storage >= 0, "Steam:Boiler1:Steam_TES_in:mdot"] = 0
    # Adding the steam dumped
    processed["Steam:HotWell:LTWater_in:mdot"]= Qdot_dumped / CONSTANTS["General"]["CP_WATER"] / 20
    processed["Steam:HotWell:Steam_Dumped_in:mdot"] = Qdot_dumped / CONSTANTS["Steam"]["DH_STEAM"]
    # The temperature of the LT water inlet to the hot well is calculated as a weighted average of all the input temperatures
    processed["Steam:HotWell:LTWater_in:T"] = (
        processed["CoolingSystems:LTdistribution13:LTWater_AE1_out:T"] * processed["CoolingSystems:LTdistribution13:LTWater_AE1_out:mdot"] +
        processed["CoolingSystems:LTdistribution13:LTWater_AE3_out:T"] * processed["CoolingSystems:LTdistribution13:LTWater_AE3_out:mdot"] +
        processed["CoolingSystems:LTdistribution13:LTWater_ME1_out:T"] * processed["CoolingSystems:LTdistribution13:LTWater_ME1_out:mdot"] +
        processed["CoolingSystems:LTdistribution13:LTWater_ME3_out:T"] * processed["CoolingSystems:LTdistribution13:LTWater_ME3_out:mdot"]) / (
        processed["CoolingSystems:LTdistribution13:LTWater_AE1_out:mdot"] +
        processed["CoolingSystems:LTdistribution13:LTWater_AE3_out:mdot"] +
        processed["CoolingSystems:LTdistribution13:LTWater_ME1_out:mdot"] +
        processed["CoolingSystems:LTdistribution13:LTWater_ME3_out:mdot"])
    processed.loc[processed["Steam:HotWell:LTWater_in:T"].isnull(),"Steam:HotWell:LTWater_in:T"] = processed["Steam:HotWell:LTWater_in:T"].mean()
    processed["Steam:HotWell:LTWater_out:T"] = processed["Steam:HotWell:LTWater_in:T"] + Qdot_dumped / CONSTANTS["General"]["CP_WATER"] / processed["Steam:HotWell:LTWater_in:mdot"]
    # To avoid NaN values, the LT water outlet temperature is equal to the inlet when the Qdot_dumped is equal to 0
    processed.loc[Qdot_dumped == 0, "Steam:HotWell:LTWater_out:T"] = processed["Steam:HotWell:LTWater_in:T"][Qdot_dumped == 0]
    # Calculating fuel flows
    processed["Steam:Boiler1:FuelCh_in:Edot"] = processed["Steam:Boiler1:Steam_HotWell_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] / CONSTANTS["OtherUnits"]["BOILER"]["ETA_DES"]
    processed.loc[processed["OperationalMode"] == "Port/Stay", "Steam:Boiler1:FuelPh_in:mdot"] = processed["Steam:Boiler1:FuelCh_in:Edot"][processed["OperationalMode"] == "Port/Stay"] / CONSTANTS["General"]["MDO"]["LHV"]
    processed.loc[processed["OperationalMode"] != "Port/Stay", "Steam:Boiler1:FuelPh_in:mdot"] = processed["Steam:Boiler1:FuelCh_in:Edot"][processed["OperationalMode"] != "Port/Stay"] / CONSTANTS["General"]["MDO"]["HHV"]
    processed.loc[processed["OperationalMode"] == "Port/Stay", "Steam:Boiler1:FuelPh_in:T"] = 60 + 273.15
    processed.loc[processed["OperationalMode"] != "Port/Stay", "Steam:Boiler1:FuelPh_in:T"] = 90 + 273.15
    # Calculating air flows
    processed["Steam:Boiler1:Air_in:mdot"] = processed["Steam:Boiler1:FuelPh_in:mdot"] * CONSTANTS["OtherUnits"]["BOILER"]["LAMBDA"]
    # Calculating exhaust flows
    processed["Steam:Boiler1:EG_out:mdot"] = processed["Steam:Boiler1:Air_in:mdot"] + processed["Steam:Boiler1:FuelPh_in:mdot"]
    processed["Steam:Boiler1:EG_out:T"] = processed["T_0"] + (
        processed["Steam:Boiler1:FuelCh_in:Edot"] * (1-CONSTANTS["OtherUnits"]["BOILER"]["ETA_DES"]) +
        processed["Steam:Boiler1:Air_in:mdot"] * CONSTANTS["General"]["CP_AIR"] * (processed["Steam:Boiler1:Air_in:T"] - processed["T_0"])) / (
        processed["Steam:Boiler1:EG_out:mdot"] * CONSTANTS["General"]["CP_EG"])
    processed.loc[processed["Steam:Boiler1:EG_out:T"].isnull(), "Steam:Boiler1:EG_out:T"] = processed["T_0"]
    processed.loc[:,"Steam:Boiler1:on"] = True  # With the new defition of the thermal systems, the steam boiler is always on


    return processed



