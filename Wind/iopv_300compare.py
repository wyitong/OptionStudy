#%%
from WindPy import w
import pandas as pd
import datetime as dt
import os
import sys
sys.path.append("C:/Users/Yitong/AppData/Local/PythonProject/Wind/")
import iopv_study
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import zlib
import iopv_study
w.start()
etfList = ["510300.SH", "159919.SZ"]
#%%
os.chdir("C:/Users/Yitong/AppData/Local/PythonProject/Wind/")
iopvChgList = {}
for etfname in etfList:
    iopvChgList[etfname] = pd.read_csv(etfname+"_chg.csv")
    # iopvSavedList[etfname]['timestamp'] = pd.to_datetime(iopvSavedList[etfname]['timestamp'])
    iopvChgList[etfname]['date'] = pd.to_datetime(iopvChgList[etfname]['date']).dt.date
    iopvChgList[etfname]['time'] = pd.to_datetime(iopvChgList[etfname]['time']).dt.time
    iopvChgList[etfname]['timestamp'] = iopvChgList[etfname].apply(lambda r : pd.datetime.combine(r['date'],r['time']),1)

# %%
#region read spotdetail
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/SpotDetail")
expSpotListSH = {}
for filename in os.listdir():
    if(not filename.startswith("510300")):
        continue
    split_filename = filename.split('_')
    exp = split_filename[2]
    date = split_filename[3][0:8]
    
    if (exp in expSpotListSH):
        curDF = pd.read_csv(filename)
        curDF['Exp'] = exp
        curDF['Date'] = date
        curDF['Und'] = '510300'
        expSpotListSH[exp] = pd.concat([expSpotListSH[exp],curDF], axis=0)        
        expSpotListSH[exp] = expSpotListSH[exp].reset_index(drop=True)   
    else:
        expSpotListSH[exp] = pd.read_csv(filename)
        expSpotListSH[exp]['Exp'] = exp
        expSpotListSH[exp]['Date'] = date
        expSpotListSH[exp]['Und'] = '159919'
for exp in expSpotListSH:
    expSpotListSH[exp]['timestamp'] = pd.to_datetime(expSpotListSH[exp]['Date']+' '+expSpotListSH[exp]['time'], infer_datetime_format=True)
    expSpotListSH[exp]['date'] =  expSpotListSH[exp]['timestamp'].dt.date
    expSpotListSH[exp]['time'] =  expSpotListSH[exp]['timestamp'].dt.time
    expSpotListSH[exp].drop(columns = ['millisec','Date'], inplace=True)
#%%

expSpotListSZ = {}
for filename in os.listdir():
    if(not filename.startswith("159919")):
        continue
    split_filename = filename.split('_')
    exp = split_filename[2]
    date = split_filename[3][0:8]
    
    if (exp in expSpotListSZ):
        curDF = pd.read_csv(filename)
        curDF['Exp'] = exp
        curDF['Date'] = date
        curDF['Und'] = '159919'
        expSpotListSZ[exp] = pd.concat([expSpotListSZ[exp],curDF], axis=0)        
        expSpotListSZ[exp] = expSpotListSZ[exp].reset_index(drop=True)   
    else:
        expSpotListSZ[exp] = pd.read_csv(filename)
        expSpotListSZ[exp]['Exp'] = exp
        expSpotListSZ[exp]['Date'] = date
        expSpotListSZ[exp]['Und'] = '159919'
for exp in expSpotListSZ:
    expSpotListSZ[exp]['timestamp'] = pd.to_datetime(expSpotListSZ[exp]['Date']+' '+expSpotListSZ[exp]['time'], infer_datetime_format=True)
    expSpotListSZ[exp]['date'] =  expSpotListSZ[exp]['timestamp'].dt.date
    expSpotListSZ[exp]['time'] =  expSpotListSZ[exp]['timestamp'].dt.time
    expSpotListSZ[exp].drop(columns = ['millisec','Date'], inplace=True)
#endregion
#%%
os.chdir("C:/Users/Yitong/AppData/Local/PythonProject/Wind")
iopvChgList = {}
for etfname in etfList:
    iopvChgList[etfname] = pd.read_csv(etfname+"_chg.csv")
    # iopvSavedList[etfname]['timestamp'] = pd.to_datetime(iopvSavedList[etfname]['timestamp'])
    iopvChgList[etfname]['date'] = pd.to_datetime(iopvChgList[etfname]['date']).dt.date
    iopvChgList[etfname]['time'] = pd.to_datetime(iopvChgList[etfname]['time']).dt.time
    iopvChgList[etfname]['timestamp'] = iopvChgList[etfname].apply(lambda r : pd.datetime.combine(r['date'],r['time']),1)

# %%

shDF = expSpotListSH['20200527']
szDF = expSpotListSZ['20200527']
shiopv = iopvChgList["510300.SH"]
sziopv = iopvChgList["159919.SZ"]

# %%
maxDate = shDF['date'].max()
minDate = shDF['date'].min()
shiopv = shiopv[shiopv['date']<= maxDate]
shiopv = shiopv[shiopv['date']>= minDate]
shiopv = shiopv[shiopv['time']>= dt.time(9,30,0)]
shiopv['matchedTime'] = shiopv.apply(iopv_study.binarySearch_RowOps, args = (shDF['timestamp'].array, 0,len(shDF['timestamp'])-1),axis=1)
mergedDFsh = pd.merge(shDF,shiopv,'outer',left_on='timestamp', right_on='matchedTime')
mergedDFsh['iopvR'] = mergedDFsh['iopv'] / mergedDFsh['etf_preclose']
mergedDFsh['futureR'] = mergedDFsh['fut'] / mergedDFsh['fut_preclose']
mergedDFsh = mergedDFsh[mergedDFsh['time_x']>= dt.time(9,30,0)]

# %%
maxDate = szDF['date'].max()
minDate = szDF['date'].min()
sziopv = sziopv[sziopv['date']<= maxDate]
sziopv = sziopv[sziopv['date']>= minDate]
sziopv = sziopv[sziopv['time']>= dt.time(9,30,0)]
sziopv['matchedTime'] = sziopv.apply(iopv_study.binarySearch_RowOps, args = (szDF['timestamp'].array, 0,len(szDF['timestamp'])-1),axis=1)
mergedDFsz = pd.merge(szDF,sziopv,'outer',left_on='timestamp', right_on='matchedTime')
mergedDFsz['iopvR'] = mergedDFsz['iopv'] / mergedDFsz['etf_preclose']
mergedDFsz['futureR'] = mergedDFsz['fut'] / mergedDFsz['fut_preclose']
mergedDFsz = mergedDFsz[mergedDFsz['time_x']>= dt.time(9,30,0)]

# %%
shortshdf = mergedDFsh[mergedDFsh['iopvR'].notnull()]
shortszdf = mergedDFsz[mergedDFsz['iopvR'].notnull()]


shortshdf['option-iopv-bo'] = shortshdf['optionSpot']-shortshdf['iopv']
shortszdf['option-iopv-bo'] = shortszdf['optionSpot']-shortszdf['iopv']

shortshdf['iopv-fut-bo'] = shortshdf['iopv'] - ((shortshdf['futureR']-1) * 0.9+1) * shortshdf['etf_preclose']
shortszdf['iopv-fut-bo'] = shortszdf['iopv'] - ((shortszdf['futureR']-1) * 0.9+1) * shortszdf['etf_preclose']

shortshdf['rawbo'] = shortshdf['option-iopv-bo'] + shortshdf['iopv-fut-bo'] 
shortszdf['rawbo'] = shortszdf['option-iopv-bo'] + shortszdf['iopv-fut-bo']
#%%
plt.close()
# plt.plot(shortszdf['rawbo'], c='red',label='rawbodiff')
plt.plot(shortshdf['rawbo'], c='blue',label='rawbodiff')
# plt.plot(shortszdf['option-iopv-bo'], c='red',label='rawbodiff')
# plt.plot(shortszdf['option-iopv-bo'], c='red',label='rawbodiff')
plt.show()
#%%
plt.close()
# plt.plot(shortszdf['rawbo'], c='red',label='rawbodiff')
plt.plot(shortszdf['rawbo'], c='blue',label='rawbodiff')
# plt.plot(shortszdf['option-iopv-bo'], c='red',label='rawbodiff')
# plt.plot(shortszdf['option-iopv-bo'], c='red',label='rawbodiff')
plt.show()
#%%
plt.close()

#%%
# fig, ax = plt.subplots()
# ax.scatter(shortshdf['option-iopv-bo'], shortshdf['iopv-fut-bo'])
# plt.show()
print("SH: rawbosd {:2f}, iopv-fut-bo sd  {:2f}, option-iopv-bo sd  {:2f}".format(shortshdf['rawbo'].std(), shortshdf['iopv-fut-bo'].std(), shortshdf['option-iopv-bo'].std()))

print("SZ: rawbosd {:2f}, iopv-fut-bo sd  {:2f}, option-iopv-bo sd  {:2f}".format(shortszdf['rawbo'].std(), shortszdf['iopv-fut-bo'].std(), shortszdf['option-iopv-bo'].std()))

# %%
merged300DF = pd.merge(shortshdf,shortszdf,how='outer',on='timestamp_x',sort=True)
merged300DF.to_csv("merged300.csv")
#%%
merged300DF.sort_values(by = ['timestamp_x'], inplace=True)
merged300DF.reset_index(inplace=True)
merged300DFi = merged300DF.interpolate(method='linear')
#%%


#%%
merged300DFi['rawbodiff'] = merged300DFi['rawbo_x'] - merged300DFi['rawbo_y']
merged300DFi['iopv-fut-bodiff'] = merged300DFi['iopv-fut-bo_x'] - merged300DFi['iopv-fut-bo_y']
merged300DFi['option-iopv-bodiff'] = merged300DFi['option-iopv-bo_x'] - merged300DFi['option-iopv-bo_y']
# %%
plt.close()
plt.plot(merged300DFi['rawbodiff'], c='red',label='rawbodiff',ms=0.2,lw=0.1)
plt.plot(merged300DFi['iopv-fut-bodiff'],c='blue',label='iopv-fut-bodiff',ms=0.2,lw=0.1)
plt.plot(merged300DFi['option-iopv-bodiff'],c='green',label='option-iopv-bodiff',ms=0.2,lw=0.1)
plt.legend()
plt.show()

# %%
print("diffSD: rawbosd {:2f}, iopv-fut-bo sd  {:2f}, option-iopv-bo sd  {:2f}".format(merged300DFi['rawbodiff'].std(), merged300DFi['iopv-fut-bodiff'].std(), merged300DFi['option-iopv-bodiff'].std()))

# %%
mild_merged300DFi = merged300DFi[['timestamp_x','rawbodiff', 'iopv-fut-bodiff', 'option-iopv-bodiff']]
#%%
mild_merged300DFi['r_outlier'] = mild_merged300DFi['rawbodiff'] - 0.5*(mild_merged300DFi['rawbodiff'].shift(1) + mild_merged300DFi['rawbodiff'].shift(-1))

mild_merged300DFi['i_outlier'] = mild_merged300DFi['iopv-fut-bodiff'] - 0.5*(mild_merged300DFi['iopv-fut-bodiff'].shift(1) + mild_merged300DFi['iopv-fut-bodiff'].shift(-1))

mild_merged300DFi['o_outlier'] = mild_merged300DFi['option-iopv-bodiff'] - 0.5*(mild_merged300DFi['option-iopv-bodiff'].shift(1) + mild_merged300DFi['option-iopv-bodiff'].shift(-1))
#%%
mild_merged300DFi = mild_merged300DFi[np.abs(mild_merged300DFi['r_outlier'])<0.003]
mild_merged300DFi = mild_merged300DFi[np.abs(mild_merged300DFi['i_outlier'])<0.003]
mild_merged300DFi = mild_merged300DFi[np.abs(mild_merged300DFi['o_outlier'])<0.003]
mild_merged300DFi['time'] = mild_merged300DFi['timestamp_x'].dt.time
#%%
print(len(mild_merged300DFi))
#%%
mild_merged300DFi = mild_merged300DFi[mild_merged300DFi['time']>dt.time(9,33,00)]
mild_merged300DFi = mild_merged300DFi[mild_merged300DFi['time']<dt.time(14,55,00)]
print(len(mild_merged300DFi))
# %%
plt.close()
plt.plot(mild_merged300DFi['rawbodiff'], c='red',label='rawbodiff',ms=0.2,lw=0.2)
plt.plot(mild_merged300DFi['iopv-fut-bodiff'],c='blue',label='iopv-fut-bodiff',ms=0.2,lw=0.2)
plt.plot(mild_merged300DFi['option-iopv-bodiff'],c='green',label='option-iopv-bodiff',ms=0.2,lw=0.2)
plt.legend()
plt.savefig('bo_diff.png',dpi=300)
plt.show()
# %%
print("diffSD: rawbosd {:2f}, iopv-fut-bo sd  {:2f}, option-iopv-bo sd  {:2f}".format(mild_merged300DFi['rawbodiff'].std(), mild_merged300DFi['iopv-fut-bodiff'].std(), mild_merged300DFi['option-iopv-bodiff'].std()))


# %%
mild_merged300DFi['time']>dt.time(9,35,00)

# %%
