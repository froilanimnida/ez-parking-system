"""System-wide error handlers."""

from marshmallow.exceptions import ValidationError
from flask import Flask
from flask_jwt_extended.exceptions import CSRFError
from sqlalchemy.exc import DatabaseError, OperationalError, IntegrityError, DataError

from app.utils.error_handlers.jwt_error_handlers import handle_csrf_error
from app.utils.error_handlers.database_error_handlers import handle_database_errors
from app.utils.error_handlers.validation_error_handlers import handle_validation_errors
from app.utils.error_handlers.general_error_handler import (
    handle_general_exception,
    handle_type_error,
)


def register_system_wide_error_handlers(app: Flask):
    """Register system-wide error handlers."""
    app.register_error_handler(DatabaseError, handle_database_errors)
    app.register_error_handler(OperationalError, handle_database_errors)
    app.register_error_handler(IntegrityError, handle_database_errors)
    app.register_error_handler(DataError, handle_database_errors)
    app.register_error_handler(ValidationError, handle_validation_errors)
    app.register_error_handler(CSRFError, handle_csrf_error)
    app.register_error_handler(TypeError, handle_type_error)
    app.register_error_handler(Exception, handle_general_exception)
