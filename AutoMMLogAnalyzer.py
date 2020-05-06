import os
from os import path
import json
from BaseFunctions import *
from pandas.io.json import json_normalize

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
from datetime import datetime, date, timedelta
import sys
from scipy import stats

datestr = sys.argv[1]
dirstr = sys.argv[2]

expiry_list = []
data_list = []
studytdate = datetime.strptime(datestr, '%m/%d/%Y').date()
filedatestr = studytdate.strftime("%Y%m%d")
os.chdir(dirstr)
for filename in os.listdir(dirstr):
    if filename.startswith("LogPTR_"+filedatestr):
        cur_exp = datetime.strptime(filename[16:24], "%Y%m%d").date()
        if not (cur_exp in expiry_list): expiry_list.append(cur_exp)
        with open(filename) as json_file:
            df = pd.DataFrame.from_dict(json.load(json_file))
            data_list.append(PTRDataframe(dataframe_prepare(df), cur_exp, studytdate))

volumeDisplay(data_list)
AutoMMLogPLStudy(data_list)



