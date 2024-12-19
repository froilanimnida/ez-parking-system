""" Wraps all function of role parking manager. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from functools import wraps

from flask import request, json
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint

from app.exceptions.general_exceptions import FileSizeTooBig
from app.exceptions.qr_code_exceptions import (
    InvalidQRContent, InvalidTransactionStatus, QRCodeExpired
)
from app.exceptions.slot_lookup_exceptions import SlotNotFound
from app.routes.transaction import handle_invalid_transaction_status
from app.schema.parking_manager_validation import ParkingManagerRequestSchema
from app.schema.response_schema import ApiResponse
from app.schema.transaction_validation import ValidateEntrySchema
from app.services.auth_service import AuthService
from app.services.establishment_service import EstablishmentService
from app.services.operating_hour_service import OperatingHourService
from app.services.transaction_service import TransactionService
from app.utils.error_handlers.general_error_handler import handle_file_size_too_big
from app.utils.error_handlers.qr_code_error_handlers import (
    handle_invalid_qr_content, handle_qr_code_expired
)
from app.utils.error_handlers.slot_lookup_error_handlers import handle_slot_not_found
from app.utils.response_util import set_response
from app.utils.security import check_file_size

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
    @parking_manager_blp.arguments(ParkingManagerRequestSchema, location="form")
    @parking_manager_blp.response(201, ApiResponse)
    def post(self):
        return set_response(
            201,
            {
                "code": "success",
                "message": "Company parking manager account created successfully.",
            },
        )


@parking_manager_blp.route("/individual/account/create")
class CreateParkingManagerIndividualAccount(MethodView):
    @parking_manager_blp.response(201, ApiResponse)
    @parking_manager_blp.doc(
        description="Individual Parking Manager Account Creation",
        responses={
            201: "Individual parking manager account created successfully.",
            400: "Bad Request",
            422: "Unprocessable Entity",
        },
    )
    @jwt_required(optional=True)
    def post(self):
        check_file_size(request)
        try:
            documents_list = []

            single_file_fields = [
                'gov_id',
                'proof_of_ownership',
                'bir_cert',
                'liability_insurance',
                'business_cert'
            ]

            for field in single_file_fields:
                if field in request.files:
                    file = request.files[field]
                    documents_list.append({
                        "type": field,
                        "file": file,
                        "filename": file.filename
                    })

            for key in request.files:
                if key.startswith('parking_photos['):
                    file = request.files[key]
                    documents_list.append({
                        "type": "parking_photo",
                        "file": file,
                        "filename": file.filename
                    })

            form_data = json.loads(request.form.get("sign_up_data"))
            form_data['documents'] = documents_list
        except Exception as e:  # pylint: disable=broad-exception-caught
            return set_response(
                400, {"code": "error", "message": "Invalid JSON data", "errors": str(e)}
            )
        parking_manager_request_schema = ParkingManagerRequestSchema()
        validated_sign_up_data = parking_manager_request_schema.load(form_data)
        auth_service = AuthService()
        auth_service.create_new_user(validated_sign_up_data)

        return set_response(
            201,
            {
                "code": "success",
                "message": "Account created successfully.",
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
parking_manager_blp.register_error_handler(FileSizeTooBig, handle_file_size_too_big)
