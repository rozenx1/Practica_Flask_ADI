#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from flask import Flask, request, jsonify, redirect, url_for, g, session, flash, render_template
from flask_oauthlib.client import OAuth
from json import dumps
from uuid import uuid4

app = Flask(__name__)
app.secret_key = str(uuid4())
app.config['DEBUG'] = True

# OAUTH
#-------------------------------------------------------------------------
client_id = "zyBHAsqORoZkkBj9ZOEF4NdyyxTkjwHbmaaHUVDY"
client_secret = "aQeqI1atg7w0vW6DZFw14O49yk5wghx7YU7BPNt3cLTOx2812n"

oauth = OAuth(app)
remote = oauth.remote_app(
    'remote',
    consumer_key=client_id,
    consumer_secret=client_secret,
    request_token_params={'scope': 'email'},
    base_url='http://localhost:8080',
    request_token_url=None,
    access_token_url='http://localhost:8080/oauth/token',
    authorize_url='http://localhost:8080/oauth/authorize'
)

@app.route('/login')
def login():
    next_url = request.args.get('next') or request.referrer or None
    url = url_for('oauthorized', _external=True).replace("127.0.0.1", "localhost")
    resp = remote.authorize(
        callback=url
    )
    return resp

@app.route('/logout')
def logout():
    session.pop('remote_oauth', None)
    return redirect("/")

@remote.tokengetter
def get_remote_token(token=None):
    if 'remote_oauth' in session:
        return session.get('remote_oauth')

@app.before_request
def before_request():
    g.user = None
    if 'remote_oauth' in session:
        g.user = session['remote_oauth']

# Callback
@app.route('/oauthorized')
def oauthorized():
    resp = remote.authorized_response()
    if resp is None:
        flash('No tienes autorizacion.')
    else:
        session['remote_oauth'] = resp
    return redirect('/')

# AUX
#-------------------------------------------------------------------------
def who_am_i():
    return remote.post('/me', data=dumps({"client_id":client_id}),
        content_type="application/json").data['me']

# ACTIONS
#-------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/allWines")
def allWines():
    wines = remote.get("/wines")
    return jsonify(wines.data)

@app.route("/filterByType/<wine_type>")
def filterByType(wine_type):
    wines = remote.get("/types/{wine_type}".format(**locals()))
    return jsonify(wines.data)

@app.route('/filterByName/<wine_name>')
def filterByName(wine_name):
    url = '/filterByName/{wine_name}'.format(**locals())
    wines = remote.get(url)
    return jsonify(wines.data)

@app.route('/filterByPrices', methods=['POST'])
def filterByPrices():
    params = request.get_json()
    wines = remote.post('/filterByPrices', data=dumps(params), 
        content_type="application/json")
    return jsonify(wines.data)

@app.route('/getCarts')
def carts():
    params = request.get_json()
    me = who_am_i()
    print me
    url = "/clients/{me}/carts".format(**locals())
    get = remote.get(url)
    print get.data
    return jsonify(get.data)

@app.route('/postCart', methods=["POST"])
def postCart():
    data = request.get_json()
    me = who_am_i()
    url = "/clients/{me}/carts".format(**locals())
    post = remote.post(url, data=dumps(data), 
        content_type="application/json")
    return jsonify(post.data)

if __name__ == "__main__":
    import os
    os.environ['DEBUG'] = 'true'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
	app.run(port=8002, host="localhost")