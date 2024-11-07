""" Wraps the establishment related exception handling. """

from app.exceptions.ez_parking_base_exception import EzParkingBaseException


class EstablishmentDoesNotExist(EzParkingBaseException):
    """Exception raised when the establishment does not exist."""

    def __init__(self, message="Establishment does not exist."):
        self.message = message
        super().__init__(message)


class EstablishmentEditsNotAllowedException(EzParkingBaseException):
    """Exception raised when the establishment edits are not allowed.
    For instance the manager_id is not align with the entry and establishment id.
    But this exception overrides if the role of the current request identity
    is an admin.
    """

    def __init__(self, message="Establishment edits are not allowed"):
        self.message = message
        super().__init__(message)
