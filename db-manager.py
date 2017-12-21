# from __future__ import unicode_literals
from bottle import get, post, put, delete, abort, request
import json

from bottle import run
from os import environ

file = 'members.db'
headers = ['id','username','last','first','password','status','years','company','role',]
header_dump_string = "{:<3} {:<12} {:12} {:12} {:10} {:<.4} {:.4} {:12} {:12}"
data_dump_string = "{id:<3} {username:<12} {last:12.12} {first:12.12} {password:10} {status:<4} {years:4} {company:12.12} {role:12.12}"
view_properties = [ x for x in headers if x!='password' ]


# Database access functions

def load(file):
    data = []
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            data.append( dict(zip(headers, line.split(","))) )
    return data

def save(data,file):
    with open(file, 'w') as f:
        for row in data:
            f.write( ",".join( [ str(row.get(key, "")) for key in headers ] ) )
            f.write( "\n" )

def seed(seedfile, dbfile):
    save(load(seedfile), dbfile)

def add(data):
    if data:
        ids = [ row['id'] for row in data ]
        new_id = str(int(sorted(ids)[-1]) + 1) # get highest id and generate one higher
    else:
        new_id = "0"
    data.append( {'id' : new_id } )
    return new_id

def index_by_id(data, user_id):
    ids = [ row['id'] for row in data ]
    try:
        return ids.index(str(user_id))
    except ValueError:
        return None

def remove(data, user_id):
    idx = index_by_id(data, user_id)
    if idx is not None:
        return data.pop(idx)

def alter(data, user_id, key, new_value):
    idx = index_by_id(data, user_id)
    if idx is not None:
        data[idx][key] = new_value
        return data[idx]

def lookup_by_id(data, user_id):
    idx = index_by_id(data, user_id)
    if idx is not None:
        return data[idx]
    else:
        return None

def dump(data):
    print header_dump_string.format(*headers)
    for line in data:
        print data_dump_string.format(**line)
    print

# Authentication functions

def authorize(credentials, member_id):
    authorized = { 
        'user' : False, 'self' : False, 'admin' : False, 'messages' : [] 
    }

    data_buffer = load(file)
    
    if ( 'id' not in credentials ) or ( 'password' not in credentials ):
        authorized['messages'].append( "missing id or password in credentials" )
        return authorized  # no need to check further
    
    user_profile = lookup_by_id( data_buffer, credentials['id'] )

    if user_profile is None:
        authorized['messages'].append( "user id not recognized" )
        return authorized  # no need to check further
    
    if user_profile['password'] != credentials['password']:
        authorized['messages'].append( "password did not match your profile")
        return authorized  # no need to check further

    # By now we know the requester is allowed to use service as "user" status
    authorized['user'] = True
    authorized['messages'].append("user access as {}".format(user_profile['username']))

    if user_profile['status'] == "1":
        authorized['admin'] = True
        authorized['messages'].append( "admin access" )

    # Does the requested member profile exist? Relationship with requestor?
    member_id = lookup_by_id( data_buffer, member_id )

    if member_id is None:
        authorized['messages'].append( "profile id not recognized")
        return authorized
        
    if user_profile['id'] == member_id['id']:
        authorized['self'] = True
        authorized['messages'].append( "self service" )

    return authorized

# Web interface functions
# For actions that modify database, expect that request will provide an object 
# containing user credentials and data specifying changes:
#     {
#         'id' : "2",               # member
#         'password' : "d9x83JD",   # member password
#         'data' : { 'years': "02" }
#     }

@post('/members')
def create_profile():
    data = json.loads(request.body.read())
    response = authorize(data, "")
    response.update({
        'action' : "create profile",
        'success' : False,
    })
    
    if response['admin']:
        data_buffer = load(file)
        new_id = add(data_buffer)
        save(data_buffer, file)
        response['success'] = True
        response['data'] = { 'id' : new_id }
    else:
        response['messages'].append("must be admin to add new member")

    return response

@put('/members/<member_id>')
def update_profile(member_id):
    data = json.loads(request.body.read())
    response = authorize(data, member_id)
    response.update({
        'action' : "update profile",
        'success' : False,
    })

    if response['admin'] or response['self']:
        data_buffer = load(file)
        for key, value in data['data'].items():
            alter(data_buffer, member_id, key, value)

        save(data_buffer, file)
        response['success'] = True
    
    elif response['user']:
        response['messages'].append("not your account")

    return response

@get('/members/<member_id>')
def view_profile(member_id):
    response = {
        'action' : "view profile",
        'success' : False,
        'data' : {},
    }

    data_buffer = load(file)
    profile = lookup_by_id(data_buffer, member_id)
    for key in view_properties:
        response['data'][key] = profile[key]

    response['success'] = True

    return response

@get('/members')
def list_profiles():
    response = {
        'action' : "list profiles",
        'success' : False,
        'data' : [],
    }

    data_buffer = load(file)
    for profile in data_buffer:
        response['data'].append( profile['id'] )
    
    response['success'] = True

    return response

@delete('/members/<member_id>')
def remove_profile(member_id):
    data = json.loads(request.body.read())
    response = authorize(data, member_id)
    response.update({
        'action' : "remove profile",
        'success' : False,
    })

    if response['admin'] or response['self']:
        data_buffer = load(file)
        remove(data_buffer, member_id)
        save(data_buffer, file)
        response['success'] = True

    return response

# Server-side testing (should be commented before deploying)

# seed('seed.txt',file)
# dump(load(file))        

if __name__ == '__main__':
    host = environ.get('IP')
    port = environ.get('PORT')
    run(host=host, port=port, debug=False, reloader=True)

