from helpers import d2df
import numpy as np
import pandas as pd


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
    processed = unitOffCheck(processed, dict_structure, CONSTANTS, system_set, call_ID)
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
    processed = unitOffCheck(processed, dict_structure, CONSTANTS, system_set, call_ID)
    for system in system_set:
        for unit in dict_structure["systems"][system]["units"]:
            (counter_c,processed) = connectionAssignment(processed, dict_structure, CONSTANTS, system, unit, call_ID)
            counter_c_tot = counter_c_tot + counter_c
    print("...done! Filled {} mdot values, {} p values, {} T values and assigned {} connections".format(counter_mdot_tot,counter_p_tot,counter_T_tot,counter_c_tot))
    return processed



def unitOffCheck(processed, dict_structure, CONSTANTS, system_set, call_ID):
    # Assigns to 0 all values related to components when they are off
    for system in system_set:
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
    text_file = open(CONSTANTS["filenames"]["consistency_check_report"], "a")  # Opens the log file
    counter = 0
    for flow in dict_structure["systems"][system]["units"][unit]["flows"]:
        if "Connections" in dict_structure["systems"][system]["units"][unit]["flows"][flow]:
            for connected_flow in dict_structure["systems"][system]["units"][unit]["flows"][flow]["Connections"]:
                for property in CONSTANTS["General"]["PROPERTY_LIST"][dict_structure["systems"][system]["units"][unit]["flows"][flow]["type"]]:
                    ID = d2df(system,unit,flow,property)  # Writing the property full ID of the flow we are checking
                    ID_c = connected_flow + ":" + property  # Writing the property full ID of the flow connected to the flow we are checking
                    if processed[ID].isnull().sum() != len(processed[ID]):  # If the flow is not empty
                        if (processed[ID_c].isnull().sum() == len(processed[ID_c])) or (sum(processed[ID_c]) == 0):  # If the connected flow IS empty
                            processed[ID_c] = processed[ID]
                            counter = counter + 1
                        elif (processed[ID] - processed[ID_c]).sum() > processed[ID].max():
                            error = abs(processed[ID] - processed[ID_c])
                            relativeError = error / processed[ID].mean()
                            averageError = relativeError.mean()
                            timesOfError = sum(error > 0.01*processed[ID].mean())
                            text_file.write("ERROR. FUN: ppo.connectionAssignment. Something is wrong. Flows {} and {} should be the same, they are not. "
                                            "Average relative error is {}, total times of error is {}\n".format(ID, ID_c, str(averageError), str(timesOfError)))
    text_file.close()
    return (counter,processed)





def massFill(processed, dict_structure, CONSTANTS, system, unit, streams, call_ID):
    # This function applies the mass balance over one component:
    # - If some of the flows have not been assigned yet, they are calculated based on the mass balance
    counter = 0
    if system+":"+unit == "CoolingSystems:LTcollector13":
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