"""Model for storing parking manager file references."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.engine import get_session


class ParkingManagerFile(Base):  # pylint: disable=too-few-public-methods
    """Model for storing parking manager file references."""

    __tablename__ = "parking_manager_files"

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    manager_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

    manager = relationship("User", back_populates="files")


class ParkingManagerFileRepository:
    """Repository for parking manager file operations."""

    @staticmethod
    def add_file(manager_id: int, file_name: str, file_url: str):
        """Add a file uploaded by a parking manager."""
        session = get_session()
        try:
            new_file = ParkingManagerFile(
                manager_id=manager_id,
                file_name=file_name,
                file_url=file_url,
                uploaded_at=datetime.now(timezone.utc),
            )
            session.add(new_file)
            session.commit()
            return new_file
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_files_by_manager(manager_id: int):
        """ Get all files uploaded by a parking manager. """
        session = get_session()
        try:
            files = (
                session.query(ParkingManagerFile).filter_by(manager_id=manager_id).all()
            )
            return files
        except Exception as e:
            raise e
        finally:
            session.close()
