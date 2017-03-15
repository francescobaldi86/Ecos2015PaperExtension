import pandas as pd
import numpy as np

#Import data into Pandas Data Frame
#The first column is data type, index col is time series Excel.
# 15 min interval data.

ME = pd.read_excel('ME.xlsx',index_col=0)
AE = pd.read_excel('AE.xlsx',index_col=0)
FO = pd.read_excel('FO.xlsx',index_col=0)
Mass_flow = pd.read_excel('Mass_flowmeters.xlsx',index_col=0)
