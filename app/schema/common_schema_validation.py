""" This module contains the common schema validation for the application. """


from marshmallow import Schema, fields, post_load

from app.utils.uuid_utility import UUIDUtility


class EstablishmentCommonValidation(Schema):
    """
    Common validation schema for establishment. It is used to validate the establishment_uuid.
    """
    establishment_uuid = fields.Str(required=True)
    @post_load
    def normalize_uuid_to_binary(
        self, in_data, **kwargs
    ):  # pylint: disable=unused-argument
        """Normalize the establishment_uuid to binary."""
        uuid_utility = UUIDUtility()
        in_data["establishment_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            in_data["establishment_uuid"]
        )
        in_data["establishment_uuid"] = uuid_utility.uuid_to_binary(
            in_data["establishment_uuid"]
        )
        return in_data

class TransactionCommonValidation(Schema):
    """ Common validation schema for transaction. It is used to validate the transaction_uuid. """
    transaction_uuid = fields.Str(required=True)
    @post_load
    def normalize_uuid_to_binary(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Normalize the transaction_uuid to binary."""
        uuid_utility = UUIDUtility()
        in_data["transaction_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            in_data["transaction_uuid"]
        )
        in_data["transaction_uuid"] = uuid_utility.uuid_to_binary(
            in_data["transaction_uuid"]
        )
        return in_data

class SlotCommonValidation(Schema):
    """ Common validation schema for slot. It is used to validate the slot_uuid. """
    slot_uuid = fields.Str(required=True)
    @post_load
    def normalize_uuid_to_binary(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Normalize the slot_uuid to binary."""
        uuid_utility = UUIDUtility()
        in_data["slot_uuid"] = uuid_utility.remove_hyphens_from_uuid(
            in_data["slot_uuid"]
        )
        in_data["slot_uuid"] = uuid_utility.uuid_to_binary(
            in_data["slot_uuid"]
        )
        return in_data

class EstablishmentBaseInformationSchema(Schema):
    """ Schema for establishment base information. """
