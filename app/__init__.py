""" This module contains the factory function to create the Flask app instance. """

from os import path

from flask import Flask
from flask_jwt_extended import JWTManager

from app.blueprints import register_blueprints
from app.config.development_config import DevelopmentConfig
from app.extension import mail, api
from app.utils.error_handlers.system_wide_error_handler import (
    register_system_wide_error_handlers,
)
from app.utils.jwt_helpers import add_jwt_after_request_handler
from app.utils.logger import setup_logging


def create_app():
    """Factory function to create the Flask app instance."""
    template_dir = path.join(path.abspath(path.dirname(__file__)), "templates")
    app = Flask(__name__, template_folder=template_dir)

    api.init_app(app)

    app.config.from_object(DevelopmentConfig)

    mail.init_app(app)
    JWTManager(app)

    setup_logging(app)
    register_system_wide_error_handlers(app)
    register_blueprints(api)
    add_jwt_after_request_handler(app)

    return app
