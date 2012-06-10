#-*- coding: utf-8 -*-



""" CONFIG OF THE APP TOKEN """
APP_KEY    = '2986120742'
APP_SECRET = '796b90d5a6e3a1cc4d719726f5f99f7d'


from flask import Flask, g, request, redirect, make_response
app = Flask(__name__)
app.debug = True
app.secret_key = "YOUR_SECRET_SESSION_KEY"

try:
    import json
except ImportError:
    import simplejson as json
from weibo import APIClient
CALLBACK_URL = "http://2.irestful.sinaapp.com/callback"


def get_api_client():
    return APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)

@app.route("/")
def index():
    client = get_api_client()
    try:
        if request.cookies['is_login'] != 'True':
            raise Exception("Haven't Login")
    except:
        auth_url = client.get_authorize_url()
        return "<a href=\"%s\">OAuth2</a>" % auth_url
    else:
        access_token = request.cookies.get('access_token')
        expires_in = request.cookies.get('expires_in')
        client.set_access_token(access_token, expires_in)
        # 判断有效期
        if client.is_expires() == True:
            raise Exception("Expires!")
        html = ''
        html = html + "<p>Welcome User %s         <a href=\"logout\">Logout</a></p>" % request.cookies.get('screen_name')
        timeline = client.get.statuses__user_timeline()
        for message in timeline.statuses:
            html += '<p>'+message['text']+'</p>'
        return html      

@app.route("/callback")
def callback():
    try:
        code   = request.args.get("code")
        client = get_api_client()
        r = client.request_access_token(code)
        client.set_access_token(r.access_token, r.expires_in)
        # get user info
        userid=client.get.account__get_uid()
        user=client.get.users__show(uid=userid.uid)
        
        resp = app.make_response(redirect('/'))
        resp.set_cookie('is_login', 'True')
        resp.set_cookie('screen_name', user["name"])
        resp.set_cookie('access_token', r.access_token)
        resp.set_cookie('expires_in', r.expires_in)
        return resp
    except Exception as e:
        return "*** OAuth2 Failed: %s" % str(e)

@app.route("/logout")
def logout():
    resp = app.make_response(redirect('/'))
    resp.set_cookie('is_login', 'False')
    resp.set_cookie('screen_name', '')
    resp.set_cookie('access_token', '')
    resp.set_cookie('expires_in', '')
    return resp
