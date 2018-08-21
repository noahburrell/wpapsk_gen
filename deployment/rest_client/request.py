import urllib2
import json


def post_data(ip, postLocation, postdata, authToken):
    try:
        url = "http://"+ip+postLocation
        req = urllib2.Request(url, postdata, headers={'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': authToken})
        response = urllib2.urlopen(req)
        return json.loads(response.read())
    except urllib2.HTTPError as e:
        error_message = e.read()
        return error_message


def get_data(ip, getLocation, parameters, authToken):
    try:
        url = "http://"+ip+getLocation+parameters
        req = urllib2.Request(url, headers={'Accept': 'application/json', 'X-Auth-Token': authToken})
        response = urllib2.urlopen(req)
        return json.loads(response.read())
    except urllib2.HTTPError as e:
        error_message = e.read()
        print error_message


def put_data(ip, putLocation, data, authToken):
    try:
        url = "http://" + ip + putLocation
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url, data, headers={'Content-type': 'application/json', 'Accept': 'application/json', 'X-Auth-Token': authToken})
        req.get_method = lambda: 'PUT'
        response = opener.open(req)
        response = response.read()
        return json.loads(response)
    except urllib2.HTTPError as e:
        error_message = e.read()
        print error_message


def del_data(ip, delLocation, authToken):
    try:
        url = "http://" + ip + delLocation
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(url, headers={'Accept': 'application/json', 'X-Auth-Token': authToken})
        req.get_method = lambda: 'DELETE'
        response = opener.open(req)
        response = response.read()
        if response is not "":
            return False
        else:
            return True
    except urllib2.HTTPError as e:
        error_message = e.read()
        print error_message
        return False
