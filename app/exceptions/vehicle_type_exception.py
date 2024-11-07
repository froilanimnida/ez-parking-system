""" Wraps all exceptions relevant to the Vehicle Type. """

from app.exceptions.ez_parking_base_exception import EzParkingBaseException


class VehicleTypeDoesNotExist(EzParkingBaseException):
    """
    Exception raised when the specified vehicle type does not exist.

    Attributes:
        message (str): Explanation of the error.
    """

    def __init__(self, message="Vehicle type does not exist."):
        self.message = message
        super().__init__(message)
