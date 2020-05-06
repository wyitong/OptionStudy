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

starting_date = datetime.date(2019,9,1)
end_date = datetime.date(2019,10,23)
studyexp = datetime.date(2019,10,23)
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/StraddlePrice/")
straddle_DF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("Straddle"):
        datestr = filename[9:17]
        filedate = datetime.datetime.strptime(datestr,"%Y%m%d").date()
        expstr = filename[19:29]
        expdate = datetime.datetime.strptime(expstr,"%Y-%m-%d").date()
        if filedate<=end_date and filedate>=starting_date and expdate ==studyexp:
            print(filename)
            straddle_DF = straddle_DF.append(pd.read_csv(filename))

print(np.std(straddle_DF['YDP30']))
print(np.std(straddle_DF['YDP60']))
print(np.std(straddle_DF['YDP120']))
print(np.std(straddle_DF['YDP300']))


studyexp = datetime.date(2019,11,27)
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/StraddlePrice/")
straddle_DF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("Straddle"):
        datestr = filename[9:17]
        filedate = datetime.datetime.strptime(datestr,"%Y%m%d").date()
        expstr = filename[19:29]
        expdate = datetime.datetime.strptime(expstr,"%Y-%m-%d").date()
        if filedate<=end_date and filedate>=starting_date and expdate ==studyexp:
            print(filename)
            straddle_DF = straddle_DF.append(pd.read_csv(filename))

print(np.std(straddle_DF['YDP30']))
print(np.std(straddle_DF['YDP60']))
print(np.std(straddle_DF['YDP120']))
print(np.std(straddle_DF['YDP300']))

studyexp = datetime.date(2019,12,25)
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/StraddlePrice/")
straddle_DF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("Straddle"):
        datestr = filename[9:17]
        filedate = datetime.datetime.strptime(datestr,"%Y%m%d").date()
        expstr = filename[19:29]
        expdate = datetime.datetime.strptime(expstr,"%Y-%m-%d").date()
        if filedate<=end_date and filedate>=starting_date and expdate ==studyexp:
            print(filename)
            straddle_DF = straddle_DF.append(pd.read_csv(filename))

print(np.std(straddle_DF['YDP30']))
print(np.std(straddle_DF['YDP60']))
print(np.std(straddle_DF['YDP120']))
print(np.std(straddle_DF['YDP300']))

studyexp = datetime.date(2020,3,25)
os.chdir("C:/Users/Yitong/AppData/Local/auto-option-mm/StraddlePrice/")
straddle_DF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("Straddle"):
        datestr = filename[9:17]
        filedate = datetime.datetime.strptime(datestr,"%Y%m%d").date()
        expstr = filename[19:29]
        expdate = datetime.datetime.strptime(expstr,"%Y-%m-%d").date()
        if filedate<=end_date and filedate>=starting_date and expdate ==studyexp:
            print(filename)
            straddle_DF = straddle_DF.append(pd.read_csv(filename))

print(np.std(straddle_DF['YDP30']))
print(np.std(straddle_DF['YDP60']))
print(np.std(straddle_DF['YDP120']))
print(np.std(straddle_DF['YDP300']))



