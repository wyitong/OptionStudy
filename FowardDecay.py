import json
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import datetime
import gc
from scipy import stats

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/Forward/")

starting_date = datetime.date(2019,1,1)
end_date = datetime.date(2019,10,20)

forward_DF = pd.DataFrame()
datelist = []
for filename in os.listdir(os.getcwd()):
    if filename.startswith("Forward") and filename.endswith("csv"):
        filedatestr = filename[8:16]
        filedate = datetime.datetime.strptime(filedatestr,"%Y%m%d").date()
        if filedate<=end_date and filedate>=starting_date:
            print(filedatestr)
            datelist.append(filedate)
            forward_DF =forward_DF.append(pd.read_csv(filename),ignore_index=True)

# monday=0
forward_DF.rename(
    columns={"Item1": "Underlying", "Item2": "Forward", "Item3": "AutoBO", "Item4": "TimeStr"},
    inplace=True)
forward_DF['time'] = pd.to_datetime(forward_DF['TimeStr'])
forward_DF.drop(columns=['Underlying', 'AutoBO', 'TimeStr'], inplace=True)
forward_DF['date'] = forward_DF['time'].apply(lambda x: x.date())
forward_DF['day'] = forward_DF['time'].apply(lambda x: x.weekday())
forward_DF['time_hm'] = forward_DF['time'].apply(lambda x: x.time())

forward_DF['open'] = np.where(forward_DF['time_hm'] == datetime.time(9, 29, 00), 1, 0)
forward_DF['M'] = np.where(forward_DF['day'] == 0, 1, 0)
forward_DF['close'] = np.where(forward_DF['time_hm'] >= datetime.time(14, 56, 50), 2, 0)
# region week-day-night part

forward_DF['time_group'] = (forward_DF['M'] * forward_DF['open']) + forward_DF['close']

forward_DF = forward_DF[forward_DF['time_group'] != 0]
forward_DF = forward_DF.groupby(['date','time_group']).last()


forward_DF['pre_Forward'] = forward_DF['Forward'].shift(1)
forward_DF = forward_DF.iloc[1:]
forward_DF['ln_pct_chg'] = np.log(forward_DF['Forward']/forward_DF['pre_Forward'])
forward_DF['sqln_pct_chg'] = (forward_DF['ln_pct_chg']*1000)**2

forward_DF['group'] = forward_DF['day']*10 + forward_DF['close']+ forward_DF['open']

print('check')
weekDF = forward_DF.groupby(['group']).mean()
weekDF['R_pct'] = weekDF['sqln_pct_chg']/weekDF['sqln_pct_chg'].sum()
weekDF['DayVol'] = weekDF['R_pct']*5


outFileName = "RealizedVol" +str(starting_date).replace("-","") + "-" + str(end_date).replace("-","")+".csv"
weekDF.to_csv(outFileName)