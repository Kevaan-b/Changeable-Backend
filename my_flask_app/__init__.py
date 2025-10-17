"""
Flask application factory and configuration.
"""
from flask import Flask
#from routes.api import api_bp
from .config.settings import Config

def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    #app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
