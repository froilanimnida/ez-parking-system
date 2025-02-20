"""This module contains the models and operations for the audit logs."""
# pylint: disable=C0301, C0303, E1102
from datetime import timedelta

from typing import overload
from uuid import uuid4

from sqlalchemy import Column, Integer, VARCHAR, DateTime, Enum, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.user import User
from app.models.parking_transaction import ParkingTransaction
from app.models.base import Base
from app.utils.db import session_scope
from app.utils.timezone_utils import get_current_time


class AuditLog(Base):  # pylint: disable=too-few-public-methods
    """Model for audit logs."""
    __tablename__ = "audit_log"
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    action_type = Column(Enum("CREATE", "UPDATE", "DELETE"), nullable=False)
    performed_by = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    target_user = Column(Integer, ForeignKey("user.user_id"), nullable=True)
    details = Column(VARCHAR(255), nullable=False)
    performed_at = Column(DateTime, nullable=False)
    ip_address = Column(VARCHAR(15), nullable=False)
    user_performed_by = relationship(
        "User",
        back_populates="performed_audits",
        foreign_keys=[performed_by]
    )
    user_target = relationship(
        "User",
        back_populates="targeted_audits",
        foreign_keys=[target_user]
    )

    # user = relationship("User", back_populates="audit")
    def to_dict(self):  # pylint: disable=missing-function-docstring
        if self is None:
            return {}
        return {
            "audit_id": self.audit_id,
            "uuid": str(self.uuid),
            "action_type": self.action_type,
            "performed_by": self.performed_by,
            "target_user": self.target_user,
            "details": self.details,
            "performed_at": self.performed_at,
            "ip_address": self.ip_address
        }


class AuditLogRepository:
    """Wraps the logic for creating, updating, and deleting audit logs."""
    @staticmethod
    def create_audit_log(log_data: dict):
        """Create a new audit log."""
        with session_scope() as session:
            new_audit_log = AuditLog(**log_data)
            session.add(new_audit_log)
            session.flush()
            session.refresh(new_audit_log)
            return new_audit_log.audit_id
    @staticmethod
    def get_audit_log(audit_uuid: bytes):
        """Get an audit log by its UUID."""
        with session_scope() as session:
            audit_log = session.query(AuditLog).filter_by(uuid=audit_uuid).first()
            return audit_log.to_dict()
    @staticmethod
    def get_all_audit_logs():
        """Get all the audit logs."""
        with session_scope() as session:
            audit_logs = session.query(AuditLog).all()
            return [audit_log.to_dict() for audit_log in audit_logs]
    @staticmethod
    @overload
    def delete_audit_log(audit_id: int):
        """Delete audit log by audit id."""
    @staticmethod
    @overload
    def delete_audit_log(audit_uuid: bytes):
        """Delete audit log by audit uuid."""
    @staticmethod
    def delete_audit_log(audit_id: int = None, audit_uuid: bytes = None):
        """Delete audit log by audit id or audit uuid."""
        with session_scope() as session:
            if audit_id:
                audit_log = session.query(AuditLog).get(audit_id)
            else:
                audit_log = session.query(AuditLog).filter_by(uuid=audit_uuid).first()
            session.delete(audit_log)
            session.flush()
            return audit_log


class AdminAnalyticsAndReports:
    """Service class for generating admin analytics and reports."""
    @staticmethod
    def get_user_activity_summary(days: int = 30) -> list:
        """Analyze user activity patterns.
        
        Returns list of active users with their transaction counts and revenue generated
        """
        with session_scope() as session:
            query = session.query(
                User.user_id,
                User.email,
                User.role,
                func.count(ParkingTransaction.transaction_id).label('transaction_count'),
                func.sum(ParkingTransaction.amount_due).label('total_spent')
            ).join(
                ParkingTransaction
            ).filter(
                ParkingTransaction.created_at >= func.current_date() - text(f'interval \'{days} days\''),
                ParkingTransaction.status != 'cancelled'
            ).group_by(User.user_id)
    
            results = query.all()
            return [{
                'user_id': result.user_id,
                'email': result.email,
                'role': result.role.value,
                'transaction_count': result.transaction_count,
                'total_spent': float(result.total_spent or 0)
            } for result in results]
    
    @staticmethod
    def get_new_user_growth(months: int = 12) -> list:
        """Track new user registrations over time.
        """
        with session_scope() as session:
            query = session.query(
                func.date_trunc('month', User.created_at).label('month'),
                func.count(User.user_id).label('new_users')
            ).filter(
                User.created_at >= func.current_date() - text(f'interval \'{months} months\'')
            ).group_by('month').order_by('month')
    
            results = query.all()
            return [{
                'month': result.month.strftime('%Y-%m'),
                'new_users': result.new_users
            } for result in results]
    
    @staticmethod
    def get_user_verification_stats() -> dict:
        """Analyze user verification status metrics.
        """
        with session_scope() as session:
            total_users = session.query(func.count(User.user_id)).scalar()
            verified_users = session.query(
                func.count(User.user_id)
            ).filter(User.is_verified is True).scalar()
            return {
                'total_users': total_users,
                'verified_users': verified_users,
                'unverified_users': total_users - verified_users,
                'verification_rate': (verified_users / total_users * 100) if total_users > 0 else 0
            }
    
    @staticmethod
    def get_user_role_distribution() -> list:
        """Analyze distribution of user roles.
        """
        with session_scope() as session:
            query = session.query(
                User.role,
                func.count(User.user_id).label('count')
            ).group_by(User.role)
    
            results = query.all()
            return [{
                'role': result.role.value,
                'count': result.count
            } for result in results]
    
    @staticmethod
    def get_user_transaction_frequency(days: int = 90) -> list:
        """Analyze how frequently users make transactions.
        """
        with session_scope() as session:
            query = session.query(
                User.user_id,
                User.email,
                func.count(ParkingTransaction.transaction_id).label('transaction_count'),
                func.min(ParkingTransaction.created_at).label('first_transaction'),
                func.max(ParkingTransaction.created_at).label('last_transaction')
            ).join(
                ParkingTransaction
            ).filter(
                ParkingTransaction.created_at >= func.current_date() - text(f'interval \'{days} days\'')
            ).group_by(User.user_id).order_by(text('transaction_count DESC'))
    
            results = query.all()
            return [{
                'user_id': result.user_id,
                'email': result.email,
                'transaction_count': result.transaction_count,
                'first_transaction': result.first_transaction.isoformat(),
                'last_transaction': result.last_transaction.isoformat()
            } for result in results]
    
    @staticmethod
    def get_top_spenders(limit: int = 10) -> list:
        """Identify top spending users.
        """
        with session_scope() as session:
            query = session.query(
                User.user_id,
                User.email,
                func.sum(ParkingTransaction.amount_due).label('total_spent')
            ).join(
                ParkingTransaction
            ).filter(
                ParkingTransaction.payment_status == 'completed'
            ).group_by(
                User.user_id
            ).order_by(text('total_spent DESC')).limit(limit)
    
            results = query.all()
            return [{
                'user_id': result.user_id,
                'email': result.email,
                'total_spent': float(result.total_spent or 0)
            } for result in results]
    
    @staticmethod
    def get_user_retention_analysis(days: int = 30) -> dict:
        """Analyze user retention metrics.
        """
        with session_scope() as session:
            date_threshold = get_current_time() - timedelta(days=days)
            
            total_users = session.query(func.count(User.user_id)).scalar()
            active_users = session.query(func.count(User.user_id)).join(
                ParkingTransaction
            ).filter(
                ParkingTransaction.created_at >= date_threshold
            ).distinct().scalar()
    
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'retention_rate': (active_users / total_users * 100) if total_users > 0 else 0
            }
