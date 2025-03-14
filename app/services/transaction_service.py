"""This module contains the services for the transaction operations."""

# pylint: disable=too-many-arguments, too-many-positional-arguments

from datetime import datetime, timedelta

from flask import render_template

from app.exceptions.authorization_exceptions import BannedUserException
from app.exceptions.qr_code_exceptions import QRCodeError, InvalidQRContent
from app.exceptions.slot_lookup_exceptions import SlotStatusTaken
from app.models.address import AddressRepository
from app.models.ban_user import BanUserRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_slot import ParkingSlotRepository, ParkingSlot
from app.models.parking_transaction import ParkingTransactionRepository
from app.models.payment_method import PaymentMethodRepository
from app.models.user import UserRepository
from app.tasks import send_mail
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
        qr_content: str,
        payment_status: str,
        exit_time: str,
        amount_due: float,
        slot_id,
        overstayed_for_more_than_1_hour: bool
    ):
        """Verifies the exit code for a user."""
        return TransactionVerification.verify_exit_transaction(
            qr_content,
            payment_status,
            exit_time,
            amount_due,
            slot_id,
            overstayed_for_more_than_1_hour
        )
    @staticmethod
    def get_latest_exit_transaction(user_id):
        """Get the latest exit transaction for a user."""
        return Transaction.get_latest_exit_transaction(user_id)

    @staticmethod
    def cancel_transaction(transaction_uuid: str, user_id: int):
        """Cancels the transaction for a user."""
        return SlotActionsService.cancel_transaction(transaction_uuid, user_id)

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
        is_banned_user = BanUserRepository.check_and_update_ban_status(
            user_id=slot_reservation_data.get("user_id")
        )
        if is_banned_user:
            raise BannedUserException("User is banned.")
        now = get_current_time()
        slot_uuid = slot_reservation_data.pop("slot_uuid")
        slot = ParkingSlotRepository.get_slot(slot_uuid=slot_uuid)
        slot_status = slot.get("slot_status")
        parking_establishment = ParkingEstablishmentRepository.get_establishment(
            establishment_id=slot.get("establishment_id")
        )
        if slot_status in ["reserved", "occupied", "closed"]:
            raise SlotStatusTaken("Invalid slot status.")
        slot_reservation_data.update({"slot_id": ParkingSlot.get_id(slot_uuid)})
        slot_reservation_data.update({"created_at": now})
        slot_reservation_data.update({"updated_at": now})
        transaction_details = ParkingTransactionRepository.create_transaction(slot_reservation_data)
        user_email = UserRepository.get_user(
            user_id=transaction_details.get("user_id")
        ).get("email")
        ParkingSlotRepository.change_slot_status(slot_uuid=slot_uuid, new_status="reserved")
        reservation_template = render_template(
            'transaction_confirmation.html',
            user_name=user_email,
            establishment_name=parking_establishment.get("name"),
            slot_code=slot.get("slot_code"),
            created_at=now
        )
        send_mail(
            email=user_email,
            subject="Reservation Confirmation",
            message=reservation_template
        )
        return transaction_details.get("uuid")

    @staticmethod
    def release_slot(slot_data):
        """Releases the slot for a user."""

    @staticmethod
    def cancel_transaction(transaction_uuid: str, user_id: int):
        """Cancels the transaction for a user."""
        transaction = ParkingTransactionRepository.get_transaction(
            transaction_uuid=transaction_uuid
        )
        details = ParkingTransactionRepository.update_transaction_status(
            transaction_uuid, "cancelled"
        )
        user_info = UserRepository.get_user(user_id=user_id)
        ParkingSlotRepository.change_slot_status(
            slot_id=transaction.get("slot_id"), new_status="open"
        )
        cancel_template = render_template(
            'transaction_cancelled.html',
            user_name=user_info.get("email"),
            transaction_uuid=transaction_uuid,
            created_at=details.get("created_at")
        )
        return send_mail(
            email=user_info.get("email"),
            subject="Transaction Cancellation",
            message=cancel_template
        )

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
        contact_number = UserRepository.get_user(user_id=owner_user_id).get("phone_number")
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
        return ParkingTransactionRepository.update_transaction(
            transaction_uuid,
            update_data={
                "payment_status": payment_status,
                "entry_time": get_current_time(),
                "status": "active"
            }
        )

    @staticmethod
    def verify_exit_transaction(
        qr_content, payment_status,
        exit_time, amount_due, slot_id,
        overstayed_for_more_than_1_hour
    ):
        """Verifies the exit transaction for a user."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(qr_content)
        if transaction_data.get("status") != "active":
            raise QRCodeError("Invalid transaction status.")
        ParkingSlotRepository.change_slot_status(slot_id=slot_id, new_status="open")
        transaction_details = ParkingTransactionRepository.update_transaction(
            transaction_data.get("uuid"),
            update_data={
                "payment_status": payment_status,
                "exit_time": exit_time,
                "status": "completed",
                "amount_due": amount_due
            }
        )
        user_info = UserRepository.get_user(user_id=transaction_details.get("user_id"))
        slot_info = ParkingSlotRepository.get_slot(
            slot_id=transaction_details.get("slot_id")
        )
        establishment_info = ParkingEstablishmentRepository.get_establishment(
            establishment_id=slot_info.get("establishment_id")
        )
        transaction_complete_template = render_template(
            'transaction_finished.html',
            establishment_name=establishment_info.get("name"),
            user_name=user_info.get("email"),
            amount_paid=amount_due,
            transaction_date=exit_time,
            transaction_uuid=transaction_details.get("uuid")
        )
        send_mail(
            email=user_info.get("email"),
            subject="Transaction Completed",
            message=transaction_complete_template
        )
        if overstayed_for_more_than_1_hour:
            BanUserRepository.ban_user({
                "ban_reason": "Overstayed for more than 1 hour",
                "user_id": user_info.get("user_id"),
                "ban_start": datetime.now(),
                "ban_end": datetime.now() + timedelta(days=30),
                "is_permanent": False
            })
            ban_template = render_template(
                '/ban.html',
                reason="Overstayed for more than 1 hour",
                email=user_info.get('email')
            )
            send_mail(
                user_info.get("email"),
                ban_template,
                'You have been banned for overstaying'
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
        is_user_banned = BanUserRepository.check_and_update_ban_status(user_id=user_id)
        if is_user_banned:
            raise BannedUserException("User is banned.")
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
    @staticmethod
    def get_latest_exit_transaction(user_id):
        """Get the latest exit transaction for a user."""
        return ParkingTransactionRepository.get_latest_exit_transaction(user_id=user_id)
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
