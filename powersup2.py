from itertools import cycle
import telnetlib
import sys
import time
import os
from raritan_support2 import hyper_rack_checker, hyper_rack_enumerator, location_derivation, \
    init_raritan_hyper_rack_telnet, outlet_enumerator, init_raritan_telnet, raritan_pwr_cycle, \
    raritan_hyper_rack_pwr_cycle, outlet_comms, raritan_hr_log_in, raritan_log_in


#Get Fully Qualified Domain Name
fqdn = os.environ['MACHINE_HOSTNAME']
fqdn = fqdn.rsplit('=')[1]
print(fqdn)

# Parse name to deduce the location of the board/ telnet info
if (location_derivation(fqdn)) == "<LOCATION_CODE>": 
# If the location derivation function returns <LOCATION_CODE>, check if this is in a Hyper Rack
    if hyper_rack_checker(fqdn) == True:
        print("Board is in a hyper rack at <LOCATION_CODE>\n")
        hyper_rack_unit = hyper_rack_enumerator(fqdn)
        HOST, PORT, PASSWORD, USER, PARSER, = init_raritan_hyper_rack_telnet(hyper_rack_unit)

    else:
        print("Board is Located in <LOCATION_CODE>\n")
        HOST, PORT, PASSWORD, USER, PARSER, = init_raritan_telnet()
    
else:
    print("Unable to Extract Power Supply IP from FQDN")
    exit()

#############
# Instatiate Telnet Class Instance
tn = telnetlib.Telnet()
#print('Establishing Telnet Connection')

# Open a Telnet Socket, Retry if another is already open
iterations = 0
while iterations < 20:
    try:
      tn.open(HOST, PORT)
      print("Telnet Connection Open - Power Cycle Board")
      break
    except:
        print("Telnet Interface Connection Busy - Retrying after 5 Sec")
        #traceback.print_exc()
        time.sleep(5)
        iterations += 1

#Test for <LOCATION_CODE> based boards and control power if found.
#The lab uses Raritan PDU's that require a login. The following
#logs us into the Raritan PDU and returns when the login is complete.
#Separate functions are used for different PDU models and locations. 
#Once the login returns, the outlet is selected and cycled.

# If the runner's fqdn indicated that the board is in <LOCATION_CODE> and in a Hyper Rack
if ((location_derivation(fqdn) == "<LOCATION_CODE>") and (hyper_rack_checker(fqdn) == True)):
    # Uncomment the following if you want to see the telnet messages
    #tn.set_debuglevel(5)
    # Find the outlet we want to interact with:
    outlet = outlet_enumerator(fqdn)
    # Declare the power target for Raritan PDU
    pwr_target = "cycle"
    # Login to Raritan Unit
    raritan_hr_log_in(tn, HOST, PORT, PASSWORD, USER, PARSER)
    # Cycle the outlet
    outlet_comms(outlet, fqdn)
    raritan_hyper_rack_pwr_cycle(tn,outlet,pwr_target)
    tn.close()

#If the runner is in <LOCATION_CODE> and not in a Hyper Rack
elif ((location_derivation(fqdn) == "<LOCATION_CODE>") and (hyper_rack_checker(fqdn) == False)):
    # Uncomment the following if you want to see the telnet messages
#    tn.set_debuglevel(5)
    # Find the outlet we want to interact with:
    outlet = outlet_enumerator(fqdn)
    # Declare the power target for <LOCATION_CODE> Hyper Rack Boards
    pwr_target = "cycle"
    # Login to Raritan Unit
    raritan_log_in(tn, HOST, PORT, PASSWORD, USER, PARSER)
    # Cycle the outlet
    outlet_comms(outlet, fqdn)
    raritan_pwr_cycle(tn, outlet, pwr_target)
    tn.close()

else:
    print("Invalid Host Name for Hardware Runner")
