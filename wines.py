#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from flask import Flask, jsonify, abort, make_response, request, url_for
from google.appengine.ext import ndb
from app_types import *
from functools import wraps
from itertools import dropwhile

app = Flask(__name__)
app.config['DEBUG'] = True

#Create wine types
for t in ("red", "white", "pink"):
	new_type = WineType(id=t)
	new_type.put()

# AUXILIARY
# ------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not Found'}), 404)

def retrieve(ID, cls=None):
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
	'''It checks whether the cart corresponds with the client.'''
	@wraps(action)
	def dec(**kwargs):
		kwargs["key_client"] = retrieve(kwargs.pop("ID_client"))
		kwargs["key_cart"] = retrieve(kwargs.pop("ID_cart"))
		if not kwargs["key_cart"].parent() == kwargs["key_client"]: abort(404)
		return action(**kwargs)
	return dec

# ACTIONS
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
def getClients():
	clients = map(lambda c: c.json(), Client.query())
	return make_response(jsonify({"all":clients}), 200)

@app.route("/clients/<ID_client>", methods=["DELETE"])
def deleteClient(ID_client):
	retrieve(ID_client).delete()
	return make_response(jsonify({"deleted":ID_client}), 200)

@app.route("/clients/<ID_client>", methods=['PUT'])
def updateClient(ID_client):
	client = retrieve(ID_client).get()
	data = request.get_json()
	vals = ("address", "phone", "password")
	for k,v in data.iteritems():
		if k in vals: setattr(client, k, v)
	client.put()
	return make_response(jsonify({"updated":ID_client}), 200)

@app.route("/clients/<ID_client>", methods=["GET"])
def getClientDetails(ID_client):
	client = retrieve(ID_client).get()
	return make_response(jsonify({"client":client.json()}), 200)


@app.route("/wines", methods=["POST"])
@check_vals(["name", "type"])
def addWine():
	data = request.get_json()
	data["parent"] = retrieve(data.pop("type"), WineType)
	new_wine = Wine(**data)
	ID = new_wine.put()
	return make_response(jsonify({"created":ID.urlsafe()}), 201)

@app.route("/wines", methods=["GET"])
def allWines():
	wines = map(lambda w: w.json(), Wine.query())
	return make_response(jsonify({"all":wines}), 200)

@app.route("/wines/<ID_wine>", methods=["GET"])
def getWineProperties(ID_wine):
	wine = retrieve(ID_wine).get()
	return make_response(jsonify({"wine":wine.json()}), 200)

@app.route("/wines/<ID_wine>", methods=["PUT"])
def updateWine(ID_wine):
	data = request.get_json()
	wine = retrieve(ID_wine).get()
	vals = ("do", "grade", "size", "varietals", "price", "name", 
		"photo", "cask", "bottle")
	for k,v in data.iteritems():
		if k in vals: setattr(wine, k, v)
	wine.put()
	return make_response(jsonify({"updated":ID_wine}), 200)

@app.route("/wines", methods=["DELETE"])
def deleteWines():
	wines = Wine.query().fetch(keys_only=True)
	for w in wines: w.delete()
	return make_response(jsonify({"deleted":"all"}), 200)

@app.route("/wines/<ID_wine>", methods=["DELETE"])
def deleteWine(ID_wine):
	wine = retrieve(ID_wine)
	wine.delete()
	return make_response(jsonify({"deleted":ID_wine}), 200)

@app.route("/types/<ID_type>", methods=["GET"])
def wineByType(ID_type):
	wines = Wine.query(ancestor=retrieve(ID_type, WineType))
	wines = map(lambda w: w.json(), wines)
	return make_response(jsonify({'all':wines}), 200)

@app.route("/clients/<ID_client>/carts", methods=["POST"])
def addCart(ID_client):
	data = request.get_json()
	data["parent"] = retrieve(ID_client)
	new_cart = Cart(**data)
	ID = new_cart.put()	
	return make_response(jsonify({"created":ID.urlsafe()}), 201)

@app.route("/clients/<ID_client>/carts/<ID_cart>", methods=["DELETE"])
@check_cart
def deleteCart(key_client, key_cart):
	key_cart.delete()
	return make_response(jsonify({"deleted":key_cart.urlsafe()}), 200)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items", methods=["POST"])
@check_vals(["item"])
@check_cart
def addItem(key_client, key_cart):
	cart = key_cart.get()
	key_wine = retrieve(request.get_json()['item'])
	cart.items.append(key_wine)
	cart.put()
	return make_response(jsonify({"added":key_wine.urlsafe()}), 201)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items", methods=["GET"])
@check_cart
def getItems(key_client, key_cart):
	wines = map(lambda w: w.get().json(), key_cart.get().items)
	return make_response(jsonify({"all":wines}), 200)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", methods=["DELETE"])
@check_cart
def delItem(key_client, key_cart, ID_wine):
	cart = key_cart.get()
	key_wine = dropwhile(lambda k: k.urlsafe()!=ID_wine, cart.items).next()
	cart.items.remove(key_wine)
	cart.put()
	return make_response(jsonify({"removed":ID_wine}), 200)

@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", methods=["PUT"])
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
	app.run()

