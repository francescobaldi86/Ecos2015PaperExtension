import numpy as np
import pandas as pd
import preprocessingO as ppo
import energyanalysis as ea

def auxEngineProcessing(raw, processed, CONSTANTS, status, hd, T_0):
    # This script summarizes all the functions that calculate the required data for the Main Engines different flows
    # Reading existing values
    processed = readAuxEnginesExistingValues(raw, processed, CONSTANTS, hd)
    # Calculating the power, including the generator efficiency
    processed = auxEnginePowerCalculation(processed, CONSTANTS)
    # Calculating engine load, that is used many times later on
    status = ppo.engineStatusCalculation("AuxEngines", raw, processed, CONSTANTS, status, hd)
    # Calculating the auxiliary engines fuel flows
    processed = auxEngineFuelFlowCalculation(raw, processed, CONSTANTS, status)
    # Calculate air and exhaust gas flows in the main engines
    processed = auxEngineAirFlowCalculation(raw, processed, CONSTANTS)
    # Calculating cooling flows
    processed = ppo.engineCoolingSystemsCalculation(processed, CONSTANTS, status, "AuxEngines", T_0)
    # Doing the trivial assignments and the calculations
    processed = ppo.trivialAssignment(processed, CONSTANTS)
    processed = ea.propertyCalculator(processed, T_0)
    return (processed, status)


def readAuxEnginesExistingValues(raw, processed,CONSTANTS,hd):
    print("Started reading raw values for auxiliary engines...")
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # Reading main engines exhaust gas temperature, TC inlet and outlet
        processed[name]["Turbine"]["Mix_in"]["T"] = raw[hd[name + "-TC_EG_T_IN1"]] + 273.15
        processed[name]["Turbine"]["Mix_out"]["T"] = raw[hd[name + "-TC_EG_T_OUT"]] + 273.15
        # Reading main engines exhaust gas temperature, after HRSG
        processed[name]["HRSG"]["Mix_out"]["T"] = raw[hd[name + "-EGB_EG_T_OUT"]] + 273.15
        processed[name]["HRSG"]["Mix_in"]["T"] = processed[name]["Turbine"]["Mix_out"]["T"] + 273.15
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[name]["Comp"]["Air_in"]["T"] = raw[hd["ER_AIR_T_"]] + 273.15
        # Reading the HT temperature before and after the main engine
        processed[name]["JWC"]["HTWater_in"]["T"] = raw[hd[name + "-HT_FW_T_IN"]] + 273.15
        # Reading the LT temperature before the main engine
        processed[name]["CAC_LT"]["LTWater_in"]["T"] = raw[hd[name + "-LT-CAC_FW_T_IN"]] + 273.15
        # Reading the Lubricating oil temperature before and after the Lubricating oil cooler
        processed[name]["LOC"]["LubOil_out"]["T"] = raw[hd[name + "-LOC_OIL_T_OUT"]] + 273.15
        # Reading fuel oil temperature before injection
        processed[name]["Cyl"]["FuelPh_in"]["T"] = raw[hd[name + "-CYL_FUEL_T_IN"]] + 273.15
        # Reading charge air temperature.
        processed[name]["CAC_LT"]["Air_out"]["T"] = raw[hd[name + "-CAC_AIR_T_OUT"]] + 273.15
        processed[name]["CAC_LT"]["Air_out"]["p"] = raw[hd[name + "-CAC_AIR_P_OUT"]] + 1
        processed[name]["AG"]["Power_out"]["Wdot"] = raw[hd[name + "_POWER_Wdot_OUT"]]
        processed[name]["Cyl"]["Air_in"]["T"] = processed[name]["CAC_LT"]["Air_out"]["T"]
        processed[name]["Cyl"]["Air_in"]["p"] = processed[name]["CAC_LT"]["Air_out"]["p"]
    print("...done!")
    return processed


def auxEnginePowerCalculation(processed, CONSTANTS):
    print("Started calculating auxiliary engine power...")
    # Calculating the power of the auxiliary engines
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        load = processed[name]["AG"]["Power_out"]["Wdot"] / CONSTANTS["AuxEngines"]["MCR"]
        eta_AG =  CONSTANTS["AuxEngines"]["AG"]["ETA_DES"] - CONSTANTS["AuxEngines"]["AG"]["A"] * np.exp(
            -CONSTANTS["AuxEngines"]["AG"]["k"] * (load))
        processed[name]["AG"]["Power_in"]["Wdot"] = processed[name]["AG"]["Power_out"]["Wdot"] / eta_AG
        processed[name]["AG"]["Losses"]["Wdot"] = processed[name]["AG"]["Power_in"]["Wdot"] - processed[name]["AG"]["Power_out"]["Wdot"]
        processed[name]["Cyl"]["Power_out"]["Wdot"] = processed[name]["AG"]["Power_in"]["Wdot"]
    print("...done!")
    return processed

def auxEngineFuelFlowCalculation(raw, processed, CONSTANTS, status):
    print("Started calculating auxiliary engine fuel flows...")
    # Proceeding with the auxiliary engines
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # First we calculate the ISO break specific fuel consumption (BSFC)
        bsfc_iso = status[name]["Load"].apply(ppo.polyvalHelperFunction, args=(CONSTANTS["AuxEngines"][
                                                                          "POLY_LOAD_2_ISO_BSFC"],))
        (bsfc, LHV) = ppo.bsfcISOCorrection(bsfc_iso, processed[name]["Cyl"]["Air_in"]["T"], processed[name]["CAC_LT"][
                "LTWater_in"]["T"], processed[name]["Cyl"]["FuelPh_in"]["T"], CONSTANTS)
        processed[name]["Cyl"]["FuelPh_in"]["mdot"] = bsfc * processed[name]["Cyl"]["Power_out"]["Wdot"] / 3600 / 1000
        processed[name]["Cyl"]["FuelCh_in"]["Wdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] * LHV
    print("...done!")
    return processed


def auxEngineAirFlowCalculation(raw, processed, CONSTANTS):
    print("Started calculating auxiliary engine air and exhaust flows...")
    # This function calculates the different air and exhaust gas flows in the main engines, taking into account the
    # presence of air bypass and exhaust wastegate valves
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # Reading the pressure of the charge air after the compressor from the raw database
        # Calculating the compressor isentropic efficiency
        comp_isentropic_efficiency = processed[name]["Cyl"]["Air_in"]["p"].apply(ppo.polyvalHelperFunction,args=(CONSTANTS["AuxEngines"][
                                                                                   "POLY_PIN_2_ETA_IS"],))
        # Calculating the compressor's compression ratio
        beta_comp = processed[name]["Comp"]["Air_out"]["p"] / processed[name]["Comp"]["Air_in"]["p"]
        # Calculating the temperature after the compressor, based on ideal gas assumption
        processed[name]["Comp"]["Air_out"]["T"] = processed[name]["Comp"]["Air_in"]["T"] * (1 + beta_comp**((
            CONSTANTS["General"]["K_AIR"]-1)/CONSTANTS["General"]["K_AIR"])) / comp_isentropic_efficiency
        # The state of the air at the outlet of the compressor, outlet of the TC block, and inlet of the bypass valve
        #  are the same
        processed[name]["Comp"]["Air_out"]["T"] = processed[name]["Comp"]["Air_out"]["T"]
        processed[name]["BPsplit"]["Air_in"]["T"] = processed[name]["Comp"]["Air_out"]["T"]
        # The same temperature is the inlet to the charge air cooler
        processed[name]["CAC_HT"]["Air_in"]["T"] = processed[name]["Comp"]["Air_out"]["T"]
        # Calculating the air inflow aspired by the cylinder: calculated as inlet air density times the maximum volume,
        # times the engine speed
        processed[name]["Cyl"]["Air_in"]["mdot"] = CONSTANTS["MainEngines"]["V_MAX"] * (
            processed[name]["Cyl"]["Air_in"]["p"] * 1e5) / (
            CONSTANTS["General"]["R_AIR"] / processed[name]["Cyl"]["Air_in"]["T"]) * (
            processed[name]["Cyl"]["Power_out"]["omega"] / 60 / 2 * CONSTANTS["General"]["ETA_VOL"]) * (
            CONSTANTS["AuxEngines"]["N_CYL"])
        processed[name]["Cyl"]["EG_out"]["mdot"] = processed[name]["Cyl"]["Air_in"]["mdot"] + processed[name]["Cyl"][
            "FuelPh_in"]["mdot"]
        # Here we calculate the bypass mass flow. THIS NEEDS TO BE CHECKED FOR CONSISTENCY (i.e. the bypass mass flow
        #  should always be kind of low, and anyway only be seen at low to medium load).
        # The equation is the result of a mass and energy balance over the whole engine
        processed[name]["BPsplit"]["BP_out"]["mdot"] = (
            processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"] * (
                processed[name]["Turbine"]["Mix_in"]["T"] - processed[name]["Turbine"]["Mix_out"]["T"]) * CONSTANTS["MainEngines"]["ETA_MECH_TC"] -
            CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (
                processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"])) / (
            CONSTANTS["General"]["CP_AIR"] * (processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"]) -
            CONSTANTS["General"]["CP_EG"] * CONSTANTS["MainEngines"]["ETA_MECH_TC"] * (
                processed[name]["Turbine"]["Mix_in"]["T"] - processed[name]["Turbine"]["Mix_out"]["T"]))
        processed[name]["BPmerge"]["BP_in"]["mdot"] = processed[name]["BPsplit"]["Air_out"]["mdot"]
        # The air mass flow going through the compressor is equal to the sum of the air flow through the bypass valve and
        # to the cylinders
        processed[name]["BPsplit"]["Air_in"]["mdot"] = processed[name]["BPsplit"]["BP_out"]["mdot"] + processed[name]["Cyl"]["Air_in"]["mdot"]
        # Inlet and outlet flows to the compressor are equal
        processed[name]["Comp"]["Air_in"]["mdot"] = processed[name]["BPsplit"]["Air_in"]["mdot"]
        processed[name]["Comp"]["Air_out"]["mdot"] = processed[name]["Comp"]["Air_in"]["mdot"]
        # The flow through the turbine is equal to the sum of the bypass flow and the exhaust coming from the cylinders
        processed[name]["BPmerge"]["Mix_out"]["mdot"] = processed[name]["BPmerge"]["BP_in"]["mdot"] + processed[name]["Cyl"]["EG_out"]["mdot"]
        processed[name]["Turbine"]["Mix_out"]["mdot"] = processed[name]["BPmerge"]["Mix_out"]["mdot"]
        processed[name]["Turbine"]["Mix_in"]["mdot"] = processed[name]["BPmerge"]["Mix_out"]["mdot"]
        # Calculating the temperature of the mixture after the merge between bypass and exhaust gas from the cylinders
        processed[name]["Cyl"]["EG_out"]["T"] = ((processed[name]["BPmerge"]["EG_in"]["mdot"] * CONSTANTS["General"]["CP_EG"] +
            processed[name]["BPmerge"]["BP_in"]["mdot"] * CONSTANTS["General"]["CP_AIR"]) * processed[name]["Turbine"]["Mix_in"]["T"] -
            processed[name]["BPmerge"]["BP_in"]["mdot"] * CONSTANTS["General"]["CP_AIR"] * processed[name]["BPmerge"]["BP_in"]["T"]) / (
            processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"])
    print("...done!")
    return processed