"""This module contains error handlers for establishment errors."""

from app.exceptions.establishment_lookup_exceptions import (
    EstablishmentDoesNotExist,
    EstablishmentEditsNotAllowedException,
)
from app.utils.error_handlers.base_error_handler import handle_error


def handle_establishment_does_not_exist(error):
    """This function handles establishment doesn't exist errors."""
    if isinstance(error, EstablishmentDoesNotExist):
        return handle_error(
            error, 404, "establishment_does_not_exist", "Establishment doesn't exist."
        )
    raise error


def handle_establishment_edits_not_allowed(error):
    """This function handles establishment edits not allowed errors."""
    if isinstance(error, EstablishmentEditsNotAllowedException):
        return handle_error(
            error,
            400,
            "establishment_edits_not_allowed",
            "Establishment edits are not allowed.",
        )
    raise error
