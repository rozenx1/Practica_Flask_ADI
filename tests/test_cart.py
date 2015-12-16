#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import os, unittest, tempfile
from json import loads
from itertools import dropwhile
from hamcrest import assert_that, equal_to, contains, is_in
from wines import app

class TestCart(unittest.TestCase):

	client = {
		"email":"test_cart@gmail.com",
		"pass":"12345",
		"address":"Calle La Pamtomima",
		"phone":"633444555"
	}

	wine = {
		"type":"white",
		"grade":"15.0",
		"size":"80",
		"varietals":["tempranillo"],
		"do":'1',
		"price":"6.5",
		"name":"Señorío de Chical",
		"photo":"photos/01234.png"
	}

	url_client = "/clients/{email}".format(**client)
	url_carts = url_client+"/carts"

	def setUp(self):
		self.tester = app.test_client(self)
		self.tester.post("/clients", data=self.client)
		self.tester.post("/wines", data=self.wine)
		get_wines = self.tester.get("/wines")
		data = loads(get_wines.data)['all']
		self.item = {'item':data[0]['id']}
		app.config['TESTING'] = True


	def tearDown(self):
		self.tester.delete(
			"/clients/{email}".format(**self.client))
		del self.tester

	def post(self):
		cart = {'name':'test_add_item'}
		post_cart = self.tester.post(self.url_carts, data=cart)
		get = self.tester.get(self.url_client)
		cart_id = loads(get.data)['carts'][0]
		self.url_item = self.url_carts+"/"+cart_id+"/items"
		return self.tester.post(self.url_item, data=self.item)
		
	# addItem() - POST
	def test_add_item(self):
		# When
		post = self.post()
		# Then
		assert_that(post.status_code, equal_to(201))

	# getItems() - GET
	def test_get_items(self):
		# When
		self.post()
		get_all = self.tester.get(self.url_item)
		# Then
		assert_that(get_all.status_code, equal_to(200))


	# delItem() - DELETE
	def test_delete_item(self):
		# When
		self.post()
		delete = self.tester.delete(self.url_item+"/"+self.item['item'])
		# Then
		assert_that(delete.status_code, equal_to(200))

	# updateItem() - PUT
	def test_update_item(self):
		# When
		self.post()
		update = self.tester.put(self.url_item+"/"+self.item['item'], 
			data={"item":"madeup"}) 
		# Then
		assert_that(update.status_code, equal_to(404))

		