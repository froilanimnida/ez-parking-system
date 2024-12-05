"""This module contains the SQLAlchemy model for the Facilities table."""


from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class Facilities(Base):
    """ Facilities Model """
    __tablename__ = 'facilities'
    
    facility_id = Column(Integer, primary_key=True, autoincrement=True)
    establishment_id = Column(Integer, ForeignKey('parking_establishment.establishment_id'), nullable=True)
    lighting = Column(Text, nullable=True)
    accessibility = Column(Text, nullable=True)
    nearby_landmarks = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        UniqueConstraint('establishment_id', name='unique_establishment_facilities'),
    )
    
    parking_establishment = relationship("ParkingEstablishment", backref="facilities")
    
    def __repr__(self):
        return f"<Facilities(facility_id={self.facility_id}, establishment_id={self.establishment_id})>"
