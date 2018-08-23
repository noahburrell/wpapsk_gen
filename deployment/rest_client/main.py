#!/usr/bin/python
import common
import argparse
import json
import subprocess
import config

parser = argparse.ArgumentParser("Update the MAC address associated with a PSK")
parser.add_argument("PSK", type=str)
parser.add_argument("MAC", type=str, help="XX:XX:XX:XX:XX:XX")
args = parser.parse_args()
args.MAC = str(args.MAC).upper()

# Check if the device's current WAN address matches service records
# If WAN address does not match service records, update the service records
f = open(config.service_records)
json_data = json.loads(f.read())[0]
datapoints = json_data['datapoints']
f.close()
bash_command = "/sbin/ifconfig eth0.2 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}'"
process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
current_ip = output
if json_data['ip'] is not current_ip:
    common.update_ip(json_data['ip'])

# Update mac address
device_info = common.lookup_psk(args.PSK)
if device_info['device']['token'] != args.PSK:
    raise ValueError("Could not find specified PSK")
mac_update = common.update_mac(str(device_info['device']['id']), args.MAC)
if mac_update['status'] is not True:
    raise ValueError("MAC did not successfully update")

print "Successfully updated MAC address"
