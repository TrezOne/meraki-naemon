#!/usr/bin/python3

"""This script is for pulling information from the Meraki API Dashboard into any Nagios and Nagios-based monitoring system, e.g. Naemon"""

import requests, json, argparse, re, datetime

################################
# BEGIN ARGPARSE FUNCTIONALITY #
################################
parser = argparse.ArgumentParser(description='''Information from Meraki Dashboard API (https://api.meraki.com/api/v0). For full documentation on the Meraki Dashboard API please see:
- https://dashboard.meraki.com/api_docs
- https://documenter.getpostman.com/view/897512/meraki-dashboard-api/2To9xm''', formatter_class=argparse.RawTextHelpFormatter)
parser._action_groups.pop()
requiredNamed = parser.add_argument_group('required arguments')
optionalNamed = parser.add_argument_group('supplemental arguments')
requiredNamed.add_argument('-k', '--api-key', required=True, help='''API key obtained from Meraki Dashboard admin account''')
requiredNamed.add_argument('-d', '--device', choices=['switch', 'ap'], required=True, help='''Device type to be queried (Wireless AP or Switch)''')
requiredNamed.add_argument('-t', '--type', choices=['license', 'uplink', 'port', 'poe', 'latency', 'ssid', 'failconn', 'connassoc', 'connauth', 'conndhcp', 'conndns', 'connsucc', 'clients'], required=True, help='''
-=EXPLANATION & USAGE=-

I. All devices
license: Expiration of Meraki device license
	-t license -o <organization id>
uplink:	Status of Meraki device connection to the cloud
	-t uplink -n <network id> -s <serial number>

II. Switch Options
port: Get status on an individual switchport (Enabled/Disabled)
	-t port -s <serial number> -p <port number>
poe: Get POE status on an individual switchport (Enabled/Disabled)
	-t poe -s <serial number> -p <port number>

III. AP Options
latency: Latency stats over the past hour per AP
	-t latency -n <network id> -s <serial>
ssid: Status of configured SSID(s)	
	-t ssid -n <network id> -w <#>
failconn: Number of failed connections over the past hour
	-t failconn -n <network id>
connassoc, connauth, conndhcp, conndns, connsucc: Connection stats per AP over the past hour at different stages (No warning/critical values for type connsucc)
        -t [connassoc, connauth, conndhcp, conndns, connsucc] -n <network id> -s <serial number>
clients: Number of connected clients per AP within the past 2 hours
        -t clients -s <serial number> 
''')
optionalNamed.add_argument('-o', '--orgid', type=int, help='''Organization ID
API Call (retrieve orgid[s]): GET /organizations

''')
optionalNamed.add_argument('-n', '--networkid', help='''Network ID
API Call (retrieve network id[s]): GET /organizations/<organization ID>/networks

''')
optionalNamed.add_argument('-s', '--serial', help='''Meraki Device Serial Number, e.g., ABCD-1234-EF56
API Call (retrieve serial number[s]): GET /networks/<network id>/devices

''')
optionalNamed.add_argument('-w', '--ssid', type=int, help='''
Specify the SSID by integer, e.g., 0
API Call (retrieve SSID number[s]): GET /networks/<network id>/ssids

''')
optionalNamed.add_argument('-p', '--port', type=int, help='''Switch port number
API Call (retrieve stats for all switch ports): GET /devices/<serial number>/switchPorts''')
args = parser.parse_args()
##############################
# END ARGPARSE FUNCTIONALITY #
##############################

#######################################
# DEFINE REQUEST (BASE URL & HEADERS) #
#######################################
merapi_url = "https://api.meraki.com/api/v0"
headers = {'Content-Type': 'application/json', 'X-Cisco-Meraki-API-Key': args.api_key}

###################
# TYPE FUNCTIONS  #
###################

def licensestate(args):
    "Retrieves the license status of a single device (may have to be modified if additional AP is added to network)"
    httpreq = merapi_url + "/organizations/" + str(args.orgid) + "/licenseState"
    try:
        license_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(2) 
    license_status = license_info['status']
    license_expire = license_info['expirationDate']
    if license_status == 'OK':
        print("License status is OK. Expiration Date: " + str(license_expire))
        exit(0)
    elif license_status != 'OK':
        print("Check Meraki AP license status. Expiration Date: " + str(license_expire))
        exit(1)

def uplinkstatus(args):
    "Returns the WAN connectivity status of a device"
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/devices/" + str(args.serial) + "/uplink" 
    try:
        uplink_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    uplink_status = uplink_info[0]['status']
    uplink_pubip = uplink_info[0]['publicIp']
    if uplink_status == 'Active':
        print("Uplink status is OK. Public IP: " + str(uplink_pubip))
        exit(0)
    elif uplink_status != 'Active':
        print("Check Meraki AP uplink status. Public IP: " + str(uplink_pubip))
        exit(2)

def portstat(args): # To be completed once switch ships in
    "Returns the status of an individual port on a switch"
    httpreq = merapi_url + "/devices/" + str(args.serial) + "/switchPorts/" + str(args.port)
    try:
        port_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3)
    port_enabled = (port_info['enabled'])
    if port_enabled == 'True':
        print("enabled: " + str(port_enabled))
        exit(0)
    elif port_enabled == 'False':
        print("disabled: " + str(port_enabled))
        exit(2)

def poeport(args): # To be completed once switch ships in
    "Returns the status of an individual port on a switch"
    httpreq = merapi_url + "/devices/" + str(args.serial) + "/switchPorts/" + str(args.port)
    try:
        port_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3)
    port_poeEnabled = (port_info['poeEnabled'])
    if port_poeEnabled == 'True':
        print("enabled: " + str(port_poeEnabled))
        exit(0)
    elif port_poeEnabled == 'False':
        print("disabled: " + str(port_poeEnabled))
        exit(2)

def ssidstatus(args):
    "Retrieves configured SSID status (enabled or not)"
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/ssids/" + str(args.ssid)
    try:
        ssid_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    ssid_name = ssid_info['name']
    ssid_status = str(ssid_info['enabled'])
    if re.match(r"^Unconfigured*", ssid_name):
        print("Invalid integer. SSID referenced is unconfigured.")
        exit(1)
    else:
        if ssid_status == 'True':
            print(str(ssid_name) + " is enabled and active.")
            exit(0)
        elif ssid_status == 'False':
            print(str(ssid_name) + " is not enabled and active. Please login to Meraki Dashboard to check.")
            exit(2)

def latencystats(args):
    "Retrieves latency stats for network per AP"
    currtime = int(datetime.datetime.now().strftime('%s'))
    starttime = currtime - 3600
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/devices/" + str(args.serial) + "/latencyStats?t0=" + str(starttime) + "&t1=" + str(currtime) + "&fields=avg"
    try:
        lat_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    be_traffic = lat_info['latencyStats']['bestEffortTraffic']['avg']
    if be_traffic <= 128:
        print("OK: Average latency for AP is: " + str(be_traffic) + "ms | latency_stat=" + str(be_traffic) + ";128;512;;")
        exit(0)
    elif be_traffic >= 128:
        print("WARNING: Average latency for AP is: " + str(be_traffic) + "ms | latency_stat=" + str(be_traffic) + ";128;512;;")
        exit(1)
    elif be_traffic >= 512:
        print("CRITICAL: Average latency for AP is: " + str(be_traffic) + "ms | latency_stat=" + str(be_traffic) + ";128;512;;")
        exit(2)

def connectionassoc(args):
    "Retrieves connectivity stats for network (Association Step)"
    currtime = int(datetime.datetime.now().strftime('%s'))
    starttime = currtime - 3600
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/devices/" + str(args.serial) + "/connectionStats?t0=" + str(starttime) + "&t1=" + str(currtime)
    try:
        conn_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    c_assoc = conn_info['connectionStats']['assoc']
    if c_assoc < 5:
        print("OK: Associations in the past hour: " + str(c_assoc) + " | " + "conn_assoc=" + str(c_assoc) + ";5;10;;")
        exit(0)
    elif c_assoc >= 5:
        print("WARNING: Associations in the past hour: " + str(c_assoc) + " | " + "conn_assoc=" + str(c_assoc) + ";5;10;;")
        exit(1)
    elif c_assoc >= 10:
        print("CRITICAL: Associations in the past hour: " + str(c_assoc) + " | " + "conn_assoc=" + str(c_assoc) + ";5;10;;")
        exit(2)

def connectionauth(args):
    "Retrieves connectivity stats for network (Authentication Step)"
    currtime = int(datetime.datetime.now().strftime('%s'))
    starttime = currtime - 3600
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/devices/" + str(args.serial) + "/connectionStats?t0=" + str(starttime) + "&t1=" + str(currtime)
    try:
        conn_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    c_auth = conn_info['connectionStats']['auth']
    if c_auth < 10:
        print("OK: Authentications in the past hour: " + str(c_auth) + " | " + "conn_auth=" + str(c_auth) + ";10;20;;")
        exit(0)
    elif c_auth >= 10:
        print("WARNING: Authentications in the past hour: " + str(c_auth) + " | " + "conn_auth=" + str(c_auth) + ";10;20;;")
        exit(1)
    elif c_auth >= 20:
        print("CRITICAL: Authentications in the past hour: " + str(c_auth) + " | " + "conn_auth=" + str(c_auth) + ";10;20;;")
        exit(2)

def connectiondhcp(args):
    "Retrieves connectivity stats for network (DHCP Step)"
    currtime = int(datetime.datetime.now().strftime('%s'))
    starttime = currtime - 3600
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/devices/" + str(args.serial) + "/connectionStats?t0=" + str(starttime) + "&t1=" + str(currtime)
    try:
        conn_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    c_dhcp = conn_info['connectionStats']['dhcp']
    if c_dhcp < 10:
        print("OK: DHCP Requests in the past hour: " + str(c_dhcp) + " | " + "conn_dhcp=" + str(c_dhcp) + ";10;20;;")
        exit(0)
    elif c_dhcp >= 10:
        print("WARNING: DHCP Requests in the past hour: " + str(c_dhcp) + " | " + "conn_dhcp=" + str(c_dhcp) + ";10;20;;")
        exit(1)
    elif c_dhcp >= 20:
        print("CRITICAL: DHCP Requests in the past hour: " + str(c_dhcp) + " | " + "conn_dhcp=" + str(c_dhcp) + ";10;20;;")
        exit(2)

def connectiondns(args):
    "Retrieves connectivity stats for network (DNS Resolution Step)"
    currtime = int(datetime.datetime.now().strftime('%s'))
    starttime = currtime - 3600
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/devices/" + str(args.serial) + "/connectionStats?t0=" + str(starttime) + "&t1=" + str(currtime)
    try:
        conn_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    c_dns = conn_info['connectionStats']['dns']
    if c_dns < 10:
        print("OK: DNS Queries in the past hour: " + str(c_dns) + " | " + "conn_dns=" + str(c_dns) + ";10;20;;")
        exit(0)
    elif c_dns >= 10:
        print("WARNING: DNS Queries in the past hour: " + str(c_dns) + " | " + "conn_dns=" + str(c_dns) + ";10;20;;")
        exit(1)
    elif c_dns >= 20:
        print("CRITICAL: DNS Queries in the past hour: " + str(c_dns) + " | " + "conn_dns=" + str(c_dns) + ";10;20;;")
        exit(2)

def connectionsucc(args):
    "Retrieves connectivity stats for network (Successful Connection)"
    currtime = int(datetime.datetime.now().strftime('%s'))
    starttime = currtime - 3600
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/devices/" + str(args.serial) + "/connectionStats?t0=" + str(starttime) + "&t1=" + str(currtime)
    try:
        conn_info = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    c_succ = conn_info['connectionStats']['success']
    if c_succ > 0:
        print("OK: Successful connections in the past hour: " + str(c_succ) + " | " + "conn_succ=" + str(c_succ) + ";;0;;")
        exit(0)
    else:
        print("CRITICAL: Successful connections in the past hour: " + str(c_succ) + " | " + "conn_succ=" + str(c_succ) + ";;0;;")
        exit(2)

def failedconnections(args):
    "Retrieves number of failed connections for network"
    currtime = int(datetime.datetime.now().strftime('%s'))
    starttime = currtime - 3600
    httpreq = merapi_url + "/networks/" + str(args.networkid) + "/failedConnections?t0=" + str(starttime) + "&t1=" + str(currtime)
    try:
        fail_api = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    fail_clients = []
    i = 0
    while i < len(fail_api):
        fail_clients.append("Client " + fail_api[i]['clientMac'] + " failed to connect (step: " + fail_api[i]['failureStep'] +")")
        i += 1
    print("Number of failed connections in the past hour: " + str(len(fail_api)) + "\n" + "\n".join(fail_clients) + " | " + "fail_conn=" + str(len(fail_api)) + ";15;25;;")
    if len(fail_api) >= 0:
        exit(0)
    elif len(fail_api) >= 10:
        exit(1)
    elif len(fail_api) >= 20:
        exit(2)

def clients(args):
    "Retrieves number of currently connected clients per AP"
    httpreq = merapi_url + "/devices/" + str(args.serial) + "/clients?timespan=360"
    try:
        clients_api = requests.get(httpreq, headers=headers).json()
    except:
        print("Unable to connect to Meraki Dashboard API.")
        exit(3) 
    num_clients = []
    i = 0 
    while i < len(clients_api):
        num_clients.append("Client: " + str(clients_api[i]['description']) + " (IP: " + str(clients_api[i]['ip']) + ", Mac Address: " + str(clients_api[i]['mac']) + ")")
        i += 1
    print("Number of clients connected: " + str(len(num_clients)) + "\n" + "\n".join(num_clients) + " | " + "num_clients=" + str(len(num_clients)) + ";10;0;;")
    if len(num_clients) >= 5: 
        exit(0)
    elif len(num_clients) < 5: 
        exit(1)
    elif len(num_clients) == 0:
        exit(2)

if args.device == 'switch':
    if args.type == 'license':
        licensestate(args)
    elif args.type == 'uplink':
        uplinkstatus(args)
    elif args.type == 'port':
        portstat(args)
    elif args.type == 'poe':
        poeport(args)
elif args.device == 'ap':
    if args.type == 'license':
        licensestate(args)
    elif args.type == 'uplink':
        uplinkstatus(args)
    elif args.type == 'ssid':
        ssidstatus(args)
    elif args.type == 'latency':
        latencystats(args) 
    elif args.type == 'connassoc':
        connectionassoc(args)
    elif args.type == 'connauth':
        connectionauth(args)
    elif args.type == 'conndhcp':
        connectiondhcp(args)
    elif args.type == 'conndns':
        connectiondns(args)
    elif args.type == 'connsucc':
        connectionsucc(args) 
    elif args.type == 'clients':
        clients(args)
    elif args.type == 'failconn':
        failedconnections(args)
