""" Wraps all function of role parking manager. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from functools import wraps

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint

from app.exceptions.qr_code_exceptions import (
    InvalidQRContent,
    InvalidTransactionStatus,
    QRCodeExpired,
)
from app.exceptions.slot_lookup_exceptions import SlotNotFound
from app.routes.transaction import handle_invalid_transaction_status
from app.schema.parking_manager_validation import (
    ParkingManagerIndividualOwnerSchema, ParkingManagerCompanyOwnerSchema
)
from app.schema.transaction_validation import ValidateEntrySchema
from app.schema.response_schema import ApiResponse
from app.services.establishment_service import EstablishmentService
from app.services.operating_hour_service import OperatingHourService
from app.services.transaction_service import TransactionService
from app.utils.error_handlers.qr_code_error_handlers import (
    handle_invalid_qr_content,
    handle_qr_code_expired,
)
from app.utils.error_handlers.slot_lookup_error_handlers import handle_slot_not_found
from app.utils.response_util import set_response

parking_manager_blp = Blueprint(
    "parking_manager",
    __name__,
    url_prefix="/api/v1/parking-manager",
    description="Parking Manager API for EZ Parking System Frontend",
)


def parking_manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data = get_jwt()
            is_parking_manager = jwt_data.get("role") == "parking_manager"
            is_admin = jwt_data.get("role") == "admin"
            if not is_parking_manager and not is_admin:
                return set_response(
                    401,
                    {
                        "code": "unauthorized",
                        "message": "Parking manager or admin required.",
                    },
                )
            user_id = jwt_data.get("sub", {}).get("user_id")
            return fn(*args, user_id=user_id, **kwargs)
        return decorator
    return wrapper


@parking_manager_blp.route("/company/account/create")
class CreateParkingManagerCompanyAccount(MethodView):
    @parking_manager_blp.arguments(ParkingManagerCompanyOwnerSchema)
    @parking_manager_blp.response(201, ApiResponse)
    @parking_manager_blp.doc(
        description="Create a new parking manager account.",
        responses={
            201: "Company parking manager account created successfully.",
            400: "Bad Request",
            422: "Unprocessable Entity",
        },
    )
    def post(self, company_account_data):
        print(company_account_data)
        # AuthService.create_new_user(company_account_data)
        return set_response(
            201,
            {
                "code": "success",
                "message": "Company parking manager account created successfully.",
            },
        )

@parking_manager_blp.route("/individual/account/create")
class CreateParkingManagerIndividualAccount(MethodView):
    @parking_manager_blp.arguments(ParkingManagerIndividualOwnerSchema)
    @parking_manager_blp.response(201, ApiResponse)
    @parking_manager_blp.doc(
        description="Individual Parking Manager Account Creation",
        responses={
            201: "Individual parking manager account created successfully.",
            400: "Bad Request",
            422: "Unprocessable Entity",
        },
    )
    @jwt_required(True)
    def post(self, individual_account_data):
        print(individual_account_data)
        # AuthService.create_new_user(individual_account_data)
        return set_response(
            201,
            {
                "code": "success",
                "message": "Individual parking manager account created successfully.",
            },
        )


@parking_manager_blp.route("/validate/entry")
class EstablishmentEntry(MethodView):
    @jwt_required(False)
    @parking_manager_required()
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Routes that will validate the token of the reservation qr code and update"
        "the status of slot to be occupied.",
        responses={
            200: "Transaction successfully verified",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    @parking_manager_blp.arguments(ValidateEntrySchema)
    @parking_manager_blp.response(200, ApiResponse)
    def patch(self, data, user_id):  # pylint: disable=unused-argument
        transaction_service = TransactionService
        transaction_service.verify_reservation_code(data.get("qr_content"))
        return set_response(
            200, {"code": "success", "message": "Transaction successfully verified."}
        )


@parking_manager_blp.route("/qr-content/overview")
class GetQRContentOverview(MethodView):
    @parking_manager_blp.arguments(ValidateEntrySchema, location="query")
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Get the QR content overview.",
        responses={
            200: "QR content overview retrieved successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @parking_manager_required()
    def get(self, data, user_id):  # pylint: disable=unused-argument
        data = TransactionService.get_transaction_details_from_qr_code(
            data.get("qr_content")
        )
        return set_response(
            200,
            {
                "code": "success",
                "message": "QR content overview retrieved successfully.",
                "data": data,
            },
        )


@parking_manager_blp.route("/get-establishment")
class GetAllEstablishmentsInfo(MethodView):
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description=(
            "Get all establishments information "
            "that is being managed by the parking manager "
            "via their uuid identity in the jwt token."
        ),
        responses={
            200: "Establishments information retrieved successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @parking_manager_required()
    def get(self, user_id):
        data = EstablishmentService.get_establishment(user_id)
        return set_response(
            200,
            {
                "code": "success",
                "message": "Establishments information retrieved successfully.",
                "data": data,
            },
        )


@parking_manager_blp.route("/get-operating-hours")
class GetScheduleHours(MethodView):
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Get the operating hours of the establishment.",
        responses={
            200: "Operating hours retrieved successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @parking_manager_required()
    def get(self, user_id):
        operating_hours = OperatingHourService.get_operating_hours(user_id)
        return set_response(
            200,
            {
                "code": "success",
                "message": "Schedule hours retrieved successfully.",
                "operating_hours": operating_hours,
            },
        )


parking_manager_blp.register_error_handler(SlotNotFound, handle_slot_not_found)
parking_manager_blp.register_error_handler(InvalidQRContent, handle_invalid_qr_content)
parking_manager_blp.register_error_handler(
    InvalidTransactionStatus, handle_invalid_transaction_status
)
parking_manager_blp.register_error_handler(QRCodeExpired, handle_qr_code_expired)
