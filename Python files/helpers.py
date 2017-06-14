import pandas as pd
import numpy as np

def polyvalHelperFunction(x,p):
    # The problem with applying "polyval" to data series is that the "x" is the second argument of the function
    # instead of being the first. So we use this function to invert the two, waiting to find a better way
    output = np.polyval(p,x)
    return output

def piecewisePolyvalHelperFunction(x,p):
    # The problem with applying "polyval" to data series is that the "x" is the second argument of the function
    # instead of being the first. So we use this function to invert the two, waiting to find a better way
    output = np.piecewise(x, [x < 0.5 , x >= 0.5], [np.polyval(p[1],x) , np.polyval(p[0],x)])
    return output


def coolpropMixtureHelperFunction(composition):
    mixture = "HEOS::" + "N2[" + str(composition["N2"]) + "]&" + "O2[" + str(composition["O2"]) + "]&" + "H2O[" + str(composition["H2O"]) + "]&" + "CO2[" + str(composition) + "]"
    return mixture


def d2df(system,unit,flow,property):
    header_name = system + ":" + unit + ":" + flow + ":" + property
    return header_name