"""
    Represents a parking slot entity in the database.

    Contains information about a parking slot including its unique identifier,
    establishment association, slot code, vehicle type, status, and timestamps.
    Maintains relationships with VehicleType and ParkingEstablishment models.
"""

# pylint: disable=R0903, C0115, C0413, E1102, C0415, R0801

from sqlalchemy import (
    DECIMAL,
    Column,
    Integer,
    VARCHAR,
    Enum,
    DateTime,
    ForeignKey,
    Boolean,
    and_,
    SMALLINT,
)
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.engine import get_session


class Slot(Base):  # pylint: disable=R0903 disable=C0115

    __tablename__ = "slot"

    slot_id = Column(Integer, primary_key=True)
    establishment_id = Column(
        Integer, ForeignKey("parking_establishment.establishment_id"), nullable=False
    )
    slot_code = Column(VARCHAR(45), nullable=False)
    vehicle_type_id = Column(
        Integer,
        ForeignKey("vehicle_type.vehicle_type_id"),
    )
    slot_status = Column(
        Enum("open", "reserved", "occupied"), nullable=False, default="open"
    )
    is_active = Column(Boolean, nullable=False, default=True)
    slot_multiplier = Column(DECIMAL(3, 2), nullable=False, default=1.00)
    is_premium = Column(Boolean, nullable=False, default=False)
    slot_features = Column(
        Enum("standard", "covered", "vip", "disabled", "ev_charging"),
        nullable=False,
        default="standard",
    )
    floor_level = Column(SMALLINT, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    vehicle_type = relationship(
        "VehicleType",
        back_populates="slot",
    )
    parking_establishment = relationship(
        "ParkingEstablishment",
        back_populates="slot",
    )
    parking_transaction = relationship(
        "ParkingTransaction",
        back_populates="slot",
    )

    def to_dict(self):  # pylint: disable=C0116
        return {
            "slot_id": self.slot_id,
            "establishment_id": self.establishment_id,
            "slot_code": str(self.slot_code),
            "vehicle_type_id": self.vehicle_type_id,
            "slot_status": self.slot_status,
            "is_active": self.is_active,
            "slot_multiplier": self.slot_multiplier,
            "is_premium": self.is_premium,
            "slot_features": self.slot_features,
            "floor_level": self.floor_level,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def calculate_total_multiplier(self) -> float:
        """Calculate final rate multiplier including vehicle type and slot factors"""
        base_multiplier = float(self.vehicle_type.base_rate_multiplier)
        slot_multiplier = float(self.slot_multiplier)  # type: ignore

        # Additional multipliers based on features
        feature_multipliers = {"covered": 1.2, "vip": 1.5, "ev_charging": 1.3}

        feature_mult = feature_multipliers.get(self.slot_features, 1.0)  # type: ignore

        return base_multiplier * slot_multiplier * feature_mult


class GettingSlotsOperations:  # pylint: disable=R0903
    """Class that provides operations for retrieving slots from the database.

    Contains methods to fetch slots based on different criteria such as vehicle type,
    establishment ID, and slot code. Each method handles database operations and
    returns the appropriate slot objects.

    Raises:
        OperationalError: If there is a database operation error in any method.
    """

    @staticmethod
    def get_slot_status(slot_code: str):
        """Get slot status by slot code."""
        session = get_session()
        try:
            slot = session.query(Slot).filter(Slot.slot_code == slot_code).first()
            if slot:
                return slot.slot_status
            return None
        except OperationalError as error:
            raise error
        finally:
            session.close()

    @staticmethod
    def get_all_slots(establishment_id: int):
        """Retrieves all slots from the database.

        Returns:
            list[Slot]: List of all slot objects in the database.

        Raises:
            OperationalError: If there is a database operation error.
        """
        from app.models.vehicle_type import VehicleType

        session = get_session()
        try:
            slots = (
                session.query(
                    Slot,
                    VehicleType.code.label("vehicle_type_code"),
                    VehicleType.name.label("vehicle_type_name"),
                    VehicleType.size_category.label("size_category"),
                    VehicleType.base_rate_multiplier.label("base_rate"),
                )
                .join(VehicleType, Slot.vehicle_type_id == VehicleType.vehicle_id)
                .where(Slot.establishment_id == establishment_id)
            )
            slots_list = []
            for slot in slots:
                slot_dict = slot[0].to_dict()
                slot_dict.update(
                    {
                        "vehicle_type_code": slot[1],
                        "vehicle_type_name": slot[2],
                        "vehicle_size_category": slot[3],
                        "base_rate": slot[4],
                    }
                )
                slots_list.append(slot_dict)
            return slots_list
        except OperationalError as error:
            raise error


class SlotOperation:  # pylint: disable=R0903
    """
    Class for managing parking slot creation operations in the database.

    Methods:
        create_slot(slot_data: dict): Creates a new parking slot with the provided slot data.
            Validates vehicle type existence before creation.

    Raises:
        VehicleTypeDoesNotExist: If the specified vehicle type does not exist.
        OperationalError, DataError, IntegrityError, DatabaseError: If any database error occurs.
    """
    @staticmethod
    def get_slot_info(slot_code: str, establishment_id: int):
        """Get Slot info including the benefits and features"""
        from app.models.vehicle_type import VehicleType

        session = get_session()
        try:
            slot_info = (
                session.query(Slot)
                .where(
                    and_(
                        Slot.slot_code == slot_code,
                        Slot.establishment_id == establishment_id,
                    )
                )
                .first()
            )
            vehicle_type_info = (
                session.query(VehicleType)
                .where(VehicleType.vehicle_id == slot_info.vehicle_type_id)
                .first()
            )
            if not slot_info:
                raise ValueError("Slot not found")
            info_dict = slot_info.to_dict()
            type_info_dict = vehicle_type_info.to_dict()
            return {
                "slot_info": info_dict,
                "vehicle_type_info": type_info_dict,
            }
        except (OperationalError, DatabaseError) as error:
            raise error
        finally:
            session.close()


class TransactionOperation:
    """Class for operations related to parking transactions"""

    @staticmethod
    def get_slot_establishment_info(establishment_uuid: bytes, slot_code: str):
        """Get slot and establishment information.

        Args:
            establishment_uuid (bytes): UUID of establishment in bytes
            slot_code (str): Unique slot identifier

        Returns:
            dict: JSON-serializable dictionary with establishment and slot info

        Raises:
            OperationalError: Database operation error
            DatabaseError: General database error
        """
        from app.models.parking_establishment import ParkingEstablishment

        session = get_session()
        try:
            establishment_info = (
                session.query(
                    ParkingEstablishment.name,
                    ParkingEstablishment.hourly_rate,
                    ParkingEstablishment.address,
                    ParkingEstablishment.longitude,
                    ParkingEstablishment.latitude,
                )
                .where(ParkingEstablishment.uuid == establishment_uuid)
                .first()
            )

            slot_info = (
                session.query(
                    Slot.slot_id,
                    Slot.slot_code,
                    Slot.is_premium,
                    Slot.slot_features,
                    Slot.floor_level,
                    Slot.slot_multiplier,
                    Slot.vehicle_type_id,
                )
                .where(Slot.slot_code == slot_code)
                .first()
            )

            if not establishment_info or not slot_info:
                raise ValueError("Establishment or slot not found")

            # Convert to serializable dictionary
            return {
                "establishment_info": {
                    "name": establishment_info[0],
                    "hourly_rate": float(establishment_info[1]),
                    "address": establishment_info[2],
                    "longitude": float(establishment_info[3]),
                    "latitude": float(establishment_info[4]),
                },
                "slot_info": {
                    "slot_id": slot_info[0],
                    "slot_code": slot_info[1],
                    "is_premium": slot_info[2],
                    "slot_features": slot_info[3],
                    "floor_level": slot_info[4],
                    "slot_multiplier": float(slot_info[5]),
                    "vehicle_type_id": slot_info[6],
                },
            }
        except (OperationalError, DatabaseError) as error:
            raise error
        finally:
            session.close()
