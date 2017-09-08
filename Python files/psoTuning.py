import sys
import numpy
import pandas as pd
import constants as kk
from pyswarm import pso
import os
import input


def preparation():
    project_path = 'C:\\Users\\FrancescoBaldi\\switchdrive\\Work in progress\\Paper 0\\Ecos2015PaperExtension\\'
    path_files = project_path + os.sep
    sys.path.append(path_files)
    filenames = input.filenames(project_path)  # Note: this is just a test
    CONSTANTS = kk.constantsSetting()
    CONSTANTS["filenames"] = filenames
    processed_temp = pd.read_hdf(CONSTANTS["filenames"]["dataset_output"], 'processed')
    dataset_raw = pd.read_hdf(filenames["dataset_raw"], 'table')
    data = pd.DataFrame(index=processed_temp.index)
    indexes_2_save_processed = {"Passengers_calc", "Demands:Electricity:HVAC:Edot", "T_air",
                      "AE1:Cyl:FuelPh_in:mdot", "AE2:Cyl:FuelPh_in:mdot", "AE3:Cyl:FuelPh_in:mdot", "AE4:Cyl:FuelPh_in:mdot",
                      "ME1:Cyl:FuelPh_in:mdot", "ME2:Cyl:FuelPh_in:mdot", "ME3:Cyl:FuelPh_in:mdot","ME4:Cyl:FuelPh_in:mdot",
                      "ME2:HRSG:Steam_in:mdot", "ME3:HRSG:Steam_in:mdot",
                      "AE1:HRSG:Steam_in:mdot", "AE2:HRSG:Steam_in:mdot", "AE3:HRSG:Steam_in:mdot", "AE4:HRSG:Steam_in:mdot",
                      "CoolingSystems:HTcollector24:HTWater_out:mdot", "CoolingSystems:HTcollector13:HTWater_out:mdot",
                      "CoolingSystems:HTcollector24:HTWater_out:T", "CoolingSystems:HTcollector13:HTWater_out:T",
                      "ME1:on", "ME2:on", "ME3:on", "ME4:on", "AE1:on", "AE2:on", "AE3:on", "AE4:on",
                      }
    indexes_2_save_raw = {"SBO 1 OUTLET PRESSUR:7313:bar:Average:900", "SBO 2 OUTLET PRESSUR:7333:bar:Average:900", "Boiler_Port", "Boiler_starbord"}
    for idx in indexes_2_save_processed:
        data[idx] = processed_temp[idx]
    for idx in indexes_2_save_raw:
        data[idx] = dataset_raw[idx]
    # Prepare the input
    constant_input = (data, CONSTANTS, "optimization")
    # Set the boundaries
    lb = [0.0, 0.5, 293, 243, 0.5, 0.5, 343, 1e4, 2000]
    ub = [1.0, 1.5, 298, 253, 1.0, 1.0, 353, 1e5, 8000]
    # Launch the optimization
    xopt, fopt = pso(fitnessFunction, lb, ub, args=constant_input, debug=True)
    # xopt = [6.71988240e-01, 5.60706250e-01, 2.97130271e+02, 2.49548290e+02, 8.10322609e-01, 5.39518203e-01, 3.51315316e+02, 5.42492594e+03]
    # xopt = [6.06116231e-01, 9.19705648e-01, 2.96474980e+02, 2.52603434e+02, 9.85583957e-01, 5.23062343e-01, 3.44799481e+02, 1.00268573e+04, 7.25138168e+03]
    fitnessFunction(xopt, data, CONSTANTS, "test")
    return (xopt, fopt)

def fitnessFunction(param, *args):
    (data, CONSTANTS, run_type) = args

    db_index = data.index
    ## CALCULATING DEMANDS
    # Re-heater
    Qdot_rh = (param[0] * data["Demands:Electricity:HVAC:Edot"] / data["Demands:Electricity:HVAC:Edot"].max()) * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_REHEATER"]
    Qdot_rh[data["Demands:Electricity:HVAC:Edot"] <= 0] = 0
    # Hot water heater
    Qdot_hwh = param[1] * data["Passengers_calc"] / 1800 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HOT_WATER_HEATER"] * (
        pd.Series((round(len(data) / 96) * numpy.ndarray.tolist(numpy.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HWH_HOURLY"], 4)))[:len(data)],index=db_index))
    temp = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"] * (param[2] - data["T_air"]) / (param[2] - param[3]) - 0.100 * data["Passengers_calc"]
    temp[temp < 0.1 * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"]] = 0
    Qdot_ph = temp  # The pre-heater is not working during summer
    Qdot_galley = param[4] * CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY"] * pd.Series((round(len(data) / 96) * numpy.ndarray.tolist(
        numpy.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY_HOURLY"], 4)))[:len(data)], index=db_index)
    Qdot_other = param[5] * (
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["TANK_HEATING"] +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["OTHER_TANKS"] +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HFO_TANK_HEATING"] +
        CONSTANTS["General"]["HFO"]["CP"] * (
            data["AE1:Cyl:FuelPh_in:mdot"] + data["AE2:Cyl:FuelPh_in:mdot"] + data[
                "AE3:Cyl:FuelPh_in:mdot"] + data["AE4:Cyl:FuelPh_in:mdot"] +
            data["ME1:Cyl:FuelPh_in:mdot"] + data["ME2:Cyl:FuelPh_in:mdot"] + data[
                "ME3:Cyl:FuelPh_in:mdot"] + data["ME4:Cyl:FuelPh_in:mdot"]) * 100)

    ## Calculation generation
    Qdot_hrsg13 = (data["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
    Qdot_hrsg24 = (data["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
    Qdot_hrsg = Qdot_hrsg13 + Qdot_hrsg24
    # HTHR
    mdot_hr = (Qdot_hwh + Qdot_rh + Qdot_ph) / (90+273.15 - param[6]) / CONSTANTS["General"]["CP_WATER"]
    ER13off = ~data["ME1:on"] & ~data["ME3:on"] & ~data["AE1:on"] & ~data["AE3:on"]
    ER24off = ~data["ME2:on"] & ~data["ME4:on"] & ~data["AE2:on"] & ~data["AE4:on"]
    # We should be able to proceed in both cases
    mdot_min24 = pd.concat([mdot_hr, data["CoolingSystems:HTcollector24:HTWater_out:mdot"]],axis=1).min(axis=1)
    mdot_min13 = pd.concat([mdot_hr, data["CoolingSystems:HTcollector13:HTWater_out:mdot"]],axis=1).min(axis=1)
    # Now, the conditions at the HTHR inputs from the HT side are given, so we can calculate the heat flow using the eps NTU method
    Qdot_HTHR24 = pd.Series(index = db_index)
    Qdot_HTHR24 = CONSTANTS["MainEngines"]["EPS_CAC_HTSTAGE"] * mdot_min24 * CONSTANTS["General"]["CP_WATER"] * (
        data["CoolingSystems:HTcollector24:HTWater_out:T"] - param[6])
    # Once again, to avoid risks, when all engines of the ER 24 are off, the heat flow here is 0
    Qdot_HTHR24[ER24off] = 0
    Qdot_HTHR24[Qdot_HTHR24 < 0] = 0  # we assume that there is no possibility of back flow
    T_HR_intermediate = param[6] + Qdot_HTHR24 / mdot_hr / CONSTANTS["General"]["CP_WATER"]
    # Finally, we can do the same for the HTHR 13 exchanger
    Qdot_HTHR13 = pd.Series(index = db_index)
    Qdot_HTHR13 = CONSTANTS["MainEngines"]["EPS_CAC_HTSTAGE"] * mdot_min13 * CONSTANTS["General"]["CP_WATER"] * (
        data["CoolingSystems:HTcollector13:HTWater_out:T"] - T_HR_intermediate)
    Qdot_HTHR13[ER13off] = 0
    Qdot_HTHR13[Qdot_HTHR13 < 0] = 0

    Qdot_demand_hr = Qdot_rh + Qdot_ph + Qdot_hwh
    Qdot_steam_heater = Qdot_demand_hr - Qdot_HTHR13 - Qdot_HTHR24

    Qdot_steam = Qdot_steam_heater + Qdot_galley + Qdot_other

    #dpdt1 = data["SBO 1 OUTLET PRESSUR:7313:bar:Average:900"].diff() * 1e5 / 15 / 60
    #dpdt2 = data["SBO 2 OUTLET PRESSUR:7333:bar:Average:900"].diff() * 1e5 / 15 / 60
    #dpdt1[(dpdt1 > 75) | (dpdt1 < -75)] = 75
    #dpdt2[(dpdt2 > 75) | (dpdt2 < -75)] = 75
    #Qdot_ab = (dpdt1 + dpdt2) * param[7] + Qdot_steam - Qdot_hrsg


    Qdot_ab = pd.Series(index=db_index)
    Qdot_ab[:] = 0
    Qdot_deficit = -Qdot_steam + Qdot_hrsg
    Qcumul_deficit = Qdot_deficit.cumsum()
    total_deficit = Qcumul_deficit[db_index[-1]]
    dt_boiler = int(numpy.ceil(param[7] / param[8]))
    limit = param[7]
    while total_deficit < -limit:
        idx = Qcumul_deficit.loc[Qcumul_deficit < -limit].index
        if len(idx) > 0:
            last = min(len(idx), dt_boiler)
            Qdot_ab[idx[0]:idx[0+last-1]] = param[7] / dt_boiler
            limit = limit + param[7]

    mdot_ab = Qdot_ab / CONSTANTS["OtherUnits"]["BOILER"]["ETA_DES"] / CONSTANTS["General"]["HFO"]["LHV"]



    # Calculation of the total error
    boilers_measured = (data["Boiler_Port"].resample("D").mean() + data["Boiler_starbord"].resample(
        "D").mean()) * CONSTANTS["General"]["HFO"]["LHV"]
    boilers_calculated = mdot_ab.resample("D").sum() * 60 * 15 * CONSTANTS["General"]["HFO"]["LHV"]

    cumulated_error = ((((boilers_calculated - boilers_measured)**2).sum()) / (boilers_measured**2).sum())**0.5
    cumulated_error = cumulated_error + sum(mdot_ab<0)/1000
    # print(".")

    if run_type == "test":
        import matplotlib.pylab as plt
        boilers_measured.plot()
        boilers_calculated.plot()
        plt.show()


    return cumulated_error



(xopt, fopt) = preparation()
