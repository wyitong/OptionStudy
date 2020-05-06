#%%
import pandas as pd
import os
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from datetime import timedelta
import matplotlib.cbook as cbook
from matplotlib.dates import bytespdate2num, num2date
import matplotlib.ticker as ticker

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/300BoR")
#%%
expList = {}
for filename in os.listdir():
    if(not filename.startswith('BoR_')):
        continue
    exp = filename[4:12]
    if (exp in expList):
        expList[exp] = pd.concat([expList[exp], pd.read_csv(filename)], axis=0)
        expList[exp]['Exp'] = exp
    else:
        expList[exp] = pd.read_csv(filename)
        expList[exp]['Exp'] = exp


# %%
allBoR = pd.DataFrame()
for item in expList:
    allBoR = pd.concat([allBoR, expList[item]])
allBoR['boDiff'] = allBoR['boSH'] - allBoR['boSZ']
allBoR['rDiff'] = allBoR['rSH'] - allBoR['rSZ']
allBoR['timestamp'] = pd.to_datetime(allBoR['timestamp'])
# %%
bor01 = allBoR[allBoR['Exp'] == '20200122']
bor01 = bor01[bor01['timestamp']< dt.datetime(2020,1,20)]
#%%
plt.plot(np.arange(len(bor01)), bor01['boDiff'], 'o-',linewidth =0.5, markersize=0.1, label='boDiff01')
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.legend()
plt.show()


# %%
plt.close()
plt.plot(np.arange(len(bor01)), bor01['rDiff'], 'o-',linewidth =0.5, markersize=0.1, label='rDiff01')
plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
plt.legend()
plt.show()

# %%
def plot_borDiff(exp, alldf):
    borexp = alldf[alldf['Exp'] == exp]
    borexp = borexp[borexp['timestamp'] < dt.datetime.strptime(exp,"%Y%m%d") - timedelta(days=2)]
    plt.plot(np.arange(len(borexp)), borexp['boDiff'], 'o-',linewidth =0.5, markersize=0.05, label="boDiff "+ exp )
    plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
    plt.legend()
    plt.savefig("boDiff_"+exp+"_.png",dpi=500)
    plt.show()
    plt.close()

    plt.plot(np.arange(len(borexp)), borexp['rDiff'], 'o-',linewidth =0.5, markersize=0.05, label="rDiff "+exp )
    plt.axhline(y=0, color='r', linestyle='-',linewidth=0.5)
    plt.legend()
    plt.savefig("rDiff_"+exp+"_.png",dpi=500)
    plt.show()
    plt.close()

    X1 = borexp['boDiff'].values
    X1= sm.add_constant(X1)
    y1 = borexp['rDiff'].values
    model = sm.OLS(y1,X1,missing='drop').fit()
    print(model.summary())

# %%
for exp in expList:
    #print()
    plot_borDiff(exp, allBoR)

# %%
