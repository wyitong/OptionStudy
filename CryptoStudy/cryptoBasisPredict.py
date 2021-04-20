#%%
import pandas as pd
import os
from typing import List
from datetime import datetime
import calendar
import ray
import matplotlib.pyplot as plt

from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
tardisSourceDir = r"X:\crypto\derivative-tickers"
downSampleMin = True
#%%
# totDf = pd.read_csv("totDf.csv")
totDf = pd.read_csv("totDfMin.csv")
totDf.index = pd.to_datetime(totDf['timestamp'])
totDf['lastTs'] = totDf['timestamp'].shift(1)
totDf.drop(totDf[totDf['lastTs']==totDf['timestamp']].index, inplace=True)
totDf.drop(columns=['lastTs','timestamp'], inplace=True)


# %%
mul = 60 if downSampleMin else 1
subDfList = []
for exp in totDf.expTime.unique():
    subDf = totDf[totDf['expTime']==exp]
    subDf['bADiff20M'] = subDf['basisAnnual'].shift(periods=-20, freq="T") - subDf['basisAnnual']
    subDf['bADiff1H'] = subDf['basisAnnual'].shift(periods=-1, freq="H") - subDf['basisAnnual']
    subDf['bADiff1D'] = subDf['basisAnnual'].shift(periods=-1, freq="D") - subDf['basisAnnual']
    subDf['bADiff5D'] = subDf['basisAnnual'].shift(periods=-5, freq="D") - subDf['basisAnnual']
    subDf['bADiff8D'] = subDf['basisAnnual'].shift(periods=-8, freq="D") - subDf['basisAnnual']
    subDf['bADiff10D'] = subDf['basisAnnual'].shift(periods=-10, freq="D") - subDf['basisAnnual']
    subDf['bADiff12D'] = subDf['basisAnnual'].shift(periods=-12, freq="D") - subDf['basisAnnual']
    subDf['bADiff15D'] = subDf['basisAnnual'].shift(periods=-15, freq="D") - subDf['basisAnnual']
    subDf['bADiff20D'] = subDf['basisAnnual'].shift(periods=-20, freq="D") - subDf['basisAnnual']
    subDf['bAMA20M'] = subDf['basisAnnual'].rolling(20,min_periods=1).mean()
    subDf['bAMA1H'] = subDf['basisAnnual'].rolling(1*mul,min_periods=1).mean()
    subDf['bAMA4H'] = subDf['basisAnnual'].rolling(4*mul,min_periods=1).mean()
    subDf['bAMA12H'] = subDf['basisAnnual'].rolling(12*mul,min_periods=1).mean()
    subDf['bAMA1D'] = subDf['basisAnnual'].rolling(24*mul,min_periods=1).mean()
    subDf['bAMA5D'] = subDf['basisAnnual'].rolling(120*mul,min_periods=1).mean()
    subDf['bAMA10D'] = subDf['basisAnnual'].rolling(240*mul,min_periods=1).mean()
    subDf['bAMA20D'] = subDf['basisAnnual'].rolling(480*mul,min_periods=1).mean()
    subDf['bAMA40D'] = subDf['basisAnnual'].rolling(960*mul,min_periods=1).mean()
    subDfList.append(subDf)
    
allExpDf = pd.concat(subDfList, axis=0)
#%%
allExpDf.to_csv("allExp.csv")
# %%
# olsDf = allExpDf.dropna(how='any')
# X = olsDf[['bAMA20M','bAMA1H','bAMA4H','bAMA1D', 'bAMA5D', 'bAMA10D','bAMA20D','basisAnnual']]
# Y1 = olsDf['bADiff1D']
# Y5 = olsDf['bADiff5D']
# Y10 = olsDf['bADiff10D']
# Y20 = olsDf['bADiff20D']
# regr = linear_model.LinearRegression()
# regr.fit(X, Y1)
# YPred = regr.predict(X)
# r2_score(Y1,YPred)
#%%
# Create linear regression object
regr = linear_model.LinearRegression()
predPeriods = ['20M','1H', '1D', '5D', '8D','10D','12D','15D','20D']
olsDfDict = {}
olsRes = {}
for predd in predPeriods:
    yCol = f'bADiff{predd}'
    olsDf = allExpDf[[yCol,'tLeftRatio','bAMA20M','bAMA1H','bAMA4H','bAMA12H','bAMA1D', 'bAMA5D', 'bAMA10D','bAMA20D','basisAnnual','expTime']]
    olsDf.dropna(how='any',inplace=True)

    X = sm.add_constant(olsDf[['tLeftRatio','bAMA12H','bAMA5D', 'bAMA10D','bAMA20D','basisAnnual']])
    Y = olsDf[yCol]
    model = sm.OLS(Y,X)
    est = model.fit()    
    olsRes[predd] = est
    olsDf[yCol+'_pred'] = est.predict(X)
    olsDfDict[predd] = olsDf
    print(f"Predicting {predd}")
    print(est.summary())
    # trainSet = olsDf.loc[olsDf.index.day%4!=1]
    # testSet = olsDf.loc[olsDf.index.day%4==1]
    # X = sm.add_constant(olsDf[['tLeftRatio','bAMA12H','bAMA5D', 'bAMA10D','bAMA20D','basisAnnual']])
    # Y = olsDf[yCol] 

# %%
for predd in predPeriods:
    plotDf = olsDfDict[predd]
    exps = plotDf.expTime.unique()
    fig,(ax1,ax2) =  plt.subplots(2,1,sharex=True, figsize = (6,9))
    for exp in exps:
        ax1.scatter(
            x=plotDf[plotDf['expTime']==exp]['tLeftRatio'],
            y=plotDf[plotDf['expTime']==exp]['basisAnnual'],
            s=1,label=pd.to_datetime(str(exp)).strftime("%Y%m%d"))
        ax1.set_ylabel("AnnualBasis")
        ax1.grid(True)
        ax2.scatter(
            plotDf[plotDf['expTime']==exp]['tLeftRatio'],
            plotDf[plotDf['expTime']==exp][f'bADiff{predd}_pred'],
            s=1,label=pd.to_datetime(str(exp)).strftime("%Y%m%d"))
        ax2.hlines(y=0, xmin = 0, xmax = 0.6, color='r')
        ax2.set_ylabel("AnnualBasisPred")
        ax2.grid(True)
    plt.title(f"AnnualBasisPred{predd}")
    plt.xlabel('TLeft')
    ax1.legend(loc='upper right')
    fig.tight_layout()
    plt.savefig(f"pred_{predd}.png")

# %%
