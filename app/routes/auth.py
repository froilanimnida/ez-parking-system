""" This module contains the routes for the authentication endpoints. """

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, decode_token, set_access_cookies, jwt_required

from app.services.token_service import TokenService
from app.exceptions.authorization_exception import (
    EmailNotFoundException, InvalidEmailException, InvalidPhoneNumberException, PhoneNumberAlreadyTaken,
    EmailAlreadyTaken, MissingFieldsException, IncorrectPasswordException, PasswordTooShort, ExpiredOTPException,
    IncorrectOTPException
)
from app.utils.error_handlers import (
    handle_email_not_found, handle_email_already_taken, handle_invalid_email, handle_phone_number_already_taken,
    handle_invalid_phone_number, handle_missing_fields, handle_incorrect_password,
    handle_password_too_short, handle_incorrect_otp, handle_expired_otp
)
from app.schema.auth_validation import (
    SignUpValidation, LoginWithEmailValidation, NicknameFormValidation, OTPSubmissionFormValidation, OTPGenerationSchema
)
from app.utils.response_util import set_response
from app.services.auth_service import AuthService

auth = Blueprint('auth', __name__)

auth.register_error_handler(EmailNotFoundException, handle_email_not_found)
auth.register_error_handler(EmailAlreadyTaken, handle_email_already_taken)
auth.register_error_handler(InvalidEmailException, handle_invalid_email)
auth.register_error_handler(PhoneNumberAlreadyTaken, handle_phone_number_already_taken)
auth.register_error_handler(InvalidPhoneNumberException, handle_invalid_phone_number)
auth.register_error_handler(MissingFieldsException, handle_missing_fields)
auth.register_error_handler(IncorrectPasswordException, handle_incorrect_password)
auth.register_error_handler(PasswordTooShort, handle_password_too_short)
auth.register_error_handler(IncorrectPasswordException, handle_incorrect_otp)
auth.register_error_handler(ExpiredOTPException, handle_expired_otp)
auth.register_error_handler(IncorrectOTPException, handle_incorrect_otp)


@auth.route('/v1/auth/create-new-account', methods=['POST'])
def create_new_account():
    """ Create a new user account. """
    data = request.get_json()
    sign_up_schema = SignUpValidation()
    data = sign_up_schema.load(data)
    if not data:
        raise MissingFieldsException('Please provide all the required fields')
    auth_service = AuthService()
    auth_service.create_new_user(data) # type: ignore
    return set_response(201, {
        'code': 'success',
        'message': 'User created successfully.'
        })


@auth.route('/v1/auth/login', methods=['POST'])
def login():
    """ Login a user. """
    data = request.get_json()
    login_schema = LoginWithEmailValidation()
    data = login_schema.load(data)
    if not data:
        raise MissingFieldsException('Please provide all the required fields')
    auth_service = AuthService()
    auth_service.login_user(data) # type: ignore
    return set_response(200, {'code': 'otp_sent', 'message': 'OTP sent successfully.'})


@auth.route('/v1/auth/generate-otp', methods=['PATCH'])
def generate_otp():
    """ Generate an OTP. """
    data = request.get_json()
    otp_schema = OTPGenerationSchema()
    data = otp_schema.load(data)
    auth_service = AuthService()
    email = data.get('email')
    auth_service.generate_otp(email)
    return set_response(200, {'code': 'otp_sent', 'message': 'OTP sent successfully.'})


@auth.route('/v1/auth/verify-otp', methods=['PATCH'])
def verify_otp():
    """ Verify the OTP. """
    data = request.get_json()
    otp_schema = OTPSubmissionFormValidation()
    data = otp_schema.load(data)
    if not data:
        raise MissingFieldsException('Please provide all the required fields')
    auth_service = AuthService()
    email = data.get('email')
    otp = data.get('otp')
    user_id = auth_service.verify_otp(email, otp)
    try:
        token_service = TokenService()
        access_token, refresh_token = token_service.generate_jwt_csrf_token(email=email, user_id=user_id)
        response = set_response(200, messages="OTP Verified")
        set_access_cookies(response, access_token)

        return response

    except Exception as e:  # pylint: disable=W0718
        return set_response(500, {
            'code': 'error',
            'message': str(e)
        })

@auth.route('/v1/auth/set-nickname', methods=['PATCH'])
@jwt_required(optional=False)
def set_nickname():
    """ Set the nickname of the user. """
    data = request.get_json()
    nickname_schema = NicknameFormValidation()
    data = nickname_schema.load(data)
    if not data:
        raise MissingFieldsException('Please provide all the required fields')
    nickname = data.get('nickname')
    if not nickname:
        raise MissingFieldsException('Please provide a nickname.')
    if  len(nickname) < 3:
        pass # Raise custom exception here
    current_user = get_jwt_identity()
    auth_service = AuthService()
    auth_service.set_nickname(email=data.get('email'), nickname=data.get('nickname'))
    return set_response(200, {
        'code': 'success', 'message': 'Nickname set successfully.'
    })
