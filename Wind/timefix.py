#%%
import pandas as pd
import datetime as dt
import os
import sys

import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import zlib
import iopv_study
w.start()
etfList = ["510300.SH", "159919.SZ",'510050.SH']
#%%
hourList = [9,10,11,13,14,15]

etfList = ["510300.SH", "159919.SZ",'510050.SH']
os.chdir("C:/Users/Yitong/AppData/Local/PythonProject/Wind/Old")
for etf in etfList:
    hrindex=0
    curDF = pd.read_csv(etf+"_chg.csv")
    
    curDF['date'] = pd.to_datetime(curDF['date']).dt.date
    curDF['time'] = pd.to_datetime(curDF['time']).dt.time
    curDF['timestamp'] = curDF.apply(lambda r : pd.datetime.combine(r['date'],r['time']),1)
    curDF['newtime'] = curDF['time']
    lastdate = curDF['date'].iloc[0]
    lastminute = curDF['time'].iloc[0].minute
    curhour = hourList[hrindex]
    for row in curDF.itertuples():        
        curdate = row.date
        curmin = row.time.minute
        messyhour = row.time.hour
        #if date changed, hourstarts from 9 again 
        if curdate>lastdate:
            hrindex=0
        elif curmin<lastminute:
            hrindex+=1
        curhour = hourList[hrindex]
        if(messyhour!=curhour):
            curDF.loc[row.Index, 'newtime'] = (dt.datetime.combine(dt.date.today(),row.time)+dt.timedelta(hours=curhour-messyhour)).time()
        lastdate = row.date
        lastminute = row.time.minute
    
    curDF['newtimestamp'] = curDF.apply(lambda r : pd.datetime.combine(r['date'],r['newtime']),1)
    curDF.drop(columns=['timestamp', 'time'],inplace=True)
    curDF.rename(columns={'newtimestamp':'timestamp','newtime':'time'},inplace=True)
    curDF.to_csv(etf+"_chg.csv", index=False) 


# %%
