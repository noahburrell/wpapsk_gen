#!/usr/bin/python
import common
import argparse


parser = argparse.ArgumentParser("Update the MAC address associated with a PSK")
parser.add_argument("PSK", type=str)
parser.add_argument("MAC", type=str, help="XX:XX:XX:XX:XX:XX")
args = parser.parse_args()
args.MAC = str(args.MAC).upper()

device_info = common.lookup_psk(args.PSK)
if device_info['device']['token'] != args.PSK:
    raise ValueError("Could not find specified PSK")
mac_update = common.update_mac(str(device_info['device']['id']), args.MAC)
if mac_update['status'] is not True:
    raise ValueError("MAC did not successfully update")

print "Successfully updated MAC address"
