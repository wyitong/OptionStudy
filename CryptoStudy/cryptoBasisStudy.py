#%%
import pandas as pd
import os
from typing import List
import datetime as dt
from datetime import datetime
import calendar
import ray
import matplotlib.pyplot as plt
import math
tardisSourceDir = r"X:\crypto\derivative-tickers"
firstRun = True
downSampleMin = True
#%%
ray.init()
# %%
def HuobiFuturesExp(ts : datetime, futureType ="CQ") -> datetime:
    if futureType=="CQ":
        #https://support.hbfile.net/hc/en-us/articles/360000113102-Introduction-of-Huobi-Futures
        trueExpMonth = 0
        if(ts.month%3==0):
            curFridays = FridaysofMonth(ts.year, ts.month)
            if(curFridays[-1]-ts.day<14 or (curFridays[-1]-ts.day==14 and ts.hour>=8)):
                resMonth = ts.month+3 - 12 if ts.month>=10 else ts.month+3
                resYear = ts.year+1 if ts.month>=10 else ts.year
                resDay = FridaysofMonth(resYear, resMonth)[-1]
                return datetime(resYear, resMonth, resDay,8)
            return datetime(ts.year, ts.month, curFridays[-1], 8)
        else:
            resMonth = (ts.month + (3 - ts.month%3))
            resMonth = resMonth if resMonth<=12 else resMonth-12
            resYear = ts.year
            resDay = FridaysofMonth(resYear, resMonth)[-1]
            return datetime(resYear, resMonth, resDay,8)
    if futureType=="NQ":
        ts = HuobiFuturesExp(ts,"CQ")
        resMonth = ts.month+3 - 12 if ts.month>=10 else ts.month+3
        resYear = ts.year+1 if ts.month>=10 else ts.year
        resDay = FridaysofMonth(resYear, resMonth)[-1]
        return datetime(resYear, resMonth, resDay,8)

    if futureType=="CW":
        #TODO
        return
    if futureType=="NW":        
        #TODO
        return
            
def FridaysofMonth(year : int, month : int) -> List[int]:
    resDates = []
    c = calendar.Calendar(firstweekday=calendar.SUNDAY)
    for dt in c.itermonthdates(year, month):
        if(dt.weekday()==4 and dt.month==month):
            resDates.append(dt.day)
    return resDates
#%%
# testDates = [
#     datetime(2020,9,11,15),
#     datetime(2020,9,11,16),
#     datetime(2020,10,11,16),
#     datetime(2020,12,11,15),
#     datetime(2020,12,11,16),
#     datetime(2020,12,20,16),
#     datetime(2021,3,12,15),
#     datetime(2021,4,18,16)]
# for td in testDates:
#     print(f"tDate: {td}, cqExp: {HuobiFuturesExp(td)}, nqExp: {HuobiFuturesExp(td,'NQ')}")

# %%
@ray.remote
def filePath2Df(filePath : str) -> pd.DataFrame:
    print(f"Start processing {filePath}")
    fType = "CQ"
    if("NQ" in filePath):
        fType = "NQ"
    if("CW" in filePath):
        fType = "CW"
    if("NW" in filePath):
        fType = "NW"
    curDf = pd.read_json(filePath)
    curDf['expTime'] = curDf['timestamp'].apply(lambda ts: HuobiFuturesExp(ts, fType))
    curDf['tLeft'] = curDf['expTime'] - curDf['timestamp']
    curDf['tLeftRatio'] = curDf['tLeft'].apply(lambda tL : tL.total_seconds() / (60*60*24*365))
    curDf['basis'] = curDf['lastPrice'] - curDf['indexPrice']
    curDf['basisAnnual'] = (1 +curDf['basis'] / curDf['indexPrice'])**(1/curDf['tLeftRatio'])-1
    curDf.set_index('timestamp', inplace=True)
    if(downSampleMin):
        resDf = curDf.resample('T', label='right').mean()
    else:        
        resDf = curDf.resample('H', label='right').mean()
    resDf['expTime'] = curDf.iloc[0]['expTime']
    resDf['symbol'] = curDf.iloc[0]['symbol']
    print(f"Done processing {filePath}")
    return resDf
#%%
tickerFiles = os.listdir(tardisSourceDir)
cqList = []
cqcnt = 0
nqcnt = 0
for f in tickerFiles:
    # if(cqcnt>2 and nqcnt>2):
    #     break
    if("CQ" in f):
        # if(cqcnt<=2):
            curPath = os.path.join(tardisSourceDir, f)
            cqList.append(curPath)
            cqcnt+=1
    if("NQ" in f):
        # if(nqcnt<=2):
            curPath = os.path.join(tardisSourceDir, f)
            cqList.append(curPath)
            nqcnt+=1
#%%
fileName = "totDfMin.csv" if downSampleMin else "totDf.csv"
if(firstRun):
    dfList = ray.get([filePath2Df.remote(p) for p in cqList])
    totDf = pd.concat(dfList, axis=0)
    #remove abnormal entries before saving
    totDf['llastPrice'] = totDf['lastPrice'].shift(1)
    totDf['nlastPrice'] = totDf['lastPrice'].shift(-1)
    totDf = totDf[((totDf['llastPrice'] - totDf['lastPrice']).abs()>0.001) & ((totDf['nlastPrice'] - totDf['lastPrice']).abs()>0.001)]
    totDf.drop(columns=['llastPrice', 'nlastPrice'], inplace=True)
    totDf.to_csv(fileName)
else:
    totDf = pd.read_csv(fileName)


#%%
subDf = totDf[totDf['tLeftRatio']>0.05]

#%%
plt.close()
exps = subDf.expTime.unique()
for exp in exps:
    plt.scatter(
        x=subDf[subDf['expTime']==exp]['tLeftRatio'],
        y=subDf[subDf['expTime']==exp]['basisAnnual'],
        s=0.2,label=pd.to_datetime(str(exp)).strftime("%Y%m%d"))
    
plt.title(f"Basis Term Structure")
plt.ylabel('Basis Annualized')
plt.xlabel('TLeft')
plt.legend()
plt.savefig("BasisAnnualized.png")

    
plt.close()
exps = subDf.expTime.unique()
for exp in exps:
    plt.scatter(
        x=subDf[subDf['expTime']==exp]['tLeftRatio'],
        y=subDf[subDf['expTime']==exp]['basis'],
        s=0.2,label=pd.to_datetime(str(exp)).strftime("%Y%m%d"))
    
plt.title(f"Basis Term Structure")
plt.ylabel('Basis')
plt.xlabel('TLeft')
plt.legend()
plt.savefig("Basis.png")

