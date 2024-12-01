"""
    Encapsulates all exceptions related to transactions
"""


from app.exceptions.ez_parking_base_exception import EzParkingBaseException

class HasExistingReservationException(EzParkingBaseException):
    """
        This error is for error that the user tries to create a reservation
        while having an existing reservation.
    """

    def __init__(self, message="User has an existing reservation."):
        self.message = message
        super().__init__(message)
class UserHasNoPlateNumberSetException(EzParkingBaseException):
    """
        This error is for error that the user tries to create a reservation
        without setting a plate number.
    """

    def __init__(self, message="User has no plate number set."):
        self.message = message
        super().__init__(message)
