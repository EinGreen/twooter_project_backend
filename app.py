import traceback
import dbshorts
from flask import Flask, request, Response
import json
import mariadb
import secrets
import sys

app = Flask(__name__)

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
        return Response("Data Error", mimetype="text/plain", status=400)

    newuser_id = dbshorts.run_insertion("insert into users (username, email, password, birthday, bio) values (?,?,?,?,?)", [username, user_email, user_pass, user_bday, user_bio])
    if(newuser_id == None):
        return Response("Database Error", mimetype="text/plain", status=500)
    else:
        newuser = [username, user_email, user_pass, user_bday, user_bio]
        newuser_json = json.dumps(newuser, default=str)
        print(f"{username} was successfully created!")
        return Response(newuser_json, mimetype="application/json", status=201)

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