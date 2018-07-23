import mysql.connector

# Save directory
saveDir = "/tmp/"

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