# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
import os


# Define the WSGI application object
app = Flask(__name__)

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
    # return render_template('404.html'), 404


current_image_1 = None
current_image_2 = None
current_picture_source = None

#Length to store cookie (in seconds)
MAX_COOKIE_AGE = 4*3600

from controllers import predict_game

app.register_blueprint(predict_game)
