""" Schema Validation for Vehicle Type. """

from marshmallow import Schema, fields, validate

class CreateVehicleTypeSchema(Schema):
    """ Schema for creating a new vehicle type. """
    size_category = fields.Str(required=True, validate=validate.OneOf(["SMALL", "MEDIUM", "LARGE"]))
    code = fields.Str(required=True, validate=validate.Length(min=3, max=45))
    name = fields.Str(required=True, validate=validate.Length(min=3, max=125))
    is_active = fields.Bool(required=False, missing=True)
    description = fields.Str(required=True, validate=validate.Length(min=3, max=255))
class GetVehicleTypeSchema(Schema):
    """ Schema for getting a vehicle type. """
    vehicle_type_uuid = fields.Str(required=True)
class UpdateVehicleTypeSchema(GetVehicleTypeSchema, CreateVehicleTypeSchema):
    """ Schema for updating a vehicle type. """
