""" This module contains error handlers for the application. """
from logging import getLogger
from os import getenv
from sqlalchemy.exc import DataError, IntegrityError, DatabaseError, OperationalError
from app.exceptions.authorization_exception import (EmailNotFoundException, MissingFieldsException, InvalidEmailException, InvalidPhoneNumberException, PhoneNumberAlreadyTaken, EmailAlreadyTaken)
from app.utils.response_util import set_response

logger = getLogger(__name__)
ENVIRONMENT = getenv('ENVIRONMENT', 'development')
is_production = ENVIRONMENT == 'production'

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


