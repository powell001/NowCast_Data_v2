import pandas as pd
from sklearn import linear_model
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import Lasso, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt

def lassoreg():

    clf = linear_model.Lasso(alpha=0.1)

    data = pd.read_csv("../output2/mergedDataforAnalysis.csv", index_col=[0])
    data = data.dropna()

    Xcolnames =  data.iloc[:, 1:]

    Y = data.iloc[:, 0].values
    X = data.iloc[:, 1:].values

    print(X.shape)

    alpha=1000.0
    lasso = Lasso(alpha=alpha, fit_intercept=True, max_iter=10000)
    lasso.fit(X,Y)
    selected_features_lasso = np.flatnonzero(lasso.coef_)
    print(selected_features_lasso)

    bestcolnames = data.columns[selected_features_lasso]

    return bestcolnames

bestcolumns = lassoreg().tolist()
print(bestcolumns)
bestcolumns.append('gdp_total')
data = pd.read_csv("../output2/mergedDataforAnalysis.csv", index_col=[0])
data[bestcolumns].corr().to_csv("corr.csv")