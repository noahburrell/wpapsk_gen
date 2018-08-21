#!/usr/bin/python
import argparse
import hashlib
import os
import paramiko
from scp import SCPClient
import config
import wireless_config_gen
import common
import time

# Setup parser. Parse for gateway IP and UID.
parser = argparse.ArgumentParser("Generate a hostapd.wpa_psk file for the home gateway. Specify the user ID who's gateways are to be modified.")
parser.add_argument('UID', type=str, help='User ID from which to pull associated devices and tokens.')
parser.add_argument('-p', type=str, help='Password of user to log into the gateway. Used to force provisioning (OPTIONAL)')
parser.add_argument('-c', dest='configure', action='store_true', help='Update gateway /etc/config/wireless file')
parser.add_argument('-v', dest='debugging', action='store_true', help='Verbose output')
parser.set_defaults(debugging=False, configure=False)
args = parser.parse_args()

if args.debugging is True:
    config.debug = True

# Connect to SQL database, pull all devices associated with user ID
connection = config.database.cursor(dictionary=True)
connection.execute("SELECT macadd, token FROM "+config.devicetable+" INNER JOIN "+config.subnettable+" ON "+config.devicetable+".sid = "+config.subnettable+".id INNER JOIN "+config.routertable+" ON "+config.subnettable+".rid = "
                   + config.routertable+".id WHERE "+config.routertable+".uid = "+args.UID+";")
results = connection.fetchall()

if args.debugging is True:
    print results

# Generate hostapd.wpa_psk file
print "Generating hostapd.wpa_psk file for user ID "+args.UID+"..."
hash = hashlib.md5(args.UID).hexdigest()
f = open(config.saveDir+hash+"_hostapd.wpa_psk", "w+")
for result in results:
    f.write(str(result['macadd']).lower()+" "+result['token']+"\n")
f.close()

# Get gateway connection details
connection.execute("SELECT * FROM "+config.gatewaytable+" WHERE uid = "+args.UID+";")
results = connection.fetchall()

# Build a wireless config
# Select all subnets to configure an SSID for each
connection.execute("SELECT * FROM " + config.subnettable + " INNER JOIN " + config.routertable + " ON rid = " + config.routertable + ".id WHERE uid = " + args.UID + ";")
wireless_results = connection.fetchall()

# Generate wireless configs
device_config = wireless_config_gen.gen_device("radio0")
iface_config = ""
for wireless_result in wireless_results:
    iface_config += wireless_config_gen.gen_iface("radio0", {"wifi-iface": str(wireless_result['subname']), "ssid": str(wireless_result['subname'])}) + '\n'

# Write configs to file
f = open(config.saveDir + hash + "_wireless", "w+")
f.write(device_config + "\n" + iface_config)
f.close()

if config.debug is True:
    print "File saved to: " + config.saveDir + hash + "_wireless"
    print device_config + "\n" + iface_config


for result in results:
    if config.debug is True:
        print result

    # Initiate SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Check if gateway needs provisioning
    if result['provisioned'] is 0 or args.p is not None:
        args.configure = True
        print "Gateway ID "+str(result['id'])+" not provisioned. Provisioning..."
        # Update database, set password to null (since key was added to gateway) and set provisioned true
        connection.execute("UPDATE "+config.gatewaytable+" SET provisioned = 1, port = 2222, password = NULL WHERE id = "+str(result['id'])+";")

        # If provisioned is 0 (or a password is manually specified) device needs to be provisioned. Login and copy the public key the the gateway, then secure dropbear
        ssh.connect(result['ip'], port=result['port'], username=result['username'], password=result['password'])
        scp = SCPClient(ssh.get_transport())
        # SCP files needed for provisioning to the gateway
        print "Updating configuration files..."
        scp.put(config.pubkey, "/etc/dropbear/authorized_keys")
        scp.put("deployment/dropbear", '/etc/config/dropbear')
        scp.put("deployment/dnsmasq.conf", '/etc/dnsmasq.conf')
        scp.put("deployment/detect_new_device.sh", '/etc/detect_new_device.sh')
        scp.put("deployment/hostapd.sh", '/lib/netifd/hostapd.sh')
        ssh.exec_command('touch /etc/hostapd.wpa_psk')
        print "Uploading REST client..."
        ssh.exec_command('mkdir /etc/notifier')
        scp.put("deployment/rest_client/main.py", '/etc/notifier/main.py')
        scp.put("deployment/rest_client/config.py", '/etc/notifier/config.py')
        scp.put("deployment/rest_client/common.py", '/etc/notifier/common.py')
        scp.put("deployment/rest_client/request.py", '/etc/notifier/request.py')
        scp.close()
        print "Setting Permissions..."
        ssh.exec_command('chmod +x /etc/detect_new_device.sh')
        ssh.exec_command('chmod +x /lib/netifd/hostapd.sh')
        ssh.exec_command('chmod +x -R /etc/notifier/')
        print "Updating packages (This may take a while)..."
        (stdin, stdout, stderr) = ssh.exec_command('opkg update')
        common.check_status(stdout.channel.recv_exit_status())
        print "Installing Python (This may take a while)..."
        (stdin, stdout, stderr) = ssh.exec_command('opkg install python')
        common.check_status(stdout.channel.recv_exit_status())
        print "Restarting WiFi..."
        (stdin, stdout, stderr) = ssh.exec_command('uci commit wireless; wifi')
        common.check_status(stdout.channel.recv_exit_status())
        print "Restarting dnsmasq..."
        (stdin, stdout, stderr) = ssh.exec_command('/etc/init.d/dnsmasq restart')
        common.check_status(stdout.channel.recv_exit_status())
        print "Restarting Dropbear..."
        (stdin, stdout, stderr) = ssh.exec_command('/etc/init.d/dropbear restart')
        common.check_status(stdout.channel.recv_exit_status())

        # Commit changes to DB after successful provisioning
        config.database.commit()
    else:
        # If no password is set, connect using the private key
        ssh.connect(result['ip'], port=result['port'], username=result['username'], key_filename=config.privkey)

    # Upload wireless config and update hostapd.wpa_psk
    if args.configure:
        print "Copying wireless config to gateway ID " + str(result['id'])
        scp = SCPClient(ssh.get_transport())
        scp.put(config.saveDir + hash + "_wireless", "/etc/config/wireless")
        scp.close()

        print "Restarting network service"
        (stdin, stdout, stderr) = ssh.exec_command('uci commit wireless; wifi')
        common.check_status(stdout.channel.recv_exit_status())

        time.sleep(5)

    common.update_hostapd(ssh, result['id'], hash)

    # Close SSH Session
    ssh.close()

# Delete temp hostapd.wpa_psk (and if exists, wireless) file
try:
    os.remove(config.saveDir + hash + "_hostapd.wpa_psk")
    os.remove(config.saveDir + hash + "_wireless")
except OSError:
    pass
