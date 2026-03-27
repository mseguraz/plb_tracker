import json
import logging
import os
import re
import sys


class ColateralCleanUp(object):
    def __init__(self, args,cfgFile):
        self.configFile= cfgFile
        self.testProgram = args.testprogram
        self.tableName= args.tableName
        self.die= args.die
        self.product =args.product
        self.chop= args.chop
        self.operation= args.operation
        self.socket=args.socket
        self.plistPath=""
    
    def CleanUp(self,fileType):
        #print("arg:",fileType)
        #print(self.configFile)
        cleanFile=[]
        if self.die is "null": # loop to concatenate the mtpls
            for die in self.configFile[self.product][self.socket].keys():
                die.split("_")[0]
                print("die to clean mtpl:", die)
                cleanMtpliPlist=self.parseMtplPlist(die,fileType)
                for line in cleanMtpliPlist:
                    cleanFile.append(line)
            return cleanFile
        else:
            cleanMtpliPlist=self.parseMtplPlist(self.die,fileType)      
            return cleanMtpliPlist
        #print ("file clean",self.cleanPlist)

    def parseMtplPlist(self,die,fileType):
        cleanFile=[]
        if fileType == "mtpl":

                if self.validatePath(self.testProgram +self.configFile[self.product][self.socket][die][self.chop][0]):
                    filePath= self.testProgram +self.configFile[self.product][self.socket][die][self.chop][0]
                    print("file path mtpl:", filePath)
                    cleanFile = self.cleanFiles (filePath)
                else:
                    print("No valid path for mtpl")
                    #print ("file clean",self.cleanPlist)
        elif fileType == "plist":
                numPlist=len(self.configFile[self.product][self.socket][die][self.chop])
                #print("numPlist",numPlist)
                for i, pp in enumerate(self.configFile[self.product][self.socket][die][self.chop]):
                    #print("numPlist",pp, i)

                    filePathEnv= self.testProgram + pp[2]
                    print("file path env:", filePathEnv)
                    # Get plist path with patch used by TP
                    with open(filePathEnv, 'r') as file:
                        for line in file:
                            if line.startswith(pp[1].upper()+"_PATMODIFY_PATH"):
                            # Split the line by the equals sign and strip any whitespace
                                parts = line.split('=', 1)
                                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                                plist_path = parts[1].strip().strip(" ';\"")
                                plist_path=plist_path.replace('\\', '/')
                                #print ("plist_path",plist_path)
                                break
                    # Get plist path in the adress of the TP
                    program_plist = plist_path.find('/')
                    # Get the base path up to 'program' from TP path
                    base_path = '/intel/'
                    # Get the suffix path after 'program' from plist path
                    suffix_path = plist_path[program_plist + len('\\'):]
                    #print("sufix",suffix_path)
                    # Combine the base path with the suffix path 
                    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
                    filePath=plist_path.replace('cfg', 'plb/' + pp[0])
                    if self.validatePath(filePath):
                        print("file path plist:", filePath)
                        self.plistPath=filePath
                        cleanFilei = self.cleanFiles (filePath)
                    else:
                        print("No valid path for plist found in the Env file with chop:", pp[1].upper())             
                    
                    for line in cleanFilei:
                        cleanFile.append(line)
        return cleanFile


    def cleanFiles (self,filePath):
        cleanFile=[]
        with open(filePath, 'r') as file:
            for line in file:
                if '#' in line:
                    result=line.split('#')[0].strip()  # delete comments from mtpl
                    cleanFile.append(result)
                else:
                    cleanFile.append(line)
        return cleanFile

        

    
    
    def validatePath(self, path):
        fileFound = False
        if not os.path.exists(path):
            logging.error ( " " * 30 + path + " not found")
            logging.error ( " " * 30 + "Path: " + path)
        else:
            fileFound = True
        return fileFound      
    
    def nateTp (self,path):
        tpName= ""
        #DMR:I:\hdmxprogs\dmr\DMRSVXXXXHX0L10S542\Shared\Common\UservarDefinitions_shared.usrv
        #GNR:I:\engineering\dev\dcd\scan\jasonfon\GNR\TEST_PROGRAM\HOLA_MUNDO_TP_WW45\Shared\Common\UservarDefinitions.usrv
        return tpName
 