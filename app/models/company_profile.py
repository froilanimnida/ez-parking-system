""" Business Profile Model (Postgres SCHEMA) """

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

    def __repr__(self):
        return f"<CompanyProfile(profile_id={self.profile_id}, user_id={self.user_id}, owner_type={self.owner_type})>"
