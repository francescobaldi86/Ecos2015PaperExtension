import numpy as np
import pandas as pd


def assumptions(raw, processed, CONSTANTS, hd):
    # This function includes generic assumed values in the main structure
    for name in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[name]["Comp"]["Air_in"]["p"][:] = CONSTANTS["General"]["P_ATM"]
    for name in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[name]["Comp"]["Air_in"]["p"][:] = CONSTANTS["General"]["P_ATM"]
    T_0 = raw[hd["SEA_SW_T_"]] + 273.15
    processed["Other"]["SWC13"]["SeaWater_out"]["T"] = raw[hd["SWC13_SW_T_OUT"]]  # CHECK IF IT IS IN OR OUT
    processed["Other"]["SWC24"]["SeaWater_out"]["T"] = raw[hd["SWC24_SW_T_OUT"]]  # CHECK IF IT IS IN OR OUT
    #processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    #processed["Other"]["SWC24"]["SeaWater"]["T_in"] = raw["SeaWater_T"]
    return (processed, T_0)


def trivialAssignment(processed, CONSTANTS):
    print("Started calculating the known connected flows...")
    for name in processed:
        for unit in processed[name]:
            for flow in processed[name][unit]:
                if "Connections" in processed[name][unit][flow].keys():
                    connected_unit = processed[name][unit][flow]["Connections"]
                    split_name = connected_unit.split(":")
                    name_c = split_name[0]
                    unit_c = split_name[1]
                    flow_c = split_name[2]
                    for property in CONSTANTS["General"]["PROPERTY_LIST"][processed[name][unit][flow]["type"]]:
                        if processed[name][unit][flow][property].isnull().sum() == 0:
                            if processed[name_c][unit_c][flow_c][property].isnull().sum() != 0:
                                processed[name_c][unit_c][flow_c][property] = processed[name][unit][flow][property]
                            elif not (processed[name][unit][flow][property].equals(processed[name_c][unit_c][flow_c][property])):
                                print("Something is wrong for {} {} {} {}".format(name,unit,flow,property))
                    if ("EG" in flow or "Mix" in flow):
                        if "N2" in processed[name][unit][flow]["Connections"]:
                            if "N2" not in processed[name][unit][flow]["Connections"]:
                                processed[name_c][unit_c][flow_c]["Connections"] = processed[name][unit][flow]["Connections"]
                            elif not (processed[name][unit][flow]["Connections"]["N2"].equals(processed[name_c][unit_c][flow_c]["Connections"]["N2"])):
                                print("Something is wrong for {} {} {} {}".format(name,unit,flow,property))
    print("...done!")
    return processed




def engineStatusCalculation(type, raw, processed, CONSTANTS, status, hd):
    for name in CONSTANTS["General"]["NAMES"][type]:
        status[name]["Load"] = processed[name]["Cyl"]["Power_out"]["Wdot"] / CONSTANTS[type]["MCR"]
        # We consider that the engines are on if the RPM of the turbocharger is higher than 5000 RPM
        #status[name]["OnOff"] = (status[name]["Load"] > 0.05) & (processed[name]["Cyl"]["Power_out"]["omega"] > CONSTANTS["MainEngines"]["RPM_DES"] * 0.1)
        status[name]["OnOff"] = raw[hd[name+"-TC__RPM_"]] > 5000
    return status


def engineCoolingSystemsCalculation(processed, CONSTANTS, status, engine_type, T_0):
    print("Started calculating analysis for {} cooling systems...".format(engine_type))
    # This function calculates the different flows related to the cooling systems of the main engines.
    for name in CONSTANTS["General"]["NAMES"][engine_type]:
        # Calculating the total energy flow going to the cooling systems, based on the energy balance on the engine
        energy_2_cooling = (processed[name]["Cyl"]["FuelCh_in"]["Wdot"] -
            processed[name]["Cyl"]["Power_out"]["Wdot"] +
            CONSTANTS["General"]["HFO"]["CP"] * processed[name]["Cyl"]["FuelPh_in"]["mdot"] *
                (processed[name]["Cyl"]["FuelPh_in"]["T"] - T_0) -
            CONSTANTS["General"]["CP_EG"] * processed[name]["Turbine"]["Mix_out"]["mdot"] *
                (processed[name]["Turbine"]["Mix_out"]["T"] - T_0) +
            CONSTANTS["General"]["CP_AIR"] * processed[name]["Comp"]["Air_in"]["mdot"] *
                (processed[name]["Comp"]["Air_in"]["T"] - T_0))
        # Calculating the energy going to the charge air cooler, based on the estimated temperatures on the air line
        energy_2_cac = CONSTANTS["General"]["CP_AIR"] * processed[name]["Cyl"]["Air_in"]["mdot"] * (processed[name]["Comp"]["Air_out"]["T"] - processed[name]["Cyl"]["Air_in"]["T"])
        # Calculating the energy going to the HT cooling systems, based on interpolation from the project guide
        energy_2_ht_theoric = status[name]["Load"].apply(piecewisePolyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_HT"],)) * CONSTANTS[engine_type]["QDOT_HT_DES"]
        energy_2_lt_theoric = status[name]["Load"].apply(piecewisePolyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_LT"],)) * CONSTANTS[engine_type]["QDOT_LT_DES"]
        # The values calculated based on the project guide are reconciled based on the energy balance
        energy_2_ht = energy_2_cooling * energy_2_ht_theoric / (energy_2_ht_theoric + energy_2_lt_theoric)
        energy_2_lt = energy_2_cooling - energy_2_ht
        # The energy going to the CAC, HT stage is calculated assuming a 85% effectiveness of the heat exchanger
        energy_2_cac_ht = CONSTANTS[engine_type]["EPS_CAC_HTSTAGE"] * processed[name]["Comp"]["Air_in"]["mdot"] * CONSTANTS["General"]["CP_AIR"] * (
            processed[name]["Comp"]["Air_out"]["T"] - processed[name]["CAC_HT"]["HTWater_in"]["T"])
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
        processed[name]["LOC"]["LubOil_in"]["T"] = processed[name]["LOC"]["LubOil_out"]["T"] + energy_2_loc / processed[name]["LOC"]["LubOil_out"]["mdot"] / CONSTANTS["General"]["CP_LO"]
    print("...done!")
    return processed



def bsfcISOCorrection(bsfc_ISO, charge_air_temp, charge_air_cooling_temp, fuel_temp, CONSTANTS):
    # This function calculates the "real" BSFC starting from the ISO corrected one and from measurements of
    # - Charge air temperature [K]
    # - Charge air coolant temperature [K]
    # - Fuel LHV [MJ/kg]
    # - Mechanical efficiency (often assumed at 0.8)

    # Assigning the value of the LHV depending on the fuel temperature
    LHV = pd.Series(0,index=charge_air_temp.index)
    LHV[fuel_temp < 70] = CONSTANTS["General"]["MDO"]["LHV"] # If T_fuel<70, it is Diesel
    LHV[fuel_temp >= 70] = CONSTANTS["General"]["HFO"]["LHV"] # If T_fuel>70, it is HFO
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


def mixtureComposition(composition,mdot_air,mdot_fuel,temp_fuel,CONSTANTS):
    # This value takes as input the flow of air and fuel and calculates the resulting composition of the exhaust gas, assuming full combustion
    # The composition is written in the code accepted by CoolProp, i.e. in the form:
    # "HEOS::COMP_1[%]&COMP_2[%]..."
    # Accepted components are: N2, O2, CO2, H2O (SO2?)
    # The composition is a dataframe of 4 columns, in the order above
    mixture = pd.Series(index=mdot_air.index)
    fuel_C_x = pd.Series(0,index=mdot_air.index)
    fuel_H_x = pd.Series(0,index=mdot_air.index)
    # Reading from the data the mass composition of the fuel, depending on its temperature
    fuel_C_x[temp_fuel < 70] = CONSTANTS["General"]["MDO"]["C"] # If T_fuel<70, it is Diesel
    fuel_C_x[temp_fuel >= 70] = CONSTANTS["General"]["HFO"]["C"] # If T_fuel>70, it is HFO
    fuel_H_x[temp_fuel < 70] = CONSTANTS["General"]["MDO"]["H"]  # If T_fuel<70, it is Diesel
    fuel_H_x[temp_fuel >= 70] = CONSTANTS["General"]["HFO"]["H"]  # If T_fuel>70, it is HFO
    # Calculating the elemental molar flows
    fuel_C_molfr = mdot_fuel * fuel_C_x / 12
    fuel_H_molfr = mdot_fuel * fuel_H_x
    air_N2_molfr = mdot_air * 0.77 / 28
    air_O2_molfr = mdot_air * 0.23 / 32
    output_CO2_molfr = fuel_C_molfr
    output_H2O_molfr = fuel_H_molfr / 2
    output_N2_molfr = air_N2_molfr
    output_O2_molfr = air_O2_molfr - output_CO2_molfr - output_H2O_molfr / 2
    # Finally, calculating the compositions
    tot_molfr = output_CO2_molfr + output_H2O_molfr + output_N2_molfr + output_O2_molfr
    tot_molfr[tot_molfr==0] = 1 # Just to avoid N2comp and so == NaN
    O2 = output_O2_molfr / tot_molfr
    H2O = output_H2O_molfr / tot_molfr
    CO2 = output_CO2_molfr / tot_molfr
    N2 = 1 - O2 - H2O - CO2
    for idx in mdot_air.index:
        mixture[idx] = "HEOS::" + "N2[" + str(N2[idx]) + "]&" + "O2[" + str(O2[idx]) + "]&" + "H2O[" + str(H2O[idx]) + "]&" + "CO2[" + str(CO2[idx]) + "]"
    return mixture


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


def coolpropMixtureHelperFunction(composition):
    mixture = "HEOS::" + "N2[" + str(composition["N2"]) + "]&" + "O2[" + str(composition["O2"]) + "]&" + "H2O[" + str(composition["H2O"]) + "]&" + "CO2[" + str(composition) + "]"
    return mixture



