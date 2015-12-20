#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from google.appengine.ext import ndb

class Client(ndb.Model):
	# email = ndb.StringProperty() 
	password = ndb.StringProperty(required=True)
	address = ndb.StringProperty(required=True)
	phone = ndb.IntegerProperty(required=True)

	def json(self):
		return {
			"url":self.key.urlsafe(),
			"email":self.key.id(),
			"password":self.password,
			"address":self.address,
			"phone":self.phone
		}

class Wine(ndb.Model):
	grade = ndb.FloatProperty(default=12.0)
	size = ndb.IntegerProperty(default=75)
	varietals = ndb.StringProperty(repeated=True)
	do = ndb.BooleanProperty(default=False)
	price = ndb.FloatProperty()
	name = ndb.StringProperty(required=True)
	photo = ndb.BlobKeyProperty()
	cask = ndb.IntegerProperty()
	bottle = ndb.IntegerProperty()

	def json(self):
		return {
			"url":self.key.urlsafe(),
			"grade":self.grade,
			"size":self.size,
			"varietals":self.varietals,
			"do":self.do,
			"price":self.price,
			"name":self.name,
			"photo":self.photo,
			"cask":self.cask,
			"bottle":self.bottle
		}

class Cart(ndb.Model):
	name = ndb.StringProperty()
	items = ndb.KeyProperty(repeated=True, kind=Wine)

	def json(self):
		return {
			"name":self.name,
			"items":self.items
		}

class WineType(ndb.Model):
	pass

