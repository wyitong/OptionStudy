import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
import datetime
from scipy import stats
from sklearn.linear_model import LinearRegression
from statsmodels.formula.api import ols
import statsmodels.api as sm

# def post_trade_analysis():
# starting_date = datetime.date(2020,1,1)
starting_date = datetime.date(2019,12,1)
end_date = datetime.date(2020,1,7)


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/theo-comp/")

surf_df = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("CompareTheo"):
        filedatestr = filename[12:20]
        filedate = datetime.datetime.strptime(filedatestr,"%Y%m%d").date()
        if filedate<=end_date and filedate>=starting_date:
            surf_df = surf_df.append(pd.read_csv(filename))
            print(filename)


surf_df['IvDiff_X_Vega'] = surf_df['SurfIVDiff'].abs()*surf_df['Vega']
surf_df['SurfIVDiffAbs'] = surf_df['SurfIVDiff'].abs()
surf_df['PDiffAbs'] = surf_df['PPDiff'].abs() + surf_df['CPDiff'].abs()

surf_df.groupby(['SurfType']).mean()
surf_summarize = surf_df.groupby(['SurfType']).mean()
surf_summarize.drop(columns = ['Strike','SurfIVDiff','Vega','Delta','PPDiff','CPDiff'],inplace=True)
bins = [0,0.3,0.4,0.5, 0.6, 0.7,1]

def surfplotgen(surf_df, propertystring):
    plotdf = pd.DataFrame()
    for surf in np.unique(surf_df['SurfType']):
        subdf = surf_df[surf_df['SurfType']==surf]
        surfgroup = subdf.groupby(
            pd.cut(subdf['Delta'], bins=bins)
        ).agg({
            propertystring: 'mean',
        })
        surfgroup.rename(columns={propertystring:propertystring+surf},inplace=True)
        if plotdf.size==0:
            plotdf = surfgroup
        else:
            plotdf = pd.concat([plotdf,surfgroup],axis=1)
    return plotdf
plotdf = surfplotgen(surf_df,'PDiffAbs')
plotdf.plot.bar()

ivVegadiff = surfplotgen(surf_df,'IvDiff_X_Vega')
ivVegadiff.plot.bar()


ivdiff = surfplotgen(surf_df,'SurfIVDiff')
ivdiff.plot.bar()

cubicgroup = cubic.groupby(
    pd.cut(cubic['Delta'], bins=bins)
).agg({
    'SurfIVDiffAbs': 'median',
    'IvDiff_X_Vega':'median'
})
cubicgroup.plot.bar()

plt.bar(np.arange(len(bins)),cubicgroup)
plt.show()
winggroup = surf_df.groupby(
    pd.cut(surf_df['Delta'], bins=bins)
).agg({
    'SurfIVDiffAbs': 'mean',
    'SurfIVDiff':'mean'
})
cubicgroup.plot.bar()



ind = np.arange(len(surf_group['SurfIVDiff']))
width = 0.35

fig, ax = plt.subplots()

rects1 = ax.bar(ind + width / 2, surf_df['IvDiff_X_Vega'], width, label='AbsIv*Vega')
rects2 = ax.bar(ind - width / 2, surf_df['SurfIVDiff'], width, label='Iv')
ax.set_ylabel('')
ax.set_title('')
ax.set_xticks(ind)
ax.set_xticklabels(('0-30', '30-50', '50-60', '60-70', '70-80', '80-90', '90-100'))
ax.legend()
fig.tight_layout()
plt.show()
plt.savefig('tmp')
plt.close(fig)
