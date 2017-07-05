import numpy as np
import pandas as pd
from helpers import d2df
from helpers import polyvalHelperFunction
import CoolProp.CoolProp as cp



def assumptions(raw, processed, CONSTANTS, hd):
    # This function includes generic assumed values in the main structure
    # ALL ENGINES
    for system in {"ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4"}:
        # The pressure at the turbocharger air inlet and exhaust outlet is equal to the atmospheric pressure
        processed.loc[:,d2df(system,"Comp","Air_in","p")] = CONSTANTS["General"]["P_ATM"]
        processed.loc[:,d2df(system, "Turbine", "Mix_out", "p")] = CONSTANTS["General"]["P_ATM"]
        # Temperature in the engine room, i.e. inlet to the compressor of the TC
        processed[d2df(system, "Comp", "Air_in", "T")] = raw[hd["ER_AIR_T_"]] + 273.15
        # Assuming that the pressure in the exhaust gas is 90% of the pressure in the inlet manifold. Somewhat reasonable
        processed[d2df(system, "Cyl", "EG_out", "p")] = (0.9 * raw[hd[system + "-CAC_AIR_P_OUT"]] + 1.01325) * 100000
        # Assuming the pressure of the fuel to be around 9 barg, based on measurements from ME4
        processed.loc[:,d2df(system, "Cyl", "FuelPh_in", "p")] = (9 + 1.01325) * 10e5
        # Assuming the temperature of the cylinder wall to be 150 degC
        processed.loc[:,d2df(system, "Cyl", "QdotJW_out", "T")] = 150 + 273.15
        processed.loc[:,d2df(system, "JWC", "QdotJW_in", "T")] = 150 + 273.15
        # Assuming a temperature of 100 degC for heat losses from the TC shaft
        processed.loc[:,d2df(system, "TCshaft", "Losses_out", "T")] = 100 + 273.15
        # Assuming the steam pressure and temperature in the HRSG to be constant...
        hrsg_pressure_assumption = (6 + 1.01325) * 100000
        #if system in {"AE1", "AE2", "AE3", "AE4", "ME2", "ME3"}:
        #    processed[d2df(system, "HRSG", "Steam_in", "T")][:] = cp.PropsSI('T', 'P', hrsg_pressure_assumption, 'Q', 0.5, "Water")
        #    processed[d2df(system, "HRSG", "Steam_in", "p")][:] = hrsg_pressure_assumption
        #    processed[d2df(system, "HRSG", "Steam_out", "T")] = processed[d2df(system, "HRSG", "Steam_in", "T")]
        #    processed[d2df(system, "HRSG", "Steam_out", "p")] = processed[d2df(system, "HRSG", "Steam_in", "p")]
        if system in {"AE1", "AE2", "AE3", "AE4"}:
            processed.loc[:,d2df(system, "AG", "Losses_out", "T")] = 100 + 273.15
            processed.loc[:,d2df(system, "Cyl", "Power_out", "omega")] = 750
    # Others
    processed.loc[:,"T_0"] = raw[hd["water_T_forsmark_smhi-opendata"]] + 273.15
    processed.loc[:,"T_air"] = raw[hd["air_T_sv_hogarna_smhi-opendata"]] + 273.15
    processed[d2df("CoolingSystems","SWC13","SeaWater_out","T")] = raw[hd["SWC13_SW_T_OUT"]]  # CHECK IF IT IS IN OR OUT
    processed[d2df("CoolingSystems","SWC24","SeaWater_out","T")] = raw[hd["SWC24_SW_T_OUT"]]  # CHECK IF IT IS IN OR OUT
    processed.loc[:,"CoolingSystems:LTHTmixer:HTWater_out:T"] = CONSTANTS["MainEngines"]["T_COOLING_MIX"]
    # HTHR system
    processed.loc[:,"HTHR:SteamHeater:HRWater_out:T"] = 90 + 273.15 # From the heat balance, the temperature needs to rise at 90 degrees
    processed.loc[:,"HTHR:SteamHeater:HRWater_out:mdot"] = 298 / 3600 * CONSTANTS["General"]["RHO_W"] # the original value is in m3/h
    processed.loc[:, "HTHR:HVACpreheater:Qdot_out:T"] = (50 - 23) / np.log((50+273.15)/(23+273.15))
    processed.loc[:, "HTHR:HVACreheater:Qdot_out:T"] = (80 - 60) / np.log((80 + 273.15) / (60 + 273.15))
    processed.loc[:, "HTHR:HotWaterHeater:Qdot_out:T"] = 70 + 273.15
    processed.loc[:, "Steam:TankHeating:Qdot_out:T"] = 60 + 273.15
    processed.loc[:, "Steam:MachinerySpaceHeaters:Qdot_out:T"] = processed["HTHR:HVACpreheater:Qdot_out:T"]
    processed.loc[:, "Steam:Galley:Qdot_out:T"] = 90 + 273.15
    processed.loc[:, "Steam:OtherTanks:Qdot_out:T"] = 60 + 273.15
    processed.loc[:, "Steam:HFOtankHeating:Qdot_out:T"] = 75 + 273.15 # some sort of average value...
    processed.loc[:, "Steam:HFOheater:Qdot_out:T"] = (110 - 75) / np.log((110 + 273.15) / (75 + 273.15))
    return processed








def systemFill(processed, dict_structure, CONSTANTS, system_type, call_ID):
    print("Started filling the gaps in the dataframe...", end="", flush=True)
    if system_type == "MainEngines":
        system_set = {"ME1", "ME2", "ME3", "ME4"}
    elif system_type == "AuxEngines":
        system_set = {"AE1", "AE2", "AE3", "AE4"}
    elif system_type == "Other":
        system_set = {"CoolingSystems", "Steam", "HTHR"}
    elif system_type == "Demands":
        system_set = {"Demands"}
    else:
        print("Error in the definition of the system type. Only MainEngines, AuxEngines and Other are accepter. Given {}".format(system_type))
    counter_mdot_tot = 0
    counter_p_tot = 0
    counter_T_tot = 0
    counter_c_tot = 0
    processed = unitOffCheck(processed, dict_structure, CONSTANTS, call_ID)
    for system in system_set:
        for unit in dict_structure["systems"][system]["units"]:
            # (counter_c, processed) = connectionAssignment(processed, dict_structure, CONSTANTS, system, unit, call_ID)
            for equation in dict_structure["systems"][system]["units"][unit]["equations"]:
                streams = dict_structure["systems"][system]["units"][unit]["streams"]
                if equation == "MassBalance":
                    (counter_mdot,processed) = massFill(processed, dict_structure, CONSTANTS, system, unit, streams, call_ID)
                    counter_mdot_tot = counter_mdot_tot + counter_mdot
                elif equation == "ConstantPressure":
                    (counter_p,processed) = constantProperty("p", processed, dict_structure, CONSTANTS, system, unit, streams, call_ID)
                    counter_p_tot = counter_p_tot + counter_p
                elif equation == "ConstantTemperature":
                    (counter_T,processed) = constantProperty("T", processed, dict_structure, CONSTANTS, system, unit, streams, call_ID)
                    counter_T_tot = counter_T_tot + counter_T
                else:
                    print("Equation not recognized")
                        # Trivial assignment: doing this if the flow is connected with other flows
    processed = unitOffCheck(processed, dict_structure, CONSTANTS, call_ID)
    for system in system_set:
        for unit in dict_structure["systems"][system]["units"]:
            (counter_c,processed) = connectionAssignment(processed, dict_structure, CONSTANTS, system, unit, call_ID)
            counter_c_tot = counter_c_tot + counter_c
    print("...done! Filled {} mdot values, {} p values, {} T values and assigned {} connections".format(counter_mdot_tot,counter_p_tot,counter_T_tot,counter_c_tot))
    return processed



def unitOffCheck(processed, dict_structure, CONSTANTS, call_ID):
    # Assigns to 0 all values related to components when they are off
    for system in dict_structure["systems"]:
        if processed[system + ":" + "on"].isnull().sum() == 0:
            for unit in dict_structure["systems"][system]["units"]:
                for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
                    try:
                        for property in dict_structure["systems"][system]["units"][unit]["flows"][flow]["properties"]:
                            if processed[d2df(system,unit,flow,property)].isnull().sum() == len(processed[d2df(system,unit,flow,property)]):
                                pass # the value is still untouched, better leave it that way
                            elif property == "T":
                                processed.loc[~processed[system + ":" + "on"], d2df(system, unit, flow, property)] = processed.loc[~processed[system+":"+"on"], "T_0"]
                            else:
                                processed.loc[~processed[system + ":" + "on"], d2df(system, unit, flow, property)] = CONSTANTS["General"]["PROPERTY_LIST"]["REF"][property]
                    except KeyError:
                        print("Something went wrong when checking the engine on/off")
        elif processed[system + ":" + "on"].isnull().sum() < len(processed[system + ":" + "on"]):
            print("Something went wrong here, the system -on- field has NaNs for system {}".format(system))
        else:
            pass
    return processed



def connectionAssignment(processed, dict_structure, CONSTANTS, system, unit, call_ID):
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")
    counter = 0
    for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
        if system+":"+unit+":"+flow == "CoolingSystems:HTcollector13:HTWater_out":
            a = 0
        if "Connections" in dict_structure["systems"][system]["units"][unit]["flows"][flow]:
            for connected_flow in dict_structure["systems"][system]["units"][unit]["flows"][flow]["Connections"]:
                for property in CONSTANTS["General"]["PROPERTY_LIST"][dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"]]:
                    ID = d2df(system,unit,flow,property)
                    ID_c = connected_flow + ":" + property
                    if processed[ID].isnull().sum() != len(processed[ID]):
                        if (processed[ID_c].isnull().sum() == len(processed[ID_c])) or (sum(processed[ID_c]) == 0):
                            processed[ID_c] = processed[ID]
                            counter = counter + 1
                        elif (processed[ID] - processed[ID_c]).sum() > processed[ID].max():
                            text_file.write("ERROR. FUN: ppo.connectionAssignment. Something is wrong. Flows {} and {} should be the same, they are not. \n".format(ID, ID_c))
    text_file.close()
    return (counter,processed)





def massFill(processed, dict_structure, CONSTANTS, system, unit, streams, call_ID):
    # This function applies the mass balance over one component:
    # - If some of the flows have not been assigned yet, they are calculated based on the mass balance
    counter = 0
    if system+":"+unit == "ME1:HTmerge":
        aaa = 0
    for stream in streams:
        # If there is only one flow, something is tricky...
        # If there are only two flows associated to the stream, things are rather easy
        flow_nan = []
        for flow in streams[stream]:
            flow_nan.append(processed[flow+"mdot"].isnull().sum() == len(processed[flow+"mdot"]))
        if sum(flow_nan) == 0:
            # All flows have a value, just do nothing
            pass
        elif sum(flow_nan) == 1:
            idx_nan = flow_nan.index(1)
            balance = pd.Series(index=processed.index)
            balance[:] = 0
            for flow in streams[stream]:
                if flow != streams[stream][idx_nan]:
                    balance = balance + processed[flow+"mdot"] * (2 * float("out" not in flow) - 1)
            processed[streams[stream][idx_nan]+"mdot"] = balance.abs()
            counter = counter + 1
        else:
            # There are are more than 1 non defined fluid, I cannot calculate the mass balance
            pass
    return (counter,processed)




def constantProperty(property, processed, dict_structure, CONSTANTS, system, unit, streams, call_ID):
    # This function assigns a constant pressure/temperature/massflow to all streams of the same type for units
    counter = 0
    if system + ":" + unit + ":" + property == "ME4:HTsplit:T":
        a = 0
    for stream in streams:
        # First, we check that the pressure is defined for this flow

        flow_nan = []
        for flow in streams[stream]:
            # If the property is not defined for one of the flows, then we simply skip the whole stream for that property
            if flow+property not in processed.keys():
                flow_nan = [0 , 0]
                break
            else:
                # Otherwise, we check whether it is full of NaNs or not.
                flow_nan.append(processed[flow+property].isnull().sum() == len(processed[flow+property]))
        if sum(flow_nan) == 0:
            # All flows have a value, just do nothing
            pass
        elif sum(flow_nan) < len(flow_nan):
            idx_non_nan = flow_nan.index(0)
            for flow in streams[stream]:
                if flow_nan[streams[stream].index(flow)] == 1:
                    processed[flow+property] = processed[streams[stream][idx_non_nan]+property]
                    counter = counter + 1
        else:
            # All fluids are NaN, so there is nothing to be done here
            pass
    return (counter,processed)






def engineStatusCalculation(type, raw, processed, CONSTANTS, hd):
    for system in CONSTANTS["General"]["NAMES"][type]:
        processed[system + ":" + "on"] = raw[hd[system+"-TC__RPM_"]] > 5000
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


def mixtureComposition(mdot_air,mdot_fuel,temp_fuel,CONSTANTS):
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




