import json
import logging
import os
import re
import sys
import csv
import datetime
import pandas as pd # type: ignore

class CsvGen(object):
    def __init__(self,args,regex,configFile):
        self.args=args
        self.regex=regex
        self.testProgram = args.testprogram
        self.tableName= args.tableName
        self.die= args.die
        self.product =args.product
        self.chop= args.chop
        self.operation= args.operation
        self.socket=args.socket
        self.step=args.step
    

    def printInfoCsv(self,hash,fileType):
        pass


    def gen_csv_plist (self,list):
        list_info=[]
        for line in list:
            print("Plist: ",line)
            hash_info = {}
            hash_info["plist"]=line[0]
            hash_info["group"]=line[1]
            hash_info["recipe"]=line[2]
            hash_info["phase"]=line[3]
            hash_info["chunks"]=line[4]
            list_info.append(hash_info)
        df = pd.DataFrame(list_info)
        #TpName=self.tesc
        #print("df:",df)
        #df.to_csv('plist_info.csv', index=False)
            

    def gen_csv_instance (self,list,flow):
        hash={}
        list_info=[]
        #print("Module", self.module)
        for line in list:
            print("Instace: ",line)
            hash_info = {}
            hash_info["module"]="SCN"
            hash_info["subflow"]=line[4]
            hash_info["instance"]=line[1]
            hash_info["ratio"]="ratio"
            hash_info["power_plane"]="powerPlane"
            hash_info["plist"]=line[3]
            if line[2]=="false":
                hash_info["status"]="kill"
            else:
                hash_info["status"]="edc"
            list_info.append(hash_info)
        df = pd.DataFrame(list_info)
        #print("df:",df)
        #df.to_csv('plist_info.csv', index=False)


    def gen_csv_all_info (self,list):
        hash={}
        list_info=[]
        fileName="fileName.csv"
        #print("Module", self.module)
        for line in list:
            #print("Instace: ",line)
            hash_info = {}
            hash_info["die"]=line[0]
            hash_info["module"]=line[1]
            hash_info["subflow"]=line[2].split("_")[3]
            hash_info["instance"]=line[3]
            hash_info["ratio"]=line[4]
            hash_info["power_plane"]=line[5]
            hash_info["plist"]=line[6]
            #print("status",line[7])
            if str(line[7])=="False":
                hash_info["status"]="kill"
            else:
                hash_info["status"]="edc"
            hash_info["group"]=line[8]
            hash_info["recipe"]=line[9]
            hash_info["phase"]=line[10]
            hash_info["chunks"]=line[11]


            list_info.append(hash_info)
        df = pd.DataFrame(list_info)
        #print("df:",df)
        #DummyTP_DMR_class_A0_2_1_2025.csv
        time = datetime.datetime.now()
        self.step.upper()
        self.product.upper()
        tpName=self.testProgram.rstrip('/').split("/")[-1]
        if self.die == "null":   
            fileName= str(tpName)+'_'+str(self.product).upper()+'_'+str(self.chop)+'_'+str(self.socket)+'_'+str(self.step).upper()+'_'+ str(time.day) +'_'+str(time.month)+'_'+str(time.year)+'.csv'
        else: 
            fileName= str(tpName)+'_'+str(self.product).upper()+'_'+str(self.die).upper()+'_'+str(self.chop)+'_'+str(self.socket)+'_'+str(self.step).upper()+'_'+ str(time.day) +'_'+str(time.month)+'_'+str(time.year)+'.csv'

        print("filename",fileName)
        df.to_csv(fileName, index=False)
            