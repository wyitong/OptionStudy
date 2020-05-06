from BaseFunctions import *
from datetime import datetime, date, timedelta
import os
import json
import pandas as pd
startdatestring = '10/24/2019'
enddatestring = '10/28/2019'
startdate = datetime.strptime(startdatestring, '%m/%d/%Y').date()
enddate = datetime.strptime(enddatestring, '%m/%d/%Y').date()
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades")

date_range = daterange(startdate,enddate)
expiry_list = []
data_list = []
data_list_merged = []


for filename in os.listdir(os.getcwd()):
    if filename.startswith("PTR_"):
        filedatestr = filename[4:12]
        filedate = datetime.strptime(filedatestr, "%Y%m%d").date()
        if(filedate <=enddate) and (startdate<=filedate) and (filename.startswith("PTR_"+filedatestr+"_")):
            cur_exp = datetime.strptime(filename[13:21], "%Y%m%d").date()
            if not (cur_exp in expiry_list): expiry_list.append(cur_exp)

            print(cur_exp)
            with open(filename) as json_file:
                df = pd.DataFrame.from_dict(json.load(json_file))
                data_list.append(PTRDataframe(df,cur_exp,filedate))

for exp in expiry_list:
    curPTRobj = PTRDataframe(pd.DataFrame(),exp,datetime.now())
    for data in data_list:
        if data.expiry==exp:
            curPTRobj.df = curPTRobj.df.append(data.df,ignore_index=True)
    curPTRobj.df = dataframe_prepare(curPTRobj.df)
    data_list_merged.append(curPTRobj)

for i in studypoint:
    pl_analysis(data_list_merged[0].df,data_list_merged[1].df,"FrontMonth","2ndMonth",i)

volumefunc(data_list_merged[0].df,data_list_merged[1].df,"FrontMonth","2ndMonth")