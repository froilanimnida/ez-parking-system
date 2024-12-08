"""This module contains the models and operations for the audit logs."""

# pylint: disable=R0801

from sqlalchemy import Column, Integer, VARCHAR, DateTime, Enum, ForeignKey, BINARY
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope
from app.utils.uuid_utility import UUIDUtility


class AuditLog(Base):  # pylint: disable=too-few-public-methods
    """Model for audit logs."""

    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(BINARY(16), nullable=False)
    admin_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    table_name = Column(VARCHAR(50), nullable=False)
    action_type = Column(Enum("CREATE", "UPDATE", "DELETE"), nullable=False)
    details = Column(VARCHAR(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="audit_log")

    # user = relationship("User", back_populates="audit")
    def to_dict(self):  # pylint: disable=missing-function-docstring
        if self is None:
            return {}
        uuid_utility = UUIDUtility()
        return {
            "id": self.id,
            "uuid": uuid_utility.format_uuid(uuid_utility.binary_to_uuid(self.uuid)),
            "admin_id": self.admin_id,
            "table_name": self.table_name,
            "action_type": self.action_type,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class AuditLogRepository:  # pylint: disable=too-few-public-methods
    @staticmethod
    def create_audit_log(log_data: dict):  # pylint: disable=missing-function-docstring
        with session_scope() as session:
            new_audit_log = AuditLog(**log_data)
            session.add(new_audit_log)
            session.flush()
            return new_audit_log.id
        
    @staticmethod
    def get_audit_log(audit_uuid: bytes):
        with session_scope() as session:
            audit_log = session.query(AuditLog).filter_by(uuid=audit_uuid).first()
            return audit_log.to_dict()
        
    @staticmethod
    def get_all_audit_logs():
        with session_scope() as session:
            audit_logs = session.query(AuditLog).all()
            return [audit_log.to_dict() for audit_log in audit_logs]

