""" Class represents parking establishment model in the database. """

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Integer,
    BINARY,
    TIME,
    DateTime,
    DECIMAL,
    func,
    update,
)
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError, DataError
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.engine import get_session


class ParkingEstablishment(Base):  # pylint: disable=R0903
    """Class represents parking establishment model in the database."""

    __tablename__ = "parking_establishment"

    establishment_id = Column(Integer, primary_key=True)
    uuid = Column(BINARY(16), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    address = Column(VARCHAR(255), nullable=False)
    contact_number = Column(VARCHAR(25), nullable=False)
    opening_time = Column(TIME, nullable=False)
    closing_time = Column(TIME, nullable=False)
    is_24_hours = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    hourly_rate = Column(DECIMAL(8, 2), nullable=False)
    longitude = Column(DECIMAL(9, 6), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=False)

    slot = relationship(
        "Slot", back_populates="parking_establishment", cascade="all, delete-orphan"
    )

    def to_dict(self):
        """Convert the ParkingEstablishment instance to a dictionary."""
        return {
            "establishment_id": self.establishment_id,
            "uuid": self.uuid.hex(),
            "name": self.name,
            "address": self.address,
            "contact_number": self.contact_number,
            "opening_time": str(self.opening_time),
            "closing_time": str(self.closing_time),
            "is_24_hours": self.is_24_hours,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "hourly_rate": float(self.hourly_rate),  # type: ignore
            "longitude": float(self.longitude),  # type: ignore
            "latitude": float(self.latitude),  # type: ignore
        }


class GetEstablishmentOperations:
    """Class for operations related to parking establishment (Getting)."""

    @staticmethod
    def get_all_establishments():
        """Get all parking establishments."""
        session = get_session()
        try:
            establishments = session.query(ParkingEstablishment).all()
            return [establishment.to_dict() for establishment in establishments]
        except OperationalError as err:
            raise err

    @staticmethod
    def get_establishment_by_id(establishment_id: int):
        """Get parking establishment by ID."""
        session = get_session()
        try:
            establishment = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.establishment_id == establishment_id)
                .first()
            )
            return establishment
        except OperationalError as err:
            raise err

    @staticmethod
    def get_nearest_establishments(latitude: float, longitude: float):
        """Get nearest parking establishments based on the current user location."""
        # Radius of Earth in kilometers
        session = get_session()
        try:
            radius_km = 6371

            establishments = (
                session.query(ParkingEstablishment)
                .filter(
                    ParkingEstablishment.latitude.isnot(None),
                    ParkingEstablishment.longitude.isnot(None),
                )
                .order_by(
                    (
                        radius_km
                        * func.acos(
                            func.cos(func.radians(latitude))
                            * func.cos(func.radians(ParkingEstablishment.latitude))
                            * func.cos(
                                func.radians(ParkingEstablishment.longitude)
                                - func.radians(longitude)
                            )
                            + func.sin(func.radians(latitude))
                            * func.sin(func.radians(ParkingEstablishment.latitude))
                        )
                    ).asc()
                )
            ).all()
            return [establishment.to_dict() for establishment in establishments]
        except OperationalError as error:
            raise error

    @staticmethod
    def get_24_hours_establishments():
        """Get parking establishments that are open 24 hours."""
        session = get_session()
        try:
            establishments = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.is_24_hours)
                .all()
            )
            return [establishment.to_dict() for establishment in establishments]
        except OperationalError as err:
            raise err


class CreateEstablishmentOperations:  # pylint: disable=R0903
    """Class for operations related to parking establishment (Creating)."""

    @staticmethod
    def create_establishment(establishment_data: dict):
        """Create a new parking establishment."""
        session = get_session()
        try:
            establishment = ParkingEstablishment(
                uuid=establishment_data.get("uuid"),
                name=establishment_data.get("name"),
                address=establishment_data.get("address"),
                contact_number=establishment_data.get("contact_number"),
                opening_time=establishment_data.get("opening_time"),
                closing_time=establishment_data.get("closing_time"),
                is_24_hours=establishment_data.get("is_24_hours"),
                created_at=establishment_data.get("created_at"),
                updated_at=establishment_data.get("updated_at"),
                hourly_rate=establishment_data.get("hourly_rate"),
                longitude=establishment_data.get("longitude"),
                latitude=establishment_data.get("latitude"),
            )
            session.add(establishment)
            session.commit()
        except (OperationalError, DatabaseError, DataError, IntegrityError) as err:
            session.rollback()
            raise err
        finally:
            session.close()


class UpdateEstablishmentOperations:  # pylint: disable=R0903
    """Class for operations related to parking establishment (Updating)."""

    @staticmethod
    def update_establishment(establishment_id: int, establishment_data: dict):
        """Update a parking establishment."""
        session = get_session()
        try:
            session.execute(
                update(ParkingEstablishment)
                .where(ParkingEstablishment.establishment_id == establishment_id)
                .values(
                    {
                        "name": establishment_data.get("name"),
                        "address": establishment_data.get("address"),
                        "contact_number": establishment_data.get("contact_number"),
                        "opening_time": establishment_data.get("opening_time"),
                        "closing_time": establishment_data.get("closing_time"),
                        "is_24_hours": establishment_data.get("is_24_hours"),
                        "hourly_rate": establishment_data.get("hourly_rate"),
                        "longitude": establishment_data.get("longitude"),
                        "latitude": establishment_data.get("latitude"),
                        "updated_at": establishment_data.get("updated_at"),
                    }
                )
            )
            session.commit()
        except (OperationalError, DatabaseError, DataError, IntegrityError) as err:
            session.rollback()
            raise err
        finally:
            session.close()


class DeleteEstablishmentOperations:  # pylint: disable=R0903
    """Class for operations related to parking establishment (Deleting)."""

    @staticmethod
    def delete_establishment(establishment_id: int):
        """Delete a parking establishment."""
        session = get_session()
        try:
            establishment = (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.establishment_id == establishment_id)
                .first()
            )
            session.delete(establishment)
            session.commit()
        except (OperationalError, DatabaseError, DataError, IntegrityError) as err:
            session.rollback()
            raise err
        finally:
            session.close()
