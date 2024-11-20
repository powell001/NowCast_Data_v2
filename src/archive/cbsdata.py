import pandas as pd
import cbsodata
import matplotlib.pyplot as plt
import numpy as np
import functools as ft

pd.set_option('display.max_columns', 40)

###################################
# https://cbsodata.readthedocs.io/en/latest/readme_link.html

# chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.cpb.nl/sites/default/files/publicaties/download/cpb-technical-background-document-bvar-models-used-cpb.pdf
###################################

###################################
####### CBS BVAR data
###################################


##### GDP
# https://opendata.cbs.nl/statline#/CBS/nl/dataset/84087NED/table?ts=1696490590802

def macro_data_cbs(identifier, verbose = False):
    print("macro_data_cbs")

    if verbose:
        info = cbsodata.get_info(identifier)
        print(info)

        tables = pd.DataFrame(cbsodata.get_table_list())
        print(tables.head())

        data = cbsodata.get_data(identifier)
        print(data.tail())

    data = pd.DataFrame(cbsodata.get_data(identifier))
    data.to_csv("ramdata.csv")

    if verbose:
        data.to_csv("original.csv")

    data = data[data["SoortGegevens"] == 'Prijsniveau 2015, seizoengecorrigeerd']
    data = data[data['Perioden'].str.contains('kwartaal')]
    #data.to_csv("tmp101.csv")

    data.index = pd.date_range(start='01/01/1995', end='12/01/2023', freq = "Q").to_period('Q')

    gdp_total = data[['BrutoBinnenlandsProduct_2', 'Totaal_3', 'Huishoudens_9', 'Overheid_10', 'BedrijvenEnHuishoudens_12', 'Totaal_15']]

    gdp_total.columns = ['gdp_total', 'imports_goods_services', 'household_cons', 'gov_consumption', 'gpd_invest_business_households', 'exports_goods_services']

    return gdp_total

# NLD_basic_macro_data = macro_data_cbs(identifier = '84105NED')
# NLD_basic_macro_data.to_csv("NLD_basic_macroo_data.csv")

NLD_basic_macro_data = pd.read_csv("adjustedMacroEconomicData.csv", index_col="Unnamed: 0")
NLD_basic_macro_data.index = pd.date_range(start='01/01/1995', end='12/01/2023', freq="Q").to_period('Q')

def quarter_to_monthly(data: pd.DataFrame):

    ### Assumes series starts at the beginning of a year ####

    data = data.resample('M').interpolate()
    rows1 = data.shape[0]
    listofrows = list(range(0,rows1))

    k = 3
    removethese = listofrows[k::k]
    removethese = [x for x in listofrows if x not in removethese]

    for rw in removethese:
        print(rw)
        data.iloc[rw, :] = np.NaN

    return data

basic_macro_mo = quarter_to_monthly(NLD_basic_macro_data)
# print(basic_macro_qt)
basic_macro_mo.to_csv("data_qt/basic_macro_sa_qt.csv")


###############################
# CPI
###############################

def price_cbs():
    print("price_cbs")

    identifier = '83131NED'
    data = pd.DataFrame(cbsodata.get_data(identifier))
    print(data.tail())
    data.to_csv("cpi_original.csv")

    data = data[data['Bestedingscategorieen'] == '000000 Alle bestedingen']
    data = data[(data['Perioden'].str.len()) > 4]
    print(pd.date_range(start='01/01/1996', end='09/01/2023', freq="M").to_period('M'))
    data.index = pd.date_range(start='01/01/1996', end='11/01/2023', freq="M").to_period('M')

    print(data[['CPI_1', 'MaandmutatieCPI_3']])

    return(data[['CPI_1', 'MaandmutatieCPI_3']])

cpi_mo = price_cbs()
cpi_mo.to_csv("data_mo/cpi_mo.csv")

################################
# WAGES_cbs
################################

def wage_cbs():
    print("wage_cbs")
    identifier = '84163NED'

    data = pd.DataFrame(cbsodata.get_data(identifier))
    print(data.tail())
    data.to_csv("wages_original.csv")

    data = data[data['BedrijfstakkenBranchesSBI2008'] == 'A-U Alle economische activiteiten']
    data = data[(data['Perioden'].str.len()) > 4]
    data.index = pd.date_range(start='01/01/1995', end='12/01/2023', freq="Q").to_period('Q')
    data = data[['BeloningSeizoengecorrigeerd_2']]

    return(data)

wages_qt = wage_cbs()
wages_mo = quarter_to_monthly(wages_qt)
wages_qt.to_csv("data_qt/wages_qt.csv")

################################
# Consumer confidence_cbs
################################

def consumer_confidence_cbs():
    print("consumer_conf_cbs")
    identifier = '83693NED'

    data = pd.DataFrame(cbsodata.get_data(identifier))
    print(data.tail())
    data.to_csv("consumer_vertrouw.csv")

    data = data[(data['Perioden'].str.len()) > 4]
    data.index = pd.date_range(start='04/01/1986', end='11/01/2023', freq="M").to_period('M')
    data = data[['Consumentenvertrouwen_1', 'EconomischKlimaat_2', 'Koopbereidheid_3']]

    data.plot()
    plt.show()
    print(data)
    return(data)

consumer_confd_mo = consumer_confidence_cbs()
print(consumer_confd_mo)
consumer_confd_mo.to_csv("data_mo/consumer_confd_mo.csv")

################################
# Business_cbs
################################

def bankrupt_cbs():
    print("bankrupt_cbs")

    identifier = '82242NED'
    data = pd.DataFrame(cbsodata.get_data(identifier))

    data.to_csv("bankrupt_cbs.csv")

    # remove jaardata
    data = data[(data['Perioden'].str.len()) > 4]
    # remove kwarteldata
    filter = data['Perioden'].str.contains('kwartaal')
    data = data[~filter]

    data = data[data['TypeGefailleerde'] == 'Totaal rechtsvormen Nederland/buitenland']
    data.drop(columns=['ID'], inplace=True)

    data.index = pd.date_range(start='01/01/1981', end='11/01/2023', freq="M").to_period('M')

    data = data[['UitgesprokenFaillissementen_1']]
    data.columns = ['Bankruptcies']

    data.plot()
    plt.show()
    print(data)

    return(data)

bankrupt_mo = bankrupt_cbs()
bankrupt_mo.to_csv("data_mo/bankrupt_mo.csv")

def producer_confidence():
    print("producer_confidence")

    identifier = '81234eng'

    data = pd.DataFrame(cbsodata.get_data(identifier))

    data.to_csv("producerConfidence_cbs.csv")

    data = data[data['SectorBranchesSIC2008'] =='C Manufacturing']
    data.index = pd.date_range(start='01/01/1985', end='11/01/2023', freq="M").to_period('M')

    data = data[['ProducerConfidence_1', 'ExpectedActivity_2']]
    data.plot()
    plt.show()
    print(data)

    return(data)

producer_confd_mo = producer_confidence()
producer_confd_mo.to_csv("data_mo/producer_confd_mo.csv")

#############
# business utilization cbs
#############


def business_utilzation2():
    print("business_utilization2: VERY SLOW")

    identifier = '81238eng'

    data = pd.DataFrame(cbsodata.get_data(identifier))

    #data.to_csv("producer_utilization_cbs.csv")

    data = data[data['BusinessesActivitiesSBI2008'] == 'C Manufacturing']
    data = data[data['Regions'] == 'Nederland']
    data = data[['CapacityUtilisation_11']]
    data = data.dropna()
    data.to_csv("tmpxxx.csv")

    data.index = pd.date_range(start='04/01/1989', end='09/01/2023', freq="Q").to_period('Q')

    data.plot()
    plt.show()
    print(data)

    return(data)

# business_utiliz = business_utilzation2()
# business_utiliz.to_csv("business_utiliz.csv")
business_utiliz_qt = pd.read_csv("business_utiliz.csv")
business_utiliz_qt.set_index('Unnamed: 0', inplace=True)

datatmp = []
datatmp.insert(0, {'CapacityUtilisation_11': np.NaN})
business_utiliz_qt = pd.concat([pd.DataFrame(datatmp), business_utiliz_qt], ignore_index=True)

business_utiliz_qt.index = pd.date_range(start='01/01/1989', end='09/01/2023', freq="Q").to_period('Q')
print("############business_utilization: ", business_utiliz_qt)

business_utiliz_qt = quarter_to_monthly(business_utiliz_qt)
business_utiliz_qt.to_csv("data_qt/business_utiliz_qt.csv")

##############################
# Combine
##############################

dfs = [basic_macro_mo, cpi_mo, consumer_confd_mo, bankrupt_mo, producer_confd_mo, wages_mo, business_utiliz_qt]

df_final = ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how = 'outer'), dfs)
df_final['myDate'] = df_final.index
df_final.index = pd.to_datetime([f'01/{m}/{y}' for y, m in zip(df_final.index.year, df_final.index.month)])
df_final.to_csv("NLD_All_Macro_data.csv")
df_final.drop(columns = ["myDate"], inplace = True)

######################################################################
######################################################################

Macro1 = pd.read_csv("NLD_All_Macro_data.csv")
print(Macro1.head())
Macro1.set_index('Unnamed: 0', inplace=True)
print(Macro1)

# ##########################################################
#
##############################
# CPB World Trade
# https://www.cpb.nl/en/world-trade-monitor-july-2023
# trade weighted Euro Area
#############################
Euro_Area_Exports_Imports_mo = pd.read_csv("Euro_Area_Exports_Imports.csv")
Euro_Area_Exports_Imports_mo.index = pd.date_range(start='01/01/2000', end='08/01/2023', freq="M").to_period('M')
print(Euro_Area_Exports_Imports_mo)
Euro_Area_Exports_Imports_mo.plot()
plt.show()
Euro_Area_Exports_Imports_mo.to_csv("data_mo/Euro_Area_Exports_Imports_mo.csv")


# ##############################
# # OECD Composite leading indicator
# # https://data.oecd.org/leadind/composite-leading-indicator-cli.htm
# ##############################
CLI_OECD_mo = pd.read_csv("CLI_OECD.csv")
CLI_OECD_mo.index = pd.date_range(start='01/01/1961', end='10/01/2023', freq="M").to_period('M')
CLI_OECD_mo.rename(columns = {"CPI_G7": "G7_Econ_Indicate", "CPI_G20": "G20_Econ_Indicate"}, inplace=True)
print(CLI_OECD_mo)

CLI_OECD_mo.plot()
plt.show()
CLI_OECD_mo.to_csv("data_mo/CLI_OECD_mo.csv")

##############################
# AEX index
# https://www.dnb.nl/statistieken/dashboards/beurs/
##############################
print('Beurs ####################### Beurs')

Beursgenoteerde_aandelen_mo = pd.read_csv("(10-10-23)_Beleggingen_van_Nederlandse_huishoudens_in_effecten_(Maand) (1).csv")
Beursgenoteerde_aandelen_mo.drop(columns=['Periode'], inplace = True)
Beursgenoteerde_aandelen_mo = Beursgenoteerde_aandelen_mo[Beursgenoteerde_aandelen_mo['Type instrument'] == 'Beursgenoteerde aandelen']
Beursgenoteerde_aandelen_mo.index = pd.date_range(start='12/01/2009', end='07/01/2023', freq="M").to_period('M')
Beursgenoteerde_aandelen_mo = Beursgenoteerde_aandelen_mo[['Waarde']]
print(Beursgenoteerde_aandelen_mo)
Beursgenoteerde_aandelen_mo.plot()
plt.title("Beurs")
plt.show()
Beursgenoteerde_aandelen_mo.columns = ['Dutch_house_stock_value']

Beursgenoteerde_aandelen_mo.to_csv("data_mo/Beursgenoteerde_aandelen_mo.csv")

#############################
# M1 must be calculated from csv (eaay)
# from DNB
# Bancaire rente op uitstaande woninghyoptheken van huishoundens in Nederland
##############################

M1 = pd.read_csv('(10-10-23)_Bijdrage_van_Nederland_aan_monetaire_aggregaten_in_het_eurogebied_(Maand) (2).csv')
print(M1)

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
print(M3_ex)
M3_ex.plot()
plt.title("M3-exclus")
plt.show()

M3_measures_mo = M3.merge(M3_ex, left_index=True, right_index=True, how = 'outer')
M3_measures_mo.plot()
plt.show()
#M3_measures_mo.to_csv("data_mo/M3_measures_mo.csv")


############################################
giral = M1[M1['StandStroom'] == 'Standen']
giral = giral[giral['Soort'] == 'M3-componenten']
giral = giral[giral['Instrument'] == 'Girale deposito\'s'][['Periode', 'waarde']]
giral.drop_duplicates(subset = 'Periode', keep="last", inplace=True)
giral.set_index('Periode', inplace=True)
print("giral: ", giral)
giral.plot()
plt.show()

M3_giral_measures_mo = M3_measures_mo.merge(giral, left_index=True, right_index=True, how = 'outer')
M3_giral_measures_mo.plot()
plt.show()

M3_giral_measures_mo.columns = ["M3_1", "M3_2", "M1"]
M3_giral_measures_mo.index.name = None
print(M3_giral_measures_mo)

M3_giral_measures_mo.index = pd.date_range(start='12/01/1982', end='09/01/2023', freq="M").to_period('M')
M3_giral_measures_mo.to_csv("tmp.csv")
M3_giral_measures_mo.to_csv("data_mo/M3_giral_measures_mo.csv")

###
# Rente
rente_mo = pd.read_csv('(10-10-23)_Bancaire_rente_op_uitstaande_woninghypotheken_van_huishoudens_in_Nederland.csv')
rente_mo.rename(columns = {'Bancaire rente op uitstaande woninghypotheken van huishoudens': "House_interest_rates"}, inplace=True)
rente_mo.drop(columns= ['Unnamed: 0'], inplace=True)
rente_mo.index = pd.date_range(start='01/01/2003', end='09/01/2023', freq="M").to_period('M')
print(rente_mo)

rente_mo.to_csv("data_mo/rente_mo.csv")

###############################
# Residential property prices
# https://fred.stlouisfed.org/series/QNLN628BIS
###############################

housing = pd.read_csv("Residential_NLD_Housing.csv")
housing.rename(columns = {'QNLN628BIS': "Residential_NLD_Housing_Prices"}, inplace=True)
housing.index = pd.date_range(start='01/01/1970', end='04/01/2023', freq="Q").to_period('Q')
housing.drop(columns=['DATE'], inplace=True)
housing = housing.resample('M').interpolate()
print(housing)

housing_prices_qt = quarter_to_monthly(housing)
print(housing_prices_qt)
housing_prices_qt.to_csv("data_qt/housing_prices_qt.csv")


# ###############################
# Euro stat various interest rates
# ###############################

euro_intr_rates = pd.read_csv("European_InterestRates_Eurostat.csv")
euro_intr_rates.index = pd.date_range(start='01/01/1990', end='10/01/2023', freq="Q").to_period('Q')
print(euro_intr_rates)

euro_intr_rates_qt = quarter_to_monthly(euro_intr_rates)
print(euro_intr_rates_qt)

euro_intr_rates_qt = quarter_to_monthly(euro_intr_rates_qt)
euro_intr_rates_qt.to_csv("data_qt/euro_intr_rates_qt.csv")

print('######################################################')
dfs = [euro_intr_rates_qt, housing_prices_qt, rente_mo, CLI_OECD_mo, Euro_Area_Exports_Imports_mo, Beursgenoteerde_aandelen_mo, euro_intr_rates_qt, M3_giral_measures_mo, unemply_mo]

print(housing)
print(rente_mo)

df_final1 = ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how = 'outer'), dfs)
print(df_final1.tail(20))

df_final1['myDate'] = df_final1.index
df_final1.index = pd.to_datetime([f'01/{m}/{y}' for y, m in zip(df_final1.index.year, df_final1.index.month)])
df_final1.drop(columns = ["myDate"], inplace = True)
df_final1.index = df_final1.index.map(str)
df_final1.index = pd.to_datetime(df_final1.index)

df_final1.to_csv("df_final1.csv")

# print("###################################################")
# print("df_final1: ", df_final1)
#
# Macro1.index.name = None
# Macro1.index = pd.to_datetime(Macro1.index)
# Macro1.to_csv("Macro1.csv")

allData_NLD = df_final.merge(df_final1, left_index=True, right_index=True,  how = 'outer')
allData_NLD.to_csv("allData_NLD_100.csv")

quart_data = allData_NLD[['gdp_total']]


# def example1():
#
#     # Download metadata and search for "Toerist" in the list with tax codes
#     metadata = pd.DataFrame(cbsodata.get_meta('84120NED', 'BelastingenEnWettelijkePremies'))
#     print(metadata[metadata['Title'].str.contains('Toerist')][['Key','Title']])
#
#     # Download data about tourist tax
#     data = pd.DataFrame(cbsodata.get_data('84120NED', filters = "BelastingenEnWettelijkePremies eq 'A045081'"))
#
#     # Filter for annual figures
#     data = data[data['Perioden'].str.match("^\d{4}$")]
#
#     # Plot the time series
#     p = data.plot(x = 'Perioden',
#                   y = 'OntvangenBelastingenEnWettPremies_1',legend = False)
#     p.set_title('Tourist tax revenue')
#     p.set_ylim([0,350])
#     p.set_xlabel("")
#     p.set_ylabel("million euro")
#
#     plt.show()
#
# #example1()
#
# def opendataexample():
#
#     import pandas as pd
#     import requests
#     import pyodata
#
#
#     def get_odata(target_url):
#         data = pd.DataFrame()
#         #data = list()
#         while target_url:
#             r = requests.get(target_url).json()
#
#             x = r['value']
#             df1 = pd.DataFrame(x)
#
#             data = data.append(r['value'])
#
#             if '@odata.nextLink' in r:
#                 target_url = r['@odata.nextLink']
#             else:
#                 target_url = None
#
#         return data
#
#
#     table_url = "https://odata4.cbs.nl/CBS/83765NED"
#
#     target_url = table_url + "/Observations"
#
#     data = get_odata(target_url)
#     print(data.head())
#
