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
###############################################
#######研究interest rate 和Forward的关系#######
###############################################
# def post_trade_analysis():
starting_date = datetime.date(2019,9,26)
end_date = datetime.date(2019,9,26)

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/Forward/EXP0")
# resultDF = pd.DataFrame()
resultDF = pd.DataFrame()
def regress(data, yvar, xvar):
    Y = data[yvar]
    X = data[xvar]
    X['intercept'] = 1
    result = sm.OLS(Y, X).fit()
    return result.params

for filename in os.listdir(os.getcwd()):
    if filename.startswith("StrikeForward"):
        filedatestr = filename[13:21]
        filedate = datetime.datetime.strptime(filedatestr,"%Y%m%d").date()
        if filedate<=end_date and filedate>=starting_date:
            print(filedate)
            forward_DF = pd.DataFrame()
            forward_DF = pd.read_csv(filename)
forward_DF.columns = ['strike', 'c-p', 't', 'datestr']
forward_DF['timestamp'] = pd.to_datetime(forward_DF['datestr'])
output = forward_DF.groupby('timestamp').apply(regress, 'c-p', ['strike'])
print("regression done.")
output.rename(columns={"strike": "-ert", "intercept": "forward"}, inplace=True)
forward_DF = forward_DF.merge(output, 'left', 'timestamp')
forward_DF['r'] = np.log(forward_DF['-ert'] * -1) / (-forward_DF['t'])
forward_DF['r'].mean()
res = [[forward_DF['timestamp'][0], forward_DF['r'].mean()]]
resDF = pd.DataFrame(res, columns=['timestamp', 'r'])
resultDF= resultDF.append(resDF, ignore_index=True)

# forward_DF['ehat'] = forward_DF['c-p'] - forward_DF['forward'] -forward_DF['strike']*forward_DF['-ert']
# conciseDF = forward_DF.groupby('timestamp').first()
# conciseDF.to_csv("r0.csv")
# y = forward_DF['ehat']
# x = forward_DF[['strike']]
# x['intercept'] =1
# strikeRes = sm.OLS(y,x).fit()
# strikeRes.summary()
resultDF['date'] = resultDF['timestamp'].apply(lambda x:x.date())
resultDF.to_csv("IR.csv")