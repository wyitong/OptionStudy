
import os
from os import path

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import json
from pandas.io.json import json_normalize

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
from datetime import datetime, date, timedelta
import sys
from scipy import stats
from BaseFunctions import *
# region inputs/constants
# startdatestring = sys.argv[1]
# enddatestring = sys.argv[2]
startdatestring = '10/24/2019'
enddatestring = '10/28/2019'
startdate = datetime.strptime(startdatestring, '%m/%d/%Y').date()
enddate = datetime.strptime(enddatestring, '%m/%d/%Y').date()
# endregion
# region vegaflow
# datestring = '10/28/2019'
def TradeFlow(date_input):
    log_pnl_filename = "LogPnlRisk_" + date_input.strftime("%Y%m%d") + ".json"
    bt_pnl_filename = "ProfitRiskSeq_" + date_input.strftime("%Y%m%d") + ".json"
    os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades")
    if not path.exists(log_pnl_filename):
        return
    with open(log_pnl_filename) as json_file:
        cur_json = json.load(json_file)
        log_DF = json_normalize(cur_json)

    log_DF['timestamp'] = pd.to_datetime(log_DF['Pnl.Timestamp'])
    log_DF = log_DF.set_index('timestamp')

    if not path.exists(bt_pnl_filename):
        return
    with open(bt_pnl_filename) as json_file:
        cur_json = json.load(json_file)
        bt_DF = json_normalize(cur_json)

    bt_DF['timestamp'] = pd.to_datetime(bt_DF['Pnl.Timestamp'])
    bt_DF = bt_DF.set_index('timestamp')

    log_DF['Vega_norm'] = log_DF['Risk.Vega'] / log_DF['Profit.Volume'][-1]
    bt_DF['Vega_norm'] = bt_DF['Risk.Vega'] / bt_DF['Profit.Volume'][-1]

    log_DF['CD_norm'] = log_DF['Risk.CashDelta'] / log_DF['Profit.Volume'][-1]
    bt_DF['CD_norm'] = bt_DF['Risk.CashDelta'] / bt_DF['Profit.Volume'][-1]

    plt.close()
    os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades")
    fig, ax1 = plt.subplots()
    color = 'tab:red'

    ax1.set_xlabel('time')
    ax1.set_ylabel('Vega/VolumeTot', color=color)
    ax1.plot(log_DF['Vega_norm'], color='deepskyblue', label='Log')
    ax1.plot(bt_DF['Vega_norm'], color='crimson', label='BackTest')

    ax1.set_title("VegaFlow " + str(date_input))
    ax1.legend(loc='lower right')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Vol', color='black')  # we already handled the x-label with ax1
    ax2.plot(log_DF['Risk.AtmVol'], color='black', label='FitVol')
    # ax2.plot(TR_DF['Risk.AtmVol'], color='gold', label = 'TRVol')
    ax2.legend(loc='upper right')
    ax2.tick_params(axis='y', labelcolor='black')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
    plt.savefig("VegaFlow_" + str(date_input).replace("-", "") + ".png")

    plt.close()
    os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades")
    fig, ax1 = plt.subplots()
    color = 'tab:red'

    ax1.set_xlabel('time')
    ax1.set_ylabel('CashDelta/VolumeTot', color=color)
    ax1.plot(log_DF['CD_norm'], color='deepskyblue', label='Log')
    ax1.plot(bt_DF['CD_norm'], color='crimson', label='BackTest')

    ax1.set_title("CashDeltaFlow " + str(date_input))
    ax1.legend(loc='lower right')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Vol', color='black')  # we already handled the x-label with ax1
    ax2.plot(log_DF['Risk.Spot'], color='black', label='SpotPrice')
    # ax2.plot(TR_DF['Risk.AtmVol'], color='gold', label = 'TRVol')
    ax2.legend(loc='upper right')
    ax2.tick_params(axis='y', labelcolor='black')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
    plt.savefig("CashDeltaFlow_" + str(date_input).replace("-", "") + ".png")
    return


for singledate in daterange(startdate, enddate):
    TradeFlow(singledate)


# endregion

# region PL analysis

def ptr_prepare2(date_input):
    log_ptr_filename = "LogPTR_" + date_input.strftime("%Y%m%d") + ".json"
    bt_ptr_filename = "PTR_" + date_input.strftime("%Y%m%d") + ".json"
    os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades")

    if not path.exists(bt_ptr_filename):
        return pd.DataFrame(), pd.DataFrame()
    with open(bt_ptr_filename) as json_file:
        cur_json = json.load(json_file)
        ptaDF = pd.DataFrame.from_dict(cur_json)

    if not path.exists(log_ptr_filename):
        return pd.DataFrame(), pd.DataFrame()
    with open(log_ptr_filename) as json_file:
        cur_json = json.load(json_file)
        logptaDF = pd.DataFrame.from_dict(cur_json)

    for i in range(len(studypoint)):
        cur_str = str(studypoint[i])
        ptaDF[('dpl' + cur_str)] = ptaDF['DeltaPL2'].apply(lambda x: (float(x[i])))
        ptaDF[('vpl' + cur_str)] = ptaDF['VegaPL2'].apply(lambda x: (float(x[i])))
        ptaDF[('pl' + cur_str)] = ptaDF['TotPL'].apply(lambda x: (float(x[i])))
        logptaDF[('dpl' + cur_str)] = logptaDF['DeltaPL2'].apply(lambda x: (float(x[i])))
        logptaDF[('vpl' + cur_str)] = logptaDF['VegaPL2'].apply(lambda x: (float(x[i])))
        logptaDF[('pl' + cur_str)] = logptaDF['TotPL'].apply(lambda x: (float(x[i])))
    ptaDF['absDelta'] = abs(ptaDF['Delta'])
    ptaDF.drop(['DeltaPL', 'VegaPL', 'TotPL'], axis=1, inplace=True)
    logptaDF['absDelta'] = abs(ptaDF['Delta'])
    logptaDF.drop(['DeltaPL', 'VegaPL', 'TotPL'], axis=1, inplace=True)
    print(str(date_input) + " ptr loaded.")
    return ptaDF, logptaDF


ptaDF = pd.DataFrame()
logptaDF = pd.DataFrame()
for singledate in daterange(startdate, enddate):
    # cur_ptaDF , cur_logptaDF = ptr_prepare(singledate)
    cur_ptaDF, cur_logptaDF = ptr_prepare2(singledate)
    ptaDF = ptaDF.append(cur_ptaDF, ignore_index=True)
    logptaDF = logptaDF.append(cur_logptaDF, ignore_index=True)

volumefunc(ptaDF, logptaDF,"Backtest","Log")
for i in studypoint:
    pl_analysis(ptaDF, logptaDF,'Backtest','Log', i)


def pl_distribution(inputDF):
    exp_DF = expand_volume(inputDF)
    bins = np.linspace(exp_DF['pl120'].min(), exp_DF['pl120'].max(), 10)
    plt.close()
    # bins = np.linspace(0, 1, 12)
    plt.hist(logptaDF[(logptaDF['absDelta'] > 0.6)]['pl120'], bins, label=['PL120'], rwidth=0.7,
             density=True)
    plt.xlabel('PL120')
    plt.ylabel('Density')
    plt.title('PL120 Distribution')
    plt.legend(loc='upper right')
    plt.show()
    plt.savefig('PL120 Distribution')

pl_distribution(logptaDF)
pl_distribution(ptaDF)

# endregion
