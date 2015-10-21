# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask_analytics import Analytics

import logging

# Define the WSGI application object
app = Flask(__name__)
Analytics(app)

app.config['ANALYTICS']['GOOGLE_ANALYTICS']['ACCOUNT'] = 'UA-32402274-3'

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

from models import Vote, Post

db.create_all()

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return "404 not found"

#Length to store cookie (in seconds)
MAX_COOKIE_AGE = 4*3600

from controllers import predict_game
from image_moderation_controllers import image_moderation

app.register_blueprint(predict_game)
app.register_blueprint(image_moderation)

# Log only in production mode.

if not app.DEBUG:
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)