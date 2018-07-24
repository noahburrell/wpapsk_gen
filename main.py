import argparse
import hashlib
import os
import paramiko
from scp import SCPClient
import config

# Setup parser. Parse for gateway IP and UID.
parser = argparse.ArgumentParser("Generate a hostapd.wpa_psk file for the home gateway. Specify the IP address of the gateway to push to config to and a user ID.")
parser.add_argument('UID', type=str, help='User ID from which to pull associated devices and tokens.')
parser.add_argument('IP_ADDR', type=str, help='IP Address of gateway to push to config to.')
parser.add_argument('PORT', type=str, help='Port number SSH is listening on.')
parser.add_argument('GW_LOGIN', type=str, help='User to log into the gateway as.')
parser.add_argument('GW_PASS', type=str, help='Password of user to log into the gateway.')
args = parser.parse_args()

# Connect to SQL database, pull all devices associated with user ID
connection = config.database.cursor(dictionary=True)
connection.execute("SELECT macadd, token FROM "+config.devicetable+" INNER JOIN "+config.subnettable+" ON "+config.devicetable+".sid = "+config.subnettable+".id INNER JOIN "+config.routertable+" ON "+config.subnettable+".rid = "
                   + config.routertable+".id WHERE "+config.routertable+".uid = "+args.UID+";")
results = connection.fetchall()

# Generate hostapd.wpa_psk file
hash = hashlib.md5(args.UID+args.IP_ADDR).hexdigest()
f = open(config.saveDir+hash+"_hostapd.wpa_psk", "w+")
for result in results:
    f.write(result['macadd']+" "+result['token']+"\n")
f.close()

# SCP hostapd.wpa_psk file to gateway
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(args.IP_ADDR, port=args.PORT, username=args.GW_LOGIN, password=args.GW_PASS)
scp = SCPClient(ssh.get_transport())
scp.put(config.saveDir+hash+"_hostapd.wpa_psk", "/etc/hostapd.wpa_psk")
scp.close()
ssh.close()

# Delete temp hostapd.wpa_psk file
os.remove(config.saveDir+hash+"_hostapd.wpa_psk")
