from BaseFunctions import *
from datetime import datetime, date, timedelta
import os
import json
import pandas as pd
startdatestring = '9/1/2019'
enddatestring = '10/31/2019'
startdate = datetime.strptime(startdatestring, '%m/%d/%Y').date()
enddate = datetime.strptime(enddatestring, '%m/%d/%Y').date()


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades/0901-1031 NormalBias")
date_range = daterange(startdate,enddate)
expiry_list = []
data_list = []
data_list_merged = []
btDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("PTR_"):
        filedatestr = filename[4:12]
        filedate = datetime.strptime(filedatestr, "%Y%m%d").date()
        if(filedate <=enddate) and (startdate<=filedate) and (filename.startswith("PTR_"+filedatestr+"_")):
            cur_exp = datetime.strptime(filename[13:21], "%Y%m%d").date()
            if not (cur_exp in expiry_list): expiry_list.append(cur_exp)

            print(filename)
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

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades/0901-1031 PositionBias 0.050.05")
date_range = daterange(startdate,enddate)

log_list = []
log_list_merged = []
logDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("PTR_"):
        filedatestr = filename[4:12]
        filedate = datetime.strptime(filedatestr, "%Y%m%d").date()
        if(filedate <=enddate) and (startdate<=filedate) and (filename.startswith("PTR_"+filedatestr+"_")):
            cur_exp = datetime.strptime(filename[13:21], "%Y%m%d").date()
            if not (cur_exp in expiry_list): expiry_list.append(cur_exp)

            print(filename)
            with open(filename) as json_file:
                df = pd.DataFrame.from_dict(json.load(json_file))
                log_list.append(PTRDataframe(df,cur_exp,filedate))

for exp in expiry_list:
    curPTRobj = PTRDataframe(pd.DataFrame(),exp,datetime.now())
    for data in log_list:
        if data.expiry==exp:
            curPTRobj.df = curPTRobj.df.append(data.df,ignore_index=True)
    curPTRobj.df = dataframe_prepare(curPTRobj.df)
    log_list_merged.append(curPTRobj)

# log_list = []
# log_list_merged = []
#
# for filename in os.listdir(os.getcwd()):
#     if filename.startswith("LogPTR_"):
#         filedatestr = filename[7:15]
#
#         filedate = datetime.strptime(filedatestr, "%Y%m%d").date()
#         if(filedate <=enddate) and (startdate<=filedate) and (filename.startswith("LogPTR_"+filedatestr+"_")):
#             cur_exp = datetime.strptime(filename[16:24], "%Y%m%d").date()
#             if not (cur_exp in expiry_list): expiry_list.append(cur_exp)
#
#             print(filename)
#             with open(filename) as json_file:
#                 df = pd.DataFrame.from_dict(json.load(json_file))
#                 log_list.append(PTRDataframe(df,cur_exp,filedate))
#
# for exp in expiry_list:
#     curPTRobj = PTRDataframe(pd.DataFrame(),exp,datetime.now())
#     for data in log_list:
#         if data.expiry==exp:
#             curPTRobj.df = curPTRobj.df.append(data.df,ignore_index=True)
#     curPTRobj.df = dataframe_prepare(curPTRobj.df)
#     log_list_merged.append(curPTRobj)

# volumefunc(log_list_merged[0].df,log_list_merged[1].df,"FrontMonth","2ndMonth")

for obj in data_list_merged:
    if (btDF.size==0):
        btDF = obj.df
    else:
        btDF.append(obj.df,ignore_index=True)

for obj in log_list_merged:
    if (logDF.size==0):
        logDF = obj.df
    else:
        logDF.append(obj.df,ignore_index=True)


volumefunc(btDF,logDF,"OldBias","NewBias")
# volumefunc(data_list_merged[1].df,log_list_merged[1].df,"BackTest0","Log0")
for i in studypoint:
    pl_analysis(btDF,logDF,"OldBias","NewBias",i)