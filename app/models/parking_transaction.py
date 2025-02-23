""" Parking transaction module that represents the parking transaction database table. """

# pylint: disable=R0401, R0801, C0415, E1102, C0103, W0613

from enum import Enum as PyEnum
from datetime import datetime, timedelta
from typing import Literal, Dict, Any, TypedDict, overload

from sqlalchemy import (
    Column, Enum, Integer, ForeignKey, TIMESTAMP, text, Numeric, UUID, update, func
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.parking_slot import ParkingSlot
from app.models.vehicle_type import VehicleType
from app.utils.db import session_scope
from app.utils.timezone_utils import get_current_time

class TransactionUpdate(TypedDict, total=False):
    """Type definition for transaction updates"""
    status: Literal["active", "completed", "cancelled"]
    payment_status: Literal["paid", "unpaid"]
    entry_time: datetime
    exit_time: datetime
    amount_due: float
    duration: int
    duration_type: str

# Define custom Enum types for 'payment_status' and 'transaction_status'
class PaymentStatusEnum(str, PyEnum):
    """Encapsulate enumerate types of payment status."""
    paid = "paid"
    unpaid = "unpaid"


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
    scheduled_entry_time = Column(TIMESTAMP(timezone=False), nullable=True)
    scheduled_exit_time = Column(TIMESTAMP(timezone=False), nullable=True)
    entry_time = Column(TIMESTAMP(timezone=False), nullable=True)
    exit_time = Column(TIMESTAMP(timezone=False), nullable=True)
    payment_status = Column(
        Enum(PaymentStatusEnum), nullable=False, server_default=text("'unpaid'::payment_status"),
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
            "duration": self.duration,
            "scheduled_entry_time": self.scheduled_entry_time,
            "scheduled_exit_time": self.scheduled_exit_time,
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
    def get_all_transactions(slot_id: int):
        """Get all parking transactions."""

    @classmethod
    def get_all_transactions(cls, user_id: int=None, slot_id: int=None):
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
            elif slot_id:
                transactions = (
                    session.query(ParkingTransaction)
                    .filter(ParkingTransaction.slot_id == slot_id)
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
    def update_entry_exit_time(
        cls, transaction_uuid: str, entry_time = None, exit_time = None
    ):
        """Update the entry and exit time of a parking transaction."""
        with session_scope() as session:
            session.execute(
                update(ParkingTransaction)
                .values(entry_time=entry_time, exit_time=exit_time)
                .where(ParkingTransaction.uuid == transaction_uuid)
            )
            session.commit()
    @classmethod
    def update_payment_status(
        cls, transaction_uuid: str, payment_status: Literal["completed", "failed"]
    ):
        """Update the payment status of a parking transaction."""
        with session_scope() as session:
            session.execute(
                update(ParkingTransaction)
                .values(payment_status=payment_status)
                .where(ParkingTransaction.uuid == transaction_uuid)
            )
            session.commit()

    @classmethod
    def update_transaction(
        cls,
        transaction_uuid: str,
        update_data: TransactionUpdate
    ) -> Dict[str, Any]:
        """
        Update a parking transaction with the provided data.

        Args:
            transaction_uuid: UUID of the transaction
            update_data: Dictionary containing fields to update

        Returns:
            dict: Updated transaction data

        Raises:
            SQLAlchemyError: If database operation fails
            ValueError: If invalid update data is provided
        """
        with session_scope() as session:
            # Add automatic updated_at timestamp
            update_values = {
                **update_data,
                "updated_at": get_current_time()
            }

            # Perform the update and return the updated record
            result = session.execute(
                update(ParkingTransaction)
                .values(**update_values)
                .where(ParkingTransaction.uuid == transaction_uuid)
                .returning(ParkingTransaction)
            )

            updated_transaction = result.scalar_one()
            return updated_transaction.to_dict()



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


class BusinessIntelligence:
    """Class for business intelligence and analytics operations."""

    @staticmethod
    def get_duration_analysis(establishment_id: int = None,
                            start_date: datetime = None,
                            end_date: datetime = None) -> list[dict[str, Any]]:
        """Analyze parking duration patterns.

        Args:
            establishment_id: Optional filter by establishment
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary containing duration metrics
        """
        with session_scope() as session:
            query = session.query(
                func.avg(
                    func.extract('epoch', ParkingTransaction.exit_time) -
                    func.extract('epoch', ParkingTransaction.entry_time)
                ).label('avg_duration'),
                func.min(
                    func.extract('epoch', ParkingTransaction.exit_time) -
                    func.extract('epoch', ParkingTransaction.entry_time)
                ).label('min_duration'),
                func.max(
                    func.extract('epoch', ParkingTransaction.exit_time) -
                    func.extract('epoch', ParkingTransaction.entry_time)
                ).label('max_duration'),
                ParkingTransaction.duration_type,
                func.count(ParkingTransaction.transaction_id).label('count')
            ).filter(
                ParkingTransaction.status == 'completed',
                ParkingTransaction.entry_time.isnot(None),
                ParkingTransaction.exit_time.isnot(None)
            ).group_by(ParkingTransaction.duration_type)

            if establishment_id:
                query = query.join(
                    ParkingSlot
                ).filter(ParkingSlot.establishment_id == establishment_id)

            if start_date:
                query = query.filter(ParkingTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(ParkingTransaction.created_at <= end_date)

            results = query.all()

            return [{
                'duration_type': result.duration_type.value,
                'average_duration_hours': round(result.avg_duration / 3600, 2),
                'min_duration_hours': round(result.min_duration / 3600, 2),
                'max_duration_hours': round(result.max_duration / 3600, 2),
                'transaction_count': result.count
            } for result in results]

    @staticmethod
    def get_payment_analytics(establishment_id: int = None,
                            start_date: datetime = None,
                            end_date: datetime = None) -> list[dict[str, float | Any]]:
        """Analyze payment patterns and status.

        Args:
            establishment_id: Optional filter by establishment
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary containing payment analytics
        """
        with session_scope() as session:
            query = session.query(
                ParkingTransaction.payment_status,
                func.count(ParkingTransaction.transaction_id).label('count'),
                func.sum(ParkingTransaction.amount_due).label('total_amount')
            ).group_by(ParkingTransaction.payment_status)

            if establishment_id:
                query = query.join(
                    ParkingSlot
                ).filter(ParkingSlot.establishment_id == establishment_id)

            if start_date:
                query = query.filter(ParkingTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(ParkingTransaction.created_at <= end_date)

            results = query.all()

            return [{
                'payment_status': result.payment_status.value,
                'transaction_count': result.count,
                'total_amount': float(result.total_amount or 0)
            } for result in results]
    @staticmethod
    def get_slot_utilization_by_type(establishment_id: int = None,
                                     start_date: datetime = None,
                                     end_date: datetime = None) -> list:
        """Analyze slot utilization by vehicle type.

        Args:
            establishment_id: Optional filter by establishment
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            List of slot utilization metrics by vehicle type
        """
        with session_scope() as session:
            query = session.query(
                VehicleType.name.label('vehicle_type_name'),  # Fetch vehicle type name
                func.count(ParkingTransaction.transaction_id).label('transaction_count'),
                func.sum(
                    func.extract('epoch', ParkingTransaction.exit_time) -
                    func.extract('epoch', ParkingTransaction.entry_time)
                ).label('total_duration')
            ).join(
                ParkingSlot, ParkingSlot.vehicle_type_id == VehicleType.vehicle_type_id
            ).join(
                ParkingTransaction, ParkingSlot.slot_id == ParkingTransaction.slot_id
            ).group_by(VehicleType.name)
            if establishment_id:
                query = query.filter(ParkingSlot.establishment_id == establishment_id)
            if start_date:
                query = query.filter(ParkingTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(ParkingTransaction.created_at <= end_date)
            results = query.all()
            return [{
                'vehicle_type_name': result.vehicle_type_name,
                'transaction_count': result.transaction_count,
                'total_duration_hours': round(
                    result.total_duration / 3600, 2
                ) if result.total_duration else 0
            } for result in results]
    @staticmethod
    def get_premium_vs_standard_analysis(establishment_id: int = None,
                                       start_date: datetime = None,
                                       end_date: datetime = None) -> dict:
        """Compare premium vs standard slot performance.

        Args:
            establishment_id: Optional filter by establishment
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary containing comparative analysis
        """
        with session_scope() as session:
            query = session.query(
                ParkingSlot.is_premium,
                func.count(ParkingTransaction.transaction_id).label('transaction_count'),
                func.sum(ParkingTransaction.amount_due).label('total_revenue'),
                func.avg(ParkingTransaction.amount_due).label('avg_revenue')
            ).join(
                ParkingTransaction,
                ParkingSlot.slot_id == ParkingTransaction.slot_id
            ).group_by(ParkingSlot.is_premium)

            if establishment_id:
                query = query.filter(ParkingSlot.establishment_id == establishment_id)

            if start_date:
                query = query.filter(ParkingTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(ParkingTransaction.created_at <= end_date)

            results = query.all()

            return [{
                'slot_type': 'premium' if result.is_premium else 'standard',
                'transaction_count': result.transaction_count,
                'total_revenue': float(result.total_revenue or 0),
                'average_revenue': float(result.avg_revenue or 0)
            } for result in results]

    @staticmethod
    def get_seasonal_trends(establishment_id: int = None,
                          days: int = 90) -> list:
        """Analyze seasonal trends in parking usage.

        Args:
            establishment_id: Optional filter by establishment
            days: Number of past days to analyze

        Returns:
            List of daily usage trends
        """
        with session_scope() as session:
            query = session.query(
                func.date_trunc('day', ParkingTransaction.created_at).label('date'),
                func.count(ParkingTransaction.transaction_id).label(
                    'daily_transactions'
                ),
                func.sum(ParkingTransaction.amount_due).label('daily_revenue')
            ).filter(
                ParkingTransaction.created_at >= func.current_date() - text(f'interval \'{days} days\'')  # pylint: disable=C0301
            ).group_by(
                func.date_trunc('day', ParkingTransaction.created_at)
            ).order_by('date')

            if establishment_id:
                query = query.join(
                    ParkingSlot
                ).filter(ParkingSlot.establishment_id == establishment_id)

            results = query.all()

            return [{
                'date': result.date.strftime('%Y-%m-%d'),
                'daily_transactions': result.daily_transactions,
                'daily_revenue': float(result.daily_revenue or 0)
            } for result in results]

    @staticmethod
    def get_occupancy_rate(establishment_id: int = None, start_date: datetime = None,
                          end_date: datetime = None) -> dict:
        """Calculate parking slot occupancy rates.

        Args:
            establishment_id: Optional filter by establishment
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary containing occupancy metrics
        """
        with session_scope() as session:
            # Base query for total slots
            slots_query = session.query(ParkingSlot)
            if establishment_id:
                slots_query = slots_query.filter(ParkingSlot.establishment_id == establishment_id)

            total_slots = slots_query.count()

            occupied_query = slots_query.filter(
                ParkingSlot.slot_status.in_(['occupied', 'reserved'])
            )

            occupied_slots = occupied_query.count()

            return {
                'total_slots': total_slots,
                'occupied_slots': occupied_slots,
                'occupancy_rate': (occupied_slots / total_slots * 100) if total_slots > 0 else 0,
                'available_slots': total_slots - occupied_slots
            }

    @staticmethod
    def get_revenue_analysis(establishment_id: int = None,
                           start_date: datetime = None,
                           end_date: datetime = None) -> dict:
        """Analyze revenue from parking transactions.

        Args:
            establishment_id: Optional filter by establishment
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            Dictionary containing revenue metrics
        """
        with session_scope() as session:
            query = session.query(
                func.sum(ParkingTransaction.amount_due).label('total_revenue'),
                func.count(ParkingTransaction.transaction_id).label('total_transactions'),
                func.avg(ParkingTransaction.amount_due).label('average_transaction_value')
            ).join(
                ParkingSlot,
                ParkingSlot.slot_id == ParkingTransaction.slot_id
            ).filter(
                ParkingTransaction.payment_status == 'paid'
            )

            if establishment_id:
                query = query.filter(ParkingSlot.establishment_id == establishment_id)

            if start_date:
                query = query.filter(ParkingTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(ParkingTransaction.created_at <= end_date)

            result = query.first()

            return {
                'total_revenue': float(result.total_revenue or 0),
                'total_transactions': result.total_transactions,
                'average_transaction_value': float(result.average_transaction_value or 0)
            }

    @staticmethod
    def get_peak_hours_analysis(establishment_id: int = None,
                              days: int = 30) -> list:
        """Analyze peak hours based on parking transactions.

        Args:
            establishment_id: Optional filter by establishment
            days: Number of past days to analyze

        Returns:
            List of hourly occupancy rates
        """
        with session_scope() as session:
            start_date = datetime.now() - timedelta(days=days)

            query = session.query(
                func.extract('hour', ParkingTransaction.entry_time).label('hour'),
                func.count(ParkingTransaction.transaction_id).label('count')
            ).join(
                ParkingSlot,
                ParkingSlot.slot_id == ParkingTransaction.slot_id
            ).filter(
                ParkingTransaction.entry_time >= start_date,
                ParkingTransaction.status != 'cancelled'
            )

            if establishment_id:
                query = query.filter(ParkingSlot.establishment_id == establishment_id)

            query = query.group_by(
                func.extract('hour', ParkingTransaction.entry_time)
            ).order_by('hour')

            results = query.all()

            return [{
                'hour': result.hour,
                'transaction_count': result.count
            } for result in results]

    @staticmethod
    def get_vehicle_type_distribution(establishment_id: int = None,
                                    start_date: datetime = None,
                                    end_date: datetime = None) -> list:
        """Analyze distribution of vehicle types using parking facilities.

        Args:
            establishment_id: Optional filter by establishment
            start_date: Start date for analysis
            end_date: End date for analysis

        Returns:
            List of vehicle type distributions
        """
        with session_scope() as session:
            query = session.query(
                VehicleType.name,
                func.count(ParkingTransaction.transaction_id).label('count')
            ).join(
                ParkingSlot,
                ParkingSlot.slot_id == ParkingTransaction.slot_id
            ).join(
                VehicleType,
                VehicleType.vehicle_type_id == ParkingSlot.vehicle_type_id
            ).filter(
                ParkingTransaction.status != 'cancelled'
            )

            if establishment_id:
                query = query.filter(ParkingSlot.establishment_id == establishment_id)

            if start_date:
                query = query.filter(ParkingTransaction.created_at >= start_date)
            if end_date:
                query = query.filter(ParkingTransaction.created_at <= end_date)

            query = query.group_by(VehicleType.name)

            results = query.all()

            return [{
                'vehicle_type': result.name,
                'count': result.count
            } for result in results]
