""" Wraps all the admin routes. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from functools import wraps

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint

from app.schema.ban_query_validation import BanQueryValidation
from app.services.admin_service import AdminService
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


@admin_blp.route("/ban-user")
class BanPlateNumber(MethodView):
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
        admin_service = AdminService()
        admin_service.unban_user(ban_data, admin_id)
        return set_response(
            201, {"code": "success", "message": "User unbanned."}
        )
