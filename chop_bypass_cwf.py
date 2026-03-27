import re

process_map = {
        "xcc_hot": (0, 0), "xcc_cold": (0, 1),
        "hcc_hot": (1, 0), "hcc_cold": (1, 1),
    }

#Check if instance is bypassed or not
def is_executed(log: str, process_name: str, qual: bool) -> bool:
    #print(process_name, log, log.split('='))
    log=log.split('=', 1)[1].strip().strip(" ';")
    #print(log)

    if process_name not in process_map:
        raise ValueError("Invalid process name")
    if log.strip() == "-1":
        return True  # All processes executed
    if log.strip() == "1":
        return False  # All processes executed

    match = re.search(r'TPKNOB_Rules.DIE\((.*)\)', log)
    if not match:
        if ".IC_REC" in log:
            match = re.search(r'TPKNOB_Rules.IC_REC\((.*?)\)', log)
            value=match.group(1).split(',')
            if qual:
                if value[0]=='-1':
                    return True
                else:
                    return False

            else:
                if value[1]=='-1':
                    return True
                else:
                    return False

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
    while len(processes) < 2:
        processes.append('1')

    processes = processes[:2]
    row, col = process_map[process_name]

    if row >= len(processes):
        raise ValueError("Log data contains invalid process state")

    process_value = processes[row]

    if not process_value:
        raise ValueError("Missing process data")
    if 'IC_REC' in process_value:
        rule_match = re.search(r'TPKNOB_Rules.IC_REC\((.*?)\)', process_value)
        
        if rule_match:
            value=rule_match.group(1).split(',')
            #print(value)
            if qual:
                if value[0]=='-1':
                    return True
                else:
                    return False
            else:
                if value[1]=='-1':
                    return True
                else:
                    return False
    else:
        try:
            return int(process_value) == -1
        except ValueError:
            raise ValueError("Invalid process state format")

# Example Usage
log1 = "-1"
log2 = "res.ult(rules(-1,1),-1,rules(1,-1),-1)"
log3 = "    BypassPort = -1;"
log4 = "BypassPort = TPKNOB_Rules.DIE(-1,-1,1,1);"
log5 = '    BypassPort = TPKNOB_Rules.DIE(TPKNOB_Rules.DOWNSTREAM_SOCKETS(-1,1),1,1,1);'
log6 = 'BypassPort = TPKNOB_Rules.IC_REC(1,-1);'
log7 = 'BypassPort = TPKNOB_Rules.DIE(TPKNOB_Rules.IC_REC(1,-1),-1);'

# Test Cases
#print(is_executed(log7, "xcc_cold", True))  # True
