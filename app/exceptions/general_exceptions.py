""" General Exceptions Module """

# pylint: disable=R0903

from app.exceptions.ez_parking_base_exception import EzParkingBaseException

class FileSizeTooBig(EzParkingBaseException):
    """File size is too big"""
    def __init__(self, message: str = "File size is too big"):
        """Initialize the exception"""
        super().__init__(message)
