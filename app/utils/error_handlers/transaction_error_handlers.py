""" Encapsulates error handling for transactions. """

from app.exceptions.transaction_exception import (
    HasExistingReservationException, UserHasNoPlateNumberSetException
)
from app.utils.error_handlers.base_error_handler import handle_error


def handle_has_existing_reservation(error):
    """This function handles existing reservation exceptions."""
    if isinstance(error, HasExistingReservationException):
        return handle_error(
            error,
            400,
            "existing_reservation",
            "User has an existing reservation.",
        )
    raise error

def handle_user_has_no_plate_number_set(error):
    """This function handles no plate number set exceptions."""
    if isinstance(error, UserHasNoPlateNumberSetException):
        return handle_error(
            error,
            400,
            "no_plate_number_set",
            "User has no plate number set.",
        )
    raise error
