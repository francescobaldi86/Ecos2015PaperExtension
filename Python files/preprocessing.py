# This module includes the functions that perform the "pre-processing": In short, they prepare the data structure
# that is then processed by the "Energy analysis" and "Exergy analysis" functions, all in one go.
#
# The module is made of :
# - One function that simply reads in the data that is already available from the original dataset

import numpy as np
import pandas as pd


def assumptions(raw, processed, CONSTANTS, hd):
    # This function includes generic assumed values in the main structure
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[name]["TC"]["Air_in"]["p"] = CONSTANTS["General"]["P_ATM"]
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[name]["TC"]["Air_in"]["p"] = CONSTANTS["General"]["P_ATM"]
    CONSTANTS["General"]["T_0"] = raw[hd["ER13_SW_T_IN"]]
    return processed


def mainEngineProcessing(raw, processed, CONSTANTS, status, hd):
    # This script summarizes all the functions that calculate the required data for the Main Engines different flows
    # Reading existing values
    processed = readMainEnginesExistingValues(raw, processed, CONSTANTS, hd)
    # Calculating the main engines fuel flows
    processed = mainEngineFuelFlowCalculation(raw, processed, CONSTANTS, hd)
    # Calculating the main engines power output
    processed = mainEnginePowerCalculation(processed, CONSTANTS)
    # Calculating engine load, that is used many times later on
    status = mainEngineStatusCalculation(processed, CONSTANTS, status)
    # Calculating air and exhaust gas flows in the main engines
    processed = mainEngineAirFlowCalculation(raw, processed, status, CONSTANTS)
    # Calculating cooling flows
    processed = engineCoolingSystemsCalculation(processed, CONSTANTS, status, "MainEngines")
    return (processed, status)


def auxEngineProcessing(raw, processed, CONSTANTS, status, hd):
    # This script summarizes all the functions that calculate the required data for the Main Engines different flows
    # Reading existing values
    processed = readAuxEnginesExistingValues(raw, processed, CONSTANTS, hd)
    # Calculating engine load, that is used many times later on
    status = auxEngineStatusCalculation(raw, processed, CONSTANTS, hd, status)
    # Calculating the auxiliary engines fuel flows
    processed = auxEngineFuelFlowCalculation(raw, processed, CONSTANTS, status)
    # Calculate air and exhaust gas flows in the main engines
    processed = auxEngineAirFlowCalculation(raw, processed, CONSTANTS)
    # Calculating cooling flows
    processed = engineCoolingSystemsCalculation(processed, CONSTANTS, status, "AuxEngines", )
    return (processed, status)



def readMainEnginesExistingValues(raw, processed, CONSTANTS, hd):
    # This function only reads existing series. It does not do any pre-processing action.
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # Reading main engines exhaust gas temperature, TC inlet and outlet
        processed[name]["Cyl"]["EG_out"]["T"] = raw[hd[name + "-TC_EG_T_IN"]] + 273.15  # Measured before mixer with flow form bypass
        processed[name]["TC"]["EG_out"]["T"] = raw[hd[name + "-TC_EG_T_OUT"]] + 273.15  # Measured after mixer with waste gate
        # Reading main engines exhaust gas temperature, after HRSG. Only two of the four main engines have the HRSG
        if name=="ME2" or name=="ME3":
            processed[name]["HRSG"]["EG_out"]["T"] = raw[hd[name + "_EGB_EG_T_OUT"]] + 273.15
            processed[name]["HRSG"]["EG_in"]["T"] = raw[hd[name + "-TC_EG_T_OUT"]] + 273.15
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[name]["TC"]["Air_in"]["T"] = raw[hd["ER-FWD_AIR_T_"]] + 273.15
        processed[name]["Comp"]["Air_in"]["T"] = processed[name]["TC"]["Air_in"]["T"]
        # Pressure of the charge air, at the compressor outlet (and, hence, at the cylinder inlet)
        processed[name]["TC"]["Air_out"]["p"] = raw[hd[name+"-CAC_AIR_P_OUT"]] + 1
        processed[name]["Cyl"]["Air_in"]["p"] = processed[name]["TC"]["Air_out"]["p"] + 1
        processed[name]["BPvalve"]["Air_in"]["p"] = processed[name]["TC"]["Air_out"]["p"]
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
        processed[name]["Cyl"]["Air_in"]["T"] = processed[name]["CAC_LT"]["Air_out"]["T"]
        # Reading Engine rpm
        processed[name]["Cyl"]["Power_out"]["omega"] = raw[hd[name + "__RPM_"]]
        return processed




def readAuxEnginesExistingValues(raw, processed,CONSTANTS,hd):
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # Reading main engines exhaust gas temperature, TC inlet and outlet
        processed[name]["TC"]["EG_in"]["T"] = raw[hd[name + "-TC_EG_T_IN1"]] + 273.15
        processed[name]["TC"]["EG_out"]["T"] = raw[hd[name + "-TC_EG_T_OUT"]] + 273.15
        # Reading main engines exhaust gas temperature, after HRSG
        processed[name]["HRSG"]["EG_out"]["T"] = raw[hd[name + "-EGB_EG_T_OUT"]] + 273.15
        processed[name]["HRSG"]["EG_in"]["T"] = processed[name]["TC"]["EG_out"]["T"] + 273.15
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[name]["TC"]["Air_in"]["T"] = raw[hd["ER_AIR_T_"]] + 273.15
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
        processed[name]["Cyl"]["Power_out"]["Wdot"] = raw[hd[name + "_POWER_Wdot_OUT"]]
        return processed


def readOtherExistingValues(raw, processed):
    # Other components
    processed["Other"]["SWC13"]["SeaWater"]["T_out"] = raw["SWC13_SeaWater_Tout"]  # CHECK IF IT IS IN OR OUT
    processed["Other"]["SWC24"]["SeaWater"]["T_out"] = raw["SWC24_SeaWater_Tout"]  # CHECK IF IT IS IN OR OUT
    processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    return processed


def mainEngineFuelFlowCalculation(raw, processed, CONSTANTS, hd):
    # This function calculates the engine
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # This function calculates the fuel flow of the main engines
        # In the case of the main engines, the fuel flow of an engine is calculated given its fuel
        # rack position and its rotating speed.
        fuel_rack_position = raw[hd[name+"__FRP_"]]
        # Temporarily, only the ISO fuel flow is calculated
        processed[name]["Cyl"]["FuelPh_in"]["mdot"] = CONSTANTS["MainEngines"]["MFR_FUEL_DES_ISO"] * (
            (CONSTANTS["MainEngines"]["POLY_FRP_2_MFR"][0] + CONSTANTS["MainEngines"]["POLY_FRP_2_MFR"][1] *
            fuel_rack_position/100*CONSTANTS["MainEngines"]["FRP_DES"][name]) / (CONSTANTS["MainEngines"]["POLY_FRP_2_MFR"][0] + CONSTANTS["MainEngines"][
            "POLY_FRP_2_MFR"][1] * CONSTANTS["MainEngines"]["FRP_DES"][name])) * (
            processed[name]["Cyl"]["Power_out"]["omega"] / CONSTANTS["MainEngines"]["RPM_DES"])
    return processed


def mainEnginePowerCalculation(processed, CONSTANTS):
    # This function calculates the Power of the engine starting from the efficiency of the engine,
    # which is calcualted starting from other available data
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # Calculate fuel flow-based engine load
        fuel_based_load = processed[name]["Cyl"]["FuelPh_in"]["mdot"] / CONSTANTS["MainEngines"]["MFR_FUEL_DES_ISO"]
        # Calculate ISO fuel mass flow rate
        mfr_fuel_iso = fuel_based_load * CONSTANTS["MainEngines"]["MFR_FUEL_DES_ISO"]
        # Calculate ISO bsfc (break specific fuel consumption)
        bsfc_iso = fuel_based_load.apply(polyvalHelperFunction, args=(CONSTANTS["MainEngines"][
                                                                          "POLY_FUEL_LOAD_2_BSFC_ISO"],))
        # Corrects the bsfc from ISO conditions to "real" conditions
        bsfc = bsfcISOCorrection(bsfc_iso,processed[name]["Cyl"]["Air_in"]["T"],processed[name]["CAC_LT"][
            "LTWater_in"]["T"],"HFO",CONSTANTS)
        # Calculates the real fuel flow using the ISO conversion
        processed[name]["Cyl"]["FuelPh_in"]["mdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] * bsfc / bsfc_iso
        # Calculates the power of the engine as mfr/bsfc, with unit conversion to get the output in kW
        # Shaft energy out
        processed[name]["Cyl"]["Power_out"]["Wdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] / bsfc * 1000 * 3600
        processed[name]["Cyl"]["FuelCh_in"]["Wdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] * CONSTANTS["General"]["LHV_HFO"]  # CORRECT WITH THE CORRECT LHV
         # Chemical energy
        processed[name]["Cyl"]["FuelCh_in"]["Wdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] * CONSTANTS["General"]["LHV_HFO"]

    return processed


def mainEngineStatusCalculation(processed, CONSTANTS, status):
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        status[name]["Load"] = processed[name]["Cyl"]["Power_out"]["Wdot"] / CONSTANTS["MainEngines"]["MCR"]
        # We consider the engines are on only if the load is above 5% and if the speed is above 10% of the nominal value
        status[name]["OnOff"] = (status[name]["Load"] > 0.05) & (processed[name]["Cyl"]["Power_out"]["omega"] > CONSTANTS["MainEngines"]["RPM_DES"] * 0.1)
    return status


def mainEngineAirFlowCalculation(raw, processed, status, CONSTANTS):
    # This function calculates the different air and exhaust gas flows in the main engines, taking into account the
    # presence of air bypass and exhaust wastegate valves
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # Reading the pressure of the charge air after the compressor from the raw database
        # Calculating the compressor isentropic efficiency
        comp_isentropic_efficiency = processed[name]["Cyl"]["Air_in"]["p"].apply(polyvalHelperFunction,args=(CONSTANTS["MainEngines"][
                                                                                   "POLY_PIN_2_ETA_IS"],))
        # Calculating the compressor's compression ratio
        beta_comp = processed[name]["TC"]["Air_out"]["p"] / processed[name]["TC"]["Air_in"]["p"]
        # Calculating the temperature after the compressor, based on ideal gas assumption
        processed[name]["TC"]["Air_out"]["T"] = processed[name]["TC"]["Air_in"]["T"] * beta_comp**((
            CONSTANTS["General"]["K_AIR"]-1)/CONSTANTS["General"]["K_AIR"]) / comp_isentropic_efficiency
        # The state of the air at the outlet of the compressor, outlet of the TC block, and inlet of the bypass valve
        #  are the same
        processed[name]["Comp"]["Air_out"]["T"] = processed[name]["TC"]["Air_out"]["T"]
        processed[name]["BPvalve"]["Air_in"]["T"] = processed[name]["TC"]["Air_out"]["T"]
        # The same temperature is the inlet to the charge air cooler
        processed[name]["CAC_HT"]["Air_in"]["T"] = processed[name]["TC"]["Air_out"]["T"]
        # Calculating the air inflow aspired by the cylinder: calculated as inlet air density times the maximum volume,
        # times the engine speed
        processed[name]["Cyl"]["Air_in"]["mdot"] = CONSTANTS["MainEngines"]["V_MAX"] * (
            processed[name]["Cyl"]["Air_in"]["p"] * 1e5) / (
            CONSTANTS["General"]["R_AIR"] * processed[name]["Cyl"]["Air_in"]["T"]) * (
            processed[name]["Cyl"]["Power_out"]["omega"] / 60 / 2 * CONSTANTS["General"]["ETA_VOL"]) * (
            CONSTANTS["MainEngines"]["N_CYL"])
        processed[name]["Cyl"]["EG_out"]["mdot"] = processed[name]["Cyl"]["Air_in"]["mdot"] + processed[name]["Cyl"][
            "FuelPh_in"]["mdot"]
        # Here we calculate the bypass mass flow. THIS NEEDS TO BE CHECKED FOR CONSISTENCY (i.e. the bypass mass flow
        #  should always be kind of low, and anyway only be seen at low to medium load).
        # The equation is the result of a mass and energy balance over the whole engine
        #dh_comp_on_eta = (CONSTANTS["General"]["CP_AIR"] / CONSTANTS["MainEngines"]["ETA_MECH_TC"] *
        #    processed[name]["Cyl"]["Air_in"]["mdot"] * (
        #    processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"]))
        #processed[name]["BPvalve"]["Air_in"]["mdot"] = (
        #    processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"] * (
        #       processed[name]["Cyl"]["EG_out"]["T"] - processed[name]["TC"]["EG_out"]["T"]) - dh_comp_on_eta) / (
        #  CONSTANTS["General"]["CP_EG"] * (
        #   processed[name]["TC"]["EG_out"]["T"] - processed[name]["Comp"]["Air_out"]["T"]) -
        #   dh_comp_on_eta)
        #processed[name]["BPvalve"]["Air_in"]["mdot"] = (
        #    CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"]) +
        #    CONSTANTS["General"]["CP_EG"] * CONSTANTS["MainEngines"]["ETA_MECH_TC"] * (processed[name]["Cyl"]["Air_in"]["mdot"] - processed[name]["Cyl"]["FuelPh_in"]["mdot"]) *
        #    (processed[name]["Cyl"]["EG_out"]["T"] - processed[name]["TC"]["EG_out"]["T"])) / (
        #    CONSTANTS["General"]["CP_AIR"] * (
        #        processed[name]["Comp"]["Air_in"]["T"]+ CONSTANTS["MainEngines"]["ETA_MECH_TC"] * processed[name]["TC"]["EG_out"]["T"] -
        #        (1 + CONSTANTS["MainEngines"]["ETA_MECH_TC"]) * processed[name]["Comp"]["Air_out"]["T"]))
        processed[name]["BPvalve"]["Air_in"]["mdot"][:] = 0
        processed[name]["BPvalve"]["Air_in"]["mdot"][status[name]["Load"]<0.5] = CONSTANTS["MainEngines"]["BYPASS_FLOW"]
        processed[name]["BPvalve"]["Air_out"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"]
        # Calculating the temperature of the mixture after the merge between bypass and exhaust gas from the cylinders
        processed[name]["TC"]["EG_in"]["T"] = processed[name]["Cyl"]["EG_out"]["T"] - (
            processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["Air_in"]["mdot"] *
            CONSTANTS["General"]["CP_AIR"] * (processed[name]["Comp"]["Air_out"]["T"] -
            processed[name]["Comp"]["Air_in"]["T"])) / CONSTANTS["MainEngines"]["ETA_MECH_TC"] / processed[name]["Cyl"]["EG_out"]["mdot"]
        # The air mass flow going through the compressor is equal to the sum of the air flow through the bypass valve and
        # to the cylinders
        processed[name]["TC"]["Air_in"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["Air_in"]["mdot"]
        # Inlet and outlet flows to the compressor are equal
        processed[name]["TC"]["Air_out"]["mdot"] = processed[name]["TC"]["Air_in"]["mdot"]
        # The flow through the turbine is equal to the sum of the bypass flow and the exhaust coming from the cylinders
        processed[name]["TC"]["EG_in"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["EG_out"]["mdot"]
    return processed


def engineCoolingSystemsCalculation(processed, CONSTANTS, status, engine_type):
    # This function calculates the different flows related to the cooling systems of the main engines.
    for name in CONSTANTS["General"]["NAMES"][engine_type]:
        # Calculating the total energy flow going to the cooling systems, based on the energy balance on the engine
        energy_2_cooling = processed[name]["Cyl"]["FuelCh_in"]["Wdot"] - processed[name]["Cyl"]["Power_out"]["Wdot"] + (
            CONSTANTS["General"]["CP_HFO"] * processed[name]["Cyl"]["FuelPh_in"]["mdot"] * (processed[name]["Cyl"]["FuelPh_in"]["T"] - CONSTANTS["General"]["T_0"])) - (
            CONSTANTS["General"]["CP_EG"] * processed[name]["TC"]["EG_out"]["mdot"] * (processed[name]["TC"]["EG_out"]["T"] - CONSTANTS["General"]["T_0"])) + (
            CONSTANTS["General"]["CP_AIR"] * processed[name]["TC"]["Air_in"]["mdot"] * (processed[name]["TC"]["Air_in"]["T"] - CONSTANTS["General"]["T_0"]))
        # Calculating the energy going to the charge air cooler, based on the estimated temperatures on the air line
        energy_2_cac = CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (processed[name]["TC"]["Air_out"]["T"] - processed[name]["Cyl"]["Air_in"]["T"])
        # Calculating the energy going to the HT cooling systems, based on interpolation from the project guide
        energy_2_ht_theoric = status[name]["Load"].apply(polyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_HT"],))
        energy_2_lt_theoric = status[name]["Load"].apply(polyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_LT"],))
        # The values calculated based on the project guide are reconciled based on the energy balance
        energy_2_ht = energy_2_cooling * energy_2_ht_theoric / (energy_2_ht_theoric + energy_2_lt_theoric)
        energy_2_lt = energy_2_cooling - energy_2_ht
        # The energy going to the CAC, HT stage is calculated assuming a 85% effectiveness of the heat exchanger
        energy_2_cac_ht = CONSTANTS[engine_type]["EPS_CAC_HTSTAGE"] * processed[name]["TC"]["Air_in"]["mdot"] * CONSTANTS["General"]["CP_AIR"] * (
            processed[name]["TC"]["Air_out"]["T"] - processed[name]["CAC_HT"]["HTWater_in"]["T"])
        # The energy going to the CAC, LT stage results as a consequence by thermal balance over the CAC
        energy_2_cac_lt = energy_2_cac - energy_2_cac_ht
        # The energy to the JWC results as a balance over the HT cooling systems
        energy_2_jwc = energy_2_ht - energy_2_cac_ht
        # The energy to the LOC results as a balance over the LT cooling systems
        energy_2_loc = energy_2_lt - energy_2_cac_lt
        # For all pumps, it is here assumed that the flow scales only with the speed of the engine (biiiiig assumption)
        processed[name]["LOC"]["LTWater_in"]["mdot"] = CONSTANTS[engine_type]["MFR_LT"] * processed[name]["Cyl"]["Power_out"]["omega"] / CONSTANTS[engine_type]["RPM_DES"]
        processed[name]["JWC"]["HTWater_in"]["mdot"] = CONSTANTS[engine_type]["MFR_HT"] * processed[name]["Cyl"]["Power_out"]["omega"] / CONSTANTS[engine_type]["RPM_DES"]
        # Asssigning values based on mass balances
        processed[name]["LOC"]["LTWater_out"]["mdot"] = processed[name]["LOC"]["LTWater_in"]["mdot"]
        processed[name]["CAC_LT"]["LTWater_out"]["mdot"] = processed[name]["LOC"]["LTWater_in"]["mdot"]
        processed[name]["CAC_LT"]["LTWater_out"]["mdot"] = processed[name]["LOC"]["LTWater_in"]["mdot"]
        processed[name]["JWC"]["HTWater_out"]["mdot"] = processed[name]["JWC"]["HTWater_in"]["mdot"]
        processed[name]["CAC_HT"]["HTWater_in"]["mdot"] = processed[name]["JWC"]["HTWater_in"]["mdot"]
        processed[name]["CAC_HT"]["HTWater_out"]["mdot"] = processed[name]["JWC"]["HTWater_in"]["mdot"]
        # Finally, the temperatures in the flows are calculated based on the calculated energy and mass flow values
        # For LT, first we have the CAC, then the LOC
        processed[name]["CAC_LT"]["LTWater_out"]["T"] = processed[name]["CAC_LT"]["LTWater_in"]["T"] + energy_2_cac_lt / processed[name]["CAC_LT"]["LTWater_out"]["mdot"] / CONSTANTS["General"]["CP_WATER"]
        processed[name]["LOC"]["LTWater_in"]["T"] = processed[name]["CAC_LT"]["LTWater_out"]["T"]
        processed[name]["LOC"]["LTWater_out"]["T"] = processed[name]["LOC"]["LTWater_in"]["T"] + energy_2_loc / processed[name]["LOC"]["LTWater_out"]["mdot"] / CONSTANTS["General"]["CP_WATER"]
        # For HT, first we have the JWC, then the CAC, HT
        processed[name]["JWC"]["HTWater_out"]["T"] = processed[name]["JWC"]["HTWater_in"]["T"] + energy_2_jwc / processed[name]["JWC"]["HTWater_out"]["mdot"] / CONSTANTS["General"]["CP_WATER"]
        processed[name]["CAC_HT"]["HTWater_in"]["T"] = processed[name]["JWC"]["HTWater_out"]["T"]
        processed[name]["CAC_HT"]["HTWater_out"]["T"] = processed[name]["CAC_HT"]["HTWater_in"]["T"] + energy_2_cac_ht / processed[name]["CAC_HT"]["HTWater_out"]["mdot"] / CONSTANTS["General"]["CP_WATER"]
    return processed




def auxEngineStatusCalculation(raw, processed, CONSTANTS, hd, status):
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        status[name]["Load"] = processed[name]["Cyl"]["Power_out"]["Wdot"] / CONSTANTS["AuxEngines"]["MCR"]
        # We consider the engines are on only if the load is above 5%
        status[name]["OnOff"] = raw[hd[name+"-TC__RPM_"]]> 5000
    return status

def auxEngineFuelFlowCalculation(raw, processed, CONSTANTS, status):
    # Proceeding with the auxiliary engines
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        bsfc_iso = status[name]["Load"].apply(polyvalHelperFunction, args=(CONSTANTS["AuxEngines"][
                                                                          "POLY_LOAD_2_ISO_BSFC"],))
        if name == "AE3":
            fuel_type = "HFO"
        else:
            fuel_type = "MDO"
        bsfc = bsfcISOCorrection(bsfc_iso, processed[name]["Cyl"]["Air_in"]["T"], processed[name]["CAC_LT"][
                "LTWater_in"]["T"], fuel_type, CONSTANTS)
        processed[name]["Cyl"]["FuelPh_in"]["mdot"] = bsfc * processed[name]["Cyl"]["Power_out"]["Wdot"] * 3600 / 1000
        processed[name]["Cyl"]["FuelCh_in"]["Wdot"] = processed[name]["Cyl"]["FuelPh_in"]["mdot"] * CONSTANTS["General"][
            "LHV_"+fuel_type]
    return processed


def auxEngineAirFlowCalculation(raw, processed, CONSTANTS):
    # This function calculates the different air and exhaust gas flows in the main engines, taking into account the
    # presence of air bypass and exhaust wastegate valves
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # Reading the pressure of the charge air after the compressor from the raw database
        # Calculating the compressor isentropic efficiency
        comp_isentropic_efficiency = processed[name]["Cyl"]["Air_in"]["p"].apply(polyvalHelperFunction,args=(CONSTANTS["AuxEngines"][
                                                                                   "POLY_PIN_2_ETA_IS"],))
        # Calculating the compressor's compression ratio
        beta_comp = processed[name]["TC"]["Air_out"]["p"] / processed[name]["TC"]["Air_in"]["p"]
        # Calculating the temperature after the compressor, based on ideal gas assumption
        processed[name]["TC"]["Air_out"]["T"] = processed[name]["TC"]["Air_in"]["T"] * (1 + beta_comp**((
            CONSTANTS["General"]["K_AIR"]-1)/CONSTANTS["General"]["K_AIR"])) / comp_isentropic_efficiency
        # The state of the air at the outlet of the compressor, outlet of the TC block, and inlet of the bypass valve
        #  are the same
        processed[name]["Comp"]["Air_out"]["T"] = processed[name]["TC"]["Air_out"]["T"]
        processed[name]["BPvalve"]["Air_in"]["T"] = processed[name]["TC"]["Air_out"]["T"]
        # The same temperature is the inlet to the charge air cooler
        processed[name]["CAC_HT"]["Air_in"]["T"] = processed[name]["TC"]["Air_out"]["T"]
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
        processed[name]["BPvalve"]["Air_in"]["mdot"] = (
            processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"] * (
                processed[name]["TC"]["EG_in"]["T"] - processed[name]["TC"]["EG_out"]["T"]) * CONSTANTS["MainEngines"]["ETA_MECH_TC"] -
            CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (
                processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"])) / (
            CONSTANTS["General"]["CP_AIR"] * (processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"]) -
            CONSTANTS["General"]["CP_EG"] * CONSTANTS["MainEngines"]["ETA_MECH_TC"] * (
                processed[name]["TC"]["EG_in"]["T"] - processed[name]["TC"]["EG_out"]["T"]))
        processed[name]["BPvalve"]["Air_out"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"]
        # The air mass flow going through the compressor is equal to the sum of the air flow through the bypass valve and
        # to the cylinders
        processed[name]["TC"]["Air_in"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["Air_in"]["mdot"]
        # Inlet and outlet flows to the compressor are equal
        processed[name]["TC"]["Air_out"]["mdot"] = processed[name]["TC"]["Air_in"]["mdot"]
        # The flow through the turbine is equal to the sum of the bypass flow and the exhaust coming from the cylinders
        processed[name]["TC"]["EG_in"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["EG_out"]["mdot"]
        # Calculating the temperature of the mixture after the merge between bypass and exhaust gas from the cylinders
        processed[name]["Cyl"]["EG_out"]["T"] = 298 + (
            processed[name]["TC"]["EG_in"]["mdot"] * CONSTANTS["General"]["CP_EG"] * (processed[name]["TC"]["EG_in"]["T"] - 298) -
            processed[name]["BPvalve"]["Air_in"]["mdot"] * CONSTANTS["General"]["CP_AIR"] * (processed[name]["TC"]["Air_out"]["T"] - 298)) / (
            processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"])
    return processed










def bsfcISOCorrection(bsfc_ISO, charge_air_temp, charge_air_cooling_temp, fuel_type, CONSTANTS):
    # This function calculates the "real" BSFC starting from the ISO corrected one and from measurements of
    # - Charge air temperature [K]
    # - Charge air coolant temperature [K]
    # - Fuel LHV [MJ/kg]
    # - Mechanical efficiency (often assumed at 0.8)

    # Assigning the value of the LHV depending on the fuel type
    if fuel_type == "HFO":
        LHV = CONSTANTS["General"]["LHV_HFO"]
    elif fuel_type == "MDO":
        LHV = CONSTANTS["General"]["LHV_MDO"]
    else:
        print("Error. The type of fuel provided is not in the list!")
    # Converting existing data (expected in the form of dataSeries
    if isinstance(charge_air_temp,pd.Series):
        T_ca = charge_air_temp.values
    else:
        print("Error: Expecting a pandas data series as data type")
    if isinstance(charge_air_cooling_temp,pd.Series):
        T_lt = charge_air_cooling_temp.values
    else:
        print("Error: Expecting a pandas data series as data type")
    # Providing reference values for the variables
    k = (CONSTANTS["General"]["ISO"]["T_CA"] / T_ca)**1.2 * (CONSTANTS["General"]["ISO"]["T_LT"] / T_lt)
    alpha = k - 0.7 * (1 - k) * (1/CONSTANTS["General"]["ISO"]["ETA_MECH"] - 1)
    beta = k / alpha
    # Final calculation of the BSFC
    bsfc = bsfc_ISO * CONSTANTS["General"]["ISO"]["LHV"] / LHV * beta
    return bsfc


def polyvalHelperFunction(x,p):
    # The problem with applying "polyval" to data series is that the "x" is the second argument of the function
    # instead of being the first. So we use this function to invert the two, waiting to find a better way
    output = np.polyval(p,x)
    return output
