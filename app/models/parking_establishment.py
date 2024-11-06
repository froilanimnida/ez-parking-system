""" Class represents parking establishment model in the database. """

from sqlalchemy import (
    VARCHAR,
    Boolean,
    Column,
    Integer,
    BINARY,
    TIME,
    DECIMAL,
    and_,
    func,
    update,
    join,
    select,
    ForeignKey,
    TIMESTAMP,
)
from sqlalchemy.exc import OperationalError, DatabaseError, IntegrityError, DataError
from sqlalchemy.orm import relationship

from app.exceptions.establishment_lookup_exception import (
    EstablishmentDoesNotExist,
    EstablishmentEditsNotAllowedException,
)
from app.models.base import Base
from app.models.slot import Slot
from app.utils.engine import get_session


class ParkingEstablishment(Base):  # pylint: disable=R0903
    """Class represents parking establishment model in the database."""

    __tablename__ = "parking_establishment"

    establishment_id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    uuid = Column(BINARY(16), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    address = Column(VARCHAR(255), nullable=False)
    contact_number = Column(VARCHAR(25), nullable=False)
    opening_time = Column(TIME, nullable=False)
    closing_time = Column(TIME, nullable=False)
    is_24_hours = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    hourly_rate = Column(DECIMAL(8, 2), nullable=False)
    longitude = Column(DECIMAL(9, 6), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=False)

    slot = relationship(
        "Slot", back_populates="parking_establishment", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="parking_establishment")

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
    def is_establishment_exists(establishment_id: int):
        """Check if the parking establishment exists in the database."""
        session = get_session()
        try:
            return (
                session.query(ParkingEstablishment)
                .filter(ParkingEstablishment.establishment_id == establishment_id)
                .count()
                > 0
            )
        except OperationalError as err:
            raise err

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

    @staticmethod
    def get_all_establishment_by_vehicle_type_accommodation(vehicle_type_id: int):
        """Get all parking establishments by vehicle type accommodation."""
        session = get_session()
        try:
            establishments = session.execute(
                select(ParkingEstablishment)
                .select_from(
                    join(
                        ParkingEstablishment,
                        Slot,
                        ParkingEstablishment.establishment_id == Slot.establishment_id,
                    )
                )
                .where(Slot.vehicle_type_id == vehicle_type_id)
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
                manager_id=establishment_data.get("manager_id"),
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
            is_establishment_exists = (
                GetEstablishmentOperations.is_establishment_exists(establishment_id)
            )
            if not is_establishment_exists:
                raise EstablishmentDoesNotExist("Establishment does not exist")
            is_allowed_to_make_edits = (
                session.query(ParkingEstablishment).filter(
                    and_(
                        ParkingEstablishment.establishment_id == establishment_id,
                        ParkingEstablishment.manager_id
                        == establishment_data.get("manager_id"),
                    )
                )
            ).count()
            if not is_allowed_to_make_edits:
                raise EstablishmentEditsNotAllowedException(
                    "You are not allowed to make edits to this establishment."
                )
            session.execute(
                update(ParkingEstablishment)
                .where(
                    and_(
                        ParkingEstablishment.establishment_id == establishment_id,
                        ParkingEstablishment.manager_id
                        == establishment_data.get("manager_id"),
                    )
                )
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
