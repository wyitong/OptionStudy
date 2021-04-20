#%%

import os
import gzip
import numpy as np
import pandas as pd
from datetime import date, datetime
ROOT = r"C:\Users\Yitong\AppData\Local\PythonProject\CryptoStudy"
os.chdir(ROOT)
import matplotlib.pyplot as plt
r2SecSpan = 2
#%%
class mdUnit:
    def __init__(self, time : datetime.timestamp, b1 : float, a1 : float, logline: str):
        self.time = time
        self.b1 = b1
        self.a1 = a1
        self.logline = logline
    def midprice(self):
        return (self.a1+self.b1)/2
    def toStr(self):
        print(f"Time: {self.time}, A1: {self.a1}, B!: {self.b1}")

class r2Unit:
    #containing enterMd, exitMd, prediciton and prediction timestamp
    def __init__(self, enterMD : mdUnit, time: datetime.timestamp, pred : float, predLine : str):
        self.enterMD = enterMD
        self.pred = pred
        self.predtime = time
        self.logline = predLine
    def attachExitMD(self, exitMD : mdUnit) -> bool:
        if(exitMD.time<self.enterMD.time):
            print(f"exitMD : {exitMD.time}")
            print(f"enterMD : {self.enterMD.time}")
            raise Exception(f"wrong md matching")
        timeDiff = (exitMD.time - self.enterMD.time).total_seconds()
        if(timeDiff>=r2SecSpan):
            self.exitMD = exitMD
            self.timeDiff = timeDiff
            return True
        else:
            return False
    def realPchg(self) -> float:
        return self.exitMD.midprice() - self.enterMD.midprice()
    def predEnterTimeDiff(self) ->float:
        return (self.predtime - self.enterMD.time).total_seconds()*1000
    def toStr(self) ->str:
        print(f"enterMD: {self.enterMD.logline}")
        print(f"pred: {self.logline}")
        print(f"exitMD: {self.exitMD.logline}")
def r2Calc(y_true, y_pred):
    r2 = np.corrcoef(y_true, y_pred)[0][1]**2
    y_bar = y_true.mean()
    # fit values, and mean
    ss_res = ((y_true-y_pred)**2).mean()
    ss_tot = ((y_true-y_bar)**2).mean()
    return r2, 1 - (ss_res/ss_tot)#r2 assumes intercept, latter does not. r2 usually higher. latter better measure as "good as prediciton"

#%%
loggzfile = "20210414.log.gz"
def log2R2(instName : str):
    print(f"start working on {instName}")
    r2List = []
    r2Buffer = []
    with gzip.open(loggzfile, 'rt') as log:
    # with open(logfile, 'r') as log:
        lineCnt = 0
        lastMd = None
        while True:
            try:
                curline = log.readline()
                if not curline:
                    break

                if("MD" in curline and instName in curline):
                    a1 = float(curline.split("A1=")[1].split(":")[0])
                    b1 = float(curline.split("B1=")[1].split(":")[0])
                    av1 = int(curline.split("A1=")[1].split(":")[1].split(",")[0])
                    bv1 = int(curline.split("B1=")[1].split(":")[1].split(",")[0])
                    if(av1==0 or bv1==0):
                        continue

                    tsStr = curline.split(" ")[1] + " " + curline.split(" ")[2]
                    ts = datetime.strptime(tsStr, "%Y%m%d %H%M%S.%f")
                    if(not lastMd == None):
                        if(lastMd.time>ts):
                            raise Exception(f"log order messy")
                    lastMd = mdUnit(ts,b1,a1, curline)
                    if(len(r2Buffer)>0):
                        buffertoCheck = len(r2Buffer)
                        while(buffertoCheck>0):
                            if(r2Buffer[0].attachExitMD(lastMd)):
                                r2List.append(r2Buffer.pop(0))
                            buffertoCheck-=1
                    lineCnt+=1
                    
                if("prediction" in curline and instName in curline):
                    prediction = float(curline.split("prediction=")[1].split(',')[0])
                    tsStr = curline.split(" ")[1] + " " + curline.split(" ")[2]
                    ts = datetime.strptime(tsStr, "%Y%m%d %H%M%S.%f")
                    if(lastMd!=None and prediction!=0):
                        r2Buffer.append(r2Unit(lastMd, ts, prediction, curline))
                        lineCnt+=1
            except Exception as ex:
                print(curline)
                print(f"{ex}")
    print(f"avg enter vs pred time diff: {np.array([r2.predEnterTimeDiff() for r2 in r2List]).mean(): >7.2f} ms")
    print(f"avg enter vs exit time diff: {np.array([r2.timeDiff for r2 in r2List]).mean(): >7.2f} s")

    realList = np.array([r2.realPchg() for r2 in r2List])
    predList = np.array([r2.pred for r2 in r2List])

    r2,R2= r2Calc(realList, predList)

    print(f"r2:{r2:>7.2%}, R2:{R2:>7.2%}")
    plt.close()
    plt.scatter(x=predList,y=realList, s = 1)
    # plt.title(f"I: {instName} R2:{r2:>7.2%}, ssres{ssres:>7.2f}, sstot{sstot:>7.2f}")
    plt.title(f"I: {instName} r2:{r2:>7.2%}, R2:{R2:>7.2%}, #Obv:{len(realList)}")
    plt.ylabel('real')
    plt.xlabel('pred')
    # plt.ylim(-0.10, 0.40)
    plt.axhline(y=0,color='red')
    datestr = loggzfile.split('.')[0]
    figname = f"{instName}_{datestr}_r2.png"
    respath = os.path.join(ROOT, "r2res",datestr)
    if not os.path.exists(respath):
        os.makedirs(respath)
    figpath = os.path.join(respath, figname)
    plt.savefig(figpath)
    print(f"done working on {instName}")
    return r2List
# %%

instList = ["BTCUSD.IPHB","BTCUSD.I1M25HB"]
# instList = ["BTCUSD.IPHB"]
for inst in instList:
    tmpr2list = log2R2(inst)
    # realList = np.array([r2.realPchg() for r2 in tmpr2list])
    # predList = np.array([r2.pred for r2 in tmpr2list])

    # df = pd.DataFrame(list(zip(([r2.realPchg() for r2 in tmpr2list]), [r2.pred for r2 in tmpr2list])))
    # df.to_csv(f"{inst}_r2.csv")


# #%%
# #%%
# from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
# # %%
# loggz= "20210414.log.gz"
# connStr = "DefaultEndpointsPrtocol=https;AccountName=awslog;AccountKey=PBij1E61KgGnJIlwnfIUljbF9FrYlaXDNRxx4hAWhiHwysNsXuJqcf/7fnJy7tYTaFBPYJkTiP435Zrxj5cxYQ==;EndpointSuffix=core.chinacloudapi.cn"
# blob_service_client = BlobServiceClient.from_connection_string(connStr)
# container_client =blob_service_client.get_container_client("huobi")
# blob = BlobClient.from_connection_string(conn_str=connStr, container_name="huobi", blob_name=f"vibc/{loggz}").
# # %%
# # %%

# downloadedgz = blob.download_blob().
# #%%
# #%%
# log = gzip.decompress(downloadedgz)    
# log = log.decode('utf-8')
# while True:
#     cnt=0
#     if(cnt>10):
#         break
#     curline = log.readline()
#     cnt+=1
#     print(curline)
# # %%
# blob.download_blob()

# %%
