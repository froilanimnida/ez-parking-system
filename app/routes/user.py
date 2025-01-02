""" User authentication routes. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint

from app.exceptions.authorization_exceptions import EmailAlreadyTaken
from app.utils.role_decorator import user_role_required
from app.schema.common_schema_validation import UserUpdateProfileSchema
from app.schema.response_schema import ApiResponse
from app.schema.user_auth_schema import UserRegistrationSchema
from app.services.auth_service import AuthService
from app.utils.error_handlers.auth_error_handlers import handle_email_already_taken
from app.utils.response_util import set_response

user_auth_blp = Blueprint(
    "user_auth",
    __name__,
    url_prefix="/api/v1/user",
    description="User authentication routes.",
)


@user_auth_blp.route("/create-new-account")
class CreateUserAccount(MethodView):
    @user_auth_blp.arguments(UserRegistrationSchema)
    @user_auth_blp.response(201, ApiResponse)
    @user_auth_blp.doc(
        description="Create a new user account.",
        responses={
            201: {"description": "User created successfully."},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def post(self, sign_up_data: dict):
        AuthService.create_new_user(sign_up_data)
        return set_response(
            201, {"code": "success", "message": "Check your email for verification."}
        )
@user_auth_blp.route("/profile")
class UserProfile(MethodView):
    @user_auth_blp.response(200, ApiResponse)
    @user_auth_blp.doc(
        description="Get user profile.",
        responses={
            200: {"description": "User profile retrieved successfully."},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    @user_role_required()
    def get(self, user_id):
        user_data = AuthService.get_profile(user_id, role=get_jwt().get("role"))
        return set_response(
            200, {"code": "success", "message": user_data}
        )
@user_auth_blp.route("/profile/update")
class UpdateUserProfile(MethodView):
    @user_auth_blp.arguments(UserUpdateProfileSchema)
    @user_auth_blp.response(200, ApiResponse)
    @user_auth_blp.doc(
        description="Update user profile.",
        responses={
            200: {"description": "User profile updated successfully."},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(optional=False)
    @user_role_required()
    def patch(self, update_data, user_id):
        AuthService.update_profile(user_id, update_data)
        return set_response(
            200, {"code": "success", "message": "Profile updated successfully."}
        )

user_auth_blp.register_error_handler(EmailAlreadyTaken, handle_email_already_taken)
