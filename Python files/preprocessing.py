# This module includes the functions that perform the "pre-processing": In short, they prepare the data structure
# that is then processed by the "Energy analysis" and "Exergy analysis" functions, all in one go.
#
# The module is made of :
# - One function that simply reads in the data that is already available from the original dataset


import numpy as np
import pandas as pd



def generalProcessing(raw, CONSTANTS):
    CONSTANTS["General"]["T_0"] = raw["T_SW"]
    return CONSTANTS




def mainEngineProcessing(raw, processed, CONSTANTS, status):
    # This script summarizes all the functions that calculate the required data for the Main Engines different flows

    # Reading existing values
    processed = readMainEnginesExistingValues(raw,processed,CONSTANTS)
    # Adding various assumptions on speific values
    processed = mainEnginesAssumptions(processed, CONSTANTS)
    # Calculating the main engines fuel flows
    processed = mainEngineFuelFlowCalculation(raw, processed, CONSTANTS)
    # Calculating the main engines power output
    processed = mainEnginePowerCalculation(processed, CONSTANTS)
    # Calculating engine load, that is used many times later on
    status = mainEngineStatusCalculation(processed,CONSTANTS,status)
    # Calculate air and exhaust gas flows in the main engines
    processed = mainEngineAirFlowCalculation(raw, processed, CONSTANTS)

    return processed



def readMainEnginesExistingValues(raw,processed,CONSTANTS):
    # This function only reads existing series. It does not do any pre-processing action.
    for name in CONSTANTS["NAMES"]["MainEngines"]:
        # Reading main engines exhaust gas temperature, TC inlet and outlet
        processed[name]["Cyl"]["EG_out"]["T"] = raw[name + "_TC_EG_T_in"]  # Measured before mixer with flow form bypass
        processed[name]["TC"]["EG_out"]["T"] = raw[name + "_TC_EG_T_out"]  # Measured after mixer with waste gate
        # Reading main engines exhaust gas temperature, after HRSG
        if idx==1 or idx==2:
            processed[name]["HRSG"]["EG_out"]["T"] = raw[name + "_HRSG_EG_T_out"]
            processed[name]["HRSG"]["EG_in"]["T"] = raw[name + "_TC_EG_T_out"]
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[name]["TC"]["Air_in"]["T"] = raw["ER_Air_T"]
        processed[name]["Comp"]["Air_in"]["T"] = processed[name]["TC"]["Air_in"]["T"]
        # Pressure of the charge air, at the compressor outlet (and, hence, at the cylinder inlet)
        processed[name]["TC"]["Air_out"]["p"] = raw[name+"air_p_out"]
        processed[name]["Cyl"]["Air_in"]["p"] = processed[name]["TC"]["Air_out"]["p"]
        processed[name]["BPvalve"]["Air_in"]["p"] = processed[name]["TC"]["Air_out"]["p"]
        # Reading the HT temperature before and after the main engine
        # processed[name]["CAC_HT"]["Water_out"]["T"] = raw[name + "_HT_water_T_out"] # Note: this might be inconsistent
        processed[name]["JWC"]["Water_in"]["T"] = raw[name + "_HT_water_T_in"]
        # Reading the LT temperature before the main engine
        processed[name]["CAC_LT"]["Water_in"]["T"] = raw[name + "_LT_water_T_in"]
        # Reading the Lubricating oil temperature before and after the Lubricating Oil Cooler (hence, In is higher)
        processed[name]["LOC"]["LubOil_in"]["T"] = raw[name + "_LOC_LubOil_T_in"]
        processed[name]["LOC"]["LubOil_out"]["T"] = raw[name + "_LOC_LubOil_T_out"]
        # Reading fuel oil temperature before injection
        processed[name]["Cyl"]["Fuel_in"]["T"] = raw[name + "_fuel_T_in"]
        # Reading charge air temperature, after the charge air cooler (or at cylinder inlet)
        processed[name]["CAC_LT"]["Air_out"]["T"] = raw[name + "_CAC_air_T_out"]
        processed[name]["Cyl"]["Air_in"]["T"] = processed[name]["CAC_LT"]["Air_out"]["T"]
        # Reading Engine rpm
        processed[name]["Cyl"]["Power_out"]["omega"] = raw[name + "_rpm"]
        return processed


def mainEnginesAssumptions(processed,CONSTANTS):
    # This function writes includes generic assumed values in the main structure
    for name in CONSTANTS["NAMES"]["MainEngines"]:
        # The pressure at the engine inlet is equal to the measured value plus the atmospheric pressure
        processed[name]["TC"]["Air_in"]["p"] = processed[name]["TC"]["Air_in"]["p"] + CONSTANTS["General"]["P_ATM"]
        # The temperature


def readAuxiliaryEnginesExistingValues(raw, processed,CONSTANTS):
    for name in CONSTANTS["NAMES"]["AuxiliaryEngines"]:
        # Reading main engines exhaust gas temperature, TC inlet and outlet
        processed[name]["TC"]["EG_in"]["T"] = raw[name + "_TC_EG_T_in"]
        processed[name]["TC"]["EG_out"]["T"] = raw[name + "_TC_EG_T_out"]
        # Reading main engines exhaust gas temperature, after HRSG
        processed[name]["HRSG"]["EG_out"]["T"] = raw[name + "_HRSG_EG_T_out"]
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[name]["TC"]["Air_in"]["T"] = raw["ER_Air_T"]
        # Reading the HT temperature before and after the main engine
        processed[name]["JWC"]["Water_in"]["T"] = raw[name + "_HT_water_T_in"]
        # Reading the LT temperature before the main engine
        processed[name]["CAC_LT"]["Water_in"]["T"] = raw[name + "_LT_water_T_in"]
        # Reading the Lubricating oil temperature before and after the Lubricating oil cooler
        processed[name]["LOC"]["LubOil_out"]["T"] = raw[name + "_LOC_LubOil_T_out"]
        # Reading fuel oil temperature before injection
        processed[name]["Cyl"]["Fuel_in"]["T"] = raw[name + "_fuel_T_in"]
        # Reading charge air temperature. NOTE: THE PRESSURE IS NOT READ, because it does not participate in the EA
        processed[name]["CAC_HT"]["Air_in"]["T"] = raw[name + "_CAC_air_T_in"]
        return processed


def readOtherExistingValues(raw, processed):
    # Other components
    processed["Other"]["SWC13"]["SeaWater"]["T_out"] = raw["SWC13_SeaWater_Tout"]  # CHECK IF IT IS IN OR OUT
    processed["Other"]["SWC24"]["SeaWater"]["T_out"] = raw["SWC24_SeaWater_Tout"]  # CHECK IF IT IS IN OR OUT
    processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    return processed


def mainEngineFuelFlowCalculation(raw, processed, CONSTANTS):
    # This function calculates the engine
    for name in CONSTANTS["NAMES"]["MainEngines"]:
        # This function calculates the fuel flow of the main engines
        # In the case of the main engines, the fuel flow of an engine is calculated given its fuel
        # rack position and its rotating speed.
        processed[name]["Cyl"]["FuelPh"]["mdot_in"] = CONSTANTS["MainEngines"]["MFR_FUEL_DES"] * (
        (CONSTANTS["MainEngines"]["POLY_FRP_2_MF"][0] + CONSTANTS["MainEngines"]["POLY_FRP_2_MF"][1] *
         fuel_rack_position) / (CONSTANTS["MainEngines"]["POLY_FRP_2_MF"][0] + CONSTANTS["MainEngines"][
            "POLY_FRP_2_MF"][1] * CONSTANTS["MainEngines"]["FRP_DES"])) * (
             engine_speed / CONSTANTS["MainEngines"]["RPM_DES"])
        processed[name]["Cyl"]["FuelCh"]["Qdot_in"] = processed["name"]["Cyl"]["FuelPh"]["mdot_in"] * CONSTANTS[
            "LHV_HFO"]
    return processed


def mainEnginePowerCalculation(processed, CONSTANTS, status):
    # This function calculates the Power of the engine starting from the efficiency of the engine,
    # which is calcualted starting from other available data
    for name in CONSTANTS["NAMES"]["MainEngines"]:
        # Calculate fuel flow-based engine load
        fuel_based_load = processed[name]["Cyl"]["FuelPh_in"]["mdot"] / CONSTANTS["MainEngines"]["MFR_FUEL_DES"]
        # Calculate ISO fuel mass flow rate
        mfr_fuel_iso = fuel_based_load * CONSTANTS["MainEngines"]["MFR_FUEL_DES_ISO"]
        # Calculate ISO bsfc (break specific fuel consumption)
        bsfc_iso = fuel_based_load.apply(polyvalHelperFunction, args=(CONSTANTS["MainEngines"][
                                                                          "POLY_FUEL_LOAD_2_BSFC_ISO"],))
        # Corrects the bsfc from ISO conditions to "real" conditions
        bsfc = bsfcISOCorrection(bsfc_iso,processed[name]["Cyl"]["Air_in"]["T"],processed["name"]["CAC_LT"][
            "LTWater_in"]["T"],"HFO",CONSTANTS)
        # Calculates the power of the engine as mfr/bsfc, with unit conversion to get the output in kW
        processed[name]["Cyl"]["Power"]["Wdot"] = - processed[name]["Cyl"]["FuelPh_in"]["mdot"] / bsfc * 1000 * 3600
        return processed


def mainEngineStatusCalculation(processed, CONSTANTS, status):
    for name in CONSTANTS["NAMES"]["MainEngines"]:
        status[name]["Load"] = - processed[name]["Cyl"]["Power"]["Wdot"] / CONSTANTS["MainEngines"]["MCR"]
        # We consider the engines are on only if the load is above 5% and if the speed is above 10% of the nominal value
        status[name]["OnOff"] = status[name]["Load"] > 0.05 and processed[name]["Cyl"]["Power"]["omega"] > 600 * 0.1
        return status


def mainEngineAirFlowCalculation(raw, processed, CONSTANTS):
    # This function calculates the different air and exhaust gas flows in the main engines, taking into account the
    # presence of air bypass and exhaust wastegate valves
    for name in CONSTANTS["NAMES"]["MainEngines"]:
        # Reading the pressure of the charge air after the compressor from the raw database
        # Calculating the compressor isentropic efficiency
        comp_isentropic_efficiency = processed[name]["Cyl"]["Air_in"]["p"].apply(polyvalHelperFunction,args=(CONSTANTS["MainEngines"][
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
            CONSTANTS["MainEngines"]["N_CYL"])
        processed[name]["Cyl"]["EG_out"]["mdot"] = processed[name]["Cyl"]["Air_in"]["mdot"] + processed[name]["Cyl"][
            "FuelPh_in"]["mdot"]
        # Here we calculate the bypass mass flow. THIS NEEDS TO BE CHECKED FOR CONSISTENCY (i.e. the bypass mass flow
        #  should always be kind of low, and anyway only be seen at low to medium load).
        # The equation is the result of a mass and energy balance over the whole engine
        processed[name]["BPvalve"]["Air_in"]["mdot"] = (
            processed[name]["Cyl"]["EG_out"]["mdot"] * CONSTANTS["General"]["CP_EG"] * (
                processed[name]["Cyl"]["EG_out"]["T"] - processed[name]["TC"]["EG_out"]["T"]) - (
                    CONSTANTS["General"]["CP_AIR"] / CONSTANTS["MainEngines"]["ETA_MECH_TC"] *
            processed[name]["Cyl"]["Air_in"]["mdot"] * (
                        processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"]))) / (
            CONSTANTS["General"]["CP_EG"] * (
            processed[name]["TC"]["EG_out"]["T"] - processed[name]["Compressor"]["Air_out"]["T"]) +
            CONSTANTS["General"]["CP_AIR"] / CONSTANTS["MainEngines"]["ETA_MECH_TC"] * (
            processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"]))
        processed[name]["BPvalve"]["Air_out"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"]
    # Calculating the temperature of the mixture after the merge between bypass and exhaust gas from the cylinders
    processed[name]["TC"]["EG_in"]["T"] = processed[name]["Cyl"]["EG_out"]["T"] - (
        processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["Air_in"]["mdot"] * CONSTANTS[
            "General"]["CP_AIR"] * (
            processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Comp"]["Air_in"]["T"])) /\
            CONSTANTS["MainEngines"]["ETA_MECH_TC"] / processed[name]["Cyl"]["EG_out"]["mdot"]
    # The air mass flow going through the compressor is equal to the sum of the air flow through the bypass valve and
    # to the cylinders
    processed[name]["TC"]["Air_in"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["Air_in"]["mdot"]
    # Inlet and outlet flows to the compressor are equal
    processed[name]["TC"]["Air_out"]["mdot"] = processed[name]["TC"]["Air_in"]["mdot"]
    # The flow through the turbine is equal to the sum of the bypass flow and the exhaust coming from the cylinders
    processed[name]["TC"]["EG_in"]["mdot"] = processed[name]["BPvalve"]["Air_in"]["mdot"] + processed[name]["Cyl"]["EG_out"]["mdot"]


def mainEngineCoolingSystemsCalculation(raw, processed, CONSTANTS, status):
    # This function calculates the different flows related to the cooling systems of the main engines.
    for name in CONSTANTS["NAMES"]["MainEngines"]:
        # Calculating the total energy flow going to the cooling systems, based on the energy balance on the engine
        energy_2_cooling = processed[name]["Cyl"]["FuelCh_in"]["Wdot"] - processed[name]["Cyl"]["FuelCh_in"]["Wdot"] + (
            CONSTANTS["General"]["CP_HFO"] * processed[name]["Cyl"]["FuelPh_in"]["mdot"] * (processed[name]["Cyl"]["FuelPh_in"]["T"] - CONSTANTS["General"]["T_0"])) - (
            CONSTANTS["General"]["CP_EG"] * processed[name]["TC"]["EG_out"]["mdot"] * (processed[name]["TC"]["EG_out"]["T"] - CONSTANTS["General"]["T_0"])) + (
            CONSTANTS["General"]["CP_AIR"] * processed[name]["TC"]["Air_in"]["mdot"] * (processed[name]["TC"]["Air_in"]["T"] - CONSTANTS["General"]["T_0"]))
        # Calculating the energy going to the charge air cooler, based on the estimated temperatures on the air line
        energy_2_cac = CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (processed[name]["TC"]["Air_out"]["T"] - processed[name]["Cyl"]["Air_in"]["T"])
        # Calculating the energy going to the HT cooling systems, based on interpolation from the project guide
        energy_2_ht_theoric = status[name]["load"].apply(polyvalHelperFunction,args=(CONSTANTS["MainEngines"]["POLY_LOAD_2_QDOT_HT"],))
        energy_2_lt_theoric = status[name]["load"].apply(polyvalHelperFunction,args=(CONSTANTS["MainEngines"]["POLY_LOAD_2_QDOT_LT"],))
        # The values calculated based on the project guide are reconciled based on the energy balance
        energy_2_ht = energy_2_cooling * energy_2_ht_theoric / (energy_2_ht_theoric + energy_2_lt_theoric)
        energy_2_lt = energy_2_cooling - energy_2_ht
        # The energy going to the CAC, HT stage is calculated assuming a 85% effectiveness of the heat exchanger
        energy_2_cac_ht = CONSTANTS["MainEngines"]["EPS_CAC_HTSTAGE"] * processed[name]["TC"]["Air_in"]["mdot"] * CONSTANTS["General"]["CP_AIR"] * (
            processed[name]["TC"]["Air_out"]["T"] - processed[name]["TC"]["Water_in"]["T"])
        # The energy going to the CAC, LT stage results as a consequence by thermal balance over the CAC
        energy_2_cac_lt = energy_2_cac - energy_2_cac_ht
        # The energy to the JWC results as a balance over the HT cooling systems
        energy_2_jwc = energy_2_ht - energy_2_cac_ht
        # The energy to the LOC results as a balance over the LT cooling systems
        energy_2_loc = energy_2_lt - energy_2_cac_lt
        # For all pumps, it is here assumed that the flow scales only with the speed of the engine (biiiiig assumption)
        processed[name]["LOC"]["LTWater_in"]["mdot"] = CONSTANTS["MainEngines"]["MFR_LT"] * processed[name]["Cyl"]["Power"]["omega"] / CONSTANTS["MainEngines"]["RPM_DES"]
        processed[name]["LOC"]["LTWater_out"]["mdot"] = processed[name]["LOC"]["LTWater_in"]["mdot"]
        processed[name]["CAC_LT"]["LTWater_out"]["mdot"] = processed[name]["LOC"]["LTWater_in"]["mdot"]
        processed[name]["CAC_LT"]["LTWater_out"]["mdot"] = processed[name]["LOC"]["LTWater_in"]["mdot"]
        processed[name]["JWC"]["HTWater_in"]["mdot"] = CONSTANTS["MainEngines"]["MFR_HT"] * processed[name]["Cyl"]["Power"]["omega"] / CONSTANTS["MainEngines"]["RPM_DES"]
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
        processed[name]["CAC_HT"]["HTWater_out"]["T"] = processed[name]["CAC_HT"]["Water_in"]["T"] + energy_2_cac_ht / processed[name]["CAC_HT"]["HTWater_out"]["mdot"] / CONSTANTS["General"]["CP_WATER"]







def auxiliaryEngineFuelFlowCalculation(raw, processed, CONSTANTS):
    # Proceeding with the auxiliary engines
    name = "AE" + str(idx + 1)
    processed["name"]["Cyl"]["FuelPh"]["mdot_in"] = 2
    return processed






def bsfcISOCorrection(bsfc_ISO,charge_air_temp,charge_air_cooling_temp,fuel_type,CONSTANTS)
    # This function calculates the "real" BSFC starting from the ISO corrected one and from measurements of
    # - Charge air temperature [K]
    # - Charge air coolant temperature [K]
    # - Fuel LHV [MJ/kg]
    # - Mechanical efficiency (often assumed at 0.8)

    # Assigning the value of the LHV depending on the fuel type
    if fuel_type == "HFO":
        LHV = CONSTANTS["LHV_HFO"]
    elif fuel_type == "MDO":
        LHV = CONSTANTS["LHV_HFO"]
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
    k = (CONSTANTS["ISO"]["T_CA"] / T_ca)**1.2 * (CONSTANTS["ISO"]["T_LT"] / T_lt)
    alpha = k - 0.7 * (1 - k) * (1/CONSTANTS["ISO"]["ETA_MECH"] - 1)
    beta = k / alpha
    # Final calculation of the BSFC
    bsfc = bsfc_ISO * CONSTANTS["ISO"]["LHV"] / CONSTANTS["ISO"]["LHV"] * beta
    return bsfc


def polyvalHelperFunction(x,p):
    # The problem with applying "polyval" to data series is that the "x" is the second argument of the function
    # instead of being the first. So we use this function to invert the two, waiting to find a better way
    output = np.polyval(p,x)
    return output
















## SONO ARRIVATO FIN QUI ##
## Auxiliary engines
## Power - fuel flow - efficiency
AE_load.(char(AE_names(i))) = AE_power.(char(AE_names(i))). / MCR_AE. * AE_on.(char(AE_names(i)));
AE_bsfc_ISO = polyval(AE_POLY_LOAD_2_ISO_BSFC, AE_load.(char(AE_names(i))));
if i == 3
    AE_bsfc.(char(AE_names(i))) = bsfcISOCorrection(AE_bsfc_ISO,
                                                    AE_T_LTcooling.(char(AE_names(i)))(:, 1), AE_T_charge_air.(
        char(AE_names(i))), LHV_MDO, 0.8) *AE_ETA_CORR;
else
    AE_bsfc.(char(AE_names(i))) = bsfcISOCorrection(AE_bsfc_ISO,
                                                    AE_T_LTcooling.(char(AE_names(i)))(:, 1), AE_T_charge_air.(
        char(AE_names(i))), LHV, 0.8) *AE_ETA_CORR;
end
AE_mfr_fuel.(char(AE_names(i))) = AE_power.(char(AE_names(i))). * AE_bsfc.(char(AE_names(i))). / 3.6e6. * AE_on.(
    char(AE_names(i)));
energy.AE.power(:, i) = AE_power.(char(AE_names(i)));
if i == 3
    # The engine number 3 runs on gas oil
    energy.AE.fuel_ch(:, i) = AE_mfr_fuel.(char(AE_names(i))). * LHV_MDO;
    energy.AE.fuel_th(:, i) = AE_mfr_fuel.(char(AE_names(i))). * CP_HFO. * (303 - T0);
else
    energy.AE.fuel_ch(:, i) = AE_mfr_fuel.(char(AE_names(i))) * LHV;
    energy.AE.fuel_th(:, i) = AE_mfr_fuel.(char(AE_names(i))). * CP_HFO. * (AE_T_fuel_oil.(char(AE_names(i))) - T0);
end
energy.AE.fuel(:, i) = energy.AE.fuel_ch(:, i) + energy.AE.fuel_th(:, i);
## Air flows
AE_T_air.(char(AE_names(i)))(:, 1) = T_ER;  # Temperature before compressor is assumed to be constant
# Temperature after the compressor
AE_T_air.(char(AE_names(i)))(:, 2) = AE_T_air.(char(AE_names(i)))(:, 1).*(
1 + (AE_p_charge_air.(char(AE_names(i))). ^ ((K_AIR - 1) / K_AIR) - 1). / polyval(AE_POLY_PIN_2_ETA_IS,
                                                                                  AE_p_charge_air.(char(AE_names(i)))));
# Mass flow rate to the engine is calculated based on the approximation of ideal gas conditions in the engine cylinders at max volume
mdot_air_2engine = AE_V_MAX. * AE_p_charge_air.(char(AE_names(i))) * 1e5. / R_AIR. / AE_T_charge_air.(
    char(AE_names(i))). * AE_rpm.(char(AE_names(i))) / 60 / 2 * ETA_VOL * AE_N_CYL. * AE_on.(char(AE_names(i)));
# Exhaust flow leaving the engine equal to sum of air and fuel flows
mdot_eg_fromengine = mdot_air_2engine + AE_mfr_fuel.(char(AE_names(i)));
# Final supercalculation
mdot_air_bypass = (mdot_eg_fromengine. * CP_EG. * (AE_T_eg.(char(AE_names(i)))(:, 1) - AE_T_eg.(
    char(AE_names(i)))(:, 2)) - CP_AIR / ETA_MECH_TC. * mdot_air_2engine. * (
AE_T_air.(char(AE_names(i)))(:, 2) - AE_T_air.(char(AE_names(i)))(:, 1)))./ ...
(CP_EG. * (AE_T_eg.(char(AE_names(i)))(:, 2) - AE_T_air.(char(AE_names(i)))(:, 2)) + CP_AIR / ETA_MECH_TC. * (
AE_T_air.(char(AE_names(i)))(:, 2) - AE_T_air.(char(AE_names(i)))(:, 1)));
T_eg_beforeBypass = AE_T_eg.(char(AE_names(i)))(:, 1) - (
mdot_air_bypass + mdot_air_2engine. * CP_AIR. * (AE_T_air.(char(AE_names(i)))(:, 2) - AE_T_air.(
    char(AE_names(i)))(:, 1)))./ ETA_MECH_TC. / CP_EG. / mdot_eg_fromengine;
AE_mfr_air.(char(AE_names(i))) = mdot_air_bypass + mdot_air_2engine;
AE_mfr_eg.(char(AE_names(i))) = mdot_air_bypass + mdot_eg_fromengine;
## Energy in the air flows
energy.AE.air_1(:, i) = AE_mfr_air.(char(AE_names(i))). * CP_AIR. * (
AE_T_air.(char(AE_names(i)))(:, 1) - T0);  # Inlet flow, at Engine Room temperature
energy.AE.air_2(:, i) = AE_mfr_air.(char(AE_names(i))). * CP_AIR. * (
AE_T_air.(char(AE_names(i)))(:, 2) - T0);  # After the compressor, at high temperature
energy.AE.air_3(:, i) = mdot_air_2engine. * CP_AIR. * (
AE_T_air.(char(AE_names(i)))(:, 3) - T0);  # After the CAC, at low temperature again
## Energy in the exhaust gas flows
energy.AE.eg_1(:, i) = AE_mfr_eg.(char(AE_names(i))). * CP_EG. * (
AE_T_eg.(char(AE_names(i)))(:, 1) - T0);  # 1 - after engine, before TC
energy.AE.eg_2(:, i) = AE_mfr_eg.(char(AE_names(i))). * CP_EG. * (
AE_T_eg.(char(AE_names(i)))(:, 2) - T0);  # 1 - after engine, after TC (and after merging with the air bypass)
energy.AE.eg_3(:, i) = AE_mfr_eg.(char(AE_names(i))). * CP_EG. * (
AE_T_eg.(char(AE_names(i)))(:, 3) - T0);  # 2 - after TC, before ExBo
energy.AE.hrsg(:, i) = energy.AE.eg_2(:, i) - energy.AE.eg_3(:, i);
## Energy to cooling systems
energy_2_cooling = energy.AE.fuel(:, i) - energy.AE.power(:, i) - energy.AE.eg_2(:, i) + energy.AE.air_1(:, i);
# Charge air cooler (total)
energy.AE.cac(:, i) = energy.AE.air_2(:, i).*mdot_air_2engine. / (
mdot_air_2engine + mdot_air_bypass) - energy.AE.air_3(:, i);
# HT cooling systems
energy.AE.ht(:, i) = energy_2_cooling. * polyval(AE_POLY_LOAD_2_QDOT_HT, AE_load.(char(AE_names(i)))). / (
polyval(AE_POLY_LOAD_2_QDOT_HT, AE_load.(char(AE_names(i)))) + polyval(AE_POLY_LOAD_2_QDOT_LT,
                                                                       AE_load.(char(AE_names(i)))));
# LT cooling systems
energy.AE.lt(:, i) = energy_2_cooling - energy.AE.ht(:, i);
# Charge air cooling, HT stage
energy.AE.cac_ht(:, i) = mdot_air_2engine. * CP_AIR. * (AE_T_air.(char(AE_names(i)))(:, 2) - AE_T_air.(
    char(AE_names(i)))(:, 1)).*EPS_CAC_HTSTAGE;  # Assuming 0.85 effectiveness
# Charge air cooling, LT stage
energy.AE.cac_lt(:, i) = energy.AE.cac(:, i) - energy.AE.cac_ht(:, i);
# Jacket water
energy.AE.jw(:, i) = energy.AE.ht(:, i) - energy.AE.cac_ht(:, i);
energy.AE.jw_ht(:, i) = energy.AE.jw(:, i);
# Lubricating Oil
energy.AE.lo(:, i) = energy.AE.lt(:, i) - energy.AE.cac_lt(:, i);
energy.AE.lo_lt(:, i) = energy.AE.lo(:, i);
## Details of cooling flows
# Mass flows.
# Calculated assuming that there is a linear relationship with the engine speed (engine driven pumps)
AE_mfr_ht(:, i) = AE_MFR_HT. * AE_rpm.(char(AE_names(
    i))) / RPM_DES_AE;  # Here we make the assumption that the mass flow rate of HT cooling water in the main engines is linearly proportional to the engine laod...
AE_mfr_lt(:, i) = AE_MFR_LT. * AE_rpm.(char(AE_names(
    i))) / RPM_DES_AE;  # Here we make the assumption that the mass flow rate of LT cooling water in the main engines is linearly proportional to the engine laod...
AE_mfr_lo(:, i) = AE_MFR_LO;
AE_T_lub_oil.(char(AE_names(i)))(:, 2) = AE_T_lub_oil.(
    char(AE_names(i)))(:, 1) + energy.AE.lo(:, i)./ CP_LO. / AE_mfr_lo(:, i);

# Temperatures
AE_T_LTcooling.(char(AE_names(i)))(:, 2) = AE_T_LTcooling.(
    char(AE_names(i)))(:, 1) + energy.AE.cac_lt(:, i)./ CP_W. / AE_mfr_lt(:, i);  # Temperature before the LO cooler
AE_T_LTcooling.(char(AE_names(i)))(:, 3) = AE_T_LTcooling.(
    char(AE_names(i)))(:, 2) + energy.AE.lo(:, i)./ CP_W. / AE_mfr_lt(:, i);  # Temperature before mixing with the HT
AE_T_LTcooling.(char(AE_names(i)))(:, 4) = AE_T_LTcooling.(
    char(AE_names(i)))(:, 3) + energy.AE.ht(:, i)./ CP_W. / AE_mfr_lt(:, i);  # Temperature after mixing with the HT
AE_T_HTcooling.(char(AE_names(i)))(:, 2) = AE_T_HTcooling.(
    char(AE_names(i)))(:, 1) + energy.AE.cac_ht(:, i)./ CP_W. / AE_mfr_ht(:, i);  # Temperature before the JW cooler
AE_T_HTcooling.(char(AE_names(i)))(:, 3) = AE_T_HTcooling.(char(
    AE_names(i)))(:, 2) + energy.AE.jw(:, i)./ CP_W. / AE_mfr_ht(:, i);  # Temperature after the JW cooler











## Eliminating NaN values from when the engine is off
energy_ME_fieldnames = fieldnames(energy.ME);
for k = 1: length(energy_ME_fieldnames)
energy.ME.(char(energy_ME_fieldnames(k)))(ME_on.(char(ME_names(i))) == 0, i) = 0;
end
energy_AE_fieldnames = fieldnames(energy.AE);
for k = 1: length(energy_AE_fieldnames)
energy.AE.(char(energy_AE_fieldnames(k)))(AE_on.(char(AE_names(i))) == 0, i) = 0;
end

end






