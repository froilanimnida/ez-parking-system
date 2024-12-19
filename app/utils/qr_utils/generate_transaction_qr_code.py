""" QR Code generation and verification utilities for parking transactions. """

# pylint: disable=R0914

import hmac
from base64 import b64encode, urlsafe_b64encode, urlsafe_b64decode
from datetime import datetime, timedelta
from hashlib import sha256
from io import BytesIO
from json import dumps, loads
from os import urandom
from re import match

import pytz
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer

from app.config.base_config import BaseConfig
from app.exceptions.qr_code_exceptions import (
    InvalidQRContent,
    InvalidTransactionStatus,
    QRCodeExpired,
)


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
        current_time = datetime.now(pytz.timezone("Asia/Manila"))
        payload = {
            "uuid": data.get("uuid"),
            "establishment_uuid": data.get("establishment_uuid"),
            "status": status,
            "plate": data.get("plate_number"),
            "timestamp": current_time.isoformat(),
            "expires_at": (current_time + timedelta(minutes=15)).isoformat(),
            "version": "1.0",
            "nonce": urlsafe_b64encode(urandom(8)).decode(),
        }

        fields_to_sign = [
            payload["uuid"],
            payload["status"],
            payload["plate"],
            payload["timestamp"],
            payload["expires_at"],
            payload["version"],
            payload["nonce"],
        ]

        payload_str = ":".join(fields_to_sign)
        signature = hmac.new(
            BaseConfig.ENCRYPTION_KEY.encode(), payload_str.encode(), sha256
        ).hexdigest()

        payload["signature"] = signature
        return urlsafe_b64encode(dumps(payload).encode()).decode()

    @staticmethod
    def verify_qr_content(
        qr_content: str,
    ) -> dict[str, str] | None:
        """
        Verify the QR content signature and status.

        Args:
            qr_content: Base64 encoded QR content string

        Returns:
            Optional[Dict]: Decoded payload if valid, None if invalid

        Raises:
            InvalidQRContent: If QR content is invalid or tampered
        """
        BASE64_PATTERN = r"^[A-Za-z0-9_-]+={0,2}$"  # pylint: disable=C0103
        if not match(BASE64_PATTERN, qr_content):
            raise InvalidQRContent("Invalid base64 format")

        try:
            if len(qr_content) < 100 or len(qr_content) > 1024:
                raise InvalidQRContent("Invalid QR content length")

            decoded = loads(urlsafe_b64decode(qr_content.encode()))

            required_fields = {"uuid", "status", "plate", "timestamp", "signature"}
            if not all(field in decoded for field in required_fields):
                raise InvalidQRContent("Missing required fields")

            if not all(isinstance(decoded[field], str) for field in required_fields):
                raise InvalidQRContent("Invalid field types")

            uuid = decoded["uuid"]
            status = decoded["status"]
            plate = decoded["plate"]
            timestamp = decoded["timestamp"]
            expires_at = decoded["expires_at"]
            version = decoded["version"]
            nonce = decoded["nonce"]

            fields_to_verify = [
                uuid,
                status,
                plate,
                timestamp,
                expires_at,
                version,
                nonce,
            ]

            payload_str = ":".join(fields_to_verify)

            expected_sig = hmac.new(
                BaseConfig.ENCRYPTION_KEY.encode(), payload_str.encode(), sha256
            ).hexdigest()

            expires_at_dt = datetime.fromisoformat(expires_at)
            current_time = datetime.now(pytz.timezone("Asia/Manila"))

            if not hmac.compare_digest(decoded["signature"], expected_sig):
                raise InvalidQRContent("Invalid signature")

            if decoded["status"] not in QRCodeUtils.VALID_STATUSES:
                raise InvalidQRContent("Invalid transaction status")

            if current_time > expires_at_dt:
                raise QRCodeExpired("QR code has expired")

            if version != "1.0":
                raise InvalidQRContent("Invalid version")

            if not match(r"^[A-Za-z0-9_-]{11,12}=*$", nonce):
                raise InvalidQRContent("Invalid nonce")

            return decoded

        except Exception as e:
            raise InvalidQRContent(f"Failed to verify QR content: {str(e)}") from e

    @staticmethod
    def is_valid_status(status: str) -> bool:
        """Check if the transaction status is valid for QR operations."""
        return status in QRCodeUtils.VALID_STATUSES

    def generate_qr_code(self, data: str) -> str:
        """
        Generate a QR code image for the given data.

        Args:
            data: Data to encode in the QR code

        Returns:
            str: Base64 encoded image data
        """
        qr = QRCode(
            version=25,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(
            fill_color="black",
            back_color="white",
            image_factory=StyledPilImage,
            module_drawer=CircleModuleDrawer(),
        )
        img_byte_arr = BytesIO()
        qr_image.save(img_byte_arr, bitmap_format="png")  # type: ignore
        img_byte_arr = img_byte_arr.getvalue()
        return b64encode(img_byte_arr).decode()
