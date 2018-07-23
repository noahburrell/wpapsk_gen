import argparse
import hashlib
import config

# Setup parser. Parse for gateway IP and UID.
parser = argparse.ArgumentParser("Generate a hostapd.wpa_psk file for the home gateway. Specify the IP address of the gateway to push to config to and a user ID.")
parser.add_argument('IP_ADDR', type=str, help='IP Address of gateway to push to config to.')
parser.add_argument('UID', type=str, help='User ID from which to pull associated devices and tokens.')
args = parser.parse_args()

# Connect to SQL database, pull all devices associated with user ID
connection = config.database.cursor(dictionary=True)
connection.execute("SELECT macadd, token FROM "+config.devicetable+" INNER JOIN "+config.subnettable+" ON "+config.devicetable+".sid = "+config.subnettable+".id INNER JOIN "+config.routertable+" ON "+config.subnettable+".rid = "\
                   + config.routertable+".id WHERE "+config.routertable+".uid = "+args.UID+";")
results = connection.fetchall()

# Generate hostapd.wpa_psk file
hash = hashlib.md5(args.UID+args.IP_ADDR).hexdigest()
f = open(config.saveDir+hash+"_hostapd.wpa_psk", "w+")
for result in results:
    f.write(result['macadd']+" "+result['token']+"\n")
f.close()

# SCP hostapd.wpa_psk file to gateway

# Delete temp hostapd.wpa_psk file
