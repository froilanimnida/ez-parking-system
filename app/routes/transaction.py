""" Wraps all the transactions routes and path of the system. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from functools import wraps

from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint

from app.exceptions.qr_code_exceptions import InvalidQRContent, InvalidTransactionStatus
from app.exceptions.transaction_exception import (
    UserHasNoPlateNumberSetException, HasExistingReservationException
)
from app.schema.response_schema import ApiResponse
from app.schema.transaction_validation import (
    CancelReservationSchema, ReservationCreationSchema, TransactionFormDetailsSchema,
    ViewTransactionSchemaSchema
)
from app.services.transaction_service import TransactionService
from app.utils.error_handlers.qr_code_error_handlers import (
    handle_invalid_qr_content, handle_invalid_transaction_status
)
from app.utils.error_handlers.transaction_error_handlers import (
    handle_user_has_no_plate_number_set, handle_has_existing_reservation,
)
from app.utils.response_util import set_response

transactions_blp = Blueprint(
    "transactions",
    __name__,
    url_prefix="/api/v1/transaction",
    description="Transaction API for EZ Parking System Frontend",
)


def user_role_and_user_id_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data = get_jwt()
            is_user = jwt_data.get("role") == "user"
            if not is_user:
                return set_response(
                    401, {"code": "unauthorized", "message": "User required."}
                )
            user_id = jwt_data.get("sub", {}).get("user_id")
            return fn(user_id=user_id, *args, **kwargs)
        return decorator
    return wrapper


@transactions_blp.route("/create")
class CreateReservation(MethodView):
    @jwt_required(False)
    @user_role_and_user_id_required()
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
    def post(self, reservation_data, user_id):
        print(reservation_data, user_id)
        reservation_data.update({"user_id": user_id})
        transaction_validation = TransactionService()
        transaction_validation.reserve_slot(reservation_data)
        return set_response(201, {"message": "Reservation created successfully."})


@transactions_blp.route("/cancel")
class CancelReservation(MethodView):

    @jwt_required(False)
    @user_role_and_user_id_required()
    @transactions_blp.response(200, ApiResponse)
    @transactions_blp.arguments(CancelReservationSchema)
    @transactions_blp.doc(
        description="Cancel a reservation transaction.",
        responses={
            200: "Reservation canceled successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def patch(self, data, user_id):  # pylint: disable=unused-argument
        transaction_service = TransactionService()
        transaction_service.cancel_transaction(data.get("transaction_uuid"))
        return set_response(200, {"message": "Reservation canceled successfully."})


@transactions_blp.route("/view")
class ViewTransaction(MethodView):
    @jwt_required(False)
    @user_role_and_user_id_required()
    @transactions_blp.arguments(ViewTransactionSchemaSchema, location="query")
    @transactions_blp.response(200, ApiResponse)
    @transactions_blp.doc(
        description="View the transaction details.",
        responses={
            200: "Transaction details fetched successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def get(self, data, user_id):  # pylint: disable=unused-argument
        transaction_service = TransactionService
        transaction = transaction_service.view_transaction(data.get("transaction_uuid"))
        return set_response(200, {"code": "success", "transaction": transaction})


@transactions_blp.route("/checkout")
class TransactionOverview(MethodView):
    @jwt_required(False)
    @user_role_and_user_id_required()
    @transactions_blp.response(200, ApiResponse)
    @transactions_blp.arguments(TransactionFormDetailsSchema, location="query")
    @transactions_blp.doc(
        description="Get the transaction details.",
        responses={
            200: "Transaction details fetched successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def get(self, data, user_id):  # pylint: disable=unused-argument
        transaction_service = TransactionService()
        transaction = transaction_service.checkout(
            data.get("establishment_uuid"), data.get("slot_uuid"), user_id
        )
        return set_response(200, {"code": "success", "transaction": transaction})


@transactions_blp.route("/all")
class GetAllUserTransaction(MethodView):
    @jwt_required(False)
    @user_role_and_user_id_required()
    @transactions_blp.response(200, ApiResponse)
    @transactions_blp.doc(
        description="Get all the transactions of the user.",
        responses={
            200: "Transactions fetched successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    def get(self, user_id):
        transaction_service = TransactionService()
        transactions = transaction_service.get_all_user_transactions(user_id)
        return set_response(200, {"code": "success", "transactions": transactions})


transactions_blp.register_error_handler(InvalidQRContent, handle_invalid_qr_content)
transactions_blp.register_error_handler(
    InvalidTransactionStatus, handle_invalid_transaction_status
)
transactions_blp.register_error_handler(
    UserHasNoPlateNumberSetException, handle_user_has_no_plate_number_set
)
transactions_blp.register_error_handler(
    HasExistingReservationException, handle_has_existing_reservation
)
