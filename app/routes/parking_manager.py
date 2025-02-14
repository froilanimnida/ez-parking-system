""" Wraps all function of role parking manager. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask import request, json
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from app.exceptions.general_exceptions import FileSizeTooBig
from app.exceptions.qr_code_exceptions import (
    InvalidQRContent, InvalidTransactionStatus, QRCodeExpired
)
from app.exceptions.slot_lookup_exceptions import SlotNotFound, SlotAlreadyExists
from app.routes.transaction import handle_invalid_transaction_status
from app.schema.common_schema_validation import TransactionCommonValidationSchema
from app.schema.parking_manager_validation import ParkingManagerRequestSchema
from app.schema.response_schema import ApiResponse
from app.schema.slot_validation import CreateSlotParkingManagerSchema
from app.schema.transaction_validation import ValidateEntrySchema, ValidateTransaction
from app.services.auth_service import AuthService
from app.services.establishment_service import EstablishmentService
from app.services.operating_hour_service import OperatingHourService
from app.services.parking_manager_service import ParkingManagerService
from app.services.transaction_service import TransactionService
from app.services.vehicle_type_service import VehicleTypeService
from app.utils.error_handlers.general_error_handler import handle_file_size_too_big
from app.utils.error_handlers.qr_code_error_handlers import (
    handle_invalid_qr_content, handle_qr_code_expired
)
from app.utils.error_handlers.slot_lookup_error_handlers import (
    handle_slot_not_found, handle_slot_already_exists
)
from app.utils.response_util import set_response
from app.utils.security import check_file_size
from app.utils.role_decorator import parking_manager_role_required

parking_manager_blp = Blueprint(
    "parking_manager",
    __name__,
    url_prefix="/api/v1/parking-manager",
    description="Parking Manager API for EZ Parking System Frontend",
)


@parking_manager_blp.route("/vehicle-types")
class GetAllVehicleTypes(MethodView):
    @parking_manager_blp.response(200, {"message": str})
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Get all vehicle types.",
        responses={
            200: "Vehicle types retrieved.",
            401: "Unauthorized",
        },
    )
    @parking_manager_role_required()
    @jwt_required(False)
    def get(self, user_id):  # pylint: disable=unused-argument
        vehicle_types = VehicleTypeService().get_all_vehicle_types()
        return set_response(200, {"code": "success", "data": vehicle_types})

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
    @parking_manager_role_required()
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
    @parking_manager_blp.arguments(ValidateTransaction)
    @parking_manager_blp.response(200, ApiResponse)
    def patch(self, data, user_id):  # pylint: disable=unused-argument
        transaction_service = TransactionService()
        transaction_service.verify_reservation_code(
            data.get("qr_content"),data.get("payment_status")
        )
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
    @parking_manager_role_required()
    def get(self, data, user_id):
        data = TransactionService.get_transaction_details_from_qr_code(
            data.get("qr_content"), user_id
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
    @parking_manager_role_required()
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


@parking_manager_blp.route("/operating-hours")
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
    @parking_manager_role_required()
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

@parking_manager_blp.route("/operating-hours/update")
class UpdateScheduleHours(MethodView):
    @parking_manager_blp.arguments(ParkingManagerRequestSchema, location="json")
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Update the operating hours of the establishment.",
        responses={
            200: "Operating hours updated successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def patch(self, data, user_id):  # pylint: disable=unused-argument
        # OperatingHourService.update_operating_hours(data, user_id)
        return set_response(
            200,
            {
                "code": "success",
                "message": "Operating hours updated successfully.",
            },
        )

@parking_manager_blp.route("/slots")
class Slots(MethodView):
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Get the slots of the establishment.",
        responses={
            200: "Slots retrieved successfully.",
            400: "Bad Request",
            401: "Unauthorized",
        },
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        slots = ParkingManagerService.get_all_slots(user_id)
        return set_response(
            200,
            {
                "code": "success",
                "data": slots,
            },
        )
@parking_manager_blp.route("/slot/create")
class CreateSlot(MethodView):
    @parking_manager_blp.arguments(CreateSlotParkingManagerSchema)
    @parking_manager_blp.response(201, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Create a new slot.",
        responses={
            201: "Slot created successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            422: "Unprocessable Entity",
        },
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def post(self, data, user_id):
        ParkingManagerService.create_slot(data, user_id, request.remote_addr)
        return set_response(
            201,
            {
                "code": "success",
                "message": "Slot created successfully.",
            },
        )

@parking_manager_blp.route('/transactions')
class GetTransactions(MethodView):
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="Get all the transactions of the user.",
        responses={
            200: "Transactions fetched successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        transactions = TransactionService.get_establishment_transaction(user_id)
        return set_response(
            200,
            {
                "code": "success",
                "data": transactions,
            },
        )
@parking_manager_blp.route('/transaction')
class GetTransaction(MethodView):
    @parking_manager_blp.arguments(TransactionCommonValidationSchema, location="query")
    @parking_manager_blp.response(200, ApiResponse)
    @parking_manager_blp.doc(
        security=[{"Bearer": []}],
        description="View the transaction details.",
        responses={
            200: "Transaction details fetched successfully.",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
        },
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, data, user_id):  # pylint: disable=unused-argument
        transaction = TransactionService.get_transaction(data.get("transaction_uuid"))
        return set_response(
            200,
            {
                "code": "success",
                "data": transaction,
            },
        )

parking_manager_blp.register_error_handler(SlotNotFound, handle_slot_not_found)
parking_manager_blp.register_error_handler(InvalidQRContent, handle_invalid_qr_content)
parking_manager_blp.register_error_handler(
    InvalidTransactionStatus, handle_invalid_transaction_status
)
parking_manager_blp.register_error_handler(QRCodeExpired, handle_qr_code_expired)
parking_manager_blp.register_error_handler(FileSizeTooBig, handle_file_size_too_big)
parking_manager_blp.register_error_handler(SlotAlreadyExists, handle_slot_already_exists)
