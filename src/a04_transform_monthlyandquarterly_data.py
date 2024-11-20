import pandas as pd
import numpy as np


def monthlytransform(donothing=False):


    data = pd.read_csv("output/a0_combinedMonthly_extended.csv", index_col=[0])
    if donothing:
        data.to_csv("output/a0_combinedMonthly_extended_transformed.csv")

    else:
        data = data.loc["1996-01-01":, :]
        print(data.columns)

        #####################
        # How to tranform each column?
        #####################

        difference1 = ['Bankruptcies', 'IMP_advanceEconomies', 'EXP_advancedEconomies', 'IMP_EuroArea', 'Exp_EuroArea', 'M3_1', 'M3_2', 'M1', 'AEX_close']

        for i in difference1:
            data[i] = data[i].diff()

        data.to_csv("output/a0_combinedMonthly_extended_transformed.csv")

monthlytransform(donothing = True)

def quarterlytransform(donothing = True):
    data = pd.read_csv("output/a0_combinedQuarterly_extended.csv", index_col=[0])
    if donothing:
        data.to_csv("output/a0_combinedQuarterly_extended_transformed.csv")

    else:
        cols = data.columns
        for i in cols:
            if any(i in s for s in ["gdp_total", "imports_goods_services", "household_cons", "investments", "gdp_invest_business_households", "gov_consumption",  "gov_invest"]):
                data[i] = data[i].diff()
            elif (i == "change_supply") or (i == 'BeloningVanWerknemers_8'):
                data[i] = data[i]
            else:
                data[i] = np.log(data[i]).diff()

        data.to_csv("output/a0_combinedQuarterly_extended_transformed.csv")
quarterlytransform(donothing=True)