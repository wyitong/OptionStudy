
import os
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
from sklearn.linear_model import LinearRegression
from statsmodels.formula.api import ols
import statsmodels.api as sm
from os import path


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades/")




# region inputs/constants
# startdatestring = sys.argv[1]
# enddatestring = sys.argv[2]
startdatestring = '09/01/2019'
enddatestring = '10/01/2019'
startdate = datetime.strptime(startdatestring, '%m/%d/%Y').date()
enddate = datetime.strptime(enddatestring, '%m/%d/%Y').date()
res = pd.DataFrame()
# region PL analysis
for filename in os.listdir(os.getcwd()):
    if filename.startswith("PTR_"):
        filedatestr = filename[4:12]
        filedate = datetime.strptime(filedatestr, "%Y%m%d").date()
        if(filedate <=enddate) and (startdate<=filedate) and (filename.startswith("PTR_"+filedatestr+"_")):
            with open(filename) as json_file:
                df = pd.DataFrame.from_dict(json.load(json_file))
                res = res.append(df,ignore_index=True)
res =dataframe_prepare(res)
res =expand_volume(res)
res['ForwardTick000'] = (res['ForwardTick'] -1)
res['FutureTick000'] = (res['FutureTick'] -1)
res['FutureForwardChgRatio'] = (res['FutureTick000'] / res['ForwardTick000'])
res['FutureForwardChgParam'] = np.log(np.abs((res['FutureTick000'] / res['ForwardTick000'])))
res['NegativeSig'] =  res['FutureForwardChgRatio']<0
res['ForwardAbsTick'] = np.abs(res['ForwardTick000'])
res['FutureAbsTick'] = np.abs(res['FutureTick000'])

x1 = res['FutureForwardChgParam'].values
x2 = res['NegativeSig'].values
x3 = x1*x2*-1
y = res['dpl30'].values
y2 = res['hpl30'].values
X = np.column_stack((x1,x3))
X = sm.add_constant(X)

model = sm.OLS(y,X).fit()
print(model.summary())

model2 = sm.OLS(y2,X).fit()
print(model2.summary())


model2 = sm.OLS(y2,X).fit()
print(model2.summary())




bins = np.linspace(-12, 12, 24)
plt.close()
plt.hist(res['FutureForwardChgParam'], bins, label='Future', rwidth=None, density=True)
plt.xlabel('Return')
plt.ylabel('Density')
plt.title('Tick Comparison')
plt.legend(loc='upper right')
plt.show()
plt.savefig('Tick Comparison')
res['FutureAbsTick'].mean()
res1 =  res[res['NegativeSig']==True]
res2 =  res[res['NegativeSig']==False]



bins=np.linspace(-15, 15, 10)
studypoint_str_list = list(map(str, studypoint))
ressubgroup = res.groupby(
    pd.cut(res['FutureForwardChgParam'], bins=bins)
).agg({

    ('hpl' + studypoint_str_list[1]): 'mean',
    ('hpl' + studypoint_str_list[2]): 'mean',
    ('hpl' + studypoint_str_list[3]): 'mean',

    ('hpl' + studypoint_str_list[4]): 'mean',
})
ressubgroup.plot.bar()

ressubgroup1 = res1.groupby(
    pd.cut(res1['FutureForwardChgParam'], bins=bins)
).agg({

    ('hpl' + studypoint_str_list[1]): 'mean',
    ('hpl' + studypoint_str_list[3]): 'mean',
    ('hpl' + studypoint_str_list[4]): 'mean',

    ('hpl' + studypoint_str_list[6]): 'mean',
})
ressubgroup1.plot.bar()

ressubgroup2 = res2.groupby(
    pd.cut(res2['FutureForwardChgParam'], bins=bins)
).agg({

    ('hpl' + studypoint_str_list[1]): 'mean',
    ('hpl' + studypoint_str_list[3]): 'mean',
    ('hpl' + studypoint_str_list[4]): 'mean',

    ('hpl' + studypoint_str_list[6]): 'mean',
})
ressubgroup2.plot.bar()

# for studypoint_str in studypoint_str_list:
studypoint_str = '1'
plt.close()
ind = np.arange(len(ressubgroup[('hpl' + studypoint_str)]))
width = 0.35
fig, ax = plt.subplots()
rects2 = ax.bar(ind, res[('hpl' + studypoint_str)], width, label='hpl')
ax.set_ylabel('hpl'.upper())
ax.set_title('hpl'.upper() + ' after ' + studypoint_str + 'sec by Fu/Fo Ratio')
ax.set_xticks(ind)
# ax.set_xticklabels(('0-30', '30-50', '50-60', '60-70', '70-80', '80-90', '90-100'))
ax.legend()
fig.tight_layout()
plt.show()
plt.savefig(studypoint_str+'Tick Comparison')
plt.close()

