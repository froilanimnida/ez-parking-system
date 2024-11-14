""" Parking transaction module that represents the parking transaction database table. """

from typing import Literal
from sqlalchemy import (
    VARCHAR,
    Column,
    Enum,
    Integer,
    ForeignKey,
    DateTime,
    BINARY,
    DECIMAL,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ParkingTransaction(Base):  # pylint: disable=R0903
    """
    SQLAlchemy model representing a parking transaction record.

    Contains details about a parking event including vehicle info, timing,
    slot allocation, payment status and associated relationships with
    slot and vehicle type tables.
    """

    __tablename__ = "parking_transaction"

    transaction_id = Column(Integer, primary_key=True)
    uuid = Column(BINARY(16), nullable=False)
    slot_id = Column(Integer, ForeignKey("slot.slot_id"), nullable=False)
    vehicle_type_id = Column(
        Integer, ForeignKey("vehicle_type.vehicle_type_id"), nullable=False
    )
    plate_number = Column(VARCHAR(15), nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=False)
    total_amount = Column(DECIMAL(9, 2), nullable=False)
    payment_status = Column(Enum("paid", "unpaid"), nullable=False, default="unpaid")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    slot = relationship("Slot", back_populates="parking_transaction")
    vehicle_type = relationship("VehicleType", back_populates="parking_transaction")


class ParkingTransactionOperation:
    """Class that provides operations for parking transactions in the database."""

    @classmethod
    def get_transaction_by(
        cls,
        by=Literal[
            "transaction_id",
            "plate_number",
            "entry_time",
            "payment_status",
            "vehicle_type_id",
            "payment_status_paid",
        ],
    ):
        """
        Retrieve a parking transaction from the database by its ID, plate number,
        entry time, payment status, vehicle type ID, or payment status.
        """

    @classmethod
    def add_new_transaction_entry(cls, transaction_data):
        """
        Add a new parking transaction entry to the database.
        """


class UpdateTransaction:  # pylint: disable=R0903
    """Class that provides operations for updating parking transactions in the database."""

    @classmethod
    def update_transaction_entry(cls, transaction_id, transaction_data):
        """
        Update a parking transaction entry in the database.
        """


class DeleteTransaction:  # pylint: disable=R0903
    """Class that provides operations for deleting parking transactions in the database."""

    @classmethod
    def delete_transaction_entry(cls, transaction_id):
        """
        Delete a parking transaction entry from the database.
        """
