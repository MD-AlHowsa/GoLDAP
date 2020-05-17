# GoLDAP

GoLDAP is a **Gophish** addon that retrieves users from your **active directory** via **LDAP** protocol and then import them into a predefined group in your Gophish . By defualt LDAP will not return more than 1000 entries as a result for your query. However, GoLDAP uses LDAP paging to retrieve as many users as your container has. If you have ideas to improve the script, do not hesitate to contact me on:
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




`ldap_server =` 'ldap://ldap_server_IP'

If your LDAP port is not the defualt one "389", spesicy the port after the IP addreess as follows:  ldap://ip_address:port

Active directory credential.
`us =`  'username'.
`pw =` 'password'.


`base_dn =`  'Location of the container'.

>  The Base DN setting specifies the root for searches in the Active
> Directory, e.g, if your domain name is "example.local". Convert it
> into  "dc=ISL,dc=local". Assuming your  targeted users are in the
> default location, the OU named "Users", it will be converted  to
> "ou=users". the final search for users will be
> "ou=users,dc=ISL,dc=local". To find the right container consult you
> system admin. Read more about "[LDAP data Interchange
> Format](http://en.wikipedia.org/wiki/LDAP_Data_Interchange_Format)"

`col_names =` 'Email, First Name, Last Name,position'  

 Unfortunately, we cannot control the order of the columns in LDAP, SO, based on my testing it usually comes in this order, change the order if yous is different.

Gophish Configuration.
`gophish_server =` 'localhost'.
`gophish_port =` '3333'.
`gophish_api_key =` 'api_key'.

`group_name =` "gophish _group_name".

Put the name of the group you want to create or  modify. 
 
> Very Important: if you want to modify a group and you specified its ID
> in the variable below, you have to put its name above as well,
> otherwise, it will modify the name of the group. Basically, the only 
> identifier for a group is its ID not its name.

`update_group = 0`  

If you want to modify an existing group, put its ID int this variable as integer, otherwise put 0 to create a new group with the name specified in the "group_name" variable.

> To get your current groups ID, request this endpoint in your browser.

    https://gophish_ip:3333/api/groups/summary?api_key=your_api_key


# GoLDAP Stages

1. Performing LDAP query.
2. Reformatting the result of the query since it comes as a list of sub-lists. The second sub-list of every list  contains a dictionary that stores every value in a list of single value. I took sometime to realize that :D.
3.  Write users and their attributes in CSV format and export it as a CSV file.
4. Rename the colomns names in the CSV file to match Gophish naming, e.g "Givenname" will be "First Name".
5. Post the CSV file to the Gophish API "Import Group" to get them in JSON format 
6. Post (if new group) or Put (if existing group) the JSON got from the API "Import Group" to the API "Create Group".
7. or mod

# Usage

`Python goLDAP.py`

> To make sure new users in active directory are always imported in a
> specific group, you can create a cron job if you using Linux or
> schedule task if using Windows. 


 


