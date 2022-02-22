#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Name: goLDAP
Author : Mohammed AlHowsa
Brief: An addon for gophish to import users via LDAP
Github : https://github.com/md-howsa
'''



#====================== Configuration ==========================



ldap_server = 'ldap://ldap_IP'
us = 'us' 
pw = 'pw' 

base_dn =  'ou=Users,,dc=example,dc=com'
col_names = 'Email, First Name, Last Name,position'

gophish_server = 'localhost'
gophish_port = '3333'
gophish_api_key = 'api_key'
group_name = "example group"
update_group = 0 

#=================================================================






import ldap
import csv
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from ldap.controls import SimplePagedResultsControl
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


filter = 'objectClass=user'
attrs = ['mail','givenname','sn','position'] 
csv_output_file = 'users.csv' 

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
        print(len(result))
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
        for i in search_result:
            temp_m = i[1].get('mail')
            temp_g = i[1].get('givenName')
            temp_s = i[1].get('sn')
            temp_p = i[1].get('position')
            if temp_m:
                i[1]['mail'] = temp_m[0].decode('utf-8')
                if temp_g:
                        i[1]['givenName'] = temp_g[0].decode('utf-8')
                        if temp_s:
                                i[1]['sn'] = temp_s[0].decode('utf-8')
                if temp_p:
                    i[1]['position'] = temp_p[0].decode('utf-8')
        return search_result


#========= to create CSV file of the LDAP result =====
def result_to_csv(result,col_names,csv_output_file):
        dest_file_name = csv_output_file
        with open(dest_file_name, 'w') as file:
            users = [x[1]  for x in result]
            file.write(col_names)
            file.write("\n")
            w = csv.DictWriter(file,users[0].keys())
            w.writerows(users)


#=========== convert csv to Json then uplad it through API =====
def upload_csv(group_name,gophish_api_key, csv_output_file,update_group):
        fileObj = {'file': open(csv_output_file,'rb')}
        response_toJson = requests.post("https://"+gophish_server+":"+gophish_port+"/api/import/group?api_key="+gophish_api_key,files=fileObj,verify=False)
        if response_toJson.status_code == 200:
                print("Step 1: CSV file has seccfully transformed to Json format")
        else:
                print("Step 1: Error, Status Code "+str(response_toJson.status_code))
        group = {}
        group['name'] = group_name
        group['targets'] = response_toJson.json()
        if update_group:
                group['id'] = update_group
        json_group = json.dumps(group)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        if update_group:
                print("Trying to update group with ID "+str(update_group))
                response_toUpload = requests.put("https://"+gophish_server+":"+gophish_port+"/api/groups/"+str(update_group)+"?api_key="+gophish_api_key,data=json_group,verify=False)
        else:
                print("Trying to create new group with name "+group_name)
                response_toUpload = requests.post("https://"+gophish_server+":"+gophish_port+"/api/groups/?api_key="+gophish_api_key,data=json_group,headers=headers,verify=False)

        if response_toUpload.status_code == 201:
                print("Step 2: Done, total number of users is "+str(len(response_toUpload.json()['targets'])))
        elif response_toUpload.status_code == 409 :
                print("Step 2: Group is Already created,put the group is in the configuration section of the code instead of 0")
                print("Status code = "+str(response_toUpload.status_code))
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
        global csv_output_file
        global col_names
        global update_group

        search_result =ldap_search(ldap_server,us,pw,base_dn,attrs,filter)
        result = gophish_format(search_result)
        result_to_csv(result,col_names,csv_output_file)
        upload_csv(group_name,gophish_api_key,csv_output_file,update_group)

if __name__ == "__main__":
        main()

