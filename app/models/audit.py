"""This module contains the models and operations for the audit logs."""

# pylint: disable=R0801

from sqlalchemy import Column, Integer, VARCHAR, DateTime, Enum, ForeignKey, BINARY
from sqlalchemy.exc import DatabaseError, DataError, IntegrityError, OperationalError
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.engine import get_session
from app.utils.uuid_utility import UUIDUtility


class Audit(Base):  # pylint: disable=too-few-public-methods
    """Model for audit logs."""
    __tablename__ = "audit"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(BINARY(16), nullable=False)
    admin_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    table_name = Column(VARCHAR(50), nullable=False)
    action_type = Column(Enum("CREATE", "UPDATE", "DELETE"), nullable=False)
    details = Column(VARCHAR(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    user = relationship("User", back_populates="audit")
    def to_dict(self):  # pylint: disable=missing-function-docstring
        uuid_utility = UUIDUtility()
        return {
            "id": self.id,
            "uuid": uuid_utility.binary_to_uuid(self.uuid),
            "admin_id": self.admin_id,
            "table_name": self.table_name,
            "action_type": self.action_type,
            "details": self.details,
            "timestamp": self.timestamp,
        }

class AuditOperations:
    """Wraps the logic for audit operations."""
    @staticmethod
    def create_audit_log(audit_data: dict):  # pylint: disable=missing-function-docstring
        session = get_session()
        try:
            audit = Audit(
                uuid=audit_data["uuid"],
                admin_id=audit_data["admin_id"],
                table_name=audit_data["table_name"],
                action_type=audit_data["action_type"],
                details=audit_data["details"],
            )
            session.add(audit)
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as error:
            session.rollback()
            raise error
        finally:
            session.close()
    @staticmethod
    def get_all_audit_logs(): # pylint: disable=missing-function-docstring
        session = get_session()
        try:
            audit_logs = session.query(Audit).all()
        except (DatabaseError, DataError, OperationalError) as error:
            session.rollback()
            raise error
        finally:
            session.close()
        return audit_logs
    @staticmethod
    def delete_audit_log(audit_uuid: bytes):  # pylint: disable=missing-function-docstring
        session = get_session()
        try:
            audit = session.query(Audit).filter_by(uuid=audit_uuid).first()
            session.delete(audit)
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as error:
            session.rollback()
            raise error
        finally:
            session.close()
