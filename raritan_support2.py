# Support functions for the Raritan Power Switch
# Methods in this file get called from powersup2.py 

# The FQDN populated in /srv/docker/hostname.env is crucial to the proper execution of these functions

import time

##### Telnet Logins #####

# Return the Raritan Power Strip in <LOCATION_CODE> Lab HyperRack login info,
# Argument:
#   hyper_rack_unit - selects hyper rack (there is more than one).
# This switch has been configured for the following login settings:
# User: 
# Pass: 
# Telnet port: 
def init_raritan_hyper_rack_telnet(hyper_rack_unit):
  HOST = ("<THIS-IS-A-PDU-HOSTNAME{}-CONVENTION.subnet.domain.com>").format(hyper_rack_unit)
  PORT = 1234
  PASSWORD = ""
  USER = ""
  PARSER = ""
  return [HOST, PORT, PASSWORD, USER, PARSER]


# Return the Raritan Power Strip in <LOCATION_CODE> lab login info,
# This switch has been configure for the following login settings:
# User: 
# Pass: 
# Telnet port:
def init_raritan_telnet():
    HOST = "<THIS-IS-A-PDU-HOSTNAME.subnet.domain.com>"
    PORT = 1234
    PASSWORD = ""
    USER = ""
    PARSER = ""
    return [HOST, PORT, PASSWORD, USER, PARSER]


# Log into the Raritan power switch in <LOCATION_CODE> (bench-top PDU)
def raritan_log_in(tn, HOST, PORT, PASSWORD, USER, PARSER):
    print("Logging into Raritan swtich, looking for Prompt")
    tn.read_until(PARSER, 5)
    tn.write(USER + "\n")
    #print("Wrote USER name, looking for Password prompt\n")
    tn.read_until("Password:", 5)
    print("Received password prompt")
    tn.write(PASSWORD + "\n")
    #print("Sent password\n")
    tn.read_until("#",5)


# Log into the Raritan power switch in one of the hyper racks
def raritan_hr_log_in(tn, HOST, PORT, PASSWORD, USER, PARSER):
    #tn.set_debuglevel(1)
    print("Logging into Raritan HyperRack swtich, looking for Prompt")
    tn_return_text = tn.read_until(PARSER, 5)
    #print("Recieved User prompt")
    tn.write(USER + "\n\r")
    tn_return_text = tn.read_until(b"Password:", 5)
    print("Received password prompt")
    tn_return_text = tn.write(PASSWORD+ "\n\r")
    #print("Sent password\n")
    tn.read_until("->", 5)


##### Variable enumerators, checkers, and supporting functions: ######

# This function derives whether this machine will be in JF or AN based on the FQDN 
# (contents of /srv/docker.hostname.env on the runner). 
def location_derivation(fqdn):
    if "STRING1" in fqdn:
        return "<LOCATION_CODE>"
    elif ("STRING2" in fqdn) or ("STRING3" in fqdn):
        return "<LOCATION_CODE>"
    else:
        print("Unable to determine if this board resides in <LOCATION_CODE> or \
            <LOCATION_CODE>, please check /srv/docker/hostname.env \n")


# Determine if the FQDN indicates that the board is in a hyper rack
def hyper_rack_checker(fqdn): 
    if "STRING" in fqdn.lower():
        return True
    else:
    	return False


# The Hyper Rack number should be one or two numerical digits that is not zero, derived from FQDN
def hyper_rack_enumerator(fqdn):
# Check if the first digit following 'STRING' is numerical, if so, check to ensure it is a non-zero value
# Return the location of the runner based on FQDN
    hyper_rack_split = str(fqdn.lower()).rsplit("STRING")[1]
    hyper_rack_unit = hyper_rack_split[:2]
    if (hyper_rack_unit.isdigit() == True):
        return int(hyper_rack_unit)
    else:
        hyper_rack_split = str(fqdn.lower()).rsplit("STRING")[1]
        hyper_rack_unit = hyper_rack_split[:1]
        if (hyper_rack_unit.isdigit() == True):
            return int(hyper_rack_unit)            
        else:
            print("Malfomred hostname on runner, STRINGX (HyperRack name) must be at least one numerical digit.")
            print("Example hostname:    <THIS-IS-A-MACHINE-HOSTNAME-EXAMPLE.subnet.domain.com>")
            exit()


# Enumerate the outlet we are going to be working with based on the FQDN
def outlet_enumerator(fqdn):
    host_split = str(fqdn.lower()).rsplit("STRING2")[1]
    # Take the first two digits, conversion to int will drop leading 0 if required
    hyper_rack_outlet_num = host_split[:2]
    if (hyper_rack_outlet_num.isdigit() == True):
        outlet = int(hyper_rack_outlet_num)
        return outlet
    
    # If the 2 characters taken are a single integer & a special character (ie:"2.")
    else:
        hyper_rack_outlet_num = host_split[:1]
        outlet = int(hyper_rack_outlet_num)
        return outlet


# Prints out the message that informs the user of outlet cycling: 
# 'Outlet' is derived from the outlet_enumerator()
def outlet_comms(outlet, fqdn):
    if (outlet >= 1) and (outlet <= 12):
        print("Power cycling outlet {}").format(outlet)
    else:
        print("* Error * Invalid Hostname: Could not derive correct outlet from host name {}").format(fqdn)
        exit()


# Power cycles  individual outlets in the HyperRack mounted Raritan
#  tn         - telnet object
#  outlet     - outlet number (1 ~ 8)
#  pwr_target - "on", "off" or "cycle"
#  cycle delay is optional, defaults to 5 seconds
#  Created the below function because the Raritan (Dominion PX) PDU's 
# do not support "cycle" as a command.
def raritan_hyper_rack_pwr_cycle(tn, outlet, pwr_target, cycle_delay=5):
    if pwr_target == "cycle":
        print("Beginning Power Cycle")
        # Uncomment to print telnet debug messages
        #tn.set_debuglevel(1)
        time.sleep(cycle_delay)
        raritan_pwr_ctl_str = "set /system1/outlet{} powerState=off\n\r".format(outlet)
        print (raritan_pwr_ctl_str)
        tn.write(raritan_pwr_ctl_str)
        tn.read_until("clp:/->", 5)

        #print ("Sleeping for: {}".format(cycle_delay))
        time.sleep(cycle_delay)
        raritan_pwr_ctl_str = "set /system1/outlet{} powerState=on\n\r".format(outlet)
        print (raritan_pwr_ctl_str)
        tn.write(raritan_pwr_ctl_str)
        tn.read_until("clp:/->", 5)
        print("Power Cycle complete")

    else:
        print("raritan_pwr_cycle outlet{}, pwr_target = {}").format(outlet, pwr_target)
        raritan_pwr_ctl_str = "set /system1/outlet{} powerState={}\n\r".format(outlet, pwr_target)
        tn.write(raritan_pwr_ctl_str)

        # Wait for the return prompt
        tn.read_until("clp:/->", 5)


# Power cycles  individual outlets on the power strip
#  tn         - telnet object
#  outlet     - outlet number (1 ~ 8)
#  pwr_target - "cycle"
def raritan_pwr_cycle(tn, outlet, pwr_target):
    print("raritan_pwr_cycle(outlet = {}, pwr_target = {})".format(outlet, pwr_target))
    print("Power cycle outlet {}".format(outlet))

    # the /y on the end eliminates the need to send a 'y' for the 'are you sure' prompt
    raritan_pwr_ctl_str = "power outlets {} {} /y \n".format(outlet, pwr_target)
    print(raritan_pwr_ctl_str)
    tn.write(raritan_pwr_ctl_str)

    # Wait for the return prompt
    tn.read_until("#", 5)


# Control individual outlets on the power strip
#  tn         - telnet object
#  outlet     - outlet number (1 ~ 8)
#  pwr_target - "on", "off"
def raritan_pwr_ctl(tn, outlet, pwr_target):
    print("raritan_pwr_ctl(outlet = %d, pwr_target = %s)\n\r" % (outlet, pwr_target))
    print("Turn outlet %d on" % outlet)

    raritan_pwr_ctl_str = "power outlets {} {} \n".format(outlet, pwr_target)
    print(raritan_pwr_ctl_str)
    tn.write(raritan_pwr_ctl_str)

    tn_return_value = tn.read_until(" [y/n] ", 5)
    print("The read_until returned with - %s -" % tn_return_value)

    tn.write(b"y" + "\n")
    tn.read_until("#", 5)
#    print("Check outlet setting on GUI")
