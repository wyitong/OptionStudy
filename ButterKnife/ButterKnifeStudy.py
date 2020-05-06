import json
from pandas.io.json import json_normalize, read_json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import statsmodels.tsa.stattools as ts

import statsmodels.api as sm


def std(x): return np.std(x, ddof=1)
rvscale = np.sqrt(2*60*60*4*252)

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife")
# def post_trade_analysis():
starting_date = dt.date(2020, 1, 1)
end_date = dt.date(2020, 10, 28)
underlyinglist = ['510300.SH', '159919.SZ']
#underlyinglist = ['510300.SH']
bodict = {}
expList = []
fileList = []
NodeVolDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("IVBO"):
        underlyingstr = filename[5:14]
        filedatestr = filename[15:23]
        filedate = dt.datetime.strptime(filedatestr, "%Y%m%d").date()
        expdatestr = filename[24:32]
        expdate = dt.datetime.strptime(expdatestr, "%Y%m%d").date()
        if expdate not in expList:
            expList.append(expdate)
        if filedate <= end_date and filedate >= starting_date and underlyingstr in underlyinglist:
            print(filename)
            curDF = pd.read_json(filename)
            curDF.columns =  [col_name+underlyingstr[-2:] for col_name in curDF.columns]
            curDF['Expiry'] = expdate
            curDF.rename(columns = {"Index"+underlyingstr[-2:]:"Index", "Time"+underlyingstr[-2:]:"Time"},inplace=True)
            #pd.DataFrame.from_dict(json.load(json_file))
            if (underlyingstr, expdate) not in bodict.keys():
                bodict[(underlyingstr, expdate)] =curDF
                continue
            bodict[(underlyingstr, expdate)] =bodict[(underlyingstr, expdate)].append(curDF,ignore_index=True)

comparedict = {}
allDF = pd.DataFrame()
for exp in expList:
    curDF = bodict[underlyinglist[0],exp].merge(bodict[underlyinglist[1],exp], on='Time')
    comparedict[exp] = curDF
    allDF = allDF.append(curDF,ignore_index=True)
allDF['Timestamp'] = pd.to_datetime(allDF['Time'])
allDF['second'] = allDF['Timestamp'].dt.second
allDF['minute'] = allDF['Timestamp'].dt.minute
allDF['hour'] = allDF['Timestamp'].dt.hour
allDF['time'] = allDF['Timestamp'].dt.time
allDF['date'] = allDF['Timestamp'].dt.date
allDF['LnRSH'] = np.log(allDF['ForwardSH'] /allDF['ForwardSH'].shift(1))
allDF['LnRSZ'] = np.log(allDF['ForwardSZ'] /allDF['ForwardSZ'].shift(1))

allDF['RVSH60'] = (allDF.groupby(['date'])['LnRSH'].rolling(60).std()*rvscale).reset_index()['LnRSH']
allDF['RVSZ60'] = (allDF.groupby(['date'])['LnRSZ'].rolling(60).std()*rvscale).reset_index()['LnRSZ']
allDF['RVDiff60'] = allDF['RVSH60'] - allDF['RVSZ60']



allDF['RVSH600'] = (allDF.groupby(['date'])['LnRSH'].rolling(600).std()*rvscale).reset_index()['LnRSH']
allDF['RVSZ600'] = (allDF.groupby(['date'])['LnRSZ'].rolling(600).std()*rvscale).reset_index()['LnRSZ']
allDF['RVDiff600'] = allDF['RVSH600'] - allDF['RVSZ600']


allDF['RVSH20m'] = (allDF.groupby(['date'])['LnRSH'].rolling(2400).std()*rvscale).reset_index()['LnRSH']
allDF['RVSZ20m'] = (allDF.groupby(['date'])['LnRSZ'].rolling(2400).std()*rvscale).reset_index()['LnRSZ']
allDF['RVDiff20m'] = allDF['RVSH20m'] - allDF['RVSZ20m']


allDF['BoDiff'] = allDF['AutoBoSH'] - allDF['AutoBoSZ']
allDF['rawBoDiff'] =allDF['RawBOSH'] - allDF['RawBOSZ']
allDF['IVDiff'] = allDF['AtmIVSH'] - allDF['AtmIVSZ']

X = allDF['IVDiff'].values
X = sm.add_constant(X)
Y = allDF['RVDiff20m'].values
#Y = allDF.groupby(['date'])['RVDiff20m'].shift(-2400).values
model = sm.OLS(Y,X,missing='drop').fit()
print(model.summary())

allDF.shape
allDF2 = allDF[allDF['time']<dt.time(14,55)]
allDF2 = allDF2[allDF2['time']>dt.time(9,33)]

allDF2 = allDF2[allDF2['date']!=dt.date(2020,2,3)]
allDF2 = allDF2[allDF2['date']!=dt.date(2020,2,4)]
allDF2.shape


minDF = allDF2[allDF2['second']==0]
minDF = minDF[minDF['Index_x']%2==1]
minDF.to_excel("min_withRawBo.xlsx")

fiveminDF = minDF[minDF['minute']%5==0]
fiveminDF.shape
plt.close()
for key,grp in allDF2.groupby(['Expiry_x']):
    plt.plot(grp['Time'],grp['BoDiff'],label=key)
plt.legend()
plt.show