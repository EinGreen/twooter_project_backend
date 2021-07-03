import traceback
import dbshorts
from flask import Flask, request, Response
import json
import secrets
import sys

# ! May or may not be needed
import hashlib
import mariadb

app = Flask(__name__)

# *User api
# creating new user
@app.post("/api/newuser")
def create_user():
    try:
        username = request.json["username"]
        user_email = request.json["email"]
        user_pass = request.json["password"]
        user_bday = request.json["birthday"]
        user_bio = request.json["bio"]
        salt = dbshorts.create_salt()
    except:
        traceback.print_exc()
        print("Welp, something went wrong")
        return Response("Data Error, request invalid", mimetype="text/plain", status=400)

    hash_pass = dbshorts.create_hash_pass(salt, user_pass)
    newuser_id = dbshorts.run_insertion("insert into users (username, email, password, birthday, bio, salt) values (?,?,?,?,?,?)", [username, user_email, hash_pass, user_bday, user_bio, salt])
    if(newuser_id == None):
        return Response("Database Error", mimetype="text/plain", status=500)
    else:
        newuser = [username, user_email, user_pass, user_bday, user_bio]
        newuser_json = json.dumps(newuser, default=str)
        print(f"{username} was successfully created!")
        return Response(newuser_json, mimetype="application/json", status=201)

# Get logged in users
@app.get("/api/user")
def get_user():
    try:
        user_id = request.json["userId"]
    except IndexError:
        return Response("User not found", mimetype="text/plain", status=404)
    except:
        traceback.print_exc()
        print("I have no idea what happened, but something went wrong")
        return Response("Data Error", mimetype="text/plain", status=400)

    user_info = dbshorts.run_selection("select u.id, username, email, bio, birthday, image_url, banner_url from users u inner join user_session us on u.id = us.user_id where us.user_id=?", [user_id])
    if(user_info == None):
        return Response("User not logged in", mimetype="text/plain", status=500)
    elif(len(user_info) == 0):
        return Response("User does not exsist", mimetype="text/plain", status=404)
    else:
        logged_in_dictionary = {
            "userId": user_info[0][0], "username": user_info[0][1], "email": user_info[0][2], "bio": user_info[0][3], "birthdate": user_info[0][4], "imageUrl": user_info[0][5], "bannerUrl": user_info[0][6]}
        log_json = json.dumps(logged_in_dictionary, default=str)
        return Response(log_json, mimetype="application/json", status=201)

# Delete User
@app.delete("/api/user")
def delete_user():
    try:
        token = str(request.json['loginToken'])
        password = request.json['password']
    except:
        traceback.print_exc()
        print("You tried, but failed")

    username = dbshorts.run_selection("select u.username from users u inner join user_session us on u.id = us.user_id where us.login_token = ?", [token])
    hash_pass = dbshorts.get_hash_pass(username[0][0], password)
    user_info = dbshorts.run_selection("select u.id, u.username from users u inner join user_session us on u.id = us.user_id where us.login_token = ? and u.password = ?", [token, hash_pass,])
    if(user_info != None):
        rows = dbshorts.run_deletion("delete from users where id = ?", [user_info[0][0],])
        if(rows == 1):
            return Response(f"{user_info[0][1]} has been deleted", mimetype="text/plain", status=200)
        else:
            return Response("DB Error", mimetype="text/plain", status=500)
    else:
        return Response("Could not fine user", mimetype="text/plain", status=404)


# *Login api
# Login
@app.post("/api/login")
def login():
    try:
        username = request.json["username"]
        password = request.json["password"]
    except:
        traceback.print_exc()
        print("Welp, something went wrong")
        return Response("User Data Error", mimetype="text/plain", status=400)

    hash_pass = dbshorts.get_hash_pass(username, password)
    rows_inserted = None
    try:
        user = dbshorts.run_selection("select id from users u where u.username=? and u.password=?", [username, hash_pass])
        if(len(user) == 1):
            token = secrets.token_urlsafe(55)
            rows_inserted = dbshorts.run_insertion("insert into user_session (login_token, user_id) values (?,?)", [token, user[0][0]])
    except: 
        traceback.print_exc()
        print("Oh no, something went wrong")

    if(rows_inserted != None):
        login_dictionary = { "login_token": token }
        login_json = json.dumps(login_dictionary, default=str)
        return Response(login_json, mimetype="application/json", status=201)
    else:
        return Response("Invalid Login, Please Try Again", mimetype="text/plain", status=400)

# Logout
@app.delete("/api/logout")
def logout():
    try:
        login_token = str(request.json['loginToken'])
    except:
        traceback.print_exc()
        print("something went wrong, unknown error")

    rows = dbshorts.run_deletion("delete from user_session where login_token = ?", [login_token,])
    if(rows == 1):
        return Response("Logout Successful", mimetype="text/plain", status=200)
    else:
        return Response("DB Error", mimetype="text/plain", status=500)



if(len(sys.argv) > 1):
    mode = sys.argv[1]
else:
    print("No mode argument, please pass a mode argument when invoking the file")
    exit()

if(mode == "production"):
    import bjoern
    bjoern.run(app, "0.0.0.0", 5021)
elif(mode == "testing"):
    from flask_cors import CORS
    CORS(app)
    app.run(debug=True)
else:
    print("Invalid mode, please select either 'production' or 'testing'")
    exit()