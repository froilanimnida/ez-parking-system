""" Represents the banned plates in the database."""

from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    ForeignKey,
    DATETIME,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, DatabaseError

from app.models.base import Base
from app.utils.engine import get_session


class BannedPlate(Base):  # pylint: disable=R0903
    """Represents the banned plates in the database."""

    __tablename__ = "banned_plate"
    id = Column(Integer, primary_key=True, autoincrement=True)
    plate_number = Column(
        VARCHAR(10), ForeignKey("user.plate_number"), unique=True, nullable=False
    )
    reason = Column(VARCHAR(255), nullable=False)
    banned_at = Column(
        DATETIME, nullable=False, default=func.now()  # pylint: disable=E1102
    )
    banned_by = Column(Integer, ForeignKey("user.user_id"), nullable=False)

    # user = relationship(
    #     "User", back_populates="banned_plate", foreign_keys=[plate_number]
    # )


class BannedPlateOperations:
    """Operations for the BannedPlate model."""

    @staticmethod
    def ban_plate(plate_number: str, reason: str, banned_by: int) -> None:
        """Ban a plate number."""
        session = get_session()
        try:
            banned_plate = BannedPlate(
                plate_number=plate_number, reason=reason, banned_by=banned_by
            )
            session.add(banned_plate)
            session.commit()
        except (
            DataError,
            IntegrityError,
            OperationalError,
            DatabaseError,
        ) as exception:
            session.rollback()
            raise exception
        finally:
            session.close()

    @staticmethod
    def unban_plate(plate_number: str) -> None:
        """Unban a plate number."""
        session = get_session()
        try:
            session.query(BannedPlate).filter(
                BannedPlate.plate_number == plate_number
            ).delete()
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as exc:
            session.rollback()
            raise exc
        finally:
            session.close()

    @staticmethod
    def get_banned_plates() -> list[BannedPlate]:
        """Get all banned plates."""
        session = get_session()
        try:
            return session.query(BannedPlate).all()
        except (OperationalError, DatabaseError) as exc:
            raise exc
        finally:
            session.close()

    @staticmethod
    def get_banned_plate(plate_number: str) -> BannedPlate:
        """Get a banned plate by plate number."""
        session = get_session()
        try:
            return (
                session.query(BannedPlate)
                .filter(BannedPlate.plate_number == plate_number)
                .first()
            )
        except (OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()
