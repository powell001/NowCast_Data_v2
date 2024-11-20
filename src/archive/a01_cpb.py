import pandas as pd
import cbsodata
import matplotlib.pyplot as plt
import numpy as np
import functools as ft

##############################
# CPB World Trade
# https://www.cpb.nl/en/world-trade-monitor-november-2023
# trade weighted Euro Area
# DATA needs to be processed by hand, just over write: data/cpb_trade_data.csv
#############################

def cpb_exports_imports(verbose = False):
    print("cpd imports/exports")
    Euro_Area_Exports_Imports_mo = pd.read_csv("data/cpb_trade_data.csv")
    Euro_Area_Exports_Imports_mo.index = pd.date_range(start='01/01/2000', end='06/01/2024', freq="M").to_period('M')
    print(Euro_Area_Exports_Imports_mo.index)
    Euro_Area_Exports_Imports_mo.index = pd.PeriodIndex(Euro_Area_Exports_Imports_mo.index, freq='M').to_timestamp()

    if verbose:
        print(Euro_Area_Exports_Imports_mo)

    # Euro_Area_Exports_Imports_mo.plot()
    # plt.title('Global Europe imports exports Index May 2024')
    # plt.savefig("../figures/Euro_Area_Exports_Imports_mo.png")
    # plt.show()

    Euro_Area_Exports_Imports_mo.to_csv("output/cpb_Euro_Area_Exports_Imports_mo.csv")

cpb_exports_imports(True)
