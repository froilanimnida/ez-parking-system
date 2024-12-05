""" Represents the ORM model for the address table. This is connected to the business_profile table. """

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String, Numeric, Text, TIMESTAMP, func
)
from sqlalchemy.orm import relationship

from app.models.base import Base



class Address(Base):
    __tablename__ = 'address'
    
    address_id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('business_profile.profile_id'), nullable=False)
    street = Column(String(255), nullable=False)
    barangay = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)
    postal_code = Column(String(10), nullable=False)
    landmarks = Column(Text)
    longitude = Column(Numeric(9, 6), nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    business_profile = relationship("BusinessProfile", backref="addresses")
    
    def __repr__(self):
        return f"<Address(address_id={self.address_id}, profile_id={self.profile_id}, street={self.street})>"
    
    def to_dict(self):
        return {
            'address_id': self.address_id,
            'profile_id': self.profile_id,
            'street': self.street,
            'barangay': self.barangay,
            'city': self.city,
            'province': self.province,
            'postal_code': self.postal_code,
            'landmarks': self.landmarks,
            'longitude': str(self.longitude),
            'latitude': str(self.latitude),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
