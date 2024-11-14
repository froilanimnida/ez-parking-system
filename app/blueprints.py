"""Register all blueprints."""

from flask import Flask

from app.routes.establishment import establishment
from app.routes.auth import auth
from app.routes.slot import slot


def register_blueprints(app: Flask):
    """Register all blueprints."""
    app.register_blueprint(auth)
    app.register_blueprint(slot)
    app.register_blueprint(establishment)
