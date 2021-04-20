#%%
import csv
import os
import gzip
import numpy as np
from datetime import date, datetime
from typing import List, Tuple, Any, Iterable
ROOT = r"C:\Users\Yitong\AppData\Local\PythonProject\CryptoStudy"
os.chdir(ROOT)
#%%
def orderBookfromLine(logline : str) -> List[str]:
    res = []
    for  i in range(1,11):#iterating level 1 - 10
        ap = float(logline.split(f"A{i}=")[1].split(":")[0])
        bp = float(logline.split(f"B{i}=")[1].split(":")[0])
        av = int(logline.split(f"A{i}=")[1].split(":")[1].split(",")[0])
        bv = int(logline.split(f"B{i}=")[1].split(":")[1].split(",")[0])
        res.extend((bp,bv,ap,av))
    return res
#%%
def log2md(dateStr : str, instName : str):
    loggzfile = "20210414.log.gz"
    tardisInstName = InstIDDict.get(instName)
    respath = os.path.join(ROOT, "mdOutput",dateStr)
    if not os.path.exists(respath):
        os.makedirs(respath)
    with open (os.path.join(respath, f"{tardisInstName}_{dateStr}.csv"),'w', newline = '') as mdfile:
        mdwriter = csv.writer(mdfile)
        mdwriter.writerow(['TimeStamp','InstrumentID','LastPrice','BidPrice1','BidVolume1','AskPrice1','AskVolume1','BidPrice2','BidVolume2','AskPrice2','AskVolume2','BidPrice3','BidVolume3','AskPrice3','AskVolume3','BidPrice4','BidVolume4','AskPrice4','AskVolume4','BidPrice5','BidVolume5','AskPrice5','AskVolume5','BidPrice6','BidVolume6','AskPrice6','AskVolume6','BidPrice7','BidVolume7','AskPrice7','AskVolume7','BidPrice8','BidVolume8','AskPrice8','AskVolume8','BidPrice9','BidVolume9','AskPrice9','AskVolume9','BidPrice10','BidVolume10','AskPrice10','AskVolume10','Volume','Turnover','OpenPrice','OpenInterest','UpperLimitPrice','LowerLimitPrice','PreClosePrice','ExTime','TradingPhase'])
        with gzip.open(loggzfile, 'rt') as log:
            while True:
                curline = log.readline()
                if not curline:
                    break            
                if("MD" in curline and instName in curline):
                    logTsStr = curline.split("ETS=")[1].split(",")[0]
                    ts = datetime.strptime(logTsStr, "%H:%M:%S.%f")#13:54:09.792
                    ts = ts.replace(year=int(dateStr[0:4]), month=int(dateStr[4:6]), day=int(dateStr[6:8]))
                    mdTsStr = ts.strftime("%Y-%m-%d %H:%M:%S.%f")
                    volume = curline.split("V=")[1].split(",")[0]
                    lastprice = curline.split("L=")[1].split(",")[0]
                    orderbookList = orderBookfromLine(curline)
                    turnOver = curline.split("T=")[1].split(" ")[0]
                    row = [mdTsStr, tardisInstName, lastprice]
                    row += orderbookList
                    row += [volume, turnOver, 0, 0, 0, 0, 0, mdTsStr, -1]
                    mdwriter.writerow(row)

# %%
instList = ["BTCUSD.IPHB","BTCUSD.I1M25HB", "BTCUSDT.LPHB"]
InstIDDict = {
    "BTCUSD.IPHB":"BTC-USD",
    "BTCUSD.I1M25HB":"BTC_CQ",
    "BTCUSDT.LPHB":"BTC-USDT"
    }
for inst in instList:
    log2md("20210414", inst)

# %%
# %%
# with open("BTC_CQ_20210413") as mdfile:
#     cnt = 0
#     while True:
#         if(cnt>5):
#             break
#         curline = mdfile.readline()
#         if(not curline):
#             break
#         print(curline)
#         cnt+=1
# %%
