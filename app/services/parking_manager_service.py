"""" Wraps the services that the parking manager can call """


class ParkingManagerService:  # pylint: disable=R0903
    """ Wraps all the services that the parking manager can call """
    @staticmethod
    def get_establishment_info(manager_id: int):
        """ Get parking establishment information """
        # return ParkingManagerOperations.get_establishment_info(manager_id)
