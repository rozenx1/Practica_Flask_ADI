#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from flask import session, request, url_for, render_template, redirect
from flask import Flask, jsonify, abort, make_response
from flask_oauthlib.provider import OAuth2Provider
from flask_httpauth import HTTPBasicAuth
from datetime import datetime, timedelta
from werkzeug.security import gen_salt
from google.appengine.ext import ndb, blobstore
from google.appengine.api import memcache
from base64 import b64encode
from itertools import dropwhile
from functools import wraps
from uuid import uuid4
from json import loads
from re import search
from app_types import *
from oauth_aux import *

app = Flask(__name__)
app.secret_key = str(uuid4())
app.config['DEBUG'] = True

# AUXILIARY
# ------------------------------------------------------------------------
for t in ("red", "white", "pink"):
	new_type = WineType(id=t)
	new_type.put()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not Found'}), 404)

def retrieve(ID, cls=None):
	'''Retrieve datastore key using urlsafe or id and class.'''
	try:
		if cls:
			key = ndb.Key(cls, ID)
		else:
			key = ndb.Key(urlsafe=ID)
	except:
		abort(404)
	return key

def check_vals(vals):
	'''It checks whether the values are present in the request.'''
	def inner(action):
		@wraps(action)
		def dec(**kwargs):
			keys = request.get_json().keys()
			if not all(x in keys for x in vals): abort(400)
			return action(**kwargs)
		return dec
	return inner

def check_cart(action):
	'''It checks whether the cart corresponds to the client.'''
	@wraps(action)
	def dec(**kwargs):
		kwargs["key_client"] = retrieve(kwargs.pop("ID_client"))
		kwargs["key_cart"] = retrieve(kwargs.pop("ID_cart"))
		if not kwargs["key_cart"].parent() == kwargs["key_client"]: abort(404)
		return action(**kwargs)
	return dec

def get_blob(request, field):
	'''Get the Blobstore key for uploaded file.'''
	content = request.files[field]
	strkey = search(r'blob-key="([^\']*?)"', str(content)).group(1)
	return blobstore.get(strkey)

# OAUTH
#-------------------------------------------------------------------------
oauth = OAuth2Provider(app)
url_redirect = "http://localhost:8002/oauthorized"

@app.route('/', methods=('GET', 'POST'))
def home():
	'''Endpoint in order to check your previously registered email.'''
    if request.method == 'POST':
        client = retrieve(request.form.get('email'), Client)
        session['client'] = client.urlsafe()
        return redirect('/app_client')
    client = session.get("client", None)
    return render_template('home.html', client=None)

@app.route('/app_client', methods=['GET'])
def client():
	'''Endpoint in order to generate app client (id and secret) for oauth.'''
    client_url = session.get("client")
    if not client_url: return redirect('/')
    app_client = AppClient(
        client_id=gen_salt(40),
        client_secret=gen_salt(50),
        redirect_uris=[url_redirect],     
        default_scopes=['email'],
        parent=retrieve(client_url)
    )
    app_client.put()
    return jsonify(
        client_id=app_client.client_id,
        client_secret=app_client.client_secret,
    )

@oauth.clientgetter
def load_client(client_id):
	return AppClient.query(AppClient.client_id == client_id).get()

@oauth.grantgetter
def load_grant(client_id, code):
	app_client = AppClient.query(AppClient.client_id == client_id).fetch()[0].key
	return GrantToken.query(GrantToken.code == code,
		ancestor=app_client.parent()).fetch()[0]

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
	expires = datetime.utcnow() + timedelta(seconds=360)
	app_client = AppClient.query(AppClient.client_id == client_id).fetch()[0]
	grant = GrantToken(
		client=app_client.key,
		parent=app_client.key.parent(),
		user=app_client.key.parent(),
		code=code['code'],
		redirect_uri=request.redirect_uri,
		scopes=request.scopes,
		expires=expires
	)
	grant.put()
	return grant

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
	if access_token:
		return Token.query(Token.access_token == access_token).get()
	else:
		return Token.query(Token.refresh_token == refresh_token).get()

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
	toks = Token.query(Token.client == request.client.key, 
		ancestor=request.user).fetch()
	for t in toks: t.delete()

	expires_in = token.pop('expires_in')
	expires = datetime.utcnow() + timedelta(seconds=expires_in)
	app_client = AppClient.query(AppClient.client_id == request.client.client_id).fetch()[0]
	tok = Token(
		access_token=token['access_token'],
		refresh_token=token['refresh_token'],
		token_type=token['token_type'],
		scopes=[token['scope']],
		expires=expires,
		client=app_client.key,
		parent=app_client.key.parent(),
		user=app_client.key.parent()
	)
	tok.put()
	return tok

@app.route('/oauth/authorize', methods=('GET', 'POST'))
@oauth.authorize_handler
def authorize(*args, **kwargs):
	if request.method == 'GET':
        client_id = kwargs.get('client_id')
        app_client = AppClient.query(AppClient.client_id == client_id).fetch()[0]
        kwargs['app_client'] = app_client
        client = app_client.key.parent().get()
        kwargs['client'] = client
        print kwargs['client']
        return render_template('authorize.html', **kwargs)

	confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@app.route('/oauth/token', methods=('GET', 'POST'))
@oauth.token_handler
def access_token():
    return None

@app.route('/me', methods=["POST"])
@oauth.require_oauth()
def me():
	'''Gives you your client (urlsafe) from app client id.'''
	client_id = request.get_json()['client_id']
	app_client = AppClient.query(AppClient.client_id == client_id).fetch()[0]
	client = app_client.key.parent()
	return make_response(jsonify({"me":client.urlsafe()}), 200)

# HTTPBASICAUTH
# ------------------------------------------------------------------------
auth = HTTPBasicAuth()

# -H "Authorization:Basic cm9vdDphZG1pbg=="
users = {
	"root":"admin"
}

@auth.get_password
def get_pw(username):
	if username in users:
		return users[username]
	return None

def get_auth(username):
	'''Gives you the basic authorization code (base64) for a user'''
	if not users.has_key(username): return
	return b64encode("{0}:{1}".format(username, users[username]))

@app.route('/submit_wine', methods=("POST", "GET"))
def submit_wine():
	'''Render the submit wine form and the auth form when GET, 
	gives you auth code and upload url when POST.'''
	if request.method == "POST":
		data = request.get_json()
		user = data['user']
		pw = data['pw']
		if users.has_key(user) and users[user] == pw:
			auth_basic = get_auth(user)
			upload_url = blobstore.create_upload_url('/wines')
			return jsonify({"auth_basic":auth_basic, 
				"upload_url":upload_url})
		else:
			return make_response(jsonify(
				{"error":"authorization failed"}), 401)

	return render_template('submit_wine.html') 


# RESOURCES
# ------------------------------------------------------------------------
@app.route('/clients', methods=['POST'])
@check_vals(["email", "password", "address", "phone"])
def newClient():
	data = request.get_json()
	data["id"] = data.pop("email")
	new_client = Client(**data)
	ID = new_client.put()
	return make_response(jsonify({"created":ID.urlsafe()}), 201)

@app.route("/clients", methods=["GET"])
@oauth.require_oauth()
def getClients():
	clients = map(lambda c: c.json(), Client.query())
	return make_response(jsonify({"all":clients}), 200)

@app.route("/clients/<ID_client>", methods=["DELETE"])
@oauth.require_oauth()
def deleteClient(ID_client):
	retrieve(ID_client).delete()
	return make_response(jsonify({"deleted":ID_client}), 200)

@app.route("/clients/<ID_client>", methods=['PUT'])
@oauth.require_oauth()
def updateClient(ID_client):
	client = retrieve(ID_client).get()
	data = request.get_json()
	vals = ("address", "phone", "password")
	for k,v in data.iteritems():
		if k in vals: setattr(client, k, v)
	client.put()
	return make_response(jsonify({"updated":ID_client}), 200)

@app.route("/clients/<ID_client>", methods=["GET"])
@oauth.require_oauth()
def getClientDetails(ID_client):
	client = retrieve(ID_client).get()
	return make_response(jsonify({"client":client.json()}), 200)

@app.route("/wines", methods=["POST"])
@auth.login_required
def addWine():
	data = loads(request.form['data'])
	data['photo'] = get_blob(request, 'photo').key()
	data["parent"] = retrieve(data.pop("type"), WineType)
	new_wine = Wine(**data)
	ID = new_wine.put()
	memcache.add(key=ID.urlsafe(), value=new_wine, time=900)
	return make_response(jsonify({"created":ID.urlsafe()}), 201)

@app.route("/wines", methods=["GET"])
def allWines():
	wines = map(lambda w: w.json(), Wine.query())
	return make_response(jsonify({"all":wines}), 200)

@app.route("/wines/<ID_wine>", methods=["GET"])
def getWineProperties(ID_wine):
	wine = memcache.get(ID_wine)
	if not wine:
		wine = retrieve(ID_wine).get()
		memcache.add(key=ID_wine, value=wine, time=900)
	return make_response(jsonify({"wine":wine.json()}), 200)

@app.route("/wines/<ID_wine>", methods=["PUT"])
def updateWine(ID_wine):
	data = request.get_json()
	wine = memcache.get(ID_wine)
	if wine:
		memcache.delete(ID_wine)
	else:
		wine = retrieve(ID_wine).get()
	vals = ("do", "grade", "size", "varietals", "price", "name", 
		"photo", "cask", "bottle")
	for k,v in data.iteritems():
		if k in vals: setattr(wine, k, v)
	wine.put()
	memcache.add(key=ID_wine, value=wine, time=900)
	return make_response(jsonify({"updated":ID_wine}), 200)

@app.route("/wines", methods=["DELETE"])
def deleteWines():
	wines = Wine.query().fetch(keys_only=True)
	for w in wines: w.delete()
	memcache.flush_all()
	return make_response(jsonify({"deleted":"all"}), 200)

@app.route("/wines/<ID_wine>", methods=["DELETE"])
def deleteWine(ID_wine):
	wine = memcache.get(ID_wine)
	if wine:
		memcache.delete(ID_wine)
	else:
		wine = retrieve(ID_wine)
	wine.delete()
	return make_response(jsonify({"deleted":ID_wine}), 200)

@app.route("/types/<ID_type>", methods=["GET"])
def wineByType(ID_type):
	wines = Wine.query(ancestor=retrieve(ID_type, WineType))
	wines = map(lambda w: w.json(), wines)
	return make_response(jsonify({'all':wines}), 200)

@app.route("/clients/<ID_client>/carts", methods=["POST"])
@oauth.require_oauth()
def addCart(ID_client):
	data = request.get_json()
	data["parent"] = retrieve(ID_client)
	data['items'] = map(lambda i: retrieve(i), data['items'])
	new_cart = Cart(**data)
	ID = new_cart.put()	
	return make_response(jsonify({"created":ID.urlsafe()}), 201)

@app.route("/clients/<ID_client>/carts/<ID_cart>", methods=["DELETE"])
@oauth.require_oauth()
@check_cart
def deleteCart(key_client, key_cart):
	key_cart.delete()
	return make_response(jsonify({"deleted":key_cart.urlsafe()}), 200)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items", methods=["POST"])
@oauth.require_oauth()
@check_vals(["item"])
@check_cart
def addItem(key_client, key_cart):
	cart = key_cart.get()
	key_wine = retrieve(request.get_json()['item'])
	cart.items.append(key_wine)
	cart.put()
	return make_response(jsonify({"added":key_wine.urlsafe()}), 201)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items", methods=["GET"])
@oauth.require_oauth()
@check_cart
def getItems(key_client, key_cart):
	wines = map(lambda w: w.get().json(), key_cart.get().items)
	return make_response(jsonify({"all":wines}), 200)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", methods=["DELETE"])
@oauth.require_oauth()
@check_cart
def delItem(key_client, key_cart, ID_wine):
	cart = key_cart.get()
	key_wine = dropwhile(lambda k: k.urlsafe()!=ID_wine, cart.items).next()
	cart.items.remove(key_wine)
	cart.put()
	return make_response(jsonify({"removed":ID_wine}), 200)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", methods=["PUT"])
@oauth.require_oauth()
@check_vals(["item"])
@check_cart
def updateItem(key_client, key_cart, ID_wine):
	cart = key_cart.get()
	key_wine = dropwhile(lambda k: k.urlsafe()!=ID_wine, cart.items).next()
	cart.items.remove(key_wine)
	item = retrieve(request.get_json()['item'])
	cart.items.append(item)
	cart.put()
	return make_response(jsonify({"updated":item.urlsafe()}), 200)


if __name__ == "__main__":
	app.run(port=8001)

