import numpy as np
import pandas as pd


def heatDemand(processed, CONSTANTS):
    # This function calculates the heat demand from the on board systems
    db_index = processed.index
    processed[""] = CONSTANTS["Other"]["HEAT_DEMAND"]["HOT_WATER_HEATER"] * pd.Series(len(processed)/96*np.repeat(CONSTANTS["Other"]["HEAT_DEMAND"]["HWH_HOURLY"],4), index=db_index)
    qdot_hvac_preheater = CONSTANTS["Other"]["HEAT_DEMAND"]["HVAC_PREHEATER"] * (CONSTANTS["Other"]["HEAT_DEMAND"]["T_INSIDE"] - processed["T_air"]) / (CONSTANTS["Other"]["HEAT_DEMAND"]["T_INSIDE"] - CONSTANTS["Other"]["HEAT_DEMAND"]["T_AIR_REF"])
    qdot_hvac_preheater[qdot_hvac_preheater < 0.1 * CONSTANTS["Other"]["HEAT_DEMAND"]["HVAC_PREHEATER"]] = 0 # The pre-heater is not working during summer
    # qdot_hvac_reheater = CONSTANTS["Other"]["HEAT_DEMAND"]["HVAC_PREHEATER"] * (CONSTANTS["Other"]["HEAT_DEMAND"]["T_INSIDE"] - processed["T_air"]) / (CONSTANTS["Other"]["HEAT_DEMAND"]["T_INSIDE"] - CONSTANTS["Other"]["HEAT_DEMAND"]["T_AIR_REF"])




    return processed












def heatDemandProducerSide(processed, CONSTANTS):





    return processed