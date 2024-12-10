"""" Wraps the services that the parking manager can call """


class ParkingManagerService:  # pylint: disable=R0903
    """ Wraps all the services that the parking manager can call """
    @staticmethod
    def get_establishment_info(manager_id: int):
        """ Get parking establishment information """
        # return ParkingManagerOperations.get_establishment_info(manager_id)

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
