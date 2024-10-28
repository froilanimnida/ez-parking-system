from flask import Blueprint, request, jsonify
from sqlalchemy.exc import DataError, IntegrityError, DatabaseError, OperationalError
from app.exceptions.authorization_exception import (EmailNotFoundException, InvalidEmailException,
                                                    InvalidPhoneNumberException, PhoneNumberAlreadyTaken,
                                                    EmailAlreadyTaken, MissingFieldsException,
                                                    IncorrectPasswordException, PasswordTooShort)
from app.utils.error_handlers import (handle_email_not_found, handle_email_already_taken, handle_invalid_email,
                                      handle_phone_number_already_taken, handle_invalid_phone_number,
                                      handle_database_errors, handle_general_exception, handle_missing_fields, handle_incorrect_password, handle_password_too_short)
from app.utils.response_util import set_response
from app.services.auth_service import AuthService

auth = Blueprint('auth', __name__)

auth.register_error_handler(EmailNotFoundException, handle_email_not_found)
auth.register_error_handler(EmailAlreadyTaken, handle_email_already_taken)
auth.register_error_handler(InvalidEmailException, handle_invalid_email)
auth.register_error_handler(PhoneNumberAlreadyTaken, handle_phone_number_already_taken)
auth.register_error_handler(InvalidPhoneNumberException, handle_invalid_phone_number)
auth.register_error_handler(MissingFieldsException, handle_missing_fields)
auth.register_error_handler(DatabaseError, handle_database_errors)
auth.register_error_handler(OperationalError, handle_database_errors)
auth.register_error_handler(IntegrityError, handle_database_errors)
auth.register_error_handler(DataError, handle_database_errors)
auth.register_error_handler(IncorrectPasswordException, handle_incorrect_password)
auth.register_error_handler(PasswordTooShort, handle_password_too_short)
auth.register_error_handler(Exception, handle_general_exception)

@auth.route('/create-new-account', methods=['POST'])
def create_new_account():
    data = request.get_json()
    if not data:
        raise MissingFieldsException('Please provide all the required fields')
    auth_service = AuthService()
    response = auth_service.create_new_user(data)
    return set_response(201, {'code': 'success', 'message': 'User created successfully.', 'uuid': response})

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        raise MissingFieldsException('Please provide all the required fields')
    auth_service = AuthService()
    authorization_token = auth_service.login_user(data)
    return set_response(200, {'code': 'success', 'message': 'User logged in successfully.'}, authorization_token=authorization_token)