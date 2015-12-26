#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from flask import Flask, request, redirect, url_for, g, session, flash, render_template
import json
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'secret'
oauth = OAuth(app)

remote = oauth.remote_app(
    'remote',
    consumer_key="CLIENT_ID",
    consumer_secret="CLIENT_SECRET",
    request_token_params={'scope': 'email'},
    base_url='http://127.0.0.1:8001',
    request_token_url=None,
    access_token_url='http://127.0.0.1:8080/oauth/token',
    authorize_url='http://127.0.0.1:8080/oauth/authorize'
)


@app.route("/", methods=["GET"])
def index():
	wines = remote.request('/wines')
	return render_template('index.html', wines=wines.data['all'])

@app.route("/filterByType/<wine_type>", methods=["GET"])
def filterByType(wine_type):
	wines = remote.request('/types/{wine_type}'.format(**locals()))
	return render_template('index.html', wines=wines.data['all'])

@app.route('/filterByName/<wine_name>', methods=["GET"])
def filterByName(wine_name):
	pass

@app.route('/filterByPrices', methods=['POST'])
def filterByPrice():
	pass

if __name__ == "__main__":
	app.run(port=8002)