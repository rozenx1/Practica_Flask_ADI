#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from google.appengine.ext import ndb

class Client(ndb.Model):
	email = ndb.KeyProperty(kind=str)
	password = ndb.StringProperty(required=True)
	address = ndb.StringProperty(required=True)
	phone = ndb.IntegerProperty(required=True)

class Cart(ndb.Model):
	name = ndb.StringProperty()
	wines = ndb.StringProperty(repeated=True)

class Wine(ndb.Model):
	grade = ndb.FloatProperty(default=12.0)
	size = ndb.IntegerProperty(default=75)
	varietals = ndb.StringProperty(repeated=True)
	do = BooleanProperty(default=False)
	price = FloatProperty()
	name = StringProperty(required=True)
	photo = BlobKeyProperty()
	cask = IntegerProperty()
	bottle = IntegerProperty()

class WineType(ndb.Model):
	kind = ndb.KeyProperty(kind=str)
