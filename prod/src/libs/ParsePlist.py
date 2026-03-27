import json
import logging
import os
import re
import sys
import time
import subprocess
import argparse

class ParsePlist(object):
    def __init__(self,args,mtplFile,plistFile,cfgFile,regexFile,die):
        self.configFile=cfgFile
        self.fullPlist=plistFile
        self.mtpl=mtplFile
        self.mtplEdcKill=[]
        self.plbs={}
        self.plist=[]
        self.audit_items={}
        self.testProgram = args.testprogram
        self.tableName= args.tableName
        self.die= die
        self.product =args.product
        self.chop= args.chop
        self.operation= args.operation
        self.socket=args.socket
        self.instance=str(regexFile[self.product][self.die+"_"+self.socket]["intance"])
        self.composite=str(regexFile[self.product][self.die+"_"+self.socket]["composite"])
        self.split=str(regexFile[self.product][self.die+"_"+self.socket]["setBin"])
        self.skipPlist=regexFile[self.product][self.die+"_"+self.socket]["skipPlist"]
        self.plbCall=str(regexFile[self.product][self.die+"_"+self.socket]["plbcall"])
        self.startInstace=str(regexFile[self.product][self.die+"_"+self.socket]["startInstace"])
        self.startPlist=str(regexFile[self.product][self.die+"_"+self.socket]["startPlist"])
        self.process_map=regexFile[self.product][self.die+"_"+self.socket]["process_map"]
        self.regex=(self.instance,self.composite)

    def paserCleanPlistFile(self):
        pass

        #Check if the exact instance name is in the line
    def contains_exact_word(self,input_string, target_word):
        # Use regex to find the exact word with word boundaries
        pattern = r'\b' + re.escape(target_word) + r'\b'
        match = re.search(pattern, input_string)
        # Return True if an exact match is found, otherwise False
        return bool(match)

    #Get plist
    def get_plist(self,plist_text,hotreset):
        plist_list=[]
        current_object = []
        text=[]
        burst=False
        
        while hotreset[-1:]=='\r' or hotreset[-1:]=='\n':
            hotreset=hotreset[0:-1]

        #print("hotreset=Plist 57",hotreset)
        for line in plist_text:
            #Each plist begints with Global
            
            if line.startswith(str(self.startPlist)) and '#' not in line:           
                #If the object has content add to the plist list
                #print ("starTag",self.startPlist, line)
                if current_object:
                    if burst:
                        burst=False   
                        text.append(current_object)
                        
                        for pat in current_object:
                            plist_list.append(pat)

                        current_object = []
                    else:
                        text.append(current_object)
                        current_object = []
                
                if self.contains_exact_word(line, hotreset):
                    burst=True  
                    
                current_object.append(line) 
                
            else:
                #print("line",line)
                current_object.append(line)
        
        #print(plist_list)
        patterns=[]
        #print("Pat88",plist_list)
        for p in plist_list:
            if self.startPlist in p:
                continue
            elif 'Skip' in p or 'Hph' in p or 'H1hot' in p or p.strip().startswith('#'): ## mseguraz
                continue

            elif all(these not in p for these in self.skipPlist):
                #print ("pat:96", p)  
                if 'Pat' in p:
                    value = p.split()
                    patterns.append(value[1].strip().strip(";"))
                elif self.plbCall in p and self.startPlist not in p:
                    value = p.split()
                    #print("pat:", value[1].strip().strip(";"))
                    patterns+=ParsePlist.get_plist(self,plist_text,value[1].strip().strip(";"))
        #print(patterns)
        return patterns
        '''
        with open(output_file, 'a') as file:
            for line in plist_list:
                if line=='\r' or line=='\n':
                    continue
                file.write(line)
        '''
        
    #Get okist for audit
    def get_plist_audit(self,plist_text, hotreset, audit):

        plist_list=[]
        current_object = []
        text=[]
        burst=False
        
        while hotreset[-1:]=='\r' or hotreset[-1:]=='\n':
            hotreset=hotreset[0:-1]
        
        #print(hotreset)
        audit.append(hotreset)
        for line in plist_text:
            
            #Each plist begints with Global
            if "GlobalPList" in line and '#' not in line:
            
                #If the object has content add to the plist list
                if current_object:
                    if burst:
                        burst=False   
                        text.append(current_object)
                        
                        for pat in current_object:
                            plist_list.append(pat)

                        current_object = []
                    else:
                        text.append(current_object)
                        current_object = []
                
                if self.contains_exact_word(line, hotreset):
                    burst=True  
                    
                current_object.append(line) 
                
            else:
                current_object.append(line)
        
        #print(plist_list)
        patterns=[]
        for p in plist_list:
            if self.plist in p:
                continue
            elif 'Skip' in p or 'Hph' in p or 'H1hot' in p or p.strip().startswith('#'):
                continue
            elif all(these not in p for these in self.skip):
                if 'Pat' in p:
                    value = p.split()
                    #print(value)
                    patterns.append(value[1].strip().strip(";"))

                elif self.plbCall in p and self.plist not in p:
                    value = p.split()
                    out1, out2=self.get_plist_audit(plist_text, value[1].strip().strip(";"), [])
                    patterns+=out1
                    audit+=out2
        #print(patterns)
        return patterns, audit
