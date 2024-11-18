"""Register all blueprints."""

from flask_smorest import Api

from app.routes.auth import auth_blp
from app.routes.establishment import establishment_blp
from app.routes.parking_manager import parking_manager_blp
from app.routes.slot import slot_blp
from app.routes.transaction import transactions_blp


def register_blueprints(app: Api):
    """Register all blueprints."""
    app.register_blueprint(auth_blp)
    app.register_blueprint(slot_blp)
    app.register_blueprint(establishment_blp)
    app.register_blueprint(parking_manager_blp)
    app.register_blueprint(transactions_blp)
