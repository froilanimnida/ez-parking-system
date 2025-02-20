"""
    This exception files contains exceptions that are
    related QR Code Verification.
"""

from app.exceptions.ez_parking_base_exception import EzParkingBaseException


class QRCodeError(EzParkingBaseException):
    """Base exception for QR code operations."""

    def __init__(self, message="QR code error."):
        self.message = message
        super().__init__(message)


class InvalidQRContent(EzParkingBaseException):
    """Raised when QR content is invalid."""

    def __init__(
        self,
        message="The QR Code transaction is invalid or belongs to other establishment."):
        self.message = message
        super().__init__(message)


class InvalidTransactionStatus(EzParkingBaseException):
    """Raised when transaction status is invalid for QR operations."""

    def __init__(self, message="Invalid transaction status."):
        self.message = message
        super().__init__(message)


class QRCodeExpired(EzParkingBaseException):
    """Raised when QR code has expired."""

    def __init__(
        self,
        message="QR code has expired. Please instruct the user to refresh the transaction page.",
    ):
        self.message = message
        super().__init__(message)
