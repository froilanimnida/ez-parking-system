""" Business Profile Model (Postgres SCHEMA) """
from typing import overload, Union

from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class CompanyProfile(Base):  # pylint: disable=too-few-public-methods
    """Business Profile Model"""

    __tablename__ = "company_profile"
    __table_args__ = (
        CheckConstraint(
            "owner_type IN ('individual', 'company')",
            name="company_profile_owner_type_check",
        ),
    )

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), unique=True)
    owner_type = Column(String(20), nullable=False)
    company_name = Column(String(255))
    company_reg_number = Column(String(50))
    tin = Column(String(20))
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp()
    )

    user = relationship("User", back_populates="company_profile")
    parking_establishment = relationship("ParkingEstablishment", back_populates="company_profile")

    def __repr__(self):
        return f"<CompanyProfile(profile_id={self.profile_id}, user_id={self.user_id}, owner_type={self.owner_type})>"
    
    def to_dict(self):
        if self is None:
            return {}
        return {
            "profile_id": self.profile_id,
            "user_id": self.user_id,
            "owner_type": self.owner_type,
            "company_name": self.company_name,
            "company_reg_number": self.company_reg_number,
            "tin": self.tin,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class CompanyProfileRepository:
    """Company Profile Repository"""

    @staticmethod
    def create_new_company_profile(profile_data: dict):
        """Create a new company profile."""
        with session_scope() as session:
            company_profile = CompanyProfile(**profile_data)
            session.add(company_profile)
            session.commit()
            return company_profile.profile_id
        
    @staticmethod
    @overload
    def get_company_profile(user_id: int):
        """Get company profile by user id."""
        ...
    
    @staticmethod
    @overload
    def get_company_profile(profile_id: int):
        """Get company profile by profile id."""
        ...
    
    @staticmethod
    def get_company_profile(profile_id: int = None, user_id: int = None) -> Union[dict, list]:
        """Get company profile by user id or profile id."""
        if profile_id:
            with session_scope() as session:
                return session.query(CompanyProfile).filter_by(profile_id=profile_id).first()
        elif user_id:
            with session_scope() as session:
                return session.query(CompanyProfile).filter_by(user_id=user_id).first()
        return {}
        
