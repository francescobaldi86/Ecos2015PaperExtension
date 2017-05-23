import matplotlib as mp

def plotMain(type,filename,structure):
    # This function plots the contents of the analysed files.
    # Two input values for "type" are accepted:
    # - "off" [default]: does not print anything
    # - "prompt": prompts the user for what s/he wants to print
    # - "csv": reads info on what is to be read from a csv file
    if type == "propmpt":
        plotPrompt(structure)
    elif type == "csv":
        plotFromCSV(filename)
    else:
        return


def plotPrompt(structure):
    # This function prompts the user for the required inputs to plot.
    # Two alternatives are available:
    # - The default is "automatic". It is the one that is set by default. The input needs to be provided using a
    #   specific format
    # - The alternative is "simple", that is activated either typing "S" or "s" or "Simple" or "simple". This helps the
    #   user plotting by specifically asking for the required input
    output = {}
    output["variables"] = []
    input1 = input("Provide input for advanced plotting. If you wish to switch to simple mode, type ""s"" ")
    if input1 == "s" or input1 == "S" or input1 == "Simple" or input1 == "simple":
        while True:
            accepted_plot_mode = ["sankey", "hist", "timeSeries"]
            plot_mode = input("Switched to simple mode. Please enter the plot type. Available choices are: ""sankey"", ""hist"", ""timeSeries"" ")
            if plot_mode in accepted_plot_mode:
                output["plot_mode"] = plot_mode
                break
            else:
                print("The input you gave (" + plot_mode + ") for the plot type is not correct! Maybe there was a typo? Try again!")
        while True:
            # We start here a loop to allow for printing more things in the same figure
            plot_info = {}
            while True:
                plot_system = input("Now input what system you like to plot for. Available are choices are ""ME#"" (#=1,2,3,4), ""AE#"" (#=1,2,3,4), and ""Other"" ")
                if plot_system in structure.keys():
                    plot_info["system"] = plot_system
                    break
                else:
                    print("The input you gave (" + plot_system + ") for the system name is not correct! Maybe there was a typo? Try again!")
            while True:
                plot_component = input("Now input what component of the chosen system you like to plot for:")
                if plot_component in structure[plot_info["system"]].keys():
                    plot_info["component"] = plot_component
                    break
                else:
                    print("The input you gave (" + plot_component + ") for the component name is not correct! Maybe there was a typo? Try again!")
            while True:
                plot_flow = input("Now input what flow of the chosen component you like to plot for:")
                if plot_flow in structure[plot_info["system"]][plot_info["component"]].keys():
                    plot_info["flow"] = plot_flow
                    break
                else:
                    print("The input you gave (" + plot_flow + ") for the flow name is not correct! Maybe there was a typo? Try again!")
            while True:
                plot_property = input("Finally, input what property of the chosen flow you like to plot for:")
                if plot_property in structure[plot_info["system"]][plot_info["component"]][plot_info["flow"]].keys():
                    plot_info["property"] = plot_property
                    break
                else:
                    print("The input you gave (" + plot_property + ") for the property name is not correct! Maybe there was a typo? Try again!")
            output["variables"].append(plot_info)
            plot_cycle = input("Thanks! We have everything we need! Do you wish to add anything more to the same plot? if so, type ""y"". Otherwise, type any other character ")
            if plot_cycle == "y":
                # Do nothing, we will continue looping
            else:
                print("OK, so no more inputs. Here comes the plot!")
                break
    else:
        # The automatic reading is based on the following structure
        # - First you give the plot type, followed by "->"
        # - Then you give the inputs in the order as above: system, component, flow, property. Separated by a comma "y"
        # - To plot more than one variable in the same plot, a new entry is added with ";" as separator
        # - To add a new plot, the separator to be used is "%"
        # Example: "hist->ME1,TC,EG_in,T;ME1,TC,EG_out,T%timeSeries->ME1,TC,EG_in,T;ME1,TC,EG_out,T"


def plotFromCSV(filename):
    # Plots a list of things defined in a CSV files
    print("Still to be defined")