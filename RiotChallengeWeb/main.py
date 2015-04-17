#-----------------------------------------------------------------------------
# Name: get_matches.py
#
# Author: Alexander Popov
#
#-----------------------------------------------------------------------------  
import logging
import time

from flask import Flask, render_template, request, abort, jsonify
from datetime import datetime
from google.appengine.api import urlfetch

import RiotApiChallenge

app = Flask(__name__)
app.config['DEBUG'] = True

#Addressing Google App Engine bug
environment = 'PROD'
if environment == 'DEV':
    import sys

    from google.appengine.tools.devappserver2.python import sandbox
    sandbox._WHITE_LIST_C_MODULES += ['_ssl', '_socket']

    #from socket import socket as patched_socket
    
    #sys.modules['socket'] = patched_socket
    #socket = patched_socket

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def index():       
    return render_template("index.html")

@app.route('/predict', methods = ['GET'])
def predict():
    #set timeout to be longer when making prediction call
    urlfetch.set_default_fetch_deadline(60)
    name = request.args.get('name', None)
    
    #For demo purposes only using NA
    #region = request.args.get('region', 'na')

    #Standardize summoner name
    name = name.lower().replace(" ", "")
    
    #Log requests
    logging.info("Processing SummonerName: {0}".format(name))
    
    if name is None:
        abort(404)
    
    current_game, summ_id = RiotApiChallenge.get_current_game(name)
    
    if current_game == RiotApiChallenge.SUMMONER_NOT_FOUND:
        abort(404)
    elif current_game == RiotApiChallenge.ERROR:
        abort(505)
    
    won, confidence = RiotApiChallenge.make_prediction(current_game, summ_id)
    return jsonify(win=won,
                   pct=confidence)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
