import matplotlib.pyplot as plt
from helpers import d2df

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
                    x = data[plot]
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
        plt.figure()
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
            plt.plot(hrsg, 'k-', label="HRSG")
            plt.plot(hthr, 'b-', label="HTHR")
            # plt.plot(hthr_max, 'b:', label="HTHR max")
            plt.plot(boilers_measured, 'r-', label="Boilers (M)")
            plt.plot(boilers_calculated, 'r:', label="Boilers (C)")
            plt.plot(total, 'g-', label='Total heating demand')
            plt.legend()
        if filename == "Pie:TotalEnergy":
            quantities = [processed["Demands:Mechanical:Total:Edot"].sum() , processed["Demands:Electricity:Total:Edot"].sum() , processed["Demands:Heat:Total:Edot"].sum()]
            labels = ["Mechanical Power" , "Electric Power" , "Thermal Power"]
            explode = (0.05 , 0.05 , 0.05)
            plt.pie(quantities, labels=labels, explode=explode, autopct='%1.1f%%', shadow=True,)
        if filename == "Pie:Heat":
            quantities = []
            labels = []
            explode = []
            for demand in dict_structure["systems"]["Demands"]["units"]["Heat"]["flows"]:
                quantities.append(processed[d2df("Demands","Heat",demand,"Edot")].sum())
                labels.append(demand)
                explode.append(0.05)
            plt.pie(quantities, labels=labels, explode=explode, autopct='%1.1f%%', shadow=True,)
        if filename == "Hist:WHR":
            temp = processed["HTHR:HTHR13:HRWater_in:mdot"] * CONSTANTS["General"]["CP_WATER"] * (processed["HTHR:HTHR13:HRWater_out:T"] - processed["HTHR:HTHR24:HRWater_in:T"])
            temp2 = (processed["ME2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["ME3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE1:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE2:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE3:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"] + processed["AE4:HRSG:Steam_in:mdot"] * CONSTANTS["Steam"]["DH_STEAM"])
            plt.hist(temp, 50, normed=1, alpha=0.5, label="HTHR")
            plt.hist(temp2, 50, normed=1, alpha=0.5, label="HRSG")
            plt.legend()
        if filename == "TimeSeries:El+Tair_vs_time":
            # Plotting with two different y axis
            fig, ax1 = plt.subplots()
            ax1.plot(processed["Demands:Electricity:Total:Edot"]["2014-04-01":"2014-11-01"].resample('D').mean(), "b--", label="Electric power")
            ax1.set_xlabel('Time [YYYY:MM]')
            ax1.set_ylabel('Power [kW]')
            plt.legend()
            # Adding the second axis
            ax2 = ax1.twinx()
            ax2.plot(processed["T_air"]["2014-04-01":"2014-11-01"].resample('D').mean(), 'r--', label="Ambient air temperature")
            ax2.set_ylabel('Temperature [K]')
            plt.legend()
        plt.show()



