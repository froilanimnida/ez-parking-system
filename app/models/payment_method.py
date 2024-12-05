
from sqlalchemy import Column, Integer, Boolean, Text, TIMESTAMP, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.models.base import Base


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
