""" Wraps all the exceptions related to slot lookup. """

from app.exceptions.ez_parking_base_exception import EzParkingBaseException


class NoSlotsFoundInTheGivenVehicleType(EzParkingBaseException):
    """
    Custom exception class to handle no slot found in the given vehicle type.
    """

    def __init__(self, message="No slot found in the given vehicle type."):
        self.message = message
        super().__init__(message)


class NoSlotsFoundInTheGivenEstablishment(EzParkingBaseException):
    """
    Custom exception class to handle no slot found in the given establishment.
    """

    def __init__(self, message="No slot found in the given establishment."):
        self.message = message
        super().__init__(message)


class NoSlotsFoundInTheGivenSlotCode(EzParkingBaseException):
    """
    Custom exception class to handle no slot found in the given slot code.
    """

    def __init__(self, message="No slot found in the given slot code."):
        self.message = message
        super().__init__(message)


class SlotNotFound(EzParkingBaseException):
    """
    Custom exception class to handle no slot found.
    """

    def __init__(self, message="Slot not found."):
        self.message = message
        super().__init__(message)

class SlotStatusTaken(EzParkingBaseException):
    """
    Custom exception class to handle slot status taken.
    """

    def __init__(self, message="Slot status is taken."):
        self.message = message
        super().__init__(message)
