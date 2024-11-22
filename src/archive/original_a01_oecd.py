import pandas as pd
import cbsodata
from functools import reduce
import matplotlib.pyplot as plt
import numpy as np
import functools as ft

# ##############################
# # OECD Composite leading indicator
# # https://data.oecd.org/leadind/composite-leading-indicator-cli.htm
# https://data-explorer.oecd.org/vis?lc=en&fs[0]=Topic%2C1%7CEconomy%23ECO%23%7CLeading%20indicators%23ECO_LEA%23&pg=0&fc=Topic&bp=true&snb=1&vw=tb&df[ds]=dsDisseminateFinalDMZ&df[id]=DSD_STES%40DF_CLI&df[ag]=OECD.SDD.STES&df[vs]=4.1&pd=1990-01%2C2024-03&dq=CHN%2BG20%2BUSA%2BGBR%2BESP%2BCAN%2BITA%2BJPN%2BDEU%2BFRA.M.LI...AA...H&ly[rw]=TIME_PERIOD&ly[cl]=REF_AREA&to[TIME_PERIOD]=false
# ##############################

def cli_oecd():
    print("Global leading indicators")

    end_date = '08/01/2024'

    CLI_OECD_mo = pd.read_csv("data/leadingIndicators1.csv")

    wantthese = ['CHN', 'JPN', 'FRA', 'USA', 'DEU', 'CAN', 'G20']
    dt1 = CLI_OECD_mo[CLI_OECD_mo['REF_AREA'].isin(wantthese)]
    dt1 = dt1[['REF_AREA', 'TIME_PERIOD', 'OBS_VALUE', 'Frequency of observation']]

    data = []
    for i in wantthese:
        dt2 = dt1[dt1['REF_AREA'] == i]
        dt2 = dt2[dt2['Frequency of observation'] == "Monthly"]
        dt2.set_index('TIME_PERIOD', inplace=True)
        dt2 = dt2[['OBS_VALUE']]
        dt2.columns = [i + "_leadIndicators"]
        data.append(dt2)
        print(dt2)

    alldata = reduce(lambda left, right: pd.merge(left, right, left_index=True,right_index=True, how='outer'), data)

    alldata.index = pd.date_range(start='01/01/1990', end=end_date, freq="M").to_period('M')

    # this adds one day, so end jan becomes first feb
    alldata.index = pd.PeriodIndex(alldata.index, freq='M').to_timestamp()

    return alldata

CLI_OECD_mo = cli_oecd()
CLI_OECD_mo.to_csv("output/LeadInd_OECD_mo.csv")
CLI_OECD_mo.plot()
plt.title('Leading Indicators August 2024')
plt.savefig("figures/CLI_OECD_mo.png")
plt.show()




# CLI_OECD_mo.index = pd.date_range(start='01/01/1961', end='12/01/2023', freq="M").to_period('M')
# CLI_OECD_mo.index = pd.PeriodIndex(CLI_OECD_mo.index, freq='M').to_timestamp()
# #CLI_OECD_mo.rename(columns = {"CPI_G7": "G7_Econ_Indicate", "CPI_G20": "G20_Econ_Indicate"}, inplace=True)
# CLI_OECD_mo.drop(columns = ['Date'], inplace = True)
# print(CLI_OECD_mo)
#
