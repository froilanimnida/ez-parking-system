"""This module contains the model for payment methods."""

# pylint: disable=E1102

from sqlalchemy import Column, Integer, Boolean, Text, TIMESTAMP, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class PaymentMethod(Base):  # pylint: disable=too-few-public-methods
    """Represents the payment methods in the database."""
    __tablename__ = 'payment_method'

    method_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(
        Integer, ForeignKey('parking_establishment.establishment_id'), nullable=True
    )
    accepts_cash = Column(Boolean, default=False)
    accepts_mobile = Column(Boolean, default=False)
    accepts_other = Column(Boolean, default=False)
    other_methods = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        UniqueConstraint('establishment_id', name='unique_establishment_payment'),
    )

    parking_establishment = relationship("ParkingEstablishment", back_populates="payment_methods")


    def to_dict(self):
        """Convert the payment method object to a dictionary."""
        if self is None:
            return {}
        return {
            'method_id': self.method_id,
            'establishment_id': self.establishment_id,
            'accepts_cash': self.accepts_cash,
            'accepts_mobile': self.accepts_mobile,
            'accepts_other': self.accepts_other,
            'other_methods': self.other_methods,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class PaymentMethodRepository:
    """Wraps the logic for creating, updating, and deleting payment methods."""

    @staticmethod
    def create_payment_method(payment_method_data: dict):
        """Create a new payment method."""
        with session_scope() as session:
            payment_method = PaymentMethod(**payment_method_data)
            session.add(payment_method)
            session.flush()
            session.refresh(payment_method)
            return payment_method.method_id

    @staticmethod
    def update_payment_method(payment_method_id: int, payment_method_data: dict):
        """Update an existing payment method."""
        with session_scope() as session:
            payment_method = session.query(PaymentMethod).get(payment_method_id)
            for key, value in payment_method_data.items():
                setattr(payment_method, key, value)
            session.flush()
            return payment_method

    @staticmethod
    def delete_payment_method(payment_method_id: int):
        """Delete an existing payment method."""
        with session_scope() as session:
            payment_method = session.query(PaymentMethod).get(payment_method_id)
            session.delete(payment_method)
            session.flush()
            return payment_method

    @staticmethod
    def get_payment_methods(establishment_id: int):
        """Get payment methods by establishment id."""
        with session_scope() as session:
            payment_methods = session.query(
                PaymentMethod).filter_by(establishment_id=establishment_id).all()
            return [method.to_dict() for method in payment_methods]
