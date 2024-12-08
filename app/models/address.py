""" Represents the ORM model for the address table. This is connected to the company_profile table. """

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class Address(Base):  # pylint: disable=too-few-public-methods, missing-class-docstring
    __tablename__ = "address"

    address_id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(
        Integer, ForeignKey("company_profile.profile_id"), nullable=False
    )
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

    def __repr__(self):
        return f"<Address(address_id={self.address_id}, profile_id={self.profile_id}, street={self.street})>"

    def to_dict(self):
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
            session.commit()
            return address.address_id
        
    @staticmethod
    def get_address(address_id: int):
        """Get address by address id."""
        with session_scope() as session:
            address = session.query(Address).filter_by(address_id=address_id).first()
            return address.to_dict()
        
    @staticmethod
    def update_address(address_id: int, address_data: dict):
        """Update an address."""
        with session_scope() as session:
            address = session.query(Address).filter_by(address_id=address_id).first()
            for key, value in address_data.items():
                setattr(address, key, value)
            session.commit()
            return address.to_dict()