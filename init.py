from flask import Flask
from .routes import main
from flask_htmlmin import HTMLMIN 

from flask_dance.contrib.google import make_google_blueprint
import os

def create_app(config_obj=None):
    app = Flask(__name__)
    app.config.from_object(config_obj)

    # register the blueprints
    app.register_blueprint(main)

    return app
