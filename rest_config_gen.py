def generate(uid,server_address,xauth,debugging="False"):
    device_config = (
            "debug = "+str(debugging)+"\n"
            "uid = '"+str(uid)+"'\n"
            "server_ip = '"+str(server_address)+"'\n"
            "xauth_base = '"+str(xauth)+"'\n"
            "service_records = \"/etc/service_records\"\n"
    )
    return device_config
