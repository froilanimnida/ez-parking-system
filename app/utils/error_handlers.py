""" This module contains error handlers for the application. """

from logging import getLogger

from sqlalchemy.exc import DataError, IntegrityError, DatabaseError, OperationalError
from marshmallow.exceptions import ValidationError
from flask_jwt_extended.exceptions import (
    CSRFError, NoAuthorizationError, JWTDecodeError, WrongTokenError, RevokedTokenError,
    UserClaimsVerificationError, UserLookupError, InvalidHeaderError,InvalidQueryParamError,
    FreshTokenRequired
)
from app.exceptions.authorization_exception import (
    EmailNotFoundException, MissingFieldsException, InvalidEmailException, InvalidPhoneNumberException,
    PhoneNumberAlreadyTaken, EmailAlreadyTaken, PasswordTooShort, IncorrectPasswordException,
    IncorrectOTPException, ExpiredOTPException
)
from app.exceptions.slot_lookup_exceptions import (
    NoSlotsFoundInTheGivenSlotCode, NoSlotsFoundInTheGivenEstablishment, NoSlotsFoundInTheGivenVehicleType
)
from app.utils.response_util import set_response

logger = getLogger(__name__)

def handle_database_errors(error):
    """ This function handles database errors. """
    if isinstance(error, (IntegrityError, DataError, DatabaseError, OperationalError)):
        logger.error("Database error: %s", error)
        return set_response(500, {
            'code': 'server_error',
            'message': 'A database error occurred. Please try again later.'
        })
    raise error

def handle_general_exception(error):
    """ This function handles general exceptions. """
    logger.error("General exception: %s", error)
    return set_response(500, {
        'code': 'unexpected_error',
        'message': 'An unexpected error occurred. Please try again later.'
    })


def handle_email_not_found(error):
    """ This function handles email not found exceptions. """
    if isinstance(error, EmailNotFoundException):
        logger.error("Email not found: %s", error)
        return set_response(404, {
            'code': 'email_not_found',
            'message': 'Email not found.'
        })
    raise error

def handle_missing_fields(error):
    """ This function handles missing fields exceptions. """
    if isinstance(error, MissingFieldsException):
        logger.error("Missing fields: %s", error)
        return set_response(400, {
            'code': 'missing_fields',
            'message': 'Please provide all the required fields.'
        })
    raise error

def handle_invalid_email(error):
    """ This function handles invalid email exceptions. """
    if isinstance(error, InvalidEmailException):
        logger.error("Invalid email: %s", error)
        return set_response(400, {
            'code': 'invalid_email',
            'message': 'Please provide a valid email address.'
        })
    raise error

def handle_invalid_phone_number(error):
    """ This function handles invalid phone number exceptions. """
    if isinstance(error, InvalidPhoneNumberException):
        logger.error("Invalid phone number: %s", error)
        return set_response(400, {
            'code': 'invalid_phone_number',
            'message': 'Please provide a valid phone number.'
        })
    raise error

def handle_email_already_taken(error):
    """ This function handles email already taken exceptions. """
    if isinstance(error, EmailAlreadyTaken):
        logger.error("Email already taken: %s", error)
        return set_response(400, {
            'code': 'email_already_taken',
            'message': 'Email already taken.'
        })
    raise error

def handle_phone_number_already_taken(error):
    """ This function handles phone number already taken exceptions. """
    if isinstance(error, PhoneNumberAlreadyTaken):
        logger.error("Phone number already taken: %s", error)
        return set_response(400, {
            'code': 'phone_number_already_taken',
            'message': 'Phone number already taken.'
        })
    raise error

def handle_password_too_short(error):
    """ This function handles password too short exceptions. """
    if isinstance(error, PasswordTooShort):
        logger.error("Password too short: %s", error)
        return set_response(400, {
            'code': 'password_too_short',
            'message': 'Password must be at least 8 characters long.'
        })
    raise error

def handle_incorrect_password(error):
    """ This function handles incorrect password exceptions. """
    if isinstance(error, IncorrectPasswordException):
        logger.error("Incorrect password: %s", error)
        return set_response(400, {
            'code': 'incorrect_password',
            'message': 'Incorrect password.'
        })
    raise error

def handle_incorrect_otp(error):
    """ This function handles incorrect OTP exceptions. """
    if isinstance(error, IncorrectOTPException):
        logger.error("Incorrect OTP: %s", error)
        return set_response(400, {
            'code': 'incorrect_otp',
            'message': 'Incorrect OTP.'
        })
    raise error

def handle_expired_otp(error):
    """ This function handles expired OTP exceptions. """
    if isinstance(error, ExpiredOTPException):
        logger.error("Expired OTP: %s", error)
        return set_response(400, {
            'code': 'expired_otp',
            'message': 'Expired OTP.'
        })
    raise error

def handle_no_slots_found_in_the_given_slot_code(error):
    """ This function handles no slots found in the given slot code exceptions. """
    if isinstance(error, NoSlotsFoundInTheGivenSlotCode):
        logger.error("No slots found in the given slot code: %s", error)
        return set_response(404, {
            'code': 'no_slots_found_in_the_given_slot_code',
            'message': 'No slots found in the given slot code.'
        })
    raise error

def handle_no_slots_found_in_the_given_establishment(error):
    """ This function handles no slots found in the given establishment exceptions. """
    if isinstance(error, NoSlotsFoundInTheGivenEstablishment):
        logger.error("No slots found in the given establishment: %s", error)
        return set_response(404, {
            'code': 'no_slots_found_in_the_given_establishment',
            'message': 'No slots found in the given establishment.'
        })
    raise error

def handle_no_slots_found_in_the_given_vehicle_type(error):
    """ This function handles no slots found in the given vehicle type exceptions. """
    if isinstance(error, NoSlotsFoundInTheGivenVehicleType):
        logger.error("No slots found in the given vehicle type: %s", error)
        return set_response(404, {
            'code': 'no_slots_found_in_the_given_vehicle_type',
            'message': 'No slots found in the given vehicle type.'
        })
    raise error

def handle_validation_errors(error):
    """ This function handles validation errors. """
    if isinstance(error, ValidationError):
        logger.error("Validation error: %s", error)
        return set_response(400, {
            'code': 'validation_error',
            'message': 'Validation error. Please provide valid data'
        })
    raise error

def handle_csrf_error(error):
    """ This function handles CSRF errors. """
    if isinstance(error, CSRFError):
        logger.error("CSRF error: %s", error)
        return set_response(400, {
            'code': 'csrf_error',
            'message': 'CSRF error.'
        })
    raise error

def handle_no_authorization_error(error):
    """ This function handles no authorization errors. """
    if isinstance(error, NoAuthorizationError):
        logger.error("No authorization error: %s", error)
        return set_response(401, {
            'code': 'no_authorization_error',
            'message': 'No authorization error.'
        })
    raise error

def handle_jwt_decode_error(error):
    """ This function handles JWT decode errors. """
    if isinstance(error, JWTDecodeError):
        logger.error("JWT decode error: %s", error)
        return set_response(400, {
            'code': 'jwt_decode_error',
            'message': 'JWT decode error.'
        })
    raise error

def handle_wrong_token_error(error):
    """ This function handles wrong token errors. """
    if isinstance(error, WrongTokenError):
        logger.error("Wrong token error: %s", error)
        return set_response(400, {
            'code': 'wrong_token_error',
            'message': 'Wrong token error.'
        })
    raise error

def handle_revoked_token_error(error):
    """ This function handles revoked token errors. """
    if isinstance(error, RevokedTokenError):
        logger.error("Revoked token error: %s", error)
        return set_response(400, {
            'code': 'revoked_token_error',
            'message': 'Revoked token error.'
        })
    raise error

def handle_user_claims_verification_error(error):
    """ This function handles user claims verification errors. """
    if isinstance(error, UserClaimsVerificationError):
        logger.error("User claims verification error: %s", error)
        return set_response(400, {
            'code': 'user_claims_verification_error',
            'message': 'User claims verification error.'
        })
    raise error

def handle_user_lookup_error(error):
    """ This function handles user lookup errors. """
    if isinstance(error, UserLookupError):
        logger.error("User lookup error: %s", error)
        return set_response(400, {
            'code': 'user_lookup_error',
            'message': 'User lookup error.'
        })
    raise error

def handle_invalid_header_error(error):
    """ This function handles invalid header errors. """
    if isinstance(error, InvalidHeaderError):
        logger.error("Invalid header error: %s", error)
        return set_response(400, {
            'code': 'invalid_header_error',
            'message': 'Invalid header error.'
        })
    raise error

def handle_invalid_query_param_error(error):
    """ This function handles invalid query param errors. """
    if isinstance(error, InvalidQueryParamError):
        logger.error("Invalid query param error: %s", error)
        return set_response(400, {
            'code': 'invalid_query_param_error',
            'message': 'Invalid query param error.'
        })
    raise error

def handle_fresh_token_required(error):
    """ This function handles fresh token required errors. """
    if isinstance(error, FreshTokenRequired):
        logger.error("Fresh token required error: %s", error)
        return set_response(400, {
            'code': 'fresh_token_required_error',
            'message': 'Fresh token required error.'
        })
    raise error