"""Wraps the general, uncaught exceptions in the application."""

from app.exceptions.general_exceptions import FileSizeTooBig
from app.utils.error_handlers.base_error_handler import handle_error

def handle_general_exception(error):
    """This function handles general exceptions."""
    return handle_error(
        error,
        "unexpected_error",
        "An unexpected error occurred. Please try again later.",
        500,
    )


def handle_type_error(error):
    """This function handles type errors."""
    if isinstance(error, TypeError):
        return handle_error(
            error,
            "type_error",
            "Type error occurred.",
            400,
        )
    raise error

def handle_file_size_too_big(error):
    """This function handles file size too big errors."""
    if isinstance(error, FileSizeTooBig):
        return handle_error(
            error,
            "file_size_too_big",
            "File size is too big.",
            400,
        )
    raise error
