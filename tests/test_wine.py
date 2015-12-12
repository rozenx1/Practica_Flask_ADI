#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import os, unittest, tempfile
from json import loads
from itertools import dropwhile
from hamcrest import assert_that, equal_to, contains, is_in
from wines import app

class TestCart(unittest.TestCase):

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

	wine_full = wine.copy()
	wine_full['type'] = "white"

	red_wine = {
		"type":"red",
		"name":"Señorío de Chical",
		"cask":"2",
		"bottle":"2",
	}

	bad_formed_wine = {
		"type":"red",
		"name":"Señorio de Chical"
		# Need cask and bottle since it's red
	}

	def setUp(self):
		self.tester = app.test_client(self)
		app.config['TESTING'] = True

	def tearDown(self):
		del self.tester

	# addWine() - POST
	def test_add_wine(self):
		# When
		post = self.tester.post("/wines", data=self.wine)
		# Then
		assert_that(post.status_code, equal_to(201))	# addWine() - POST

	# addWine() - POST - red_wine
	def test_add_red_wine(self):
		# When
		post = self.tester.post("/wines", data=self.red_wine)
		# Then
		assert_that(post.status_code, equal_to(201))

	# addWine() - POST - bad_formed_wine
	def test_add_bad_wine(self):
		# When
		post = self.tester.post("/wines", 
			data=self.bad_formed_wine)
		# Then
		assert_that(post.status_code, equal_to(400))

	# allWines() - GET
	def test_all_wines(self):
		# Given
		self.wine['name'] = "test_all_wines"
		# Then
		post = self.tester.post("/wines", 
			data=self.wine)
		get_all = self.tester.get("/wines")	
		data = loads(get_all.data)['all']
		for wine in data: wine.pop("id")
		copy = self.wine.copy()
		copy.pop('type')
		# When
		assert_that(get_all.status_code, 200)
		assert_that(copy, is_in(data))

	# getWineProperties() - GET
	def test_get_wine(self):
		# Given
		self.wine['name'] = "test_get_wine"
		# When
		# + POST
		post = self.tester.post("/wines", 
			data=self.wine)
		# + GET (ALL)
		get_all = self.tester.get("/wines")	
		data_all = loads(get_all.data)['all']
		my_wine = dropwhile(lambda x: x['name'] != "test_get_wine",
			data_all).next()
		# + GET
		get = self.tester.get("/wines/{id}".format(**my_wine))
		data = loads(get.data)
		data.pop("id")
		copy = self.wine.copy()
		copy.pop('type')
		# Then
		assert_that(get.status_code, 200)
		assert_that(data, equal_to(copy))

	# updateWine() - PUT
	def test_update_wine(self):
		# Given
		self.wine['name'] = "test_update_wine"
		# When
		# + POST
		post = self.tester.post("/wines", 
			data=self.wine)
		# + GET (ALL)
		get_all = self.tester.get("/wines")	
		data_all = loads(get_all.data)['all']
		my_wine = dropwhile(lambda x: x['name'] != "test_get_wine",
			data_all).next()
		# + UPDATE
		copy = self.wine.copy()
		copy['price'] = "12.0"
		update = self.tester.put("/wines/{id}".format(**my_wine),
			data=copy)
		data = loads(update.data)
		data.pop('id')
		# Then
		assert_that(update.status_code, equal_to(200))
		assert_that(data, equal_to(copy))
		
	# deleteWines() - DELETE
	def test_delete_wines(self):
		# When
		post = self.tester.post("/wines", 
			data=self.wine)
		delete = self.tester.delete("/wines")		
		get = self.tester.get("/wines")
		# Then
		assert_that(delete.status_code, equal_to(200))
		assert_that(loads(get.data)['all'], equal_to([]))

	# deleteWine() - DELETE
	def test_delete_wine(self):
		# Given
		self.wine['name'] = "test_delete_wine"
		# When
		post = self.tester.post("/wines", 
			data=self.wine)
		get_all = self.tester.get("/wines")	
		data_all = loads(get_all.data)['all']
		my_wine = dropwhile(lambda x: x['name'] != "test_delete_wine",
			data_all).next()
		delete = self.tester.delete("/wines/{id}".format(**my_wine))
		data = loads(delete.data)
		data.pop('id')
		copy = self.wine.copy()
		copy.pop('type')
		# Then
		assert_that(delete.status_code, equal_to(200))
		assert_that(data, equal_to(copy))

	# wineByType() - GET
	def test_wine_by_type(self):
		# Given
		self.wine['name'] = "test_delete_wine"
		# When
		post = self.tester.post("/wines", 
			data=self.wine)
		get_white = self.tester.get("/types/white")
		data = loads(get_white.data)['all']
		for white in data: white.pop('id')
		copy = self.wine.copy()
		copy.pop('type')
		# Then
		assert_that(get_white.status_code, equal_to(200))
		assert_that(copy, is_in(data))
		# assert_that(data, equal_to(copy))

