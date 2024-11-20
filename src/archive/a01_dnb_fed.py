import pandas as pd
import cbsodata
import matplotlib.pyplot as plt
import numpy as np
import functools as ft
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings("ignore")

##############################
# AEX index
# https://www.dnb.nl/statistieken/dashboards/beurs/
# https://www.dnb.nl/statistieken/data-zoeken/#/details/aandelenbeursindices/dataset/71497a3a-391b-41e3-a858-0d1cc6475208/resource/9f3c874d-6407-44f6-881c-7f9de1dcf31e
# https://finance.yahoo.com/quote/%5EAEX/history/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAACu4k7ufBHqhNRAnGiCQnvmFvIU4HDd918075wEtN7DD3o53yGi6om5kBaEtCX-M3PoJanilbb6BiDq9T0RGLi93eB5a_YSn1YtuaMrf07xiZ5iHPG89TH0gUf8JCljCxikfqsXTyULeltonzyQB-ITTKBXTI173y_PX-s2byRlj

 #############################

def aex_index():
    print('AEX')

    data = pd.read_csv("data/AEX.csv")
    data = data[['Date', 'Adj Close']]
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True, drop=True)

    #data = data.resample('MS').mean()
    data.rename(columns = {"Adj Close": "AEX_close"}, inplace = True)

    return data

aex1 = aex_index()
aex1.to_csv("output/yahoo_aex_index_mo.csv")

aex1.plot()
plt.title('aex close monthly from Yahoo')
plt.savefig("figures/yahoo_aex_index_mo.png")

#############################
# M1 must be calculated from csv (easy)
# from DNB
# Bancaire rente op uitstaande woninghyoptheken van huishoundens in Nederland
# https://www.dnb.nl/statistieken/data-zoeken/#/details/bijdrage-van-nederland-aan-monetaire-aggregaten-in-het-eurogebied-maand/dataset/2639cea8-012c-4202-bb06-51e76bedfeb4/resource/8d1a3cde-6dd8-4207-acb9-8940fc9efe07
##############################

def moneysupply(verbose = False):

    print("Money supply")
    M1 = pd.read_csv('data/(14-08-24)_Bijdrage_van_Nederland_aan_monetaire_aggregaten_in_het_eurogebied_(Maand).csv')

    M1.rename(columns=lambda x: x.strip(), inplace=True)
    M1['Instrument'] = M1['Instrument'].str.strip()
    M1['Periode'] = M1['Periode'].str.strip()
    M1['Soort'] = M1['Soort'].str.strip()
    M1['StandStroom'] = M1['StandStroom'].str.strip()
    M1['Instrument'] = M1['Instrument'].str.strip()

    ############################################
    # M3-inclusive
    M3 = M1[M1['StandStroom'] == 'Standen']
    M3 = M3[M3['Soort'] == 'Aanvullende gegevens']
    M3 = M3[M3['Instrument'] == 'M3 (inclusief chartaal geld in omloop)'][['Periode', 'waarde']]
    M3.drop_duplicates(subset = 'Periode', keep="last", inplace=True)
    M3.set_index('Periode', inplace=True)

    if verbose:
        print(M3)
        M3.plot()
        plt.title("M3-inclus")
        plt.show()
        M3.to_csv("m3.csv")

    # M3-exclusive
    M3_ex = M1[M1['StandStroom'] == 'Standen']
    M3_ex = M3_ex[M3_ex['Soort'] == 'M3-componenten']
    M3_ex = M3_ex[M3_ex['Instrument'] == 'M3 (exclusief chartaal geld in omloop)'][['Periode', 'waarde']]
    M3_ex.drop_duplicates(subset = 'Periode', keep="last", inplace=True)
    M3_ex.set_index('Periode', inplace=True)

    M3_measures_mo = M3.merge(M3_ex, left_index=True, right_index=True, how = 'outer')
    M3_measures_mo.plot()

    if verbose:
        print(M3_ex)
        M3_ex.plot()
        plt.title("M3-exclus")
        plt.show()
    #M3_measures_mo.to_csv("data_mo/M3_measures_mo.csv")

    ############################################
    giral = M1[M1['StandStroom'] == 'Standen']
    giral = giral[giral['Soort'] == 'M3-componenten']
    giral = giral[giral['Instrument'] == 'Girale deposito\'s'][['Periode', 'waarde']]
    giral.drop_duplicates(subset = 'Periode', keep="last", inplace=True)
    giral.set_index('Periode', inplace=True)

    M3_giral_measures_mo = M3_measures_mo.merge(giral, left_index=True, right_index=True, how = 'outer')
    M3_giral_measures_mo.plot()

    if verbose:
        print("giral: ", giral)
        giral.plot()
        plt.show()

    M3_giral_measures_mo.columns = ["M3_1", "M3_2", "M1"]
    M3_giral_measures_mo.index.name = None
    M3_giral_measures_mo.index = pd.date_range(start='12/01/1982', end='07/01/2024', freq="M").to_period('M')
    M3_giral_measures_mo.index = pd.PeriodIndex(M3_giral_measures_mo.index, freq='M').to_timestamp()

    return M3_giral_measures_mo

data = moneysupply(verbose = False)
data.to_csv("output/dnb_M3_giral_measures_mo.csv")

data.plot()
plt.title('DNB Monthly supply December 2023')
plt.savefig("figures/dnb_M3_giral_measures_mo.png")
plt.show()

#############################
# Rente
# https://www.dnb.nl/statistieken/data-zoeken/#/details/kernindicatoren-monetaire-statistieken-maand/dataset/b698ca40-9cae-435b-954e-4fe2c5651370/resource/a8df8430-d941-4706-907b-efd5a9c0bc00
#############################

def renteNetherlands():

    print("Dutch interest rates")
    data = pd.read_csv('data/(14-08-24)_Kernindicatoren_monetaire_statistieken_(Maand).csv')
    data.rename(columns=lambda x: x.strip(), inplace=True)
    data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    data = data[data['Instrument'] == 'Woninghypotheken']
    data = data[data['InstrumentSub'] == "Rente op nieuwe contracten, inclusief heronderhandelingen (percentages)"]
    data.rename(columns = {"Rente op nieuwe contracten, inclusief heronderhandelingen (percentages)": "houseInterestRate"}, inplace = True)
    data.index = pd.date_range(start='01/01/2003', end='07/01/2024', freq="M").to_period('M')
    data.index = pd.PeriodIndex(data.index, freq='M').to_timestamp()
    data = data[["waarde"]]
    data.columns = ['HousingInterestRatesNLD']

    return data

data = renteNetherlands()
data.to_csv("output/dnb_interestrates_mo.csv")
# data.plot()
# plt.title('Interest Rates Housing December 2023')
# plt.savefig("figures/dnb_interestrates_mo.png")
# plt.show()

def zakerenteNetherlands():

    print("Dutch Business interests rates")
    data = pd.read_csv('data/(14-08-24)_Kernindicatoren_monetaire_statistieken_(Maand).csv')
    data.rename(columns=lambda x: x.strip(), inplace=True)
    data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    data = data[data['Instrument'] == "Zakelijke kredietverlening"]
    data = data[data['InstrumentSub'] == "Rente op nieuwe contracten > € 1 mln (percentages)"]
    data.rename(columns = {"Rente op nieuwe contracten > € 1 mln (percentages)  ": "BigBusinessInterestRate"}, inplace = True)
    data.index = pd.date_range(start='01/01/2003', end='07/01/2024', freq="M").to_period('M')
    data.index = pd.PeriodIndex(data.index, freq='M').to_timestamp()
    data = data[["waarde"]]
    data.columns = ['BigBusinessInterestRate']

    return data

data = zakerenteNetherlands()
data.plot()
plt.show()
data.to_csv("output/dnb_bigbusinessinterestrates_mo.csv")

def dnb_bigbusinessOutstanding_mo():

    print("Dutch Business outstanding")
    data = pd.read_csv('data/(14-08-24)_Kernindicatoren_monetaire_statistieken_(Maand).csv')
    data.rename(columns=lambda x: x.strip(), inplace=True)
    data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    data = data[data['Instrument'] == "Zakelijke kredietverlening"]
    data = data[data['InstrumentSub'] == "Uitstaande bedragen (mln euro's)"]
    data.rename(columns = {"Uitstaande bedragen (mln euro's)": "BigBusinessOutstanding"}, inplace = True)
    data.index = pd.date_range(start='01/01/2003', end='07/01/2024', freq="M").to_period('M')
    data.index = pd.PeriodIndex(data.index, freq='M').to_timestamp()
    data = data[["waarde"]]
    data.columns = ['BigBusinessOutstanding']

    return data

data = dnb_bigbusinessOutstanding_mo()
data.plot()
plt.show()
data.to_csv("output/dnb_bigbusinessOutstanding_mo.csv")


#############################
# Savings
# https://www.dnb.nl/statistieken/data-zoeken/#/details/spaargeld-van-nederlandse-huishoudens-maand/dataset/6ef46471-d025-421e-ac01-1631a996c7c7/resource/7d127f00-6917-4e63-a163-08afd65ecb1a
#############################

def savingsNetNetherlands():
    print("savings amounts")
    data = pd.read_csv('data/(14-08-24)_Spaargeld_van_Nederlandse_huishoudens_(Maand).csv')
    data = data[data['Instrument'] == 'Totaal spaargeld ']
    data = data[data['StandStroom'] == 'Netto inleg ']
    data.index = pd.date_range(start='01/01/1998', end='07/01/2024', freq="M").to_period('M')
    data = data[['waarde']]
    data.index = pd.PeriodIndex(data.index, freq='M').to_timestamp()
    data.rename(columns={"waarde": "NetSavings"}, inplace = True)

    return data

data = savingsNetNetherlands()
data.to_csv("output/dnb_savingsnet_mo.csv")
data.plot()
plt.title('Net savings NLD January 2024')
plt.savefig("figures/dnb_savingsnet_mo.png")
plt.show()
#
# ###############################
# # Residential property prices
# # https://fred.stlouisfed.org/series/QNLN628BIS
# ###############################
#
# def housingprices():
#     print("housing prices")
#     #def residentialhousing():
#     housing = pd.read_csv("../data/residentialhousing2010index.csv")
#     housing.rename(columns = {'QNLN628BIS': "Residential_NLD_Housing_Prices"}, inplace=True)
#     housing.index = pd.date_range(start='01/01/1970', end='01/01/2024', freq="Q").to_period('Q')
#     housing.drop(columns=['DATE'], inplace=True)
#     housing.index = pd.PeriodIndex(housing.index, freq='Q').to_timestamp()
#
#     return housing
#
# data = housingprices()
# data.to_csv("../output/fed_housing_prices_qt.csv")
# # data.plot()
# # plt.title('Housing Prices Fed 3rd Quarter 2024')
# # plt.savefig("../figures/fed_housing_prices_qt.png")
# # plt.show()
#
###############################
# Interest rates
# https://ec.europa.eu/eurostat/databrowser/view/irt_st_m__custom_9247368/default/table?lang=en
# SDMX-CSV 1.0
# ###############################
from functools import reduce

def interestratesEurope(verbose = False):
    print("Interest rates outside europe")

    data = pd.read_csv('data/europeaninterestrates1.csv')

    data = data[data["int_rt"] == 'IRT_M3']
    data = data[data['geo'].isin(['EA','US', 'JP', 'UK'])]
    data = data[['geo', 'TIME_PERIOD', 'OBS_VALUE']]

    dataUS = data[data['geo'] == 'US']
    dataEA = data[data['geo'] == 'EA']
    dataUK = data[data['geo'] == 'UK']

    dfs = [dataEA, dataUS, dataUK]
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['TIME_PERIOD'], how='outer'), dfs)
    df_merged = df_merged.dropna()
    df_merged = df_merged[['TIME_PERIOD', 'OBS_VALUE_x', 'OBS_VALUE_y', 'OBS_VALUE']]
    df_merged.rename(columns = {'TIME_PERIOD': 'Date', 'OBS_VALUE_x': 'EA', 'OBS_VALUE_y': 'US', 'OBS_VALUE': 'UK'}, inplace = True)

    df_merged.index = pd.date_range(start='01/01/1990', end='04/01/2024', freq="M").to_period('M')
    df_merged = df_merged.resample('M').interpolate()
    df_merged.index = pd.PeriodIndex(df_merged.index, freq='M').to_timestamp()
    df_merged.drop(columns = ['Date'], inplace = True)

    if verbose:
        print(df_merged)
        plt.plot(df_merged)
        plt.show()

    return df_merged

data = interestratesEurope()
data.to_csv("output/euro_interestrateEurope_mo.csv")

data.plot()
plt.title('Interest Rates Eurostat December 2023')
plt.savefig("figures/euro_interestrateEurope_mo.png")
plt.show()