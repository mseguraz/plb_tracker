
import json
import logging
import os
import re
import sys


class SetUp(object):

    def __init__(self, args):
        self.args = args
        self.pathToFlowName = os.path.dirname (os.path.realpath(__file__)) + "/../../cfg/"+ self.args.product.lower()  +"/flowName.json"
        self.flowName = self.readProjectsConfig(self.pathToFlowName)
        self.pathToMtplFileName = os.path.dirname (os.path.realpath(__file__)) + "/../../cfg/"+ self.args.product.lower()  +"/mtplFileName.json"
        self.mtplFileName = self.readProjectsConfig(self.pathToMtplFileName)
        self.pathToPlistFileName = os.path.dirname (os.path.realpath(__file__)) + "/../../cfg/"+ self.args.product.lower()  +"/plistFileName.json"
        self.plistFileName = self.readProjectsConfig(self.pathToPlistFileName)
        self.pathToRegexDef = os.path.dirname (os.path.realpath(__file__)) + "/../../cfg/"+ self.args.product.lower()  +"/regexDef.json"
        self.regexDef = self.readProjectsConfig(self.pathToRegexDef)
        self.pathToPatternPlistName = os.path.dirname (os.path.realpath(__file__)) + "/../../cfg/"+ self.args.product.lower()  +"/patternPlistName.json"
        self.patternPlistName = self.readProjectsConfig(self.pathToPatternPlistName)
        #print ("Paths:", self.pathToFlowName,self.pathToMtplFileName,self.pathToPatternPlistName,self.pathToPlistFileName,self.pathToRegexDef,self.pathToRegexDef)
        self.actualPath = os.getcwd()
        self.mainOutputDir = self.getMainOutputDir()
        self.createOutputDir()

    def setUpLogger(self):
        os.chdir(self.mainOutputDir)
        logging.basicConfig(level=logging.DEBUG, filename='Report.log', filemode='w')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)
        logging.info(" " * 30 + "Output Dir : " + self.mainOutputDir)
        os.chdir("..")

    def getMainOutputDir(self):
        outputDir = "ReportTool"
        iteration = 1
        while os.path.exists(self.actualPath + "/" + outputDir):
            outputDir = "ReportTool"
            outputDir = outputDir + "_" + str(iteration)
            iteration += 1
        return outputDir

    def createOutputDir(self):
        print (self.mainOutputDir)
        os.mkdir(self.mainOutputDir)
    
    def readProjectsConfig(self, path):
        if os.path.isfile(path):
            data=self.loadJson(path)
        else:
            logging.warning("No files found for " + path)
            data =[]
            return 0
        return data

    def loadJson(self, pathToJsonFile):
        with open(pathToJsonFile, 'r') as jsonFile:
            data = json.load(jsonFile)
        return data
    