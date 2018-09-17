#!/usr/bin/python
import common
import argparse
import subprocess, shlex
import config

parser = argparse.ArgumentParser("Update the MAC address associated with a PSK")
parser.add_argument("PSK", type=str)
parser.add_argument("MAC", type=str, help="XX:XX:XX:XX:XX:XX")
args = parser.parse_args()
args.MAC = str(args.MAC).upper()

# Check if the device's current WAN address matches service records
# If WAN address does not match service records, update the service records
f = open(config.service_records)
last_good_ip = f.read()
f.close()

bash_command = ["/sbin/ifconfig eth0.2", "grep 'inet addr'", "cut -d: -f2", "awk '{print $1}'"]
command_args = shlex.split(bash_command[0])
process = subprocess.Popen(command_args, stdout=subprocess.PIPE)
command_args = shlex.split(bash_command[1])
process = subprocess.Popen(command_args, stdin=process.stdout, stdout=subprocess.PIPE)
command_args = shlex.split(bash_command[2])
process = subprocess.Popen(command_args, stdin=process.stdout, stdout=subprocess.PIPE)
command_args = shlex.split(bash_command[3])
process = subprocess.Popen(command_args, stdin=process.stdout, stdout=subprocess.PIPE)
output, error = process.communicate()
current_ip = output

if last_good_ip is not current_ip:
    api_response = common.update_ip(last_good_ip)
    print "\nLocal service record: " + last_good_ip
    print "API reported IP: " + api_response['new_ip']
    print "WAN Interface IP: " + current_ip
    if api_response["old_ip"] != api_response["new_ip"]:
        f = open(config.service_records, "w")
        f.write(api_response["new_ip"])
        print "Current and previous IPs differ, service record updated!"
    else:
        print "API reported IP and local record are identical but do not match WAN interface IP address. Assuming "\
        "gateway exists within NATed network!"


# Update mac address
print args.PSK
device_info = common.lookup_psk(args.PSK)
if device_info['device']['token'] != args.PSK:
    raise ValueError("Could not find specified PSK")
mac_update = common.update_mac(str(device_info['device']['id']), args.MAC)
if mac_update['status'] is not True:
    raise ValueError("MAC did not successfully update")

print "Successfully updated MAC address"
