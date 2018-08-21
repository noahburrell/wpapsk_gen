import config
import hashlib
import time
import request
import json


def create_xauth_token():
    token = str(hashlib.sha512(config.xauth_base+str(int(time.time()))).hexdigest()).upper()
    if config.debug:
        print "Time: "+str(int(time.time()))
        print "X-Auth-Token: "+token
    return token


def lookup_psk(psk):
    return request.get_data(config.server_ip, "/api/v1.0/psk/", config.uid+"/"+psk, create_xauth_token())


def update_mac(device_id, new_mac):
    data = \
        {
            "mac_add": new_mac
        }
    return request.put_data(config.server_ip, "/api/v1.0/mac/"+config.uid+"/"+device_id, json.dumps(data), create_xauth_token())
