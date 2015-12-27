#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from google.appengine.ext import ndb

class AppClient(ndb.Model):
	client_id = ndb.StringProperty()
	client_secret = ndb.StringProperty()
	client_type = ndb.StringProperty(default="public")
	default_redirect_uri = ndb.StringProperty(
		default="http://localhost:8002/oauthorized")
	user = ndb.KeyProperty(kind="Client")
	redirect_uris = ndb.StringProperty(repeated=True)
	default_scopes = ndb.StringProperty(repeated=True)


class GrantToken(ndb.Model):
	client = ndb.KeyProperty(kind="AppClient")
	user = ndb.KeyProperty(kind="Client")
	expires = ndb.DateTimeProperty()
	scopes = ndb.StringProperty(repeated=True)
	code = ndb.StringProperty()
	redirect_uri = ndb.StringProperty()

	def delete(self):
		self.key.delete()

class Token(ndb.Model):
	client = ndb.KeyProperty(kind="AppClient")
	user = ndb.KeyProperty(kind="Client")
	expires = ndb.DateTimeProperty()
	scopes = ndb.StringProperty(repeated=True)
	access_token = ndb.StringProperty()
	refresh_token = ndb.StringProperty()
	token_type = ndb.StringProperty()
	
	def delete(self):
		self.key.delete()