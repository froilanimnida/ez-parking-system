"""This module contains the services for the transaction operations."""

import io
from base64 import b64encode
from datetime import datetime
from uuid import uuid4

import qrcode
import qrcode.constants

from app.exceptions.qr_code_exceptions import QRCodeError
from app.exceptions.slot_lookup_exceptions import SlotStatusTaken
from app.models.parking_establishment import GetEstablishmentOperations
from app.models.parking_transaction import (
    ParkingTransactionOperation,
    UpdateTransaction,
)
from app.models.slot import GettingSlotsOperations, TransactionOperation
from app.models.user import UserOperations
from app.models.vehicle_type import VehicleTypeOperations
from app.utils.qr_utils.generate_transaction_qr_code import QRCodeUtils
from app.utils.uuid_utility import UUIDUtility


class TransactionService:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for parking transaction operations"""

    @staticmethod
    def reserve_slot(reservation_data):
        """Reserves the slot for a user."""
        return SlotActionsService.reserve_slot(reservation_data)

    @staticmethod
    def verify_reservation_code(reservation_code):
        """Verifies the reservation code for a user."""
        return TransactionVerification.verify_entry_transaction(reservation_code)

    @staticmethod
    def verify_exit_code(exit_code):
        """Verifies the exit code for a user."""
        return TransactionVerification.verify_exit_transaction(exit_code)

    @staticmethod
    def occupy_slot(parking_data):
        """Occupies the slot for a user."""

    @staticmethod
    def release_slot(slot_data):
        """Releases the slot for a user."""

    @staticmethod
    def cancel_transaction(transaction_id):
        """Cancels the transaction for a user."""
        return SlotActionsService.cancel_transaction(transaction_id)

    @staticmethod
    def view_transaction(transaction_uuid):
        """View the transaction for a user."""
        return SlotActionsService.view_transaction(transaction_uuid)

    @staticmethod
    def get_transaction_form_details(establishment_uuid: str, slot_code: str):
        """Get the transaction form details for a user."""
        return TransactionFormDetails.get_transaction_form_details(
            establishment_uuid, slot_code
        )

    @staticmethod
    def get_all_user_transactions(user_id):
        """Get all the transactions for a user."""
        return Transaction.get_all_user_transactions(user_id)


class SlotActionsService:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for slot operations"""

    @staticmethod
    def reserve_slot(slot_reservation_data):
        """Reserves the slot for a user."""
        now = datetime.now()
        slot_reservation_data.update({"uuid": uuid4().bytes})
        slot_reservation_data.update({"created_at": now})
        slot_reservation_data.update({"updated_at": now})
        return ParkingTransactionOperation.add_new_transaction_entry(
            slot_reservation_data
        )

    @staticmethod
    def occupy_slot(slot_data):
        """Occupies the slot for a user."""

    @staticmethod
    def release_slot(slot_data):
        """Releases the slot for a user."""

    @staticmethod
    def cancel_transaction(transaction_id):
        """Cancels the transaction for a user."""
        return UpdateTransaction.cancel_transaction(transaction_id)

    @staticmethod
    def view_transaction(transaction_id):
        """View the transaction for a user."""
        transaction_data = ParkingTransactionOperation.get_transaction(transaction_id)
        qr_code_utils = QRCodeUtils()
        qr_data = qr_code_utils.generate_qr_content(
            data={
                "uuid": transaction_data.get("uuid"),
                "status": transaction_data.get("status"),
                "plate_number": transaction_data.get("plate_number"),
            }  # type: ignore
        )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = io.BytesIO()
        qr_image.save(img_byte_arr, bitmap_format="png")  # type: ignore
        img_byte_arr = img_byte_arr.getvalue()
        base64_image = b64encode(img_byte_arr).decode()
        return {"transaction_data": transaction_data, "qr_code": base64_image}


class TransactionVerification:
    """Wraps the service actions for transaction verification operations"""

    @staticmethod
    def verify_entry_transaction(transaction_qr_code_data):
        """Verifies the entry transaction for a user."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(transaction_qr_code_data)
        if transaction_data.get("status") != "reserved":  # type: ignore
            raise QRCodeError("Invalid transaction status.")
        return UpdateTransaction.update_transaction_status(
            "active", transaction_data.get("uuid")  # type: ignore
        )

    @staticmethod
    def verify_exit_transaction(transaction_qr_code_data):
        """Verifies the exit transaction for a user."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(transaction_qr_code_data)
        if transaction_data.get("status") != "active":  # type: ignore
            raise QRCodeError("Invalid transaction status.")


class TransactionFormDetails:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for transaction form details operations"""

    @staticmethod
    def get_transaction_form_details(establishment_uuid: str, slot_code: str):
        """
        Get the transaction form details for a user.

        Args:
            establishment_uuid (str): UUID string of establishment
            slot_code (str): Slot code identifier

        Raises:
            SlotStatusTaken: If slot is not available
            ValueError: If UUID format is invalid
        """
        status = GettingSlotsOperations.get_slot_status(slot_code)
        if status in ["reserved", "occupied"]:
            raise SlotStatusTaken("Invalid slot status.")

        uuid_utility = UUIDUtility()
        establishment_uuid = establishment_uuid.strip()

        if "-" not in establishment_uuid:
            establishment_uuid = uuid_utility.format_uuid(establishment_uuid)

        # Convert to binary
        establishment_uuid_bin = uuid_utility.uuid_to_binary(establishment_uuid)

        establishment_info = GetEstablishmentOperations.get_establishment_id_by_uuid(
            establishment_uuid_bin
        )
        print(establishment_info)

        return TransactionOperation.get_slot_establishment_info(
            establishment_uuid_bin, slot_code
        )


class Transaction:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for transaction operations"""

    @staticmethod
    def get_all_user_transactions(user_id):
        """Get all the transactions for a user."""
        transaction_details = ParkingTransactionOperation.get_transaction_by_plate_number(
            UserOperations.get_user_plate_number(user_id)
        )
        slot_information = GettingSlotsOperations.get_slot_by_slot_id(
            transaction_details.get("slot_id")
        )
        vehicle_type_information = VehicleTypeOperations.get_vehicle_type_by_id(
            transaction_details.get("vehicle_type_id")
        )
        return {
            "transaction_details": transaction_details,
            "slot_information": slot_information,
            "vehicle_type_information": vehicle_type_information,
        }
