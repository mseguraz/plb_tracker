import argparse
import sys
import subprocess
import os
import re
import copy
import importlib.util

TARGET_PYTHON = "/nfs/site/disks/mdo_dcd_001/scan/jspereir/Scripts/gnr_plb_tracker/env/bin/python"  # Change this to your target Python interpreter
print(sys.executable)
if sys.executable != TARGET_PYTHON:
    print(f"Restarting script with {TARGET_PYTHON}...")
    subprocess.run([TARGET_PYTHON, *sys.argv])
    sys.exit()  # Exit the current script to prevent duplicate execution

print(f"Running with {sys.executable}")

from generate_table_cwf import generate_excel_tables, generate_excel_tables_audit
from get_plist import get_plist, contains_exact_word, get_plist_audit
from chop_bypass_cwf import process_map, is_executed
from tabulate import tabulate

UNCORE_MTPL='SCN_UNCORE_COMP.mtpl'
HVQK_MTPL='SCN_UNCOREHVQK_COMP.mtpl'
CLASS_MTPL='SCN_SCAN_COMP.mtpl'
IO_MTPL='SCN_UNCORE_IO.mtpl'
IO_HVQK_MTPL='SCN_UNCOREHVQK_IO.mtpl'
IO_CLASS_MTPL='SCN_UNCORE_IO.mtpl'

PATMOD = set()

FLOWS_UNCORE={'begin': ['SCN_UNCORE_COMP_BEGIN'], 
              'end atpg': ['ATPG'], 
              'end tatpg': ['TATPG'],
              #'end edc': ['UNCORE_END_EDC'],
              'exvf': ['SCN_UNCORE_COMP_EXVF'],
              'sdt atpg' : ['SDT_ATPG'],
              'sdt tatpg' : ['SDT_TATPG']}

FLOWS_HVQK={'prehvqk': ['SCN_UNCOREHVQK_COMP_PREHVQK'],
            'posthvqk': ['SCN_UNCOREHVQK_COMP_POSTHVQK'], 
            'vmax': ['SCN_UNCOREHVQK_COMP_VMAX']}

FLOWS_CLASS={
    'begin_atpg': ['atpg_comp_hvm_begin'],
    'begin_tatpg': ['tatpg_comp_hvm_begin'],
    'srh_vccinf': ['SCN_SCAN_COMP_SRH_VCCINF'],
    'chk_vccinf': ['SCN_SCAN_COMP_CHK_VCCINF'],
    'vmax_vinf': ['SCN_SCAN_COMP_VMAX_VINF'],
    'srh_cfchdc_f1': ['SCN_SCAN_COMP_SRH_CFCHDC_F1'],
    'chk_cfchdc_f1': ['SCN_SCAN_COMP_CHK_CFCHDC_F1'],
    'srh_cfchdc_f2': ['SCN_SCAN_COMP_SRH_CFCHDC_F2'],
    'chk_cfchdc_f2': ['SCN_SCAN_COMP_CHK_CFCHDC_F2'],
    'srh_cfchdc_f3': ['SCN_SCAN_COMP_SRH_CFCHDC_F3'],
    'srh_cfchdc_f4': ['SCN_SCAN_COMP_SRH_CFCHDC_F4'],
    'chk_cfchdc_f4': ['SCN_SCAN_COMP_CHK_CFCHDC_F4'],
    'vmax_cfccomp': ['SCN_SCAN_COMP_VMAX_CFCCOMP'],
    'srh_ddrd_f1': ['SCN_SCAN_COMP_SRH_DDRD_F1'],
    'chk_ddrd_f1': ['SCN_SCAN_COMP_CHK_DDRD_F1'],
    'srh_ddrd_f2': ['SCN_SCAN_COMP_SRH_DDRD_F2'],
    'chk_ddrd_f2': ['SCN_SCAN_COMP_CHK_DDRD_F2'],
    'srh_ddrd_f3': ['SCN_SCAN_COMP_SRH_DDRD_F3'],
    'chk_ddrd_f3': ['SCN_SCAN_COMP_CHK_DDRD_F3'],
    'vmax_ddrd': ['SCN_SCAN_COMP_VMAX_DDRD'],
    'end_extest': ['EXTEST'],
    'end_atpg': ['ATPG'],
    'lttc': ['LTTC'],
    'i2td': ['I2TD'],}

FLOWS_IODIE={
    'begin': ['SCN_UNCORE_IO_BEGIN'], 
    'end atpg': ['ATPG_END'], 
    'end tatpg': ['TATPG_END'],
    'exvf': ['SCN_UNCORE_IO_EXVF'],
    'sdt atpg' : ['SDTEND_ATPG_MP'],
    'sdt tatpg' : ['SDTEND_TATPG_MP'],
}

FLOWS_IODIE_HVQK={'prehvqk': ['SCN_UNCOREHVQK_IO_PREHVQK'],
                  'posthvqk': ['SCN_UNCOREHVQK_IO_POSTHVQK'], 
                  'stress': ['SCN_UNCOREHVQK_IO_STRESS'],                                         
                  }

FLOWS_IODIE_CLASS={
    'begin_atpg': ['atpg_io_hvm_begin'],
    'srh_cfcio_f1': ['SCN_UNCORE_IO_SRH_CFCIO_F1'],
    'chk_cfcio_f1': ['SCN_UNCORE_IO_CHK_CFCIO_F1'],
    'srh_cfcio_f2': ['SCN_UNCORE_IO_SRH_CFCIO_F2'],
    'chk_cfcio_f2': ['SCN_UNCORE_IO_CHK_CFCIO_F2'],
    'srh_cfcio_f3': ['SCN_UNCORE_IO_SRH_CFCIO_F3'],
    'srh_cfcio_f4': ['SCN_UNCORE_IO_SRH_CFCIO_F4'],
    'chk_cfcio_f4': ['SCN_UNCORE_IO_CHK_CFCIO_F4'],
    'vmax_cfcio': ['SCN_UNCORE_IO_VMAX_CFCIO'],
    'srh_cfn_f1': ['SCN_UNCORE_IO_SRH_CFN_F1'],
    'chk_cfn_f1': ['SCN_UNCORE_IO_CHK_CFN_F1'],
    'vmax_cfnhca': ['SCN_UNCORE_IO_VMAX_CFNHCA'],
    'vmax_cfnpcie': ['SCN_UNCORE_IO_VMAX_CFNPCIE'],
    'vmax_cfnupi': ['SCN_UNCORE_IO_VMAX_CFNUPI'],
    'srh_vccinf': ['SCN_UNCORE_IO_SRH_VCCINF'],
    'chk_vccinf': ['SCN_UNCORE_IO_CHK_VCCINF'],
    'vmax_vinf': ['SCN_UNCORE_IO_VMAX_VINF'],
    'end': ['SCN_UNCORE_IO_END'],
    'lttc': ['LTTC'],
    'i2td': ['I2TD'],
    'mdi': ['MDI'],
    'alltest': ['ALLTEST'],
}

NAMES=[key for flow in [FLOWS_UNCORE, FLOWS_HVQK] for key in flow.keys()]
NAMES_CLASS=[key for flow in [FLOWS_CLASS] for key in flow.keys()]
NAMES_IO=[key for flow in [FLOWS_IODIE, FLOWS_IODIE_HVQK] for key in flow.keys()]
NAMES_IO_CLASS=[key for flow in [FLOWS_IODIE_CLASS] for key in flow.keys()]

SORT = False
SEPARATE=False
IODIE=False
FUSED=False
DSTEP=0
CWF=False
QUAL=False

BIN_DICTIONARY={}

# Load pathmod
def get_patmod(pathmod_path):
    if SORT and IODIE:
         with open(pathmod_path, 'r') as file:
             lines = file.readlines()
             for i in range(len(lines)):
                 if 'PatternsRegEx' in lines[i]:
                     line=lines[i+1].replace("payload", "").replace("  ", " ").strip()
                     PATMOD.add(line.strip().strip(" \""))
    else:
        with open(pathmod_path, 'r') as file:
            for line in file:
                matches = re.findall(r'PatternsRegEx": \[(.*?)\]', line)
                for m in matches:
                    PATMOD.add(m.strip().strip(" \""))
    #print(PATMOD)

# Load mtpl files
def load_mtpls():
    global uncore_mtpl, hvqk_mtpl, class_mtpl
    uncore_mtpl, hvqk_mtpl, class_mtpl= [], [], []

    if SORT:
        with open(uncore_mtpl_path, 'r') as file:
            for line in file:
                if '#' in line:
                    result=line.split('#')[0].strip()  # delete comments from mtpl
                    uncore_mtpl.append(result)
                else:
                    uncore_mtpl.append(line)

        with open(hvqk_mtpl_path, 'r') as file:
            for line in file:
                if '#' in line:
                    result=line.split('#')[0].strip()  # delete comments from mtpl
                    hvqk_mtpl.append(result)
                else:
                    hvqk_mtpl.append(line)
    else:
        with open(class_mtpl_path, 'r') as file:
            for line in file:
                if '#' in line:
                    result=line.split('#')[0].strip()  # delete comments from mtpl
                    class_mtpl.append(result)
                else:
                    class_mtpl.append(line)

# Load plist
def load_plist():
    global plist_lines
    plist_lines= []

    with open(plist_path, 'r') as file:
        for line in file:

            if '#' in line:
                result=line.split('#')[0].strip()  # delete comments from mtpl
                plist_lines.append(result)
            else:
                plist_lines.append(line)

# Import variables of config file
def import_file_as_alias(file_path, alias='f'):
        # Load the module dynamically
        module_name = os.path.splitext(os.path.basename(file_path))[0]  # Get the module name
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Assign the module to the provided alias
        return module

# Load flows from config for TP
def load_flows_from_config(file):
    global FLOWS_UNCORE, FLOWS_HVQK, FLOWS_CLASS, FLOWS_IODIE, FLOWS_IODIE_HVQK, FLOWS_IODIE_CLASS, NAMES, NAMES_CLASS, NAMES_IO, NAMES_IO_CLASS
    f = import_file_as_alias(file, "f")
    FLOWS_UNCORE=f.FLOWS_UNCORE
    FLOWS_HVQK=f.FLOWS_HVQK
    FLOWS_CLASS=f.FLOWS_CLASS
    FLOWS_IODIE=f.FLOWS_IODIE
    FLOWS_IODIE_HVQK=f.FLOWS_IODIE_HVQK
    FLOWS_IODIE_CLASS=f.FLOWS_IODIE_CLASS
    if SORT:
        NAMES=[key for flow in [FLOWS_UNCORE, FLOWS_HVQK] for key in flow.keys()]
        NAMES_IO=[key for flow in [FLOWS_IODIE, FLOWS_IODIE_HVQK] for key in flow.keys()]
    else:
        NAMES_CLASS=[key for flow in [FLOWS_CLASS] for key in flow.keys()]
        NAMES_IO_CLASS=[key for flow in [FLOWS_IODIE_CLASS] for key in flow.keys()]

# Use config file
def use_config_file(file, plist, table, format):
    f = import_file_as_alias(file, "f")

    #Load plist path
    global plist_path
    plist_path=f.plist if f.plist is not None else plist
    print(plist_path)
    load_plist()

    # load mtpls
    mtpl_file=[]
    for i in range(len(f.mtpls)):
        mtpl_file.append([])
        try:
            with open(f.mtpls[i], 'r') as file:
                for line in file:
                    
                    if '#' in line:
                        result=line.split('#')[0].strip()  # delete comments from mtpl
                        mtpl_file[i].append(result)
                    else:
                        mtpl_file[i].append(line)
        except:
            print("Mtpl file in config doesn't exist")
            return 0
        i+=1

    i=0
    plbs={}
    audit_flows={}
    if format.lower()=='txt':
        with open(table+'.txt', "w", encoding="utf-8") as file:
            file.write("")

    for region in f.flows:
            #print(i, region, mtpl_file[i][5])
            for flow in region:
                a=f.flows[i][flow]
                items=get_dutflow_items(a, mtpl_file[i])
                plbs[a]= items 

                #For txt instance audit
                items2=get_dutflow_items_for_audit(a, mtpl_file[i])
                audit_flows[flow]=items2
                if format.lower()=='txt':
                    with open(table+'.txt', "a", encoding="utf-8") as file:
                        file.write(a+'\n\n')
                    print_structured_table(items2, table+'.txt')
            i+=1      

    generate_excel_tables(plbs, table, f.names)
    if format.lower()=='excel':
        generate_excel_tables_audit(audit_flows, table+'_audit.xlsx', BIN_DICTIONARY)

# Merge two dictionaries
def merge_dictionaries(dict1, dict2):
    # Merge dictionaries using unpacking
    return {**dict1, **dict2}

# Get paths of all files to be used for the table for class
def filepaths_class_linux(tp_path):
    global plist_path, class_mtpl_path
    tp_env_path=tp_path+'/POR_TP/CLASS_TP'

    for file in os.listdir(tp_env_path):
        file_path = os.path.join(tp_env_path, file)
        # Check if it's a file and if both patterns are in the file name
        if os.path.isfile(file_path) and 'Environment' in file and 'File' in file and 'P.env' in file and process[0:3] in file.lower():
            env_path=tp_env_path + f'/{file}'

    # Plist_ALL file
    if 'ucc' not in process:
        plist_all_path=tp_env_path + f'/{process[0:3].upper()}SP.all.plist.xml'  
    else: 
        plist_all_path=tp_env_path + f'/{process[0:3].upper()}AP.all.plist.xml'
    #print(plist_all_path)

    #PATMODS
    patmods=[]

    # Get plist path with patch used by TP
    with open(env_path, 'r') as file:
        for line in file:
            if line.startswith(f'MSCNCD{process[0:3].upper()}_PATMODIFY_PATH'):

                # Split the line by the equals sign and strip any whitespace
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_path = parts[1].strip().strip(" ';\"")
                plist_path=plist_path.replace('\\', '/')

            if f'MSCNCD{process[0:3].upper()}_PATMODIFY_PATH' in line and '.patmod' in line:
                ptd=line.split('\\', 1)
                ptd=ptd[1].strip().strip('" ;+')
                patmods.append(ptd)

    patmods=list(dict.fromkeys(patmods))            
    #print(patmods)

    # Get plist path in the adress of the TP
    program_plist = plist_path.find('/')

    # Get the base path up to 'program' from TP path
    base_path = '/intel/'

    # Get the suffix path after 'program' from plist path
    suffix_path = plist_path[program_plist + len('\\'):]
    #print(suffix_path)

    # Find the name of plist
    with open(plist_all_path, 'r') as file:
        for line in file:
            if 'scan' in line and 'compute' in line:
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_name = parts[1].strip().strip(" ';\">/")
                #print(plist_name)
                break
    
    # Combine the base path with the suffix path 
    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
    plist_path=plist_path.replace('cfg', 'plb/' + plist_name)

    # Combine the base path with the suffix path 
    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
    plist_path=plist_path.replace('cfg', 'plb/' + plist_name)

    #Find name of patmods
    if not PATMOD:
        for p in patmods:
            patmods_path=os.path.join(base_path, suffix_path.lstrip('//')+f'/{p}')
            if 'cold' in patmods_path.lower() and 'cold' not in process:
                continue
            print(patmods_path)
            get_patmod(patmods_path)

    # mtpl paths
    class_mtpl_path = tp_path + f'/Modules/SCN_SCAN_COMP/{CLASS_MTPL}'

def filepaths_class_linux_cwf(tp_path):
    global plist_path, class_mtpl_path
    tp_env_path=tp_path+'/POR_TP/CLASS_TP'
    thename=(process[0:1]+'d'+process[1:3]).upper()

    for file in os.listdir(tp_env_path):        
        #print(file)
        file_path = os.path.join(tp_env_path, file)
        # Check if it's a file and if both patterns are in the file name
        if os.path.isfile(file_path) and 'Environment' in file and 'File' in file and 'P.env' in file and thename in file:
            env_path=tp_env_path + f'/{file}'

    # Plist_ALL file
    if 'xcc' not in process:
        plist_all_path=tp_env_path + f'/{thename}_SP.all.plist.xml'  
    else:
        plist_all_path=tp_env_path + f'/{thename}_AP.all.plist.xml'
    #print(plist_all_path)
    #print(env_path)

    #PATMODS
    patmods=[]

    # Get plist path with patch used by TP
    with open(env_path, 'r') as file:
        for line in file:
            if line.startswith(f'MSCNCD{process[0:3].upper()}_PATMODIFY_PATH'):

                # Split the line by the equals sign and strip any whitespace
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_path = parts[1].strip().strip(" ';\"")
                plist_path=plist_path.replace('\\', '/')
                print(plist_path)
            if f'MSCNCD{process[0:3].upper()}_PATMODIFY_PATH' in line and '.patmod' in line:
                ptd=line.split('\\', 1)
                ptd=ptd[1].strip().strip('" ;+')
                patmods.append(ptd)

    patmods=list(dict.fromkeys(patmods))            
    print(patmods)

    # Get plist path in the adress of the TP
    program_plist = plist_path.find('/')

    # Get the base path up to 'program' from TP path
    base_path = '/intel/'

    # Get the suffix path after 'program' from plist path
    suffix_path = plist_path[program_plist + len('\\'):]
    #print(suffix_path)

    # Find the name of plist
    with open(plist_all_path, 'r') as file:
        for line in file:
            if 'scan' in line and 'compute' in line:
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_name = parts[1].strip().strip(" ';\">/")
                #print(plist_name)
                break
    
    # Combine the base path with the suffix path 
    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
    plist_path=plist_path.replace('cfg', 'plb/' + plist_name)

    # Combine the base path with the suffix path 
    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
    plist_path=plist_path.replace('cfg', 'plb/' + plist_name)

    #Find name of patmods
    if not PATMOD:
        for p in patmods:
            patmods_path=os.path.join(base_path, suffix_path.lstrip('//')+f'/{p}')
            if 'cold' in patmods_path.lower() and 'cold' not in process:
                continue
            print(patmods_path)
            get_patmod(patmods_path)

    # mtpl paths
    class_mtpl_path = tp_path + f'/Modules/SCN_SCAN_COMP/{CLASS_MTPL}'

# Get paths of all files to be used for the table for class
def filepaths_class_windows(tp_path):
    global plist_path, class_mtpl_path
    tp_env_path=tp_path+'\\POR_TP\\CLASS_TP'

    for file in os.listdir(tp_env_path):
        file_path = os.path.join(tp_env_path, file)
        # Check if it's a file and if both patterns are in the file name
        if os.path.isfile(file_path) and 'Environment' in file and 'File' in file and 'P.env' in file and process[0:3] in file.lower():
            env_path=tp_env_path + f'\\{file}'

    # Plist_ALL file
    if 'ucc' not in process:
        plist_all_path=tp_env_path + f'\\{process[0:3].upper()}SP.all.plist.xml'  
    else: 
        plist_all_path=tp_env_path + f'\\{process[0:3].upper()}AP.all.plist.xml'
    #print(plist_all_path)

    #PATMODS
    patmods=[]

    # Get plist path with patch used by TP
    with open(env_path, 'r') as file:
        for line in file:
            if line.startswith(f'MSCNCD{process[0:3].upper()}_PATMODIFY_PATH'):

                # Split the line by the equals sign and strip any whitespace
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_path = parts[1].strip().strip(" ';\"")

            if f'MSCNCD{process[0:3].upper()}_PATMODIFY_PATH' in line and '.patmod' in line:
                ptd=line.split('\\', 1)
                ptd=ptd[1].strip().strip('" ;+')
                patmods.append(ptd)

    patmods=list(dict.fromkeys(patmods))            
    #print(patmods)

    # Get plist path in the adress of the TP
    program_plist = plist_path.find('\\')
    program_tp = tp_path.find('intel')

    # Get the base path up to 'program' from TP path
    base_path = tp_path[:program_tp + len('intel')]

    # Get the suffix path after 'program' from plist path
    suffix_path = plist_path[program_plist + len('\\'):]

    # Find the name of plist
    with open(plist_all_path, 'r') as file:
        for line in file:
            if 'scan' in line and 'compute' in line:
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_name = parts[1].strip().strip(" ';\">/")
                #print(plist_name)
                break
    
    # Combine the base path with the suffix path 
    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
    plist_path=plist_path.replace('cfg', 'plb\\' + plist_name)

    # Combine the base path with the suffix path 
    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
    plist_path=plist_path.replace('cfg', 'plb\\' + plist_name)

    #Find name of patmods
    if not PATMOD:
        for p in patmods:
            patmods_path=os.path.join(base_path, suffix_path.lstrip('/\\')+f'\\{p}')
            if 'cold' in patmods_path.lower() and 'cold' not in process:
                continue
            print(patmods_path)
            get_patmod(patmods_path)

    # mtpl paths
    class_mtpl_path = tp_path + f'\\Modules\\SCN_SCAN_COMP\\{CLASS_MTPL}'

# Get paths of all files to be used for the table for sort
def filepaths(tp_path):
    global plist_path, uncore_mtpl_path, hvqk_mtpl_path

    # Environment file
    for file in os.listdir(tp_path):
        file_path = os.path.join(tp_path, file)
        
        # Check if it's a file and if both patterns are in the file name
        if os.path.isfile(file_path) and 'Environment' in file and 'File' in file and 'env' in file:
            env_path=tp_path + f'\\{file}'

    # Plist_ALL file
    plist_all_path=tp_path + '\\PLIST_ALL.plist.xml'

    #PATMODS
    patmods=[]

    # Get plist path with patch used by TP
    with open(env_path, 'r') as file:
        for line in file:
            if line.startswith('MSCNCD_PATMODIFY_PATH'):

                # Split the line by the equals sign and strip any whitespace
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_path = parts[1].strip().strip(" ';\"")

            #for patmod
            if 'MSCNCD_PATMODIFY_PATH' in line and '.patmod' in line:
                ptd=line.split('\\', 1)
                ptd=ptd[1].strip().strip('" ;+')
                patmods.append(ptd)
                
    # Get plist path in the adress of the TP
    program_plist = plist_path.find('program')
    program_tp = tp_path.find('program')

    # Get the base path up to 'program' from TP path
    base_path = tp_path[:program_tp + len('program')]

    # Get the suffix path after 'program' from plist path
    suffix_path = plist_path[program_plist + len('program'):]

    # Find the name of plist
    with open(plist_all_path, 'r') as file:
        for line in file:
            if 'scan' in line and 'compute' in line:
                parts = line.split('=', 1)

                # Extract the right-hand side, strip any extra whitespace, and remove the quotes and semicolons
                plist_name = parts[1].strip().strip(" ';\">/")
                break
    
    # Combine the base path with the suffix path 
    plist_path = os.path.join(base_path, suffix_path.lstrip('/\\'))
    plist_path=plist_path.replace('cfg', 'plb\\' + plist_name)

    #Find name of patmods
    if not PATMOD:
        for p in patmods:
            patmods_path=os.path.join(base_path, suffix_path.lstrip('/\\')+f'\\{p}')
            print(patmods_path)
            get_patmod(patmods_path)

    # mtpl paths
    uncore_mtpl_path = tp_path + f'\\Modules\\SCN_UNCORE_COMP\\{UNCORE_MTPL}'
    hvqk_mtpl_path = tp_path + f'\\Modules\\SCN_UNCOREHVQK_COMP\\{HVQK_MTPL}'

# Get where each DUT item goes to in the DUT flow 
def get_goto(flow, flow_list):
    global BIN_DICTIONARY
    dut=False
    result=False
    softbin=False
    #print('here', flow)
    for i in range(len(flow_list)):
        #It's very important to match the exact name of the DUT item
        if 'DUTFlowItem' in flow_list[i] and contains_exact_word(flow_list[i], flow):
            dut=True
        if dut and 'Result 0' in flow_list[i]: #Fail bin
            softbin=True

        #Fail bin
        if softbin and dut and 'SetBin' in flow_list[i]:
            value = flow_list[i].strip().split()
            value = value[1].split('.')[1].split('_')[0]
            BIN_DICTIONARY[flow]=value
            #print(flow, value, flow_list[i])

        if dut and 'Result 1' in flow_list[i]: #What happens if the test is successful
            result=True
            #print(flow_list[i])

        #Where does it go if test if successful
        if result and dut and 'GoTo' in flow_list[i]:
            value = flow_list[i].strip().split()
            value = value[1].strip().strip(";")
            #print(value, flow_list[i])
            return [value]+get_goto(value, flow_list)
        if dut and result and '}' in flow_list[i]: #If it's the last test of the flow
            print(flow, 'last')
            return []

# Gets the flow items of a DUT flow
def get_dut_flow(flow, mtpl_file):
    mainflow=[]
    cond=False
    count_corch=0
    for line in mtpl_file:
        if line.startswith('DUTFlow') and flow in line:
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
        print(f"Flow {flow} is not defined in mtpl")
        return []
    for i in range(len(mainflow)):
        if 'DUTFlowItem' in mainflow[i] and not first:
            value = mainflow[i].strip().split()
            print(value[1])  # This will print name of the flow instance
            flow_order=[value[1]]
            break
    flow_order+=get_goto(value[1], mainflow)
    return flow_order

# Get scan region, flavor and rev of a pattern
def extract_data(input_str): 
    #For IODIE
    if IODIE:
        input_str = input_str.replace("payload", "").replace("  ", " ").strip()
    
    # Regular expression to find the pattern between two underscores before "edt"
    match = re.search(r'_([^_]+)_edt', input_str) if '_edt' in input_str else re.search(r'_([^_]+)_byp', input_str)

    if input_str in PATMOD:
        masking=True
    else:
        masking=False
    
    # Check if the pattern is found and return the desired string
    result = match.group(1) if match else None

    lstr=input_str.split('_')[-1]
    content=input_str.split('_')[-2]

    if 'chain' in input_str:
        region='chain' 
        h_position = lstr.find('h')
        rev=lstr[0:h_position-1]
        return result, rev, region, masking, content

    elif 'dport' in input_str:
        region='dport'
        rev=lstr
        return result, rev, region, masking, content
    
    elif 'ca1tf' in input_str or 'ca2tf' in input_str:
        region='ca1tf' if 'ca1tf' in input_str else 'ca2tf'
        p_position = lstr.find('p')
        rev = lstr[0:p_position]
        #print(input_str, result, rev, region)
        return result, rev, region, masking, content
    
    # ph1, ph2 or ph3
    else:
        #Get the rev and partition
        region=lstr
        p_position = region.find('p')
        rev = region[0:p_position]

        if not SEPARATE:

            if region[p_position+3:]:  #If there is topoff
                return result, rev, region[p_position+3:], masking, content
            else:
                return result, rev, region[p_position:p_position+3], masking, content
            
        else:
            if 'trans' in input_str:
                if region[p_position+3:]:  #If there is topoff
                    return result, rev, region[p_position+3:]+'_tatpg', masking, content
                else:
                    return result, rev, region[p_position:p_position+3]+'_tatpg', masking, content
                
            else:
                if region[p_position+3:]:  #If there is topoff
                    return result, rev, region[p_position+3:]+'_atpg', masking, content
                else:
                    return result, rev, region[p_position:p_position+3]+'_atpg', masking, content

# Gets the flow items of a DUT flow
def check_further_flow(flow, mtpl_file):
    mainflow=[]
    cond=False
    for line in mtpl_file:
        if line.startswith('DUTFlow') and flow in line and 'DUTFlowItem' not in line:
            cond=True
        if cond:
            mainflow.append(line)
        if cond and line.startswith('}'):
            break
    
    #If there is no main flow, is an instance
    if len(mainflow)==0:
        return False
    
    else:
        first=False
        for i in range(len(mainflow)):
            if 'DUTFlowItem' in mainflow[i] and not first:
                value = mainflow[i].strip().split()
                #print(value[1])  # This will print name of the flow instance
                new_flow=[value[1]]
                break

        new_flow+=get_goto(value[1], mainflow)
    
        subflow_instances=[{flow: []}]

        for f in new_flow:
            result=check_further_flow(f, mtpl_file)
            if result:
                subflow_instances+=result
            else:
                subflow_instances[0][flow].append(f)

        return subflow_instances

# This functon gets a dictionary with subflows and the instances with plist running on them
def get_flow_with_instances(flow, mtpl_file):

    #Get the subflows of the main flow
    flow_order=get_dut_flow(flow, mtpl_file)
    print(flow_order)
    subflow_instances={flow: []}
    for f in flow_order:
        result=check_further_flow(f, mtpl_file)  
        if result:  
            #print('aca', result)
            for d in result:
                subflow_instances = merge_dictionaries(subflow_instances, d)
        else:
            subflow_instances[flow].append(f)
        
    print(subflow_instances)
    return subflow_instances

# Get dut items running in flow
def get_dutflow_items(flow, mtpl_file):
    flow_instances=get_flow_with_instances(flow, mtpl_file)

    plist=[]
    for f in flow_instances:
        for instance in flow_instances[f]:
            cond=False
            EDC=False
            bypassed=False
            to_append=None
            #print(instance)
            for line in mtpl_file:
                
                #Get the main flow
                if (line.startswith('Test') or line.startswith('MultiTrialTest')) and contains_exact_word(line, instance):
                    cond=True

                    #Skip core 
                    if '_CORE_' in line:
                        break
                    if 'EDC' in line:
                        EDC=True
                    else:
                        for ln in mtpl_file:
                            if 'DUTFlowItem' in ln and contains_exact_word(ln, instance) and 'EDC' in ln:
                                EDC=True
                                break

                # Instance is bypassed
                if cond and 'BypassPort' in line:
                    # for sort instance is either bypass or not
                    if SORT and '-1' not in line:
                        print('bypass', instance)
                        break

                    elif not SORT:
                        if not is_executed(line, process, QUAL):
                            print('bypass', instance)
                            print(line)
                            bypassed=True
                            break

                if cond and ('Patlist' in line or 'patlist' in line) and '"Patlist"' not in line:
                    #print('aca', instance, line)
                    value = line.split('=')
                    #print(value[1].strip().strip("\";"), '\n')
                    
                    # Check for value inside parentheses first
                    match = re.search(r'\((.*?)\)', value[1])
                    
                    if match:
                        value=match.group(1).split(',')
                        if len(value)==4:
                            to_append=[value[process_map[process][0]].strip("\"'"), EDC]
                        else:
                            to_append=[value[0].strip("\"'"), EDC] if 'hot' in process else [value[1].strip("\"'"), EDC]
                            #print(value, process)
                    else:
                        to_append=[value[1].strip().strip("\";'"), EDC]
                    
                if cond and line.startswith('}'):
                    if not bypassed:
                        print(instance, to_append)
                        if to_append:
                            plist.append(to_append)
                    bypassed=False
                    break
    
    plbs={}
    for p in plist:

        current_region=0
        previous_region=None
        previous_flavor=None
        previous_rev=None
        previous_content=None
        plbs_list=get_plist(plist_lines, p[0])
        pp_list=[]
        for i, pp in enumerate(plbs_list):

            # this skips repeated patterns
            if pp in pp_list and i!=(len(plbs_list))-1:
                continue
            # last element
            elif pp in pp_list and i==(len(plbs_list))-1:
                print('special case last plist has repeated plbs')
                # if flavor is not yet in dictionary (punit for example)
                if previous_flavor not in plbs:
                    plbs[previous_flavor]={}
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                elif previous_region not in plbs[previous_flavor]:
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region is defined in dictionary
                else:
                    stored_data=plbs[previous_flavor][previous_region]

                    # Store the one with the biggest rev
                    if int(stored_data[0][-1])<int(previous_rev[-1]):
                        plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

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
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                current_region=0
                pp_list=[]
                previous_mask=False
            
            flavor, rev, region, mask, content =extract_data(pp) 
            #print(flavor, rev, region, content, pp)
            if not previous_flavor:
                previous_flavor=flavor
                previous_region=region
                previous_rev=rev
                previous_mask=mask
                previous_content=content

            if flavor!= previous_flavor or previous_region != region:
                #print(previous_region, region)
                # if flavor is not yet in dictionary (punit for example)
                if previous_flavor not in plbs:
                    plbs[previous_flavor]={}
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                elif previous_region not in plbs[previous_flavor]:
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region is defined in dictionary
                else:
                    stored_data=plbs[previous_flavor][previous_region]
                    #print(previous_flavor, previous_region, stored_data, previous_rev, current_region, p[1])

                    # Store the one with the biggest rev
                    if int(stored_data[0][-1])<int(previous_rev[-1]):
                        plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

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
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                current_region=0
                pp_list=[]
                previous_mask=False

            current_region+=1
            previous_flavor=flavor
            previous_region=region
            previous_rev=rev
            previous_content=content
            previous_mask=previous_mask | mask
            pp_list.append(pp)

            if i==(len(plbs_list))-1:
                # if flavor is not yet in dictionary (punit for example)
                if previous_flavor not in plbs:
                    plbs[previous_flavor]={}
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                elif previous_region not in plbs[previous_flavor]:
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region is defined in dictionary
                else:
                    stored_data=plbs[previous_flavor][previous_region]

                    # Store the one with the biggest rev
                    if int(stored_data[0][-1])<int(previous_rev[-1]):
                        plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

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
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                current_region=0
                pp_list=[]
                previous_mask=False     
    return plbs

# Get dut items running in flow
def get_dutflow_items_for_audit(flow, mtpl_file):
    flow_instances=get_flow_with_instances(flow, mtpl_file)

    #to store instances
    info={}

    plist=[]
    for f in flow_instances:
        for instance in flow_instances[f]:
            cond=False
            EDC=False
            bypassed=False
            to_append=None
            #print(instance)
            for line in mtpl_file:
                
                #Get the main flow
                if (line.startswith('Test') or line.startswith('MultiTrialTest')) and contains_exact_word(line, instance):
                    cond=True

                    #Skip core 
                    if '_CORE_' in line:
                        break

                    if 'EDC' in line:
                        EDC=True
                    else:
                        for ln in mtpl_file:
                            if 'DUTFlowItem' in ln and contains_exact_word(ln, instance) and 'EDC' in ln:
                                EDC=True
                                break

                # Instance is bypassed
                if cond and 'BypassPort' in line:
                    # for sort instance is either bypass or not
                    if SORT and '-1' not in line:
                        print('bypass', instance)
                        break

                    elif not SORT:
                        if not is_executed(line, process, QUAL):
                            print('bypass', instance)
                            print(line)
                            bypassed=True
                            break

                if cond and ('Patlist' in line or 'patlist' in line) and '"Patlist"' not in line:
                    #print('aca', instance, line)
                    value = line.split('=')
                    #print(value[1].strip().strip("\";"), '\n')
                    
                    # Check for value inside parentheses first
                    match = re.search(r'\((.*?)\)', value[1])
                    
                    if match:
                        value=match.group(1).split(',')
                        if len(value)==4:
                            to_append=[value[process_map[process][0]].strip("\"'"), EDC]
                        else:
                            to_append=[value[0].strip("\"'"), EDC] if 'hot' in process else [value[1].strip("\"'"), EDC]
                            #print(value, process)
                    else:
                        to_append=[value[1].strip().strip("\";'"), EDC]
                    
                if cond and line.startswith('}'):
                    if not bypassed:
                        print(instance, to_append)
                        if to_append:
                            plist.append(to_append)
                            info[instance]=to_append[0]
                    bypassed=False
                    break
    #print(info)
    to_return={}
    
    for p in info:
        #print(p, info[p])
        plbs={}
        current_region=0
        previous_region=None
        previous_flavor=None
        previous_rev=None
        previous_content=None
        plbs_list, plist_list_audit=get_plist_audit(plist_lines, info[p], [])
        plist_list_audit.remove(info[p])
        #print(plist_list_audit)
        pp_list=[]
        for i, pp in enumerate(plbs_list):

            # this skips repeated patterns
            if pp in pp_list and i!=(len(plbs_list))-1:
                continue
            # last element
            elif pp in pp_list and i==(len(plbs_list))-1:
                print('special case last plist has repeated plbs')
                # if flavor is not yet in dictionary (punit for example)
                if previous_flavor not in plbs:
                    plbs[previous_flavor]={}
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                elif previous_region not in plbs[previous_flavor]:
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region is defined in dictionary
                else:
                    stored_data=plbs[previous_flavor][previous_region]

                    # Store the one with the biggest rev
                    if int(stored_data[0][-1])<int(previous_rev[-1]):
                        plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

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
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                current_region=0
                pp_list=[]
                previous_mask=False
            
            flavor, rev, region, mask, content =extract_data(pp) 
            #print(flavor, rev, region, content, pp)

            if not previous_flavor:
                previous_flavor=flavor
                previous_region=region
                previous_rev=rev
                previous_mask=mask
                previous_content=content

            if flavor!= previous_flavor or previous_region != region:
                #print(previous_region, region)
                
                # if flavor is not yet in dictionary (punit for example)
                if previous_flavor not in plbs:
                    plbs[previous_flavor]={}
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                elif previous_region not in plbs[previous_flavor]:
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region is defined in dictionary
                else:
                    stored_data=plbs[previous_flavor][previous_region]
                    #print(previous_flavor, previous_region, stored_data, previous_rev, current_region, p[1])

                    # Store the one with the biggest rev
                    if int(stored_data[0][-1])<int(previous_rev[-1]):
                        plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

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
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                current_region=0
                pp_list=[]
                previous_mask=False

            current_region+=1
            previous_flavor=flavor
            previous_region=region
            previous_rev=rev
            previous_mask=previous_mask | mask
            previous_content=content
            pp_list.append(pp)

            if i==(len(plbs_list))-1:
                # if flavor is not yet in dictionary (punit for example)
                if previous_flavor not in plbs:
                    plbs[previous_flavor]={}
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region of current flavor is not yet in dictionary (ph3 or ca1tf of punit for example)
                elif previous_region not in plbs[previous_flavor]:
                    plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                # if region is defined in dictionary
                else:
                    stored_data=plbs[previous_flavor][previous_region]

                    # Store the one with the biggest rev
                    if int(stored_data[0][-1])<int(previous_rev[-1]):
                        plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

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
                            plbs[previous_flavor][previous_region]=[previous_rev, current_region, p[1], previous_mask, previous_content]

                current_region=0
                pp_list=[]
                previous_mask=False     

        #print(plbs)
        to_return[p]=[info[p], plist_list_audit, plbs]

    return to_return

#For generating instance txt
def print_structured_table(items, name):
    # Extract first column and repeat for all rows
    items=copy.deepcopy(items)

    for i in items:
        col3 = items[i][1] if items[i][1] else [""]
        col1 = [i] + [""] * (len(col3))
        col2 = [items[i][0]] + [""] * (len(col3))

        try:
            col_12=[BIN_DICTIONARY[i]]+[""]*len(col3)
            #print(col_12)
        except:
            col_12=[""]+[""] * (len(col3))

        #print(col3)
        #print(col1)
        #print(col2)
        #print(items[i][2])
        for j in items[i][2]:
            for k in items[i][2][j]:
                #print(items[i][2][j][k])
                items[i][2][j][k]=items[i][2][j][k][1]

        # Convert dictionary to string format for display
        col4 = [f"{key}: {value}" + "" * (len(col3)) for j, (key, value) in enumerate(items[i][2].items())]
        col4 += [""] * (len(col3) - len(col4))

         # Combine all columns
        table_data = list(zip(col1, col_12, col2, col3, col4))
        tabla_final=tabulate(table_data, headers=["Instancia", "Bin", "Main Plist", "Plist Calls", "Plbs"], tablefmt="grid")

        print(tabla_final)

        with open(name, "a", encoding="utf-8") as file:
            file.write(tabla_final)
            file.write('\n\n\n')
            #print(f"Table saved to {'test.txt'}")

# Check user inputs of program
def check_inputs(args):
    global process, SORT
    if args.tp is None and args.config_file is None:
        print('Error. Please specify either a TP or a config file')
        return 0
    if args.table is None:
        print('Error. No table name specified')
        return 0
    
    # Check there is a flow defined
    if args.f is None or (args.f.lower() != 'sort' and args.f.lower() != 'class'):
        print('Error. Define if flow is either sort or class')
        return 0
    if args.f.lower() == 'sort':
        SORT=True
    if args.f.lower() == 'class':
        if args.chop is None:
            print('Error. For class you have to define a chop (XCC, UCC, HCC, LCC)')
            return 0
        if args.op is None:
            print('Error. For class you have to define an operation (Cold, Hot)')
            return 0
        process= args.chop.lower() + '_' + args.op.lower()
        
        if process not in process_map:
            print("Invalid process name")
            return 0

    if args.format is None:
        print('Error. Define a format for instance output (txt/excel) with --format flag')
        return 0
    if args.format.lower() not in ['txt', 'excel']:
        print('Error. Define a format for output table (txt/excel)')
        return 0

    # Check if the files exists
    if args.tp is not None:
        if not os.path.exists(args.tp):
            print("Error. The TP path specified does not exist. Check path")
            return 0
    if args.config_file is not None:
        if not os.path.exists(args.config_file):
            print("Error. The config file specified does not exist. Check path")
            return 0
    if args.plist is not None:
        if not os.path.exists(args.plist):
            print("Error. The plist file specified does not exist. Check path")
            return 0
    if args.patmod is not None:
        if not os.path.exists(args.patmod):
            print("Error. The patmod file specified does not exist. Check path")
            return 0
    if args.plist is None and args.config_file is not None and args.tp is None:
        print("WARNING: Not --plist flag. Make sure you define either this flag or a plist in confing.py")
        #return 0        

    return args

#Main
def main(args): 
    print(os.getenv('OS'))  
    parser = argparse.ArgumentParser(description="Script for generating table with content in kill")
    parser.add_argument("--tp", type=str, help="TP path (should be in a location where it can be loaded)")
    parser.add_argument("--table", type=str, help="Name of the output table")
    parser.add_argument("--plist", type=str, default=None, help="Plist path for TP (optional)")
    parser.add_argument("--config_file", type=str, default=None, help="File with specific path for mtpl and flows to generate table (either this or tp)")
    parser.add_argument("--patmod", type=str, help="Patmod location")
    parser.add_argument("--chop", type=str, help="Chop (UCC, XCC, HCC, LCC)")
    parser.add_argument("--op", type=str, help="Operation (HOT, COLD)")
    parser.add_argument("--f", type=str, help="Flow (SORT, CLASS)")
    parser.add_argument("--format", type=str, help="Audit output (txt, excel)")
    parser.add_argument("-separate", action="store_true", help="Differentiates between atpg and tatpg")
    parser.add_argument("-cwf", action="store_true", help="We are running CWF")
    parser.add_argument("-qual", action="store_true", help="We are running in QUAL")
    args = parser.parse_args(args)
    args = check_inputs(args)

    if not args:
        return 0
    
    if args.separate:
        global SEPARATE
        SEPARATE=True
    
    if args.cwf:
        global CWF
        CWF=True

    if args.qual:
        global QUAL
        QUAL=True
    
    if args.patmod:
        get_patmod(args.patmod)

    if args.config_file is not None and args.tp is None:
        use_config_file(args.config_file, args.plist, args.table, args.format)
        return 0
    
    elif args.config_file is not None and args.tp is not None:
        load_flows_from_config(args.config_file)

    #for scan by default
    if SORT:
        filepaths(args.tp) 
    else:
        if 'dows' in os.getenv('OS'):
            filepaths_class_windows(args.tp)
        else:
            filepaths_class_linux(args.tp) if not CWF else filepaths_class_linux_cwf(args.tp)

    #If user specified plist to get plbs
    if args.plist is not None:
        global plist_path
        plist_path=args.plist

    print(plist_path)

    if SORT:
        print(uncore_mtpl_path)
        print(hvqk_mtpl_path)
    else:
        print(class_mtpl_path)

    load_mtpls()
    load_plist()
    plbs={}
    audit_items={}

    #Table with instances audit
    if args.format.lower()=='txt':
        audit_table=args.table+'.txt'
        with open(audit_table, "w", encoding="utf-8") as file:
            file.write("")
    
    if SORT:
        for region in FLOWS_UNCORE:
            for flow in FLOWS_UNCORE[region]:
                items=get_dutflow_items(flow, uncore_mtpl)
                plbs[flow]= items if flow not in plbs else merge_dictionaries(plbs[flow], items)

                #For txt instance audit
                items2=get_dutflow_items_for_audit(flow, uncore_mtpl)
                audit_items[flow]=items2
                if args.format.lower()=='txt':
                    with open(audit_table, "a", encoding="utf-8") as file:
                        file.write(flow+'\n\n')
                    print_structured_table(items2, audit_table)  

        for region in FLOWS_HVQK:
            for flow in FLOWS_HVQK[region]:
                items=get_dutflow_items(flow, hvqk_mtpl)
                plbs[flow]= items if flow not in plbs else merge_dictionaries(plbs[flow], items)

                #For txt instance audit
                items2=get_dutflow_items_for_audit(flow, hvqk_mtpl)
                audit_items[flow]=items2
                if args.format.lower()=='txt':
                    with open(audit_table, "a", encoding="utf-8") as file:
                        file.write(flow+'\n\n')
                    print_structured_table(items2, audit_table)

    else:
        for region in FLOWS_CLASS:
            for flow in FLOWS_CLASS[region]:
                #print(region, flow)
                items=get_dutflow_items(flow, class_mtpl)
                plbs[flow]= items if flow not in plbs else merge_dictionaries(plbs[flow], items)

                #For txt instance audit
                items2=get_dutflow_items_for_audit(flow, class_mtpl)
                audit_items[flow]=items2
                if args.format.lower()=='txt':
                    with open(audit_table, "a", encoding="utf-8") as file:
                        file.write(flow+'\n\n')
                    print_structured_table(items2, audit_table)

    #print(plbs)
    #print(BIN_DICTIONARY)
    generate_excel_tables(plbs, args.table, NAMES) if SORT else generate_excel_tables(plbs, args.table, NAMES_CLASS)
    if args.format.lower()=='excel':
        generate_excel_tables_audit(audit_items, args.table+'_audit.xlsx', BIN_DICTIONARY)

if __name__ == "__main__":
    main(sys.argv[1:])
