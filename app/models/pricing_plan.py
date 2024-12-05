"""
This module defines the PricingPlan model which represents the pricing plan of a parking establishment.
"""


from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, Numeric, Boolean, TIMESTAMP, func, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from app.models.base import Base


class RateType(PyEnum):
    """Enum for rate type"""
    HOURLY = 'hourly'
    DAILY = 'daily'
    MONTHLY = 'monthly'


class PricingPlan(Base):
    """ Pricing Plan Model """
    __tablename__ = 'pricing_plan'
    
    # Columns definition
    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(Integer, ForeignKey('parking_establishment.establishment_id'), nullable=True)
    rate_type = Column(ENUM(RateType), nullable=True)
    is_enabled = Column(Boolean, default=False)
    rate = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('establishment_id', 'rate_type', name='unique_establishment_rate_type'),
        CheckConstraint('rate >= 0', name='pricing_plan_rate_check'),
        CheckConstraint('rate_type IN (%s, %s, %s)' % (
            RateType.HOURLY.value, RateType.DAILY.value, RateType.MONTHLY.value), name='pricing_plan_rate_type_check')
    )
    
    # Relationship to ParkingEstablishment
    parking_establishment = relationship("ParkingEstablishment", backref="pricing_plans")
    
    def __repr__(self):
        return f"<PricingPlan(plan_id={self.plan_id}, establishment_id={self.establishment_id}, rate_type={self.rate_type}, rate={self.rate})>"
