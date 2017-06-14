import numpy as np
import pandas as pd
from helpers import d2df
from helpers import piecewisePolyvalHelperFunction
from helpers import polyvalHelperFunction



def systemFill(processed, dict_structure, CONSTANTS):
    print("Started filling the gaps in the dataframe...")
    counter_mdot_tot = 0
    counter_p_tot = 0
    counter_T_tot = 0
    counter_c_tot = 0
    for system in dict_structure["systems"]:
        for unit in dict_structure["systems"][system]["units"]:
            # Check if the mass balance needs to be respected:
            for equation in dict_structure["systems"][system]["units"][unit]["equations"]:
                if equation == "MassBalance":
                    streams = dict_structure["systems"][system]["units"][unit]["streams"]
                    (counter_mdot,processed) = massFill(processed, dict_structure, CONSTANTS, system, unit, streams)
                    counter_mdot_tot = counter_mdot_tot + counter_mdot
                elif equation == "ConstantPressure":
                    (counter_p,processed) = constantProperty("p", processed, dict_structure, CONSTANTS, system, unit, streams)
                    counter_p_tot = counter_p_tot + counter_p
                elif equation == "ConstantTemperature":
                    (counter_T,processed) = constantProperty("T", processed, dict_structure, CONSTANTS, system, unit, streams)
                    counter_T_tot = counter_T_tot + counter_T
                else:
                    print("Equation not recognized")
                        # Trivial assignment: doing this if the flow is connected with other flows
            (counter_c,processed) = connectionAssignment(processed, dict_structure, CONSTANTS, system, unit)
            counter_c_tot = counter_c_tot + counter_c
    print("...done! Filled {} mdot values, {} p values, {} T values and assigned {} connections".format(counter_mdot_tot,counter_p_tot,counter_T_tot,counter_c_tot))
    return processed



def connectionAssignment(processed, dict_structure, CONSTANTS, system, unit):
    counter = 0
    for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
        if "Connections" in dict_structure["systems"][system]["units"][unit]["flows"][flow]:
            for connected_flow in dict_structure["systems"][system]["units"][unit]["flows"][flow]["Connections"]:
                for property in CONSTANTS["General"]["PROPERTY_LIST"][dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"]]:
                    ID = d2df(system,unit,flow,property)
                    ID_c = connected_flow + ":" + property
                    if processed[ID].isnull().sum() == 0:
                        if processed[ID_c].isnull().sum() != 0:
                            processed[ID_c] = processed[ID]
                            counter = counter + 1
                        elif not (processed[ID].equals(processed[ID_c])):
                            print("Something is wrong for {} {} {} {}".format(system,unit,flow,property))
    return (counter,processed)





def massFill(processed, dict_structure, CONSTANTS, system, unit, streams):
    # This function applies the mass balance over one component:
    # - If some of the flows have not been assigned yet, they are calculated based on the mass balance
    counter = 0
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
            balance = pd.Series()
            for flow in streams[stream]:
                if flow != idx_nan:
                    balance = balance + processed[flow+"mdot"] * (2 * float("out" not in flow) - 1)
            processed[streams[stream][idx_nan]] = balance.abs()
            counter = counter + 1
        else:
            # There are are more than 1 non defined fluid, I cannot calculate the mass balance
            pass
    return (counter,processed)




def constantProperty(property, processed, dict_structure, CONSTANTS, system, unit, streams):
    # This function assigns a constant pressure to all streams of the same type for units
    counter = 0
    for stream in streams:
        # If there is only one flow, something is tricky...
        # If there are only two flows associated to the stream, things are rather easy
        flow_nan = []
        for flow in streams[stream]:
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



def assumptions(raw, processed, CONSTANTS, hd):
    # This function includes generic assumed values in the main structure
    for system in CONSTANTS["General"]["NAMES"]["MainEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[d2df(system,"Comp","Air_in","p")][:] = CONSTANTS["General"]["P_ATM"]
    for system in CONSTANTS["General"]["NAMES"]["AuxEngines"]:
        # The pressure at the turbocharger inlet is equal to the atmospheric pressure
        processed[d2df(system, "Comp", "Air_in", "p")][:] = CONSTANTS["General"]["P_ATM"]
    processed["T_0"] = raw[hd["SEA_SW_T_"]] + 273.15
    processed[d2df("Other","SWC13","SeaWater_out","T")] = raw[hd["SWC13_SW_T_OUT"]]  # CHECK IF IT IS IN OR OUT
    processed[d2df("Other","SWC24","SeaWater_out","T")] = raw[hd["SWC24_SW_T_OUT"]]  # CHECK IF IT IS IN OR OUT
    return processed


def engineStatusCalculation(type, raw, processed, CONSTANTS, hd):
    for system in CONSTANTS["General"]["NAMES"][type]:
        processed[system+":"+"load"] = processed[d2df(system,"Cyl","Power_out","Wdot")] / CONSTANTS[type]["MCR"]
        # We consider that the engines are on if the RPM of the turbocharger is higher than 5000 RPM
        #status[system]["OnOff"] = (status[system]["Load"] > 0.05) & (processed[d2df(system,"Cyl"]["Power_out","omega"] > CONSTANTS["MainEngines"]["RPM_DES"] * 0.1)
        processed[system + ":" + "on"] = raw[hd[system+"-TC__RPM_"]] > 5000
    return processed


def engineCoolingSystemsCalculation(processed, CONSTANTS, engine_type):
    print("Started calculating analysis for {} cooling systems...".format(engine_type))
    # This function calculates the different flows related to the cooling systems of the main engines.
    for system in CONSTANTS["General"]["NAMES"][engine_type]:
        # Calculating the total energy flow going to the cooling systems, based on the energy balance on the engine
        energy_2_cooling = (processed[d2df(system,"Cyl","FuelCh_in","Wdot")] -
            processed[d2df(system,"Cyl","Power_out","Wdot")] +
            CONSTANTS["General"]["HFO"]["CP"] * processed[d2df(system,"Cyl","FuelPh_in","mdot")] *
                (processed[d2df(system,"Cyl","FuelPh_in","T")] - processed["T_0"]) -
            CONSTANTS["General"]["CP_EG"] * processed[d2df(system,"Turbine","Mix_out","mdot")] *
                (processed[d2df(system,"Turbine","Mix_out","T")] - processed["T_0"]) +
            CONSTANTS["General"]["CP_AIR"] * processed[d2df(system,"Comp","Air_in","mdot")] *
                (processed[d2df(system,"Comp","Air_in","T")] - processed["T_0"]))
        # Calculating the energy going to the charge air cooler, based on the estimated temperatures on the air line
        energy_2_cac = CONSTANTS["General"]["CP_AIR"] * processed[d2df(system,"Cyl","Air_in","mdot")] * (processed[d2df(system,"Comp","Air_out","T")] - processed[d2df(system,"Cyl","Air_in","T")])
        # Calculating the energy going to the HT cooling systems, based on interpolation from the project guide
        energy_2_ht_theoric = processed[system+":"+"load"].apply(piecewisePolyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_HT"],)) * CONSTANTS[engine_type]["QDOT_HT_DES"]
        energy_2_lt_theoric = processed[system+":"+"load"].apply(piecewisePolyvalHelperFunction,args=(CONSTANTS[engine_type]["POLY_LOAD_2_QDOT_LT"],)) * CONSTANTS[engine_type]["QDOT_LT_DES"]
        # The values calculated based on the project guide are reconciled based on the energy balance
        energy_2_ht = energy_2_cooling * energy_2_ht_theoric / (energy_2_ht_theoric + energy_2_lt_theoric)
        energy_2_lt = energy_2_cooling - energy_2_ht
        # The energy going to the CAC, HT stage is calculated assuming a 85% effectiveness of the heat exchanger
        energy_2_cac_ht = CONSTANTS[engine_type]["EPS_CAC_HTSTAGE"] * processed[d2df(system,"Comp","Air_in","mdot")] * CONSTANTS["General"]["CP_AIR"] * (
            processed[d2df(system,"Comp","Air_out","T")] - processed[d2df(system,"CAC_HT","HTWater_in","T")])
        # The energy going to the CAC, LT stage results as a consequence by thermal balance over the CAC
        energy_2_cac_lt = energy_2_cac - energy_2_cac_ht
        # The energy to the JWC results as a balance over the HT cooling systems
        energy_2_jwc = energy_2_ht - energy_2_cac_ht
        # The energy to the LOC results as a balance over the LT cooling systems
        energy_2_loc = energy_2_lt - energy_2_cac_lt
        # For all pumps, it is here assumed that the flow scales only with the speed of the engine (biiiiig assumption)
        processed[d2df(system,"LOC","LTWater_in","mdot")] = CONSTANTS[engine_type]["MFR_LT"] * processed[d2df(system,"Cyl","Power_out","omega")] / CONSTANTS[engine_type]["RPM_DES"]
        processed[d2df(system,"JWC","HTWater_in","mdot")] = CONSTANTS[engine_type]["MFR_HT"] * processed[d2df(system,"Cyl","Power_out","omega")] / CONSTANTS[engine_type]["RPM_DES"]
        # Finally, the temperatures in the flows are calculated based on the calculated energy and mass flow values
        # For LT, first we have the CAC, then the LOC
        processed[d2df(system,"CAC_LT","LTWater_out","T")] = processed[d2df(system,"CAC_LT","LTWater_in","T")] + energy_2_cac_lt / processed[d2df(system,"CAC_LT","LTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        processed[d2df(system,"LOC","LTWater_in","T")] = processed[d2df(system,"CAC_LT","LTWater_out","T")]
        processed[d2df(system,"LOC","LTWater_out","T")] = processed[d2df(system,"LOC","LTWater_in","T")] + energy_2_loc / processed[d2df(system,"LOC","LTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        # For HT, first we have the JWC, then the CAC, HT
        processed[d2df(system,"JWC","HTWater_out","T")] = processed[d2df(system,"JWC","HTWater_in","T")] + energy_2_jwc / processed[d2df(system,"JWC","HTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        processed[d2df(system,"CAC_HT","HTWater_in","T")] = processed[d2df(system,"JWC","HTWater_out","T")]
        processed[d2df(system,"CAC_HT","HTWater_out","T")] = processed[d2df(system,"CAC_HT","HTWater_in","T")] + energy_2_cac_ht / processed[d2df(system,"CAC_HT","HTWater_out","mdot")] / CONSTANTS["General"]["CP_WATER"]
        # For the LOC, we know the outlet (lower) temperature, we calculate the inlet temperature
        processed[d2df(system,"LOC","LubOil_out","mdot")][:] = CONSTANTS[engine_type]["MFR_LO"]
        processed[d2df(system,"LOC","LubOil_in","T")] = processed[d2df(system,"LOC","LubOil_out","T")] + energy_2_loc / processed[d2df(system,"LOC","LubOil_out","mdot")] / CONSTANTS["General"]["CP_LO"]
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






