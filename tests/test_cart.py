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
	url_items = url_carts+"/items"

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


	# addItem() - POST
	def test_add_item(self):
		# Given
		cart = {'name':'test_add_item'}
		# When
		post_cart = self.tester.post(self.url_carts, data=cart)
		get = self.tester.get(self.url_client)
		cart_id = loads(get.data)['carts'][0]
		url_item = self.url_carts+"/"+cart_id+"/items"
		post_item = self.tester.post(url_item, data=self.item)
		# Then
		assert_that(post_item.status_code, equal_to(201))
		