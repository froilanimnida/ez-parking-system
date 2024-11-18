"""
    Represents a parking slot entity in the database.

    Contains information about a parking slot including its unique identifier,
    establishment association, slot code, vehicle type, status, and timestamps.
    Maintains relationships with VehicleType and ParkingEstablishment models.
"""

# pylint: disable=R0903, C0115, C0413, E1102, C0415

from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    Enum,
    DateTime,
    ForeignKey,
    select,
    Boolean,
    func,
    and_,
    update,
)
from sqlalchemy.orm import relationship
from sqlalchemy.exc import OperationalError, DataError, IntegrityError, DatabaseError

from app.exceptions.slot_lookup_exceptions import SlotNotFound
from app.models.base import Base
from app.models.vehicle_type import VehicleTypeOperations
from app.exceptions.vehicle_type_exceptions import VehicleTypeDoesNotExist
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
        ForeignKey("vehicle_type.vehicle_id"),
    )
    slot_status = Column(
        Enum("open", "reserved", "occupied"), nullable=False, default="open"
    )
    is_active = Column(Boolean, nullable=False, default=True)
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
            "slot_code": self.slot_code,
            "vehicle_type_id": self.vehicle_type_id,
            "slot_status": self.slot_status,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class GettingSlotsOperations:  # pylint: disable=R0903
    """Class that provides operations for retrieving slots from the database.

    Contains methods to fetch slots based on different criteria such as vehicle type,
    establishment ID, and slot code. Each method handles database operations and
    returns the appropriate slot objects.

    Raises:
        OperationalError: If there is a database operation error in any method.
    """

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
                        "size_category": slot[3],
                    }
                )
                slots_list.append(slot_dict)
            return slots_list
        except OperationalError as error:
            raise error

    @staticmethod
    def get_slots_by_vehicle_type(vehicle_type_id: int, establishment_id: int):
        """Retrieves slots from the database filtered by vehicle type and establishment.

        Args:
            vehicle_type_id (int): The ID of the vehicle type to filter by.
            establishment_id (int): The ID of the parking establishment to filter by.

        Returns:
            list[Slot]: List of slot objects matching the vehicle type and establishment criteria.

        Raises:
            OperationalError: If there is a database operation error.
        """
        session = get_session()
        try:
            slots = (
                session.query(Slot)
                .filter(
                    Slot.vehicle_type_id == vehicle_type_id,
                    Slot.establishment_id == establishment_id,
                )
                .all()
            )
            return slots
        except OperationalError as error:
            raise error

    @staticmethod
    def get_slots_by_establishment(establishment_id: int):
        """Retrieves all slots from the database for a specific establishment with open slot count.

        Args:
            establishment_id (int): The ID of the parking establishment.

        Returns:
            list[dict]: List of dictionaries containing slot, vehicle type info and open slot count.

        Raises:
            OperationalError: If there is a database operation error.
        """
        from app.models.vehicle_type import VehicleType

        session = get_session()
        try:
            # First get total open slots count
            open_slots_count = (
                session.query(func.count(Slot.slot_id))
                .filter(
                    Slot.establishment_id == establishment_id,
                    Slot.slot_status == "open",
                )
                .scalar()
            )

            # Then get detailed slot info
            results = session.execute(
                select(
                    Slot,
                    VehicleType.name.label("vehicle_type_name"),
                    VehicleType.size_category.label("size_category"),
                    VehicleType.code.label("vehicle_type_code"),
                    func.count(Slot.slot_id)
                    .filter(Slot.slot_status == "open")
                    .over(partition_by=VehicleType.vehicle_id)
                    .label("available_slots"),
                )
                .where(Slot.establishment_id == establishment_id)
                .join(VehicleType, Slot.vehicle_type_id == VehicleType.vehicle_id)
            ).all()

            slots_with_vehicle_info = []
            for result in results:
                slot_dict = result[0].to_dict()
                slot_dict.update(
                    {
                        "vehicle_type_name": result[1],
                        "size_category": result[2],
                        "vehicle_type_code": result[3],
                        "available_slots": result[4],
                        "total_open_slots": open_slots_count,
                    }
                )
                slots_with_vehicle_info.append(slot_dict)

            return slots_with_vehicle_info

        except OperationalError as error:
            raise error
        finally:
            session.close()

    @staticmethod
    def get_slots_by_slot_code(slot_code: str):
        """Retrieves a single slot from the database by its slot code.

        Args:
            slot_code (str): The unique code identifier for the slot.

        Returns:
            Slot: The slot object matching the provided code, or None if not found.

        Raises:
            OperationalError: If there is a database operation error.
        """
        session = get_session()
        try:
            slot = session.query(Slot).filter(Slot.slot_code == slot_code).first()
            return slot
        except OperationalError as error:
            raise error


class ParkingManagerOperation:  # pylint: disable=R0903
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
    def create_slot(slot_data: dict):
        """
        Creates a new parking slot in the database with the provided slot data.

        Parameters:
            slot_data (dict): Dictionary containing slot details including establishment_id,
                            slot_code, vehicle_type_id, created_at and updated_at.

        Raises:
            VehicleTypeDoesNotExist: If the specified vehicle type does not exist.
            OperationalError: If there is a problem executing the database operation.
            DataError: If there is a problem with the data format.
            IntegrityError: If there is a violation of database constraints.
            DatabaseError: If any other database error occurs.
        """
        session = get_session()
        try:
            if not VehicleTypeOperations.is_vehicle_type_exist(
                slot_data.get("vehicle_type_id")
            ):
                raise VehicleTypeDoesNotExist("Vehicle type does not exist.")
            new_slot = Slot(
                establishment_id=slot_data.get("establishment_id"),
                slot_code=slot_data.get("slot_code"),
                vehicle_type_id=slot_data.get("vehicle_type_id"),
                created_at=slot_data.get("created_at"),
                updated_at=slot_data.get("updated_at"),
            )
            session.add(new_slot)
            session.commit()
        except (
            OperationalError,
            DataError,
            IntegrityError,
            DatabaseError,
            VehicleTypeDoesNotExist,
        ) as error:
            session.rollback()
            raise error
        finally:
            session.close()

    @staticmethod
    def delete_slot(slot_id: int, manager_id: int):
        """
        Deletes a parking slot from the database.

        Parameters:
            slot_id (int): The ID of the slot to be deleted.
            manager_id (int): The ID of the parking manager making the request.

        Raises:
            OperationalError: If there is a problem executing the database operation.
            DataError: If there is a problem with the data format.
            IntegrityError: If there is a violation of database constraints.
            DatabaseError: If any other database error occurs.
        """
        # pylint: disable=cyclic-import
        from app.models.parking_establishment import ParkingEstablishment

        session = get_session()

        try:
            slot = (
                session.query(Slot)
                .join(
                    ParkingEstablishment,
                    Slot.establishment_id == ParkingEstablishment.establishment_id,
                )
                .where(
                    and_(
                        Slot.slot_id == slot_id,
                        ParkingEstablishment.manager_id == manager_id,
                    )
                )
            )
            if slot:
                session.delete(slot)
                session.commit()
            else:
                raise SlotNotFound("Slot not found.")
        except (OperationalError, DataError, IntegrityError, DatabaseError) as error:
            session.rollback()
            raise error
        finally:
            session.close()

    @staticmethod
    def update_slot(slot_id: int, manager_id: int, slot_data: dict):
        """
        Updates a parking slot in the database.

        Parameters:
            slot_id (int): The ID of the slot to be updated.
            manager_id (int): The ID of the parking manager making the request.

        Raises:
            OperationalError: If there is a problem executing the database operation.
            DataError: If there is a problem with the data format.
            IntegrityError: If there is a violation of database constraints.
            DatabaseError: If any other database error occurs.
        """
        # pylint: disable=cyclic-import
        from app.models.parking_establishment import ParkingEstablishment

        session = get_session()
        try:
            is_eligible_to_edit = (
                session.query(Slot)
                .join(
                    ParkingEstablishment,
                    Slot.establishment_id == ParkingEstablishment.establishment_id,
                )
                .where(
                    and_(
                        Slot.slot_id == slot_id,
                        ParkingEstablishment.manager_id == manager_id,
                    )
                )
            )
            if not is_eligible_to_edit:
                raise SlotNotFound("Slot not found.")
            session.execute(
                update(Slot)
                .where(Slot.slot_id == slot_id)
                .values(
                    is_active=slot_data.get("is_active"),
                    slot_code=slot_data.get("slot_code"),
                    vehicle_type_id=slot_data.get("vehicle_type_id"),
                    updated_at=slot_data.get("updated_at"),
                )
            )
        except (OperationalError, DataError, IntegrityError, DatabaseError) as error:
            session.rollback()
            raise error
        finally:
            session.close()
