import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
from datetime import datetime, date, timedelta
from scipy import stats

# def post_trade_analysis():
starting_date = date(2019,6,3)
end_date = date(2019,12,13)
expiry_list = []

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades/")

plDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("ProfitRiskSeq_"):
        filedatestr = filename[14:22]
        filedate = datetime.strptime(filedatestr,"%Y%m%d").date()
        if filedate<=end_date \
                and filedate>=starting_date \
                and  (filename.startswith("ProfitRiskSeq_"+filedatestr+"_")):
            with open(filename) as json_file:
                print(filename)
                cur_exp = datetime.strptime(filename[23:31], "%Y%m%d").date()
                if not (cur_exp in expiry_list): expiry_list.append(cur_exp)

                cur_json = json.load(json_file)
                cur_DF = pd.DataFrame([cur_json[-1]['Profit']])
                cur_DF['Date'] = filedate
                cur_DF2= pd.DataFrame([cur_json[-1]['Risk']])
                cur_DF = pd.concat([cur_DF,cur_DF2],axis=1)
                cur_DF3= pd.DataFrame([cur_json[-1]['Pnl']])
                cur_DF = pd.concat([cur_DF,cur_DF3],axis=1)
                plDF = plDF.append(cur_DF,ignore_index=True)


outFileName = "PnLSummary" +str(starting_date).replace("-","") + "-" + str(end_date).replace("-","")+".xlsx"
plDF['pnltot/V'] = plDF['pnl_tot'] / plDF['Volume']
plDF['PnL/Profit'] = plDF['pnl_tot'] / plDF['NetProfit']
plDF['pnl_tot_net'] = plDF['pnl_tot'] - plDF['Fee']
plDF.drop(columns= ['Timestamp', 'timeIndex', 'timeindex'],inplace=True)
plDF.to_excel(outFileName)
