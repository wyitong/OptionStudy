import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
import datetime
from scipy import stats
from sklearn.linear_model import LinearRegression
from statsmodels.formula.api import ols
import statsmodels.api as sm

# def post_trade_analysis():
starting_date = datetime.date(2019,1,1)
end_date = datetime.date(2019,1,30)


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/Forward/")

forward_DF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("Forward"):
        filedatestr = filename[8:19]
        filedate = datetime.datetime.strptime(filedatestr,"%Y%m%d").date()
        if filedate<=end_date and filedate>=starting_date:
            print(filedate)
            forward_DF = forward_DF.append(pd.read_csv(filename))
filename[8:19]
forward_DF.columns = ['strike','t','f-s','s','timestamp']
forward_DF['s-k'] = forward_DF['s'] - forward_DF['strike']
forward_DF['f-s_tsmean'] =forward_DF.groupby('timestamp')['f-s'].transform('mean')
forward_DF['f-s_demean'] = forward_DF['f-s'] - forward_DF['f-s_tsmean']
forward_DF['tXs-k'] = forward_DF['t']*forward_DF['s-k']

x1 = forward_DF['t'].values
x2 = forward_DF['s-k'].values
x3 = forward_DF['tXs-k'].values
X = np.column_stack((x1,x2))
X = sm.add_constant(X)

X2 = np.column_stack((x2,x3))
X2= sm.add_constant(X2)
y = forward_DF['f-s_demean'].values

res = LinearRegression().fit(X,y)
model = sm.OLS(y,X).fit()
print(model.summary())

model2 = sm.OLS(y,X2).fit()
print(model2.summary())