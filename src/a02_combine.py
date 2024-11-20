import os
import pandas as pd
import functools as ft


input_path = "output_mo_qt/"
output_path = "output_mo/combined_mo_data/"

filesall = os.listdir(input_path)

listoffiles = []
for enum, i in enumerate(filesall):
    if "_mo" in i:
        data = pd.read_csv(input_path + i,  index_col=[0])
        data.index.name = ''
        listoffiles.append(data)

print(listoffiles)

df_final_mo = ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how = 'outer'), listoffiles)

df_final_mo = df_final_mo.loc['1995-01-01':, :]  ##############

df_final_mo = df_final_mo.interpolate(limit_direction='both', limit_area='inside') ##############

df_final_mo.interpolate(method='linear', limit_direction='forward', axis=0)

df_final_mo.to_csv(output_path + "a0_combinedMonthly.csv")

###########################################
###########################################
###########################################

# listoffiles = []
# for enum, i in enumerate(filesall):
#     if "_qt" in i:
#         data = pd.read_csv("output/" + i,  index_col=[0])
#         data.index.name = ''
#         listoffiles.append(data)

# print(listoffiles)

# df_final_qt = ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how = 'outer'), listoffiles)

# df_final_qt = df_final_qt.loc['1995-01-01':, :]  ##############

# df_final_qt = df_final_qt.interpolate(limit_direction='both', limit_area='inside') ##############

# df_final_qt.to_csv("output_combined/a0_combinedQuarterly.csv")

