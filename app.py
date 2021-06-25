import traceback
import dbshorts
from flask import Flask, request, Response
import json
import mariadb
import secrets
import sys

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
    except:
        traceback.print_exc()
        print("Welp, something went wrong")
        return Response("Data Error, request invalid", mimetype="text/plain", status=400)

    newuser_id = dbshorts.run_insertion("insert into users (username, email, password, birthday, bio) values (?,?,?,?,?)", [username, user_email, user_pass, user_bday, user_bio])
    if(newuser_id == None):
        return Response("Database Error", mimetype="text/plain", status=500)
    else:
        newuser = [username, user_email, user_pass, user_bday, user_bio]
        newuser_json = json.dumps(newuser, default=str)
        print(f"{username} was successfully created!")
        return Response(newuser_json, mimetype="application/json", status=201)


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

    rows_inserted = None
    try:
        user = dbshorts.run_selection("select id from users u where u.username=? and u.password=?", [username, password])
        if(len(user) == 1):
            token = secrets.token_urlsafe(55)
            rows_inserted = dbshorts.run_insertion("insert into user_session (login_token, user_id) values (?,?)", [token, user[0][0]])
    except: 
        traceback.print_exc()
        print("Oh no, something went wrong")

    print(rows_inserted)
    if(rows_inserted != None):
        login_dictionary = { "login_token": token }
        login_json = json.dumps(login_dictionary, default=str)
        return Response(login_json, mimetype="application/json", status=201)
    else:
        return Response("Invalid Login, Please Try Again", mimetype="text/plain", status=400)


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