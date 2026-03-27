#OPTION 1: 

#Uncomment this for using these flows. They will be used alongise the TP you defined

#these flows are defined in uncore mtpl file
FLOWS_UNCORE={'begin': ['SCN_UNCORE_COMP_BEGIN'], 
              'end atpg' : ['ATPG']
              }

#these flows have to be defined in hvkq mtpl file
FLOWS_HVQK={'prehvqk': ['SCN_UNCOREHVQK_COMP_PREHVQK'], 
            #'posthvqk': ['SCN_UNCOREHVQK_COMP_POSTHVQK'],
            'stress': ['SCN_UNCOREHVQK_COMP_HOTSTRESS'],
            }
#these flows have to be defined in class mtpl file         
FLOWS_CLASS={'srh_vccinf': ['SCN_SCAN_COMP_SRH_VCCINF'], 
             }

'''
#OPTION 2

#Uncomment this for using these variables. 

#List with mtpl paths you want to use
mtpls=[r"I:\\intel\\engineering\\dev\\dcd\\scan\\agloriaj\\25ww06p2_Release\\Modules\\SCN_SCAN_COMP\SCN_SCAN_COMP.mtpl", 
       ]

#IMPORTANT: use full path if using mapped hard drive
#For example, do NOT use "U:\program", use instead:
# r"\\s46file1.cd.intel.com\program"

#flows for each mtpl file
flows1={'begin_atpg': 'atpg_comp_hvm_begin', 
        'begin_tatpg':'tatpg_comp_hvm_begin',
        'srh_vccinf': 'SCN_SCAN_COMP_SRH_VCCINF',
        'chk_vccinf': 'SCN_SCAN_COMP_CHK_VCCINF',
        'vmax_vinf': 'SCN_SCAN_COMP_VMAX_VINF',
        'srh_cfchdc_f1': 'SCN_SCAN_COMP_SRH_CFCHDC_F1',
        'chk_cfchdc_f1': 'SCN_SCAN_COMP_CHK_CFCHDC_F1',
        'srh_cfchdc_f2': 'SCN_SCAN_COMP_SRH_CFCHDC_F2',
        'chk_cfchdc_f2': 'SCN_SCAN_COMP_CHK_CFCHDC_F2',
        'srh_cfchdc_f3': 'SCN_SCAN_COMP_SRH_CFCHDC_F3',
        'srh_cfchdc_f4': 'SCN_SCAN_COMP_SRH_CFCHDC_F4',
        'chk_cfchdc_f4': 'SCN_SCAN_COMP_CHK_CFCHDC_F4',
        'vmax_cfccomp': 'SCN_SCAN_COMP_VMAX_CFCCOMP',
        'srh_ddrd_f1': 'SCN_SCAN_COMP_SRH_DDRD_F1',
        'chk_ddrd_f1': 'SCN_SCAN_COMP_CHK_DDRD_F1',
        'srh_ddrd_f2': 'SCN_SCAN_COMP_SRH_DDRD_F2',
        'chk_ddrd_f2': 'SCN_SCAN_COMP_CHK_DDRD_F2',
        'srh_ddrd_f3': 'SCN_SCAN_COMP_SRH_DDRD_F3',
        'chk_ddrd_f3': 'SCN_SCAN_COMP_CHK_DDRD_F3',
        'vmax_ddrd': 'SCN_SCAN_COMP_VMAX_DDRD',
        'end_extest': 'EXTEST',
        'end_atpg': 'ATPG',
        'lttc': 'LTTC',
        'i2td': 'I2TD',}

flows2={'prehvqk': 'SCN_UNCOREHVQK_COMP_PREHVQK', 
        'vmax': 'SCN_UNCOREHVQK_COMP_VMAX',
        }

#add all your flows into this list
flows=[flows1]

#OPTIONAL: path of plist to use. Overwrittes --plist flag when running script if not set to None
plist=None
#plist = None # uncommwnt this if using --plist flag

#DO NOT TOUCH THIS
names = [key for flow in flows for key in flow.keys()]
# name: name of DUTFlow as it appears in mtpl file

'''