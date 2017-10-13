import numpy as np
import pandas as pd
from helpers import d2df
from helpers import polyvalHelperFunction
import CoolProp.CoolProp as cp


def operationalModeCalculator(processed, raw, CONSTANTS, hd):
    # Initializing the data series
    temp = pd.Series(index=processed.index)
    temp[raw[hd["SHIP_SPEED_KNOT_"]] > 15] = "High Speed Sailing"
    temp[(raw[hd["SHIP_SPEED_KNOT_"]] < 15) * (raw[hd["SHIP_SPEED_KNOT_"]] > 4)] = "Low Speed Sailing"
    temp[((processed["Demands:Electricity:Thrusters:Edot"] > 0) + ((raw[hd["SHIP_SPEED_KNOT_"]] < 4) * (raw[hd["SHIP_SPEED_KNOT_"]] > 2)))] = "Maneuvering"
    temp[temp.isnull()] = "Port/Stay"
    processed["operationalMode"] = temp
    return processed


def engineStatusCalculation(type, raw, processed, CONSTANTS, hd, dict_structure):
    for system in CONSTANTS["General"]["NAMES"][type]:
        processed[system + ":" + "on"] = raw[hd[system+"-TC__RPM_"]] > 5000
        for unit in dict_structure["systems"][system]["units"]:
            processed[system + ":" + unit + ":on"] = processed[system + ":" + "on"]
    return processed



def engineLoadCalculation(type, raw, processed, CONSTANTS, hd):
    for system in CONSTANTS["General"]["NAMES"][type]:
        processed[system+":"+"load"] = processed[d2df(system,"Cyl","Power_out","Edot")] / CONSTANTS[type]["MCR"]
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


def mixtureComposition(mdot_eg,mdot_fuel,temp_fuel,CONSTANTS):
    # This value takes as input the flow of air and fuel and calculates the resulting composition of the exhaust gas, assuming full combustion
    # The composition is written in the code accepted by CoolProp, i.e. in the form:
    # "HEOS::COMP_1[%]&COMP_2[%]..."
    # Accepted components are: N2, O2, CO2, H2O (SO2?)
    # The composition is a dataframe of 4 columns, in the order above
    mdot_air = mdot_eg - mdot_fuel
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

def mixtureCompositionNew(mdot_tot,mdot_fuel,temp_fuel,CONSTANTS):
    # This value takes as input the flow of air and fuel and calculates the resulting composition of the exhaust gas, assuming full combustion
    # The composition is written in the code accepted by CoolProp, i.e. in the form:
    # "HEOS::COMP_1[%]&COMP_2[%]..."
    # Accepted components are: N2, O2, CO2, H2O (SO2?)
    # The composition is a dataframe of 4 columns, in the order above
    mdot_air = mdot_tot - mdot_fuel
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
    mixture = {"N2": N2, "O2": O2, "CO2": CO2, "H2O": H2O}
    return mixture




