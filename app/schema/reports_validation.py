"""This module contains the schema for the reports validation."""

from marshmallow import Schema, fields


class RevenueReportSchema(Schema):
    """Revenue report schema."""
    start_data = fields.Date(required=False)
    end_date = fields.Date(required=False)
