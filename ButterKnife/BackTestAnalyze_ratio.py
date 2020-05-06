#%%
import json
from pandas.io.json import json_normalize, read_json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import statsmodels.tsa.stattools as ts
from matplotlib.dates import bytespdate2num, num2date
import matplotlib.ticker as ticker

import statsmodels.api as sm
rootpath = "C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/"
#test ratio
paramlist = []
# paramlist.append((0.001,0.00025,0.005,4000, 0.9))
# paramlist.append((0.001,0.00025,0.005,4000, 0.7))
# paramlist.append((0.001,0.00025,0.005,4000, 0.6))
# paramlist.append((0.001,0.00025,0.005,4000, 0.5))
# paramlist.append((0.001,0.00025,0.005,4000, 0.4))
# paramlist.append((0.001,0.00025,0.005,4000, 0.3))
# #test min_closeOffset
# paramlist.append((0.001,0.00025,0.004,4000, 0.4))
# paramlist.append((0.001,0.00025,0.008,4000, 0.4))
# paramlist.append((0.001,0.00025,0.007,4000, 0.4))
# paramlist.append((0.001,0.00025,0.006,4000, 0.4))

# #vega and open threshold
# paramlist.append((0.002,0.00025,0.006,4000, 0.4))
# paramlist.append((0.001,0.00025,0.006,2000, 0.4))
# paramlist.append((0.001,0.00025,0.006,10000, 0.4))
# #vega
# paramlist.append((0.001,0.00025,0.006,20000, 0.4))
# paramlist.append((0.001,0.00025,0.006,50000, 0.4))

# #bo
# paramlist.append((0.001,0.00025,0.006,4000, 0.4, 'bo'))
# # paramlist.append((0.002,0.0005,0.015,4000, 0.4, 'bo'))

#Extrinsic
# paramlist.append((0.002,0.0005,0.015,4000, 0.4, 'Extrinsic'))
# paramlist.append((0.0005,0.0005,0.015,4000, 0.4, 'Extrinsic'))
paramlist.append((0.0005,0.0005,0.0015,4000, 0.4, 'Extrinsic'))
#%%
def LoadCostPnl(filename,monthstr):
    pnlcost = pd.read_csv(filename)
    pnlcost['Time'] = pd.to_datetime(pnlcost['Timestamp'])
    pnlcost['Expiry'] = pd.to_datetime(pnlcost['Expiry'])
    pnlcost['Date'] = pnlcost['Time'].dt.date
    pnlcost = pnlcost[['Time','Date','Expiry','Timeindex','Closedpnl','UnClosedPnL','TotalCost','TotalPnL']]    
    #pnlcost.rename(columns={"TotalPnL":"TotalPnL"+monthstr, "TotalCost":"TotalCost"+monthstr},inplace=True)
    return pnlcost

#%%
def produceBtSum(plcostDF,expstr,paramlist):
    resDict = {'Expiry':expstr}
    resDict.update({'openThreshold':paramlist[0],'posDiff':paramlist[1],'mincloseOffest':paramlist[2],'posVega':paramlist[3],'holdRatio':paramlist[4]})
    resDict.update({'Cost':plcostDF['TotalCost'].max()})
    resDict.update({'PnL':plcostDF['TotalPnL'].iloc[-1]})
    resDict.update({'Return':resDict['PnL']/resDict['Cost']})
    totalTDays = len(set(plcostDF['Date']))
    resDict.update({'AReturn':(resDict['Return']+1)**(250/totalTDays)-1})

    preDF = plcostDF.loc[plcostDF['Date']<dt.date(2020,2,3)]
    if(preDF.shape[0]!=0):
        resDict.update({'PnL_pre':preDF['TotalPnL'].iloc[-1]})
        resDict.update({'Cost_pre':preDF['TotalCost'].max()})
        resDict.update({'Return_pre':resDict['PnL_pre']/resDict['Cost_pre']})
        totalTDays_pre = len(set(preDF['Date']))
        resDict.update({'AReturn_pre':(resDict['Return_pre']+1)**(250/totalTDays_pre)-1})
    else:
        resDict.update({'PnL_pre':0})
        resDict.update({'Cost_pre':0})
        resDict.update({'Return_pre':0})
        resDict.update({'AReturn_pre':0})
    if(expstr!='01'):       
        specialDF = plcostDF.loc[(plcostDF['Date']>=dt.date(2020,2,3)) & (plcostDF['Date']<=dt.date(2020,2,7))]
        if(specialDF.shape[0]!=0):
            specialPl = specialDF['TotalPnL'].iloc[-1] - resDict['PnL_pre']
        else:
            specialPl = 0

        excDF = plcostDF.loc[(plcostDF['Date']<dt.date(2020,2,3)) | (plcostDF['Date']>dt.date(2020,2,7))]

        resDict.update({'PnL_exc':resDict['PnL'] - specialPl})
        resDict.update({'Cost_exc':excDF['TotalCost'].max()})    
        resDict.update({'Return_exc':resDict['PnL_exc']/resDict['Cost_exc']})
        totalTDays_exc = len(set(excDF['Date']))
        resDict.update({'AReturn_exc':(resDict['Return_exc']+1)**(250/totalTDays_exc)-1})
    else:
        resDict.update({'PnL_exc':resDict['PnL_pre']})
        resDict.update({'Cost_exc':resDict['Cost_pre']})
        resDict.update({'Return_exc':resDict['Return_pre']})
        resDict.update({'AReturn_exc':resDict['AReturn_pre']})
    return resDict


#%%
reslist = []
for param in paramlist:
    filepathsuffix = " ".join(str(x) for x in param)
    print("Working on "+ filepathsuffix+"...")
    # folderpath = rootpath+(filepathsuffix)
    folderpath = rootpath+(filepathsuffix)
    os.chdir(folderpath)
    plcost01 = LoadCostPnl("PnlCost_20200122_20200122.csv","01")
    reslist.append(produceBtSum(plcost01,'01',param))
    plcost02 = LoadCostPnl("PnlCost_20200226_20200220.csv","02")
    reslist.append(produceBtSum(plcost02,'02',param))
    plcost03 = LoadCostPnl("PnlCost_20200325_20200325.csv","03")
    reslist.append(produceBtSum(plcost03,'03',param))
    plcost04 = LoadCostPnl("PnlCost_20200422_20200326.csv","04")
    reslist.append(produceBtSum(plcost04,'04',param))
    plcost06 = LoadCostPnl("PnlCost_20200624_20200326.csv","06")
    reslist.append(produceBtSum(plcost06,'06',param))
    plcost09 = LoadCostPnl("PnlCost_20200923_20200326.csv","09")
    reslist.append(produceBtSum(plcost09,'09',param))
    plcost01.rename(columns={"TotalPnL":"TotalPnL"+"01", "TotalCost":"TotalCost"+"01"},inplace=True)
    plcost02.rename(columns={"TotalPnL":"TotalPnL"+"02", "TotalCost":"TotalCost"+"02"},inplace=True)
    plcost03.rename(columns={"TotalPnL":"TotalPnL"+"03", "TotalCost":"TotalCost"+"03"},inplace=True)
    plcost04.rename(columns={"TotalPnL":"TotalPnL"+"04", "TotalCost":"TotalCost"+"04"},inplace=True)
    plcost06.rename(columns={"TotalPnL":"TotalPnL"+"06", "TotalCost":"TotalCost"+"06"},inplace=True)
    plcost09.rename(columns={"TotalPnL":"TotalPnL"+"09", "TotalCost":"TotalCost"+"09"},inplace=True)
    allPlCost = plcost01.merge(plcost02,how='outer',on='Time')
    allPlCost = allPlCost.merge(plcost03,how='outer',on='Time')
    allPlCost = allPlCost.merge(plcost04,how='outer',on='Time')
    allPlCost = allPlCost.merge(plcost06,how='outer',on='Time')
    allPlCost = allPlCost.merge(plcost09,how='outer',on='Time')
    allPlCost.sort_values('Time',inplace=True)
    allPlCost = allPlCost.reset_index(drop=True)
    allPlCost.fillna(method='ffill',inplace=True)    
    allPlCost.fillna(0,inplace=True)
    allPlCost['Date'] = allPlCost['Time'].dt.date
    allPlCost['TotalCost'] = allPlCost['TotalCost01'] + allPlCost['TotalCost02'] + allPlCost['TotalCost03']  + allPlCost['TotalCost04'] + allPlCost['TotalCost06'] + allPlCost['TotalCost09']
    allPlCost['TotalPnL'] = allPlCost['TotalPnL01'] + allPlCost['TotalPnL02'] + allPlCost['TotalPnL03'] + allPlCost['TotalPnL04']+ allPlCost['TotalPnL06'] + allPlCost['TotalPnL09']
    reslist.append(produceBtSum(allPlCost,'Total',param))
    print("Done.")


#%%
sumDF = pd.DataFrame(reslist)
sumDF['Vega/VolPoint'] = sumDF['posVega'] /sumDF['posDiff']/100
sumDF = sumDF[['Expiry', 'openThreshold', 'mincloseOffest','holdRatio', 'posDiff','posVega','Vega/VolPoint','PnL','Cost','Return','AReturn','PnL_pre','Cost_pre','Return_pre','AReturn_pre','PnL_exc','Cost_exc','Return_exc','AReturn_exc']]
os.chdir(rootpath+"/Summary/")
sumDF.to_excel("Summary_Auto_v1.xlsx")


# %%
def LoadVSTrades(filename,monthstr):
    tradelist = pd.read_csv(filename)
    tradelist= tradelist.loc[tradelist['Volume']!=0]
    tradelist['openTime'] = pd.to_datetime(tradelist['openTime'])
    tradelist['closeTime'] = pd.to_datetime(tradelist['closeTime'])
    tradelist['Expiry'] = pd.to_datetime(tradelist['Expiry'])
    tradelist['ExpiryStr'] = monthstr
    tradelist = tradelist[['TotalPnl','NetPnl','TotalPnlTheory','Leg1Pnl','Leg2Pnl','HoldingMin','SHVegaCompletionRate','SZVegaCompletionRate', 'SHDeltaCompletionRate', 'SZDeltaCompletionRate','longSH','OpenExecuMin','CloseExecuMin']]    
    #pnlcost.rename(columns={"TotalPnL":"TotalPnL"+monthstr, "TotalCost":"TotalCost"+monthstr},inplace=True)
    return tradelist
def produceTradesSum(tradesDF,expstr,paramlist):
    resDict = {'Expiry':expstr}
    resDict.update({'openThreshold':paramlist[0],'posDiff':paramlist[1],'mincloseOffest':paramlist[2],'posVega':paramlist[3],'holdRatio':paramlist[4]})
    resDict.update({'TotalPnl':tradesDF['TotalPnl'].mean()})
    resDict.update({'NetPnl':tradesDF['NetPnl'].mean()})
    resDict.update({'TotalPnlTheory':tradesDF['TotalPnlTheory'].mean()})
    resDict.update({'PnlCompleteRatio':resDict['NetPnl'] / resDict['TotalPnlTheory']})
    resDict.update({'Leg1Pnl':tradesDF['Leg1Pnl'].mean()})
    resDict.update({'Leg2Pnl':tradesDF['Leg2Pnl'].mean()})
    resDict.update({'HoldingMin':tradesDF['HoldingMin'].mean()})
    resDict.update({'SHVegaCompletionRate':tradesDF['SHVegaCompletionRate'].mean()})    
    resDict.update({'SZVegaCompletionRate':tradesDF['SZVegaCompletionRate'].mean()})    
    resDict.update({'SHDeltaCompletionRate':tradesDF['SHDeltaCompletionRate'].mean()})   
    resDict.update({'SZDeltaCompletionRate':tradesDF['SZDeltaCompletionRate'].mean()})  
    resDict.update({'LongSH':tradesDF['longSH'].mean()})
    resDict.update({'Count':tradesDF.shape[0]})
    resDict.update({'OpenExecuMin':tradesDF['OpenExecuMin'].mean()})
    resDict.update({'CloseExecuMin':tradesDF['CloseExecuMin'].mean()})
    return resDict
#%%
reslist =[]
for param in paramlist:
    filepathsuffix = " ".join(str(x) for x in param)
    print("Working on "+ filepathsuffix+"...")
    # folderpath = rootpath+(filepathsuffix)
    folderpath = rootpath+(filepathsuffix)
    os.chdir(folderpath)
    trades01 = LoadVSTrades("ButterKnifeZeroTrades_20200122_20200122.csv","01")
    trades02 = LoadVSTrades("ButterKnifeZeroTrades_20200226_20200220.csv","02")
    trades03 = LoadVSTrades("ButterKnifeZeroTrades_20200325_20200325.csv","03")
    trades04 = LoadVSTrades("ButterKnifeZeroTrades_20200422_20200326.csv","03")
    trades06 = LoadVSTrades("ButterKnifeZeroTrades_20200624_20200326.csv","06")
    trades09 = LoadVSTrades("ButterKnifeZeroTrades_20200923_20200326.csv","09")
    allTrades =  trades01.append([trades02,trades03,trades04,trades06,trades09])
    reslist.append(produceTradesSum(trades01,'01',param))
    reslist.append(produceTradesSum(trades02,'02',param))
    reslist.append(produceTradesSum(trades03,'03',param))
    reslist.append(produceTradesSum(trades03,'04',param))
    reslist.append(produceTradesSum(trades06,'06',param))
    reslist.append(produceTradesSum(trades09,'09',param))
    reslist.append(produceTradesSum(allTrades,'Total',param))
    print("Done.")
#%%
sumDF = pd.DataFrame(reslist)
sumDF['Vega/VolPoint'] = sumDF['posVega'] /sumDF['posDiff']/100
sumDF = sumDF[['Expiry', 'openThreshold', 'mincloseOffest','holdRatio', 'posDiff','posVega','Vega/VolPoint','Count','LongSH','HoldingMin','NetPnl','TotalPnlTheory','PnlCompleteRatio','Leg1Pnl','Leg2Pnl','SHVegaCompletionRate','SZVegaCompletionRate','SHDeltaCompletionRate','SZDeltaCompletionRate','OpenExecuMin','CloseExecuMin']]
os.chdir(rootpath+"/Summary/")
sumDF.to_excel("Summary_Trades_v1.xlsx")


# %%
param = (0.001,0.00025,0.005,4000, 0.6)
filepathsuffix = " ".join(str(x) for x in param)
print("Working on "+ filepathsuffix+"...")
# folderpath = rootpath+(filepathsuffix)
folderpath = rootpath+(filepathsuffix)
os.chdir(folderpath)
plcost01 = LoadCostPnl("PnlCost_20200122_20200122.csv","01")
# reslist.append(produceBtSum(plcost01,'01',param))
plcost02 = LoadCostPnl("PnlCost_20200226_20200220.csv","02")
# reslist.append(produceBtSum(plcost02,'02',param))
plcost03 = LoadCostPnl("PnlCost_20200325_20200325.csv","03")
# reslist.append(produceBtSum(plcost03,'03',param))
plcost04 = LoadCostPnl("PnlCost_20200422_20200326.csv","04")
# reslist.append(produceBtSum(plcost04,'04',param))
plcost06 = LoadCostPnl("PnlCost_20200624_20200326.csv","06")
# reslist.append(produceBtSum(plcost06,'06',param))
plcost09 = LoadCostPnl("PnlCost_20200923_20200326.csv","09")
# reslist.append(produceBtSum(plcost09,'09',param))
plcost01.rename(columns={"TotalPnL":"TotalPnL"+"01", "TotalCost":"TotalCost"+"01"},inplace=True)
plcost02.rename(columns={"TotalPnL":"TotalPnL"+"02", "TotalCost":"TotalCost"+"02"},inplace=True)
plcost03.rename(columns={"TotalPnL":"TotalPnL"+"03", "TotalCost":"TotalCost"+"03"},inplace=True)
plcost04.rename(columns={"TotalPnL":"TotalPnL"+"04", "TotalCost":"TotalCost"+"04"},inplace=True)
plcost06.rename(columns={"TotalPnL":"TotalPnL"+"06", "TotalCost":"TotalCost"+"06"},inplace=True)
plcost09.rename(columns={"TotalPnL":"TotalPnL"+"09", "TotalCost":"TotalCost"+"09"},inplace=True)
allPlCost = plcost01.merge(plcost02,how='outer',on='Time')
allPlCost = allPlCost.merge(plcost03,how='outer',on='Time')
allPlCost = allPlCost.merge(plcost04,how='outer',on='Time')
allPlCost = allPlCost.merge(plcost06,how='outer',on='Time')
allPlCost = allPlCost.merge(plcost09,how='outer',on='Time')
allPlCost.sort_values('Time',inplace=True)
allPlCost = allPlCost.reset_index(drop=True)
allPlCost.fillna(method='ffill',inplace=True)
allPlCost.fillna(0,inplace=True)
allPlCost['Date'] = allPlCost['Time'].dt.date
allPlCost['TotalCost'] = allPlCost['TotalCost01'] + allPlCost['TotalCost02'] + allPlCost['TotalCost03']  + allPlCost['TotalCost04'] + allPlCost['TotalCost06'] + allPlCost['TotalCost09']
allPlCost['TotalPnL'] = allPlCost['TotalPnL01'] + allPlCost['TotalPnL02'] + allPlCost['TotalPnL03'] + allPlCost['TotalPnL04']+ allPlCost['TotalPnL06'] + allPlCost['TotalPnL09']

reslist.append(produceBtSum(allPlCost,'Total',param))
os.chdir(rootpath+"/Summary/")
allPlCost.to_excel('allplcost.xlsx')

