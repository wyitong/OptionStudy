import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import gc
from scipy import stats


starting_date = datetime.date(2019,4,2)
end_date = datetime.date(2019,9,2)

os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades")
# def post_trade_analysis():
ptaDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("PTR"):
        filedatestr = filename[4:12]
        filedate = datetime.datetime.strptime(filedatestr, "%Y%m%d").date()
        if filedate <= end_date and filedate >= starting_date:
            # print(filedate)
            with open(filename) as json_file:
                cur_json = json.load(json_file)
                cur_ptrDF = pd.DataFrame.from_dict(cur_json)
                ptaDF = ptaDF.append(cur_ptrDF,ignore_index=True)
print(len(ptaDF))
ptaDF['absDelta'] = abs(ptaDF['Delta'])

def calldeltacalc(row):
    if row['Delta']<=0:
        return row['Delta']+1
    else:
        return row['Delta']

ptaDF['callDelta'] =ptaDF.apply(calldeltacalc,axis=1)

ptaDF = ptaDF[ptaDF['Expiry']==False]

studypoint = [0,1,10,60,120]
for i in range(len(studypoint)):
    print(i)
    cur_str = str(studypoint[i])

    ptaDF[('dpl' + cur_str)]= ptaDF['DeltaPL'].apply(lambda x:(float(x[i])))
    ptaDF[('dplpercent'+ cur_str)] = ptaDF[('dpl' + cur_str)] / ptaDF['DOffset']

    ptaDF[('vpl' + cur_str)]= ptaDF['VegaPL'].apply(lambda x:(float(x[i])))
    ptaDF[('vplpercent' + cur_str)] = ptaDF[('vpl' + cur_str)] / ptaDF['VOffset']

# ptaDF.drop(['DeltaPL','VegaPL'],axis=1,inplace=True)
ptaDF.drop(['DeltaPL','VegaPL'],axis=1,inplace=True)

# plt.clf()
# plt.hist(ptaDF['Volume'])
# plt.title("Volume Histogram")
# plt.show()
# print ("Avg. volume per trade is: "+str(ptaDF['Volume'].mean()))
# print ("70-quantile volume per trade is: "+str(ptaDF['Volume'].quantile(0.7)))
# ptaDF = ptaDF[ptaDF["Volume"]<10]


ptaDF = ptaDF.reindex(ptaDF.index.repeat(ptaDF['Volume']))
ptaDF.index = np.arange(0,ptaDF.shape[0])

#region vega study
vegaDF = ptaDF[ptaDF['absDelta']<0.6]
bins = pd.cut(vegaDF['callDelta'], [0,0.25,0.35,0.5,0.65,0.75,1])

vegaRes = vegaDF.groupby(bins)['vplpercent1'].agg(['mean'])
vegaRes.drop("mean",axis=1,inplace=True)
for i in range(len(studypoint)):
    cur_str = str(studypoint[i])
    tmp = vegaDF.groupby(bins)['vplpercent' + cur_str].agg(['mean'])
    tmp.rename(columns={'mean':'VQ'+cur_str},inplace=True)
    vegaRes= vegaRes.merge(tmp,on='callDelta')
outFileName = "VegaQuality" + str(starting_date).replace("-", "") + "-" + str(end_date).replace("-", "") + ".csv"
vegaRes.to_csv(outFileName)

#endregion vega study

def groupFunc(row):
    if row['absDelta']<0.3:
        return "<30"
    elif abs(row['absDelta']-0.4)<0.1:
        return "30-50"
    else:
        return "50-100"
gc.collect()
ptaDF['DeltaGroup'] = ptaDF.apply(groupFunc,axis=1)

# ptaTinyD = ptaDF[abs(ptaDF['Delta']<0.1)]
# ptaLowD  = ptaDF[abs(abs(ptaDF['Delta'])-0.2)<0.1]
# ptaMidD  = ptaDF[abs(abs(ptaDF['Delta'])-0.4)<0.1]
# ptaHighD = ptaDF[abs(ptaDF['Delta'])>0.5]


ptaDF[ptaDF['Expiry']=='True']
def func_tTest(i,typestr):
    res = []
    cur_str = str(studypoint[i])
    for dgroup in ["<30","30-50","50-100"]:
        tmp = ptaDF.loc[ptaDF['DeltaGroup'] == dgroup][typestr+'plpercent'+cur_str]
        tmp.index = np.arange(0, len(tmp))
        res.append(stats.ttest_1samp(tmp, 0, nan_policy='omit')[1])

    return res


resDF = pd.DataFrame({'Delta':["<30","30-50","50-100"]})
resDF.index = resDF['Delta']
del resDF['Delta']
for i in range(len(studypoint)):
    cur_str = str(studypoint[i])
    resDF[('DQ'+cur_str)] = np.array([ptaDF[ptaDF['DeltaGroup']=="<30"]['dplpercent' + cur_str].mean(),
                                      ptaDF[ptaDF['DeltaGroup'] == "30-50"]['dplpercent' + cur_str].mean(),
                                      ptaDF[ptaDF['DeltaGroup'] == "50-100"]['dplpercent' + cur_str].mean()])

    resDF[('DQ'+cur_str+" p-value")] = np.array(func_tTest(i,'d'))

    resDF[('VQ'+cur_str)] = np.array([ptaDF[ptaDF['DeltaGroup']=="<30"]['vplpercent' + cur_str].mean(),
                                      ptaDF[ptaDF['DeltaGroup'] == "30-50"]['vplpercent' + cur_str].mean(),
                                      ptaDF[ptaDF['DeltaGroup'] == "50-100"]['vplpercent' + cur_str].mean()])
    resDF[('VQ'+cur_str+" p-value")] = np.array(func_tTest(i,'v'))

    # return resDF

outFileName = "TradeQuality" + str(starting_date).replace("-", "") + "-" + str(end_date).replace("-", "") + ".csv"
resDF.to_csv(outFileName)

# region


def using_dictcomp(df):
    return pd.DataFrame({col:np.repeat(df[col].values, df['Volume'], axis=0)
                          for col in df})
exp_ptaDF = using_dictcomp(ptaDF)
exp_ptaDF['absDelta'].plot.hist(grid=True, bins=20, rwidth=0.5,
                   color='#607c8e',density=False)
plt.title('TR Trade Delta Distribution')
plt.xlabel('Abs(Delta)')
plt.ylabel('Volume')
plt.grid(axis='y', alpha=0.75)
plt.show()
plt.savefig('TRDeltaDist')


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades/0201 - 0401 Fit")
# endregion

# def post_trade_analysis():
ptaFitDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("PTR"):
        filedatestr = filename[4:12]
        filedate = datetime.datetime.strptime(filedatestr, "%Y%m%d").date()
        if filedate <= end_date and filedate >= starting_date:
            # print(filedate)
            with open(filename) as json_file:
                cur_json = json.load(json_file)
                cur_ptrDF = pd.DataFrame.from_dict(cur_json)
                ptaFitDF = ptaFitDF.append(cur_ptrDF,ignore_index=True)
ptaFitDF = ptaFitDF[ptaFitDF['Expiry']==False]

ptaFitDF['absDelta'] = abs(ptaFitDF['Delta'])
exp_ptaFitDF = using_dictcomp(ptaFitDF)
bins = np.linspace(0, 1, 10)
plt.close()
plt.hist([exp_ptaDF['absDelta'], exp_ptaFitDF['absDelta']], bins, label=['TradeRetreat', 'Fit'], rwidth=0.7,
                   density=True)
plt.xlabel('Abs(Delta)')
plt.ylabel('Density')
plt.title('Trade AbsDelta Distribution Comparison')
plt.legend(loc='upper right')
plt.show()
plt.savefig('Comparison')


os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/trades/0201 - 0401 TR 1 2.4")
transDF = pd.DataFrame()

for filename in os.listdir(os.getcwd()):
    if filename.startswith("Trans"):
        filedatestr = filename[6:14]
        filedate = datetime.datetime.strptime(filedatestr, "%Y%m%d").date()
        if filedate <= end_date and filedate >= starting_date:
            with open(filename) as json_file:
                # print(filename)
                cur_json = json.load(json_file)["Transaction"]
                cur_transDF = pd.DataFrame.from_dict(cur_json)
                transDF = transDF.append(cur_transDF)
                if len(transDF[transDF['Delta']==0])>0:
                    print(filedate)

def dayfunc(row):
    if len(str(row['dayhr'])) == 2:
        return 0
    else:
        dayhr = float(row['dayhr'])
        if dayhr%1==0:
            return 0
        else:
            return int(dayhr//1)


def hourfunc(row):
    if len(row['dayhr'])==2:
        return int(row['dayhr'])
    else:
        dayhr = float(row['dayhr'])
        if dayhr%1==0:
            return int(dayhr)
        else:
            return int((dayhr%1)*100)
transDF.reset_index(inplace=True)
transDF['dayhr'] = transDF['HoldingTime'].apply(lambda x:x.split(":")[0])
transDF['Day'] = transDF.apply(dayfunc,axis=1)
transDF['Hour'] = transDF.apply(hourfunc,axis=1)
transDF['Minute'] = transDF['HoldingTime'].apply(lambda x:int(x.split(":")[1]))
transDF['Second'] = transDF['HoldingTime'].apply(lambda x:float(x.split(":")[2]))


transDF.drop(['index','dayhr'],axis=1,inplace=True)

def TotalSecCal(row):
    return row['Day']*3600*4+row['Hour']*3600 + row['Minute']*60 + row['Second']


transDF['TotalSec'] = transDF.apply(TotalSecCal,axis=1)

transDF['VolumeXTime'] = transDF['Volume'] * transDF['TotalSec']
transDF['absDelta'] = abs(transDF['Delta'])


print("Total Average Holding Time: %.1f seconds" %(transDF['VolumeXTime'].sum() / transDF['Volume'].sum()))
print("0-25D Average Holding Time: %.1f seconds" %(transDF[transDF['absDelta']<0.25]['VolumeXTime'].sum() / transDF[transDF['absDelta']<0.25]['Volume'].sum()))
print("25-50D Average Holding Time: %.1f seconds" %(transDF[abs(transDF['absDelta']-0.375)<0.125]['VolumeXTime'].sum() / transDF[abs(transDF['absDelta']-0.375)<0.125]['Volume'].sum()))
print("50-100D Average Holding Time: %.1f seconds" %(transDF[transDF['absDelta']>0.5]['VolumeXTime'].sum() / transDF[transDF['absDelta']>0.5]['Volume'].sum()))

quicktransDF = transDF[transDF['Day']==0]
print("Total Average Holding Time: %.1f seconds" %(quicktransDF['VolumeXTime'].sum() / quicktransDF['Volume'].sum()))
print("0-25D Average Holding Time: %.1f seconds" %(quicktransDF[quicktransDF['absDelta']<0.25]['VolumeXTime'].sum() / quicktransDF[quicktransDF['absDelta']<0.25]['Volume'].sum()))
print("25-50D Average Holding Time: %.1f seconds" %(quicktransDF[abs(quicktransDF['absDelta']-0.375)<0.125]['VolumeXTime'].sum() / quicktransDF[abs(quicktransDF['absDelta']-0.375)<0.125]['Volume'].sum()))
print("50-100D Average Holding Time: %.1f seconds" %(quicktransDF[quicktransDF['absDelta']>0.5]['VolumeXTime'].sum() / quicktransDF[quicktransDF['absDelta']>0.5]['Volume'].sum()))


    # plt.clf()
    # plt.hist(transDF['TotalSec'],weights=transDF['Volume'],range=(0,600))
    # plt.title("Holding Time Histogram")
    # plt.show()

