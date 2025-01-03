import os
import pandas as pd
import functools as ft

def mo_data():

    input_path = "./output_mo_qt/"
    output_path = "./output_combined/"

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
    cols_before_removing = df_final_mo.columns

    # remove empty columns or columns with little data
    print("Number of columns before removing: ", len(df_final_mo.columns))

    df_final_mo.dropna(thresh=len(df_final_mo) - 400, axis=1, inplace=True)
    col_after_removing = df_final_mo.columns

    print("Columns removed: ", set(cols_before_removing) - set(col_after_removing))

    df_final_mo.to_csv(output_path + "a0_combinedMonthly.csv")

mo_data()

###########################################
###########################################
###########################################

def qt_data():

    input_path = "output_mo_qt/"
    output_path = "output_combined/"

    filesall = os.listdir(input_path)

    listoffiles = []
    for enum, i in enumerate(filesall):
        if "_qt" in i:
            data = pd.read_csv(input_path + i,  index_col=[0])
            data.index.name = ''
            listoffiles.append(data)

    print(listoffiles)

    df_final_qt = ft.reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how = 'outer'), listoffiles)

    df_final_qt = df_final_qt.loc['1995-01-01':, :]  ##############

    df_final_qt = df_final_qt.interpolate(limit_direction='both', limit_area='inside') ##############
    col_before_removing = df_final_qt.columns

    # remove empty columns or columns with little data
    print("Number of columns before removing: ", len(df_final_qt.columns))
    df_final_qt.dropna(thresh=len(df_final_qt) - 80, axis=1, inplace=True)
    col_after_removing = df_final_qt.columns

    print("Columns removed: ", set(col_before_removing) - set(col_after_removing))
    print("Number of columns after removing: ", len(df_final_qt.columns))

    df_final_qt.to_csv(output_path + "a0_combinedQuarterly.csv")

qt_data()



