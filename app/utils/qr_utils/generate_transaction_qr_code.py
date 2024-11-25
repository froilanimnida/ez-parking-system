""" QR Code generation and verification utilities for parking transactions. """

from datetime import datetime
from base64 import urlsafe_b64encode, urlsafe_b64decode
from json import dumps, loads
from hashlib import sha256
import hmac

from app.config.base_config import BaseConfig
from app.exceptions.qr_code_exceptions import InvalidQRContent, InvalidTransactionStatus


class QRCodeUtils:
    """Handles generation and verification of QR codes for parking transactions."""

    VALID_STATUSES = {"reserved", "active"}

    def generate_qr_content(self, data: dict[str, str]) -> str:
        """
        Generate the QR content for a parking transaction.

        Args:
            data: Dictionary containing transaction data (uuid, status, plate_number)

        Returns:
            str: Base64 encoded QR content
        """
        status = data.get("status")
        if status not in self.VALID_STATUSES:
            raise InvalidTransactionStatus(f"Invalid status: {status}")

        # Create payload with status
        payload = {
            "uuid": data.get("uuid"),
            "status": status,
            "plate": data.get("plate_number"),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Generate HMAC signature
        uuid = payload["uuid"]
        status = payload["status"]
        plate = payload["plate"]
        timestamp = payload["timestamp"]
        payload_str = f"{uuid}:{status}:{plate}:{timestamp}"
        signature = hmac.new(
            BaseConfig.ENCRYPTION_KEY.encode(), payload_str.encode(), sha256
        ).hexdigest()

        payload["signature"] = signature
        return urlsafe_b64encode(dumps(payload).encode()).decode()

    @staticmethod
    def verify_qr_content(qr_content: str) -> dict[str, str] | None:
        """
        Verify the QR content signature and status.

        Args:
            qr_content: Base64 encoded QR content string

        Returns:
            Optional[Dict]: Decoded payload if valid, None if invalid

        Raises:
            InvalidQRContent: If QR content is invalid or tampered
        """
        try:
            decoded = loads(urlsafe_b64decode(qr_content.encode()))

            uuid = decoded["uuid"]
            status = decoded["status"]
            plate = decoded["plate"]
            timestamp = decoded["timestamp"]
            payload_str = f"{uuid}:{status}:{plate}:{timestamp}"

            expected_sig = hmac.new(
                BaseConfig.ENCRYPTION_KEY.encode(), payload_str.encode(), sha256
            ).hexdigest()

            if not hmac.compare_digest(decoded["signature"], expected_sig):
                raise InvalidQRContent("Invalid signature")

            if decoded["status"] not in QRCodeUtils.VALID_STATUSES:
                raise InvalidQRContent("Invalid transaction status")

            return decoded

        except Exception as e:
            raise InvalidQRContent(f"Failed to verify QR content: {str(e)}") from e

    @staticmethod
    def is_valid_status(status: str) -> bool:
        """Check if the transaction status is valid for QR operations."""
        return status in QRCodeUtils.VALID_STATUSES
