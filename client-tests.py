import requests
import json
from pandas import DataFrame
headers = ['id','username','last','first','status','years','company','role',]

url = "https://jmol-tutorial-garcias.c9users.io:8080/members"
url_chen3 = url + "/12"

admin_cred = { 'id': "08", 'password' : "u3n9DF" }
chen3_cred  = { 'id': "12", 'password' : "ABCD" }

def request_report(r):
    return "{} {} ({}: {}):".format(r.request.method, r.request.url, r.status_code, r.reason)

def view_members(base_url):
    r = requests.get(base_url)
    member_ids = r.json()['data']
    member_data = [
        requests.get("{}/{}".format(base_url,each)).json()['data']
        for each in member_ids
    ]
        
    df = DataFrame(member_data, columns=headers)
    print df.to_string()
    print

def view_member(member_url):
    r = requests.get(member_url)
    data = r.json()['data']
    print request_report(r)
    print "  data: {}".format(json.dumps(data))
    # df = DataFrame([data], columns=headers)
    # print df.to_string()
    print

def update_member(member_url, payload):
    r = requests.put(member_url, data=json.dumps(payload) )
    print request_report(r)
    print "  payload: {}".format(payload)
    body = r.json()
    print "  message: {}".format(json.dumps(body['messages']))
    print

def add_member(base_url, payload):
    r = requests.post(base_url, data=json.dumps(payload) )
    print request_report(r)
    print "  payload: {}".format(payload)
    body = r.json()
    print "  message: {}".format(json.dumps(body['messages']))
    if "data" in body:
        print "  data:    {}".format(json.dumps(body['data']))
        print
        return body['data']['id']
    else:
        print
        return None

def remove_member(member_url, payload):
    r = requests.delete(member_url, data=json.dumps(payload) )
    print request_report(r)
    print "  payload: {}".format(payload)
    body = r.json()
    print body
    print "  message: {}".format(json.dumps(body['messages']))
    print


##############################
#  TESTS
##############################

# Before running tests, make sure to seed database file 
# with at least one admin account

# Print list of members in database
view_members(url)

# Print JSON of profile for chen3
view_member(url_chen3)

# Try to change chen3's years of service 
payload = {'data' : {"years":"8"}}

# First without credentials
# Should fail
update_member(url_chen3, payload )

# Then with henderson1's credentials 
# Should fail
payload.update({'id':"35", 'password':"be7ab3K"})
update_member(url_chen3, payload )

# Now with chen3's credentials
payload.update(chen3_cred)
update_member(url_chen3, payload )

# Print JSON of profile for chen3
# "years" should now be 8
view_member(url_chen3)

# Create a new member and get their id with chen3's credentials
# Should fail with message "must be admin to add user"
payload.update(chen3_cred)
add_member(url, payload)

# Create a new member and get their id with ball's credentials
# Should indicate admin access
payload.update( { 'id':"08", 'password':"u3n9DF" } )
new_id = add_member(url, payload)
new_url = "{}/{}".format( url, new_id )

# Populate member's profile
payload['data'].update( {
    'password' : "111111",
    'first' : "Tabitha",
    'last' : "Jenkins",
    'username' : "jenkins1",
    'status' : "0",
    'years' : "0",
    'company' : "Tau Factor",
    'role' : "15",
})
update_member(new_url, payload)

# View the member's profile
view_member(new_url)

# Print list of members in database
# New member should have all fields populated
view_members(url)

# Delete the member with chen3's credentials
payload.update( chen3_cred )
remove_member( new_url, payload )

# Delete the member with user's credentials
payload.update( { 'id': new_id, 'password' : "111111" } )
remove_member(new_url, payload)

# Print list of members in database
# New user should not be in list
view_members(url)
