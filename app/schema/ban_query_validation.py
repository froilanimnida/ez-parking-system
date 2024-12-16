""" Wraps the query validation for banning the plate numbers by the admin. """

from marshmallow import Schema, fields, validate, post_load


class BanQueryValidation(Schema):
    """Validation schema for banning the plate numbers by the admin."""

    ban_reason = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    user_id = fields.Str(required=True)
    ban_start = fields.DateTime(required=True)
    ban_end = fields.DateTime(required=True)
    is_permanent = fields.Bool(required=True)
    @post_load
    def normalize_ban_reason(self, in_data, **kwargs):  # pylint: disable=unused-argument
        """Normalize ban reason by removing leading and trailing whitespaces."""
        if "ban_reason" in in_data:
            in_data["ban_reason"] = in_data["ban_reason"].strip()
        return in_data
    @post_load
    def validate_ban_start_end(self, in_data, **kwargs): # pylint: disable=unused-argument
        """Validate if the ban end is greater than the ban start."""
        if "ban_start" in in_data and "ban_end" in in_data:
            if in_data["ban_start"] > in_data["ban_end"]:
                raise ValueError("Ban end should be greater than the ban start.")
        if "ban_start" in in_data and "ban_end" in in_data:
            if in_data["ban_start"] == in_data["ban_end"]:
                raise ValueError("Ban start and end should not be the same.")
        return in_data

class UnbanQueryValidation(Schema):
    """Validation schema for unbanning the plate numbers by the admin."""
    ban_uuid = fields.Str(required=True)
