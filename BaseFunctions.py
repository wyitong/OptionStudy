import json
from pandas.io.json import json_normalize
import os
from os import path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
from datetime import datetime, date, timedelta
import sys
from scipy import stats
studypoint = [0, 1, 5, 10, 30, 60, 120]
# bins = [0,0.1,0.2, 0.3,0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
bins = [0,0.3,0.5, 0.6, 0.7, 0.8, 0.9, 1]

def daterange(start_date, end_date):
    """Return a iterable date range"""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def expand_volume(df):
    """Expand dataframe by the volume column"""
    return pd.DataFrame({col: np.repeat(df[col].values, df['Volume'], axis=0)
                         for col in df})

def dataframe_prepare(df):
    """prpare rawinput dataframe to be usable study object"""
    for i in range(len(studypoint)):
        cur_str = str(studypoint[i])
        df[('dpl' + cur_str)] = df['DeltaPL'].apply(lambda x: (float(x[i])))
        df[('hpl' + cur_str)] = df['HedgePL'].apply(lambda x: (float(x[i])))
        df[('vpl' + cur_str)] = df['VegaPL'].apply(lambda x: (float(x[i])))
        df[('pl' + cur_str)] = df['TotPL'].apply(lambda x: (float(x[i])))
    df['absDelta'] = abs(df['Delta'])
    df.drop(['DeltaPL', 'VegaPL', 'TotPL','HedgePL'], axis=1, inplace=True)
    return df

def pl_analysis(df1, df2,label1,label2, studypoint):
    """Take two prepared dataframes and analyze on post-trade results"""
    exp_df1 = expand_volume(df1)
    exp_df2 = expand_volume(df2)
    studypoint_str = str(studypoint)
    btgroup = exp_df1.groupby(
        pd.cut(exp_df1['absDelta'], bins)
    ).agg({
        ('pl' + studypoint_str): 'mean',
        ('vpl' + studypoint_str): 'mean',
        ('dpl' + studypoint_str): 'mean'
    })
    loggroup = exp_df2.groupby(
        pd.cut(exp_df2['absDelta'], bins)
    ).agg({
        ('pl' + studypoint_str): 'mean',
        ('vpl' + studypoint_str): 'mean',
        ('dpl' + studypoint_str): 'mean'
    })

    metriclist = ['pl', 'vpl', 'dpl']
    for metric in metriclist:
        ind = np.arange(len(loggroup[(metric + studypoint_str)]))
        width = 0.35

        fig, ax = plt.subplots()

        rects1 = ax.bar(ind + width / 2, btgroup[(metric + studypoint_str)], width, label=label1)
        rects2 = ax.bar(ind - width / 2, loggroup[(metric + studypoint_str)], width, label=label2)
        ax.set_ylabel(metric.upper())
        ax.set_title(metric.upper() + ' after ' + studypoint_str + 'sec by Abs(Delta) and trade source')
        ax.set_xticks(ind)
        ax.set_xticklabels(('0-30', '30-50', '50-60', '60-70', '70-80', '80-90', '90-100'))
        ax.legend()
        fig.tight_layout()
        plt.show()
        plt.savefig(label1+"_"+label2+metric + studypoint_str)
        plt.close(fig)

def AutoMMLogPLStudy(listPTRDF):
    for sp in studypoint:
        studypoint_str = str(sp)
        for exp in listPTRDF:
            expdf = expand_volume(exp.df)
            expdfgroup = expdf.groupby(
                pd.cut(expdf['absDelta'], bins)
            ).agg({
                ('pl' + studypoint_str): 'mean',
                ('vpl' + studypoint_str): 'mean',
                ('dpl' + studypoint_str): 'mean'
            })

            metriclist = ['pl', 'vpl', 'dpl']
            ind = np.arange(len(expdfgroup[(metriclist[0] + studypoint_str)]))
            width = 0.2
            fig, ax = plt.subplots()
            rects1 = ax.bar(ind - width, expdfgroup[(metriclist[0] + studypoint_str)], width, label="TotalPL")
            rects2 = ax.bar(ind , expdfgroup[(metriclist[1] + studypoint_str)], width, label="VegaPL")
            rects3 = ax.bar(ind + width, expdfgroup[(metriclist[2] + studypoint_str)], width, label="DeltaPL")
            ax.set_ylabel("PnL")
            ax.set_title('Expiry:'+ exp.expiry.strftime("%Y%m%d")+' Trade Quality after ' + studypoint_str + 'sec by Abs(Delta)')
            ax.set_xticks(ind)
            ax.set_xticklabels(('0-30', '30-50', '50-60', '60-70', '70-80', '80-90', '90-100'))
            ax.legend()
            fig.tight_layout()
            # plt.show()
            plt.savefig("TradeQuality"+exp.date.strftime("%Y%m%d")+'_'+exp.expiry.strftime("%Y%m%d")+'_'+studypoint_str)
            plt.close(fig)

def volumefunc(df1, df2,label1,label2):
    """Take two prepared dataframes and compare trades' distribution on abs_Delta"""
    exp_df1 = expand_volume(df1)
    exp_df2 = expand_volume(df2)

    # bins = np.linspace(0, 1, 12)
    plt.close()
    plt.hist([exp_df1['absDelta'], exp_df2['absDelta']], bins, label=[label1, label2], rwidth=None,
             density=True)
    plt.xlabel('Abs(Delta)')
    plt.ylabel('Density')
    plt.title('Trade AbsDelta Distribution Comparison')
    plt.legend(loc='upper right')
    plt.show()
    plt.savefig('VolumeComparison')

def volumeDisplay(listPTRDF):
    mergedDF = pd.DataFrame()
    for exp in listPTRDF:
        expdf = expand_volume(exp.df)
        plt.close()
        plt.hist(expdf['absDelta'],bins,label = 'Exp='+exp.expiry.strftime("%Y%m%d"),rwidth=None,density=True)
        plt.xlabel('Abs(Delta)')
        plt.ylabel('Density')
        plt.title('Trade AbsDelta Distribution' +exp.date.strftime("%Y%m%d"))
        plt.legend(loc='upper right')
        plt.savefig('Volume_'+exp.date.strftime("%Y%m%d")+'_'+exp.expiry.strftime("%Y%m%d"))
        if mergedDF.size==0:
            mergedDF = expdf
        else:
            mergedDF = mergedDF.append(expdf)
    plt.close()
    plt.hist(mergedDF['absDelta'], bins, label="All trades", rwidth=None, density=True,color='orange')
    plt.xlabel('Abs(Delta)')
    plt.ylabel('Density')
    plt.title('All Trade AbsDelta Distribution')
    plt.legend(loc='upper right')
    # plt.show()
    plt.savefig('Volume_' + exp.date.strftime("%Y%m%d") + '_all')
    plt.close()



class PTRDataframe:
    def __init__(self,df, expiry, date):
        self.df = df
        self.expiry = expiry
        self.date = date
