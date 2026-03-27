import json
import logging
import os
import re
import sys
import copy
from libs.ParsePlist import ParsePlist
#from libs.CsvGen import CsvGen

class ParseMtpl(object):
    def __init__(self,args,mtplFile,plistFile,cfgFile,regexFile):
        self.args=args
        self.mtpl=mtplFile
        self.plist=plistFile
        self.configFile=cfgFile
        self.regexFile=regexFile
        self.die= args.die
        self.testProgram = args.testprogram
        self.tableName= args.tableName 
        self.product =args.product
        self.chop= args.chop
        self.operation= args.operation
        self.socket=args.socket
        self.step=args.step
        
    def setVarsPerDie (self,die):
        self.mtplEdcKill=[]
        self.plbs={}
        self.hashData={}
        self.audit_items={}

        self.instance=str(self.regexFile[self.product][die+"_"+self.socket]["intance"])
        self.composite=str(self.regexFile[self.product][die+"_"+self.socket]["composite"])
        self.split=str(self.regexFile[self.product][die+"_"+self.socket]["setBin"])
        self.startInstace=str(self.regexFile[self.product][die+"_"+self.socket]["startInstace"])
        self.startPlist=str(self.regexFile[self.product][die+"_"+self.socket]["startPlist"])
        self.plbCall=str(self.regexFile[self.product][die+"_"+self.socket]["plbcall"])
        self.process_map=self.regexFile[self.product][die+"_"+self.socket]["process_map"]
        self.bypassPortRuleMap=self.regexFile[self.product][die+"_"+self.socket]["bypassPortRuleMap"]
        self.skipPlist=self.regexFile[self.product][die+"_"+self.socket]["skipPlist"]
        self.delimiter=self.regexFile[self.product][die+"_"+self.socket]["DelimitersPosition"]
        self.recipeMap=self.regexFile[self.product][die+"_"+self.socket]["recipeMap"]
        self.module=str(self.regexFile[self.product][die+"_"+self.socket]["module"])
        self.chunkNumber=self.delimiter["chunkNumber"]
        self.scanRegion=self.delimiter["scanRegion"]
        self.revision=self.delimiter["revision"]
        self.flavor=self.delimiter["flavor"]
        self.type=self.delimiter["type"]
        self.phase=self.delimiter["phase"]
        self.regex=(self.instance,self.composite,self.split,self.startInstace,self.plbCall)
        parsePlist =ParsePlist(self.args,self.mtpl,self.plist,self.configFile,self.regexFile,die)
        #printList=CsvGen(self.args,self.regexFile,self.configFile)   


    def paserCleanMtplFile(self):
        fullInfoTP=[]
        #print ("mtpl:", self.mtpl)
        if self.die == "null":
            for die_socket in self.configFile[self.product].keys():
                die=die_socket.split("_")[0]
                logging.info(" " * 20 + "Die: " + die)
                #print("die if NULL:", die)
                self.setVarsPerDie(die)
                fullInfo=self.parse_die(die)
                for line in fullInfo:
                    fullInfoTP.append(line)
        else:
            logging.info(" " * 20 + "Die: " + self.die)
            #print("die:", self.die)
            self.setVarsPerDie(self.die)
            fullInfo=self.parse_die(self.die)
            fullInfoTP=fullInfo
        
       # hash_fullInfo=CsvGen.gen_csv_all_info(self,fullInfoTP)
                    

        #print("Plist Info",fullInstaceInfo)
        #hash_fullPlistInfo=CsvGen.gen_csv_plist(self,fullPlistInfo)
        #hash_fullInstaceInfo=CsvGen.gen_csv_instance(self,fullInstaceInfo,flows)
        
        #print("Instance Info",fullPlistInfo)
             #   #For txt instance audit
             #   items2=get_dutflow_items_for_audit(flow, class_mtpl)
             #   audit_items[flow]=items2
             #   if args.format.lower()=='txt':
             #       with open(audit_table, "a", encoding="utf-8") as file:
             #           file.write(flow+'\n\n')
             #       print_structured_table(items2, audit_table)


    def parse_die (self,die):
        hashPlistInfo={}
        hashInstaceInfo={}
        fullPlistInfo=[]
        fullInstaceInfo=[]
        fullInfo=[]
        missingPlist=[]
        #load flows
        flows=self.configFile[self.product][die+"_"+self.socket]
        #print ("flows",flows)
        flowNames=[key for flow in [flows] for key in flow.keys()]
        #print("flownames: ", flowNames)

        for tpRegion in flows:
            for flow in flows[tpRegion]:
                #print("Region:",tpRegion,"Flow:",flow)
                items,plistInfo,instanceInfo,hashPlistInfo=self.get_dutflow_items(flow,self.mtpl,self.regex)
                #self.plbs[flow]= items if flow not in self.plbs else self.merge_dictionaries(self.plbs[flow], items)
                #logging.info(" " * 25 + "Flow INFO: ")
                #logging.info(" " * 28 + "Region: "+ region)
                #logging.info(" " * 28 + "Sub Flow: "+ flow)
                #print("Global INFO:")
                #print("Regio:", tpRegion)
                #print("Flow:",flow)
                #print("Plist Info",plistInfo)
                #print("Instance Info",instanceInfo)
                
                for line in plistInfo:
                    #print("linea",line)
                    #line.append(region)
                    fullPlistInfo.append(line)
                for line in instanceInfo:                    
                    newLine=[line[0],line[1],line[2],line[3],tpRegion]

                    #print ("line",newLine)
                    fullInstaceInfo.append(newLine)
                    #hashTuples[plistname]={region_:{flavor_:{phase_:{"chunks":chunks}}}}

                    if line[3] in hashPlistInfo.keys():                      
                        for region in hashPlistInfo[line[3]].keys():
                            #print("region:", region)
                            #print("tpregion:", tpRegion)
                            for flavor in hashPlistInfo[line[3]][region].keys():
                                #print ("flavor:",flavor)
                                for phase in hashPlistInfo[line[3]][region][flavor].keys():
                                    #print ("phase:", phase)
                                    chunks=hashPlistInfo[line[3]][region][flavor][phase]["chunks"]
                                    #print ("chunks",chunks)
                                    ratio=tpRegion.split("_")[-1]
                                    powerPlane=tpRegion.split("_")[2]
                                    instance=line[1]
                                    plist=line[3]
                                    edcStatus=line[2]
                                    newFlavor=self.map_flavor(flavor)
                                    #print("flavor", flavor,newFlavor)
                                    newdie= str(die).replace("pkg","")

                                    #print("die",newdie,die)

                                    lineTotalInfo=[newdie,self.module,flow,instance,ratio,powerPlane,plist,edcStatus,region,newFlavor,phase,chunks]
                                    #print("full info line 151",lineTotalInfo)
                                    fullInfo.append(lineTotalInfo)
                    else:
                        print("PLB:", line[3], " in not in plist,from instace:",flow )
                        missingPlist.append(flow,)
                        #break

        #print("info",fullInfo)
        return fullInfo


    def map_flavor(self,flavor):
        newFlavor=self.recipeMap[flavor]
        return newFlavor

    def get_dutflow_items(self,flow,mtpl_file,regex):    
        flow_instances=self.get_flow_with_instances(flow,mtpl_file,regex)
        #print ("Flow Instances 134: ", flow_instances)
        fullInfo={}
        plist=[]
        plistInfo=[]
        hashEDC={}
        hashBYP={}
        hashPlis={}
        hashInstance={}
        listInstace=[]
        data=[]
        dataInstance=[]
        for f in flow_instances:
            #print ("f:",f)
            #self.hashData[flow]={f:{}}
            for instance in flow_instances[f]:
                #print("instace",instance)
                cond=False
                EDC=False
                bypassed=False
                to_append=None
                #print(instance)
                for line in mtpl_file:                  
                    #Get the main flow
                    #print("split",self.split)
                    if (line.startswith(tuple(self.startInstace)) or line.startswith('MultiTrialTest')) and self.contains_exact_word(line, instance): ##check TOS4
                        cond=True
                        #print("line",line)
                        #Skip core 
                        if '_CORE_' in line:
                            break
                        if 'EDC' in line:
                            EDC=True

                        else:
                            for ln in mtpl_file:
                                if str(self.instance) in ln and self.contains_exact_word(ln, instance) and 'EDC' in ln:
                                    EDC=True
                                    
                                    break

                    # Instance is bypassed
                    if cond and 'BypassPort' in line:
                        # for sort instance is either bypass or not
                        #print ("line:",line)
                        chekcLine=copy.deepcopy(line)
                        bypStatus = self.bypassDefRule(chekcLine)
                        #print("line", line,bypStatus)
                        if (self.socket == 'sort') and bypStatus:
                            #print("This instance is Bypass:", instance)
                            logging.info(" " * 20 + "This instance is Bypass: "+  instance + line)
                            data=[f,instance,"null", True]
                            #logging.info("------" * 15)
                            break
                        elif self.socket == 'class' and bypStatus:
                            #print("This instance is Bypass,", instance)
                            logging.info(" " * 20 + "This instance is Bypass: " + instance + line)
                            #logging.info("------" * 15)
                            data=[f,instance,"null", True]
                            ##listInstace.append(data)
                            #print("DATA BYP:",f,instance, ["null", True])
                            #print(line)
                            bypassed=True
                            break

                    if cond and ('Patlist' in line or 'patlist' in line) and '"Patlist"' not in line:      
                        # Count occurrences of the substring
                        occurrences = line.count('_Rules.')

                        # Check if the word appears twice or more
                        if occurrences >= 2:
                            logging.info(" " * 20 + "Patlist with several rules: " + instance + line)
                            value=self.get_plist_with_rules(line, self.chop)
                            to_append=[value, EDC]

                        elif occurrences > 0  and self.socket == "sort":
                            value=self.get_plist_with_rules(line, self.chop )
                            to_append=[value, EDC]

                        else:
                            #print("The word appears less than twice.")
                            #print('aca', instance, line)
                            value = line.split('=')[1]
                            valueMultiPlist=line.split('=')
                            if "::" in value:
                                value = line.split(':')[2]
                            value=value.strip().strip("\";'"),
                            #print('aca 220', instance,line)

                            #print(value[1].strip().strip("\";"), '\n')
                            
                            # Check for value inside parentheses first
                            match = re.search(r'\((.*?)\)', valueMultiPlist[1])
                            #print('aca', instance,value,match)
                            if match: ## CHEKC for multi plis GNR mseguraz
                                logging.info(" " * 20 + "Multiples plist: " + instance + line)
                                
                                valueMultiPlist=match.group(1).split(',')
                                if len(value)==4:
                                    to_append=[valueMultiPlist[self.process_map[self.chop][0]].strip("\"'"), EDC]
                                else:
                                    to_append=[valueMultiPlist[0].strip("\"'"), EDC] if 'hot' in self.chop else [valueMultiPlist[1].strip("\"'"), EDC]
                                    #print(value, process)
                            else:
                                #print('aca', instance,value,match,value[0])
                                to_append=[value[0],EDC]
                        
                    if cond and line.startswith('}'):
                        if not bypassed:
                            #print("Instance to Append:",instance, to_append)
                            if to_append:
                                plist.append(to_append)
                                data=[f,instance,to_append[1],to_append[0]]
                                listInstace.append(data)
                        bypassed=False
                        break
            #self.hashData[flow][f]={instance:{"EDCStatus": True}}
            #self.hashData[flow][f]={}
        #print("Plist 250:",f, plist)
        #print("HASH_ins:",hashInstance)
        #print("list_instance",listInstace)     

        hathplistInfo,new_listInstace,golden_plist=self.plistInfo(listInstace) 
        #print("intance: ", instance ,"plist: ",plist, "hash", hathplistInfo)        
        print("valid plist 295:", golden_plist)
        #plbs,plbsData=self.juan_plist_info(plist)
        plbs,plbsData=self.juan_plist_info(golden_plist)     
        
        
        #return plbs, plbsData, listInstace, hathplistInfo
        return plbs, plbsData, new_listInstace, hathplistInfo        


    ####
    ####
    ####
    def bypassDefRule (self,line):
        #forDMR
        
        if 'COLD_BYPASS' in line:
            rule=line.split("=")[1].split(".")[1]
            rule=str(rule.strip().strip("\";'"))
            ruleValue=self.bypassPortRuleMap[rule][self.operation]
            #print("rule 268",rule,ruleValue)                             

        elif 'UCCAP_BYPASS' in line or ('UCCX1_BYPASS' in line):
            rule=line.split("=")[1].split(".")[1]
            rule=str(rule.strip().strip("\";'"))
            ruleValue=self.bypassPortRuleMap[rule][self.chop]
            #print("rule 274",rule,ruleValue)
        elif '-1' not in line:
            ruleValue=True
            #print("rule line 277: ",ruleValue,rule)
        else: 
            ruleValue=False
        return ruleValue


        
    def plistInfo (self,listInstace):
        #print ("data: ",listInstace)
        hashTuples={}
        firstLine=True
        valid_list=copy.deepcopy(listInstace)
        valid_plist=[]

        for line in listInstace:
            flow= line[0]
            instance=line[1]
            plistname=line[3]
            edc=line[2]
            chunks=0
            tuplesList=ParsePlist.get_plist(self,self.plist,plistname)
            if len(tuplesList) ==0 and edc is True:
                logging.error(" " * 20 + plistname +" plist is empty for kill instace: "+ instance)
                valid_list.remove(line)
                
            elif len(tuplesList) ==0 and edc is False:
                logging.info(" " * 20 + plistname +" plist is empty for edc instace: "+ instance)
                valid_list.remove(line)
            else: 
                valid_plist.append(plistname)
                #print("Valid Plist",plistname)
                #print("Valid LISTt", valid_list)
                #print("Orig List",listInstace)
                

            #print ("line info 336: ", line, tuplesList)
            cleanTupleList=[]  

            for tupple in tuplesList:
                #print ("tuple 340: ", tupple)
                flavor_, rev_, region_, mask_, phase_, chuck_ =self.extract_data(tupple)
                if firstLine ==True:
                    chunks=1
                    #print("chunks 1er line:",chuck_,chunks) 
                    hashTuples[plistname]={region_:{flavor_:{phase_:{"chunks":chunks}}}}
                    firstLine=False
                else:
                    if plistname in  hashTuples.keys():
                        if region_ in hashTuples[plistname].keys():
                            if flavor_ in hashTuples[plistname][region_].keys():
                                if phase_ in hashTuples[plistname][region_][flavor_].keys():
                                    chunks=chunks+1
                                    #print("chunks:",chuck_,chunks)                               
                                    hashTuples[plistname][region_][flavor_][phase_]={"chunks":chunks}
                                else:
                                    chunks=1
                                    #print("new phase:",phase_,chuck_,chunks)
                                    hashTuples[plistname][region_][flavor_][phase_]={"chunks":chunks}
                            else:
                                chunks=1
                                hashTuples[plistname][region_][flavor_]={phase_:{"chunks":chunks}}
                        else:
                            chunks=1
                            hashTuples[plistname][region_]={flavor_:{phase_:{"chunks":chunks}}}
                    else:
                            chunks=1
                            hashTuples[plistname]={region_:{flavor_:{phase_:{"chunks":chunks}}}}
                                                   
        #print ("hash: 371",hashTuples)
        return hashTuples,valid_list,valid_plist


                    


    #flavor, rev, region, mask =self.extract_data(pp) 
    # Get scan region, flavor and rev of a pattern
    def extract_data(self,input_str):
        #print ("pat line 376",input_str) 
        patternLine=input_str
        lstr=patternLine
        chunk=patternLine.split("_")[self.chunkNumber]
        scanRegion=patternLine.split("_")[self.scanRegion]
        revision=patternLine.split("_")[self.revision]
        flavor=patternLine.split("_")[self.flavor]
        if self.product == "gnr" or self.product == "gmm":
            chunk =chunk[15:18]
            if 'chain' in input_str:
                flavor='chain' 
                h_position = revision.find('h')
                revision=revision[0:h_position-1]
            elif 'dport' in input_str:
                flavor='dport'
            elif 'ca1tf' in input_str or 'ca2tf' in input_str:
                flavor='ca1tf' if 'ca1tf' in input_str else 'ca2tf'
                p_position = revision.find('p')
                revision = revision[0:p_position]
            else:
                h_position = revision.find('h')
                revision=revision[0:h_position-1]
        
        flavor=patternLine.split("_")[self.flavor]
        type=patternLine.split("_")[self.type]
        phase=patternLine.split("_")[self.phase]
        masking=False ## add funtion for patmos analysis 
        #print("data 404:",flavor,revision,scanRegion,masking,phase, chunk )
        return flavor,revision,scanRegion,masking,phase, chunk     

    def get_plist_with_rules(self, patlist, process_name):
        if "TPKNOB_Rules.DIE" in patlist:
            match = re.search(r'TPKNOB_Rules.DIE\((.*)\)', patlist)
            # Extract processes safely
            processes = []
            balance = 0
            current_process = []
            for char in match.group(1):
                if char == '(':
                    balance += 1
                elif char == ')':
                    balance -= 1
                if char == ',' and balance == 0:
                    processes.append(''.join(current_process).strip())
                    current_process = []
                else:
                    current_process.append(char)
            if current_process:
                processes.append(''.join(current_process).strip())

            # Ensure processes has exactly 4 elements
            while len(processes) < 4:
                processes.append('1')
            #print(processes)
            processes = processes[:4]
            row, col = self.process_map[process_name]
            #print(row, col)

            if row >= len(processes):
                raise ValueError("Log data contains invalid process state")

            process_value = processes[row]
            #print(process_value, row, col)

            if not process_value:
                raise ValueError("Missing process data")
            if 'DOWNSTREAM_SOCKETS' in process_value:
                rule_match = re.search(r'TPKNOB_Rules.DOWNSTREAM_SOCKETS\((.*?)\)', process_value)
                #print(rule_match)
                if rule_match:
                    rule_values = rule_match.group(1).split(',')
                    #print(rule_values)
                    if len(rule_values) != 2:
                        raise ValueError("Invalid rules format")
                    return rule_values[0].strip("\"'") if 'hot' in process_name else rule_values[1].strip("\"'")
            #else:
                #return processes[dstep].strip("\"'")
                
        elif 'TPKNOB_Rules.TEMPERATURE' in patlist:
            match = re.search(r'TPKNOB_Rules.TEMPERATURE\((.*)\)', patlist)

            # Extract processes safely
            processes = []
            balance = 0
            current_process = []
            for char in match.group(1):
                if char == '(':
                    balance += 1
                elif char == ')':
                    balance -= 1
                if char == ',' and balance == 0:
                    processes.append(''.join(current_process).strip())
                    current_process = []
                else:
                    current_process.append(char)

            if current_process:
                processes.append(''.join(current_process).strip())

            #print(processes)
            processes = processes[:2]
            #print(processes)
            row, col = self.process_map[process_name]

            process_value = processes[col]

            if not process_value:
                raise ValueError("Missing process data")
            if 'fuseIO' in process_value:
                match = re.search(r'SCN_UNCORE_IO_Rules.SCAN_fuseIO\((.*)\)', process_value)
                if match:
                    process_value=match.group(1).split(',')  
                    return process_value[1].strip("\"'")
                    #if fused:
                    #    return process_value[0].strip("\"'")
                    #else:
                    #    return process_value[1].strip("\"'")
            else:
                return process_value.strip("\"'") 
                


        # This functon gets a dictionary with subflows and the instances with plist running on them
    def get_flow_with_instances(self,flow,mtpl_file,regex):
        #Get the subflows of the main flow
        flow_order=self.get_dut_flow(flow,mtpl_file,regex)
        #print("Flow order:",flow_order)
        subflow_instances={flow: []}
        for f in flow_order:
            #print("line:411",f)
            result=self.check_further_flow(f, mtpl_file,regex)  
            if result:  
                #print('line:414', result)
                for d in result:
                    subflow_instances = self.merge_dictionaries(subflow_instances, d)
            else:
                subflow_instances[flow].append(f)
            
        #print("subflow_instances:",subflow_instances)
        return subflow_instances
        

    # Merge two dictionaries
    def merge_dictionaries(self,dict1, dict2):
        # Merge dictionaries using unpacking
        return {**dict1, **dict2}

    def check_further_flow(self,flow, mtpl_file,regex):
        mainflow=[]
        cond=False
        for line in mtpl_file:
            #self.regex=(self.instance,self.composite,self.split,self.startInstace,self.plbCall)
            #if line.startswith('DUTFlow') and flow in line and 'DUTFlowItem' not in line:
            if line.startswith(str(regex[1])) and flow in line and str(regex[0]) not in line:
                cond=True
                #print("line 437", line)
            if cond:
                mainflow.append(line)
            if cond and line.startswith('}'):
                break
        
        #If there is no main flow, is an instance
        if len(mainflow)==0:
            return False
        
        else:
            first=False
            #print ("regex line 446", regex[0], self.instance)
            for i in range(len(mainflow)):
                #print ("regex line 447", regex[0], self.instance)
                if  regex[0] in mainflow[i] and not first:
                    value = mainflow[i].strip().split()
                    #print(value[1])  # This will print name of the flow instance
                    new_flow=[value[1]]
                    #print("new_flow",new_flow)
                    break
            
            #print ("line 445", new_flow,value[1])
            new_flow+=self.get_goto(value[1], mainflow,self.regex)
        
            subflow_instances=[{flow: []}]

            for f in new_flow:
                result=self.check_further_flow(f, mtpl_file,self.regex)
                if result:
                    subflow_instances+=result
                else:
                    subflow_instances[0][flow].append(f)

            return subflow_instances

        
    # Gets the flow items of a DUT flow
    def get_dut_flow (self,flow, mtpl_file,regex):
        mainflow=[]
        cond=False
        count_corch=0
        for line in mtpl_file:
            if line.startswith(tuple(regex[1])) and flow in line: #mseguraz: change for DMR tos4
                cond=True
            if cond:
                mainflow.append(line)
            if cond and '{' in line:
                count_corch+=1
            if cond and '}' in line:
                count_corch-=1
            if cond and line.startswith('}') and count_corch==0:
                break
        
        first=False
        if len(mainflow)==0:
            logging.info(" " * 20 + "Flow"+ flow +"is not defined in mtpl." )
            print(f"Flow {flow} is not defined in mtpl")
            return []
        for i in range(len(mainflow)):
            if str(self.instance) in mainflow[i] and not first:
                value = mainflow[i].strip().split()
                #print("Flow insntance:",value[1])  # This will print name of the flow instance
                flow_order=[value[1]]
                break
        flow_order+=self.get_goto(value[1], mainflow,regex)
        return flow_order
    
    def get_goto(self,flow, flow_list, regex):
        BIN_DICTIONARY ={}
        dut=False
        result=False
        softbin=False
        #print('here', flow)
        for i in range(len(flow_list)):
            #It's very important to match the exact name of the DUT item
            if str(regex[0]) in flow_list[i] and self.contains_exact_word(flow_list[i], flow):
                dut=True
            if dut and 'Result 0' in flow_list[i]: #Fail bin
                softbin=True

            #Fail bin
            if softbin and dut and 'SetBin' in flow_list[i]:
                #print ("here2",flow_list[i])
                value = flow_list[i].strip().split()
                value = value[1].split('_')[0]
                #print ("here3",value,self.split)
                if str(self.split) in value:
                    value = value.split(str(self.split))[1]
                    #print ("here4",value,self.split)

                #value = value[1].split('.')[1].split('_')[0] #mseguraz dif tos3 and tos4
                #print("value",value)
                BIN_DICTIONARY[flow]=value
                #print(flow, value, flow_list[i])


            if dut and 'Result 1' in flow_list[i]: #What happens if the test is successful
                result=True
                #print("Flow List Result 1:",flow_list[i])

            #Where does it go if test if successful
            if result and dut and 'GoTo' in flow_list[i]:
                value = flow_list[i].strip().split()
                value = value[1].strip().strip(";")
                #print("GOTO",value, flow_list[i])
                #print(value,flow_list[i])
                return [value]+self.get_goto(value, flow_list,regex)
            if dut and result and '}' in flow_list[i]: #If it's the last test of the flow
                #print("This is the last flow:",flow)
                return []
            
    #Check if the exact instance name is in the line
    def contains_exact_word(self,input_string, target_word):
        # Use regex to find the exact word with word boundaries
        pattern = r'\b' + re.escape(target_word) + r'\b'
        match = re.search(pattern, input_string)
        
        # Return True if an exact match is found, otherwise False
        return bool(match)
    
    def juan_plist_info(self,plist):
        plbs={}
        plbsData=[]      

        for p in plist:
                current_region=0
                previous_region=None
                previous_flavor=None
                previous_rev=None

                plbs_list=ParsePlist.get_plist(self,self.plist,p[0])
                #print("plb",p,plbs_list)
                pp_list=[]
                for i, pp in enumerate(plbs_list):
                    # this skips repeated patterns
                    #print("Plist:",p[0])
                    #print("Patter:",pp)
                    if pp in pp_list and i!=(len(plbs_list))-1:
                        continue
                    # last element
                    elif pp in pp_list and i==(len(plbs_list))-1:
                        #print(p[0],'special case last plist has repeated plbs')
                        #logging.info(" " * 20 + pp + "special case last plist has repeated plbs")
                        # if flavor is not yet in dictionary (punit for example)
                        if previous_flavor not in plbs:
                            plbs[previous_flavor]={}
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]
                        # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                        elif previous_region not in plbs[previous_flavor]:
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]
                        # if region is defined in dictionary
                        else:
                            stored_data=plbs[previous_flavor][previous_region]

                            # Store the one with the biggest rev
                            if int(stored_data[0][-1])<int(previous_rev[-1]):
                                plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                            # if there are more plbs than previously reported, uptade value
                            elif stored_data[1]<current_region and int(stored_data[0][-1])==int(previous_rev[-1]):
                                plbs[previous_flavor][previous_region][1]=current_region
                                plbs[previous_flavor][previous_region][3]=previous_mask

                            # if one is in EDC and the other not
                            elif stored_data[2]!=p[1] and stored_data[1]==current_region and int(stored_data[0][-1])==int(previous_rev[-1]):

                                #if the stored one is not in edc
                                if not stored_data[2]:
                                    pass
                                else:
                                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                        current_region=0
                        pp_list=[]
                        previous_mask=False
                    
                    flavor, rev, region, mask, phase , chunk =self.extract_data(pp)
                    #print("pat:",pp) 
                    #print("INFO 711",flavor, rev, region, mask, phase, chunk, pp,p[0])
                    if not previous_flavor:
                        previous_flavor=flavor
                        previous_region=region
                        previous_rev=rev
                        previous_mask=mask

                    if flavor!= previous_flavor or previous_region != region:
                        #print("here",previous_region, region)
                        # if flavor is not yet in dictionary (punit for example)
                        if previous_flavor not in plbs:
                            plbs[previous_flavor]={}
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                        # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                        elif previous_region not in plbs[previous_flavor]:
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                        # if region is defined in dictionary
                        else:
                            stored_data=plbs[previous_flavor][previous_region]
                            #print("here2",previous_flavor, previous_region, stored_data, previous_rev, current_region, p[1])

                            # Store the one with the biggest rev
                            if int(stored_data[0][-1])<int(previous_rev[-1]):
                                plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                            # if there are more plbs than previously reported, uptade value
                            elif stored_data[1]<current_region and int(stored_data[0][-1])==int(previous_rev[-1]):
                                plbs[previous_flavor][previous_region][1]=current_region
                                plbs[previous_flavor][previous_region][3]=previous_mask

                            # if one is in EDC and the other not
                            elif stored_data[2]!=p[1] and stored_data[1]==current_region and int(stored_data[0][-1])==int(previous_rev[-1]):

                                #if the stored one is not in edc
                                if not stored_data[2]:
                                    pass
                                else:
                                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                        current_region=0
                        pp_list=[]
                        previous_mask=False

                    current_region+=1
                    previous_flavor=flavor
                    previous_region=region
                    previous_rev=rev
                    previous_mask=previous_mask | mask
                    pp_list.append(pp)


                    if i==(len(plbs_list))-1:
                        # if flavor is not yet in dictionary (punit for example)
                        if previous_flavor not in plbs:
                            plbs[previous_flavor]={}
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                        # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                        elif previous_region not in plbs[previous_flavor]:
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                        # if region is defined in dictionary
                        else:
                            stored_data=plbs[previous_flavor][previous_region]

                            # Store the one with the biggest rev
                            if int(stored_data[0][-1])<int(previous_rev[-1]):
                                plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]

                            # if there are more plbs than previously reported, uptade value
                            elif stored_data[1]<current_region and int(stored_data[0][-1])==int(previous_rev[-1]):
                                plbs[previous_flavor][previous_region][1]=current_region
                                plbs[previous_flavor][previous_region][3]=previous_mask

                            # if one is in EDC and the other not
                            elif stored_data[2]!=p[1] and stored_data[1]==current_region and int(stored_data[0][-1])==int(previous_rev[-1]):

                                #if the stored one is not in edc
                                if not stored_data[2]:
                                    pass
                                else:
                                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask]
                    
                    
                        current_region=0
                        pp_list=[]
                        previous_mask=False
                #print("Debug Info 800",region,current_region,previous_region,flavor,previous_flavor)
                    
                info=[p[0],region,flavor,phase,plbs[flavor][region][1]]
                #info=[]
                plbsData.append(info)
        return plbs,plbsData

  
