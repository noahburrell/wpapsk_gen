#!/usr/bin/python
import argparse
import hashlib
import os
import paramiko
from scp import SCPClient
import config

# Setup parser. Parse for gateway IP and UID.
parser = argparse.ArgumentParser("Generate a hostapd.wpa_psk file for the home gateway. Specify the IP address of the gateway to push to config to and a user ID.")
parser.add_argument('UID', type=str, help='User ID from which to pull associated devices and tokens.')
parser.add_argument('-p', type=str, help='Password of user to log into the gateway. (OPTIONAL) Only required on first login, will use authorized keys after')
parser.add_argument('-v', dest='debugging', action='store_true', help='Verbose output')
parser.set_defaults(debugging=False)
args = parser.parse_args()

# Connect to SQL database, pull all devices associated with user ID
connection = config.database.cursor(dictionary=True)
connection.execute("SELECT macadd, token FROM "+config.devicetable+" INNER JOIN "+config.subnettable+" ON "+config.devicetable+".sid = "+config.subnettable+".id INNER JOIN "+config.routertable+" ON "+config.subnettable+".rid = "
                   + config.routertable+".id WHERE "+config.routertable+".uid = "+args.UID+";")
results = connection.fetchall()

# Generate hostapd.wpa_psk file
print "Generating hostapd.wpa_psk file for user ID "+args.UID+"..."
hash = hashlib.md5(args.UID).hexdigest()
f = open(config.saveDir+hash+"_hostapd.wpa_psk", "w+")
for result in results:
    f.write(str(result['macadd']).lower()+" "+result['token']+"\n")
f.close()

# Get gateway connection details
connection.execute("SELECT * FROM "+config.gatewaytable+" WHERE id = "+args.UID+";")
results = connection.fetchall()
for result in results:
    # SCP hostapd.wpa_psk file to gateway and SIGHUP
    print result
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if result['provisioned'] is 0:
        print "Gateway ID "+str(result['id'])+" not provisioned. Provisioning..."
        # If a password is specified device needs to be provisioned. Login and copy the public key the the gateway, then secure dropbear
        ssh.connect(result['ip'], port=result['port'], username=result['username'], password=result['password'])
        scp = SCPClient(ssh.get_transport())
        scp.put(config.pubkey, "/etc/dropbear/authorized_keys")
        scp.put("dropbear.txt", '/etc/config/dropbear')
        (stdin, stdout, stderr) = ssh.exec_command('/etc/init.d/dropbear restart')
        scp.close()
        # Update database, set password to null (since key was added to gateway) and set provisioned true
        connection.execute("UPDATE "+config.gatewaytable+" SET provisioned = 1, password = NULL WHERE id = "+str(result['id'])+";")
        config.database.commit()
    else:
        # If no password is set, connect using the private key
        ssh.connect(result['ip'], port=result['port'], username=result['username'], key_filename=config.privkey)
    print "Copying hostapd.wpa_psk to gateway ID "+str(result['id'])
    scp = SCPClient(ssh.get_transport())
    scp.put(config.saveDir+hash+"_hostapd.wpa_psk", "/etc/hostapd.wpa_psk")
    (stdin, stdout, stderr) = ssh.exec_command('cat '+config.pidfile)
    pid = stdout.read()
    (stdin, stdout, stderr) = ssh.exec_command('kill -1 '+pid)
    scp.close()
    ssh.close()

# Delete temp hostapd.wpa_psk file
os.remove(config.saveDir+hash+"_hostapd.wpa_psk")