import argparse
import sys
import subprocess
import re
import time

SKIP_THESE=['cold_preamble',
            'reset_Mscn',
            'reset_uncore',
            'pre_precat_',
            'clear_uncore',
            'one_hundred_nops',
            'safetyseal',
            'safety_seal',
            'end_gracefully',
            'fivrshutdown',
            'vbump_trigger',
            'fivr7nm',
            'bipre',
            'bipost',
            'grdt_tour',
            'dummy',
            'solout',
            'tempreadmax_all',
            'r0Hclk',
            'r0clk',
            'testend',
            'ssnsetup',
            'ssnend',
            'testsetup',
            'preprecats',
			'cwf_stf_gid_clear',
			'bgr_isolation',
            'parfditd_tdr_ovrd',
            'scn_preprecat'
            ]

#Check if the exact instance name is in the line
def contains_exact_word(input_string, target_word):
    # Use regex to find the exact word with word boundaries
    pattern = r'\b' + re.escape(target_word) + r'\b'
    match = re.search(pattern, input_string)
    
    # Return True if an exact match is found, otherwise False
    return bool(match)

#Get plist
def get_plist(plist_text, hotreset):

    plist_list=[]
    current_object = []
    text=[]
    burst=False
    
    while hotreset[-1:]=='\r' or hotreset[-1:]=='\n':
        hotreset=hotreset[0:-1]

    print(hotreset)
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
            
            if contains_exact_word(line, hotreset):
                burst=True  
                
            current_object.append(line) 
            
        else:
            current_object.append(line)
    
    #print(plist_list)
    patterns=[]
    for p in plist_list:
        if 'Global' in p:
            continue
        elif 'Skip' in p or 'Hph' in p or 'H1hot' in p or p.strip().startswith('#'):
            continue
        elif all(these not in p for these in SKIP_THESE):

            if 'Pat' in p:
                value = p.split()
                #print(value)
                patterns.append(value[1].strip().strip(";"))

            elif 'PList' in p and 'Global' not in p:
                value = p.split()
                patterns+=get_plist(plist_text, value[1].strip().strip(";"))
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
def get_plist_audit(plist_text, hotreset, audit):

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
            
            if contains_exact_word(line, hotreset):
                burst=True  
                
            current_object.append(line) 
            
        else:
            current_object.append(line)
    
    #print(plist_list)
    patterns=[]
    for p in plist_list:
        if 'Global' in p:
            continue
        elif 'Skip' in p or 'Hph' in p or 'H1hot' in p or p.strip().startswith('#'):
            continue
        elif all(these not in p for these in SKIP_THESE):
            if 'Pat' in p:
                value = p.split()
                #print(value)
                patterns.append(value[1].strip().strip(";"))

            elif 'PList' in p and 'Global' not in p:
                value = p.split()
                out1, out2=get_plist_audit(plist_text, value[1].strip().strip(";"), [])
                patterns+=out1
                audit+=out2
    #print(patterns)
    return patterns, audit

#Main for testing things
def main(args):    
    parser = argparse.ArgumentParser(description="Process a text file as described.")
    parser.add_argument("input_file", type=str, help="Input file plist")
    parser.add_argument("output_file", type=str, help="Output file path")
    parser.add_argument("plist", type=str, help="Plist to find")
    args = parser.parse_args(args)
    
    # Open the file with plist and read its lines into a list
    with open(args.plist, 'r') as file:
        plist_list = [line.strip() for line in file]  # Read each line, strip the line break, and store it in the list
    
    for plist in plist_list:
        get_plist(args.input_file, args.output_file, plist)

if __name__ == "__main__":
    main(sys.argv[1:])