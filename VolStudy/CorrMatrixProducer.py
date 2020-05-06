import json
from pandas.io.json import json_normalize
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc
import datetime as dt
from datetime import timedelta
from matplotlib import pyplot
import statsmodels.api as sm
from ast import literal_eval

cwd = os.getcwd()
# def post_trade_analysis():
starting_date = dt.date(2019,4,1)
end_date = dt.date(2019,10,28)
# starting_date = dt.date(2018,7,2)
# end_date = dt.date(2019,1,1)

NodeVolDF = pd.DataFrame()
for filename in os.listdir(os.getcwd()):
    if filename.startswith("VolNodeTS"):
        filedatestr = filename[9:17]
        filedate = dt.datetime.strptime(filedatestr,"%Y%m%d").date()
        if filedate<=end_date and filedate>=starting_date:
            print(filename)

            with open(filename) as json_file:
                cur_json = json.load(json_file)
                oldTs = dt.datetime(2000,1,1)

                cur_DF = json_normalize(cur_json)
                cur_DF['timestamp'] = pd.to_datetime(cur_DF['ts'])
                NodeVolDF = NodeVolDF.append(cur_DF, ignore_index=True)


NodeVolDF = NodeVolDF[NodeVolDF['expire']==False]
OrigVolDF = NodeVolDF
nodeList = []
for column in NodeVolDF:
    if column.startswith('node'):
        nodeList.append(float((column[8:])))
        NodeVolDF.rename(columns={column: column[8:]},inplace=True)


nodeList.sort()
nodeList = [str(elem) for elem in nodeList]
for i in range(len(nodeList)):
    if nodeList[i].endswith(".0"):
        nodeList[i] = nodeList[i][0:-2]

# tmp = NodeVolDF.mean(axis = 0)
AtmNode = nodeList[int(len(nodeList)/2)]
for node in nodeList:
    if node == AtmNode:
        NodeVolDF[node + 'd'] = NodeVolDF[node]
        continue
    NodeVolDF[node+'d'] = NodeVolDF[node] - NodeVolDF[AtmNode]
# tmpdf = NodeVolDF[1:500]
# tmpdf.to_excel("NodeVol.xlsx")

# NodeVolDF['0.65dlog'] = np.log(NodeVolDF['0.65d']-NodeVolDF['0.65d'].min()+0.001)
# NodeVolDF['0.35dlog'] = np.log(NodeVolDF['0.35d']-NodeVolDF['0.35d'].min()+0.001)

NodeVolDF['date']= NodeVolDF['timestamp'].dt.date
NodeVolDF = NodeVolDF.set_index('timestamp')

for node in nodeList:
    nodename = node+'_l1'
    NodeVolDF[nodename] = NodeVolDF.groupby(['date'])[node].shift(2)

rightWingNodes = []
leftWingNodes = []

for index_x, Node in enumerate(nodeList):
    if float(Node) < 50:
        rightWingNodes.append(Node)
        if nodeList[index_x+1]==AtmNode:
            rightPivotNode=Node
    if float(Node) >50:
        leftWingNodes.append(Node)
        if nodeList[index_x-1]==AtmNode:
            leftPivotNode=Node


def slopeCalc(y_str,x_str):
    x = sm.add_constant(NodeVolDF[x_str].values)
    y = NodeVolDF[y_str].values
    model = sm.OLS(y,x).fit()
    return model.params[-1]

def slopeCalcwVol(y_str,x_str):
    if x_str == AtmNode:
        return 0
    x = sm.add_constant(NodeVolDF[[AtmNode,x_str]].values)
    y = NodeVolDF[y_str].values
    model = sm.OLS(y,x).fit()
    return model.params[-1]

def slopeCalcwVol_lag(y_str,x_str):
    if x_str == AtmNode:
        return 0
    x = sm.add_constant(NodeVolDF[[AtmNode+'_l1',x_str+'_l1']].values)
    y = NodeVolDF[y_str].values

    # these 3 lines below is the constraint on 65-35 symmetry
    if ((y_str==leftPivotNode and x_str==rightPivotNode) or (y_str==rightPivotNode and x_str==leftPivotNode)):
        x = np.append(x, sm.add_constant(NodeVolDF[[AtmNode+'_l1',y_str+'_l1']].values),axis=0)
        y = np.append(y, NodeVolDF[x_str].values,axis=0)

    model = sm.OLS(y,x,missing='drop').fit()
    return model.params[-1]


# t1 = sm.add_constant(NodeVolDF[['0.5_l1','0.35_l1']].values)[1:5]
# t2 = np.append(t1,t1,axis=0)

NodeCorr = pd.DataFrame()
data = {}
for yNode in nodeList:
    ycolumn = []
    for xNode in nodeList:
        # ystr = yNode+'d'
        # xstr = xNode+'d'
        ystr = yNode
        xstr = xNode
        # ycolumn.append(slopeCalc(ystr,xstr))
        # ycolumn.append(slopeCalcwVol(ystr,xstr))
        if xNode==yNode:
            ycolumn.append(1)
        else:
            ycolumn.append(slopeCalcwVol_lag(ystr,xstr))
    data[yNode]=ycolumn
NodeCorr = pd.DataFrame(data,index=nodeList)

NodeCorr_adj = NodeCorr.copy()


#region improving on pure correlation
for index_x, xNode in enumerate(nodeList):
    for index_y, yNode in enumerate(nodeList):
        if xNode in rightWingNodes:
            #wing nodes only affect outter nodes
            if index_y>index_x+1:
                NodeCorr_adj[yNode][xNode]=0

        elif xNode in leftWingNodes:
            #wing nodes only affect outter nodes
            if index_y<index_x-1:
                NodeCorr_adj[yNode][xNode]=0
        #pivot nodes affect cross-wing
        if xNode == rightPivotNode and yNode in leftWingNodes:
            NodeCorr_adj[yNode][xNode] = NodeCorr[yNode][leftPivotNode] * NodeCorr[leftPivotNode][rightPivotNode]
            # NodeCorr_adj[yNode][xNode] = NodeCorr[yNode][leftPivotNode] * (-0.6)

        if xNode == leftPivotNode and yNode in rightWingNodes:
            NodeCorr_adj[yNode][xNode] = NodeCorr[yNode][rightPivotNode] * NodeCorr[rightPivotNode][leftPivotNode]
            # NodeCorr_adj[yNode][xNode] = NodeCorr[yNode][rightPivotNode] * (-0.6)
        if yNode ==AtmNode:
            NodeCorr_adj[yNode][xNode] =0

        if xNode == AtmNode:
            NodeCorr_adj[yNode][xNode] =1
#end region

NodeCorr.to_excel("NodeCorr.xlsx")
NodeCorr_adj.to_json(r'C:\Users\Yitong\AppData\Local\auto-option-mm\Node_Corr_adj.json',orient='index')

outFileName = "NodeCorrAdj" +str(starting_date).replace("-","") + "-" + str(end_date).replace("-","")+".xlsx"
NodeCorr_adj.to_excel(outFileName)


plt.close()
NodeVolDF[NodeVolDF['date']==dt.date(2019,6,24)]['0.5'].plot(linewidth = 0.8)


#region

x05 = NodeVolDF['0.05d'].values
x10 = NodeVolDF['0.1d'].values
x25 = NodeVolDF['0.25d'].values
x35 = NodeVolDF['0.35d'].values
x50 = NodeVolDF['0.5'].values
x65 = NodeVolDF['0.65d'].values
x75 = NodeVolDF['0.75d'].values
x90 = NodeVolDF['0.9d'].values
x95 = NodeVolDF['0.95d'].values
# x35log = NodeVolDF['0.35dlog'].values
# x65log = NodeVolDF['0.65dlog'].values

X05 = sm.add_constant(x05)
X10 = sm.add_constant(x10)
X25 = sm.add_constant(x25)
X35 = sm.add_constant(x35)
X50 = sm.add_constant(x50)
X65 = sm.add_constant(x65)
X75 = sm.add_constant(x75)
X90 = sm.add_constant(x95)
X95 = sm.add_constant(x95)
# X35l = sm.add_constant(x35log)
# X65l = sm.add_constant(x65log)


#OLS(Y,x)
model = sm.OLS(x75,X65).fit()
print(model.summary())

model2 = sm.OLS(x90,X65).fit()
print(model2.summary())

model3 = sm.OLS(x90,X75).fit()
print(model3.summary())

model4 = sm.OLS(x35,X65).fit()
print(model4.summary())

model5 = sm.OLS(x65,X35).fit()
print(model5.summary())

model6 = sm.OLS(x65, X50).fit()
print(model6.summary())

model7 = sm.OLS(x35, X50).fit()
print(model7.summary())



# Plot
plt.scatter(x35, x65)
plt.title('Scatter plot 35/65')
plt.xlabel('x35')
plt.ylabel('x65')
plt.show()

# log model does not increase R^@
# model4l = sm.OLS(x35log,X65l).fit()
# print(model4l.summary())
#
# model5l = sm.OLS(x65log,X35l).fit()
# print(model5l.summary())
#endregion
