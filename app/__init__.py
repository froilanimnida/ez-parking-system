""" This module contains the factory function to create the Flask app instance. """

# pylint: disable=W0603:

from os import path

from flask import Flask
from flask_jwt_extended import JWTManager

from app.blueprints import register_blueprints
from app.config.development_config import DevelopmentConfig
from app.extension import mail, api, celery
from app.utils.celery_utils import make_celery
from app.utils.error_handlers.system_wide_error_handler import (
    register_system_wide_error_handlers,
)
from app.utils.jwt_helpers import add_jwt_after_request_handler
from app.utils.logger import setup_logging


# noinspection PyGlobalUndefined
def create_app():
    """Factory function to create the Flask app instance."""
    template_dir = path.join(path.abspath(path.dirname(__file__)), "templates")

    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(DevelopmentConfig)

    global celery
    celery = make_celery(app)

    api.init_app(app)
    JWTManager(app)
    mail.init_app(app)

    setup_logging(app)
    register_system_wide_error_handlers(app)
    register_blueprints(api)
    add_jwt_after_request_handler(app)
    return app
