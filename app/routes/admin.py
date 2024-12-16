""" Wraps all the admin routes. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from functools import wraps

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint

from app.exceptions.establishment_lookup_exceptions import EstablishmentDoesNotExist
from app.schema.ban_query_validation import BanQueryValidation
from app.schema.common_schema_validation import NewEstablishmentCommonValidation
from app.services.admin_service import AdminService
from app.services.establishment_service import EstablishmentService
from app.services.vehicle_type_service import VehicleTypeService
from app.utils.error_handlers.establishment_error_handlers import (
    handle_establishment_does_not_exist
)
from app.utils.response_util import set_response

admin_blp = Blueprint(
    "admin",
    "admin",
    url_prefix="/api/v1/admin",
    description="Admin API for EZ Parking System Frontend",
)


def admin_role_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data = get_jwt()
            is_admin = jwt_data.get("role") == "admin"
            if not is_admin:
                return set_response(
                    401, {"code": "unauthorized", "message": "Admin required."}
                )
            admin_id = jwt_data.get("sub", {}).get("user_id")
            return fn(admin_id=admin_id, *args, **kwargs)

        return decorator

    return wrapper

@admin_blp.route("/users")
class GetAllUsers(MethodView):
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Get all users.",
        responses={
            200: "Users retrieved.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def get(self, admin_id): # pylint: disable=unused-argument
        admin_service = AdminService()
        users = admin_service.get_all_users()
        return set_response(200, {"code": "success", "data": users})


@admin_blp.route("/ban-user")
class BanUser(MethodView):
    @admin_blp.arguments(BanQueryValidation)
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Ban a plate number.",
        responses={
            200: "Plate number banned.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @admin_role_required()
    @jwt_required(False)
    def post(self, ban_data, admin_id):
        admin_service = AdminService()
        admin_service.ban_user(ban_data, admin_id)
        return set_response(201, {"code": "success", "message": "Plate number banned."})


@admin_blp.route("/unban-user")
class UnbanUser(MethodView):
    @admin_blp.arguments(BanQueryValidation)
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Unban a user.",
        responses={
            200: "User unbanned.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @admin_role_required()
    @jwt_required(False)
    def post(self, ban_data, admin_id):
        # admin_service = AdminService()
        print(ban_data, admin_id)
        # admin_service.unban_user(ban_data, admin_id)
        return set_response(
            201, {"code": "success", "message": "User unbanned."}
        )


@admin_blp.route("/get-banned-users")
class GetBannedUsers(MethodView):
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Get all banned users.",
        responses={
            200: "Banned users retrieved.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @admin_role_required()
    @jwt_required(False)
    def get(self, admin_id):  # pylint: disable=unused-argument
        # admin_service = AdminService()
        # banned_users = admin_service.get_banned_users(admin_id)
        return set_response(200, {"code": "success", "data": "HELLO"})

@admin_blp.route("/vehicle-types")
class GetAllVehicleTypes(MethodView):
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Get all vehicle types.",
        responses={
            200: "Vehicle types retrieved.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    @jwt_required(False)
    def get(self, admin_id):  # pylint: disable=unused-argument
        vehicle_types = VehicleTypeService().get_all_vehicle_types()
        return set_response(200, {"code": "success", "data": vehicle_types})


@admin_blp.route("/establishments")
class ParkingManagerApplications(MethodView):
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Get all establishment along their data.",
        responses={
            200: "Establishment data retrieved.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def get(self, admin_id):  # pylint: disable=unused-argument
        parking_establishments = AdminService().get_establishments()
        print(parking_establishments)
        return set_response(200, {"code": "success", "data": parking_establishments})


@admin_blp.route("/approve-parking-manager-application")
class ApproveManagerApplication(MethodView):
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Approve a parking manager application.",
        responses={
            200: "Parking manager application approved.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def post(self, ban_data, admin_id):  # pylint: disable=unused-argument
        # AdminService().approve_parking_applicant(ban_data)
        return set_response(
            201, {"code": "success", "message": "Parking manager application approved."}
        )
@admin_blp.route("/establishment")
class GetParkingEstablishment(MethodView):
    @admin_blp.arguments(NewEstablishmentCommonValidation, location="query")
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Get parking establishment details.",
        responses={
            200: "Parking establishment details retrieved.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def get(self, data, admin_id): # pylint: disable=unused-argument
        establishment_info = EstablishmentService.get_establishment(
            data.get('establishment_uuid')
        )
        company_profile_creator = establishment_info.get('company_profile').get('user_id')
        user_info = AdminService.get_user(company_profile_creator)
        establishment_info.update({"user": user_info})
        print(company_profile_creator)
        return set_response(200, {"code": "success", "data": establishment_info})


admin_blp.register_error_handler(EstablishmentDoesNotExist, handle_establishment_does_not_exist)
