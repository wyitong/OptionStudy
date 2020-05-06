import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
import datetime as dt
from scipy import stats
from sklearn.linear_model import LinearRegression
from statsmodels.formula.api import ols
import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.ar_model import ar_select_order
# def post_trade_analysis():
starting_date = dt.date(2019,10,1)
end_date = dt.date(2020,1,31)


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/Forward/")

forward_DF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("Forward") and len(filename)==20:
        filedatestr = filename[8:16]
        filedate = dt.datetime.strptime(filedatestr,"%Y%m%d").date()
        if filedate<=end_date and filedate>=starting_date:
            print(filedate)
            forward_DF = forward_DF.append(pd.read_csv(filename))
forward_DF_raw = forward_DF
forward_DF['Time']  = pd.to_datetime(forward_DF['Time'],infer_datetime_format=True)
forward_DF['date'] = forward_DF['Time'].dt.date
forward_DF['TickBo'] = forward_DF['Forward'] - forward_DF['Underlying']
forward_DF['DTickBo'] = forward_DF['TickBo'] - forward_DF.groupby(['date'])['TickBo'].shift(1)

forward_DF.drop(columns={'Item1','Item2','Item3','Item4','Item5','Item6'},inplace=True)

forward_DF['Forwardlag1'] = forward_DF.groupby(['date'])['Forward'].shift(1)
forward_DF['Underlyinglag1'] = forward_DF.groupby(['date'])['Underlying'].shift(1)
forward_DF['ForwardTick1'] = (forward_DF['Forward'] - forward_DF['Forwardlag1'])
forward_DF['UnderlyingTick1'] = (forward_DF['Underlying'] - forward_DF['Underlyinglag1'])
forward_DF['UnderlyingTick2'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(1)
forward_DF['UnderlyingTick3'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(2)
forward_DF['UnderlyingTick4'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(3)
forward_DF['UnderlyingTick5'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(4)
forward_DF['UnderlyingTick6'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(5)
forward_DF['UnderlyingTick7'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(6)
forward_DF['UnderlyingTick8'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(7)
forward_DF['UnderlyingTick9'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(8)
forward_DF['UnderlyingTick10'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(9)
forward_DF['UnderlyingTick11'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(10)
forward_DF['UnderlyingTick12'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(11)
forward_DF['UnderlyingTick13'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(12)
forward_DF['UnderlyingTick14'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(13)
forward_DF['UnderlyingTick15'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(14)
forward_DF['UnderlyingTick16'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(15)
forward_DF['UnderlyingTick17'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(16)
forward_DF['UnderlyingTick18'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(17)
forward_DF['UnderlyingTick19'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(18)
forward_DF['UnderlyingTick20'] = forward_DF.groupby(['date'])['UnderlyingTick1'].shift(18)
forward_DF = forward_DF.dropna()


X1 = np.column_stack((forward_DF['UnderlyingTick1'],
                      forward_DF['UnderlyingTick2'],
                      forward_DF['UnderlyingTick3'],
                      forward_DF['UnderlyingTick4'],
                      forward_DF['UnderlyingTick5'],
                      forward_DF['UnderlyingTick6'],
                      forward_DF['UnderlyingTick7'],
                      forward_DF['UnderlyingTick8'],
                      forward_DF['UnderlyingTick9'],
                      forward_DF['UnderlyingTick10'],
                      forward_DF['UnderlyingTick11'],
                      forward_DF['UnderlyingTick12'],
                      forward_DF['UnderlyingTick13'],
                      forward_DF['UnderlyingTick14'],
                      forward_DF['UnderlyingTick15'],
                      forward_DF['UnderlyingTick16'],
                      forward_DF['UnderlyingTick17'],
                      forward_DF['UnderlyingTick18'],
                      forward_DF['UnderlyingTick19'],
                      forward_DF['UnderlyingTick20']))

X1 = np.column_stack((forward_DF['UnderlyingTick1'],
                      forward_DF['UnderlyingTick2'],
                      forward_DF['UnderlyingTick3'],
                      forward_DF['UnderlyingTick4'],
                      forward_DF['UnderlyingTick5'],
                      forward_DF['UnderlyingTick6'],
                      forward_DF['UnderlyingTick7'],))
X1= sm.add_constant(X1)
y1 = forward_DF['ForwardTick1'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())
forward_DF['ForwardTick1_OLS_Residual'] = model.resid
forward_DF['DBO_OLS_Residual'] = forward_DF['ForwardTick1_OLS_Residual'] - forward_DF['UnderlyingTick1']
forward_DF['MABo'] = forward_DF.groupby(['date'])['TickBo'].rolling(60).mean().reset_index()['TickBo']

forward_DF['MABoF25'] = forward_DF.groupby(['date'])['MABo'].shift(-25) -forward_DF['MABo']
X1 = forward_DF['ForwardTick1_OLS_Residual'].values

X1= sm.add_constant(X1)
y1 = forward_DF['MABoF25'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())

X1 = (forward_DF['ForwardTick1'] - forward_DF['UnderlyingTick1']).values
X1 = sm.add_constant(X1)
y1 = forward_DF['MABoF25'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())

plt.close()
plt.scatter(forward_DF['UnderlyingTick1'],forward_DF['UnderlyingTick3'])
plt.show()
corr, _ = stats.pearsonr(forward_DF['ForwardTick1'], forward_DF['UnderlyingTick3'])
corr, _ = stats.pearsonr(forward_DF['UnderlyingTick2'], forward_DF['UnderlyingTick1'])
corr, _ = stats.pearsonr(forward_DF['UnderlyingTick3'], forward_DF['UnderlyingTick1'])
plt.close()
sm.graphics.tsa.plot_acf(forward_DF['ForwardTick1'],lags=5)
plt.show()
plt.close()
sm.graphics.tsa.plot_acf(forward_DF['ForwardTick1'],None,forward_DF['Underlyinglag1'])
plt.show()

mod01 = ARMA(forward_DF['ForwardTick1'],(0,20),forward_DF['UnderlyingTick1'],None,None,missing='drop').fit()
mod01.summary()


forward_DF['RFor1'] = forward_DF['Forward'] / forward_DF['Forwardlag1'] -1
forward_DF['RUnd1'] = forward_DF['Underlying'] / forward_DF['Underlyinglag1'] -1
#forward_DF['ForRatio'] = np.log(np.abs(forward_DF['RFor1'] / forward_DF['RUnd1']))

forward_DF['ForRatio'] = np.abs(forward_DF['RFor1']) / (np.abs(forward_DF['RFor1'])+ np.abs(forward_DF['RUnd1']))
forward_DF['FutRatio'] = np.abs(forward_DF['RUnd1']) / (np.abs(forward_DF['RFor1'])+ np.abs(forward_DF['RUnd1']))


forward_DF['ForRatio'] = forward_DF['ForwardTick1']*np.abs(forward_DF['RFor1']) / (np.abs(forward_DF['RFor1'])+ np.abs(forward_DF['RUnd1']))
forward_DF['FutRatio'] = forward_DF['ForwardTick1']*np.abs(forward_DF['RUnd1']) / (np.abs(forward_DF['RFor1'])+ np.abs(forward_DF['RUnd1']))

forward_DF['ForDBo'] = forward_DF['DTickBo']* np.abs(forward_DF['RFor1']) / (np.abs(forward_DF['RFor1'])+ np.abs(forward_DF['RUnd1']))
forward_DF['FutDBo'] = forward_DF['DTickBo']* np.abs(forward_DF['RUnd1']) / (np.abs(forward_DF['RFor1'])+ np.abs(forward_DF['RUnd1']))



forward_DF['ForRatio60sum'] = forward_DF.groupby(['date'])['ForRatio'].shift(1).rolling(window=60).sum()
forward_DF['FutRatio60sum'] = forward_DF.groupby(['date'])['FutRatio'].shift(1).rolling(window=60).sum()
forward_DF['ForRatio120sum'] = forward_DF.groupby(['date'])['ForRatio'].shift(1).rolling(window=120).sum()
forward_DF['FutRatio120sum'] = forward_DF.groupby(['date'])['FutRatio'].shift(1).rolling(window=120).sum()
forward_DF['ForRatio180sum'] = forward_DF.groupby(['date'])['ForRatio'].shift(1).rolling(window=180).sum()
forward_DF['FutRatio180sum'] = forward_DF.groupby(['date'])['FutRatio'].shift(1).rolling(window=180).sum()


forward_DF['ForRatio15'] = forward_DF.groupby(['date'])['ForRatio'].shift(15).rolling(window=60).sum()
forward_DF['FutRatio15'] = forward_DF.groupby(['date'])['FutRatio'].shift(15).rolling(window=60).sum()
forward_DF['ForRatio30'] = forward_DF.groupby(['date'])['ForRatio'].shift(30).rolling(window=60).sum()
forward_DF['FutRatio30'] = forward_DF.groupby(['date'])['FutRatio'].shift(30).rolling(window=60).sum()
forward_DF['ForRatio60'] = forward_DF.groupby(['date'])['ForRatio'].shift(60).rolling(window=60).sum()
forward_DF['FutRatio60'] = forward_DF.groupby(['date'])['FutRatio'].shift(60).rolling(window=60).sum()
forward_DF['ForRatio120'] = forward_DF.groupby(['date'])['ForRatio'].shift(120).rolling(window=60).sum()
forward_DF['FutRatio120'] = forward_DF.groupby(['date'])['FutRatio'].shift(120).rolling(window=60).sum()
forward_DF['ForRatio180'] = forward_DF.groupby(['date'])['ForRatio'].shift(180)
forward_DF['FutRatio180'] = forward_DF.groupby(['date'])['FutRatio'].shift(180)

forward_DF['ForDBo15'] = forward_DF.groupby(['date'])['ForDBo'].shift(15)
forward_DF['FutDBo15'] = forward_DF.groupby(['date'])['FutDBo'].shift(15)
forward_DF['ForDBo30'] = forward_DF.groupby(['date'])['ForDBo'].shift(30)
forward_DF['FutDBo30'] = forward_DF.groupby(['date'])['FutDBo'].shift(30)

forward_DF['TickBo60'] =  forward_DF.groupby(['date'])['TickBo'].shift(60)
forward_DF['TickBo120'] =  forward_DF.groupby(['date'])['TickBo'].shift(120)
forward_DF['TickBo180'] =  forward_DF.groupby(['date'])['TickBo'].shift(180)
forward_DF['DTickBO60'] = (forward_DF['TickBo'] - forward_DF['TickBo60'])
forward_DF['DTickBO120'] = (forward_DF['TickBo'] - forward_DF['TickBo120'])
forward_DF['DTickBO180'] = (forward_DF['TickBo'] - forward_DF['TickBo180'])
forward_DF['MABo'] = forward_DF.groupby(['date'])['TickBo'].rolling(60).mean().reset_index()['TickBo']

forward_DF['TickBo60'] =  forward_DF.groupby(['date'])['TickBo'].shift(60)
forward_DF['TickBo120'] =  forward_DF.groupby(['date'])['TickBo'].shift(120)
forward_DF['TickBo180'] =  forward_DF.groupby(['date'])['TickBo'].shift(180)

forward_DF['MABo15'] = forward_DF.groupby(['date'])['MABo'].shift(15)
forward_DF['MABo30'] = forward_DF.groupby(['date'])['MABo'].shift(30)
forward_DF['MABo60'] = forward_DF.groupby(['date'])['MABo'].shift(60)
forward_DF['MABo120'] = forward_DF.groupby(['date'])['MABo'].shift(120)
forward_DF['MABo180'] = forward_DF.groupby(['date'])['MABo'].shift(180)
forward_DF['DMABo15'] = (forward_DF['MABo'] - forward_DF['MABo15'])
forward_DF['DMABo30'] = (forward_DF['MABo'] - forward_DF['MABo30'])
forward_DF['DMABo60'] = (forward_DF['MABo'] - forward_DF['MABo60'])
forward_DF['DMABo120'] = (forward_DF['MABo'] - forward_DF['MABo120'])
forward_DF['DMABo180'] = (forward_DF['MABo'] - forward_DF['MABo180'])


forratio15 = forward_DF['ForRatio15'].values
futratio15 = forward_DF['FutRatio15'].values
forratio30 = forward_DF['ForRatio30'].values
futratio30 = forward_DF['FutRatio30'].values
forratio60 = forward_DF['ForRatio60'].values
futratio60 = forward_DF['FutRatio60'].values
forratio120 = forward_DF['ForRatio120'].values
futratio120 = forward_DF['FutRatio120'].values
forratio180 = forward_DF['ForRatio180'].values
futratio180 = forward_DF['FutRatio180'].values



X1 = np.column_stack((forward_DF['ForDBo30'].values, forward_DF['FutDBo30'].values))
X1= sm.add_constant(X1)
y1 = forward_DF['DMABo60'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())

X1 = np.column_stack((forratio120,futratio120))
X1= sm.add_constant(X1)
y1 = forward_DF['DMABo120'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())


X1 = np.column_stack((forratio120,futratio120))
X1= sm.add_constant(X1)
y1 = forward_DF['MABo120'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())


x1 = forward_DF['ForRatio120sum'].values
x2 = forward_DF['FutRatio120sum'].values
X1 = np.column_stack((x1,x2))
X1= sm.add_constant(X1)
y1 = forward_DF['DTickBO120'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())


x1 = forward_DF['ForRatio60sum'].values
x2 = forward_DF['FutRatio60sum'].values
X1 = np.column_stack((x1,x2))
X1= sm.add_constant(X1)
y1 = forward_DF['DTickBO60'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())

x1 = forward_DF['ForRatio180sum'].values
x2 = forward_DF['FutRatio180sum'].values
X1 = np.column_stack((x1,x2))
X2= sm.add_constant(X1)
y2 = forward_DF['DTickBO180'].values
model = sm.OLS(y2,X2,missing='drop').fit()
print(model.summary())


x1 = forward_DF['ForRatio60sum'].values
x2 = forward_DF['FutRatio60sum'].values
X1= sm.add_constant(x1)
y1 = forward_DF['DTickBO60'].values
model = sm.OLS(y1,X1,missing='drop').fit()
print(model.summary())

tmp = pd.DataFrame()
tmp['a'] = range(1,1000)
tmp['ma'] =tmp['a'].rolling(60).mean()
tmp['ma2'] =tmp['a'].shift(10).rolling(60).mean()