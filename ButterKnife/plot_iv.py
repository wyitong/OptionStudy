#%%
import pandas as pd
import os
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.cbook as cbook
from matplotlib.dates import bytespdate2num, num2date
import matplotlib.ticker as ticker

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/extrinsic-iv")

#func for  extimate ivdiff's ohprocess
def calcIvOHProcess(filestring, expstr):
    resDict = {}
    resDict.update({'Exp':expstr})
    ivdf = pd.read_csv(filestring)
    ivdf.rename(columns={"Key":"Date", "Value":"IVDiff"},inplace=True)
    ivdf['dIVDiff'] = ivdf['IVDiff'].shift(1) - ivdf['IVDiff']

    X1 = ivdf['IVDiff'].values
    X1= sm.add_constant(X1)
    y1 = ivdf['dIVDiff'].values
    model = sm.OLS(y1,X1,missing='drop').fit()
    resDict.update({'a':model.params[0],'a t-stat':model.tvalues[0]})
    resDict.update({'theta':-model.params[1],'theta t-stat':-model.tvalues[1]})
    resDict.update({'mu':resDict['a'] / resDict['theta']})
    resDict.update({'sigma':np.sqrt(model.mse_resid)})
    #print(model.summary())
    #print(np.sqrt(model.mse_resid))
    return resDict

#%%
#func for  extimate exdifff's ohprocess
def calcIvOHProcess2(filestring, expstr):
    resDict = {}
    resDict.update({'Exp':expstr})
    ivdf = pd.read_csv(filestring)
    ivdf.rename(columns={"timestamp":"Date", "ivdiff":"IVDiff"},inplace=True)
    ivdf['dIVDiff'] = ivdf['IVDiff'].shift(1) - ivdf['IVDiff']

    X1 = ivdf['IVDiff'].values
    X1= sm.add_constant(X1)
    y1 = ivdf['dIVDiff'].values
    model = sm.OLS(y1,X1,missing='drop').fit()
    resDict.update({'a':model.params[0],'a t-stat':model.tvalues[0]})
    resDict.update({'theta':-model.params[1],'theta t-stat':-model.tvalues[1]})
    resDict.update({'mu':resDict['a'] / resDict['theta']})
    resDict.update({'sigma':np.sqrt(model.mse_resid)})
    #print(model.summary())
    #print(np.sqrt(model.mse_resid))
    return resDict
#%%
#v0 block used for estimimate ivdiff's oh process
OHList = []
OHList.append(calcIvOHProcess("IVDiffNorm_20200122_20200122.csv",'01'))
OHList.append(calcIvOHProcess("IVDiffNorm_20200226_20200220.csv",'02'))
OHList.append(calcIvOHProcess("IVDiffNorm_20200325_20200325.csv",'03'))
OHList.append(calcIvOHProcess("IVDiffNorm_20200422_20200326.csv",'04'))
OHList.append(calcIvOHProcess("IVDiffNorm_20200624_20200326.csv",'06'))
OHList.append(calcIvOHProcess("IVDiffNorm_20200923_20200326.csv",'09'))
res = pd.DataFrame(OHList)
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/Summary")
res.to_excel('OH_OLSRes.xlsx')
#%%
#v1 block used for estimate extdiff's oh process
OHList = []
OHList.append(calcIvOHProcess2("extrinsic-iv_20200122_20200122.csv",'01'))
OHList.append(calcIvOHProcess2("extrinsic-iv_20200226_20200220.csv",'02'))
OHList.append(calcIvOHProcess2("extrinsic-iv_20200325_20200325.csv",'03'))
OHList.append(calcIvOHProcess2("extrinsic-iv_20200422_20200326.csv",'04'))
OHList.append(calcIvOHProcess2("extrinsic-iv_20200624_20200326.csv",'06'))
OHList.append(calcIvOHProcess2("extrinsic-iv_20200923_20200326.csv",'09'))
res = pd.DataFrame(OHList)
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/Summary")
res.to_excel('OH_OLSRes.xlsx')
#%%

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/0.001 0.00025 0.005 4000 0.5")
ivdiff01 = pd.read_csv("IVDiffNorm_20200122_20200122.csv")
ivdiff01.rename(columns={"Value":"IVDiff01"},inplace=True)
ivdiff01['dIVDiff'] = ivdiff01['IVDiff01'].shift(1) - ivdiff01['IVDiff01']

ivdiff02 = pd.read_csv("IVDiffNorm_20200226_20200220.csv")
ivdiff02.rename(columns={"Value":"IVDiff02"},inplace=True)
ivdiff02['dIVDiff'] = ivdiff02['IVDiff02'].shift(1) - ivdiff02['IVDiff02']

ivdiff03 = pd.read_csv("IVDiffNorm_20200325_20200325.csv")
ivdiff03.rename(columns={"Value":"IVDiff03"},inplace=True)
ivdiff03['dIVDiff'] = ivdiff03['IVDiff03'].shift(1) - ivdiff03['IVDiff03']

ivdiff04 = pd.read_csv("IVDiffNorm_20200422_20200326.csv")
ivdiff04.rename(columns={"Value":"IVDiff04"},inplace=True)
ivdiff04['dIVDiff'] = ivdiff04['IVDiff04'].shift(1) - ivdiff04['IVDiff04']

ivdiff06 = pd.read_csv("IVDiffNorm_20200624_20200326.csv")
ivdiff06.rename(columns={"Value":"IVDiff06"},inplace=True)
ivdiff06['dIVDiff'] = ivdiff06['IVDiff06'].shift(1) - ivdiff06['IVDiff06']

ivdiff09 = pd.read_csv("IVDiffNorm_20200923_20200326.csv")
ivdiff09.rename(columns={"Value":"IVDiff09"},inplace=True)
ivdiff09['dIVDiff'] = ivdiff09['IVDiff09'].shift(1) - ivdiff09['IVDiff09']
# %%
allIvDiff = ivdiff01.merge(ivdiff02,how='outer',on='Key')
allIvDiff = allIvDiff.merge(ivdiff03,how='outer',on='Key')
allIvDiff = allIvDiff.merge(ivdiff04,how='outer',on='Key')
allIvDiff = allIvDiff.merge(ivdiff06,how='outer',on='Key')
allIvDiff = allIvDiff.merge(ivdiff09,how='outer',on='Key')
allIvDiff.rename(columns={"Key":"Date"},inplace=True)
allIvDiff['DateTime'] = pd.to_datetime(allIvDiff['Date'])
allIvDiff['Date'] = allIvDiff['DateTime'].dt.date
allIvDiff.sort_values('DateTime',inplace=True)
allIvDiff = allIvDiff.reset_index(drop=True)
#%%
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/extrinsic-iv")
ivdiff01 = pd.read_csv("extrinsic-iv_20200122_20200122.csv")
ivdiff01.rename(columns={"extdiff":"IVDiff01"},inplace=True)
ivdiff01['dIVDiff'] = ivdiff01['IVDiff01'].shift(1) - ivdiff01['IVDiff01']

ivdiff02 = pd.read_csv("extrinsic-iv_20200226_20200220.csv")
ivdiff02.rename(columns={"extdiff":"IVDiff02"},inplace=True)
ivdiff02['dIVDiff'] = ivdiff02['IVDiff02'].shift(1) - ivdiff02['IVDiff02']

ivdiff03 = pd.read_csv("extrinsic-iv_20200325_20200325.csv")
ivdiff03.rename(columns={"extdiff":"IVDiff03"},inplace=True)
ivdiff03['dIVDiff'] = ivdiff03['IVDiff03'].shift(1) - ivdiff03['IVDiff03']

ivdiff04 = pd.read_csv("extrinsic-iv_20200422_20200326.csv")
ivdiff04.rename(columns={"extdiff":"IVDiff04"},inplace=True)
ivdiff04['dIVDiff'] = ivdiff04['IVDiff04'].shift(1) - ivdiff04['IVDiff04']

ivdiff06 = pd.read_csv("extrinsic-iv_20200624_20200326.csv")
ivdiff06.rename(columns={"extdiff":"IVDiff06"},inplace=True)
ivdiff06['dIVDiff'] = ivdiff06['IVDiff06'].shift(1) - ivdiff06['IVDiff06']

ivdiff09 = pd.read_csv("extrinsic-iv_20200923_20200326.csv")
ivdiff09.rename(columns={"extdiff":"IVDiff09"},inplace=True)
ivdiff09['dIVDiff'] = ivdiff09['IVDiff09'].shift(1) - ivdiff09['IVDiff09']

allIvDiff = ivdiff01.merge(ivdiff02,how='outer',on='timestamp')
allIvDiff = allIvDiff.merge(ivdiff03,how='outer',on='timestamp')
allIvDiff = allIvDiff.merge(ivdiff04,how='outer',on='timestamp')
allIvDiff = allIvDiff.merge(ivdiff06,how='outer',on='timestamp')
allIvDiff = allIvDiff.merge(ivdiff09,how='outer',on='timestamp')

allIvDiff.rename(columns={"timestamp":"Date"},inplace=True)
allIvDiff['DateTime'] = pd.to_datetime(allIvDiff['Date'])
allIvDiff['Date'] = allIvDiff['DateTime'].dt.date
allIvDiff.sort_values('DateTime',inplace=True)
allIvDiff = allIvDiff.reset_index(drop=True)




#%%
def format_date(x, pos=None):
    thisind = np.clip(int(x + 0.5), 0, len(allIvDiff) - 1)
    return allIvDiff['Date'][thisind].strftime('%Y-%m-%d')


#%%
fig, ax = plt.subplots()
ax1 = plt.subplot(611)
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
plt.plot(np.arange(len(allIvDiff)), allIvDiff['IVDiff01'], 'o-',linewidth =0.5, markersize=0.1, label='IVDiff01')
plt.ylim(-0.02,0.02)
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.setp(ax1.get_xticklabels(), visible=False)
plt.legend()

ax2 = plt.subplot(612, sharex=ax1, sharey= ax1)
plt.plot(np.arange(len(allIvDiff)), allIvDiff['IVDiff02'], 'o-',linewidth =0.5, markersize=0.1, label='IVDiff02')
# make these tick labels invisible
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.setp(ax2.get_xticklabels(), visible=False)
plt.legend()

ax3 = plt.subplot(613, sharex=ax1, sharey= ax1)
plt.plot(np.arange(len(allIvDiff)), allIvDiff['IVDiff03'], 'o-',linewidth =0.5, markersize=0.1, label='IVDiff03')
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.setp(ax3.get_xticklabels(), visible=False)
plt.legend()

ax4 = plt.subplot(614, sharex=ax1, sharey= ax1)
plt.plot(np.arange(len(allIvDiff)), allIvDiff['IVDiff04'], 'o-',linewidth =0.5, markersize=0.1, label='IVDiff04')
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.legend()

ax6 = plt.subplot(615, sharex=ax1, sharey= ax1)
plt.plot(np.arange(len(allIvDiff)), allIvDiff['IVDiff06'], 'o-',linewidth =0.5, markersize=0.1, label='IVDiff06')
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.legend()

ax9 = plt.subplot(616, sharex=ax1, sharey= ax1)
plt.plot(np.arange(len(allIvDiff)), allIvDiff['IVDiff09'], 'o-',linewidth =0.5, markersize=0.1, label='IVDiff09')
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.legend()

fig.autofmt_xdate()
plt.xticks(rotation=30)
fig.set_figheight(10)
fig.set_figwidth(15)
fig.set_figwidth(15)
fig.tight_layout(pad=1.0)
plt.legend()
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/Summary")
plt.savefig("ivdiff.png",dpi=500)
plt.show()


# %%
