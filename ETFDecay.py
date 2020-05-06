import json
import os
import numpy as np
import pandas as pd
import datetime


os.chdir("C:/Users/Yitong/Desktop/常用/MinuteLevelETF")

starting_date = datetime.date(2019,1,1)
end_date = datetime.date(2019,10,20)

etf_df = pd.DataFrame()
datelist = []
for filename in os.listdir(os.getcwd()):
    if filename.startswith("50ETF") and filename.endswith("csv"):
            print(filename)

            etf_df =etf_df.append(pd.read_csv(filename),ignore_index=True)

etf_df.rename(columns={'open':'etf'},inplace=True)
# monday=0
etf_df['time'] = pd.to_datetime(etf_df['time'])
etf_df['date'] = etf_df['time'].apply(lambda x: x.date())
etf_df['day'] = etf_df['time'].apply(lambda x: x.weekday())
etf_df['time_hm'] = etf_df['time'].apply(lambda x: x.time())

etf_df['open'] = np.where(etf_df['time_hm'] == datetime.time(9, 30, 00), 1, 0)
etf_df['M'] = np.where(etf_df['day'] == 0, 1, 0)
etf_df['close'] = np.where(etf_df['time_hm'] >= datetime.time(14, 56, 50), 2, 0)
# region week-day-night part
# etf_df = etf_df[etf_df['date']<=end_date]
etf_df = etf_df[etf_df['date']>=starting_date]



etf_df['time_group'] = (etf_df['M'] * etf_df['open']) + etf_df['close']

etf_df = etf_df[etf_df['time_group'] != 0]
etf_df = etf_df.groupby(['date','time_group']).last()


etf_df['pre_etf'] = etf_df['etf'].shift(1)
etf_df = etf_df.iloc[1:]
etf_df['ln_pct_chg'] = np.log(etf_df['etf']/etf_df['pre_etf'])
etf_df['sqln_pct_chg'] = (etf_df['ln_pct_chg']*1000)**2

etf_df['group'] = etf_df['day']*10 + etf_df['close']+ etf_df['open']

print('check')
weekDF = etf_df.groupby(['group']).mean()
weekDF['R_pct'] = weekDF['sqln_pct_chg']/weekDF['sqln_pct_chg'].sum()
weekDF['DayVol'] = weekDF['R_pct']*5

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/Forward/")
weekDF.to_csv("DayWeight.csv")