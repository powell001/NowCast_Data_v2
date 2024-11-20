import pandas as pd
import numpy as np
from pmdarima import auto_arima
import matplotlib.pyplot as plt

# process monthly data, read in and forecast to end of the period using simple arima
# loop over each column

##################################
# Monthly data
##################################

def monthlydata():

    data = pd.read_csv("output_combined/a0_combinedMonthly.csv", index_col=[0])

    a0_combinedMonthly_new = []
    for i in range(0, data.shape[1]):
        print("##################################")
        print(i)
        lastdate = data.index[-1]
        col1 = data.iloc[:, [i]]

        negatives = list(range(-4, 0, 1))
        lengthtoforecast = []
        for i in negatives:
            val = col1.iloc[i,:].tolist()
            if np.isnan(val):
                nan_date = col1.iloc[[i]].index[0]
                lengthtoforecast.append(nan_date)

        forecasthorizon = len(lengthtoforecast)

        data1 = col1.dropna()

        arima_model = auto_arima(data1.values, start_p=0, d=1, start_q=0,
            max_p=5, max_d=5, max_q=5,
            start_P=0, D=1, start_Q=0, max_P=5, max_D=5,
            max_Q=5, seasonal=False,
            stationary=False,
            error_action='warn', trace=False,
            suppress_warnings=True, stepwise=True, n_fits=50)

        if len(lengthtoforecast) > 0:
            forecasts = arima_model.predict(forecasthorizon)
            print(lengthtoforecast)

        for i in range(0,len(lengthtoforecast)):
            col1.loc[lengthtoforecast[i],:] = forecasts[i]
        a0_combinedMonthly_new.append(col1)

    a0_combinedMonthly_extended = pd.concat(a0_combinedMonthly_new, axis=1)

    a0_combinedMonthly_extended.columns = data.columns
    a0_combinedMonthly_extended.to_csv("output_combined/a0_combinedMonthly_extended_ARIMA.csv")
    print(a0_combinedMonthly_extended)


monthlydata()

##################################
# Quarterly data (do by hand because only one column needs to be adjusted
# open a0_combinedQuarterly
# Then save by hand
##################################
def qtdata(donothing=True):
    data = pd.read_csv("output_combined/a0_combinedQuarterly.csv", index_col=[0])

    if donothing:
        data.to_csv("output_combined/a0_combinedQuarterly_extended_ARIMA.csv")

    else:
        print(data)

        datacolumns = data.loc[:, ['Residential_NLD_Housing_Prices']]

        data_nonans = datacolumns.dropna()

        arima_model = auto_arima(data_nonans.values, start_p=0, d=1, start_q=0,
                    max_p=5, max_d=5, max_q=5,
                    start_P=0, D=1, start_Q=0, max_P=5, max_D=5,
                    max_Q=5, seasonal=False,
                    stationary=False,
                    error_action='warn', trace=False,
                    suppress_warnings=True, stepwise=True, n_fits=50)


        forecasts = arima_model.predict(1)
        print(forecasts)

        xxx.to_csv("output_combined/a0_combinedMonthly_extended_ARIMA.csv")

        # ######################
        # print("Stop, this needs to be done by hand!")

#qtdata(donothing=True)