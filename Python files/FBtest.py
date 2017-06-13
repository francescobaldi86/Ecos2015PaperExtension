import pandas as pd
import sys
import numpy as np

def speedTest(processed):
    dataframe = pd.DataFrame()
    array = np.ndarray((36652,1))
    for system in processed:
        for unit in processed[system]:
            for flow in processed[system][unit]:
                for property in processed[system][unit][flow]:
                    if type(processed[system][unit][flow][property]) == pd.Series:
                        ID = system+"_"+unit+"_"+flow+"_"+property
                        print(ID)
                        dataframe[ID] = processed[system][unit][flow][property]
                        np.append(array,np.array(processed[system][unit][flow][property]))
    print("Dictionary %d MB " % (sys.getsizeof(processed)/1000000))
    print("Dataframe %d MB " % (sys.getsizeof(dataframe)/1000000))
    print("NP-Array %d MB " % (sys.getsizeof(array)/1000000))
    return (dataframe, array)