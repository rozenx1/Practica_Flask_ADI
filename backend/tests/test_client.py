#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import os, unittest, tempfile
from json import loads
from hamcrest import assert_that, equal_to, contains, is_in
from wines import app

class TestClient(unittest.TestCase):

	client = {
		"pass":"12345",
		"address":"Calle La Pamtomima",
		"phone":"633444555",
		'carts': []
	}

	def setUp(self):
		self.tester = app.test_client(self)
		app.config['TESTING'] = True

	def tearDown(self):
		del self.tester

	# newClient() - POST
	def test_new_client(self):
		# Given
		self.client['email'] = "test_new_clients@gmail.com"
		# When
		post = self.tester.post("/clients", data=self.client)
		# Then
		assert_that(post.status_code, equal_to(201))

	# getClients() - GET
	def test_get_clients(self):
		# Given
		self.client['email'] = "test_get_clients@gmail.com"
		# When
		self.tester.post("/clients", data=self.client)
		get = self.tester.get("/clients")
		# Then
		assert_that(get.status_code, equal_to(200))
		assert_that(self.client,
			 is_in(loads(get.data)['all']))

	# deleteClient() - DELETE
	def test_delete_client(self):
		# Given
		self.client['email'] = "test_delete_clients@gmail.com"
		# When
		self.tester.post("/clients", data=self.client)
		delete = self.tester.delete(
			"/clients/test_delete_clients@gmail.com")
		# Then
		assert_that(delete.status_code, equal_to(200))
		assert_that(loads(delete.data), 
			equal_to(self.client))

	# updateClient() - PUT
	def test_update_client(self):
		# Given
		self.client['email'] = "test_update_clients@gmail.com"
		# When
		self.tester.post("/clients", data=self.client)
		self.client['pass'] = "new pass"
		update = self.tester.put("/clients/test_update_clients@gmail.com",
			data=self.client)
		# Then
		assert_that(update.status_code, equal_to(200))

	# getClientDetails() - GET
	def test_get_client_details(self):
		# Given
		self.client['email'] = "test_get_client_details@gmail.com"
		# When
		self.tester.post("/clients", data=self.client)
		get = self.tester.get(
			"/clients/test_get_client_details@gmail.com")
		# Then
		assert_that(get.status_code, equal_to(200))
		assert_that(loads(get.data), 
			equal_to(self.client))

	# addCart() - POST
	def test_add_cart(self):
		# Given
		cart = {"name":"test_add_cart"}
		self.client['email'] = "test_add_cart@gmail.com"
		# When
		self.tester.post("/clients", data=self.client)
		post = self.tester.post("/clients/{email}/carts"
			.format(**self.client), data=cart)
		# Then 
		assert_that(post.status_code, equal_to(201))

	# deleteCart() - DELETE
	def test_delete_cart(self):
		# Given
		cart = {"name":"test_delete_cart"}
		self.client['email'] = "test_delete_cart@gmail.com"
		# When
		url = "/clients/{email}".format(**self.client)
		self.tester.post("/clients", data=self.client)
		post = self.tester.post(url+"/carts", data=cart)
		## We need to retrieve random id (a boring task)
		get_client = self.tester.get(url)
		ids = loads(get_client.data)['carts']
		delete = self.tester.delete(url+"/carts/"+ids[0])
		# Then		
		assert_that(delete.status_code, equal_to(200))