""" This module contains the routes for the authentication endpoints. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import (
    get_jwt,
    set_access_cookies,
    jwt_required,
    set_refresh_cookies,
)

from app.services.token_service import TokenService
from app.exceptions.authorization_exceptions import (
    BannedUserException,
    EmailNotFoundException,
    InvalidPhoneNumberException,
    PhoneNumberAlreadyTaken,
    EmailAlreadyTaken,
    ExpiredOTPException,
    IncorrectOTPException,
    RequestNewOTPException,
)
from app.utils.error_handlers.auth_error_handlers import (
    handle_banned_user,
    handle_email_not_found,
    handle_email_already_taken,
    handle_phone_number_already_taken,
    handle_invalid_phone_number,
    handle_incorrect_otp,
    handle_expired_otp,
    handle_request_new_otp,
)
from app.schema.auth_validation import (
    OTPGenerationSchema,
    LoginWithEmailValidationSchema,
    NicknameFormValidationSchema,
    OTPSubmissionSchema,
    SignUpValidationSchema,
)
from app.schema.response_schema import ApiResponse
from app.utils.response_util import set_response
from app.services.auth_service import AuthService

auth_blp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/v1/auth",
    description="Auth API for EZ Parking System Frontend",
)


@auth_blp.route("/create-new-account")
class CreateNewAccount(MethodView):

    @auth_blp.arguments(SignUpValidationSchema)
    @auth_blp.response(201, ApiResponse)
    @auth_blp.doc(
        description="Create a new user account.",
        responses={
            201: {"description": "User created successfully."},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def post(self, sign_up_data):
        auth_service = AuthService()
        auth_service.create_new_user(sign_up_data)
        return set_response(
            201, {"code": "success", "message": "User created successfully."}
        )


@auth_blp.route("/login")
class Login(MethodView):
    @auth_blp.arguments(LoginWithEmailValidationSchema)
    @auth_blp.response(200, ApiResponse)
    @auth_blp.doc(
        description="Login with email.",
        responses={
            200: {"description": "OTP sent successfully."},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def post(self, login_data):
        auth_service = AuthService()
        auth_service.login_user(login_data)
        return set_response(
            200, {"code": "otp_sent", "message": "OTP sent successfully."}
        )


@auth_blp.route("/generate-otp")
class GenerateOTP(MethodView):
    @auth_blp.arguments(OTPGenerationSchema)
    @auth_blp.response(200, ApiResponse)
    @auth_blp.doc(
        description="Generate an OTP.",
        responses={
            200: {"description": "OTP sent successfully."},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def patch(self, data):
        auth_service = AuthService()
        email = data.get("email")
        auth_service.generate_otp(email)
        return set_response(
            200, {"code": "otp_sent", "message": "OTP sent successfully."}
        )


@auth_blp.route("/verify-otp")
class VerifyOTP(MethodView):
    @auth_blp.arguments(OTPSubmissionSchema)
    @auth_blp.response(200, ApiResponse)
    @auth_blp.doc(
        description="Verify the OTP.",
        responses={
            200: {"description": "OTP verified."},
            400: {"description": "Bad Request"},
        },
    )
    @jwt_required(True)
    def patch(self, data):
        auth_service = AuthService()
        email = data.get("email")
        otp = data.get("otp")
        remember_me = data.get("remember_me")
        user_id, role = auth_service.verify_otp(email, otp)
        token_service = TokenService()
        (
            access_token,
            refresh_token,
        ) = token_service.generate_jwt_csrf_token(
            email=email, user_id=user_id, role=role, remember_me=remember_me
        )
        response = set_response(200, {"code": "success", "message": "OTP verified."})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response


@auth_blp.route("/set-nickname")
class SetNickname(MethodView):
    @auth_blp.arguments(NicknameFormValidationSchema)
    @auth_blp.response(200, ApiResponse)
    @auth_blp.doc(
        description="Set the nickname of the user.",
        responses={
            200: {"description": "Nickname set successfully."},
            404: {"description": "Not Found"},
        },
    )
    @jwt_required(False)
    def patch(self, data):
        nickname = data.get("nickname")
        user_id = get_jwt().get("sub").get("user_id")  # type: ignore
        auth_service = AuthService()
        auth_service.set_nickname(user_id=user_id, nickname=nickname)
        return set_response(
            200, {"code": "success", "message": "Nickname set successfully."}
        )


@auth_blp.route("/logout")
class Logout(MethodView):
    @auth_blp.response(200, ApiResponse)
    @auth_blp.doc(
        description="Logout the user.",
        responses={
            200: {"description": "Logged out successfully."},
        },
    )
    @jwt_required(False)
    def post(self):
        response = set_response(
            200, {"code": "success", "message": "Logged out successfully."}
        )
        set_access_cookies(response, "")
        set_refresh_cookies(response, "")
        return response


@auth_blp.route("/verify-token")
@jwt_required(False)
class VerifyToken(MethodView):
    @auth_blp.response(200, ApiResponse)
    @auth_blp.doc(
        description="Verify the JWT token present in the request.",
        responses={
            200: {"description": "Token verified successfully."},
            400: {"description": "Bad Request"},
            401: {"description": "Unauthorized"},
        },
    )
    def post(self):
        get_jwt()
        return set_response(
            200,
            {"code": "success", "message": "Token verified successfully."},
        )


auth_blp.register_error_handler(BannedUserException, handle_banned_user)
auth_blp.register_error_handler(EmailNotFoundException, handle_email_not_found)
auth_blp.register_error_handler(EmailAlreadyTaken, handle_email_already_taken)
auth_blp.register_error_handler(
    PhoneNumberAlreadyTaken, handle_phone_number_already_taken
)
auth_blp.register_error_handler(
    InvalidPhoneNumberException, handle_invalid_phone_number
)
auth_blp.register_error_handler(ExpiredOTPException, handle_expired_otp)
auth_blp.register_error_handler(IncorrectOTPException, handle_incorrect_otp)
auth_blp.register_error_handler(RequestNewOTPException, handle_request_new_otp)
