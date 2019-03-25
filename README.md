# meraki-naemon

Python3 Script for pulling Meraki device info into Nagios & Nagios-derived monitoring systems

usage: meraki_api.py [-h] -k API_KEY -d {switch,ap} -t {license,uplink,port,latency,ssid,failconn,connassoc,connauth,conndhcp,conndns,connsucc,clients}
                     [-o ORGID] [-n NETWORKID] [-s SERIAL] [-w SSID] [-p PORT]

Information from Meraki Dashboard API (https://api.meraki.com/api/v0). For full documentation on the Meraki Dashboard API please see:
- https://dashboard.meraki.com/api_docs
- https://documenter.getpostman.com/view/897512/meraki-dashboard-api/2To9xm

**Required Arguments**:

  -k API_KEY, --api-key API_KEY
  
                        API key obtained from Meraki Dashboard admin account
                        
  -d {switch,ap}, --device {switch,ap}
  
                        Device type to be queried (Wireless AP or Switch)
                        
  -t {license,uplink,port,latency,ssid,failconn,connassoc,connauth,conndhcp,conndns,connsucc,clients}, --type {license,uplink,port,latency,ssid,failconn,connassoc,connauth,conndhcp,conndns,connsucc,clients}

**Supplemental arguments**:

  -o ORGID, --orgid ORGID
  
                        Organization ID
                        
                        API Call (retrieve orgid[s]): GET /organizations
                        
  -n NETWORKID, --networkid NETWORKID
  
                        Network ID
                        
                        API Call (retrieve network id[s]): GET /organizations/<organization ID>/networks
                        
  -s SERIAL, --serial SERIAL
  
                        Meraki Device Serial Number, e.g., ABCD-1234-EF56
                        
                        API Call (retrieve serial number[s]): GET /networks/<network id>/devices
                        
  -w SSID, --ssid SSID
  
                        Specify the SSID by integer, e.g., 0
                        
                        API Call (retrieve SSID number[s]): GET /networks/<network id>/ssids
                        
  -p PORT, --port PORT  
  
                        Switch port number
                        
                        API Call (retrieve stats for all switch ports): GET /devices/<serial number>/switchPorts


**EXPLANATION & USAGE**
                        
    I. All devices
        license: Expiration of Meraki device license
        	-t license -o <organization id>
        uplink:	Status of Meraki device connection to the cloud
        	-t uplink -n <network id> -s <serial number>

    II. Switch Options
        port: Get status on an individual switchport
        	-t port -s <serial number> -p <port number>

    III. AP Options
        latency: Latency stats over the past hour per AP
        	-t latency -n <network id> -s <serial>
        ssid: Status of configured SSID(s)	
        	-t ssid -n <network id> -w <#>
        failconn: Number of failed connections over the past hour
        	-t failconn -n <network id>
        connassoc, connauth, conndhcp, conndns, connsucc: Connection stats per AP over the past hour at different stages
            -t [connassoc, connauth, conndhcp, conndns, connsucc] -n <network id> -s <serial number>
        clients: Number of connected clients per AP within the past 2 hours
                -t clients -s <serial number>

