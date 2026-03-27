#!/usr/bin/env python3
from libs.ConsoleInput import ConsoleInput
from libs.SetUp import SetUp
from libs.ColateralCleanUp import ColateralCleanUp
from libs.ParseMtpl import ParseMtpl
from libs.ParsePlist import ParsePlist
#import pandas as pd # type: ignore
def main ():

    userInfoObj = ConsoleInput()
    userInfoObj.parseArguments()
    ##print("user info:", userInfoObj.args)
    setUpConfig = SetUp(userInfoObj.args)
    setUpConfig.setUpLogger()
    cleanColateral=ColateralCleanUp(userInfoObj.args,setUpConfig.mtplFileName)
    cleanMtpl = cleanColateral.CleanUp("mtpl")
    cleanColateral=ColateralCleanUp(userInfoObj.args,setUpConfig.plistFileName)
    cleanPlist = cleanColateral.CleanUp("plist")
    parseMtplPlist =ParseMtpl(userInfoObj.args,cleanMtpl,cleanPlist,setUpConfig.flowName,setUpConfig.regexDef)
    hashMtpl =parseMtplPlist.paserCleanMtplFile()
    #projectPath = setUpConfig.validateInputs()
    #dieRecipes = setUpConfig.validateInputsRecipe()
    #print("config_var", dieRecipes)
    #ArchiveParserClass = ArchiveParser(userInfoObj.args, projectPath,dieRecipes)

if __name__== "__main__":

    main()
