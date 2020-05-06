import json
from pandas.io.json import json_normalize, read_json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import statsmodels.tsa.stattools as ts
import time


import statsmodels.api as sm
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades/VolNodeTimeSeries/")
# def post_trade_analysis():
starting_date = dt.date(2019,10,1)
end_date = dt.date(2020,1,1)
long_month = [3,6,9,12]
# starting_date = dt.date(2018,7,2)
# end_date = dt.date(2019,1,1)
ExpList = {}
fileList = []
NodeVolDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("VolNodeTS") and len(filename)>25:
        filedatestr = filename[10:18]
        filedate = dt.datetime.strptime(filedatestr,"%Y%m%d").date()
        expdatestr = filename[19:27]
        expdate = dt.datetime.strptime(expdatestr,"%Y%m%d").date()

        if filedate<=end_date and filedate>=starting_date and expdate.month in long_month:
            print(filename)
            fileList.append(filename)
            if ((expdate not in ExpList.keys())):
                ExpList[expdate] = []
            if filedate not in ExpList[expdate]:
                ExpList[expdate].append(filedate)


# Load each file individually in a generator expression
a = time.perf_counter()
df2 = pd.concat(pd.read_json(f) for f in fileList)
df2.reset_index(inplace=True,drop=True)
provider = pd.DataFrame([md for md in df2.NodeVol])
provider.columns = ['NodeVol.'+col_name for col_name in provider.columns]
df3 = df2.drop(columns = ['NodeVol'])
df3 = pd.concat([df3,provider],sort=False,axis=1)
b = time.perf_counter()
print(b-a)
a = time.perf_counter()
df = pd.concat(json_normalize(json.load(open(f))) for f in fileList)
b = time.perf_counter()
print(b-a)
tmp  = pd.read_json(fileList[0])
with open(filename) as json_file:
    cur_json = json.load(json_file)
    cur_DF = json_normalize(cur_json)
    cur_DF['timestamp'] = pd.to_datetime(cur_DF['Ts'])
    cur_DF['ExpDate'] = pd.to_datetime(cur_DF['ExpDate'])
    NodeVolDF = NodeVolDF.append(cur_DF, ignore_index=True)

NodeVolDF = NodeVolDF[NodeVolDF['Maturity']>0.1]
NodeVolDF['TradeDate'] = NodeVolDF['timestamp'].dt.date
NodeVolDF['DaysLeft'] = (NodeVolDF['ExpDate'].dt.date - NodeVolDF['TradeDate']).dt.days
NodeVolDF.sort_values(by=['Ts'],ascending=True,inplace=True)
NodeVolDF.reset_index(drop=True,inplace=True)
NodeVolDF.sort_values(by=['ExpDate'],ascending=True,inplace=True)
NodeVolDF.reset_index(drop=True,inplace=True)
tmp = NodeVolDF[NodeVolDF['ExpDate']==dt.datetime(2018,9,25)]
tmp.reset_index(drop=True,inplace=True)
tmp = NodeVolDF[tmp['DaysLeft']==86]
VoV = NodeVolDF.groupby(['DaysLeft','ExpDate']).agg({
    'NodeVol.50':std,
    'DaysLeft':max,
    'ExpDate':max
})