"""Register all blueprints."""

from flask_smorest import Api

from app.routes.auth import auth_blp
from app.routes.slot import slot_blp


def register_blueprints(app: Api):
    """Register all blueprints."""
    app.register_blueprint(auth_blp)
    app.register_blueprint(slot_blp)
