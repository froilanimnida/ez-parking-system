""" Wraps all the transactions routes and path of the system. """

from flask import Blueprint
from flask_jwt_extended import jwt_required

transactions = Blueprint("transactions", __name__)


@transactions.route("/v1/transaction/reservation/create", methods=["POST"])
@jwt_required(optional=False)
def create_transaction_reservation():
    """Creates a new transaction for a reservation."""
    # Implementation goes here


@transactions.route("/v1/transaction/reservation/cancel", methods=["POST"])
@jwt_required(optional=False)
def cancel_transaction_reservation():
    """Cancels a transaction for a reservation."""
    # Implementation goes here
