#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from base64 import b64encode
from uuid import uuid4 
from flask import Flask, jsonify, abort, make_response, request, url_for
from app_types import *
app = Flask(__name__)
app.config['DEBUG'] = True

grp_wines = {"red":{}, "pink":{}, "white":{}}
all_wines = {}
clients = {}
carts = {}

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

def check_vals(vals):
	if not all(x in request.form.keys() for x in vals):
		abort(400) # Bad request

# newClient() - POST
@app.route('/clients', methods=['POST'])
def newClient():
	# Check whether values are present in the request
	check_vals(["email", "pass", "address", "phone"])
	# Check whether client is not repeated
	new_client = Client(
		email=request.form["email"],
		password=request.form["pass"],
		address=request.form["address"],
		phone=request.form["phone"]
	)
	ID = new_client.put()
	# Make response "201 Created"
	return make_response(jsonify({"created":ID}), 201)

# getClients() - GET
@app.route("/clients", methods=["GET"])
def getClients():
	return jsonify({"all":clients.values()})

# deleteClient() - DELETE
@app.route("/clients/<ID_client>", methods=["DELETE"])
def deleteClient(ID_client):
	return jsonify(clients.pop(ID_client))

# updateClient() - PUT
@app.route("/clients/<ID_client>", methods=['PUT'])
def updateClient(ID_client):
	# Remove old email
	old = clients.pop(ID_client)
	# Rescue values from request and initialize carts to empty
	new_client = {
		"email":	request.form.get("email", old["email"]),
		"pass":		request.form.get("pass", old["pass"]),
		"address":	request.form.get("address", old["address"]),
		"phone":	request.form.get("phone", old["phone"]),
		"carts":	old['carts']
	}
	clients[new_client["email"]] = new_client
	return make_response(jsonify({"updated":new_client['email']}), 200)

# getClientDetails() - GET
@app.route("/clients/<ID_client>", methods=["GET"])
def getClientDetails(ID_client):
	# Check whether client already exists
	if not clients.has_key(ID_client):
		abort(400) # Bad request
	return jsonify(clients[ID_client])


# addWine() - POST
@app.route("/wines", methods=["POST"])
def addWine():
	form = request.form
	# Check whether values are present in the request
	check_vals(["name", "type"])
	# Generate universal ID (random)
	ID = str(uuid4())
	# Needed values
	new_wine = {
		'id': ID,
		'grade': form.get("grade", "12"),
		'size': form.get('size', "75"),
		'varietals': form.getlist('varietals'),
		'do': form.get("do", "0"),
		'price': form.get("price", ""),
		'name': form['name'],
		'photo': form.get("photo", "")
	}
	# Decide depending on the type of wine
	group = form['type']
	if group == "red":
		check_vals(["cask","bottle"])
		new_wine.update({
			"cask": form['cask'],
			"bottle": form["bottle"]
		})
		grp_wines["red"][ID] = new_wine
	elif group == "white":
		grp_wines["white"][ID] = new_wine
	elif group == "rose":
		grp_wines["rose"][ID] = new_wine
	else:
		abort(400) # Bad request
	all_wines[ID] = new_wine
	# Make response "201 Created"
	return make_response(jsonify({"created":ID}), 201)

# allWines() - GET
@app.route("/wines", methods=["GET"])
def allWines():
	return jsonify({"all":all_wines.values()})

# getWineProperties() - GET
@app.route("/wines/<ID_wine>", methods=["GET"])
def getWineProperties(ID_wine):
	if not all_wines.has_key(ID_wine):
		abort(404) # Not found
	return jsonify(all_wines[ID_wine])

# updateWine() - PUT
@app.route("/wines/<ID_wine>", methods=["PUT"])
def updateWine(ID_wine):
	form = request.form
	# Check whether wine is alredy inside 
	if not all_wines.has_key(ID_wine):
		abort(404) # Not found
	old = all_wines[ID_wine]
	# All regular values
	new = {
		'id': old['id'],
		'grade': form.get("grade", old["grade"]),
		'size': form.get('size', old["size"]),
		'varietals': form.getlist('varietals') or old['varietals'],
		'do': form.get("do", old["do"]),
		'price': form.get("price", old["price"]),
		'name': form.get('name', old['name']),
		'photo': form.get("photo", old["photo"])
	}
	# Red wine values
	if grp_wines['red'].has_key(ID_wine):
		for v in red_wine_vals:
			if request.form.has_key(v):
				wine[v] = request.form[v]
	return make_response(jsonify({"updated":ID_wine}), 200)

# deleteWines() - DELETE
@app.route("/wines", methods=["DELETE"])
def deleteWines():
	wines = all_wines.keys()
	all_wines.clear()
	for k,v in grp_wines.iteritems(): v.clear()
	return make_response(jsonify({"deleted":wines}), 200)

# deleteWine() - DELETE
@app.route("/wines/<ID_wine>", methods=["DELETE"])
def deleteWine(ID_wine):
	# Check whether the wine exists
	if not all_wines.has_key(ID_wine):
		abort(404) # Not found
	# Removing
	all_wines.pop(ID_wine)
	for k,v in grp_wines.iteritems():
		if v.has_key(ID_wine): 
			v.pop(ID_wine)
			break
	# Make response 200 "OK"
	return make_response(jsonify({"deleted":ID_wine}), 200)

# wineByType() - GET
@app.route("/types/<ID_type>", methods=["GET"])
def wineByType(ID_type):
	# Check whether the type exists
	if not grp_wines.has_key(ID_type):
		abort(404) # Not found

	results = grp_wines[ID_type]
	return jsonify({'all':results.values()})

# addCart() - POST
@app.route("/clients/<ID_client>/carts", methods=["POST"])
def addCart(ID_client):
	# Generate universal ID (random)
	ID = str(uuid4()) 
	new_cart = {
		"id":ID,
		"name": request.form.get("name", ""),
		"items":[]
	}
	# Update everything
	carts[ID] = new_cart
	clients[ID_client]['carts'].append(ID)
	# Make response "201 Created"
	return make_response(jsonify({"created":ID}), 201)

# deleteCart() - DELETE
@app.route("/clients/<ID_client>/carts/<ID_cart>", methods=["DELETE"])
def deleteCart(ID_client, ID_cart):
	# Check whether the cart and the client exist
	if not (clients.has_key(ID_client) and clients[ID_client]['carts'].count(ID_cart)):
		abort(404) # Not found
	# Remove itself, also from client
	carts.pop(ID_cart)
	clients[ID_client]['carts'].remove(ID_cart)
	# Make response "200 OK"
	return make_response(jsonify({"deleted":ID_cart}), 200)

# addItem() - POST
@app.route("/clients/<ID_client>/carts/<ID_cart>/items", methods=["POST"])
def addItem(ID_client, ID_cart):
	# Check whether the cart and the client exist
	if not (clients.has_key(ID_client) and clients[ID_client]['carts'].count(ID_cart)):
		abort(404) # Not found
	# Check if the value is present in the request and exists
	check_vals(['item'])
	item = request.form['item']
	if not all_wines.has_key(item):
		abort(404)
	carts[ID_cart]['items'].append(item)
	# Make response "201 Created"
	return make_response(jsonify(carts[ID_cart]), 201)


# getItems() - GET
@app.route("/clients/<ID_client>/carts/<ID_cart>/items", methods=["GET"])
def getItems(ID_client, ID_cart):
	# Check whether the cart and the client exist
	if not (clients.has_key(ID_client) and clients[ID_client]['carts'].count(ID_cart)):
		abort(404) # Not found
	# Make response "200 OK"
	return make_response(jsonify({"all":carts[ID_cart]['items']}), 200)
	

# delItem() - DELETE
@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", methods=["DELETE"])
def delItem(ID_client, ID_cart, ID_wine):
	# Check whether the cart and the client exist
	if not (clients.has_key(ID_client) and clients[ID_client]['carts'].count(ID_cart)
		and all_wines.has_key(ID_wine)):
		abort(404) # Not found
	carts[ID_cart]['items'].remove(ID_wine)
	# Make response "200 OK"
	return make_response(jsonify({"deleted":ID_wine}), 200)


# updateItem() - PUT
@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", methods=["PUT"])
def updateItem(ID_client, ID_cart, ID_wine):
	# Check whether the cart and the client exist
	if not (clients.has_key(ID_client) and clients[ID_client]['carts'].count(ID_cart)):
		abort(404) # Not found
	check_vals(["item"])
	if not all_wines.has_key(request.form['item']):
		abort(404)
	carts[ID_cart]['items'].remove(ID_wine)
	carts[ID_cart]['items'].append(request.form["item"])
	# Make response "200 OK"
	return make_response(jsonify({"updated":request.form["item"]}), 200)


if __name__ == "__main__":
	app.run()

