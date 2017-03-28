import numpy
import pdb

def general(): 
    # GENERAL CONSTANTS
    output = {}
    output["R_AIR"] = 8314.0 / 29 # Air gas constant
    output["K_AIR"] = 1.4   # Air specific heat ratio
    output["CP_AIR"] = 1.02   # Air specific heat, in [kJ/kgK] 
    output["CP_EG"] = 1.08   # EG specific heat, in [kJ/kgK] 
    output["CP_LO"] = 2.1   # Lubricating oil specific heat, in [kW/kgK]
    output["CP_W"] = 4.187   # Water specifi heat, in [kW/kgK] 
    output["RHO_W"] = 1000.0   # Water density, in [kg/m^3]
    output["RHO_LO"] = 850.0   # Lubricating oil density, in [kg/m^3]
    output["LHV_HFO"] = 41170.0   # Heavy Fuel Oil lower heating value, in [kJ/kg]
    output["HHV_HFO"] = output["LHV_HFO"] * (1.0406 + 0.0144 * 0.1185 / 0.8794 * 12)    # Calculated Higher heating value
    output["LHV_MDO"] = 42230.0 # Marine Diesel Oil lower heating value, in [kJ/kg]
    output["HHV_MDO"] = output["LHV_MDO"] * (1.0406 + 0.0144 * 0.1185 / 0.8794 * 12) * 1.01  # Calculated Higher heating value
    output["CP_HFO"] = 1.8   # Fuel specific heat, [kJ/kg]
    output["RHO_HFO"] = numpy.mean([890 , 919 , 924 , 926 , 925 , 921 , 924 , 918 , 920 , 919 , 933])  # HFO density, in [kg/m^3]
    output["AIR_STOIC"] = 14.7  # Stoichiometric ratio fuel/air for Diesel-type fuels
    output["ETA_VOL"] = 0.97 # Assumption about volumetric efficiency 
    return output

def steamProperties():
    ## STEAM PROPERTIES
    output = {}
    output["H_STEAM_LS"] = 662.0 # Specific enthalpy of 6 bar steam, saturated liquid, in [kJ/kg]
    output["H_STEAM_VS"] = 2754.0  # Specific enthalpy of 6 bar steam, saturated vapour, in [kJ/kg]
    output["S_STEAM_LS"] = 1.9108 # Specific entropy of 6 bar steam, saturated liquid , in [kJ/kg]
    output["S_STEAM_VS"] = 6.7766  # Specific entrpy of 6 bar steam, saturated vapour, in [kJ/kg]
    output["DH_STEAM"] = output["H_STEAM_VS"] - output["H_STEAM_LS"]  
    output["DS_STEAM"] = output["S_STEAM_VS"] - output["S_STEAM_LS"]
    output["TSAT_STEAM"] = 430.0 # Saturation temperature chosen for the selected pressure, in [kJ/kg] 
    return output
    
def mainEngines(CONSTANTS_GENERAL):
    output = {} # Initializing the output dictionary
    output["MCR"] = 5890   # Main engines maximum power, in [kW]
    output["RPM_DES"] = 500 # Main engine design speed, in [rpm] 
    output["MFR_FUEL_DES_ISO"] = 1165 / 3600 * 186.1 / 197.6   # Fuel flow at 100# load at ISO conditions, in [kg/s]
# output["POLY_FUEL_RACK_2_MFR_FUEL"] = polyfit([24 31 38 42 46]/46 , [336.3 587.8 836.6 953.1 1141]/3600 , 2)   # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
    output["POLY_FUEL_LOAD_2_BSFC_ISO"] = numpy.polyfit(numpy.array([336.3 , 587.8 , 836.6 , 953.1 , 1141])/1141 , numpy.array([216.9 , 187.1 , 178.5 , 179.2 , 181.4]) , 2)   # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
# output["POLY_RPM_2_POWER"] = polyfit([315 397 454 474 500 516] , [1463 2925 4388 4973 5890 6435] , 3)  
    output["POLY_RPM_2_ISO_BSFC"] = numpy.polyfit(numpy.array([315.0 , 397.0 , 454.0 , 474.0 , 500.0 , 516.0]) , numpy.array([numpy.mean([216.1 , 207.6 , 225.5 , 209.9]) , 188.2 , 179.7 , 181.6 , 185 , 191.1]) , 2)  
# output["POLY_PCA_2_LOAD"] = [0.25/0.24 , 0 , 0.2577 , 0.1438 , 0.5 , 0]  
    output["POLY_LOAD_2_ISO_BSFC"] = numpy.polyfit(numpy.array([0.25 , 0.5 , 0.75 , 0.85 , 1.0 , 1.1]) , numpy.array([numpy.mean([216.1 , 207.6 , 225.5 , 209.9]) , 188.2 , 179.7 , 181.6 , 185 , 191.1]) , 2)  
    output["QDOT_HT_DES"] = 1650.0 # Heat flow to the HT cooling systems at design load, in [kW]
    output["QDOT_LT_DES"] = 1450.0 # Heat flow to the HT cooling systems at design load, in [kW]
    output["POLY_LOAD_2_QDOT_HT"] = numpy.polyfit(numpy.array([0.5 , 0.75 , 0.85 , 1]) , numpy.array([500.0 , 1000.0 , 1250.0 , output["QDOT_HT_DES"]]) , 2)  
    output["POLY_LOAD_2_QDOT_LT"] = numpy.polyfit(numpy.array([0.5 , 0.75 , 0.85 , 1]) , numpy.array([800.0 , 1050.0 , 1200.0 , output["QDOT_LT_DES"]]) , 2)  
    output["POLY_LOAD_2_EPS_CACHT"] = numpy.polyfit(numpy.array([0.5 , 0.75 , 0.85 , 1]) , numpy.array([0.922 , 0.902 , 0.876 , 0.871]),1)  
# output["POLY_FUEL_RACK_2_MASS_FUEL_CYCLE"] = polyfit([0.233333 , 0.5 , 0.7 , 0.8 , 1],[0.01726 , 0.02435 , 0.03081 , 0.03397 , 0.03869],1)  
    output["BSFC_ISO_DES"] = numpy.polyval(output["POLY_LOAD_2_ISO_BSFC"],1)  
# Function handle that allows to calculate the fuel load
    output["BORE"] = 0.46   # Main engine bore
    output["STROKE"] = 0.58   # Main engine stroke
    output["N_CYL"] = 6   # Number of cylinders
    output["R_C"] = 14   # Assumption of compression ratio
    output["V_SW"] = output["BORE"]**2 / 4 * numpy.pi * output["STROKE"]   # Swept volume, in [m^3]
    output["V_MAX"] = output["V_SW"] * output["R_C"] / (output["R_C"] - 1)   # Maximum volume, in [m^3]
    output["MFR_LO"] = 120.0 * CONSTANTS_GENERAL["RHO_LO"] / 3600.0   # Mass flow rate of oil in each main engine, in [kg/s]
    output["MFR_LT"] = 120.0 * CONSTANTS_GENERAL["RHO_W"] / 3600.0   # Mass flow rate of LT cooling water, in [kg/s]
    output["MFR_HT"] = 120.0 * CONSTANTS_GENERAL["RHO_W"] / 3600.0   # Mass flow rate of LT cooling water, in [kg/s]
    output["POLY_PIN_2_ETA_IS"] = [-1.18e-2 , 8.74e-2 , 6.81e-1]   # Polynoimial regression for isentropic efficiency of the compressor
    output["ETA_CORR"] = 1.05  
    output["ETA_IS_TC_MAX"] = 0.85  
    output["ETA_IS_TC"] = 0.8  
    output["ETA_MECH_TC"] = 0.98   
    output["EPS_CAC_HTSTAGE"] = 0.85  
    output["ETA_GB"] = 0.985  
    output["ETA_SHAFT"] = 0.99 
    return output
    
    
def auxiliaryEngines(CONSTANTS_GENERAL,CONSTANTS_MAIN_ENGINE):
    output = {} # Initializing the output dictionary
    output["MCR"] = 2760.0  # Auxiliary engines maximum power, in [kW] ;
    output["RPM_DES"] = 750.0  # Auxiliary engines design speed, in [rpm] ;
# AE_POLY_FUEL_RACK_2_MFR_FUEL = polyfit([17 27 37 44.5 46]/46 , [336.3 587.8 836.6 953.1 1141]/3600 , 2) ; # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
    output["POLY_LOAD_2_ISO_BSFC"] = numpy.polyfit(numpy.array([0.5 , 0.75 , 1.0]) , numpy.array([191.0 , 184.0 , 183.0])/183.0*190.6 , 2)  # Fits a 2nd degree polynomial relating relative fuel rack position to fuel flow in kg/s
    output["POLY_PIN_2_ETA_IS"] = numpy.array([-1.18e-2 , 8.74e-2 , 6.81e-1]) 
    output["BORE"] = 0.32  # Main engine bore, in [m]
    output["STROKE"] = 0.40  # Main engine stroke, in [m]
    output["N_CYL"] = 6.0  # Number of cylinders
    output["V_SW"] = output["BORE"]**2 / 4.0 * numpy.pi * output["STROKE"]  # Swept volume, in [m^3]
    output["R_C"] = 14.0  # Assumption of compression ratio
    output["V_MAX"] = output["V_SW"] * output["R_C"] / (output["R_C"] - 1)  # Maximum volume, in [m^3]
    output["MFR_LO"] = 70 * CONSTANTS_GENERAL["RHO_LO"] / 3600 ; # Mass flow rate of oil in each auxiliary engine, in [kg/s]
    output["QDOT_2_CAC_HT_DES"] = 351.0  # Heat flow to the charge air cooler, High temperature stage,  at the engine design point, in [kW]
    output["QDOT_2_CAC_LT_DES"] = 433.0  # Heat flow to the charge air cooler, Low temperature stage,  at the engine design point, in [kW]
    output["QDOT_2_JWC_DES"] = 414.0  # Heat flow to the jacket water cooler at the engine design point, in [kW]
    output["QDOT_2_LOC_DES"] = 331.0  # Heat flow to the lubricating oil cooler at the engine design point, in [kW]
# Assuming that the amount of heat from the engine to the HT cooling systems behaves in the same way as that of the main engines.
    output["POLY_LOAD_2_QDOT_HT"] = CONSTANTS_MAIN_ENGINE["POLY_LOAD_2_QDOT_HT"] * (output["QDOT_2_CAC_HT_DES"] + output["QDOT_2_JWC_DES"]) / CONSTANTS_MAIN_ENGINE["QDOT_HT_DES"]
    output["POLY_LOAD_2_QDOT_LT"] = CONSTANTS_MAIN_ENGINE["POLY_LOAD_2_QDOT_LT"] * (output["QDOT_2_CAC_LT_DES"] + output["QDOT_2_LOC_DES"]) / CONSTANTS_MAIN_ENGINE["QDOT_LT_DES"]
# Assuming that the sare of the charge air cooling heat going to the HT stage is linearly increasing from 0 to its value at the engine design point.
    output["POLY_LOAD_2_SHARE_CAC"] = numpy.polyfit([0 , 1] , [0 , output["QDOT_2_CAC_HT_DES"]/(output["QDOT_2_CAC_HT_DES"]+output["QDOT_2_CAC_LT_DES"])] , 1)
    output["MFR_LT"] = 60.0 * CONSTANTS_GENERAL["RHO_W"] / 3600.0  # Mass flow rate of LT cooling water, in [kg/s]
    output["MFR_HT"] = 60.0 * CONSTANTS_GENERAL["RHO_W"] / 3600.0  # Mass flow rate of HT cooling water, in [kg/s]
    output["ETA_CORR"] = 1.15  # Used because one of the engines need correction, to be checked
    output["ETA_SG"] = 0.97 ;
    return output
    


def monthLimits (N_POINTS):
    # This function is used to store the limits of each month. This is useful whenever one wants to make inputs vary each month, etc. 
    # Months start from 01 February 2014 until 17 December 2014
    MONTH_LIMIT_IDX = [{"Name":"FEB", "Days":28} , {"Name":"MAR", "Days":31} , {"Name":"APR", "Days":30} , {"Name":"MAY", "Days":31} , {"Name":"JUN", "Days":30} , {"Name":"JUL", "Days":31} , {"Name":"AUG", "Days":31} , {"Name":"SEP", "Days":30} , {"Name":"OCT", "Days":31} , {"Name":"NOV", "Days":30} , {"Name":"DEC", "Days":(16 + 19/24)}] # Note that we only have data until 17 of December!
    # Here we calculate the index in the original dataset of the limit between each month. Hence, 
    idx = 0
    for element in MONTH_LIMIT_IDX:
        if idx == 0:
            MONTH_LIMIT_IDX[idx].update({"Limits": (0,MONTH_LIMIT_IDX[idx]["Days"] * 24 * 4 - 1)})  # The first month's starts at 0
        else:
            MONTH_LIMIT_IDX[idx].update({"Limits": (MONTH_LIMIT_IDX[idx-1]["Limits"][1]+1, MONTH_LIMIT_IDX[idx-1]["Limits"][1] + MONTH_LIMIT_IDX[idx]["Days"] * 24 * 4)})
        idx = idx + 1
    # MONTH_ID_LIMIT(length(MONTH_DAYS)) = MONTH_ID_LIMIT(length(MONTH_DAYS)) - 1 ;I am commenting this because it was in the original code, but I am not sure why it was there from the beginning :-)
    
    # We also want an object that, for each day of the year, gives us the first and last point in the dataset
    DAY_LIMIT_IDX = []
    idx1 = 0
    idx2 = 0
    day = 1
    month = "FEB"
    idx_month = 0 
    while idx1 < N_POINTS:
        DAY_LIMIT_IDX[idx2] = {}
        DAY_LIMIT_IDX[idx2]["Month"] = month
        DAY_LIMIT_IDX[idx2]["Day"] = day
        DAY_LIMIT_IDX[idx2]["indexes"] = (idx1,idx1+24*4-1)
        idx1 = idx1 + 24 * 4 # The next index will be 24*4 timesteps later
        idx2 = idx2 + 1
        if day+1 <= MONTH_LIMIT_IDX[idx_month]["Days"]:
            day = day + 1
        else:
            day = 1
            idx_month = idx_month + 1
            month = MONTH_LIMIT_IDX[idx_month]["Name"]
    output = [MONTH_LIMIT_IDX , DAY_LIMIT_IDX]
    return output

    

    
# NOTE: THIS SHOULD BE MOVED TO ANOTHER PYTHON FILE
def engineFuelFlowCalculation(fuel_rack_position,engine_speed,CONSTANTS):
    # This function is used to calculate the fuel flow of an engine given its fuel rack position and its rotating speed. 
    # Inputs are free, as long as the same unit is used for the fuel rack position and the engine speed in both the input and the "design" values in the "CONSTANTS" dictionary
    output = CONSTANTS["MFR_FUEL_DES"] * ( (CONSTANTS["POLY_FRP_2_MF"][0] + CONSTANTS["POLY_FRP_2_MF"][1] * fuel_rack_position) / (CONSTANTS["POLY_FRP_2_MF"][0] + CONSTANTS["POLY_FRP_2_MF"][1] * CONSTANTS["FRP_DES"])) * (engine_speed / CONSTANTS["RPM_DES"])
    return output
    