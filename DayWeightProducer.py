import json
import os
import numpy as np
import pandas as pd
import csv

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/Forward/")
weightsource  = "DayWeight.csv"
dayweight = pd.read_csv(weightsource)
dayweight = dayweight[['day','DayVol']]
# dayweight.drop(columns=['ln_pct_chg', 'sqln_pct_chg','R_pct','close','pre_etf','M','close','open','etf','group'],inplace=True)

dayconfig = pd.read_csv('cfg.txt', sep=",", header=None)

dayconfig.columns = ["dateinput","weightinput","na"]
dayconfig['datestr'] = dayconfig['dateinput'].apply(lambda x:x[1:])
dayconfig['date'] = pd.to_datetime(dayconfig['datestr'])
dayconfig['day'] = dayconfig['date'].apply(lambda x:x.weekday())
dayconfig['weight'] = dayconfig['weightinput'].apply(lambda x:float(x[:-1]))
dayconfig.drop(columns=["dateinput","weightinput","na"],inplace=True)
dayconfig.to_csv('cfg.csv')
#divide weekend weight over two to get a avg non-trading day weight
dayweight['DayVol'][0] = dayweight['DayVol'][0] /2
#mark it for later use
dayweight['day'][0] = 5
dayweight = dayweight.append({'day':6, 'DayVol':dayweight['DayVol'][0]},ignore_index=True)



mergedf = dayconfig.merge(dayweight,left_on='day',right_on='day')
mergedf.sort_values(by='date',inplace=True)

mergedf.loc[mergedf['weight']==0,'DayVol'] = dayweight['DayVol'][0]

outputdf = mergedf
outputdf['weight'] = outputdf['DayVol'].apply(lambda x:str(x))

outputdf['datestr'] = outputdf['datestr'].apply(lambda x:'['+x)
outputdf['weightstr'] = outputdf['weight'].apply(lambda x:x[0:7]+']')
outputdf = outputdf[['datestr','weightstr']]
# outputdf.to_csv('output.txt',sep=',',header=None,index=False,quoting=csv.QUOTE_NONE,escapechar=",")
outputdf.to_csv('output.txt',sep=',',header=None,index=False,line_terminator=',\n')
mergedf.to_csv('output.csv',sep=',',header=None,index=False,line_terminator=',\n')

