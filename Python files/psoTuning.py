import pandas as pd
import numpy as np
import preprocessingME as ppm
import preprocessingAE as ppa
import constants as kk
from pyswarm import pso

preparation()

def preparation():
    CONSTANTS = kk.constantsSetting()
    processed_temp = pd.read_hdf(CONSTANTS["filenames"]["dataset_output"], 'processed')
    data = pd.DataFrame(index=processed_temp.index)
    indexes_2_save = {"Passengers_calc", "Demands:Electricity:HVAC:Edot", "T_air",
                      "AE1:Cyl:FuelPh_in:mdot", "AE2:Cyl:FuelPh_in:mdot", "AE3:Cyl:FuelPh_in:mdot", "AE4:Cyl:FuelPh_in:mdot",
                      "ME1:Cyl:FuelPh_in:mdot", "ME2:Cyl:FuelPh_in:mdot", "ME3:Cyl:FuelPh_in:mdot","ME4:Cyl:FuelPh_in:mdot",
                      "ME2:HRSG:Steam_in:mdot", "ME3:HRSG:Steam_in:mdot",
                      "AE1:HRSG:Steam_in:mdot", "AE2:HRSG:Steam_in:mdot", "AE3:HRSG:Steam_in:mdot", "AE4:HRSG:Steam_in:mdot",
                      "CoolingSystems:HTcollector24:HTWater_out:mdot", "CoolingSystems:HTcollector13:HTWater_out:mdot",
                      "CoolingSystems:HTcollector24:HTWater_out:T", "CoolingSystems:HTcollector13:HTWater_out:T",
                      "ME1:on", "ME2:on", "ME3:on", "ME4:on", "AE1:on", "AE2:on", "AE3:on", "AE4:on"
                      }
    for idx in indexes_2_save:
        data[idx] = processed_temp[idx]

    # Prepare the input
    constant_input = (data, CONSTANTS)
    # Set the boundaries
    lb = [0, 0, 0, 0, 0, 0, 0, 0]
    ub = [1, 1, 1, 1, 1, 1, 1, 1]
    # Launch the optimization
    xopt, fopt = pso(fitnessFunction, lb, ub, args=constant_input)

def fitnessFunction(param, *args):
    (data, CONSTANTS) = args

    db_index = data.index
    ## CALCULATING DEMANDS
    # Re-heater
    Qdot_rh = (param[0] + param[1] * data["Wdot_hvac"]) * CONSTANTS["OtherUnits"][]
    # Hot water heater
    Qdot_hwh = param[2] * data["Passengers_calc"] / 1800 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HOT_WATER_HEATER"] * (
        pd.Series((round(len(data) / 96) * np.ndarray.tolist(np.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HWH_HOURLY"], 4)))[:len(data)],index=db_index))
    temp = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"] * (
    CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_AIR_REF_MAX"] - data["T_air"]) / (
           CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["T_AIR_REF_MAX"] - CONSTANTS["OtherUnits"]["HEAT_DEMAND"][
               "T_AIR_REF_MIN"]) - param[3] * data["Passengers_calc"]
    temp[temp < 0.1 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"]] = 0
    Qdot_ph = param[4] * temp  # The pre-heater is not working during summer
    Qdot_galley = param[5] * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY"] * pd.Series((round(len(data) / 96) * np.ndarray.tolist(
        np.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY_HOURLY"], 4)))[:len(data)], index=db_index)
    Qdot_other = (
        0.5 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["TANK_HEATING"] +
        0.5 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["OTHER_TANKS"] +
        0.5 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HFO_TANK_HEATING"] +
        CONSTANTS["General"]["HFO"]["CP"] * (
            data["AE1:Cyl:FuelPh_in:mdot"] + data["AE2:Cyl:FuelPh_in:mdot"] + data[
                "AE3:Cyl:FuelPh_in:mdot"] + data["AE4:Cyl:FuelPh_in:mdot"] +
            data["ME1:Cyl:FuelPh_in:mdot"] + data["ME2:Cyl:FuelPh_in:mdot"] + data[
                "ME3:Cyl:FuelPh_in:mdot"] + data["ME4:Cyl:FuelPh_in:mdot"]) * 100)

    ## Calculation generation
    Qdot_hrsg13 = (data["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
    Qdot_hrsg24 = (data["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])

    # HTHR
    mdot_hr = (Qdot_hwh + Qdot_rh + Qdot_ph) / (90+237.15 - param[6]) / CONSTANTS["General"]["CP_WATER"]
    ER13off = ~data["ME1:on"] & ~data["ME3:on"] & ~data["AE1:on"] & ~data["AE3:on"]
    ER24off = ~data["ME2:on"] & ~data["ME4:on"] & ~data["AE2:on"] & ~data["AE4:on"]
    # We should be able to proceed in both cases
    mdot_min24 = pd.concat([mdot_hr, data["CoolingSystems:HTcollector24:HTWater_out:mdot"]],axis=1).min(axis=1)
    mdot_min13 = pd.concat([mdot_hr, data["CoolingSystems:HTcollector13:HTWater_out:mdot"]],axis=1).min(axis=1)
    # Now, the conditions at the HTHR inputs from the HT side are given, so we can calculate the heat flow using the eps NTU method
    Qdot_HTHR24 = pd.Series(index = db_index)
    Qdot_HTHR24 = CONSTANTS["MainEngines"]["EPS_CAC_HTSTAGE"] * mdot_min24 * CONSTANTS["General"]["CP_WATER"] * (
        data["CoolingSystems:HTcollector24:HTWater_out:T"] - param[6])
    # Once again, to avoid risks, when all engines of the ER 24 are off, the heat flow here is 0
    Qdot_HTHR24[ER24off] = 0
    Qdot_HTHR24[Qdot_HTHR24 < 0] = 0  # we assume that there is no possibility of back flow
    T_HR_intermediate = param[6] + Qdot_HTHR24 / mdot_hr / CONSTANTS["General"]["CP_WATER"]
    # Finally, we can do the same for the HTHR 13 exchanger
    Qdot_HTHR13 = pd.Series(index = db_index)
    Qdot_HTHR13 = CONSTANTS["MainEngines"]["EPS_CAC_HTSTAGE"] * mdot_min13 * CONSTANTS["General"]["CP_WATER"] * (
        data["CoolingSystems:HTcollector13:HTWater_out:T"] - T_HR_intermediate)
    Qdot_HTHR13[ER13off] = 0
    Qdot_HTHR13[Qdot_HTHR13 < 0] = 0


