import eurostat

data = eurostat.get_data_df('namq_10_gdp')
data = data[data["unit"] == "CLV10_MEUR"]
data = data[data["s_adj"] == "NSA"]
data = data[data['na_item'] == 'B1G']

data.to_csv(r"data/TMP_Eurostat_CLV10_NSA_ValueAdded.csv")

##################
# select needed items for analysis
##################

dt1 = data[data['geo\TIME_PERIOD'].isin(['EU27_2020','NL','DE','FR','IT','ES','BE','AT','FI','IE','PT','GR','EE','LV','LT','CZ','SK','HU','PL','SI','BG','RO','HR','CY','MT','LU'])].T
dt2 = dt1.loc["1995-Q1":, :]
dt2.columns = ['EU27_2020','NL','DE','FR','IT','ES','BE','AT','FI','IE','PT','GR','EE','LV','LT','CZ','SK','HU','PL','SI','BG','RO','HR','CY','MT','LU']
dt2.to_csv("output/european_GDP_qt.csv")