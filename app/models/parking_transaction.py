""" Parking transaction module that represents the parking transaction database table. """

# pylint: disable=R0401, R0801, C0415, E1102

from enum import Enum as PyEnum
from typing import Literal, overload

from sqlalchemy import (
    Column,
    Enum,
    Integer,
    ForeignKey,
    TIMESTAMP,
    text,
    Numeric,
    UUID,
    update,
    func,
    String,
)
from sqlalchemy.exc import DataError, DatabaseError, IntegrityError, OperationalError
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.vehicle_type import VehicleType
from app.utils.engine import get_session
from app.utils.uuid_utility import UUIDUtility


# Define custom Enum types for 'payment_status' and 'transaction_status'
class PaymentStatusEnum(str, PyEnum):
    """Encapsulate enumerate types of payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class TransactionStatusEnum(str, PyEnum):
    """Encapsulate enumerate types of transaction status."""
    RESERVED = "reserved"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ParkingTransaction(
    Base
):  # pylint: disable=too-few-public-methods, missing-class-docstring
    __tablename__ = "parking_transaction"

    transaction_id = Column(
        Integer, primary_key=True, autoincrement=True,
        server_default=text("nextval('parking_transaction_transaction_id_seq'::regclass)"),
    )
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    slot_id = Column(
        Integer, ForeignKey("parking_slot.slot_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    vehicle_type_id = Column(
        Integer, ForeignKey("vehicle_type.vehicle_type_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    plate_number = Column(String(15), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=True)
    entry_time = Column(TIMESTAMP(timezone=False), nullable=True)
    exit_time = Column(TIMESTAMP(timezone=False), nullable=True)
    payment_status = Column(
        Enum(PaymentStatusEnum), nullable=False, server_default=text("'pending'::payment_status"),
    )
    status = Column(
        Enum(TransactionStatusEnum), nullable=False,
        server_default=text("'reserved'::transaction_status"),
    )
    amount_due = Column(Numeric(9, 2), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        TIMESTAMP(timezone=False), nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    parking_slots = relationship("ParkingSlot", back_populates="transactions")
    vehicle_type = relationship("VehicleType", back_populates="parking_transactions")
    user = relationship("User", back_populates="transactions")

    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        """
        if self is None:
            return {}
        uuid_utility = UUIDUtility()
        return {
            "transaction_id": self.transaction_id,
            "uuid": uuid_utility.format_uuid(
                uuid_utility.binary_to_uuid(self.uuid)
            ),
            "slot_id": self.slot_id,
            "vehicle_type_id": self.vehicle_type_id,
            "plate_number": self.plate_number,
            "entry_time": self.entry_time is not None
            and self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            or "Not Available",
            "exit_time": self.exit_time is not None
            and self.exit_time.strftime("%Y-%m-%d %H:%M:%S")
            or "Not Available",
            "amount_due": self.amount_due,
            "payment_status": str(self.payment_status).capitalize(),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ParkingTransactionOperation:
    """Class that provides operations for parking transactions in the database."""

    @classmethod
    def get_transaction_by_plate_number(cls, plate_number: str):
        """
        Retrieve a parking transaction from the database by the vehicle plate number.
        Returns dictionary with transaction details including related slot and vehicle info.
        """
        from app.models.slot import Slot
        from app.models.vehicle_type import VehicleType

        session = get_session()
        try:
            uuid_utility = UUIDUtility()
            transactions = (
                session.query(ParkingTransaction)
                .join(Slot, Slot.slot_id == ParkingTransaction.slot_id)
                .join(
                    VehicleType,
                    VehicleType.vehicle_id == ParkingTransaction.vehicle_type_id,
                )
                .filter(ParkingTransaction.plate_number == plate_number)
                .all()
            )
            if not transactions:
                return {}
            return {
                "transactions": [
                    {
                        "uuid": uuid_utility.format_uuid(
                            uuid_utility.binary_to_uuid(transaction.uuid)
                        ),
                        "status": transaction.status,
                        "payment_status": str(transaction.payment_status).capitalize(),
                        "slot_details": {
                            "slot_code": transaction.slot.slot_code,
                            "slot_status": transaction.slot.slot_status,
                            "slot_features": str(
                                transaction.slot.slot_features
                            ).capitalize(),
                            "floor_level": transaction.slot.floor_level,
                            "slot_multiplier": float(transaction.slot.slot_multiplier),
                            "is_premium": transaction.slot.is_premium == 1
                            and "Yes"
                            or "No",
                        },
                        "vehicle_details": {
                            "type_name": transaction.vehicle_type.name,
                            "size_category": transaction.vehicle_type.size_category,
                            "base_rate_multiplier": float(
                                transaction.vehicle_type.base_rate_multiplier
                            ),
                        },
                    }
                    for transaction in transactions
                ]
            }

        except (DatabaseError, OperationalError) as error:
            raise error
        finally:
            session.close()

    @classmethod
    def get_transaction(cls, transaction_uuid_bin: bytes):
        """
        Retrieve a parking transaction from the database by its UUID.
        Returns dictionary with transaction details including related slot and vehicle info.
        """
        from app.models.slot import Slot
        from app.models.vehicle_type import VehicleType
        from app.models.parking_establishment import ParkingEstablishment

        session = get_session()
        try:
            transaction = (
                session.query(ParkingTransaction)
                .join(Slot, Slot.slot_id == ParkingTransaction.slot_id)
                .join(
                    VehicleType,
                    VehicleType.vehicle_id == ParkingTransaction.vehicle_type_id,
                )
                .filter(ParkingTransaction.uuid == transaction_uuid_bin)
                .first()
            )
            establishment_info = (
                session.query(
                    ParkingEstablishment.name,
                    ParkingEstablishment.address,
                    ParkingEstablishment.longitude,
                    ParkingEstablishment.latitude,
                    ParkingEstablishment.contact_number,
                )
                .join(
                    Slot, Slot.establishment_id == ParkingEstablishment.establishment_id
                )
                .filter(Slot.slot_id == transaction.slot_id)
                .first()
            )

            if not transaction:
                return {}
            transaction_dict = transaction.to_dict()
            transaction_dict.update(
                {
                    "uuid": UUIDUtility().format_uuid(
                        UUIDUtility().binary_to_uuid(transaction.uuid)
                    ),
                    "slot_details": {
                        "slot_code": transaction.slot.slot_code,
                        "slot_status": transaction.slot.slot_status,
                        "slot_features": str(
                            transaction.slot.slot_features
                        ).capitalize(),
                        "floor_level": transaction.slot.floor_level,
                        "slot_multiplier": float(transaction.slot.slot_multiplier),
                        "is_premium": transaction.slot.is_premium == 1
                        and "Yes"
                        or "No",
                    },
                    "vehicle_details": {
                        "type_name": transaction.vehicle_type.name,
                        "size_category": transaction.vehicle_type.size_category,
                        "base_rate_multiplier": float(
                            transaction.vehicle_type.base_rate_multiplier
                        ),
                    },
                    "establishment_info": {
                        "name": establishment_info.name,
                        "address": establishment_info.address,
                        "longitude": establishment_info.longitude,
                        "latitude": establishment_info.latitude,
                        "contact_number": establishment_info.contact_number,
                    },
                }
            )

            return transaction_dict

        except (DatabaseError, OperationalError) as error:
            raise error
        finally:
            session.close()

    @classmethod
    def add_new_transaction_entry(cls, transaction_data):
        """
        Add a new parking transaction entry to the database.
        """
        from app.models import Slot

        session = get_session()
        try:
            transaction = ParkingTransaction(
                uuid=transaction_data.get("uuid"),
                slot_id=transaction_data.get("slot_id"),
                vehicle_type_id=transaction_data.get("vehicle_type_id"),
                plate_number=transaction_data.get("plate_number"),
                entry_time=transaction_data.get("entry_time"),
                exit_time=transaction_data.get("exit_time"),
                created_at=transaction_data.get("created_at"),
                updated_at=transaction_data.get("updated_at"),
            )

            session.execute(
                update(Slot)
                .values(slot_status="occupied")
                .where(Slot.slot_id == transaction_data.get("slot_id"))
            )

            session.add(transaction)
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class UpdateTransaction:  # pylint: disable=R0903
    """Class that provides operations for updating parking transactions in the database."""

    @classmethod
    def update_transaction_entry(cls, transaction_id, transaction_data):
        """
        Update a parking transaction entry in the database.
        """

    @classmethod
    def update_transaction_status(
        cls, transaction_status: Literal["active", "completed"], transaction_uuid: str
    ):
        """
        Update the status of a parking transaction in the database.
        """
        from app.models import Slot

        session = get_session()
        try:
            transaction_uuid_bin = bytes.fromhex(transaction_uuid)
            session.execute(
                update(ParkingTransaction)
                .values(status=transaction_status)
                .where(ParkingTransaction.uuid == transaction_uuid_bin)
            )
            transaction_slot = (
                session.query(ParkingTransaction)
                .filter(ParkingTransaction.uuid == transaction_uuid_bin)
                .first()
            )
            session.execute(
                update(Slot)
                .values(slot_status="occupied")
                .where(Slot.slot_id == transaction_slot.slot_id)  # type: ignore
            )
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class ParkingTransactionRepository:  # pylint: disable=R0903
    """Repository for ParkingTransaction model."""
    vehicle_type = VehicleType()

    @staticmethod
    def create_transaction(data: dict):
        """Create a parking transaction."""
        with get_session() as session:
            transaction = ParkingTransaction(**data)
            session.add(transaction)
            session.commit()
            return transaction.transaction_id

    @classmethod
    @overload
    def get_transaction(cls, transaction_uuid: bytes):
        """Get a parking transaction by UUID."""

    @classmethod
    @overload
    def get_transaction(cls, transaction_id: int):
        """Get a parking transaction by ID."""
        
    @classmethod
    def get_transaction(cls, transaction_uuid: bytes=None, transaction_id: int=None) -> dict:
        """Get a parking transaction."""
        with get_session() as session:
            if transaction_uuid:
                transaction = (
                    session.query(ParkingTransaction)
                    .filter(ParkingTransaction.uuid == transaction_uuid)
                    .join(cls.vehicle_type, cls.vehicle_type.vehicle_type_id == ParkingTransaction.vehicle_type_id)
                )
            elif transaction_id:
                transaction = session.query(ParkingTransaction).filter(
                    ParkingTransaction.transaction_id == transaction_id
                ).join(cls.vehicle_type, cls.vehicle_type.vehicle_type_id == ParkingTransaction.vehicle_type_id)
            transaction_dict = {}
            if transaction:
                transaction_dict = transaction.to_dict()
                transaction_dict["vehicle_type"] = cls.vehicle_type.to_dict()
            return transaction_dict

    @staticmethod
    @overload
    def get_all_transactions(user_id: int):
        """Get all parking transactions for a user."""

    @staticmethod
    @overload
    def get_all_transactions():
        """Get all parking transactions."""

    @classmethod
    def get_all_transactions(cls, user_id: int=None):
        """Get all parking transactions."""
        with get_session() as session:
            if user_id:
                transactions = (
                    session.query(ParkingTransaction)
                    .filter(ParkingTransaction.user_id == user_id)
                    .join(cls.vehicle_type, cls.vehicle_type.vehicle_type_id == ParkingTransaction.vehicle_type_id)
                )
            else:
                transactions = session.query(ParkingTransaction).join(
                    cls.vehicle_type, cls.vehicle_type.vehicle_type_id == ParkingTransaction.vehicle_type_id
                )
            transactions_arr_dict = []
            for transaction in transactions:
                transaction_dict = transaction.to_dict()
                transaction_dict["vehicle_type"] = cls.vehicle_type.to_dict()
                transactions_arr_dict.append(transaction_dict)
            return transactions_arr_dict
        
    @classmethod
    def update_transaction_status(cls, transaction_uuid: bytes, status: Literal["active", "completed", "cancelled"]):
        """Update the status of a parking transaction."""
        with get_session() as session:
            session.execute(
                update(ParkingTransaction)
                .values(status=status)
                .where(ParkingTransaction.uuid == transaction_uuid)
            )
            session.commit()
