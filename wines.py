#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from base64 import b64encode
from flask import Flask, jsonify, abort, make_response, request, url_for
app = Flask(__name__)
app.config['DEBUG'] = True

