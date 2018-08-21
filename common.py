from scp import SCPClient
import config


def check_status(exit_status, output=True):
    if exit_status == 0:
        if output is True:
            print ("COMPLETE!")
    else:
        print("Error", exit_status)


def update_hostapd(ssh, gateway, hash):
    # Upload hostapd.wpa_psk file
    print "Copying hostapd.wpa_psk to gateway ID "+str(gateway)
    scp = SCPClient(ssh.get_transport())
    scp.put(config.saveDir+hash+"_hostapd.wpa_psk", "/etc/hostapd.wpa_psk")
    (stdin, stdout, stderr) = ssh.exec_command('cat '+config.pidfile)
    check_status(stdout.channel.recv_exit_status(), False)
    pid = stdout.read()
    print "Restarting PID: "+pid
    (stdin, stdout, stderr) = ssh.exec_command('kill -1 '+pid)
    scp.close()