""" User authentication routes. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from app.exceptions.authorization_exceptions import EmailAlreadyTaken
from app.schema.auth_validation import EmailVerificationSchema
from app.schema.response_schema import ApiResponse
from app.schema.user_auth_schema import UserRegistrationSchema
from app.services.auth_service import AuthService
from app.services.user_auth import UserAuth
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
        sign_up_data.update({"role": "user"})
        UserAuth.create_new_user(sign_up_data)
        return set_response(
            201, {"code": "success", "message": "Check your email for verification."}
        )


user_auth_blp.register_error_handler(EmailAlreadyTaken, handle_email_already_taken)
