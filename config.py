import mysql.connector

# Save directory
saveDir = "/tmp/"

# RSA Keyfile locations
privkey = "/home/noah/.ssh/id_rsa"
pubkey = "/home/noah/.ssh/id_rsa.pub"

# Location of hostapd keyfile location on gateway
pidfile = "/var/run/wifi-phy1.pid"

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