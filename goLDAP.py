#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Name: goLDAP
Author : Mohammed AlHowsa
Brief: An addon for gophish to import users via LDAP
Github : https://github.com/MD-AlHowsa/GoLDAP
'''

#=================================================================


import ldap
import requests
import json
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from ldap.controls import SimplePagedResultsControl
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#=================================================================
def parse_config(config_file):
    global ldap_server
    global us
    global pw
    global attrs
    global base_dn
    global filter
    global ldap_to_gophish_mapping
    global gophish_server
    global gophish_port
    global gophish_api_key
    global group_name
    global update_group

    with open(config_file) as json_data_file:
        config = json.load(json_data_file)

    ldap_server = config['ldap']['server']
    us = config['ldap']['username']
    pw = config['ldap']['password']
    attrs = config['ldap']['attrs']
    base_dn = config['ldap']['base_dn']
    filter = config['ldap']['filter']
    ldap_to_gophish_mapping = config['ldap_to_gophish_mapping']
    gophish_server = config['gophish']['server']
    gophish_port = config['gophish']['port']
    gophish_api_key = config['gophish']['api_key']
    group_name = config['gophish']['group_name']
    update_group = config['gophish']['update_group']


#============= Ldap Connection & search  =======================
def ldap_search(ldap_server,us,pw,base_dn,attrs,filter):

    connect = ldap.initialize(ldap_server)
    connect.set_option(ldap.OPT_REFERRALS, 0)
    connect.simple_bind_s(us, pw)
    page_control = SimplePagedResultsControl(True, size=1000, cookie='')
    response = connect.search_ext(base_dn,ldap.SCOPE_SUBTREE,filter,attrs,0,serverctrls=[page_control])

    result = []
    pages = 0
    while True:

        pages += 1
        rtype, rdata, rmsgid, serverctrls = connect.result3(response)
        result.extend(rdata)
        controls = [control for control in serverctrls
                    if control.controlType == SimplePagedResultsControl.controlType]
        if not controls:
            print('The server ignores RFC 2696 control')
            break
        if not controls[0].cookie:
            break
        page_control.cookie = controls[0].cookie
        response = connect.search_ext(base_dn,ldap.SCOPE_SUBTREE,filter,attrs,0,serverctrls=[page_control])

    return result



#========= orgnize response for Gophish =============
# == remove the bracket of the dict in every value ==
def gophish_format(search_result):
    targets = []
    for i in search_result:
        user = i[1]
        target = {}
        for field in ldap_to_gophish_mapping.keys():
            if ldap_to_gophish_mapping[field] in user:
                target[field] = user[ldap_to_gophish_mapping[field]][0].decode('utf-8')
            else:
                target[field] = ""
        targets.append(target)
    return targets


#=========== check if a group with given name exists, if so, update, otherwise create new =====
def create_group(group_name, gophish_api_key, targets, update_group):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        group = {}
        group['name'] = group_name
        group['targets'] = targets

        response = requests.get("https://"+gophish_server+":"+gophish_port+"/api/groups/summary?api_key="+gophish_api_key,headers=headers,verify=False)
        if response.status_code == 200:
                groups = response.json()['groups']
                for g in groups:
                    if group_name == g['name']:
                        group['id'] = g['id']
                        break

        json_group = json.dumps(group)

        if "id" in group:
                print("Step 1: Trying to update group with ID "+str(group['id']))
                response_toUpload = requests.put("https://"+gophish_server+":"+gophish_port+"/api/groups/"+str(group['id'])+"?api_key="+gophish_api_key,data=json_group,verify=False)
        else:
                print("Step 1: Trying to create new group with name "+group_name)
                response_toUpload = requests.post("https://"+gophish_server+":"+gophish_port+"/api/groups/?api_key="+gophish_api_key,data=json_group,headers=headers,verify=False)

        if response_toUpload.status_code == 201:
                print("Step 2: Done, total number of users is "+str(len(response_toUpload.json()['targets'])))
        elif response_toUpload.status_code == 200:
                print("Step 2: Done, total number of users is "+str(len(response_toUpload.json()['targets'])))
        else:
                print("Step 2: Error, Status Code "+str(response_toUpload.status_code))

def main():
        global ldap_server
        global us
        global pw
        global attrs
        global base_dn
        global filter
        global update_group

        parser = argparse.ArgumentParser(description='Import GoPhish groups from LDAP.')
        parser.add_argument('--config', dest='config_file', default="config.json",
                    help='config file path (default: config.json)')

        args = parser.parse_args()

        parse_config(args.config_file)
        search_result =ldap_search(ldap_server,us,pw,base_dn,attrs,filter)
        targets = gophish_format(search_result)
        create_group(group_name,gophish_api_key,targets,update_group)

if __name__ == "__main__":
        main()

