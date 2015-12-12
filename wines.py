#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from base64 import b64encode
from uuid import uuid4 
from flask import Flask, jsonify, abort, make_response, request, url_for
app = Flask(__name__)
app.config['DEBUG'] = True

grp_wines = {"red":{}, "pink":{}, "white":{}}
all_wines = {}
clients = {}
carts = {}

# Definitions of values (without lists such as "varietals")
vals_client = ["email", "pass", "address", "phone"]
min_wine_vals = ["name", "type"]
def_wine_vals = {'size':"75", 'do':"0", 'grade':"12"}
opt_wine_vals = ["price", "photo"]
red_wine_vals = ["cask", "bottle"]


def check_vals(vals):
	if not all(x in request.form.keys() for x in vals):
		abort(400) # Bad request

def check_exists(ID, collection):
	if any(request.form[ID]==y for y in collection.keys()):
		abort(400) # Bad request

# newClient() - POST
@app.route('/clients', methods=['POST'])
def newClient():
	# Check whether values are present in the request
	check_vals(vals_client)
	# Check whether client is not repeated
	check_exists(vals_client[0], clients)
	# Rescue values from request and initialize carts to empty
	new_client = {val:request.form[val] for val in vals_client}
	new_client['carts'] = []
	clients[request.form["email"]] = new_client
	# Make response "201 Created"
	return make_response(jsonify(new_client), 201)

# getClients() - GET
@app.route("/clients", methods=["GET"])
def getClients():
	return jsonify({"all":clients.values()})

# deleteClient() - DELETE
@app.route("/clients/<ID_mail>", methods=["DELETE"])
def deleteClient(ID_mail):
	return jsonify(clients.pop(ID_mail))

# updateClient() - PUT
@app.route("/clients/<ID_mail>", methods=['PUT'])
def updateClient(ID_mail):
	# Check whether values are present in the request
	check_vals(vals_client[:1])
	# Remove old email
	clients.pop(ID_mail)
	# Rescue values from request and initialize carts to empty
	new_mail = request.form['email']
	clients[new_mail] = {val:request.form[val] for val 
		in vals_client}
	clients[new_mail]['carts'] = []
	return jsonify(clients[new_mail])

# getClientDetails() - GET
@app.route("/clients/<ID_mail>", methods=["GET"])
def getClientDetails(ID_mail):
	# Check whether client already exists
	if not clients.has_key(ID_mail):
		abort(400) # Bad request
	return jsonify(clients[ID_mail])


# addWine() - POST
@app.route("/wines", methods=["POST"])
def addWine():
	form = request.form 
	# Check whether values are present in the request
	check_vals(min_wine_vals)
	# Generate universal ID (random)
	ID = str(uuid4())
	# Needed values
	new_wine = {
		'id':ID,
		'name':form['name'],
		'varietals':form.getlist('varietals')
	}
	# Default values
	for k,v in def_wine_vals.iteritems():
		new_wine[k] = form.get(k,v)
	# Optional values
	for v in opt_wine_vals:
		if form.has_key(v):
			new_wine[v] = form[v]
	# Decide depending on the type of wine
	group = form['type']
	if group == "red":
		check_vals(red_wine_vals)
		new_wine.update({val:form[val] for val 
			in red_wine_vals})
		grp_wines["red"][ID] = new_wine
	elif group == "white":
		grp_wines["white"][ID] = new_wine
	elif group == "rose":
		grp_wines["rose"][ID] = new_wine
	else:
		abort(400) # Bad request
	all_wines[ID] = new_wine
	# Make response "201 Created"
	return make_response(jsonify(new_wine), 201)

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
	# Check whether wine is alredy inside 
	if not all_wines.has_key(ID_wine):
		abort(404) # Not found
	wine = all_wines[ID_wine]
	# All regular values
	vals = def_wine_vals.keys() + min_wine_vals + opt_wine_vals
	for v in vals:
		if request.form.has_key(v):
			wine[v] = request.form[v]
	# Red wine values
	if grp_wines['red'].has_key(ID_wine):
		for v in red_wine_vals:
			if request.form.has_key(v):
				wine[v] = request.form[v]
	return jsonify(wine)

# deleteWines() - DELETE
@app.route("/wines", methods=["DELETE"])
def deleteWines():
	all_wines.clear()
	for k,v in grp_wines.iteritems(): v.clear()
	return jsonify({"all":[]})

# deleteWine() - DELETE
@app.route("/wines/<ID_wine>", methods=["DELETE"])
def deleteWine(ID_wine):
	if not all_wines.has_key(ID_wine):
		abort(404) # Not found

	wine = all_wines.pop(ID_wine)
	for k,v in grp_wines.iteritems():
		if v.has_key(ID_wine): 
			v.pop(ID_wine)
			break

	return jsonify(wine)

# wineByType() - GET
@app.route("/types/<ID_type>")
def wineByType(ID_type):
	if not grp_wines.has_key(ID_type):
		abort(404) # Not found

	results = grp_wines[ID_type]
	return jsonify({'all':results.values()})

# addCart() - POST
@app.route("/clients/<ID_mail>/carts", methods=["POST"])
def addCart(ID_mail):
	# Generate universal ID (random)
	ID = str(uuid4()) 
	new_cart = {
		"id":ID,
		"items":[]
	}
	# Name is optional so it may be in the request
	if request.form.has_key('name'):
		new_cart["name"] = request.form['name']
	# Update everything
	carts[ID] = new_cart
	clients[ID_mail]['carts'].append(ID)
	# Make response "201 Created"
	return make_response(jsonify(new_cart), 201)

# deleteCart() - DELETE
@app.route("/clients/<ID_mail>/carts/<ID_cart>", methods=["DELETE"])
def deleteCart(ID_mail, ID_cart):
	cart = carts.pop(ID_cart)
	clients[ID_mail]['carts'].remove(ID_cart)
	return jsonify(cart)

# addItem() - POST
@app.route("/clients/<ID_client>/carts/<ID_cart>/items", 
	methods=["POST"])
def addItem(ID_client, ID_cart):
	if not clients.has_key(ID_client):
		abort(404) # Not found
	client = clients[ID_client]
	if not client['carts'].count(ID_cart):
		abort(404) # Not found
	if not request.form.has_key('item'):
		abort(404) # Not found
	item = request.form['item']
	if not all_wines.has_key(item):
		abort(404)
	carts[ID_cart]['items'].append(item)
	return make_response(jsonify(carts[ID_cart]), 201)


# getItems() - GET
@app.route("/clients/<ID_client>/carts/<ID_cart>/items", 
	methods=["GET"])
def getItems(ID_client, ID_cart):
	# TODO
	pass

# delItem() - DELETE
@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", 
	methods=["DELETE"])
def delItem(ID_client, ID_cart, ID_wine):
	# TODO
	pass	

# updateItem() - PUT
@app.route("/clients/<ID_client>/carts/<ID_cart>/items/<ID_wine>", 
	methods=["PUT"])
def updateItem(ID_client, ID_cart, ID_wine):
	# TODO
	pass



if __name__ == "__main__":
	app.run()

