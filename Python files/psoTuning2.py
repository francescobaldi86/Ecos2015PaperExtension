import sys
import numpy
import pandas as pd
import constants as kk
from pyswarm import pso
import os
import input
import datetime as dt


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
    lb = [0.0,  0.0,  0.0, 0.5, 0.5, 0.5, 0.2, 343, 0.5, 1e2, 2000]
    ub = [1000, 1000, 1.0, 1.0, 1.0, 1.0, 1.0, 353, 0.9, 1e5, 8000]
    # param[0] = Constant demand to the HTHR systems
    # param[1] = Constant steam demand
    # param[2] = a1 factor of the HVAC re-heater     (HVAC,RH)
    # param[3] = a1 factor of the hot water heater   (HWH)
    # param[4] = a1 factor of the HVAC pre-heater    (HVAC,PH)
    # param[5] = a1 factor of the Galley             (G)
    # param[6] = a1 factor of the Other users        (TH, OT, HFOT)
    # param[7] = Fixed temperature of the HRHT
    # param[8] = Effectiveness of the HTHR heat exchangers
    # param[9] = Boiler drum steam storage capacity [MJ, energy]
    # param[10] = Boiler heat rate when in use [kW]

    # Launch the optimization
    # xopt, fopt = pso(fitnessFunction, lb, ub, args=constant_input, debug=True)
    # Test 1: Storage size lower boundary = 1e4
    # xopt = [2.91644687e+02, 8.17208680e+01, 5.53887266e-01, 9.09731971e-01, 9.94747229e-01, 5.00805591e-01, 2.77852293e-01, 3.44650539e+02, 8.61087194e-01, 1.00000000e+04, 7.81351743e+03]
    # opt = 0.37162408752748827
    # Test 2: Storage size lower boundary = 1e3
    # Note: the 3* factor in param[9] comes from trying to manually adapt the frequency of the start-stops to the boiler pressure signal
    xopt = [1.36929841e+02, 1.76569058e+02, 5.90926596e-01, 7.06974933e-01, 9.98138178e-01, 5.47476618e-01, 2.69942265e-01, 3.45398252e+02, 7.18364651e-01, 3*2.06480953e+03, 2.92188518e+03]
    fopt = 0.3633742911019279
    fitnessFunction(xopt, data, CONSTANTS, "test")
    return (xopt, fopt)

def fitnessFunction(param, *args):
    (data, CONSTANTS, run_type) = args

    Qdot_HTHR_constant = param[0]
    Qdot_steam_constant = param[1]
    HVACreheaterCoefficient = param[2]
    HotWaterHeaterCoefficient = param[3]
    HVACpreheaterCoefficient = param[4]
    GalleyCoefficient = param[5]
    OtherCoefficient = param[6]
    HTHRinletTemperature = param[7]
    HTHRhexEffectiveness = param[8]
    BoilerStorageSize = param[9]
    BoilerReferencePower = param[10]

    db_index = data.index
    ## CALCULATING DEMANDS
    # Re-heater
    Qdot_rh = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_REHEATER"] * (HVACreheaterCoefficient * data["Demands:Electricity:HVAC:Edot"] / data["Demands:Electricity:HVAC:Edot"].max())
    Qdot_rh[data["Demands:Electricity:HVAC:Edot"] <= 0] = 0
    # Hot water heater
    Qdot_hwh = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HOT_WATER_HEATER"] * (HotWaterHeaterCoefficient * data["Passengers_calc"] / 1800 * (
        pd.Series((round(len(data) / 96) * numpy.ndarray.tolist(numpy.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HWH_HOURLY"], 4)))[:len(data)],index=db_index)))
    temp = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HVAC_PREHEATER"] * (HVACpreheaterCoefficient * (297 - data["T_air"]) / (297 - 248)) - 0.100 * data["Passengers_calc"]
    temp[data["Demands:Electricity:HVAC:Edot"] > 20] = 0
    Qdot_ph = temp  # The pre-heater is not working during summer
    Qdot_galley = CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY"] * (GalleyCoefficient * pd.Series((round(len(data) / 96) * numpy.ndarray.tolist(
        numpy.repeat(CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["GALLEY_HOURLY"], 4)))[:len(data)], index=db_index))
    Qdot_other = ((
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["TANK_HEATING"] +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["OTHER_TANKS"]  +
        CONSTANTS["OtherUnits"]["HEAT_DEMAND"]["HFO_TANK_HEATING"]) * (OtherCoefficient * data["T_air"] / 298) +
        CONSTANTS["General"]["HFO"]["CP"] * (
            data["AE1:Cyl:FuelPh_in:mdot"] + data["AE2:Cyl:FuelPh_in:mdot"] + data[
                "AE3:Cyl:FuelPh_in:mdot"] + data["AE4:Cyl:FuelPh_in:mdot"] +
            data["ME1:Cyl:FuelPh_in:mdot"] + data["ME2:Cyl:FuelPh_in:mdot"] + data[
                "ME3:Cyl:FuelPh_in:mdot"] + data["ME4:Cyl:FuelPh_in:mdot"]) * (150-80))

    ## Calculation generation
    Qdot_hrsg13 = (data["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
    Qdot_hrsg24 = (data["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                   data["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
    Qdot_hrsg = Qdot_hrsg13 + Qdot_hrsg24
    # HTHR
    mdot_hr = (Qdot_hwh + Qdot_rh + Qdot_ph) / (90+273.15 - HTHRinletTemperature) / CONSTANTS["General"]["CP_WATER"]
    ER13off = ~data["ME1:on"] & ~data["ME3:on"] & ~data["AE1:on"] & ~data["AE3:on"]
    ER24off = ~data["ME2:on"] & ~data["ME4:on"] & ~data["AE2:on"] & ~data["AE4:on"]
    # We should be able to proceed in both cases
    mdot_min24 = pd.concat([mdot_hr, data["CoolingSystems:HTcollector24:HTWater_out:mdot"]],axis=1).min(axis=1)
    mdot_min13 = pd.concat([mdot_hr, data["CoolingSystems:HTcollector13:HTWater_out:mdot"]],axis=1).min(axis=1)
    # Now, the conditions at the HTHR inputs from the HT side are given, so we can calculate the heat flow using the eps NTU method
    Qdot_HTHR24 = pd.Series(index = db_index)
    Qdot_HTHR24 = HTHRhexEffectiveness * mdot_min24 * CONSTANTS["General"]["CP_WATER"] * (
        data["CoolingSystems:HTcollector24:HTWater_out:T"] - HTHRinletTemperature)
    # Once again, to avoid risks, when all engines of the ER 24 are off, the heat flow here is 0
    Qdot_HTHR24[ER24off] = 0
    Qdot_HTHR24[Qdot_HTHR24 < 0] = 0  # we assume that there is no possibility of back flow
    T_HR_intermediate = HTHRinletTemperature + Qdot_HTHR24 / mdot_hr / CONSTANTS["General"]["CP_WATER"]
    # Finally, we can do the same for the HTHR 13 exchanger
    Qdot_HTHR13 = pd.Series(index = db_index)
    Qdot_HTHR13 = HTHRhexEffectiveness * mdot_min13 * CONSTANTS["General"]["CP_WATER"] * (
        data["CoolingSystems:HTcollector13:HTWater_out:T"] - T_HR_intermediate)
    Qdot_HTHR13[ER13off] = 0
    Qdot_HTHR13[Qdot_HTHR13 < 0] = 0

    Qdot_demand_hr = Qdot_rh + Qdot_ph + Qdot_hwh + Qdot_HTHR_constant
    Qdot_steam_heater = Qdot_demand_hr - Qdot_HTHR13 - Qdot_HTHR24

    Qdot_steam = Qdot_steam_heater + Qdot_galley + Qdot_other + Qdot_steam_constant

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
    dt_boiler = int(numpy.ceil(BoilerStorageSize / BoilerReferencePower))
    limit = BoilerStorageSize
    while total_deficit < -limit:
        idx = Qcumul_deficit.loc[Qcumul_deficit < -limit].index
        if len(idx) > 0:
            last = min(len(idx), dt_boiler)
            Qdot_ab[idx[0]:idx[0]+dt.timedelta(minutes=15*(last-1))] = (BoilerStorageSize - (limit + Qcumul_deficit[idx[0]]) - Qdot_deficit[idx[0]+dt.timedelta(minutes=15):idx[0]+dt.timedelta(minutes=15*(last-1))].sum()) / dt_boiler
            # limit = limit + param[7] - Qdot_deficit[idx[0]+dt.timedelta(minutes=15):idx[0]+dt.timedelta(minutes=15*(last-1))].sum()
            limit = limit + Qdot_ab[idx[0]:idx[0]+dt.timedelta(minutes=15*(last-1))].sum()
    mdot_ab = Qdot_ab / CONSTANTS["OtherUnits"]["BOILER"]["ETA_DES"] / CONSTANTS["General"]["HFO"]["LHV"]
    # The extra steam during summer is dumped in the hot well
    Qdot_steam_dumped = (Qdot_hrsg + Qdot_ab[:] - Qdot_steam)
    Qdot_steam_dumped[(Qdot_hrsg + Qdot_ab[:] - Qdot_steam).cumsum()<BoilerStorageSize*0.05] = 0



    # Calculation of the total error
    boilers_measured = (data["Boiler_Port"].resample("D").mean() + data["Boiler_starbord"].resample(
        "D").mean()) * CONSTANTS["General"]["HFO"]["LHV"]
    boilers_calculated = mdot_ab.resample("D").sum() * 60 * 15 * CONSTANTS["General"]["HFO"]["LHV"]

    cumulated_error = ((((boilers_calculated - boilers_measured)**2).sum()) / (boilers_measured**2).sum())**0.5
    # Add to the error on the boiler fuel consumption, the possible error on the boiler being "overloaded" during the summer months
    # print(".")

    if run_type == "test":
        import matplotlib.pylab as plt
        boilers_measured.plot()
        boilers_calculated.plot()
        plt.show()


    return cumulated_error



(xopt, fopt) = preparation()

