import json
from pandas.io.json import json_normalize, read_json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import statsmodels.tsa.stattools as ts

import statsmodels.api as sm


def std(x): return np.nanstd(x, ddof=1)
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
allDF['VIXXSHSD600'] = allDF['AtmIVSH'].rolling(600).std()*rvscale
allDF['VIXXSZSD600'] = allDF['AtmIVSZ'].rolling(600).std()*rvscale


allDF['IVDiff_normalize'] = allDF['IVDiff'] * np.sqrt(allDF['ExpiryTimeSH'])
#3h 21600>5h 36000
allDF['IVDiff_normalize_MA3h'] = allDF.groupby(['Expiry_x'])['IVDiff_normalize'].rolling(21600).mean().reset_index()['IVDiff_normalize']


allDF['IVDiff_normalize_MA3h_diff'] = allDF['IVDiff_normalize'] -  allDF['IVDiff_normalize_MA3h']
allDF['IVDiff_normalize_MA3h_diffsd'] = allDF.groupby('Expiry_x')['IVDiff_normalize_MA3h_diff'].transform('std')
allDF['IVDiff_normalize_MA3h_diff_tstat'] = allDF['IVDiff_normalize_MA3h_diff'] / allDF['IVDiff_normalize_MA3h_diffsd']
tmpDF = allDF[np.abs(allDF['IVDiff_normalize_MA3h_diff_tstat']-1)<0.001]
tmpDF['expTimesqrt'] = np.sqrt(tmpDF['ExpiryTimeSH'])
tmpDF['normdiffdivsqrttime'] = allDF['IVDiff_normalize_MA3h_diff'] / tmpDF['expTimesqrt']

allDF['IVDiff_normalize_MA3h'] = allDF.groupby(['Expiry_x'])['IVDiff_normalize'].rolling(36000).mean().reset_index()['IVDiff_normalize']
#plt.close()
#plt.hist(allDF['IVDiff_normalize_MA3h_diff_tstat'].dropna(),bins=50 )
#plt.show()
allDF['IVDiff_normalize_MA3h_diff_tstat'].describe()
tmp = allDF[np.abs(allDF['IVDiff_normalize_MA3h_diff_tstat'])>10]
def pos(x,open,close):
    if x>open:
        return -1
    elif x<-open:
        return 1
    elif abs(x)<close:
        return 0
    else:
        return np.nan

def pos2(x,voldiffopen, voldiffclose):
    if x>voldiffopen*np.sqrt(1/12):
        return -1
    elif x<-voldiffopen*np.sqrt(1/12):
        return 1
    elif abs(x)<voldiffclose*np.sqrt(1/12):
        return 0
    else:
        return np.nan

def action(row):
    if row['lastpos']==0 and row['pos']!=0:
        return 'open'
    elif row['lastpos']!=0 and row['pos']==0:
        return 'close'
    elif row['pos']==0:
        return 'empty'
    else:
        return 'hold'


#allDF['pos'] = allDF['IVDiff_normalize_MA3h_diff_tstat'].apply(lambda x:pos(x,2,1))
allDF['pos'] = allDF['IVDiff_normalize_MA3h_diff'].apply(lambda x:pos2(x,0.002,0.001))
allDF['pos'].fillna(method='ffill',inplace=True)
allDF['lastpos'] = allDF.groupby(['Expiry_x'])['pos'].shift(1)
allDF['lastpos'].fillna(0,inplace=True)
allDF['Trade'] = allDF['pos'] - allDF['lastpos']
allDF['Trade'].fillna(0,inplace=True)
allDF['Action'] = allDF.apply(action,axis=1)

(allDF['Action']=='open').count()
(allDF['Action']=='close').count()
(allDF['Action']=='hold').count()
allDF['entrytime']=np.nan
allDF['shiv0']=np.nan
allDF['shiv1']=np.nan
allDF['sziv0']=np.nan
allDF['sziv1']=np.nan
allDF['cost']=np.nan
allDF['entervega']=np.nan
allDF.loc[allDF['Action'] == 'open','entrytime']= allDF['Timestamp']
allDF.loc[allDF['Action'] == 'open','shiv0']= allDF['AtmIVSH']
allDF.loc[allDF['Action'] == 'open','sziv0']= allDF['AtmIVSZ']
allDF.loc[allDF['Action'] == 'open','cost']= allDF['StraddleMarginSH']
allDF.loc[allDF['Action'] == 'open','entervega']= allDF['StraddleVegaSH']

allDF['entrytime'] = allDF.groupby(['Expiry_x'])['entrytime'].apply(lambda x:x.ffill())
allDF['entrytime'] = allDF['entrytime'].astype('datetime64[ns]')


allDF['shiv0'] = allDF.groupby(['Expiry_x'])['shiv0'].apply(lambda x:x.ffill())
allDF['sziv0'] = allDF.groupby(['Expiry_x'])['sziv0'].apply(lambda x:x.ffill())
allDF['cost'] = allDF.groupby(['Expiry_x'])['cost'].apply(lambda x:x.ffill())
allDF['entervega'] = allDF.groupby(['Expiry_x'])['entervega'].apply(lambda x:x.ffill())
traderecord = allDF.loc[allDF['Action'] == 'close']
traderecord = traderecord[traderecord['ExpiryTimeSH']>0.015]
traderecord['holdingtime'] = traderecord['Timestamp'] - traderecord['entrytime']
traderecord['SHIVDiff'] = - traderecord['shiv0'] + traderecord['AtmIVSH']
traderecord['SZIVDiff'] = - traderecord['sziv0'] + traderecord['AtmIVSZ']
traderecord['SHIVDiffAbs'] = np.abs(traderecord['SHIVDiff'])
traderecord['SZIVDiffAbs'] = np.abs(traderecord['SZIVDiff'])

traderecord['SZIVDiffAbs'] = - traderecord['sziv0'] + traderecord['AtmIVSZ']
traderecord['SHPnl'] = -1*traderecord['Trade']*(traderecord['SHIVDiff']) * traderecord['entervega']*1000000
traderecord['SZPnl'] = -1*traderecord['Trade']*(-traderecord['SZIVDiff'] ) * traderecord['entervega']*1000000

traderecord['SpreadPnl'] = traderecord['SHPnl'] + traderecord['SZPnl']

traderecord['SHLegRatio'] = traderecord['SHPnl'] / traderecord['SpreadPnl']
traderecord['holdingminute'] = traderecord['holdingtime'].apply(lambda x: x.total_seconds()/60)

#traderecord = traderecord[traderecord['holdingminute']>1]
#traderecord = traderecord[np.abs(traderecord['IVDiff_normalize_MA3h_diff_tstat'])<4]
traderecord.groupby(['Expiry_x'])['holdingminute'].mean()
traderecord.groupby(['Expiry_x'])['SpreadPnl'].mean()
traderecord.groupby(['Expiry_x'])['SHLegRatio'].mean()
traderecord.groupby(['Expiry_x'])['SHIVDiffAbs'].mean()
traderecord.groupby(['Expiry_x'])['SZIVDiffAbs'].mean()
traderecord.groupby(['Expiry_x'])['SHPnl'].mean()
traderecord.groupby(['Expiry_x'])['SZPnl'].mean()
traderecord.groupby(['Expiry_x'])['Action'].count()
traderecord['holdingminute'].describe()
tmp = traderecord[traderecord['SpreadPnl']<-20]
plt.close()
plt.hist(traderecord['SpreadPnl'].dropna(),bins=50 )
plt.show()
class SpreadPos():
    def __init__(self,expiry, entrytime,exittime,shiv1,shiv2,sziv1,sziv2,cost,vega):
        self.expiry = expiry
        self.entrytime = entrytime
        self.exittime = exittime
        self.shiv0 = shiv1
        self.shiv1 = shiv2
        self.sziv0= sziv1
        self.sziv1 = sziv2




allDF['IVDiff_normalize_MA3h_diff_tstat'].describe()
plt.close()
plt.hist(allDF['IVDiff_normalize_MA3h_diff_tstat'].dropna(),bins=50 )
plt.show()
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