""" User Authentication Schema. """

from marshmallow import fields, validate, Schema, post_load


class RegistrationBaseSchema(Schema):
    nickname = fields.Str(required=True, validate=validate.Length(min=3, max=24))
    first_name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    middle_name = fields.Str(required=False, missing=None, validate=validate.Length(min=3, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    suffix = fields.Str(required=False, missing=None, validate=validate.Length(min=3, max=10))
    email = fields.Email(required=True, validate=validate.Length(min=3, max=75))
    phone_number = fields.Str(required=True, validate=[
        validate.Length(min=10, max=15),
        validate.Regexp(
            regex=r"^\+?[0-9]\d{1,14}$", error="Invalid phone number format."
        ),
    ])
    plate_number = fields.Str(required=True, validate=[
        validate.Length(min=6, max=8),
        validate.Regexp(
            regex=r"^(?:"
                  r"[A-Z]{2,3}[\s-]?\d{3,4}|"
                  r"CD[\s-]?\d{4}|"
                  r"[A-Z]{3}[\s-]?\d{3}|"
                  r"\d{4}"
                  r")$",
            error=(
                "Invalid plate number format. Please use one of these formats:\n"
                "• Private vehicles: ABC 123 or ABC 1234\n"
                "• Diplomatic: CD 1234\n"
                "• Government: SFP 123\n"
                "• Special: 1234"
            ),
        ),
    ])
    
    @post_load
    def normalize_plate_number(
        self, in_data, **kwargs
    ):  # pylint: disable=unused-argument
        """Normalize plate number format by removing spaces and converting to uppercase"""
        if "plate_number" in in_data:
            in_data["plate_number"] = in_data["plate_number"].upper().replace(" ", "")
        return in_data
        
    @post_load
    def normalize_email(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Method to convert email to lowercase."""
        in_data["email"] = in_data["email"].lower()
        return in_data
    
    @post_load(pass_many=True)
    def normalize_personal_data(self, in_data, **kwargs):
        """ Method to capitalize the first name, middle name, last name, suffix, and nickname. """
        for data in in_data:
            data["first_name"] = data["first_name"].capitalize()
            data["middle_name"] = data["middle_name"].capitalize() if data["middle_name"] else None
            data["last_name"] = data["last_name"].capitalize()
            data["suffix"] = data["suffix"].capitalize() if data["suffix"] else None
            data["nickname"] = data["nickname"].capitalize()
        return in_data
    
    
class UserRegistrationSchema(RegistrationBaseSchema):
    """ Schema for user registration. """
    pass
