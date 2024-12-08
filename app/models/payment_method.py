
from sqlalchemy import Column, Integer, Boolean, Text, TIMESTAMP, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class PaymentMethod(Base):
    __tablename__ = 'payment_method'
    
    # Columns definition
    method_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(Integer, ForeignKey('parking_establishment.establishment_id'), nullable=True)
    accepts_cash = Column(Boolean, default=False)
    accepts_mobile = Column(Boolean, default=False)
    accepts_other = Column(Boolean, default=False)
    other_methods = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('establishment_id', name='unique_establishment_payment'),
    )
    
    # Relationship to ParkingEstablishment
    parking_establishment = relationship("ParkingEstablishment", backref="payment_methods")
    
    def __repr__(self):
        return f"<PaymentMethod(method_id={self.method_id}, establishment_id={self.establishment_id}, accepts_cash={self.accepts_cash})>"


class PaymentMethodRepository:
    """Wraps the logic for creating, updating, and deleting payment methods."""
    
    @staticmethod
    def create_payment_method(payment_method_data: dict):
        """Create a new payment method."""
        with session_scope() as session:
            payment_method = PaymentMethod(**payment_method_data)
            session.add(payment_method)
            session.flush()
            return payment_method

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
            payment_methods = session.query(PaymentMethod).filter_by(establishment_id=establishment_id).all()
            return [method.to_dict() for method in payment_methods]