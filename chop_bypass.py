import re

process_map = {
        "ucc_hot": (0, 0), "ucc_cold": (0, 1),
        "xcc_hot": (1, 0), "xcc_cold": (1, 1),
        "hcc_hot": (2, 0), "hcc_cold": (2, 1),
        "lcc_hot": (3, 0), "lcc_cold": (3, 1),
    }
 
def temperature_execution(log, process_name, fused):
    match = re.search(r'TPKNOB_Rules.TEMPERATURE\((.*)\)', log)

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
   
    if 'hot' in process_name:
        process_value=processes[0]
    else:
        process_value=processes[1]

    match = re.search(r'SCN_UNCORE_IO_Rules.SCAN_fuseIO\((.*)\)', process_value)
    if match:
        process_value=match.group(1).split(',')  

        if fused:
            return process_value[0]=='-1' 
        else:
            return process_value[1]=='-1'   
    
    return process_value=='-1'

#Check if instance is bypassed or not
def is_executed(log: str, process_name: str, fused: bool) -> bool:
    #print(process_name, log, log.split('='))
    log=log.split('=', 1)[1].strip().strip(" ';")
    #print(log)

    if process_name not in process_map:
        raise ValueError("Invalid process name")
    if log.strip() == "-1":
        return True  # All processes executed
    if log.strip() == "1":
        return False  # All processes bypassed

    match = re.search(r'TPKNOB_Rules.DIE\((.*)\)', log)
    if not match:
        if "TEMPERATURE" in log:
            return temperature_execution(log, process_name, fused)
            
        else:
            raise ValueError("Invalid log format") #CHECK THIS

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
    row, col = process_map[process_name]

    if row >= len(processes):
        raise ValueError("Log data contains invalid process state")

    process_value = processes[row]
    #print(process_value)

    if not process_value:
        raise ValueError("Missing process data")
    if 'DOWNSTREAM_SOCKETS' in process_value:
        rule_match = re.search(r'TPKNOB_Rules.DOWNSTREAM_SOCKETS\((.*?)\)', process_value)
        
        if rule_match:
            rule_values = rule_match.group(1).split(',')
            if len(rule_values) != 2 or not all(r.strip().lstrip('-').isdigit() for r in rule_values):
                raise ValueError("Invalid rules format")
            types = list(map(int, rule_values))
            return types[col] == -1
        else:
            raise ValueError("Invalid rules format")
        
    elif 'TEMPERATURE' in process_value:
        return temperature_execution(process_value, process_name, fused)
    
    elif 'fuseIO' in process_value:
        match = re.search(r'SCN_UNCORE_IO_Rules.SCAN_fuseIO\((.*)\)', process_value)
        if match:
            process_value=match.group(1).split(',')  

            if fused:
                return process_value[0]=='-1'
            else:
                return process_value[1]=='-1'
    
    else:
        try:
            return int(process_value) == -1
        except ValueError:
            return True

def get_plist_with_rules(patlist: str, process_name: str, fused: bool, dstep=0) -> bool:
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
        row, col = process_map[process_name]
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
        else:
            return processes[dstep].strip("\"'")
            
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
        row, col = process_map[process_name]

        process_value = processes[col]

        if not process_value:
            raise ValueError("Missing process data")
        if 'fuseIO' in process_value:
            match = re.search(r'SCN_UNCORE_IO_Rules.SCAN_fuseIO\((.*)\)', process_value)
            if match:
                process_value=match.group(1).split(',')  

                if fused:
                    return process_value[0].strip("\"'")
                else:
                    return process_value[1].strip("\"'")
        else:
            return process_value.strip("\"'") 
            
# Example Usage
log1 = "-1"
log2 = "res.ult(rules(-1,1),-1,rules(1,-1),-1)"
log3 = "    BypassPort = -1;"
log4 = "BypassPort = TPKNOB_Rules.DIE(-1,-1,1,1);"
log5 = '    BypassPort = TPKNOB_Rules.DIE(TPKNOB_Rules.DOWNSTREAM_SOCKETS(-1,1),1,1,1);'

# Test Cases
#print(is_executed(log5, "ucc_hot"))  # True
