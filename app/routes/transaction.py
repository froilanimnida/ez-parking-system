""" Wraps all the transactions routes and path of the system. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from app.schema.response_schema import ApiResponse
from app.schema.transaction_validation import ReservationCreationSchema
from app.utils.response_util import set_response

transactions_blp = Blueprint(
    "transactions",
    __name__,
    url_prefix="/api/v1/transaction",
    description="Transaction API for EZ Parking System Frontend",
)


@transactions_blp.route("/reservation/create", methods=["POST"])
class CreateReservation(MethodView):

    @transactions_blp.arguments(ReservationCreationSchema)
    @transactions_blp.response(201, ApiResponse)
    @transactions_blp.doc(
        description="Create a new reservation transaction.",
        responses={
            201: "Reservation created successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    def post(self, data):
        # Create a new transaction for a reservation
        print(data)
        return set_response(201, {"message": "Reservation created successfully."})


@transactions_blp.route("/reservation/cancel", methods=["POST"])
@jwt_required(False)
class CancelReservation(MethodView):

    @transactions_blp.response(200, ApiResponse)
    @transactions_blp.doc(
        description="Cancel a reservation transaction.",
        responses={
            200: "Reservation canceled successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    @jwt_required(False)
    def post(self, data):
        # Cancel a transaction for a reservation
        print(data)
        return set_response(200, {"message": "Reservation canceled successfully."})
