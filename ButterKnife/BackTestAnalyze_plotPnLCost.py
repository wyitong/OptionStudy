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
#%%
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/0.001 0.00025 0.006 4000 0.4")
def LoadCostPnl(filename,monthstr):
    pnlcost = pd.read_csv(filename)
    pnlcost['Time'] = pd.to_datetime(pnlcost['Timestamp'])
    pnlcost['Expiry'] = pd.to_datetime(pnlcost['Expiry'])
    pnlcost = pnlcost[['Time','Expiry','Timeindex','Closedpnl','UnClosedPnL','TotalCost','TotalPnL']]    
    pnlcost.rename(columns={"TotalPnL":"TotalPnL"+monthstr, "TotalCost":"TotalCost"+monthstr},inplace=True)
    return pnlcost

# #%%
# plcost01 = pd.read_csv("PnlCost_20200122_20200122.csv")
# plcost01['Time'] = pd.to_datetime(plcost01['Timestamp'])
# plcost01['Expiry'] = pd.to_datetime(plcost01['Expiry'])
# plcost01 = plcost01[['Time','Expiry','Timeindex','Closedpnl','UnClosedPnL','TotalCost','TotalPnL']]

#%%
plcost01 = LoadCostPnl("PnlCost_20200122_20200122.csv","01")
plcost02 = LoadCostPnl("PnlCost_20200226_20200220.csv","02")
plcost03 = LoadCostPnl("PnlCost_20200325_20200325.csv","03")
plcost04 = LoadCostPnl("PnlCost_20200422_20200326.csv","04")
plcost06 = LoadCostPnl("PnlCost_20200624_20200326.csv","06")
plcost09 = LoadCostPnl("PnlCost_20200923_20200326.csv","09")

#%%
os.curdir
# %%
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

allPlCost['Date'] = allPlCost['Time'].dt.date
allPlCost['TotalCost'] = allPlCost['TotalCost01'] + allPlCost['TotalCost02'] + allPlCost['TotalCost03']  + allPlCost['TotalCost04'] + allPlCost['TotalCost06'] + allPlCost['TotalCost09']
allPlCost['TotalPnL'] = allPlCost['TotalPnL01'] + allPlCost['TotalPnL02'] + allPlCost['TotalPnL03'] + allPlCost['TotalPnL04']+ allPlCost['TotalPnL06'] + allPlCost['TotalPnL09']

#%%
def format_date(x, pos=None):
    thisind = np.clip(int(x + 0.5), 0, len(allPlCost) - 1)
    return allPlCost['Time'][thisind].strftime('%Y-%m-%d')
# %%
plt.close()
fig, ax = plt.subplots()

ax6 = plt.subplot(615)
l1 = ax6.plot(np.arange(len(allPlCost)), allPlCost['TotalPnL06'], 'o-',label = "PnL06",linewidth =0.5, markersize=0.1, color='dodgerblue')
ax6.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax6.set_ylabel("PnL")


ax62 = ax6.twinx()
l2 = ax62.plot(allPlCost['TotalCost06'], 'o-',label = "Cost06",linewidth =0.1, markersize=0, color='black')
ax62.fill_between(np.arange(len(allPlCost)), allPlCost['TotalCost06'], 0, facecolor='darkorange', alpha=0.3)
ax62.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax62.set_ylabel("Cost")
lns = l1+l2
labs =[l.get_label() for l in lns]
ax6.legend(lns,labs,loc=0)
plt.setp(ax6.get_xticklabels(), visible=False)

ax1 = plt.subplot(611, sharex=ax6)
l1= ax1.plot(np.arange(len(allPlCost)), allPlCost['TotalPnL01'], 'o-',label = "PnL01",linewidth =0.5, markersize=0.1, color='dodgerblue')
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax1.set_ylabel("PnL")

ax12 = ax1.twinx()
l2= ax12.plot(allPlCost['TotalCost01'], 'o-',label = "Cost01",linewidth =0.1, markersize=0, color='black')
ax12.fill_between(np.arange(len(allPlCost)), allPlCost['TotalCost01'], 0, facecolor='darkorange', alpha=0.3)
ax12.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax12.set_ylabel("Cost")
lns = l1+l2
labs =[l.get_label() for l in lns]
ax1.legend(lns,labs,loc=0)
plt.setp(ax1.get_xticklabels(), visible=False)

ax2 = plt.subplot(612,sharex= ax6)
l1 = ax2.plot(np.arange(len(allPlCost)), allPlCost['TotalPnL02'], 'o-',label = "PnL02",linewidth =0.5, markersize=0.1, color='dodgerblue')
ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax2.set_ylabel("PnL")

ax22 = ax2.twinx()
l2 = ax22.plot(allPlCost['TotalCost02'], 'o-',label = "Cost02",linewidth =0.1, markersize=0, color='black')
ax22.fill_between(np.arange(len(allPlCost)), allPlCost['TotalCost02'], 0, facecolor='darkorange', alpha=0.3)
ax22.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax22.set_ylabel("Cost")
lns = l1+l2
labs =[l.get_label() for l in lns]
ax2.legend(lns,labs,loc=0)
plt.setp(ax2.get_xticklabels(), visible=False)

ax3 = plt.subplot(613, sharex=ax6)
l1= ax3.plot(np.arange(len(allPlCost)), allPlCost['TotalPnL03'], 'o-',label = "PnL03",linewidth =0.5, markersize=0.1, color='dodgerblue')
ax3.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax3.set_ylabel("PnL")

ax32 = ax3.twinx()
l2= ax32.plot(allPlCost['TotalCost03'], 'o-',label = "Cost03",linewidth =0.1, markersize=0, color='black')
ax32.fill_between(np.arange(len(allPlCost)), allPlCost['TotalCost03'], 0, facecolor='darkorange', alpha=0.3)
ax32.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax32.set_ylabel("Cost")
lns = l1+l2
labs =[l.get_label() for l in lns]
ax3.legend(lns,labs,loc=0)
plt.setp(ax3.get_xticklabels(), visible=False)

ax3 = plt.subplot(614, sharex=ax6)
l1= ax3.plot(np.arange(len(allPlCost)), allPlCost['TotalPnL04'], 'o-',label = "PnL04",linewidth =0.5, markersize=0.1, color='dodgerblue')
ax3.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax3.set_ylabel("PnL")

ax32 = ax3.twinx()
l2= ax32.plot(allPlCost['TotalCost04'], 'o-',label = "Cost04",linewidth =0.1, markersize=0, color='black')
ax32.fill_between(np.arange(len(allPlCost)), allPlCost['TotalCost04'], 0, facecolor='darkorange', alpha=0.3)
ax32.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax32.set_ylabel("Cost")
lns = l1+l2
labs =[l.get_label() for l in lns]
ax3.legend(lns,labs,loc=0)
plt.setp(ax3.get_xticklabels(), visible=False)

ax9 = plt.subplot(616, sharex=ax6)
l1= ax9.plot(np.arange(len(allPlCost)), allPlCost['TotalPnL09'], 'o-',label = "PnL09",linewidth =0.5, markersize=0.1, color='dodgerblue')
ax9.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax9.set_ylabel("PnL")

ax92 = ax9.twinx()
l2 = ax92.plot(allPlCost['TotalCost09'], 'o-',label = "Cost09",linewidth =0.1, markersize=0, color='black')
ax92.fill_between(np.arange(len(allPlCost)), allPlCost['TotalCost09'], 0, facecolor='darkorange', alpha=0.3)
ax92.set_ylabel("Cost")
lns = l1+l2
labs =[l.get_label() for l in lns]
ax9.legend(lns,labs,loc=0)
ax92.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

fig.set_figheight(15)
fig.set_figwidth(15)
fig.autofmt_xdate()
plt.tight_layout()
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/Summary")
plt.savefig("pnlcost_Month.png",dpi=500)

plt.show()
# %%
plt.close()
fig, ax1 = plt.subplots()
l1=ax1.plot(np.arange(len(allPlCost)), allPlCost['TotalPnL'], 'o-',label = "TotalPnL",linewidth =0.2, markersize=0.01, color='dodgerblue')
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
ax1.set_ylabel("PnL")

ax2 = ax1.twinx()
l2 = ax2.plot(allPlCost['TotalCost'], 'o-',label = "TotalCost",linewidth =0.05, markersize=0.0, color='yellow')
ax2.fill_between(np.arange(len(allPlCost)), allPlCost['TotalCost'], 0, facecolor='darkorange', alpha=0.3)
ax2.set_ylabel("Cost")
lns = l1+l2
labs =[l.get_label() for l in lns]
ax2.legend(lns,labs,loc=2)
ax2.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
fig.autofmt_xdate()
plt.grid(True)
fig.set_figwidth(10)
fig.set_figheight(5)
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/ButterKnife/Summary")
plt.savefig("pnlcost_All.png",dpi=500)
plt.show()

# %%


# %%
