# GoLDAP

GoLDAP is a **[Gophish](https://getgophish.com/)** addon that retrieves users from your **active directory** via **LDAP** protocol and then import them into a predefined group in your Gophish . By defualt LDAP will not return more than 1000 entries as a result for your query. However, GoLDAP uses LDAP paging to retrieve as many users as your container has. If you have ideas to improve the script, do not hesitate to contact me on:  
moh2006s@hotmail.com


# GoLDAP requirements 
 - Requests 
 - Python-ldap 
	 - libsasl2-dev 
	 - python-dev 
	 - libldap2-dev 
	 - libssl-dev
	 - perhaps others. 
 
# GoLDAP Configuration

A configuration example is given in the config.json file.

## LDAP related items in the "ldap" dictionary

`ldap_server =` 'ldap://ldap_server_IP'  

If your LDAP port is not the defualt one "389", spesicy the port after the IP addreess as follows:  ldap://ip_address:port

Active directory credential  
`us =`  'username'  
`pw =` 'password'  


`base_dn =`  'Location of the container'

>  The Base DN setting specifies the root for searches in the Active
> Directory, e.g, if your domain name is "example.local". Convert it
> into  "dc=example,dc=local". Assuming your  targeted users are in the
> default location, the OU named "Users", it will be converted  to
> "ou=users". the final search for users will be
> "ou=users,dc=example,dc=local". To find the right container consult you
> system admin. Read more about "[LDAP data Interchange
> Format](http://en.wikipedia.org/wiki/LDAP_Data_Interchange_Format)"

`attrs =`    'A list of the user attributes to fetch from LDAP'

## Mapping between LDAP attributes and GoPhish fields are in the "ldap_to_gophish_mapping" dictionary:

Note: The keys are the GoPhish fields, and should always be the same, the values are the respective
LDAP attributes, and should match the attrs given in the "ldap" dictionary.

## Gophish configuration items in the "gophish" dictionary:

`gophish_server =` 'localhost'  
`gophish_port =` '3333'  
`gophish_api_key =` 'api_key'  

`group_name =` "gophish _group_name"  

Put the name of the group you want to create or modify.  
 
# GoLDAP Stages

1. Performing LDAP query.
2. Transform the LDAP result into a dictionary ready to upload to GoPhish.
3. Check if a group with the given name already exists.
4. Post (if new group) or Put (if existing group) the JSON to the API "Create Group".

# Usage

1. `pip install -r requirements.txt`
2. `Python goLDAP.py`  

> To make sure new users in active directory are always imported in a
> specific group, you can create a cron job if you using Linux or
> schedule task if using Windows. 

 
 Thanks to this reference :  
 `https://medium.com/@alpolishchuk/pagination-of-ldap-search-results-with-python-ldap-845de60b90d2`


