"""
            This exception files contains exceptions that are
            related to the authorization of the user.
    """
from app.exceptions.ez_parking_base_exception import EzParkingBaseException


class EmailNotFoundException(EzParkingBaseException):
    """
        This error is for error that the user tries to log in with an email that
        doesn't exist on the database.
    """

    def __init__(self, message="Email not found."):
        self.message = message
        super().__init__(message)

class MissingFieldsException(EzParkingBaseException):
    """
        This error is for error that the user tries to log in without the required fields.
    """

    def __init__(self, message="Please provide all the required fields."):
        self.message = message
        super().__init__(message)


class EmailAlreadyTaken(EzParkingBaseException):
    """
        This is for error that will be raised when the user creates an account
        with an email that is already taken. A bit redundant, but it will be
        beneficial for custom errors rather than SQL Generic Errors on
        Primary keys. Additionally, this approach will ultimately lay off the
        exception on the API Level, further reducing the load for database.
    """

    def __init__(self, message="Email already taken."):
        self.message = message
        super().__init__(message)


class PhoneNumberAlreadyTaken(EzParkingBaseException):
    """
        This is for error that will be raised when the user creates an account
        with a phone number that is already taken. A bit redundant, but it will be
        beneficial for custom errors rather than SQL Generic Errors on
        Primary keys. Additionally, this approach will ultimately lay off the
        exception on the API Level, further reducing the load for database.
    """

    def __init__(self, message="Phone number already taken."):
        self.message = message
        super().__init__(message)


class InvalidPhoneNumberException(EzParkingBaseException):
    """
        This error is for error that the user tries to log in with a phone number that
        is invalid.
    """

    def __init__(self, message="Phone number is invalid."):
        self.message = message
        super().__init__(message)


class IncorrectOTPException(EzParkingBaseException):
    """
        This error is for error that the user tries to log in with an incorrect OTP.
    """

    def __init__(self, message="Incorrect OTP."):
        self.message = message
        super().__init__(message)

class ExpiredOTPException(EzParkingBaseException):
    """
        This error is for error that the user tries to log in with an expired OTP.
    """

    def __init__(self, message="Expired OTP."):
        self.message = message
        super().__init__(message)

class RequestNewOTPException(EzParkingBaseException):
    """
        This error is for error that the user tries to log in with an expired OTP.
    """

    def __init__(self, message="Please request a new OTP."):
        self.message = message
        super().__init__(message)


class BannedUserException(EzParkingBaseException):
    """
        This error is for error that the user tries to log in with a banned account.
    """

    def __init__(self, message="User is banned."):
        self.message = message
        super().__init__(message)
