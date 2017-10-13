def exportEfficiecies(processed, CONSTANTS, dict_structure):
    # This function writes out the CSV file with the processed, aggregated data about efficiencies and such for the
    # whole operating period
    text_file = open(CONSTANTS["filenames"]["aggregated_efficiencies"], "w")
    text_file.write("Variable name,EnergyEfficiency,ExergyEfficiency,EfficiencyDefect,IrreversibilityShare\n")
    for system in ["ME1", "ME2", "ME3", "ME4", "AE1", "AE2", "AE3", "AE4", "CoolingSystems", "HTHR", "Steam"]:
        text_file.write("\n")
        text_file.write(system+", , , ," + str(processed[system+":"+"delta"].mean()) + "\n")
        for unit in dict_structure["systems"][system]["units"]:
            text_file.write(unit)
            for efficiency in ["eta", "eps", "lambda", "delta"]:
                if system + ":" + unit + ":" + efficiency in processed.columns:
                    text_file.write("," + str(processed[system+":"+unit+":"+ efficiency].mean()))
                else:
                    text_file.write(",")
            text_file.write("\n")
    text_file.close()
