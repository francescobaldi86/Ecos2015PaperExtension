import numpy as np
import pandas as pd
import preprocessingO as ppo
import energyanalysis as ea
import CoolProp.CoolProp as cp


def mainEngineProcessing(raw, processed, CONSTANTS, status, hd, T_0):
    # This script summarizes all the functions that calculate the required data for the Main Engines different flows
    # Reading existing values
    processed = readMainEnginesExistingValues(raw, processed, CONSTANTS, hd)
    # Calculating the main engines fuel flows
    processed = mainEngineFuelFlowCalculation(raw, processed, CONSTANTS, hd)
    # Calculating the main engines power output
    processed = mainEnginePowerCalculation(processed, CONSTANTS)
    # Calculating engine load, that is used many times later on
    status = ppo.engineStatusCalculation("MainEngines", raw, processed, CONSTANTS, status, hd)
    # Calculating air and exhaust gas flows in the main engines
    processed = ppo.trivialAssignment(processed, CONSTANTS) # Assigning connected values
    # processed = ea.propertyCalculator(processed, T_0) # First, let's calculate that we already know
    processed = mainEngineAirFlowCalculation(raw, processed, status, CONSTANTS)
    # Calculating cooling flows
    processed = ppo.engineCoolingSystemsCalculation(processed, CONSTANTS, status, "MainEngines", T_0)
    # Doing the trivial assignments and the calculations
    processed = ppo.trivialAssignment(processed, CONSTANTS)
    # Calculating the properties of the flows that are already fully defined
    # processed = ea.propertyCalculator(processed, T_0)
    return (processed, status)


def readMainEnginesExistingValues(raw, processed, CONSTANTS, hd):
    print("Started reading main engines raw values...")
    # This function only reads existing series. It does not do any pre-processing action.
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # Reading main engines exhaust gas temperature, TC inlet and outlet
        processed[name]["Cyl"]["EG_out"]["T"] = raw[hd[name + "-TC_EG_T_IN"]] + 273.15  # Measured before mixer with flow form bypass
        processed[name]["Turbine"]["Mix_out"]["T"] = raw[hd[name + "-TC_EG_T_OUT"]] + 273.15  # Measured after mixer with waste gate
        # Reading main engines exhaust gas temperature, after HRSG. Only two of the four main engines have the HRSG
        if name=="ME2" or name=="ME3":
            processed[name]["HRSG"]["Mix_out"]["T"] = raw[hd[name + "-EGB_EG_T_OUT"]] + 273.15
            processed[name]["HRSG"]["Mix_in"]["T"] = raw[hd[name + "-TC_EG_T_OUT"]] + 273.15
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[name]["Comp"]["Air_in"]["T"] = raw[hd["ER-FWD_AIR_T_"]] + 273.15
        # Pressure of the charge air, at the compressor outlet (and, hence, at the cylinder inlet)
        processed[name]["Comp"]["Air_out"]["p"] = (raw[hd[name+"-CAC_AIR_P_OUT"]] + 1.01325) * 100000
        # Reading the HT temperature before and after the main engine
        # processed[name]["CAC_HT"]["Water_out"]["T"] = raw[name + "_HT_water_T_out"] # Note: this might be inconsistent
        processed[name]["JWC"]["HTWater_in"]["T"] = raw[hd[name + "-HT_FW_T_IN"]] + 273.15
        # Reading the LT temperature before the main engine
        processed[name]["CAC_LT"]["LTWater_in"]["T"] = raw[hd[name + "-LT_FW_T_IN"]] + 273.15
        # Reading the Lubricating oil temperature before and after the Lubricating Oil Cooler (hence, In is higher)
        processed[name]["LOC"]["LubOil_out"]["T"] = raw[hd[name + "-LOC_OIL_T_OUT"]] + 273.15
        #                           processed[name]["LOC"]["LubOil_out"]["T"] = raw[hd[name + "_TC_OIL_T_OUT"]]
        # Reading fuel oil temperature before injection
        processed[name]["Cyl"]["FuelPh_in"]["T"] = raw[hd[name + "-CYL_FUEL_T_IN"]] + 273.15
        # Reading charge air temperature, after the charge air cooler (or at cylinder inlet)
        processed[name]["CAC_LT"]["Air_out"]["T"] = raw[hd[name + "-CAC_AIR_T_OUT"]] + 273.15
        # Reading Engine rpm
        processed[name]["Cyl"]["Power_out"]["omega"] = raw[hd[name + "__RPM_"]]

        # Assuming that the pressure in the exhaust gas is 90% of the pressure in the inlet manifold. Somewhat reasonable
        processed[name]["Cyl"]["EG_out"]["p"] = (0.9 * raw[hd[name+"-CAC_AIR_P_OUT"]] + 1.01325) * 100000
        processed[name]["BPmerge"]["Mix_out"]["p"] = processed[name]["Cyl"]["EG_out"]["p"]
    print("...done!")
    return processed





def mainEngineFuelFlowCalculation(raw, processed, CONSTANTS, hd):
    print("Started calculating main engine fuel flows...")
    # This function calculates the engine
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # This function calculates the fuel flow of the main engines
        # In the case of the main engines, the fuel flow of an engine is calculated given its fuel
        # rack position and its rotating speed.
        fuel_rack_position = CONSTANTS["MainEngines"]["FRP_2_MFR"]["FRP_MIN"][name] + (CONSTANTS["MainEngines"]["FRP_2_MFR"]["FRP_MAX"][name]-CONSTANTS["MainEngines"]["FRP_2_MFR"]["FRP_MIN"][name]) * raw[hd[name+"__FRP_"]]/100
        # Temporarily, only the ISO fuel flow is calculated
        processed[name]["Cyl"]["FuelPh_in"]["mdot"] = CONSTANTS["MainEngines"]["MFR_FUEL_DES_ISO"] * (
            (CONSTANTS["MainEngines"]["FRP_2_MFR"]["POLY"][name][0] + CONSTANTS["MainEngines"]["FRP_2_MFR"]["POLY"][name][1] * fuel_rack_position) /
            (CONSTANTS["MainEngines"]["FRP_2_MFR"]["POLY"][name][0] + CONSTANTS["MainEngines"]["FRP_2_MFR"]["POLY"][name][1] * CONSTANTS["MainEngines"]["FRP_DES"][name])) * (
            processed[name]["Cyl"]["Power_out"]["omega"] / CONSTANTS["MainEngines"]["RPM_DES"])
    print("...done!")
    return processed


def mainEnginePowerCalculation(processed, CONSTANTS):
    print("Started calculating main engine power...")
    # This function calculates the Power of the engine starting from the efficiency of the engine,
    # which is calcualted starting from other available data
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # Calculate fuel flow-based engine load
        fuel_based_load = processed[name]["Cyl"]["FuelPh_in"]["mdot"] / CONSTANTS["MainEngines"]["MFR_FUEL_DES_ISO"]
        # Calculate ISO bsfc (break specific fuel consumption)
        bsfc_iso = fuel_based_load.apply(ppo.polyvalHelperFunction, args=(CONSTANTS["MainEngines"][                                                                  "POLY_FUEL_LOAD_2_BSFC_ISO"],))
        # Corrects the bsfc from ISO conditions to "real" conditions
        (bsfc,LHV) = ppo.bsfcISOCorrection(bsfc_iso,processed[name]["CAC_LT"]["Air_out"]["T"],processed[name]["CAC_LT"]["LTWater_in"]["T"],processed[name]["Cyl"]["FuelPh_in"]["T"],CONSTANTS)
        # Calculates the real fuel flow using the ISO conversion
        processed[name]["Cyl"]["FuelPh_in"]["mdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] * bsfc / bsfc_iso
        # Calculates the power of the engine as mfr/bsfc, with unit conversion to get the output in kW
        # Shaft energy out
        processed[name]["Cyl"]["Power_out"]["Wdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] / bsfc * 1000 * 3600
        # Chemical energy in the fuel
        processed[name]["Cyl"]["FuelCh_in"]["Wdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] * LHV
    print("...done!")
    return processed





def mainEngineAirFlowCalculation(raw, processed, status, CONSTANTS):
    print("Started calculating main engine air and exhaust flows...")
    # This function calculates the different air and exhaust gas flows in the main engines, taking into account the
    # presence of air bypass and exhaust wastegate valves
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # Calculating the compressor's compression ratio
        beta_comp = processed[name]["Comp"]["Air_out"]["p"] / processed[name]["Comp"]["Air_in"]["p"]
        #  Calculating the compressor isentropic efficiency
        comp_isentropic_efficiency = beta_comp.apply(ppo.polyvalHelperFunction,args=(CONSTANTS["MainEngines"][
                                                                                   "POLY_PIN_2_ETA_IS"],))
        # Calculating the temperature after the compressor, based on ideal gas assumption
        #processed[name]["Comp"]["Air_out"]["T"] = processed[name]["Comp"]["Air_in"]["T"] * beta_comp**((
        #    CONSTANTS["General"]["K_AIR"]-1)/CONSTANTS["General"]["K_AIR"]) / comp_isentropic_efficiency
        T_Comp_out_iso = processed[name]["Comp"]["Air_in"]["T"] * beta_comp**((CONSTANTS["General"]["K_AIR"]-1)/CONSTANTS["General"]["K_AIR"])
        processed[name]["Comp"]["Air_out"]["T"] = processed[name]["Comp"]["Air_in"]["T"] + (
            T_Comp_out_iso - processed[name]["Comp"]["Air_in"]["T"]) / comp_isentropic_efficiency
        # Calculating the air inflow aspired by the cylinder: calculated as inlet air density times the maximum volume,
        # times the engine speed
        processed[name]["Cyl"]["Air_in"]["mdot"] = CONSTANTS["MainEngines"]["V_SW"] * (
            processed[name]["Comp"]["Air_out"]["p"]) / (
            CONSTANTS["General"]["R_AIR"] * processed[name]["Cyl"]["Air_in"]["T"]) * (
            processed[name]["Cyl"]["Power_out"]["omega"] / 60 / 2 * CONSTANTS["General"]["ETA_VOL"]) * (
            CONSTANTS["MainEngines"]["N_CYL"])
        processed[name]["Cyl"]["EG_out"]["mdot"] = processed[name]["Cyl"]["Air_in"]["mdot"] + processed[name]["Cyl"][
            "FuelPh_in"]["mdot"]
        # Calculating an approximated value for the CP_EG and CP_AIR
        processed[name]["Cyl"]["EG_out"]["Composition"] = ppo.mixtureComposition(
            processed[name]["Cyl"]["EG_out"]["Composition"], processed[name]["Cyl"]["Air_in"]["mdot"],
            processed[name]["Cyl"]["FuelPh_in"]["mdot"], processed[name]["Cyl"]["FuelPh_in"]["T"], CONSTANTS)
        # Calculating the bypass flow
        processed[name]["BPsplit"]["BP_out"]["mdot"] = (
            CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"]) +
            CONSTANTS["General"]["CP_EG"] * CONSTANTS["MainEngines"]["ETA_MECH_TC"] * (processed[name]["Cyl"]["Air_in"]["mdot"] + processed[name]["Cyl"]["FuelPh_in"]["mdot"]) *
            (processed[name]["Turbine"]["Mix_out"]["T"] - processed[name]["Cyl"]["EG_out"]["T"])) / (
            CONSTANTS["General"]["CP_AIR"] * (
                processed[name]["Comp"]["Air_in"]["T"] - CONSTANTS["MainEngines"]["ETA_MECH_TC"] * processed[name]["Turbine"]["Mix_out"]["T"] -
                (CONSTANTS["MainEngines"]["ETA_MECH_TC"] - 1) * processed[name]["Comp"]["Air_out"]["T"]))
        # The new approximation is that the valve is only open for engine load below 50%, and when it is open it increases the flow by a fixed amount
        #processed[name]["BPvalve"]["Air_in"]["mdot"][:] = 0
        #processed[name]["BPvalve"]["Air_in"]["mdot"][(status[name]["Load"]<0.6) | ((status[name]["Load"]<0.75) & (processed[name]["TC"]["EG_out"]["T"]<620))] = CONSTANTS["MainEngines"]["BYPASS_FLOW"]
        #processed[name]["BPvalve"]["Air_out"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"]
        # Calculating the temperature of the mixture after the merge between bypass and exhaust gas from the cylinders
        processed[name]["Turbine"]["Mix_in"]["T"] = (
            processed[name]["BPsplit"]["BP_out"]["mdot"] * CONSTANTS["General"]["CP_AIR"] * processed[name]["Comp"]["Air_out"]["T"] +
            processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"] * processed[name]["Cyl"]["EG_out"]["T"]) / (
            processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"] +
            processed[name]["BPsplit"]["BP_out"]["mdot"] * CONSTANTS["General"]["CP_AIR"])
        # The air mass flow going through the compressor is equal to the sum of the air flow through the bypass valve and
        # to the cylinders
        processed[name]["BPsplit"]["Air_in"]["mdot"] = processed[name]["BPsplit"]["BP_out"]["mdot"] + processed[name]["Cyl"]["Air_in"]["mdot"]
        # The flow through the turbine is equal to the sum of the bypass flow and the exhaust coming from the cylinders
        processed[name]["BPmerge"]["Mix_out"]["mdot"] = processed[name]["BPsplit"]["BP_out"]["mdot"] + processed[name]["Cyl"]["EG_out"]["mdot"]
        processed[name]["Turbine"]["Mix_out"]["mdot"] = processed[name]["BPmerge"]["Mix_out"]["mdot"]
        if "HRSG" in processed[name].keys():
            processed[name]["HRSG"]["Mix_out"]["mdot"] = processed[name]["BPmerge"]["Mix_out"]["mdot"]
        processed[name]["Comp"]["Air_in"]["mdot"] = processed[name]["BPsplit"]["Air_in"]["mdot"]
    print("...done!")
    return processed