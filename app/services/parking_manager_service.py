"""" Wraps the services that the parking manager can call """

from app.models.parking_establishment import ParkingManagerOperations
from app.models.slot import ParkingManagerOperations as SlotParkingManagerOperation


class ParkingManagerService:  # pylint: disable=R0903
    """ Wraps all the services that the parking manager can call """

    @staticmethod
    def get_all_establishment_info(manager_id: int):
        """ Get all establishment information """
        return EstablishmentService.get_establishment_info(manager_id)


class EstablishmentService:
    """ Wraps all the services that the parking manager can call """

    @staticmethod
    def delete_establishment(establishment_id: int):
        """ Delete parking establishment """
        # return ParkingEstablishment.delete_establishment(establishment_id)

    @staticmethod
    def update_establishment(establishment_id: int, establishment_data: dict):
        """ Update parking establishment information """
        # return ParkingEstablishment.update_establishment(establishment_id, establishment_data)

    @staticmethod
    def get_establishment_info(manager_id: int):
        """ Get parking establishment information """
        parking_establishment = ParkingManagerOperations.get_all_slots(manager_id)
        slots = SlotParkingManagerOperation.get_all_slot_info(manager_id)
        return {"establishment": parking_establishment, "slots": slots}
        # return ParkingEstablishment.get_establishment_info(establishment_id)
