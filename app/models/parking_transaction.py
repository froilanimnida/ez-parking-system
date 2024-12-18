""" Parking transaction module that represents the parking transaction database table. """

# pylint: disable=R0401, R0801, C0415, E1102, C0103

from enum import Enum as PyEnum
from typing import Literal, overload

from sqlalchemy import (
    Column, Enum, Integer, ForeignKey, TIMESTAMP, text, Numeric, UUID, update, func
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.parking_slot import ParkingSlot
from app.utils.db import session_scope


# Define custom Enum types for 'payment_status' and 'transaction_status'
class PaymentStatusEnum(str, PyEnum):
    """Encapsulate enumerate types of payment status."""
    pending = "pending"
    completed = "completed"
    failed = "failed"


class TransactionStatusEnum(str, PyEnum):
    """Encapsulate enumerate types of transaction status."""
    reserved = "reserved"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class DurationTypeEnum(str, PyEnum):
    """Encapsulate enumerate types of duration."""
    monthly = "monthly"
    daily = "daily"
    hourly = "hourly"


class ParkingTransaction(
    Base
):  # pylint: disable=too-few-public-methods, missing-class-docstring
    __tablename__ = "parking_transaction"

    transaction_id = Column(
        Integer, primary_key=True, autoincrement=True,
        server_default=text("nextval('parking_transaction_transaction_id_seq'::regclass)"),
    )
    uuid = Column(
        UUID(as_uuid=True), unique=True, nullable=False, server_default=text("uuid_generate_v4()")
    )
    slot_id = Column(
        Integer, ForeignKey("parking_slot.slot_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
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
    duration_type = Column(Enum(DurationTypeEnum), nullable=False)
    duration = Column(Integer, nullable=False)

    parking_slots = relationship("ParkingSlot", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

    def to_dict(self):
        """ Convert the model instance to a dictionary. """
        if self is None:
            return {}
        return {
            "transaction_id": self.transaction_id,
            "uuid": str(self.uuid),
            "slot_id": self.slot_id,
            "user_id": self.user_id,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
            "payment_status": self.payment_status.value if self.payment_status else None,
            "status": self.status.value if self.status else None,
            "amount_due": self.amount_due,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "duration_type": self.duration_type.value if self.duration_type else None,
        }


class ParkingTransactionRepository:
    """Repository for ParkingTransaction model."""

    @staticmethod
    def create_transaction(data: dict):
        """Create a parking transaction."""
        with session_scope() as session:
            transaction = ParkingTransaction(**data)
            session.add(transaction)
            session.commit()
            return transaction.transaction_id

    @classmethod
    @overload
    def get_transaction(cls, transaction_uuid: str):
        """Get a parking transaction by UUID."""

    @classmethod
    @overload
    def get_transaction(cls, transaction_id: int):
        """Get a parking transaction by ID."""

    @classmethod
    def get_transaction(cls, transaction_uuid: str=None, transaction_id: int=None) -> dict:
        """Get a parking transaction."""
        with session_scope() as session:
            if transaction_uuid:
                transaction = (
                    session.query(ParkingTransaction)
                    .filter(ParkingTransaction.uuid == transaction_uuid)
                ).first()
                transaction_dict = transaction.to_dict()
                return transaction_dict
            if transaction_id:
                transaction = session.query(ParkingTransaction).filter(
                    ParkingTransaction.transaction_id == transaction_id
                ).first()
                return transaction.to_dict()
            return {}

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
        with session_scope() as session:
            if user_id:
                transactions = (
                    session.query(ParkingTransaction)
                    .filter(ParkingTransaction.user_id == user_id)
                    .join(
                        ParkingSlot,
                        ParkingSlot.slot_id == ParkingTransaction.slot_id
                    )
                ).all()
            else:
                transactions = session.query(ParkingTransaction).join(
                    ParkingSlot,
                    ParkingSlot.slot_id == ParkingTransaction.slot_id
                ).all()

            transactions_arr_dict = []
            for transaction in transactions:
                transaction_dict = transaction.to_dict()
                parking_slot_dict = transaction.parking_slots.to_dict()
                parking_slot_dict.pop('uuid')
                transaction_dict.update(parking_slot_dict)
                transactions_arr_dict.append(transaction_dict)
            return transactions_arr_dict

    @classmethod
    def update_transaction_status(
        cls, transaction_uuid: str, status: Literal["active", "completed", "cancelled"]
    ):
        """Update the status of a parking transaction."""
        with session_scope() as session:
            session.execute(
                update(ParkingTransaction)
                .values(status=status)
                .where(ParkingTransaction.uuid == transaction_uuid)
            )
            session.commit()


    @classmethod
    def is_user_have_an_ongoing_transaction(cls, user_id: int) -> bool:
        """Check if a user has an ongoing transaction."""
        with session_scope() as session:
            transaction = (
                session.query(ParkingTransaction)
                .filter(ParkingTransaction.user_id == user_id)
                .filter(ParkingTransaction.status.in_(["reserved", "active"]))
                .first()
            )
            return bool(transaction)
