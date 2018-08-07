import mysql.connector

# Debugging
debug = False

# Save directory
saveDir = "/tmp/"

# RSA Keyfile locations
privkey = "/home/noah/.ssh/id_rsa"
pubkey = "/home/noah/.ssh/id_rsa.pub"

# Location of hostapd keyfile location on gateway
pidfile = "/var/run/wifi-phy0.pid"

# Initialize connection to database
database = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="telus"
)

# Define various database table name
usertable = "loginInfo"
routertable = "routerTable"
subnettable = "subnetTable"
porttable = "portTable"
devicetable = "deviceTable"
gatewaytable = "gateways"

# Default device configuration
default_device_config = {
        "wifi-device": "",  # DO NOT CHANGE IN THIS FILE
        "type": "mac80211",
        "hwmode": "11a",
        "path": "pci0000:01/0000:01:00.0",
        "country": "US",
        "legacy_rates": "1",
        "channel": "48",
        "htmode": "HT20"
    }

# Default interface configuration
default_iface_config = {
    "wifi-iface": "",  # DO NOT CHANGE IN THIS FILE
    "device": "",  # DO NOT CHANGE IN THIS FILE
    "network": "lan",
    "mode": "ap",
    "ssid": "OpenWRT",
    "encryption": "psk2",
    "wpa_psk_file": "/etc/hostapd.wpa_psk",
    "isolate": "1"
}
