"""
Represents the ORM model for the address table. This is connected to the company_profile table.
"""

# pylint: disable=E1102

from typing import overload

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class Address(Base):  # pylint: disable=too-few-public-methods, missing-class-docstring
    __tablename__ = "address"

    address_id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("company_profile.profile_id"), nullable=False)
    street = Column(String(255), nullable=False)
    barangay = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)
    postal_code = Column(String(10), nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    company_profile = relationship("CompanyProfile", backref="addresses")

    def to_dict(self):
        """ Convert the address object to a dictionary. """
        if self is None:
            return {}
        return {
            "address_id": self.address_id,
            "profile_id": self.profile_id,
            "street": self.street,
            "barangay": self.barangay,
            "city": self.city,
            "province": self.province,
            "postal_code": self.postal_code,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AddressRepository:
    """Wraps the logic for creating, updating, and deleting addresses."""
    @staticmethod
    def create_address(address_data: dict):
        """Create a new address."""
        with session_scope() as session:
            address = Address(**address_data)
            session.add(address)
            session.flush()
            session.refresh(address)
            return address.address_id

    @staticmethod
    @overload
    def get_address(address_id: int = None) -> dict:
        """Get address by address id."""

    @staticmethod
    @overload
    def get_address(profile_id: int = None) -> dict:
        """Get addresses by profile id."""

    @staticmethod
    def get_address(profile_id: int = None, address_id: int = None) -> dict:
        """Get address by address id or profile id."""
        with session_scope() as session:
            if profile_id is not None:
                address = session.query(Address).filter_by(profile_id=profile_id).first()
            elif address_id is not None:
                address = session.query(Address).filter_by(address_id=address_id).first()
            else:
                return {}
            return address.to_dict()

    @staticmethod
    def update_address(address_id: int, address_data: dict):
        """Update an address."""
        with session_scope() as session:
            session.query(Address).update(**address_data).where(
                Address.address_id == address_id
            )
