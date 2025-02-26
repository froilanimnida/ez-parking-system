"""This module contains the services for the transaction operations."""

from app.exceptions.qr_code_exceptions import QRCodeError, InvalidQRContent
from app.exceptions.slot_lookup_exceptions import SlotStatusTaken
from app.models.address import AddressRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_slot import ParkingSlotRepository, ParkingSlot
from app.models.parking_transaction import ParkingTransactionRepository
from app.models.payment_method import PaymentMethodRepository
from app.models.user import UserRepository
from app.utils.qr_utils.generate_transaction_qr_code import QRCodeUtils
from app.utils.timezone_utils import get_current_time


class TransactionService:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for parking transaction operations"""

    @staticmethod
    def reserve_slot(reservation_data: dict):
        """Reserves the slot for a user."""
        return SlotActionsService.reserve_slot(reservation_data)

    @staticmethod
    def verify_reservation_code(qr_content: str, payment_status: str):
        """Verifies the reservation code for a user."""
        return TransactionVerification.verify_entry_transaction(qr_content, payment_status)

    @staticmethod
    def verify_exit_code(
        qr_content: str, payment_status: str, exit_time: str, amount_due: float, slot_id
    ):
        """Verifies the exit code for a user."""
        return TransactionVerification.verify_exit_transaction(
            qr_content,
            payment_status,
            exit_time,
            amount_due,
            slot_id
        )

    @staticmethod
    def occupy_slot(parking_data):
        """Occupies the slot for a user."""

    @staticmethod
    def release_slot(slot_data):
        """Releases the slot for a user."""

    @staticmethod
    def cancel_transaction(transaction_uuid: str):
        """Cancels the transaction for a user."""
        return SlotActionsService.cancel_transaction(transaction_uuid)

    @staticmethod
    def get_transaction_details_from_qr_code(qr_code_data, user_id):
        """Get the transaction details from a QR code."""
        return TransactionVerification.get_transaction_details_from_qr_code(qr_code_data, user_id)

    @staticmethod
    def view_transaction(transaction_uuid: str):
        """View the transaction for a user."""
        return SlotActionsService.view_transaction(transaction_uuid)

    @staticmethod
    def checkout(establishment_uuid: str, slot_uuid: str, user_id: int):
        """Get the transaction form details for a user."""
        return TransactionFormDetails.checkout(
            establishment_uuid, slot_uuid, user_id
        )
    @staticmethod
    def get_all_user_transactions(user_id):
        """Get all the transactions for a user."""
        return Transaction.get_all_user_transactions(user_id)
    @classmethod
    def get_establishment_transaction(cls, user_id):
        """Get all the transactions for the establishment."""
        return Transaction.get_establishment_transaction(user_id)
    @classmethod
    def get_transaction(cls, transaction_uuid):
        """Get the transaction details."""
        return Transaction.get_transaction(transaction_uuid)

class SlotActionsService:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for slot operations"""

    @staticmethod
    def reserve_slot(slot_reservation_data: dict):
        """Reserves the slot for a user."""
        now = get_current_time()
        slot_uuid = slot_reservation_data.pop("slot_uuid")
        slot_status = ParkingSlotRepository.get_slot(slot_uuid=slot_uuid).get("slot_status")
        if slot_status in ["reserved", "occupied", "closed"]:
            raise SlotStatusTaken("Invalid slot status.")
        slot_reservation_data.update({"slot_id": ParkingSlot.get_id(slot_uuid)})
        slot_reservation_data.update({"created_at": now})
        slot_reservation_data.update({"updated_at": now})
        ParkingTransactionRepository.create_transaction(slot_reservation_data)
        return ParkingSlotRepository.change_slot_status(slot_uuid=slot_uuid, new_status="reserved")

    @staticmethod
    def release_slot(slot_data):
        """Releases the slot for a user."""

    @staticmethod
    def cancel_transaction(transaction_uuid: str):
        """Cancels the transaction for a user."""
        slot_id = ParkingTransactionRepository.get_transaction(
            transaction_uuid=transaction_uuid
        ).get("slot_id")
        ParkingTransactionRepository.update_transaction_status(
            transaction_uuid, "cancelled"
        )
        return ParkingSlotRepository.change_slot_status(slot_id=slot_id, new_status="open")

    @staticmethod
    def view_transaction(transaction_uuid: str):
        """View the transaction for a user."""
        transaction_data = ParkingTransactionRepository.get_transaction(
            transaction_uuid=transaction_uuid
        )
        slot_info = ParkingSlotRepository.get_slot(
            slot_id=transaction_data.get("slot_id")
        )
        establishment_info = ParkingEstablishmentRepository.get_establishment(
            establishment_id=slot_info.get("establishment_id")
        )
        company_profile = CompanyProfileRepository.get_company_profile(
            profile_id=establishment_info.get("profile_id")
        )
        owner_user_id = company_profile.get("user_id")
        contact_number = UserRepository.get_user(user_id=owner_user_id).get("contact_number")
        establishment_profile_id = company_profile.get("profile_id")
        address_info = AddressRepository.get_address(profile_id=establishment_profile_id)
        user_plate_number = UserRepository.get_user(
            user_id=transaction_data.get("user_id")
        ).get("plate_number")
        returned_data = {}
        if transaction_data.get("status") in ["active", "reserved"]:
            qr_code_utils = QRCodeUtils()
            qr_data = qr_code_utils.generate_qr_content({
                "uuid": transaction_data.get("uuid"),
                "status": transaction_data.get("status"),
                "plate_number": user_plate_number,
                "establishment_uuid": establishment_info.get("uuid"),
            })
            base64_image = qr_code_utils.generate_qr_code(qr_data)
            returned_data.update({"qr_code": base64_image})
        returned_data.update({
            "transaction_data": transaction_data,
            "establishment_info": establishment_info,
            "slot_info": slot_info,
            "user_plate_number": user_plate_number,
            "address_info": address_info,
            "contact_number": contact_number,
        })
        return returned_data

class TransactionVerification:
    """Wraps the service actions for transaction verification operations"""

    @staticmethod
    def verify_entry_transaction(transaction_qr_code_data, payment_status):
        """Verifies the entry transaction for a user."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(transaction_qr_code_data)
        if transaction_data.get("status") != "reserved":
            raise QRCodeError("Invalid transaction status.")
        transaction_uuid = transaction_data.get("uuid")
        return ParkingTransactionRepository.update_transaction(transaction_uuid, update_data={
            "payment_status": payment_status,
            "entry_time": get_current_time(),
            "status": "active"
        })

    @staticmethod
    def verify_exit_transaction(qr_content, payment_status, exit_time, amount_due, slot_id):
        """Verifies the exit transaction for a user."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(qr_content)
        print(transaction_data)
        if transaction_data.get("status") != "active":
            raise QRCodeError("Invalid transaction status.")
        ParkingSlotRepository.change_slot_status(slot_id=slot_id, new_status="open")
        return ParkingTransactionRepository.update_transaction(
            transaction_data.get("uuid"),
            update_data={
                "payment_status": payment_status,
                "exit_time": exit_time,
                "status": "completed",
                "amount_due": amount_due
            }
        )

    @staticmethod
    def get_transaction_details_from_qr_code(qr_code_data, manager_id):
        """Get the transaction details from a QR code."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(qr_code_data)
        transaction_uuid = transaction_data.get("uuid")
        establishment_uuid = transaction_data.get("establishment_uuid")
        establishment_info = ParkingEstablishmentRepository.get_establishment(
            establishment_uuid=establishment_uuid
        )
        user_id = CompanyProfileRepository.get_company_profile(
            profile_id=establishment_info.get("profile_id")
        ).get("user_id")
        if manager_id != user_id:
            raise InvalidQRContent("Invalid QR code content, the establishment does not match.")
        transaction_data = ParkingTransactionRepository.get_transaction(
            transaction_uuid=transaction_uuid
        )
        parking_slot_info = ParkingSlotRepository.get_slot(
            slot_id=transaction_data.get("slot_id")
        )
        user_info = UserRepository.get_user(user_id=transaction_data.get("user_id"))
        return {
            "user_info": user_info,
            "transaction_data": transaction_data,
            "parking_slot_info": parking_slot_info,
        }


class TransactionFormDetails:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for transaction form details operations"""

    @staticmethod
    def checkout(establishment_uuid: str, slot_uuid: str, user_id: int):
        """
        Get the transaction form details for a user.

        Args:
            establishment_uuid (str): UUID of the establishment
            slot_uuid (str): Slot code identifier
            user_id (int): User ID

        Raises:
            SlotStatusTaken: If slot is not available
            ValueError: If UUID format is invalid
        """
        status = ParkingSlotRepository().get_slot(slot_uuid=slot_uuid).get("status")
        if status in ["reserved", "occupied"]:
            raise SlotStatusTaken("Invalid slot status.")
        user_ongoing_transaction = ParkingTransactionRepository.is_user_have_an_ongoing_transaction(
            user_id
        )
        establishment_info = ParkingEstablishmentRepository.get_establishment(
            establishment_uuid=establishment_uuid
        )
        establishment_id = establishment_info.get("establishment_id")
        profile_id = establishment_info.get("profile_id")
        address = AddressRepository.get_address(profile_id=profile_id)
        operating_hours = OperatingHoursRepository.get_operating_hours(establishment_id)
        payment_methods = PaymentMethodRepository.get_payment_methods(establishment_id)
        slot_info = ParkingSlotRepository.get_slot(slot_uuid=slot_uuid)
        return {
            "establishment_info": establishment_info,
            "address": address,
            "operating_hours": operating_hours,
            "payment_methods": payment_methods,
            "slot_info": slot_info,
            "has_ongoing_transaction": user_ongoing_transaction
        }


class Transaction:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for transaction operations"""

    @staticmethod
    def get_all_user_transactions(user_id):
        """Get all the transactions for a user."""
        return ParkingTransactionRepository.get_all_transactions(user_id=user_id)
    @classmethod
    def get_establishment_transaction(cls, user_id):
        """Get all the transactions for the establishment."""
        profile_id = CompanyProfileRepository.get_company_profile(user_id=user_id).get("profile_id")
        establishment_id = ParkingEstablishmentRepository.get_establishment(
            profile_id=profile_id
        ).get("establishment_id")
        parking_slots = ParkingSlotRepository.get_slots(establishment_id=establishment_id)
        parking_slots_id = [slot.get("slot_id") for slot in parking_slots]
        transactions = []
        for slot_id in parking_slots_id:
            # transactions.append(ParkingTransactionRepository.get_all_transactions(
            # slot_id=slot_id
            # ))
            transaction = ParkingTransactionRepository.get_all_transactions(slot_id=slot_id)
            if transaction:
                transactions.append(transaction)
        return transactions
    @classmethod
    def get_transaction(cls, transaction_uuid):
        """Get the transaction details."""
        transaction = ParkingTransactionRepository.get_transaction(
            transaction_uuid=transaction_uuid
        )
        slot_info = ParkingSlotRepository.get_slot(slot_id=transaction.get("slot_id"))
        user_info = UserRepository.get_user(user_id=transaction.get("user_id"))
        return {
            "transaction": transaction,
            "slot_info": slot_info,
            "user_info": user_info
        }
