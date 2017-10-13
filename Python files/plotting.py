import matplotlib.pyplot as plt
from helpers import d2df
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle

def plotMain(type, dict_structure, processed, *args):
    # This function plots the contents of the analysed files.
    # Two input values for "type" are accepted:
    # - "off" [default]: does not print anything
    # - "prompt": prompts the user for what s/he wants to print
    # - "csv": reads info on what is to be read from a csv file
    if type == "prompt":
        plot_info = plotPrompt(dict_structure)
        data_type = "processed"
    elif type == "prompt_raw":
        hd = args[0]
        plot_info = plotPromptRaw(dict_structure,hd)
        data_type = "raw"
    elif type == "csv":
        filename = args[0]
        plot_info = plotFromCSV(dict_structure)
        data_type = "processed"
    else:
        print("Either the -type- input was not correct, or you don't wish to print anything. No printout")
        return
    plottingFunction(plot_info, processed, data_type)


def plotPrompt(dict_structure):
    # This function prompts the user for the required inputs to plot.
    # Two alternatives are available:
    # - The default is "automatic". It is the one that is set by default. The input needs to be provided using a
    #   specific format
    # - The alternative is "simple", that is activated either typing "S" or "s" or "Simple" or "simple". This helps the
    #   user plotting by specifically asking for the required input
    #
    # This function outputs an object structured in this way:
    # - The main object is a LIST.
    # - Every list element is a DICTIONARY, representing a different plot. There are two fields:
    # --- A "plot_mode" field, which is just a STRING
    # --- A "variables" field, which is a LIST of DICTIONARIES. Each element is a different line in the plot
    # - Each line is identified by the following fields:
    # --- System
    # --- Component
    # --- Flow
    # --- Property
    output = []
    accepted_plot_mode = ["sankey", "hist", "timeSeries"]
    input1 = input("Provide input for advanced plotting. If you wish to switch to simple mode, type ""s"" ")
    if input1 == "s" or input1 == "S" or input1 == "Simple" or input1 == "simple":
        output.append({})
        output[0]["variables"] = []
        while True:
            plot_mode = input("Switched to simple mode. Please enter the plot type. Available choices are: ""sankey"", ""hist"", ""timeSeries"" ")
            if plot_mode in accepted_plot_mode:
                output[0]["plot_mode"] = plot_mode
                break
            else:
                print("The input you gave (" + plot_mode + ") for the plot type is not correct! Maybe there was a typo? Try again!")
        while True:
            # We start here a loop to allow for printing more things in the same figure
            line_info = {}
            while True:
                plot_system = input("Now input what system you like to plot for. Available are choices are ""ME#"" (#=1,2,3,4), ""AE#"" (#=1,2,3,4), and ""Other"" ")
                if plot_system in dict_structure["systems"]:
                    line_info["system"] = plot_system
                    break
                else:
                    print("The input you gave (" + plot_system + ") for the system name is not correct! Maybe there was a typo? Try again!")
            while True:
                plot_unit = input("Now input what component of the chosen system you like to plot for:")
                if plot_unit in dict_structure["systems"][line_info["system"]]["units"]:
                    line_info["unit"] = plot_unit
                    break
                else:
                    print("The input you gave (" + plot_unit + ") for the component name is not correct! Maybe there was a typo? Try again!")
            while True:
                plot_flow = input("Now input what flow of the chosen component you like to plot for:")
                if plot_flow in dict_structure["systems"][line_info["system"]]["untis"][line_info["unit"]]["flows"]:
                    line_info["flow"] = plot_flow
                    break
                else:
                    print("The input you gave (" + plot_flow + ") for the flow name is not correct! Maybe there was a typo? Try again!")
            while True:
                plot_property = input("Finally, input what property of the chosen flow you like to plot for:")
                if plot_property in dict_structure["systems"][line_info["system"]]["untis"][line_info["unit"]]["flows"][line_info["flow"]]["properties"]:
                    line_info["property"] = plot_property
                    break
                else:
                    print("The input you gave (" + plot_property + ") for the property name is not correct! Maybe there was a typo? Try again!")
            output[0]["variables"].append(line_info)
            plot_cycle = input("Thanks! We have everything we need! Do you wish to add anything more to the same plot? if so, type ""y"". Otherwise, type any other character ")
            if plot_cycle == "y":
                print("Cool! Let's add a line to the plot, shall we?")
            else:
                print("OK, so no more inputs. Here comes the plot!")
                break
    else:
        # The automatic reading is based on the following structure
        # - First you give the plot type, followed by "->"
        # - Then you give the inputs in the order as above: system, component, flow, property. Separated by a comma ","
        # - To plot more than one variable in the same plot, a new entry is added with ";" as separator
        # - To add a new plot, the separator to be used is "%"
        # Example: "hist->ME1,TC,EG_in,T;ME1,TC,EG_out,T%timeSeries->ME1,TC,EG_in,T;ME1,TC,EG_out,T"
        split1 = input1.split("%")
        for plot in split1:
            plot_info = {}
            plot_info["variables"] = []
            split2 = plot.split("->")
            plot_mode = split2[0]
            if plot_mode in accepted_plot_mode:
                plot_info["plot_mode"] = plot_mode
            else:
                print("The input you gave (" + plot_mode + ") for the plot type is not correct! Maybe there was a typo? Try again!")
                break
            split3 = split2[1].split(";")
            for line in split3:
                line_info = {}
                split4 = line.split(",")
                plot_system = split4[0]
                plot_unit = split4[1]
                plot_flow = split4[2]
                plot_property = split4[3]
                if plot_system in dict_structure["systems"]:
                    line_info["system"] = plot_system
                else:
                    print("The input you gave (" + plot_system + ") for the system name is not correct! Maybe there was a typo? Try again!")
                    break
                if plot_unit in dict_structure["systems"][line_info["system"]]["units"]:
                    line_info["unit"] = plot_unit
                else:
                    print("The input you gave (" + plot_unit + ") for the component name is not correct! Maybe there was a typo? Try again!")
                    break
                if plot_flow in dict_structure["systems"][line_info["system"]]["units"][line_info["unit"]]["flows"]:
                    line_info["flow"] = plot_flow
                else:
                    print("The input you gave (" + plot_flow + ") for the flow name is not correct! Maybe there was a typo? Try again!")
                    break
                if plot_property in dict_structure["systems"][line_info["system"]]["units"][line_info["unit"]]["flows"][line_info["flow"]]["properties"]:
                    line_info["property"] = plot_property
                else:
                    print("The input you gave (" + plot_property + ") for the property name is not correct! Maybe there was a typo? Try again!")
                    break
                plot_info["variables"].append(line_info)
            output.append(plot_info)
    return output


def plotPromptRaw(structure, hd):
    output = []
    accepted_plot_mode = ["sankey", "hist", "timeSeries"]
    output.append({})
    output[0]["variables"] = []
    while True:
        plot_mode = input(
            "Please enter the plot type. Available choices are: ""sankey"", ""hist"", ""timeSeries"" ")
        if plot_mode in accepted_plot_mode:
            output[0]["plot_mode"] = plot_mode
            break
        else:
            print(
                "The input you gave (" + plot_mode + ") for the plot type is not correct! Maybe there was a typo? Try again!")
    while True:
        # We start here a loop to allow for printing more things in the same figure
        while True:
            plot_var = input("Now input what variable you like to plot for. ")
            if hd[plot_var] in structure.keys():
                output[0]["variables"].append(hd[plot_var])
                break
            else:
                print("The input you gave (" + plot_var + ") for the plot type is not correct! Maybe there was a typo? Try again!")
        plot_cycle = input(
            "Thanks! We have everything we need! Do you wish to add anything more to the same plot? if so, type ""y"". Otherwise, type any other character ")
        if plot_cycle == "y":
            print("Cool! Let's add a line to the plot, shall we?")
        else:
            print("OK, so no more inputs. Here comes the plot!")
            break
    return output



def plotFromCSV(filename):
    # Plots a list of things defined in a CSV files
    print("Still to be defined")



def plottingFunction(plot_info, processed, data_type):
    # Here we go
    if data_type == "processed":
        for figure in plot_info:
            if figure["plot_mode"] == "sankey":
                print("Plot Sankey diagram...as if this was easy")
            else:
                fig = plt.figure()
                for plot in figure["variables"]:
                    x = processed[d2df(plot["system"], plot["unit"], plot["flow"], plot["property"])]
                    if figure["plot_mode"] == "hist":
                        num_bins = 50
                        # the histogram of the data
                        n, bins, patches = plt.hist(x, num_bins, normed=1, alpha=0.5)
                        # add a 'best fit' line
                        plt.xlabel(plot["property"]+" of "+plot["flow"]+" of "+plot["unit"]+" in "+plot["system"])
                        plt.ylabel('Probability')
                    if figure["plot_mode"] == "timeSeries":
                        plt.plot(x)
                        plt.ylabel("Time [YYY:MM]")
                        plt.ylabel(plot["property"] + " of " + plot["flow"] + " of " + plot["unit"] + " in " + plot["system"])

            plt.show()
    elif data_type == "raw":
        for figure in plot_info:
            if figure["plot_mode"] == "sankey":
                print("Plot Sankey diagram...as if this was easy")
            else:
                fig = plt.figure()
                for plot in figure["variables"]:
                    x = processed[plot]
                    if figure["plot_mode"] == "hist":
                        num_bins = 50
                        # the histogram of the data
                        n, bins, patches = plt.hist(x, num_bins, normed=1, alpha=0.5)
                        # add a 'best fit' line
                        plt.xlabel("Variable of interest")
                        plt.ylabel('Probability')
                    if figure["plot_mode"] == "timeSeries":
                        x.plot()
    else:
        print("Data type is wrong. It should be either -raw- or -processed-")




def predefinedPlots(processed, dataset_raw, CONSTANTS, dict_structure, filenames):
    for filename in filenames:
        fig, ax = plt.subplots()

        ### TIME SERIES ###

        if filename == "TimeSeries:Heat_vs_time":
            # Contribution from the HRSGs
            temp = (processed["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
            hrsg = temp.resample("D").sum() * 60 * 15
            # Contribution from the HTHR
            temp = processed["HTHR:HTHR13:HRWater_in:mdot"] * CONSTANTS["General"]["CP_WATER"] * (processed["HTHR:HTHR13:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"])
            hthr = temp.resample("D").sum() * 60 * 15
            # Maximum theoretical contribution from the HT systems
            engine_set = {"ME1" , "ME2" , "ME3" , "ME4" , "AE1" , "AE2" , "AE3" , "AE4"}
            temp =  (sum((processed[d2df(idx, "CAC_HT", "HTWater_out", "T")] - processed[d2df(idx, "JWC", "HTWater_in", "T")]) *
                     processed[d2df(idx, "CAC_HT", "HTWater_out", "mdot")] * CONSTANTS["General"]["CP_WATER"] for idx in engine_set))
            hthr_max = temp.resample("D").sum() * 60 * 15
            # Contribution from the auxiliary boilers
            boilers_measured = (dataset_raw["Boiler_Port"].resample("D").mean() + dataset_raw["Boiler_starbord"].resample("D").mean()) * CONSTANTS["General"]["HFO"]["LHV"]
            boilers_calculated = processed["Steam:Boiler1:FuelPh_in:mdot"].resample("D").sum() * 60 * 15 * CONSTANTS["General"]["HFO"]["LHV"]
            # Total demand
            total = processed["Demands:Heat:Total:Edot"].resample("D").sum() * 60 * 15
            # Actual plotting
            ax.plot(hrsg, 'k-', label="HRSG")
            ax.plot(hthr, 'b-', label="HTHR")
            # plt.plot(hthr_max, 'b:', label="HTHR max")
            ax.plot(boilers_measured, 'r-', label="Boilers (M)")
            ax.plot(boilers_calculated, 'r:', label="Boilers (C)")
            ax.plot(total, 'g-', label='Total heating demand')
            plt.legend()

        if filename == "TimeSeries:TypicalWinterDay":
            ax.plot(processed["Demands:Mechanical:Total:Edot"]["2014-01-31"], "g-", label = "Propulsion power")
            ax.plot(processed["Demands:Electricity:Total:Edot"]["2014-01-31"], "b--", label="Electric power")
            ax.plot(processed["Demands:Heat:Total:Edot"]["2014-01-31"], "r:", label="Heat")
            fig.autofmt_xdate()
            plt.xlabel("Time [MM-DD HH]")
            plt.ylabel("Power [kW]")
            plt.legend()

        if filename == "TimeSeries:TypicalSummerDay":
            ax.plot(processed["Demands:Mechanical:Total:Edot"]["2014-07-31"], "g-", label = "Propulsion power")
            ax.plot(processed["Demands:Electricity:Total:Edot"]["2014-07-31"], "b--", label="Electric power")
            ax.plot(processed["Demands:Heat:Total:Edot"]["2014-07-31"], "r:", label="Heat")
            fig.autofmt_xdate()
            plt.xlabel("Time, [MM-DD HH]")
            plt.ylabel("Power [kW]")
            plt.legend()

        if filename == "TimeSeries:El+Tair_vs_time":
            # Plotting with two different y axis
            ax.plot(processed["Demands:Electricity:Total:Edot"]["2014-04-01":"2014-11-01"].resample('D').mean(), "b--", label="Electric power")
            ax.set_xlabel('Time [YYYY:MM]')
            ax.set_ylabel('Power [kW]')
            plt.legend()
            # Adding the second axis
            ax2 = ax.twinx()
            ax2.plot(processed["T_air"]["2014-04-01":"2014-11-01"].resample('D').mean(), 'r--', label="Ambient air temperature")
            ax2.set_ylabel('Temperature [K]')
            plt.legend()

        if filename == "TimeSeries:HeatBalance":
            # Contribution from the HRSGs
            Qdot_hrsg = (processed["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                    processed["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                    processed["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                    processed["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                    processed["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                    processed["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
            # Contribution from the HTHR
            Qdot_hthr = processed["HTHR:HTHR13:HRWater_in:mdot"] * CONSTANTS["General"]["CP_WATER"] * (processed["HTHR:HTHR13:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"])
            Qdot_ab = processed["Steam:Boiler1:FuelPh_in:mdot"] * CONSTANTS["General"]["HFO"]["LHV"] * CONSTANTS["OtherUnits"]["BOILER"]["ETA_DES"]
            Qdot_dumped = processed["Steam:HotWell:LTWater_in:mdot"] * (
                processed["Steam:HotWell:LTWater_out:T"] - processed["Steam:HotWell:LTWater_in:T"]
            ) * CONSTANTS["General"]["CP_WATER"]
            Qdot_balance = Qdot_hrsg + Qdot_hthr + Qdot_ab - processed["Demands:Heat:Total:Edot"] - Qdot_dumped
            Qdot_balance.plot()
            ax.plot(Qdot_balance.cumsum())
            plt.title("Heat balance")
            plt.xlabel("Time")
            plt.ylabel("Heat balance [kW]")

        if filename == "TimeSeries:HeatGenerationStacked":
            Qdot_hrsg = (processed["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                         processed["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                         processed["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                         processed["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                         processed["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] +
                         processed["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).resample('D').mean()
            Qdot_hthr = (processed["HTHR:HTHR13:HRWater_in:mdot"] * CONSTANTS["General"]["CP_WATER"] * (
                        processed["HTHR:HTHR13:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"])).resample('D').mean()
            Qdot_ab = (processed["Steam:Boiler1:Steam_HotWell_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).resample('D').mean()
            x = Qdot_ab.index
            ax.stackplot(x, Qdot_hrsg, Qdot_hthr, Qdot_ab, colors = ("0.66", "0.33", "0")) # label = ["HRSG", "HTHR", "Aux boiler"]
            p1 = Rectangle((0, 0), 1, 1, fc="0.66")
            p2 = Rectangle((0, 0), 1, 1, fc="0.33")
            p3 = Rectangle((0, 0), 1, 1, fc="0")
            plt.legend([p1, p2, p3], ["HRSG", "HTHR", "Aux boiler"])
            plt.xlabel("Time [YYYY-MM]")
            plt.ylabel("Power [kW]")
        ### PIE CHARTS ###

        if filename == "Pie:TotalEnergySimple":
            quantities = [processed["Demands:Mechanical:Total:Edot"].sum() , processed["Demands:Electricity:Total:Edot"].sum() , processed["Demands:Heat:Total:Edot"].sum()]
            labels = ["Mechanical Power" , "Electric Power" , "Thermal Power"]
            explode = (0.05 , 0.05 , 0.05)
            ax.pie(quantities, labels=labels, explode=explode, autopct='%1.1f%%', shadow=True,)

        if filename == "Pie:DemandFull":
            quantities = [processed["Demands:Mechanical:Propeller1:Edot"].sum() ,
                          processed["Demands:Mechanical:Propeller2:Edot"].sum(),
                          processed["Demands:Electricity:HVAC:Edot"].sum() ,
                          processed["Demands:Electricity:Thrusters:Edot"].sum(),
                          processed["Demands:Electricity:Other:Edot"].sum(),
                          processed["Demands:Heat:HVACpreheater:Edot"].sum(),
                          processed["Demands:Heat:HVACreheater:Edot"].sum(),
                          processed["Demands:Heat:HotWaterHeater:Edot"].sum(),
                          processed["Demands:Heat:MachinerySpaceHeaters:Edot"].sum(),
                          processed["Demands:Heat:OtherTanks:Edot"].sum(),
                          processed["Demands:Heat:TankHeating:Edot"].sum(),
                          processed["Demands:Heat:HFOheater:Edot"].sum(),
                          processed["Demands:Heat:HFOtankHeating:Edot"].sum(),
                          processed["Demands:Heat:Galley:Edot"].sum()]
            labels = ["Propeller-1" , "Propeller-1" ,
                      "HVAC", "Thrusters", "Other users",
                      "HVAC Preheater", "HVAC Reheater", "Hot water heater",
                      "Machinery space heaters", "Other tanks heating", "Fuel tanks heating", "HFO tanks heating", "HFO pre-injection heating", "Galley"]
            explode = []
            for idx in range(len(labels)):
                explode.append((1-(quantities[idx]/sum(quantities))) * 0.1)
            colors = ["green", "green",
                     "blue", "blue", "blue",
                     "sandybrown","sandybrown","sandybrown",
                     "red","red","red","red","red","red"]
            ax.pie(quantities, labels=labels, explode=explode, autopct='%1.1f%%', colors=colors)

        if filename == "Pie:GenerationFull":
            quantities = [processed["ME1:Cyl:FuelPh_in:mdot"].sum(),
                          processed["ME2:Cyl:FuelPh_in:mdot"].sum(),
                          processed["ME3:Cyl:FuelPh_in:mdot"].sum(),
                          processed["ME4:Cyl:FuelPh_in:mdot"].sum(),
                          processed["AE1:Cyl:FuelPh_in:mdot"].sum(),
                          processed["AE2:Cyl:FuelPh_in:mdot"].sum(),
                          processed["AE3:Cyl:FuelPh_in:mdot"].sum(),
                          processed["AE4:Cyl:FuelPh_in:mdot"].sum(),
                          processed["Steam:Boiler1:FuelPh_in:mdot"].sum()]
            labels = ["ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4", "AB"]
            colors = ["0.33", "0.33", "0.33", "0.33", "0.66", "0.66", "0.66", "0.66", "black"]
            ax.pie(quantities, labels=labels, explode=(0.05, )*len(labels), autopct='%1.1f%%', colors=colors)

        if filename == "Pie:HeatDemand":
            quantities = []
            labels = []
            explode = []
            for demand in dict_structure["systems"]["Demands"]["units"]["Heat"]["flows"]:
                quantities.append(processed[d2df("Demands","Heat",demand,"Edot")].sum())
                labels.append(demand)
                explode.append(0.05)
            ax.pie(quantities, labels=labels, explode=tuple(explode), autopct='%1.1f%%', shadow=True)

        if filename == "Pie:HeatGeneration":
            quantities = []
            quantities.append((processed["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum())
            quantities.append((processed["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum())
            quantities.append((processed["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum())
            quantities.append((processed["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum())
            quantities.append((processed["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum())
            quantities.append((processed["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum())
            quantities.append((processed["HTHR:HTHR13:HRWater_in:mdot"] * CONSTANTS["General"]["CP_WATER"] * (
                    processed["HTHR:HTHR13:HRWater_out:T"] - processed["HTHR:HTHR13:HRWater_in:T"])).sum())
            quantities.append((processed["HTHR:HTHR13:HRWater_in:mdot"] * CONSTANTS["General"]["CP_WATER"] * (
                processed["HTHR:HTHR24:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"])).sum())
            quantities.append((processed["Steam:Boiler1:Steam_HotWell_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum())
            labels = ["HRSG - ME2", "HRSG - ME3",
                      "HRSG - AE1", "HRSG - AE2", "HRSG - AE3", "HRSG - AE4",
                      "HTHR - ER13", "HTHR - ER24", "Aux Boiler"]
            explode = (0.05, ) * len(labels)
            colors = ("0.33", "0.33",  "0.33", "0.33", "0.33", "0.33", "0.66", "0.66", "1.0")
            ax.pie(quantities, labels=labels, explode=tuple(explode), autopct='%1.1f%%', shadow=True, colors=colors)

        if filename == "Pie:OperationalMode":
            quantities = []
            labels = []
            colors = []
            temp = pd.Series(processed["operationalMode"].values, dtype="category")
            for category in temp.cat.categories:
                quantities.append(sum(temp == category))
                labels.append(category)
                colors.append("gray")
            patches = ax.pie(quantities, labels=labels, explode=(0.05, 0.05, 0.05, 0.05), autopct='%1.1f%%', shadow=True, colors=colors)[0]
            patches[0].set_hatch('/')
            patches[1].set_hatch('\\')
            patches[2].set_hatch('x')

        ### HISTOGRAMS ###

        if filename == "Hist:WHR":
            temp = processed["HTHR:HTHR13:HRWater_in:mdot"] * CONSTANTS["General"]["CP_WATER"] * (processed["HTHR:HTHR13:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"])
            temp2 = (processed["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
            ax.hist(temp, 50, normed=1, alpha=0.5, label="HTHR")
            ax.hist(temp2, 50, normed=1, alpha=0.5, label="HRSG")
            plt.legend()

        if filename == "Hist:AuxEngines":
            temp1 = []
            for engine in {"AE1", "AE2", "AE3", "AE4"}:
                temp1.append(processed[engine+":Cyl:Power_out:Edot"][processed[engine+":on"]]/CONSTANTS["AuxEngines"]["MCR"])
            ax.hist(tuple(temp1), normed=1, alpha=0.8, label=["AE1", "AE2", "AE3", "AE4"])
            plt.legend()

        if filename == "Hist:MainEngines":
            for engine in {"ME1", "ME2", "ME3", "ME4"}:
                ax.hist(processed[engine+":Cyl:Power_out:Edot"][processed[engine+":on"]]/CONSTANTS["MainEngines"]["MCR"], normed=1, alpha=0.5, label=engine)
            plt.legend()


        ### SCATTER PLOTS ###

        if filename == "Scatter:Pmech_vs_Vship":
            enginesOn = processed["ME1:on"].astype(int) + processed["ME2:on"].astype(int) + processed["ME3:on"].astype(int) + processed["ME4:on"].astype(int)
            for idx in range(5):
                ax.scatter(
                    dataset_raw["SHIPS SPEED:79025:knot:Average:900"][enginesOn==idx],
                    processed["Demands:Mechanical:Total:Edot"][enginesOn==idx],
                    label=(str(idx) + "Engines on"))
            plt.legend()


        ### BAR CHARTS ###

        if filename == "Bar:PercentageWHR":
            # Exhaust gas
            Qdot_hrsg = 0
            Qdot_eg = 0
            Qdot_eg160 = 0
            Bdot_hrsg = 0
            Bdot_eg = 0
            Bdot_eg160diff = 0
            Qdot_hthr = (processed["HTHR:HTHR13:HRWater_out:Edot"] - processed["HTHR:HTHR24:HRWater_in:Edot"]).sum()
            Qdot_ht = 0
            Qdot_lt = 0
            Bdot_hthr = (processed["HTHR:HTHR13:HRWater_out:Bdot"] - processed["HTHR:HTHR24:HRWater_in:Bdot"]).sum()
            Bdot_ht = 0
            Bdot_lt = 0
            for system in {"AE1", "AE2", "AE3", "AE4", "ME1" , "ME2", "ME3", "ME4"}:
                # Exhaust gas, Energy
                if system in {"AE1", "AE2", "AE3", "AE4", "ME2", "ME3"}:
                    Qdot_hrsg = Qdot_hrsg + (processed[system+":HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"]).sum()
                    Bdot_hrsg = Bdot_hrsg + (processed[system + ":HRSG:Steam_out:Bdot"] - processed[system + ":HRSG:Steam_in:Bdot"]).sum()
                Qdot_eg = Qdot_eg + processed[system+":Turbine:Mix_out:Edot"].sum()
                Qdot_eg160 = Qdot_eg160 + (processed[system+":Turbine:Mix_out:mdot"] * CONSTANTS["General"]["CP_EG"] * (processed[system+":Turbine:Mix_out:T"] - 160-273.15)).sum()
                # Exhaust gas, Exergy
                Bdot_eg = Bdot_eg + processed[system + ":Turbine:Mix_out:Bdot"].sum()
                Bdot_eg160diff = Bdot_eg160diff + (processed[system + ":Turbine:Mix_out:mdot"] * CONSTANTS["General"]["CP_EG"] * np.log((160+237.15)/(processed["T_0"])) * ((160+237.15-processed["T_0"]) / np.log((160+237.15)/(processed["T_0"])) - processed["T_0"])).sum()
                # Heating systems, Energy
                Qdot_ht = Qdot_ht + (processed[system+":CAC_HT:HTWater_out:Edot"] - processed[system+":JWC:HTWater_in:Edot"]).sum()
                Qdot_lt = Qdot_lt + (processed[system+":LOC:LTWater_out:Edot"] - processed[system+":CAC_LT:LTWater_in:Edot"]).sum()
                # Heating systems, Exergy
                Bdot_ht = Bdot_ht + (processed[system + ":CAC_HT:HTWater_out:Bdot"] - processed[system + ":JWC:HTWater_in:Bdot"]).sum()
                Bdot_lt = Bdot_lt + (processed[system + ":LOC:LTWater_out:Bdot"] - processed[system + ":CAC_LT:LTWater_in:Bdot"]).sum()
            Bdot_eg160 = Bdot_eg - Bdot_eg160diff
            Qdot_cool = Qdot_ht + Qdot_lt
            Bdot_cool = Bdot_ht + Bdot_lt
            # Exhast gas, efficiencies
            eta_hrsg = Qdot_hrsg / Qdot_eg
            eta_hrsg160 = Qdot_hrsg / Qdot_eg160
            eps_hrsg = Bdot_hrsg / Bdot_eg
            eps_hrsg160 = Bdot_hrsg / Bdot_eg160
            # Cooling systems, efficiencies
            eta_hthr_ht = Qdot_hthr / Qdot_ht
            eta_hthr_lt = Qdot_hthr / Qdot_cool
            eps_hthr_ht = Bdot_hthr / Bdot_ht
            eps_hthr_lt = Bdot_hthr / Bdot_cool
            # Now we plot for real
            n_groups = 4
            bar_width = 0.4
            opacity = 0.4
            index = np.arange(n_groups)
            labels = ("HT water", "All cooling water", "Exhaust Gas, to 160 degC", "Exhaust gas, to environment")
            group1 = ax.bar(index, [eta_hthr_ht, eta_hthr_lt, eta_hrsg160, eta_hrsg], bar_width,
                            alpha = opacity,
                            color = 'b',
                            label = "Energy-based efficiency")
            group2 = ax.bar(index+bar_width, [eps_hthr_ht, eps_hthr_lt, eps_hrsg160, eps_hrsg], bar_width,
                            alpha=opacity,
                            color='r',
                            label="Exergy-based efficiency")
            plt.ylabel('Proportion of available heat recovered')
            plt.xticks(index + bar_width / 2, labels, rotation=10)
            plt.legend()
        plt.show()



