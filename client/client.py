#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

from flask import Flask, request, redirect, url_for, g, session, flash, render_template
from flask_oauthlib.client import OAuth
import json, requests

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'secret'

# OAUTH
#-------------------------------------------------------------------------
oauth = OAuth(app)
remote = oauth.remote_app(
    'remote',
    consumer_key="BVR357AwLPWqcgrK3sxIm0K0dFU5XpGAMZ3i4CyR",
    consumer_secret="Oe0Vo0fxOKGAikEkpxjFEehBVCkxHKl5y853OmEFU3A3bkmuZF",
    request_token_params={'scope': 'email'},
    base_url='http://localhost:8080',
    request_token_url=None,
    access_token_url='http://localhost:8080/oauth/token',
    authorize_url='http://localhost:8080/oauth/authorize'
)

@app.route('/login')
def login():
    next_url = request.args.get('next') or request.referrer or None
    url = url_for('oauthorized', _external=True).replace("127.0.0.1", "localhost")
    resp = remote.authorize(
        callback=url
    )
    return resp

@app.route('/logout')
def logout():
    session.pop('remote_oauth', None)
    return redirect("/")

@remote.tokengetter
def get_remote_token(token=None):
    if 'remote_oauth' in session:
        return session.get('remote_oauth')

@app.before_request
def before_request():
    g.user = None
    if 'remote_oauth' in session:
        g.user = session['remote_oauth']

# Callback
@app.route('/oauthorized')
def oauthorized():
    print "oauthorized!"
    resp = remote.authorized_response()
    print "paso la cagada"
    if resp is None:
        flash('No tienes autorizacion.')
    else:
        session['remote_oauth'] = resp
    print "paso la ultima cagada"
    print resp
    return render_template('index.html', wines=None)



# ACTIONS
#-------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
	# wines = remote.request('wines')
    return render_template('index.html', wines=None)
	# return render_template('index.html', wines=wines.data['all'])

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
    import os
    os.environ['DEBUG'] = 'true'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
	app.run(port=8002, host="localhost")