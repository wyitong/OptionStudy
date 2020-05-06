#%%
from WindPy import w
import pandas as pd
import datetime as dt
import os
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import zlib
w.start()
etfList = ["510300.SH", "510050.SH", "159919.SZ"]


# %%
#%%
os.chdir("C:/Users/Yitong/AppData/Local/PythonProject/Wind/Old")
iopvChgList = {}
for etfname in etfList:
    iopvChgList[etfname] = pd.read_csv(etfname+"_chg.csv")
    # iopvSavedList[etfname]['timestamp'] = pd.to_datetime(iopvSavedList[etfname]['timestamp'])
    iopvChgList[etfname]['date'] = pd.to_datetime(iopvChgList[etfname]['date']).dt.date
    iopvChgList[etfname]['time'] = pd.to_datetime(iopvChgList[etfname]['time']).dt.time
    iopvChgList[etfname]['timestamp'] = iopvChgList[etfname].apply(lambda r : pd.datetime.combine(r['date'],r['time']),1)
#%%
# %%
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/SpotDetail")
expSpotList = {}
for filename in os.listdir():
    if(not filename.startswith("SpotDetail")):
        continue
    exp = filename[11:19]
    date = filename[20:28]
    if (exp in expSpotList):
        curDF = pd.read_csv(filename)
        curDF['Exp'] = exp
        curDF['Date'] = date
        expSpotList[exp] = pd.concat([expSpotList[exp],curDF], axis=0)        
        expSpotList[exp] = expSpotList[exp].reset_index(drop=True)   
    else:
        expSpotList[exp] = pd.read_csv(filename)
        expSpotList[exp]['Exp'] = exp
        expSpotList[exp]['Date'] = date


#%%
for exp in expSpotList:
   expSpotList[exp]['timestamp'] = pd.to_datetime(expSpotList[exp]['Date']+' '+expSpotList[exp]['time'], infer_datetime_format=True)
   expSpotList[exp]['date'] =  expSpotList[exp]['timestamp'].dt.date
   expSpotList[exp]['time'] =  expSpotList[exp]['timestamp'].dt.time
   expSpotList[exp].drop(columns = ['millisec','Date'], inplace=True)

#%%
#reformat the binarysearch to be row function
def binarySearch_RowOps(target, arr, l, r):
    
    timeStamp = target['timeStamp']
    return arr[binarySearch(timeStamp, arr, l, r)]
#binary search for matching iopv ts with option ts. iopv tsmatched to exact or next available ts
def binarySearch(target, arr, l, r):
    if r>l:
        mid = (l + r-1)//2
        if(arr[mid]==target):
            return mid
        elif(arr[mid]>target):
            if(arr[mid-1]<target):
                return mid
            else:
                return binarySearch(target, arr, l, mid-1)
        else:
            return binarySearch(target, arr, mid+1, r)
    elif r==l:
        return r
    else:
        return -1#%%
# %%
curExpDF = expSpotList['20200527']
iopv50 = iopvChgList["510050.SH"]

maxDate = curExpDF['date'].max()
minDate = curExpDF['date'].min()
iopv50 = iopv50[iopv50['date']<= maxDate]
iopv50 = iopv50[iopv50['date']>= minDate]
iopv50 = iopv50[iopv50['time']>= dt.time(9,30,0)]
iopv50['matchedTime'] = iopv50.apply(binarySearch_RowOps, args = (curExpDF['timestamp'].array, 0,len(curExpDF['timestamp'])-1),axis=1)

#%%
mergedDF = pd.merge(curExpDF,iopv50,'outer',left_on='timestamp', right_on='matchedTime')
#%%
mergedDF['iopvR'] = mergedDF['iopv'] / mergedDF['etf_preclose']
mergedDF['futureR'] = mergedDF['fut'] / mergedDF['fut_preclose']
mergedDF = mergedDF[mergedDF['time_x']>= dt.time(9,30,0)]

#%%
def date2color(dateinput):
    datestr = dt.datetime.strftime(dateinput, format="%Y%m%d")
    tmpnum = int(zlib.crc32(datestr.encode('utf-8')))
    r = (tmpnum%13) / 13
    g = (tmpnum%11) / 11
    b = (tmpnum%17) / 17

    color = [r,g,b]
    return color

fig, ax = plt.subplots()
ax.scatter(mergedDF['iopvR'], mergedDF['futureR'],c=mergedDF['date_x'].apply(lambda x: date2color(x)))
plt.show()
#%%
#this func regress futureR and iopvR and compare the slope/intercept
#result implies both slope/intercept would shift
def futureIopvOLS(data):
    X1 = data['futureR'].values
    X1= sm.add_constant(X1)
    y1 = data['iopvR'].values
    model = sm.OLS(y1,X1,missing='drop').fit()
    print("Date: "+dt.datetime.strftime(data['date_x'].iloc[0], format="%Y%m%d")+"Intercept: {:1f}  Slope: {:1f} R2 {:.2%}".format(model.params[0],model.params[1], model.rsquared))


mergedDF.groupby('date_x').apply(futureIopvOLS)
#%%
def fut_iopv_compare(data):
    X1 = data['fut'].values
    X1= sm.add_constant(X1)
    X2 = data['optionSpot'].values
    X2 = sm.add_constant(X2)

    y1 = data['iopv'].values
    model1 = sm.OLS(y1,X1,missing='drop').fit()
    model2= sm.OLS(y1,X2,missing='drop').fit()

    print("FutR2 {:.2%}, IopvR2 {:.2%}".format(model1.rsquared, model2.rsquared))

mergedDF.groupby('date_x').apply(fut_iopv_compare)


# %%

def gen_iopv_spottheory_ols(olsWindow, mergedDF):
    """   
    moving window ols(iopvR on futureR)
    """
    ols_windowSize = olsWindow
    fut_r_array= []
    iopv_r_array = []
    boArray = []
    intercept = 0 
    slope = 0.98
    for row in mergedDF.itertuples():
        if(not np.isnan(row.iopvR)):
            fut_r_array.append(row.futureR)
            iopv_r_array.append(row.iopvR)
            if(len(fut_r_array)>ols_windowSize*0.5):
                X1 = sm.add_constant(fut_r_array)
                Y1 = iopv_r_array
                model = sm.OLS(Y1,X1, missing='drop').fit()
                intercept = model.params[0]
                slope = model.params[1]
            while(len(fut_r_array)>ols_windowSize):
                del fut_r_array[0]
            while(len(iopv_r_array)>ols_windowSize):
                del iopv_r_array[0]
        mergedDF.loc[row.Index, 'b0'] = intercept
        mergedDF.loc[row.Index, 'b1'] = slope
    mergedDF['iopvR'+str(ols_windowSize)] = mergedDF['b0'] + mergedDF['b1'] * mergedDF['futureR']
    mergedDF['iopv'+str(ols_windowSize)] = mergedDF['iopvR'+str(ols_windowSize)] * mergedDF['etf_preclose']
    mergedDF['rawBo' + str(ols_windowSize)] = mergedDF['optionSpot'] - mergedDF['iopv'+str(ols_windowSize)]
    mergedDF['bo'+str(ols_windowSize)] = mergedDF['rawBo' + str(ols_windowSize)].rolling(120).mean()
    mergedDF['spotTheo'+ str(ols_windowSize)] = mergedDF['bo'+str(ols_windowSize)] + mergedDF['iopv'+str(ols_windowSize)]


def gen_iopv_spottheory_bo(BoWindow, mergedDF, iopvBeta = 0.97):
    """   
    moving window on bo = iopvR-futureR*slope. 
    equivalent to ols version with slope fixed

    """
    futureBoWindow = BoWindow
    slope = iopvBeta
    validDF = mergedDF[mergedDF['iopvR'].notnull()]
    validDF = validDF.reset_index(drop=True)
    validDF['rDiff'] = validDF['iopvR'] - validDF['futureR'] * slope
    validDF['rdiff_ma'+str(futureBoWindow)] = validDF['rDiff'].rolling(futureBoWindow).mean()
    validDF = validDF[['rdiff_ma'+str(futureBoWindow), 'timestamp']]
    #%%
    mergedDF2 = pd.merge(validDF,mergedDF,how='outer',on='timestamp')
    mergedDF2.sort_values(by = ['timestamp'], inplace=True)
    #%%
    mergedDF2['rdiff_ma'+str(futureBoWindow)].ffill(inplace=True)
    mergedDF2['iopvR'+str(futureBoWindow)+'bo'] = mergedDF2['futureR'] * slope + mergedDF2['rdiff_ma'+str(futureBoWindow)]
    mergedDF2['iopv'+str(futureBoWindow)+'bo'] = mergedDF2['iopvR'+str(futureBoWindow)+'bo'] * mergedDF2['etf_preclose']
    mergedDF2['rawBo' + str(futureBoWindow)+'bo'] = mergedDF2['optionSpot'] - mergedDF2['iopv'+str(futureBoWindow)+'bo']
    mergedDF2['bo'+str(futureBoWindow)+'bo'] = mergedDF2['rawBo' + str(futureBoWindow)+'bo'].rolling(120).mean()
    mergedDF2['spotTheo'+ str(futureBoWindow)+'bo'] = mergedDF2['bo'+str(futureBoWindow)+'bo'] + mergedDF2['iopv'+str(futureBoWindow)+'bo']
    return mergedDF2
#%%
#
def gen_PredictionGraph(olsWindow, mergedDF,studylag,returnlag=10,method=""):
    """ 
    Summary line. 
  
    compare original Bo based spot prediction vs iopv based spot prediction
  
    Parameters: 
    olsWindow (int): window used in gen spotPredict
    studylag (int): how lagged signal
    returnlag (int): prediction timeframe to compare
  
    Returns: 
    int: Description of return value 
  
    """
    suffix = str(olsWindow)+method
    mergedDFshort = mergedDF[mergedDF['date_x']>dt.datetime(2020,4,17).date()]
    mergedDFshort = mergedDFshort[mergedDFshort['date_x']!=dt.datetime(2020,4,24).date()]
    
    mergedDFshort['spotTheoR'] = mergedDFshort['spotTheo'] / mergedDFshort['spotTheo'].shift(returnlag)
    mergedDFshort['spotTheoR_lag'] = mergedDFshort['spotTheoR'].shift(studylag)
    mergedDFshort['spotTheoR_iopv'] = mergedDFshort['spotTheo'+ suffix] / mergedDFshort['spotTheo'+ suffix].shift(returnlag)
    mergedDFshort['spotTheoR_iopv_lag'] = mergedDFshort['spotTheoR_iopv'].shift(studylag)
    x1 = sm.add_constant(mergedDFshort['spotTheoR_lag'].values)
    x2 = sm.add_constant(mergedDFshort['spotTheoR_iopv_lag'].values)
    y1 = (mergedDFshort['optionSpot'] / mergedDFshort['optionSpot'].shift(returnlag)).values
    model1 = sm.OLS(y1,x1,missing='drop').fit()
    model2 = sm.OLS(y1,x2,missing='drop').fit()
    return (model1.rsquared, model2.rsquared)

# %%
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/SpotDetail")
ols_windowlist = [12,25,50,100,150,200,300]
lagList = [1,2,5,10,20,50,100,150,200,250,300,400,500]
for ols_window in ols_windowlist:
    gen_iopv_spottheory_ols(ols_window,mergedDF)    
    botheoR2 = []
    iopvtheoR2 = []
    for lag in lagList:
        (r1,r2) = gen_PredictionGraph(ols_window,mergedDF,lag)
        botheoR2.append(r1)
        iopvtheoR2.append(r2)

    tmpdf = pd.DataFrame(data={'botheoR2':botheoR2,'iopvtheoR2':iopvtheoR2},index=lagList)
    plt.plot(tmpdf['iopvtheoR2'], c='red',label='iopv')
    plt.plot(tmpdf['botheoR2'],c='blue',label='bo')
    plt.xlabel('Time in ticks')
    plt.ylabel('R2')
    plt.title(str(ols_window)+ "-tick OLS window Iopv Prediction")
    plt.legend()
    figname = str(ols_window)+"iopv_vs_bo.png"
    plt.savefig(figname)
    plt.show()
#%%
ols_windowlist = [12,25,50,100,150,200,300]
for ols_window in ols_windowlist:
    botheoR2 = []
    iopvtheoR2 = []
    for lag in lagList:
        (r1,r2) = gen_PredictionGraph(ols_window,mergedDF,lag)
        botheoR2.append(r1)
        iopvtheoR2.append(r2)

    tmpdf = pd.DataFrame(data={'botheoR2':botheoR2,'iopvtheoR2':iopvtheoR2},index=lagList)
    plt.plot(tmpdf['iopvtheoR2'], c='red',label='iopv')
    plt.plot(tmpdf['botheoR2'],c='blue',label='bo')
    plt.xlabel('Time in ticks')
    plt.ylabel('R2')
    plt.title(str(ols_window)+ "-tick OLS window Iopv Prediction")
    plt.legend()
    figname = str(ols_window)+"iopv_vs_bo.png"
    plt.savefig(figname)
    plt.show()

#%%
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/SpotDetail")
ols_windowlist = [8,12,25,50,100,150,200,300,500]
lagList = [1,2,3,4,5,6,7,8,9,10,12,15,20]
for ols_window in ols_windowlist:
    mergedDF2 = gen_iopv_spottheory_bo(ols_window,mergedDF,1)    
    botheoR2 = []
    iopvtheoR2 = []
    for lag in lagList:
        (r1,r2) = gen_PredictionGraph(ols_window,mergedDF2,lag,8,'bo')
        botheoR2.append(r1)
        iopvtheoR2.append(r2)

    tmpdf = pd.DataFrame(data={'botheoR2':botheoR2,'iopvtheoR2':iopvtheoR2},index=lagList)
    plt.plot(tmpdf['iopvtheoR2'], c='red',linewidth =0.5, markersize=0.1,label='iopv')
    plt.plot(tmpdf['botheoR2'],c='blue',linewidth =0.5, markersize=0.1,label='bo')
    plt.xlabel('Time in ticks')
    plt.ylabel('R2')
    plt.title('futurebo'+str(ols_window)+" window Iopv Prediction")
    plt.legend()
    figname = 'futurebo'+ str(ols_window)+"iopv_vs_bo.png"
    plt.savefig(figname)
    plt.show()

# %%
plt.plot(np.arange(len(mergedDF2)),mergedDF2['rawBo500bo'])
plt.plot(np.arange(len(mergedDF2)),mergedDF2['autoBo'])

# %%
plt.close()
plt.plot(np.arange(len(mergedDF2)),mergedDF2['optionSpot'])

# %%
plt.close()
plt.plot(np.arange(len(mergedDF2)),mergedDF2['rdiff_ma'])

# %%
