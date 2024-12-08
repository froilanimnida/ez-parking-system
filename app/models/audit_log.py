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
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(BINARY(16), nullable=False)
    action_type = Column(Enum("CREATE", "UPDATE", "DELETE"), nullable=False)
    performed_by = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    target_user = Column(Integer, ForeignKey("user.user_id"), nullable=True)
    details = Column(VARCHAR(255), nullable=False)
    performed_at = Column(DateTime, nullable=False)
    ip_address = Column(VARCHAR(15), nullable=False)
    
    user = relationship("User", back_populates="audit_log")

    # user = relationship("User", back_populates="audit")
    def to_dict(self):  # pylint: disable=missing-function-docstring
        if self is None:
            return {}
        uuid_utility = UUIDUtility()
        return {
            "audit_id": self.audit_id,
            "uuid": uuid_utility.format_uuid(uuid_utility.binary_to_uuid(self.uuid)),
            "action_type": self.action_type,
            "performed_by": self.performed_by,
            "target_user": self.target_user,
            "details": self.details,
            "performed_at": self.performed_at,
            "ip_address": self.ip_address
        }


class AuditLogRepository:  # pylint: disable=too-few-public-methods
    @staticmethod
    def create_audit_log(log_data: dict):  # pylint: disable=missing-function-docstring
        with session_scope() as session:
            new_audit_log = AuditLog(**log_data)
            session.add(new_audit_log)
            session.flush()
            return new_audit_log.audit_id
        
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

