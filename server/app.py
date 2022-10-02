from flask import Flask, render_template, send_file, request, redirect, url_for, make_response
from oauthlib.oauth2 import WebApplicationClient
import os
import requests
import json
from peewee import *
import qrcode
dbmanager = SqliteDatabase('data.db')
dbmanager.connect()
if (dbmanager.is_closed() == False):
    dbmanager.close()
class BaseModel(Model):
    class Meta:
        database = dbmanager

class Users(BaseModel):
    id = TextField(null=False)
    username = TextField(null=False, default=" ")
    email = TextField(null=False, unique=True)
    point = TextField(null=False, default="0")

class Detect(BaseModel):
    bin_id = IntegerField(null=False)

dbmanager.drop_tables([Users])
dbmanager.create_tables([Users])

app = Flask("point")
GOOGLE_CLIENT_ID = "420123632397-rvsdilapasadjd6imk7sfkp2stc8tdmk.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def filetxt(f):
    f = open(f"{f}", "r")
    return f.read()

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def logged_in():
    cookie = request.cookies.get('logged_in')
    if(cookie == None or cookie == False):
        return False
    user_id = request.cookies.get('log_in_time_encrypted')
    if user_id != None:
        user = Users.select().where(Users.id == user_id)
        if(user.exists() == False):
            return False
        return True
    else:
        return False

@app.route('/qr/<uid>', methods=['GET', 'POST'])
def qr(uid):
    try:
        return send_file(f'{uid}.png')
    except Exception:
        qr = qrcode.make(uid)
        qr.save(f'{uid}.png')
    return send_file(f'{uid}.png')

# @app.route('/index.css', methods=['GET', 'POST'])
# def css(uid):
#     return send_file(f'index.css')

@app.route('/bin/<bin>', methods=['GET', 'POST'])
def bin(bin):
    Detect.create(bin_id = int(bin))
    return "success"

@app.route('/clear/', methods=['GET', 'POST'])
def delete_all():
    dbmanager.drop_tables([Users, Detect])
    dbmanager.create_tables([Users, Detect])

@app.route('/add/<uid>/<bin>', methods=['GET', 'POST'])
def add(uid, bin):
    bin = int(bin)
    bins = Detect.select().where(Detect.bin_id == bin)
    temp = 0
    for i in bins:
        temp += 1
    for i in bins:
        i.delete_instance()
    uid = str(uid)
    point = 5*temp
    user = Users.select().where(Users.id == uid).get()
    user.point = str(int(user.point) + point)
    dbmanager.execute_sql(f'UPDATE users SET point="{user.point}" WHERE id= "{user.id}"')
    return "success"

@app.route("/")
def index():
    if(not logged_in()):
        return redirect(url_for("login"))
    user_id = request.cookies.get('log_in_time_encrypted')
    user_id = str(user_id)
    user = Users.select().where(Users.id == user_id).get()
    S = filetxt('index.html')
    data = user.__dict__['__data__']
    for i in data:
        S = S.replace(f"<{i}>", str(data[i]))
    return S

# @app.route('/<path>/<path:url>', methods=['GET', 'POST'])
# def catch_all(path, url):
#     temp = url.split("/")
#     if("." not in temp[-1]):
#         url += ".html"
#     if(url.endswith(".html")):
#         if (not logged_in()):
#             return login()
#     return file(f"public/{path}/{url}")

# @app.route('/<url>', methods=['GET', 'POST'])
# def other_html(url):
#     if(not logged_in()):
#         return login()
#     if(url == "requirementx.txt"):
#         return "File not found"
#     if("." not in url):
#         url += ".html"
#     return file(f"public/{url}")

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri="https://cookiespeanutbutter.herokuapp.com/callback",
        scope=["email"],
    )
    return redirect(request_uri)

@app.route("/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        user = Users.select().where(Users.id == users_email)
        unique_id = str(unique_id)
        if(user.exists() == False):
            Users.create(id=unique_id, email=users_email)
        else:
            dbmanager.execute_sql(f'UPDATE users SET id="{unique_id}" WHERE email= "{users_email}"')
        resp = make_response(redirect(url_for("index")))
        resp.set_cookie('log_in_time_encrypted', unique_id)
        resp.set_cookie('logged_in', "True")
        return resp
    else:
        return "Oh no too bad"

app.secret_key = os.urandom(24)
if __name__ == "__main__":
    app.run(ssl_context="adhoc", port="51603")