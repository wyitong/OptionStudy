#%%
from WindPy import w
import pandas as pd
import datetime as dt
import os
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import zlib
w.start()
etfList = ["510300.SH", "510050.SH", "159919.SZ"]


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/PythonProject/Wind/tmp")
todaystr = dt.datetime.today().strftime(format="%Y-%m-%d")
def windDownloadIOPV(windObj, etfName):
    res = windObj.wst(etfName, "iopv", "2020-01-02 09:00:00", todaystr+" 15:00:00", "")
    timeseries = res.Times
    iopv = res.Data[0]
    iopvDF = pd.DataFrame({'timestamp':timeseries, 'iopv':iopv})
    iopvDF.to_csv(etfName+".csv", index=False)
    return iopvDF
#%%
iopvDFList = {}
for etfname in etfList:
    iopvDFList[etfname] = windDownloadIOPV(w,etfname)

iopvChgList = {}
for etfname in iopvDFList:
    iopvDF = iopvDFList[etfname]
    iopvDF['time'] = iopvDF['timestamp'].dt.time
    iopvDF['date'] = iopvDF['timestamp'].dt.date
    iopvDF['iopv_lag'] = iopvDF.groupby(['date'])['iopv'].shift(1)
    iopvChg = iopvDF[iopvDF['iopv']!=iopvDF['iopv_lag']]
    iopvChg.to_csv(etfname+"_chg.csv", index=False)    
    iopvChgList[etfname] = iopvChg
#%%
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/PythonProject/Wind/0417-0428")
iopvSavedList = {}
for etfname in etfList:
    iopvSavedList[etfname] = pd.read_csv(etfname+"_chg.csv")
    # iopvSavedList[etfname]['timestamp'] = pd.to_datetime(iopvSavedList[etfname]['timestamp'])
    iopvSavedList[etfname]['date'] = pd.to_datetime(iopvSavedList[etfname]['date']).dt.date
    iopvSavedList[etfname]['time'] = pd.to_datetime(iopvSavedList[etfname]['time']).dt.time
    iopvSavedList[etfname]['timestamp'] = iopvSavedList[etfname].apply(lambda r : pd.datetime.combine(r['date'],r['time']),1)
#%%
for etfname in etfList:
    lastts = iopvSavedList[etfname]['timestamp'].max()
    iopvSavedList[etfname] = pd.concat([iopvSavedList[etfname], iopvChgList[etfname][iopvChgList[etfname]['timestamp']>lastts]]])
#%%
iopvDFSavedList = {}
for etfname in etfList:
    iopvDFSavedList[etfname] = pd.read_csv(etfname+".csv")
    iopvDFSavedList[etfname]['timestamp'] = pd.to_datetime(iopvDFSavedList[etfname]['timestamp'])


# %%
