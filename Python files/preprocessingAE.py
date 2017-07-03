import numpy as np
import pandas as pd
import preprocessingO as ppo
import coolingsystems as cs
from helpers import d2df

def auxEngineProcessing(raw, processed, dict_structure, CONSTANTS, hd):
    # This script summarizes all the functions that calculate the required data for the Main Engines different flows
    # Reading existing values
    processed = readAuxEnginesExistingValues(raw, processed, CONSTANTS, hd)
    processed = ppo.engineStatusCalculation("AuxEngines", raw, processed, CONSTANTS, hd)
    # Calculating the cooling flows, so that they can be later assigned easily
    processed = cs.coolingFlows(processed, CONSTANTS, "AuxEngines")
    processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "AuxEngines", "AE-1.1")
    processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "AuxEngines", "AE-1.2")
    # Calculating the power, including the generator efficiency
    processed = auxEnginePowerCalculation(processed, CONSTANTS)
    # Calculating engine load, that is used many times later on
    processed = ppo.engineLoadCalculation("AuxEngines", raw, processed, CONSTANTS, hd)
    # Calculating the auxiliary engines fuel flows
    processed = auxEngineFuelFlowCalculation(raw, processed, CONSTANTS)
    # Calculate air and exhaust gas flows in the main engines
    processed = auxEngineAirFlowCalculation(raw, processed, CONSTANTS)
    processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "AuxEngines", "AE-2.1")
    processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "AuxEngines", "AE-2.2")
    # Calculating cooling flows
    processed = cs.engineCoolingSystemsCalculation(processed, CONSTANTS, "AuxEngines")
    processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "AuxEngines", "AE-3.1")
    processed = ppo.systemFill(processed, dict_structure, CONSTANTS, "AuxEngines", "AE-3.2")
    return processed


def readAuxEnginesExistingValues(raw, processed,CONSTANTS,hd):
    print("Started reading raw values for auxiliary engines...", end="", flush=True)
    for system in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # Reading main engines exhaust gas temperature, TC inlet and outlet
        processed[d2df(system,"Turbine","Mix_in","T")] = raw[hd[system + "-TC_EG_T_IN1"]] + 273.15
        processed[d2df(system,"Turbine","Mix_out","T")] = raw[hd[system + "-TC_EG_T_OUT"]] + 273.15
        # Reading main engines exhaust gas temperature, after HRSG
        processed[d2df(system,"HRSG","Mix_out","T")] = raw[hd[system + "-EGB_EG_T_OUT"]] + 273.15
        # Reading the HT temperature before and after the main engine
        processed[d2df(system,"JWC","HTWater_in","T")] = raw[hd[system + "-HT_FW_T_IN"]] + 273.15
        # Reading the LT temperature before the main engine
        processed[d2df(system,"CAC_LT","LTWater_in","T")] = raw[hd[system + "-LT-CAC_FW_T_IN"]] + 273.15
        # Reading the Lubricating oil temperature before and after the Lubricating oil cooler
        processed[d2df(system,"LOC","LubOil_out","T")] = raw[hd[system + "-LOC_OIL_T_OUT"]] + 273.15
        # Reading fuel oil temperature before injection
        processed[d2df(system,"Cyl","FuelPh_in","T")] = raw[hd[system + "-CYL_FUEL_T_IN"]] + 273.15
        # Reading charge air temperature.
        processed[d2df(system,"CAC_LT","Air_out","T")] = raw[hd[system + "-CAC_AIR_T_OUT"]] + 273.15
        # Reading power output
        processed[d2df(system,"AG","Power_out","Edot")] = raw[hd[system + "_POWER_Wdot_OUT"]]
        # Reading Engine rpm
        # processed[d2df(system, "Cyl", "Power_out", "omega")] = raw[hd[system + "__RPM_"]]
        # Reading the pressure in the cooling flows
        processed[d2df(system, "CAC_LT", "LTWater_in", "p")] = (raw[hd[system + "-LT-CAC_FW_P_IN"]] + 1.01325) * 100000
        processed[d2df(system, "JWC", "HTWater_in", "p")] = raw[hd[system + "-HT-JWC_FW_P_IN"]] + 273.15
        processed[d2df(system, "Comp", "Air_out", "p")] = (raw[hd[system + "-CAC_AIR_P_OUT"]] + 1.01325) * 100000
        # Reading the pressure of the lubricating oil
        processed[d2df(system, "LOC", "LubOil_out", "p")] = (raw[hd[system + "-LOC_OIL_P_IN"]] + 1.01325) * 100000
        # Reading the pressure in the cooling flows
        processed[d2df(system, "CAC_LT", "LTWater_in", "p")] = (raw[hd[system + "-LT-CAC_FW_P_IN"]] + 1.01325) * 100000
        processed[d2df(system, "JWC", "HTWater_in", "p")] = (raw[hd[system + "-HT-JWC_FW_P_IN"]] + 1.01325) * 100000
        # Reading turbocharger speed
        processed[d2df(system, "TCshaft", "Power_in", "omega")] = raw[hd[system + "-TC__RPM_"]]
        processed[d2df(system, "TCshaft", "Power_out", "omega")] = raw[hd[system + "-TC__RPM_"]]
        processed[d2df(system, "Turbine", "Power_out", "omega")] = raw[hd[system + "-TC__RPM_"]]
        processed[d2df(system, "Compressor", "Power_in", "omega")] = raw[hd[system + "-TC__RPM_"]]
    print("...done!")
    return processed


def auxEnginePowerCalculation(processed, CONSTANTS):
    print("Started calculating auxiliary engine power...", end="", flush=True)
    # Calculating the power of the auxiliary engines
    for system in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        load = processed[d2df(system,"AG","Power_out","Edot")] / CONSTANTS["AuxEngines"]["MCR"]
        eta_AG =  CONSTANTS["AuxEngines"]["AG"]["ETA_DES"] - CONSTANTS["AuxEngines"]["AG"]["A"] * np.exp(
            -CONSTANTS["AuxEngines"]["AG"]["k"] * (load))
        processed[d2df(system,"AG","Power_in","Edot")] = processed[d2df(system,"AG","Power_out","Edot")] / eta_AG
        processed[d2df(system,"AG","Losses","Qdot")] = processed[d2df(system,"AG","Power_in","Edot")] - processed[d2df(system,"AG","Power_out","Edot")]
        processed[d2df(system,"Cyl","Power_out","Edot")] = processed[d2df(system,"AG","Power_in","Edot")]
    print("...done!")
    return processed

def auxEngineFuelFlowCalculation(raw, processed, CONSTANTS):
    print("Started calculating auxiliary engine fuel flows...", end="", flush=True)
    # Proceeding with the auxiliary engines
    for system in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # First we calculate the ISO break specific fuel consumption (BSFC)
        bsfc_iso = processed[system+":"+"load"].apply(ppo.polyvalHelperFunction, args=(CONSTANTS["AuxEngines"][
                                                                          "POLY_LOAD_2_ISO_BSFC"],))
        (bsfc, LHV) = ppo.bsfcISOCorrection(bsfc_iso, processed[d2df(system,"Cyl","Air_in","T")], processed[d2df(system,"CAC_LT",
                "LTWater_in","T")], processed[d2df(system,"Cyl","FuelPh_in","T")], CONSTANTS)
        processed[d2df(system,"Cyl","FuelPh_in","mdot")] = bsfc * processed[d2df(system,"Cyl","Power_out","Edot")] / 3600 / 1000
        processed[d2df(system,"Cyl","FuelCh_in","Edot")] = processed[d2df(system,"Cyl","FuelPh_in","mdot")] * LHV
    print("...done!")
    return processed


def auxEngineAirFlowCalculation(raw, processed, CONSTANTS):
    print("Started calculating auxiliary engine air and exhaust flows...", end="", flush=True)
    # This function calculates the different air and exhaust gas flows in the main engines, taking into account the
    # presence of air bypass and exhaust wastegate valves
    for system in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # Calculating the compressor's compression ratio
        beta_comp = processed[d2df(system,"Comp","Air_out","p")] / processed[d2df(system,"Comp","Air_in","p")]
        # Calculating the compressor isentropic efficiency
        comp_isentropic_efficiency = beta_comp.apply(ppo.polyvalHelperFunction, args=(CONSTANTS["AuxEngines"]["POLY_PIN_2_ETA_IS"],))
        # Calculating the temperature after the compressor, based on ideal gas assumption
        T_Comp_out_iso = processed[d2df(system, "Comp", "Air_in", "T")] * beta_comp ** ((CONSTANTS["General"]["K_AIR"] - 1) / CONSTANTS["General"]["K_AIR"])
        processed[d2df(system, "Comp", "Air_out", "T")] = processed[d2df(system, "Comp", "Air_in", "T")] + (
            T_Comp_out_iso - processed[d2df(system, "Comp", "Air_in", "T")]) / comp_isentropic_efficiency
        #### NOTE: HERE WE MAKE THE ASSUMPTION THAT THE COMPRESSOR OUTLET TEMPERATURE CANNOT BE LOWER THAN THE CYLINDER INLET TEMPERATURE
        processed.loc[processed[d2df(system, "Comp", "Air_out", "T")] < processed[d2df(system, "Cyl", "Air_in", "T")], d2df(
                system, "Comp", "Air_out", "T")] = \
            processed.loc[processed[d2df(system, "Comp", "Air_out", "T")] < processed[d2df(system, "Cyl", "Air_in", "T")], d2df(
                    system, "Cyl", "Air_in", "T")]
        # Calculating the air inflow aspired by the cylinder: calculated as inlet air density times the maximum volume,
        # times the engine speed
        processed[d2df(system,"Cyl","Air_in","mdot")] = CONSTANTS["AuxEngines"]["V_MAX"] * (
            processed[d2df(system,"Comp","Air_out","p")]) / (
            CONSTANTS["General"]["R_AIR"] * processed[d2df(system,"Cyl","Air_in","T")]) * (
            processed[d2df(system,"Cyl","Power_out","omega")] / 60 / 2 * CONSTANTS["General"]["ETA_VOL"]) * (
            CONSTANTS["AuxEngines"]["N_CYL"])
        # Exhaust gas flow after the cylinders
        processed[d2df(system,"Cyl","EG_out","mdot")] = processed[d2df(system,"Cyl","Air_in","mdot")] + processed[d2df(system,"Cyl","FuelPh_in","mdot")]
        # Here we calculate the bypass mass flow. THIS NEEDS TO BE CHECKED FOR CONSISTENCY (i.e. the bypass mass flow
        #  should always be kind of low, and anyway only be seen at low to medium load).
        # The equation is the result of a mass and energy balance over the whole engine
        # dT_comp = processed[d2df(system,"Comp","Air_out","T")] - processed[d2df(system,"Comp","Air_in","T")]
        # dT_turb = processed[d2df(system,"Turbine","Mix_in","T")] - processed[d2df(system,"Turbine","Mix_out","T")]
        # processed[d2df(system, "BPsplit", "BP_out", "mdot")] = (processed[d2df(system, "Cyl", "Air_in", "mdot")] * CONSTANTS["General"]["CP_AIR"] * dT_comp -
        #     processed[d2df(system,"Cyl","EG_out","mdot")] * CONSTANTS["General"]["CP_EG"] * dT_turb * CONSTANTS["MainEngines"]["ETA_MECH_TC"]) / (
        #     CONSTANTS["General"]["CP_AIR"] * (CONSTANTS["MainEngines"]["ETA_MECH_TC"] * dT_turb - dT_comp))
        processed.loc[:, d2df(system, "BPmerge", "BP_in", "mdot")] = 0
        # The air mass flow going through the compressor is equal to the sum of the air flow through the bypass valve and
        # to the cylinders
        processed[d2df(system,"BPsplit","Air_in","mdot")] = processed[d2df(system, "BPmerge", "BP_in", "mdot")] + processed[d2df(system,"Cyl","Air_in","mdot")]
        # The flow through the turbine is equal to the sum of the bypass flow and the exhaust coming from the cylinders
        processed[d2df(system,"BPmerge","Mix_out","mdot")] = processed[d2df(system,"BPmerge","BP_in","mdot")] + processed[d2df(system,"Cyl","EG_out","mdot")]
        # Calculating the temperature of the mixture after the merge between bypass and exhaust gas from the cylinders
        processed[d2df(system,"Cyl","EG_out","T")] = ((processed[d2df(system,"Cyl","EG_out","mdot")] * CONSTANTS["General"]["CP_EG"] +
            processed[d2df(system,"BPmerge","BP_in","mdot")] * CONSTANTS["General"]["CP_AIR"]) * processed[d2df(system,"Turbine","Mix_in","T")] -
            processed[d2df(system,"BPmerge","BP_in","mdot")] * CONSTANTS["General"]["CP_AIR"] * processed[d2df(system, "Comp", "Air_out", "T")]) / (
            processed[d2df(system,"Cyl","EG_out","mdot")] * CONSTANTS["General"]["CP_EG"])
        processed[system + ":CP_MIX"] = (processed[d2df(system, "BPmerge", "BP_in", "mdot")] * CONSTANTS["General"]["CP_AIR"] +
            processed[d2df(system, "Cyl", "EG_out", "mdot")] * CONSTANTS["General"]["CP_AIR"]) / processed[d2df(system, "BPmerge", "Mix_out", "mdot")]
        # Calculating the turbine's power outpput to the compressor
        processed[d2df(system, "Turbine", "Power_out", "Edot")] = processed[system + ":CP_MIX"] * processed[d2df(system, "BPmerge", "Mix_out", "mdot")] * (
            processed[d2df(system, "Turbine", "Mix_in", "T")] - processed[d2df(system, "Turbine", "Mix_out", "T")])
        # Calculating the compressor's power input.
        processed[d2df(system, "Comp", "Power_in", "Edot")] = CONSTANTS["General"]["CP_AIR"] * processed[d2df(system, "BPsplit", "Air_in", "mdot")] * (
            processed[d2df(system, "Comp", "Air_out", "T")] - processed[d2df(system, "Comp", "Air_in", "T")])
        # Losses at the TC shaft level are calculated
        processed[d2df(system, "TCshaft", "Losses_out", "Qdot")] = processed[d2df(system, "Turbine", "Power_out", "Edot")] - processed[d2df(system, "Comp", "Power_in", "Edot")]

        # processed[system + ":EG_Composition"] = ppo.mixtureComposition(
        #     processed[d2df(system, "Cyl", "Air_in", "mdot")],
        #     processed[d2df(system, "Cyl", "FuelPh_in", "mdot")],
        #     processed[d2df(system, "Cyl", "FuelPh_in", "T")],
        #     CONSTANTS)
        # processed[system + ":Mix_Composition"] = ppo.mixtureComposition(
        #     processed[d2df(system, "BPsplit", "Air_in", "mdot")],
        #     processed[d2df(system, "Cyl", "FuelPh_in", "mdot")],
        #     processed[d2df(system, "Cyl", "FuelPh_in", "T")],
        #     CONSTANTS)
    print("...done!")
    return processed