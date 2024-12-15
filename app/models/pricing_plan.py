"""
This module defines the PricingPlan model which represents the
pricing plan of a parking establishment.
"""

# pylint: disable=E1102


from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, Numeric, Boolean, TIMESTAMP, func, ForeignKey,
    UniqueConstraint, CheckConstraint, String
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class RateType(PyEnum):
    """Enum for rate type"""
    HOURLY = 'hourly'
    DAILY = 'daily'
    MONTHLY = 'monthly'


class PricingPlan(Base):  # pylint: disable=too-few-public-methods
    """ Pricing Plan Model """
    __tablename__ = 'pricing_plan'

    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(
        Integer, ForeignKey('parking_establishment.establishment_id'), nullable=True
    )
    rate_type = Column(String(10), nullable=True)
    is_enabled = Column(Boolean, default=False)
    rate = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    __table_args__ = (
        UniqueConstraint('establishment_id', 'rate_type', name='unique_establishment_rate_type'),
        CheckConstraint('rate >= 0', name='pricing_plan_rate_check'),
        CheckConstraint(
            "rate_type IN ('hourly', 'daily', 'monthly')",
            name='pricing_plan_rate_type_check'
        )
    )

    parking_establishment = relationship("ParkingEstablishment", backref="pricing_plans")

    def to_dict(self):
        """Convert the pricing plan object to a dictionary."""
        if self is None:
            return {}
        return {
            'plan_id': self.plan_id,
            'establishment_id': self.establishment_id,
            'rate_type': self.rate_type,
            'is_enabled': self.is_enabled,
            'rate': self.rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PricingPlanRepository:
    """Repository for the PricingPlan model."""

    @staticmethod
    def create_pricing_plan(establishment_id: int, pricing_plans: list):
        """Create pricing plan for a parking establishment."""
        with session_scope() as session:
            pricing_plan_ids = []
            for plan in pricing_plans:
                pricing_plan = PricingPlan(
                    establishment_id=establishment_id,
                    rate_type=plan.get('rate_type'),
                    rate=plan.get('rate')
                )
                session.add(pricing_plan)
                session.flush()
                pricing_plan_ids.append(pricing_plan.plan_id)
            return pricing_plan_ids

    @staticmethod
    def get_pricing_plans(establishment_id: int):
        """Get pricing plans of a parking establishment."""
        with session_scope() as session:
            pricing_plans = session.query(
                PricingPlan).filter_by(establishment_id=establishment_id).all()
            return [plan.to_dict() for plan in pricing_plans]

    @staticmethod
    def update_pricing_plans(establishment_id: int, pricing_plans: list):
        """Update pricing plans of a parking establishment."""
        with session_scope() as session:
            for plan in pricing_plans:
                pricing_plan = session.query(PricingPlan).filter_by(
                    establishment_id=establishment_id, rate_type=plan.get('rate_type')
                ).first()
                if pricing_plan is not None:
                    pricing_plan.rate = plan.get('rate')
                    pricing_plan.is_enabled = plan.get('is_enabled')
            session.commit()

    @staticmethod
    def delete_pricing_plans(establishment_id: int):
        """Delete pricing plans of a parking establishment."""
        with session_scope() as session:
            pricing_plans = session.query(
                PricingPlan).filter_by(establishment_id=establishment_id).all()
            for plan in pricing_plans:
                session.delete(plan)
            session.commit()
