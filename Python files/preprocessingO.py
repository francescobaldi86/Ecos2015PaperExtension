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
    processed["T_0"] = raw[hd["ER13_SW_T_IN"]] + 273.15
    processed["Other"]["SWC13"]["SeaWater"]["T_out"] = raw["SWC13_SeaWater_Tout"]  # CHECK IF IT IS IN OR OUT
    processed["Other"]["SWC24"]["SeaWater"]["T_out"] = raw["SWC24_SeaWater_Tout"]  # CHECK IF IT IS IN OR OUT
    processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    return processed


def trivialAssignment(processed, CONSTANTS):
    for name in processed:
        for unit in name:
            for flow in unit:
                connected_unit = flow["Connections"]
                split_name = splistring(connected_unit)
                name_c = split_name[0]
                unit_c = split_name[1]
                flow_c = split_name[2]
                for property in CONSTANTS["General"]["PROPERTY_LIST"][flow["type"]]:
                    if processed[name][unit][flow][property].isnan().sum() == 0:
                        if processed[name_c][unit_c][flow_c][property].isnan().sum() != 0:
                            processed[name_c][unit_c][flow_c][property] = processed[name][unit][flow][property]
                        elif processed[name][unit][flow][property] != processed[name_c][unit_c][flow_c][property]:
                            print("Something is wrong for %s_%s_%s_%s",name,unit,flow,property)




def engineStatusCalculation(type, raw, processed, CONSTANTS, status, hd):
    for name in CONSTANTS["General"]["NAMES"][type]:
        status[name]["Load"] = processed[name]["Cyl"]["Power_out"]["Wdot"] / CONSTANTS[type]["MCR"]
        # We consider that the engines are on if the RPM of the turbocharger is higher than 5000 RPM
        #status[name]["OnOff"] = (status[name]["Load"] > 0.05) & (processed[name]["Cyl"]["Power_out"]["omega"] > CONSTANTS["MainEngines"]["RPM_DES"] * 0.1)
        status[name]["OnOff"] = raw[hd[name+"-TC__RPM_"]] > 5000
    return status


def engineCoolingSystemsCalculation(processed, CONSTANTS, status, engine_type):
    # This function calculates the different flows related to the cooling systems of the main engines.
    for name in CONSTANTS["General"]["NAMES"][engine_type]:
        # Calculating the total energy flow going to the cooling systems, based on the energy balance on the engine
        energy_2_cooling = (processed[name]["Cyl"]["FuelCh_in"]["Wdot"] -
            processed[name]["Cyl"]["Power_out"]["Wdot"] +
            CONSTANTS["General"]["CP_HFO"] * processed[name]["Cyl"]["FuelPh_in"]["mdot"] *
                (processed[name]["Cyl"]["FuelPh_in"]["T"] - processed["T_0"]) -
            CONSTANTS["General"]["CP_EG"] * processed[name]["TC"]["EG_out"]["mdot"] *
                (processed[name]["TC"]["EG_out"]["T"] - processed["T_0"]) +
            CONSTANTS["General"]["CP_AIR"] * processed[name]["TC"]["Air_in"]["mdot"] *
                (processed[name]["TC"]["Air_in"]["T"] - processed["T_0"]))
        # Calculating the energy going to the charge air cooler, based on the estimated temperatures on the air line
        energy_2_cac = CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (processed[name]["TC"]["Air_out"]["T"] - processed[name]["Cyl"]["Air_in"]["T"])
        # Calculating the energy going to the HT cooling systems, based on interpolation from the project guide
        energy_2_ht_theoric = status[name]["Load"].apply(piecewisePolyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_HT"],)) * CONSTANTS[engine_type]["QDOT_HT_DES"]
        energy_2_lt_theoric = status[name]["Load"].apply(piecewisePolyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_LT"],)) * CONSTANTS[engine_type]["QDOT_LT_DES"]
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
        # For the LOC, we know the outlet (lower) temperature, we calculate the inlet temperature
        processed[name]["LOC"]["LubOil_out"]["mdot"][:] = CONSTANTS[engine_type]["MFR_LO"]
        processed[name]["LOC"]["LubOil_in"]["mdot"][:] = CONSTANTS[engine_type]["MFR_LO"]
        processed[name]["LOC"]["LubOil_in"]["T"] = processed[name]["LOC"]["LubOil_out"]["T"] + energy_2_loc / processed[name]["LOC"]["LubOil_out"]["mdot"] / CONSTANTS["General"]["CP_LO"]
    return processed



def bsfcISOCorrection(bsfc_ISO, charge_air_temp, charge_air_cooling_temp, fuel_temp, CONSTANTS):
    # This function calculates the "real" BSFC starting from the ISO corrected one and from measurements of
    # - Charge air temperature [K]
    # - Charge air coolant temperature [K]
    # - Fuel LHV [MJ/kg]
    # - Mechanical efficiency (often assumed at 0.8)

    # Assigning the value of the LHV depending on the fuel temperature
    LHV = pd.Series(0,index=charge_air_temp.index)
    LHV[fuel_temp < 70] = CONSTANTS["General"]["LHV_MDO"] # If T_fuel<70, it is Diesel
    LHV[fuel_temp >= 70] = CONSTANTS["General"]["LHV_HFO"] # If T_fuel>70, it is HFO
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
    return (bsfc, LHV)


def polyvalHelperFunction(x,p):
    # The problem with applying "polyval" to data series is that the "x" is the second argument of the function
    # instead of being the first. So we use this function to invert the two, waiting to find a better way
    output = np.polyval(p,x)
    return output

def piecewisePolyvalHelperFunction(x,p):
    # The problem with applying "polyval" to data series is that the "x" is the second argument of the function
    # instead of being the first. So we use this function to invert the two, waiting to find a better way
    output = np.piecewise(x, [x < 0.5 , x >= 0.5], [np.polyval(p[1],x) , np.polyval(p[0],x)])
    return output



def assumptions(raw, processed, CONSTANTS, hd):
    # This function includes generic assumed values in the main structure
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[name]["TC"]["Air_in"]["p"] = CONSTANTS["General"]["P_ATM"]
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[name]["TC"]["Air_in"]["p"] = CONSTANTS["General"]["P_ATM"]
    processed["T_0"] = raw[hd["ER13_SW_T_IN"]] + 273.15
    return processed