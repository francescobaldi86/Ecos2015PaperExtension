import numpy as np
import pandas as pd


def constantsSetting():
    output = {}
    output["General"] = general()  # loading dictionary with general, physical constants
    output["Steam"] = steamProperties()  # loading dictionary with steam properties constants
    output["MainEngines"] = mainEngines(output)  # loading dictionary with main-engine related constants
    output["AuxEngines"] = auxiliaryEngines(output)  # loading dictionary with auxiliary-engine related constants
    output["OtherUnits"] = otherUnits(output)
    return output


def general():
    # GENERAL CONSTANTS
    output = {}
    output["R_0"] = 8.3140 # Ideal gas constant, in [J/mol*K]
    output["R_AIR"] = output["R_0"] * 1000 / 29 # Air gas constant, in [J/kg*K]
    output["K_AIR"] = 1.4   # Air specific heat ratio
    output["CP_AIR"] = 1.015   # Air specific heat, in [kJ/kgK]
    output["CP_EG"] = 1.11   # EG specific heat, in [kJ/kgK]
    output["CP_LO"] = 2.1   # Lubricating oil specific heat, in [kW/kgK]
    output["CP_WATER"] = 4.187   # Water specifi heat, in [kW/kgK]
    output["RHO_W"] = 1000.0   # Water density, in [kg/m^3]
    output["RHO_LO"] = 850.0   # Lubricating oil density, in [kg/m^3]
    # output["RHO_HFO"] = np.mean([890, 919, 924, 926, 925, 921, 924, 918, 920, 919, 933])  # HFO density, in [kg/m^3]
    output["AIR_STOIC"] = 14.7  # Stoichiometric ratio fuel/air for Diesel-type fuels
    output["ETA_VOL"] = 0.97 # Assumption about volumetric efficiency
    output["P_ATM"] = 101325 # Assumption on atmospheric pressure
    output["T_STANDARD"] = 323 # Standard temperature, for the calculation of the exergy in the exhaust gas
    output["ISO"] = {"LHV": 42700, "T_CA": 298, "T_LT": 298, "ETA_MECH": 0.8} # Reference values for ISO conditions
    output["NAMES"] = {"MainEngines": {"ME1", "ME2", "ME3", "ME4"}, "AuxEngines": {"AE1", "AE2", "AE3", "AE4"}}
    output["PROPERTY_LIST"] = {}
    output["PROPERTY_LIST"]["CPF"] =  {"mdot", "T", "p", "h", "b", "Edot", "Bdot"} # Compressible physical flow
    output["PROPERTY_LIST"]["IPF"] =  {"mdot", "T", "h", "b", "Edot", "Bdot"} # Incompressible physical flow
    output["PROPERTY_LIST"]["SF"] = {"mdot", "h", "b", "Edot", "Bdot"}  # Incompressible physical flow
    output["PROPERTY_LIST"]["Qdot"] = {"T", "Edot", "Bdot"} # Heat flow
    output["PROPERTY_LIST"]["Wdot"] = {"omega", "Edot", "Bdot"} # Mechanical rotational energy flow
    output["PROPERTY_LIST"]["CEF"] = {"Edot", "Bdot"} # Chemical / Electrical energy flows
    output["PROPERTY_LIST"]["REF"] = {"Wdot": 0, "omega":0, "mdot":0, "T": 273, "p": output["P_ATM"], "h": 0, "b": 0, "Edot": 0, "Bdot": 0, "Qdot": 0}
    output["EFFICIENCY_LIST"] = {}
    output["EFFICIENCY_LIST"]["STANDARD"] = {"eta", "eps", "lambda", "delta"}
    output["EFFICIENCY_LIST"]["HEX"] = {"eps", "lambda", "delta"}
    output["EFFICIENCY_LIST"]["MIXMERGE"] = {"lambda", "delta"}
    output["UNIT_TYPES"] = {}
    output["UNIT_TYPES"]["STANDARD"] = {"cyl", "comp", "turbine", "ag", "boiler", "shaft"}
    output["UNIT_TYPES"]["MIXMERGE"] = {"merge", "split", "distribution", "collector", "valve"}
    # output["FLUIDS"] = {"BP": "Air", "Air": "Air", "Water": "Water"}
    output["MDO"] = {"LHV": 42230.0, "CP": 1.8, "C": 0.87, "H": 0.13}
    output["MDO"]["HHV"] = output["MDO"]["LHV"] * (1.0406 + 0.0144 * output["MDO"]["H"] / output["MDO"]["C"] * 12) * 1.01  # Calculated Higher heating value
    output["HFO"] = {"LHV": 40360.0, "CP": 1.8, "C": 0.89, "H": 0.11}
    output["HFO"]["HHV"] = output["HFO"]["LHV"] * (1.0406 + 0.0144 * output["HFO"]["H"] / output["HFO"]["C"] * 12) * 1.01  # Calculated Higher heating value
    output["NASA_POLY"] = {"N2":  [0.03298677E+02,  0.14082404E-02, -0.03963222E-04,  0.05641515E-07, -0.02444854E-10, -0.10208999E+04,  0.03950372E+02],
                 "O2":  [3.78245636E+00, -2.99673416E-03,  9.84730201E-06, -9.68129509E-09,  3.24372837E-12, -1.06394356E+03,  3.65767573E+00],
                 "CO2": [2.35677352E+00,  8.98459677E-03, -7.12356269E-06,  2.45919022E-09, -1.43699548E-13, -4.83719697E+04,  9.90105222E+00],
                 "H2O": [4.19864056E+00, -2.03643410E-03,  6.52040211E-06, -5.48797062E-09,  1.77197817E-12, -3.02937267E+04, -8.49032208E-01]}
    output["MOLAR_MASSES"] = {"N2": 28, "O2": 32, "CO2": 44, "H2O": 18}
    return output

def steamProperties():
    # STEAM PROPERTIES
    output = {}
    output["H_STEAM_LS"] = 662.0  # Specific enthalpy of 6 bar steam, saturated liquid, in [kJ/kg]
    output["H_STEAM_VS"] = 2754.0  # Specific enthalpy of 6 bar steam, saturated vapour, in [kJ/kg]
    output["S_STEAM_LS"] = 1.9108  # Specific entropy of 6 bar steam, saturated liquid, in [kJ/kg]
    output["S_STEAM_VS"] = 6.7766  # Specific entrpy of 6 bar steam, saturated vapour, in [kJ/kg]
    output["DH_STEAM"] = output["H_STEAM_VS"] - output["H_STEAM_LS"]  
    output["DS_STEAM"] = output["S_STEAM_VS"] - output["S_STEAM_LS"]
    output["TSAT_STEAM"] = 430.0  # Saturation temperature chosen for the selected pressure, in [kJ/kg]
    return output
    
def mainEngines(CONSTANTS):
    output = {"MCR": 5890}   # Main engines maximum power, in [kW]
    output["RPM_DES"] = 500  # Main engine design speed, in [rpm]
    output["MFR_FUEL_DES_ISO"] = 184 * output["MCR"] / 1000 / 3600 # Fuel flow at 100# load at ISO conditions, in [kg/s]. 184 is the ISO bsfc at 100% load (average for the 4 MEs)
# output["POLY_FUEL_RACK_2_MFR_FUEL"] = polyfit([24 31 38 42 46]/46, [336.3 587.8 836.6 953.1 1141]/3600, 2)   # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
    # Here we write all the required info for the fuel rack position to mass flow rate relation
    output["FRP_2_MFR"] = {}
    output["FRP_2_MFR"]["POLY"] = {"ME1": [-159.612, 24.23254], "ME2": [-159.612, 28.282788], "ME3": [-159.612, 28.282788], "ME4": [-159.612, 28.282788]}
    output["FRP_2_MFR"]["FRP_MIN"] = {"ME1": 18.0, "ME2": 16.6, "ME3": 17.5, "ME4": 16.4}
    output["FRP_2_MFR"]["FRP_MAX"] = {"ME1": 51, "ME2": 47, "ME3": 47, "ME4": 46}
    output["POLY_FUEL_LOAD_2_BSFC_ISO"] = np.polyfit(np.array([336.3, 587.8, 836.6, 953.1, 1141])/1141, [216.9, 187.1, 178.5, 179.2, 181.4], 2)   # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
# output["POLY_RPM_2_POWER"] = polyfit([315 397 454 474 500 516], [1463 2925 4388 4973 5890 6435], 3)  
    output["POLY_RPM_2_ISO_BSFC"] = np.polyfit([315.0, 397.0, 454.0, 474.0, 500.0, 516.0], [np.mean([216.1, 207.6, 225.5, 209.9]), 188.2, 179.7, 181.6, 185, 191.1], 2)
# output["POLY_PCA_2_LOAD"] = [0.25/0.24, 0, 0.2577, 0.1438, 0.5, 0]  
    output["POLY_LOAD_2_ISO_BSFC"] = np.polyfit([0.25, 0.5, 0.75, 0.85, 1.0, 1.1], [np.mean([216.1, 207.6, 225.5, 209.9]), 188.2, 179.7, 181.6, 185, 191.1], 2)
    output["QDOT_HT_DES"] = 1650.0  # Heat flow to the HT cooling systems at design load, in [kW]
    output["QDOT_LT_DES"] = 1450.0  # Heat flow to the HT cooling systems at design load, in [kW]
    # output["POLY_LOAD_2_QDOT_HT"] = [np.polyfit(np.array([0.5, 0.75, 0.85, 1]),
    #                                     np.array([500.0, 1000.0, 1250.0, output["QDOT_HT_DES"]]) / output["QDOT_HT_DES"], 2)]
    # output["POLY_LOAD_2_QDOT_LT"] = [np.polyfit(np.array([0.5, 0.75, 0.85, 1]),
    #                                     np.array([800.0, 1050.0, 1200.0, output["QDOT_LT_DES"]]) / output["QDOT_LT_DES"], 2)]
    # output["POLY_LOAD_2_QDOT_HT"].append(np.polyfit(np.array([0, 0.5]), np.array([0, np.polyval(output["POLY_LOAD_2_QDOT_HT"][0],0.5)]), 1))
    # output["POLY_LOAD_2_QDOT_LT"].append(np.polyfit(np.array([0, 0.5]), np.array([0, np.polyval(output["POLY_LOAD_2_QDOT_LT"][0], 0.5)]), 1))
    # output["POLY_LOAD_2_EPS_CACHT"] = np.polyfit(np.array([0.5, 0.75, 0.85, 1]),
    #                                                 np.array([0.922, 0.902, 0.876, 0.871]), 1)
    output["POLY_LOAD_2_QDOT_HT"] = np.array([0.7826 , 0.2204 , 0])
    output["POLY_LOAD_2_QDOT_LT"] = np.array([-0.1206 , 1.0978 , 0])
    output["POLY_H_2_QDOT"] = np.array([-3.65E-4, +3.17E-2, 2.85E1])
# output["POLY_FUEL_RACK_2_MASS_FUEL_CYCLE"] = polyfit([0.233333, 0.5, 0.7, 0.8, 1],[0.01726, 0.02435, 0.03081, 0.03397, 0.03869],1)  
    output["BSFC_ISO_DES"] = np.polyval(output["POLY_LOAD_2_ISO_BSFC"], 1)
# Function handle that allows to calculate the fuel load
    output["BORE"] = 0.46   # Main engine bore
    output["STROKE"] = 0.58   # Main engine stroke
    output["N_CYL"] = 6   # Number of cylinders
    output["R_C"] = 14   # Assumption of compression ratio
    output["V_SW"] = output["BORE"]**2 / 4 * np.pi * output["STROKE"]   # Swept volume, in [m^3]
    output["V_MAX"] = output["V_SW"] * output["R_C"] / (output["R_C"] - 1)   # Maximum volume, in [m^3]
    output["MFR_LO"] = 120.0 * CONSTANTS["General"]["RHO_LO"] / 3600.0   # Mass flow rate of oil in each main engine, in [kg/s]
    output["MFR_LT"] = 120.0 * CONSTANTS["General"]["RHO_W"] / 3600.0   # Mass flow rate of LT cooling water, in [kg/s]
    output["MFR_HT"] = 120.0 * CONSTANTS["General"]["RHO_W"] / 3600.0   # Mass flow rate of LT cooling water, in [kg/s]
    output["POLY_PIN_2_ETA_IS"] = [-1.18e-2, 8.74e-2, 6.81e-1] # Polynoimial regression for isentropic efficiency of the compressor
    output["ETA_CORR"] = 1.05
    output["ETA_MECH_TC"] = 0.9   # Mechanical efficiency of the turbocharger [-]. Variations from "Development and validation of a new turbocharger simulation methodology for marine two stroke diesel engine modelling and diagnostic applications"
    output["POLY_TC_RPM_2_ETA_MECH"] = np.polyfit([6000, 9500, 13000, 16500, 20000], [0.7 , 0.76 , 0.84 , 0.91 , 0.91], 2)
    output["EPS_CAC_HTSTAGE"] = 0.85  # Effectiveness, as defined by the epsNTU method, of the High Temperature stage of the Charge Air Cooler, in [-]
    output["ETA_GB"] = 0.985   # Mechanical efficiency of the gearbox
    output["ETA_SHAFT"] = 0.99  # Mechanical efficiency of the engine shaft
    output["FRP_DES"] = {"ME1": 51, "ME2": 47, "ME3": 47, "ME4": 46}  # Value of the fuel rack position at 100% load
    # output["BYPASS_FLOW"] = 1.1
    output["STATIC_HEAD"] = 19
    output["T_COOLING_MIX"] = 71 + 273.15  # Temperature of the LT/HT mix before the mixing with the HT cooling systems
    return output
    
    
def auxiliaryEngines(CONSTANTS):
    output = {"MCR": 2760.0}  # Auxiliary engines maximum power, in [kW]
    output["RPM_DES"] = 750.0  # Auxiliary engines design speed, in [rpm]
# AE_POLY_FUEL_RACK_2_MFR_FUEL = polyfit([17 27 37 44.5 46]/46, [336.3 587.8 836.6 953.1 1141]/3600, 2) # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
    output["POLY_LOAD_2_ISO_BSFC"] = np.polyfit(np.array([0.5, 0.75, 0.85, 1.0]), np.array([193.0, 182.0, 181.0, 184.0])/184.0*190.0, 2)  # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
    output["POLY_PIN_2_ETA_IS"] = np.array([-1.18e-2, 8.74e-2, 6.81e-1]) 
    output["BORE"] = 0.32  # Main engine bore, in [m]
    output["STROKE"] = 0.40  # Main engine stroke, in [m]
    output["N_CYL"] = 6.0  # Number of cylinders
    output["V_SW"] = output["BORE"]**2 / 4.0 * np.pi * output["STROKE"]  # Swept volume, in [m^3]
    output["R_C"] = 14.0  # Assumption of compression ratio
    output["V_MAX"] = output["V_SW"] * output["R_C"] / (output["R_C"] - 1)  # Maximum volume, in [m^3]
    output["MFR_LO"] = 70 * CONSTANTS["General"]["RHO_LO"] / 3600 # Mass flow rate of oil in each auxiliary engine, in [kg/s]
    output["QDOT_2_CAC_HT_DES"] = 351.0  # Heat flow to the charge air cooler, High temperature stage,  at the engine design point, in [kW]
    output["QDOT_2_CAC_LT_DES"] = 433.0  # Heat flow to the charge air cooler, Low temperature stage,  at the engine design point, in [kW]
    output["QDOT_2_JWC_DES"] = 414.0  # Heat flow to the jacket water cooler at the engine design point, in [kW]
    output["QDOT_2_LOC_DES"] = 331.0  # Heat flow to the lubricating oil cooler at the engine design point, in [kW]
    output["QDOT_HT_DES"] = output["QDOT_2_CAC_HT_DES"] + output["QDOT_2_JWC_DES"]
    output["QDOT_LT_DES"] = output["QDOT_2_CAC_LT_DES"] + output["QDOT_2_LOC_DES"]
# Assuming that the amount of heat from the engine to the HT cooling systems behaves in the same way as that of the main engines.
    output["POLY_LOAD_2_QDOT_HT"] = CONSTANTS["MainEngines"]["POLY_LOAD_2_QDOT_HT"]
    output["POLY_LOAD_2_QDOT_LT"] = CONSTANTS["MainEngines"]["POLY_LOAD_2_QDOT_LT"]
    output["POLY_H_2_QDOT"] = np.array([-1.74E-3, -1.36E-2, 3.48E1])
# Assuming that the sare of the charge air cooling heat going to the HT stage is linearly increasing from 0 to its value at the engine design point.
    output["POLY_LOAD_2_SHARE_CAC"] = np.polyfit([0, 1], [0, output["QDOT_2_CAC_HT_DES"]/(output["QDOT_2_CAC_HT_DES"]+output["QDOT_2_CAC_LT_DES"])], 1)
    output["MFR_LT"] = 60.0 * CONSTANTS["General"]["RHO_W"] / 3600.0  # Mass flow rate of LT cooling water, in [kg/s]
    output["MFR_HT"] = 60.0 * CONSTANTS["General"]["RHO_W"] / 3600.0  # Mass flow rate of HT cooling water, in [kg/s]
    output["ETA_CORR"] = 1.15  # Used because one of the engines need correction, to be checked
    # The efficiency is calculated at eta = eta_des - A exp(-k (x-x_ref)/x_ref)
    output["AG"] = {}
    output["AG"]["ETA_DES"] = 0.97
    output["AG"]["A"] = 0.18
    output["AG"]["k"] = 5
    output["EPS_CAC_HTSTAGE"] = 0.85  # Effectiveness, as defined by the epsNTU method, of the High Temperature stage of the Charge Air Cooler, in [-]
    # output["STATIC_HEAD"] = 15     # Now it is calculated instead
    output["T_COOLING_MIX"] = 71 + 273.15  # Temperature of the LT/HT mix before the mixing with the HT cooling systems
    return output




def otherUnits(CONSTANTS):
    output = {}  # Initializing the output dictionary
    output["BOILER"] = {}  # Initializing the boiler sub-dictionary
    output["BOILER"]["ETA_DES"] = 0.9
    output["BOILER"]["ETA_REGR_X"] = [6.79E-02, 1.20E-01, 1.62E-01, 2.12E-01, 2.86E-01, 3.52E-01, 4.03E-01, 4.41E-01, 4.90E-01, 5.40E-01, 5.89E-01, 6.54E-01, 7.16E-01, 7.67E-01, 8.31E-01, 8.94E-01, 9.47E-01, 9.89E-01, 1.04E+00, 1.09E+00, 1.14E+00, 1.20E+00]
    output["BOILER"]["ETA_REGR_Y"] = [0.8787, 0.8830, 0.8864, 0.8889, 0.8910, 0.8897, 0.8870, 0.8842, 0.8810, 0.8777, 0.8740, 0.8692, 0.86486, 0.8613, 0.8570, 0.8528, 0.8491, 0.8462, 0.8427, 0.8390, 0.8356, 0.8317]
    output["BOILER"]["OXYGEN_EG"] = 0.04
    # Here we calculate the air/fuel ratio of the boiler, given the concentration of oxygen in the exhaust
    output["BOILER"]["LAMBDA"] = (CONSTANTS["General"]["MDO"]["C"] / 12 + CONSTANTS["General"]["MDO"]["H"] / 4 * (1 + output["BOILER"]["OXYGEN_EG"])
                                  ) / (1 - 100/21 * output["BOILER"]["OXYGEN_EG"]) * (32 + 100 / 21 * 28)
    for idx in range(len(output["BOILER"]["ETA_REGR_Y"])):
        output["BOILER"]["ETA_REGR_Y"][idx] = output["BOILER"]["ETA_REGR_Y"][idx] / max(output["BOILER"]["ETA_REGR_Y"])
    output["PROPULSION"] = {}
    output["PROPULSION"]["ETA_GB"] = 0.98
    output["PROPULSION"]["ETA_SH"] = 0.99
    output["HEAT_DEMAND"] = {}
    output["HEAT_DEMAND"]["HOT_WATER_HEATER"] = 1200
    output["HEAT_DEMAND"]["HVAC_PREHEATER"] = 3500
    output["HEAT_DEMAND"]["HVAC_REHEATER"] = 1780
    output["HEAT_DEMAND"]["TANK_HEATING"] = 210
    output["HEAT_DEMAND"]["OTHER_TANKS"] = 140
    output["HEAT_DEMAND"]["HFO_TANK_HEATING"] = 270
    output["HEAT_DEMAND"]["MACHINERY_SPACE_HEATERS"] = 280
    output["HEAT_DEMAND"]["GALLEY"] = 600
    output["HEAT_DEMAND"]["HWH_HOURLY"] = [0.10, 0.10, 0.10, 0.10, 0.70, 1.00, 1.00, 1.00, 0.50, 0.50, 0.50, 0.50,
                                           0.50, 0.50, 0.50, 0.50, 0.70, 0.70, 1.00, 1.00, 1.00, 0.50, 0.50, 0.30]
    output["HEAT_DEMAND"]["GALLEY_HOURLY"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 0.5, 1.0,
                                              1.0, 0.5, 0.1, 0.1, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 0.1, 0.1]
    output["HEAT_DEMAND"]["T_INSIDE"] = 22 + 273.15
    output["HEAT_DEMAND"]["WINTER_START"] = np.datetime64("2013-12-03")
    output["HEAT_DEMAND"]["WINTER_END"] = np.datetime64("2014-04-14")
    output["HEAT_DEMAND"]["SPRING_START"] = np.datetime64("2014-04-15")
    output["HEAT_DEMAND"]["SPRING_END"] = np.datetime64("2014-07-02")
    output["HEAT_DEMAND"]["SUMMER_START"] = np.datetime64("2014-07-03")
    output["HEAT_DEMAND"]["SUMMER_END"] = np.datetime64("2014-08-21")
    output["HEAT_DEMAND"]["AUTUMN_START"] = np.datetime64("2014-08-22")
    output["HEAT_DEMAND"]["AUTUMN_END"] = np.datetime64("2014-12-02")
    output["HEAT_DEMAND"]["TOTAL_AREA"] = (150 + 30) * 2 * 20 + 2 * 150 * 30
    output["HEAT_DEMAND"]["T_AIR_REF_MIN"]  = -20 + 273
    output["HEAT_DEMAND"]["T_AIR_REF_MAX"] = 15 + 273
    output["HEAT_DEMAND"]["TOTAL_U"] = output["HEAT_DEMAND"]["HVAC_PREHEATER"] / output["HEAT_DEMAND"]["TOTAL_AREA"] / (output["HEAT_DEMAND"]["T_INSIDE"] - output["HEAT_DEMAND"]["T_AIR_REF_MIN"])
    output["HEAT_DEMAND"]["HTHR_EPS"] = 0.85  # Effectiveness of the HTHR water-water heat exchangers
    return output
    


def seasons(dataset_raw, processed, CONSTANTS):
    # This function is used to define some time-related features, such as the season, the weekends, etc.
    # Definition of the weekend: all data points are 1 if it's weekend, 0 if it is a weekday.
    temp = pd.Series(index = processed.index)
    temp[processed.index.dayofweek == 4] = 1  # Fridays
    temp[processed.index.dayofweek == 5] = 1  # Saturdays
    temp[processed.index.dayofweek == 6] = 1  # Sundays
    temp[temp.isnull()] = 0  # All other weekdays
    temp = temp.shift(16*4-1)  # Shifting to account for the fact that passengers are going on and off at 16
    temp[temp.isnull()] = 0
    processed["Weekends"] = temp

    # Definition of the seasons based on energy demand
    # 0 = winter, 1 = spring/fall, 2 = summer
    temp = pd.Series(index=processed.index)
    temp[CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["WINTER_START"]:CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["WINTER_END"]] = 0
    temp[CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SPRING_START"]:CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SPRING_END"]] = 1
    temp[CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SUMMER_START"]:CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["SUMMER_END"]] = 2
    temp[CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["AUTUMN_START"]:CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["AUTUMN_END"]] = 1
    processed["Seasons"] = temp

    # Definition of the summer based on the number of passengers
    temp = pd.Series(index=processed.index)
    temp["2014-06-21":"2014-08-17"] = 1
    temp[temp.isnull()] = 0
    passenger_summer = temp

    # Definition of the number of passengers
    N_passengers_summer = dataset_raw["Passengers"][passenger_summer==1].mean()
    temp = pd.Series(index=processed.index)
    temp = processed["Weekends"].copy()
    temp[passenger_summer==1] = 0
    N_passengers_weekend = dataset_raw["Passengers"][temp == 1].mean()
    N_passengers_weekday = dataset_raw["Passengers"][(temp == 0) & (passenger_summer == 0)].mean()
    temp[processed["Weekends"]==1] = N_passengers_weekend
    temp[processed["Weekends"] == 0] = N_passengers_weekday
    temp[passenger_summer==1] = N_passengers_summer
    processed["Passengers_calc"] = temp



    return processed