""" Returns tailored response for qr related errors. """

from app.exceptions.qr_code_exceptions import InvalidQRContent, InvalidTransactionStatus

from app.utils.error_handlers.base_error_handler import handle_error


def handle_invalid_qr_content(error):
    """This function handles invalid QR content exceptions."""
    if isinstance(error, InvalidQRContent):
        return handle_error(
            error,
            400,
            "invalid_qr_content",
            "The QR code content is invalid.",
        )
    raise error


def handle_invalid_transaction_status(error):
    """This function handles invalid transaction status exceptions."""
    if isinstance(error, InvalidTransactionStatus):
        return handle_error(
            error,
            400,
            "invalid_transaction_status",
            "The transaction status is invalid.",
        )
    raise error
