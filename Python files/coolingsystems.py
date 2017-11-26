import numpy as np
import pandas as pd
from helpers import d2df
from helpers import polyvalHelperFunction
import fillerfunctions as ff


def engineCoolingSystemsCalculation(processed, CONSTANTS, engine_type):
    print("Started calculating analysis for {} cooling systems...".format(engine_type), end="", flush=True)
    # This function calculates the different flows related to the cooling systems of the main engines.
    for system in CONSTANTS["General"]["NAMES"][engine_type]:
        # Calculating the total energy flow going to the cooling systems, based on the energy balance on the engine
        energy_2_cooling = (processed[d2df(system,"Cyl","FuelCh_in","Edot")] +
            CONSTANTS["General"]["HFO"]["CP"] * processed[d2df(system,"Cyl","FuelPh_in","mdot")] * (processed[d2df(system,"Cyl","FuelPh_in","T")] - processed["T_0"]) -
            processed[d2df(system, "Cyl", "Power_out", "Edot")] -
            processed[d2df(system,"Turbine","Mix_out","Edot")] +
            processed[d2df(system,"Comp","Air_in","Edot")] -
            processed[d2df(system, "Cyl", "QdotRad_out", "Edot")])
        # Calculating the energy going to the charge air cooler, based on the estimated temperatures on the air line
        energy_2_cac = CONSTANTS["General"]["CP_AIR"] * processed[d2df(system,"Cyl","Air_in","mdot")] * (processed[d2df(system,"Comp","Air_out","T")] - processed[d2df(system,"Cyl","Air_in","T")])
        # Calculating the energy going to the HT cooling systems, based on interpolation from the project guide
        energy_2_ht_theoric = processed[system+":"+"load"].apply(polyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_HT"],)) * CONSTANTS[engine_type]["QDOT_HT_DES"]
        energy_2_lt_theoric = processed[system+":"+"load"].apply(polyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_LT"],)) * CONSTANTS[engine_type]["QDOT_LT_DES"]
        # The values calculated based on the project guide are reconciled based on the energy balance
        energy_2_ht = energy_2_cooling * energy_2_ht_theoric / (energy_2_ht_theoric + energy_2_lt_theoric)
        energy_2_ht[energy_2_ht.isnull()] = 0
        energy_2_lt = energy_2_cooling - energy_2_ht
        # The energy going to the CAC, HT stage is calculated assuming a 85% effectiveness of the heat exchanger
        energy_2_cac_ht = CONSTANTS[engine_type]["EPS_CAC_HTSTAGE"] * processed[d2df(system,"Comp","Air_in","mdot")] * CONSTANTS["General"]["CP_AIR"] * (
            processed[d2df(system,"Comp","Air_out","T")] - processed[d2df(system,"JWC","HTWater_in","T")])
        energy_2_cac_ht[energy_2_cac_ht<0] = 0
        # The energy going to the CAC, LT stage results as a consequence by thermal balance over the CAC
        energy_2_cac_lt = energy_2_cac - energy_2_cac_ht
        # The energy to the JWC results as a balance over the HT cooling systems
        # energy_2_jwc = energy_2_ht - energy_2_cac_ht
        energy_2_jwc = (energy_2_cooling - energy_2_cac) / 2
        processed[d2df(system,"JWC","QdotJW_in","Edot")] = energy_2_jwc
        processed[d2df(system, "Cyl", "QdotJW_out", "Edot")] = energy_2_jwc
        # The energy to the LOC results as a balance over the LT cooling systems
        # energy_2_loc = energy_2_lt - energy_2_cac_lt
        energy_2_loc = (energy_2_cooling - energy_2_cac) / 2
        # Finally, the temperatures in the flows are calculated based on the calculated energy and mass flow values
        # For LT, first we have the CAC, then the LOC
        processed[d2df(system,"CAC_LT","LTWater_out","T")] = processed[d2df(system,"CAC_LT","LTWater_in","T")] + energy_2_cac_lt / processed[d2df(system,"CAC_LT","LTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        processed[d2df(system,"LOC","LTWater_out","T")] = processed[d2df(system,"CAC_LT","LTWater_out","T")] + energy_2_loc / processed[d2df(system,"LOC","LTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        # For HT, first we have the JWC, then the CAC, HT
        processed[d2df(system,"JWC","HTWater_out","T")] = processed[d2df(system,"JWC","HTWater_in","T")] + energy_2_jwc / processed[d2df(system,"JWC","HTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        processed[d2df(system,"CAC_HT","HTWater_out","T")] = processed[d2df(system,"JWC","HTWater_out","T")] + energy_2_cac_ht / processed[d2df(system,"CAC_HT","HTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        # For the LOC, we know the outlet (lower) temperature, we calculate the inlet temperature
        processed[d2df(system,"LOC","LubOil_in","T")] = processed[d2df(system,"LOC","LubOil_out","T")] + energy_2_loc / processed[d2df(system,"LOC","LubOil_out","mdot")] / CONSTANTS["General"]["CP_LO"]
        # Now calculating the temperature of the air in the charge air cooler
        processed[d2df(system, "CAC_HT", "Air_out", "T")] = processed[d2df(system, "Comp", "Air_out", "T")] - energy_2_cac_ht / processed[d2df(system,"Cyl","Air_in","mdot")] / CONSTANTS["General"]["CP_AIR"]
        processed[d2df(system, "CAC_LT", "Air_out", "T")] = processed[d2df(system, "CAC_HT", "Air_out", "T")] - energy_2_cac_lt / processed[d2df(system, "Cyl", "Air_in", "mdot")] / CONSTANTS["General"]["CP_AIR"]
        # Finally, we have the HRSG (for some cases)
        if system == "ME1":
            aaa = 0
        if engine_type == "AuxEngines" or system in {"ME2", "ME3"}:
            processed[d2df(system,"HRSG","Steam_in","mdot")] = ((processed[d2df(system,"HRSG","Mix_in","h")] - processed[d2df(system,"HRSG","Mix_out","h")]) *
                processed[d2df(system, "HRSG", "Mix_in", "mdot")]  /
                (CONSTANTS["Steam"]["H_STEAM_VS"] - CONSTANTS["Steam"]["H_STEAM_LS"]))
            processed.loc[processed[d2df(system, "HRSG", "Steam_in", "mdot")]<0, d2df(system, "HRSG", "Steam_in", "mdot")] = 0
        # Calculation of the mass recirculating from the LT outlet to the HT inlet (not exactly...)
        processed[d2df(system, "HTmerge", "LTWater_in", "mdot")] = processed[d2df(system,"JWC","HTWater_out","mdot")] * (
            processed[d2df(system, "CAC_HT", "HTWater_out", "T")] - processed[d2df(system,"JWC","HTWater_in","T")]) / (
            processed[d2df(system, "CAC_HT", "HTWater_out", "T")] - CONSTANTS[engine_type]["T_COOLING_MIX"])
    print("...done!")
    return processed


def centralCoolingSystems(processed, CONSTANTS):

    # Doing the calculations for the 1-3 engine room
    ER13set = {"AE1", "AE3", "ME1", "ME3", "AB1"}
    # Calculating the temperature at the LT collector outlet
    mdot_temp = sum(processed[d2df("CoolingSystems", "LTcollector13", "LTWater_" + idx + "_in", "mdot")] for idx in ER13set)
    processed[d2df("CoolingSystems", "LTcollector13", "LTWater_out", "T")] = (
        (sum(processed[d2df("CoolingSystems", "LTcollector13", "LTWater_"+idx+"_in", "T")] *
            processed[d2df("CoolingSystems", "LTcollector13", "LTWater_"+idx+"_in", "mdot")] for idx in ER13set)) / (
            mdot_temp))
    processed.loc[mdot_temp == 0, d2df("CoolingSystems", "LTcollector13", "LTWater_out", "T")] = processed['T_0']
    # The temperature at the other output of the collector is the same
    processed["CoolingSystems:LTcollector13:HTWater_out:T"] = processed["CoolingSystems:LTcollector13:LTWater_out:T"]
    # Note that the temperature at the LT distribution inlet is calculated based on the average temperature at the LT collector outlets.
    # The idea is that we have different temperatures at different instants, and we need to average them
    mdot_temp = sum(processed[d2df("CoolingSystems", "LTdistribution13", "LTWater_" + idx + "_out", "mdot")] for idx in ER13set)
    processed[d2df("CoolingSystems", "LTdistribution13", "LTWater_in", "T")] = (
        sum(processed[d2df("CoolingSystems", "LTdistribution13", "LTWater_" + idx + "_out", "T")] *
            processed[d2df("CoolingSystems", "LTdistribution13", "LTWater_" + idx + "_out", "mdot")] for idx in ER13set) / (
        mdot_temp))
    processed.loc[mdot_temp==0, d2df("CoolingSystems", "LTdistribution13", "LTWater_in", "T")] = processed['T_0']
    # The temperature at the Sea water cooler outlet is then equal to the inlet to the distribution systems
    #processed[d2df("CoolingSystems", "SWC13", "LTWater_out", "T")] = processed[d2df("CoolingSystems", "LTdistribution13", "LTWater_in", "T")]

    # Doing the calculations for the "2-4 engine room
    ER24set = {"AE2", "AE4", "ME2", "ME4"}
    # Calculating the temperature at the LT collector outlet
    mdot_temp = sum(processed[d2df("CoolingSystems", "LTcollector24", "LTWater_" + idx + "_in", "mdot")] for idx in ER24set)
    processed[d2df("CoolingSystems", "LTcollector24", "LTWater_out", "T")] = (
        (sum(processed[d2df("CoolingSystems", "LTcollector24", "LTWater_" + idx + "_in", "T")] *
             processed[d2df("CoolingSystems", "LTcollector24", "LTWater_" + idx + "_in", "mdot")] for idx in ER24set)) / (
            mdot_temp))
    processed.loc[mdot_temp==0, d2df("CoolingSystems", "LTcollector24", "LTWater_out", "T")] = processed['T_0']
    processed["CoolingSystems:LTcollector24:HTWater_out:T"] = processed["CoolingSystems:LTcollector24:LTWater_out:T"]
    # Note that the temperature at the LT distribution inlet is calculated based on the average temperature at the LT collector outlets
    mdot_temp = sum(processed[d2df("CoolingSystems", "LTdistribution24", "LTWater_" + idx + "_out", "mdot")] for idx in ER24set)
    processed[d2df("CoolingSystems", "LTdistribution24", "LTWater_in", "T")] = (
        sum(processed[d2df("CoolingSystems", "LTdistribution24", "LTWater_" + idx + "_out", "T")] *
            processed[d2df("CoolingSystems", "LTdistribution24", "LTWater_" + idx + "_out", "mdot")] for idx in ER24set) / (
        mdot_temp))
    processed.loc[mdot_temp == 0, d2df("CoolingSystems", "LTdistribution24", "LTWater_in", "T")] = processed['T_0']

    # We can now calculate the flows into the LTHT merge for the ER 13
    mdot_HTHR13_tot = processed["CoolingSystems:LTHTmerge13:HTWater_ME1_out:mdot"] + processed["CoolingSystems:LTHTmerge13:HTWater_ME3_out:mdot"] + processed["CoolingSystems:LTHTmerge13:HTWater_AE1_out:mdot"] + processed["CoolingSystems:LTHTmerge13:HTWater_AE3_out:mdot"]
    processed["CoolingSystems:LTHTmerge13:HTWater_in:mdot"] = mdot_HTHR13_tot * (
        CONSTANTS["MainEngines"]["T_COOLING_MIX"] - processed["CoolingSystems:LTcollector13:HTWater_out:T"]) / (
        processed["CoolingSystems:LTHTmerge13:HTWater_in:T"] - processed["CoolingSystems:LTcollector13:HTWater_out:T"])
    # If the previously calculated mass flow is NaN, we set it equal to 0
    processed.loc[np.isnan(processed["CoolingSystems:LTHTmerge13:HTWater_in:mdot"]), "CoolingSystems:LTHTmerge13:HTWater_in:mdot"] = 0
    processed["CoolingSystems:LTHTmerge13:LTWater_in:mdot"] = mdot_HTHR13_tot - processed["CoolingSystems:LTHTmerge13:HTWater_in:mdot"]

    # We can now calculate the flows into the LTHT merge for the ER 24
    mdot_HTHR24_tot = processed["CoolingSystems:LTHTmerge24:HTWater_ME2_out:mdot"] + processed["CoolingSystems:LTHTmerge24:HTWater_ME4_out:mdot"] + processed["CoolingSystems:LTHTmerge24:HTWater_AE2_out:mdot"] + processed["CoolingSystems:LTHTmerge24:HTWater_AE4_out:mdot"]
    processed["CoolingSystems:LTHTmerge24:HTWater_in:mdot"] = mdot_HTHR24_tot * (
        CONSTANTS["MainEngines"]["T_COOLING_MIX"] - processed["CoolingSystems:LTcollector24:HTWater_out:T"]) / (
        processed["CoolingSystems:LTHTmerge24:HTWater_in:T"] - processed["CoolingSystems:LTcollector24:HTWater_out:T"])
    # If the previously calculated mass flow is NaN, we set it equal to 0
    processed.loc[np.isnan(processed["CoolingSystems:LTHTmerge24:HTWater_in:mdot"]), "CoolingSystems:LTHTmerge24:HTWater_in:mdot"] = 0
    processed["CoolingSystems:LTHTmerge24:LTWater_in:mdot"] = mdot_HTHR24_tot - processed["CoolingSystems:LTHTmerge24:HTWater_in:mdot"]

    return processed


def seaWaterCoolers(processed, CONSTANTS, dict_structure):
    # Calculations for the seaWaterCoolers
    processed[d2df("CoolingSystems", "SWC13", "SeaWater_in", "T")] = processed.loc[:, "T_0"]  # Inlet temperature equal to the sea water temperature
    processed[d2df("CoolingSystems", "SWC24", "SeaWater_in", "T")] = processed.loc[:, "T_0"]  # Inlet temperature equal to the sea water temperature
    dT_13 = processed[d2df("CoolingSystems", "SWC13", "SeaWater_out", "T")] - processed[d2df("CoolingSystems", "SWC13", "SeaWater_in", "T")]
    dT_13[dT_13 < 5] = 5
    dT_24 = processed[d2df("CoolingSystems", "SWC24", "SeaWater_out", "T")] - processed[d2df("CoolingSystems", "SWC24", "SeaWater_in", "T")]
    dT_24[dT_24 < 5] = 5
    processed[d2df("CoolingSystems", "SWC13", "SeaWater_in", "mdot")] = (
        processed[d2df("CoolingSystems", "SWC13", "LTWater_out", "mdot")] *
        (processed[d2df("CoolingSystems", "SWC13", "LTWater_in", "T")] - processed[d2df("CoolingSystems", "SWC13", "LTWater_out", "T")]) /
        (dT_13))
    processed[d2df("CoolingSystems", "SWC13", "SeaWater_out", "mdot")] = processed[d2df("CoolingSystems", "SWC13", "SeaWater_in", "mdot")]
    processed[d2df("CoolingSystems", "SWC24", "SeaWater_in", "mdot")] = (
        processed[d2df("CoolingSystems", "SWC24", "LTWater_out", "mdot")] *
        (processed[d2df("CoolingSystems", "SWC24", "LTWater_in", "T")] - processed[d2df("CoolingSystems", "SWC24", "LTWater_out", "T")]) /
        (dT_24))
    processed[d2df("CoolingSystems", "SWC24", "SeaWater_out", "mdot")] = processed[d2df("CoolingSystems", "SWC24", "SeaWater_in", "mdot")]
    # Extra calls to the mass balance calculation function to make sure all values are calculated
    (counter, processed) = ff.massFill(processed, dict_structure, CONSTANTS, "CoolingSystems", "SWC13", dict_structure["systems"]["CoolingSystems"]["units"]["SWC13"]["streams"], "extra-1")
    processed[d2df("CoolingSystems", "LTcollector13", "LTWater_out", "mdot")] = processed[d2df("CoolingSystems", "SWC13", "LTWater_in", "mdot")]
    (counter, processed) = ff.massFill(processed, dict_structure, CONSTANTS, "CoolingSystems", "LTcollector13", dict_structure["systems"]["CoolingSystems"]["units"]["LTcollector13"]["streams"],"extra-1")
    processed[d2df("CoolingSystems", "LTHTmerge13", "LTWater_in", "mdot")] = processed[d2df("CoolingSystems", "LTcollector13", "HTWater_out", "mdot")]
    return processed


def coolingFlows(processed, CONSTANTS, engine_type):
    print("Started calculating cooling flows for the {}...".format(engine_type), end="", flush=True)
    # This function calculates the different flows related to the cooling systems of the main engines.
    for system in CONSTANTS["General"]["NAMES"][engine_type]:
        processed.loc[processed[d2df(system, "JWC", "HTWater_in", "p")] < 150000,d2df(system, "JWC", "HTWater_in", "p")] = 190000
        processed.loc[processed[d2df(system, "CAC_LT", "LTWater_in", "p")] < 150000, d2df(system, "CAC_LT", "LTWater_in", "p")] = 190000
        head_HT = processed[d2df(system, "JWC", "HTWater_in", "p")][~processed[system+":on"]].mean()
        heat_LT = processed[d2df(system, "CAC_LT", "LTWater_in", "p")][~processed[system+":on"]].mean()
        # Mass flow in the LT water cooling systems
        processed[d2df(system, "CAC_LT", "LTWater_in", "mdot")] = pumpFlow(processed[d2df(system, "Cyl", "Power_out", "omega")],
                       processed[d2df(system, "CAC_LT", "LTWater_in", "p")], heat_LT, CONSTANTS, engine_type)
        processed.loc[:,d2df(system, "CAC_LT", "LTWater_in", "mdot")] = processed[d2df(system, "CAC_LT", "LTWater_in", "mdot")] / max(processed[d2df(system, "CAC_LT", "LTWater_in", "mdot")]) * CONSTANTS[engine_type]["MFR_LT"]
        processed.loc[processed[d2df(system, "CAC_LT", "LTWater_in", "mdot")] < 0,d2df(system, "CAC_LT", "LTWater_in", "mdot")] = 0
        processed.loc[processed[d2df(system, "CAC_LT", "LTWater_in", "mdot")] > CONSTANTS[engine_type]["MFR_LT"], d2df(system, "CAC_LT", "LTWater_in","mdot")] = CONSTANTS[engine_type]["MFR_LT"]
        # Mass flow in the HT water cooling systems
        processed[d2df(system, "JWC", "HTWater_in", "mdot")] = pumpFlow(processed[d2df(system, "Cyl", "Power_out", "omega")],
                       processed[d2df(system, "JWC", "HTWater_in", "p")], head_HT, CONSTANTS, engine_type)
        processed.loc[:, d2df(system, "JWC", "HTWater_in", "mdot")] = processed[d2df(system, "JWC", "HTWater_in","mdot")] / max(processed[d2df(system, "JWC", "HTWater_in", "mdot")]) * CONSTANTS[engine_type]["MFR_HT"] * 2
        processed.loc[processed[d2df(system, "JWC", "HTWater_in", "mdot")] < 0, d2df(system, "JWC", "HTWater_in","mdot")] = 0
        processed.loc[processed[d2df(system, "JWC", "HTWater_in", "mdot")] > CONSTANTS[engine_type]["MFR_HT"], d2df(system,"JWC","HTWater_in","mdot")] = CONSTANTS[engine_type]["MFR_HT"]
        # Mass flow in the lubricating oil cooler
        processed.loc[:, d2df(system, "LOC", "LubOil_out", "mdot")] = CONSTANTS[engine_type]["MFR_LO"]
    print("done!")
    return processed


def pumpFlow(rpm, pressure, static_head, CONSTANTS, engine_type):
    "Engine driven cooling water pump HT/LT for ME. Inputs engine-rpm and gauge-pressure [bar] CW."
    # The equation was derived from the pump diagram in the engine project manual at 500 rpm
    # H = -0.0004 Q^2 + 0.0317 Q + 28.47
    # pq-formula: ax^2 + bx + c = 0
    # Affinity laws
    #if pressure < 1:
    #    print('Out of domain, P')
    # The pump formula is for 500 rpm. So the pressure input must be scaled so
    # it "fits" the right rpm using the affinity laws
    # static_head = CONSTANTS[engine_type]["STATIC_HEAD"]
    H = (pressure - static_head) / (9.81 * 1000) * (CONSTANTS[engine_type]["RPM_DES"]/(rpm+1))**2

    a = CONSTANTS[engine_type]["POLY_H_2_QDOT"][0]
    b = CONSTANTS[engine_type]["POLY_H_2_QDOT"][1]
    c = CONSTANTS[engine_type]["POLY_H_2_QDOT"][2] - H
    # pq-formula, only the positive
    Q = -b/(2*a) + ( (b**2) / ((2*a)**2) - (c / a) )**0.5

    # The value which is calculated is for if the pump was running on 500 rpm
    # Account for the affinity laws
    Q_out = Q * (rpm/CONSTANTS[engine_type]["RPM_DES"]) * 1000 / 3600 # Also converting from m3/h to kg/s
    Q_out[Q_out.isnull()] = -b/(2*a)
    return Q_out