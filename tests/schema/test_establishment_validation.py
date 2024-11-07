""" Test cases for establishment validation schema. """

# pylint: disable=unused-import
# pylint: disable=redefined-outer-name

from datetime import time

import pytest
from marshmallow import ValidationError

from app.schema.establishment_validation import (
    EstablishmentValidationSchema,
    UpdateEstablishmentInfoSchema,
)
from tests.models.user_conftest import mock_session


@pytest.fixture
def valid_establishment_data():
    """Return valid establishment data."""
    return {
        "manager_id": 1,
        "name": "Test Parking",
        "address": "123 Test Street",
        "contact_number": "+1234567890",
        "opening_time": "08:00:00",
        "closing_time": "20:00:00",
        "is_24_hours": False,
        "hourly_rate": 2.50,
        "longitude": -73.935242,
        "latitude": 40.730610,
    }


class TestEstablishmentCreationSchema:
    """Test cases for establishment creation."""

    def test_valid_establishment_data(self, valid_establishment_data):
        """Test valid establishment data."""
        schema = EstablishmentValidationSchema()
        result = schema.load(valid_establishment_data)
        # assert result == valid_establishment_data
        # compare each value since it returns python dictionary:
        assert result.get("manager_id") == 1  # type: ignore
        assert result.get("name") == "Test Parking"  # type: ignore
        assert result.get("address") == "123 Test Street"  # type: ignore
        assert result.get("contact_number") == "+1234567890"  # type: ignore
        assert str(result.get("opening_time")) == "08:00:00"  # type: ignore
        assert str(result.get("closing_time")) == "20:00:00"  # type: ignore
        assert result.get("is_24_hours") is False  # type: ignore
        assert result.get("hourly_rate") == 2.50  # type: ignore
        assert result.get("longitude") == -73.935242  # type: ignore
        assert result.get("latitude") == 40.730610  # type: ignore

    @pytest.mark.parametrize(
        "field",
        [
            "manager_id",
            "name",
            "address",
            "contact_number",
            "opening_time",
            "closing_time",
            "is_24_hours",
            "hourly_rate",
            "longitude",
            "latitude",
        ],
    )
    def test_required_fields(self, valid_establishment_data, field):
        """Test required fields."""
        schema = EstablishmentValidationSchema()
        valid_establishment_data.pop(field)
        with pytest.raises(ValidationError) as exc:
            schema.load(valid_establishment_data)
        assert "Missing data for required field." in str(exc.value)

    def test_invalid_name_length(self, valid_establishment_data):
        """Test invalid name length."""
        schema = EstablishmentValidationSchema()
        valid_establishment_data.update({"name": "a" * 256})
        with pytest.raises(ValidationError) as exc:
            schema.load(valid_establishment_data)
        assert "name" in exc.value.messages

    @pytest.mark.parametrize(
        "contact_number",
        [
            ("123", "Shorter than minimum length"),
            ("abcd1234567", "Invalid phone number format."),
            ("+123456789012345678", "Longer than maximum length"),
        ],
    )
    def test_invalid_contact_number(self, contact_number, valid_establishment_data):
        """Test invalid contact number."""
        schema = EstablishmentValidationSchema()
        valid_establishment_data.update({"contact_number": contact_number})
        with pytest.raises(ValidationError) as exc:
            schema.load({"contact_number": contact_number})
        assert "contact_number" in exc.value.messages

    @pytest.mark.parametrize(
        "field,value,error_type",
        [
            ("manager_id", "not_an_integer", "Not a valid integer."),
            ("hourly_rate", "not_a_float", "Not a valid number."),
            ("longitude", "not_a_float", "Not a valid number."),
            ("latitude", "not_a_float", "Not a valid number."),
            ("is_24_hours", "not_a_boolean", "Not a valid boolean."),
        ],
    )
    def test_invalid_field_types(self, field, value, error_type):
        """Test invalid field types."""
        schema = EstablishmentValidationSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load({field: value})
        assert error_type in str(exc.value)

    def test_invalid_time_format(self, valid_establishment_data):
        """Test invalid time format."""
        schema = EstablishmentValidationSchema()
        valid_establishment_data.update({"opening_time": "invalid_time_format"})
        with pytest.raises(ValidationError) as exc:
            schema.load(valid_establishment_data)
        assert "opening_time" in exc.value.messages

    def test_negative_hourly_rate(self, valid_establishment_data):
        """Test negative hourly rate validation."""
        schema = EstablishmentValidationSchema()
        data = valid_establishment_data.copy()
        data["hourly_rate"] = -1.0
        result = schema.load(data)
        assert (
            result["hourly_rate"] == -1.0  # type: ignore
        )  # Assuming negative values are allowed

    def test_edge_case_time_values_00(self, valid_establishment_data):
        """Test edge cases for time fields."""
        schema = EstablishmentValidationSchema()

        # Test midnight
        valid_establishment_data["opening_time"] = "00:00:00"
        valid_establishment_data["closing_time"] = "00:01:00"
        result = schema.load(valid_establishment_data)
        assert result["opening_time"] == time(00, 00, 00)  # type: ignore
        assert result["closing_time"] == time(00, 1, 00)  # type: ignore

    def test_edge_case_time_values_24(self, valid_establishment_data):
        """Test edge cases for time fields."""
        # Test 23:59
        schema = EstablishmentValidationSchema()
        valid_establishment_data["opening_time"] = "23:58:00"
        valid_establishment_data["closing_time"] = "23:59:00"
        result = schema.load(valid_establishment_data)
        assert result["opening_time"] == time(23, 58, 00)  # type: ignore
        assert result["closing_time"] == time(23, 59, 00)  # type: ignore

    def test_edge_case_time_values_25(self, valid_establishment_data):
        """Test edge cases for time fields."""
        schema = EstablishmentValidationSchema()
        valid_establishment_data["opening_time"] = "24:00:00"
        valid_establishment_data["closing_time"] = "00:00:01"
        with pytest.raises(ValidationError) as exc:
            schema.load(valid_establishment_data)
        assert "Not a valid time." in str(exc.value)

    def test_edge_case_opening_time_is_less_than_closing_time(
        self, valid_establishment_data
    ):
        """Test edge cases for time fields."""
        schema = EstablishmentValidationSchema()
        valid_establishment_data["opening_time"] = "14:00:00"
        valid_establishment_data["closing_time"] = "12:00:00"
        with pytest.raises(ValidationError) as exc:
            schema.load(valid_establishment_data)
        assert "Closing time must be greater than opening time" in str(exc.value)

    def test_edge_case_opening_time_is_equal_to_closing_time(
        self, valid_establishment_data
    ):
        """Test edge cases for time fields."""
        schema = EstablishmentValidationSchema()
        valid_establishment_data["opening_time"] = "14:00:00"
        valid_establishment_data["closing_time"] = "14:00:00"
        with pytest.raises(ValidationError) as exc:
            schema.load(valid_establishment_data)
        assert "Closing time must be greater than opening time" in str(exc.value)


class TestEstablishmentUpdateSchema:
    """Test cases for EstablishmentUpdateSchema."""

    def test_valid_updated_data(self, valid_establishment_data):
        """Test valid updated data."""
        # update some data from the existing valid_establishment_data
        updated_data = valid_establishment_data.copy()
        # Add manager id to the existing valid_establishment_data
        updated_data["establishment_id"] = 1
        updated_data["manager_id"] = 1
        updated_data["name"] = "Updated Name"
        updated_data["contact_number"] = "+123456789"
        updated_data["address"] = "Updated Address"
        updated_data["opening_time"] = "14:00:00"
        updated_data["closing_time"] = "15:00:00"
        updated_data["is_24_hours"] = False
        schema = UpdateEstablishmentInfoSchema()
        result = schema.load(updated_data)
        assert result.get("name") == "Updated Name"  # type: ignore
        assert result.get("contact_number") == "+123456789"  # type: ignore
        assert result.get("address") == "Updated Address"  # type: ignore
        assert str(result.get("opening_time")) == "14:00:00"  # type: ignore
        assert str(result.get("closing_time")) == "15:00:00"  # type: ignore
        assert result.get("is_24_hours") is False  # type: ignore
        assert result.get("manager_id") == 1  # type: ignore

    def test_invalid_updated_data(self, valid_establishment_data):
        """Test invalid updated data."""
        updated_data = valid_establishment_data.copy()
        updated_data["opening_time"] = "invalid_time_format"
        updated_data["establishment_id"] = 1
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "opening_time" in exc.value.messages
        assert "Not a valid time" in str(exc.value.messages)
        updated_data["opening_time"] = "14:00:00"
        updated_data["closing_time"] = "13:00:00"
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "Closing time must be greater than opening time" in str(exc.value)
        updated_data["opening_time"] = "14:00:00"
        updated_data["closing_time"] = "14:00:00"
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "Closing time must be greater than opening time" in str(exc.value)
        updated_data["opening_time"] = "14:00:00"
        updated_data["closing_time"] = "13:00:00"
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)

    def test_invalid_manager_id(self, valid_establishment_data):
        """Test invalid manager id."""
        updated_data = valid_establishment_data.copy()
        updated_data["manager_id"] = "not_an_integer"
        updated_data["establishment_id"] = 1
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "manager_id" in exc.value.messages
        assert "Not a valid integer" in str(exc.value.messages)

    def test_missing_manager_id(self, valid_establishment_data):
        """Test missing manager id."""
        updated_data = valid_establishment_data.copy()
        updated_data.pop("manager_id")
        updated_data["establishment_id"] = 1
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "manager_id" in exc.value.messages
        assert "Missing data for required field" in str(exc.value.messages)

    def test_missing_establishment_id(self, valid_establishment_data):
        """Test missing establishment id."""
        updated_data = valid_establishment_data.copy()
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "establishment_id" in exc.value.messages
        assert "Missing data for required field" in str(exc.value.messages)

    def test_invalid_establishment_id(self, valid_establishment_data):
        """Test invalid establishment id."""
        updated_data = valid_establishment_data.copy()
        updated_data["establishment_id"] = "not_an_integer"
        updated_data["manager_id"] = 1
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "establishment_id" in exc.value.messages
        assert "Not a valid integer" in str(exc.value.messages)

    def test_invalid_name(self, valid_establishment_data):
        """Test invalid name."""
        updated_data = valid_establishment_data.copy()
        updated_data["establishment_id"] = 1
        updated_data["manager_id"] = 1
        updated_data["name"] = "a" * 256
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "name" in str(exc.value)

    @pytest.mark.parametrize(
        "field, value",
        [
            ("contact_number", "+12345678901234567890"),
            ("address", "a" * 256),
        ],
    )
    def test_invalid_field_length(self, field, value, valid_establishment_data):
        """Test invalid field length."""
        updated_data = valid_establishment_data.copy()
        updated_data[field] = value
        updated_data["establishment_id"] = 1
        updated_data["manager_id"] = 1
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert field in exc.value.messages
        assert "Length must be between" in str(exc.value.messages)

    @pytest.mark.parametrize(
        "field, value",
        [
            ("contact_number", "+12345678901234567890"),
            ("address", "a" * 256),
        ],
        ids=["contact_number", "address"],
    )
    def test_invalid_field_format(self, field, value, valid_establishment_data):
        """Test invalid field format."""
        updated_data = valid_establishment_data.copy()
        updated_data["manager_id"] = 1
        updated_data["establishment_id"] = 1
        updated_data[field] = value
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert field in exc.value.messages
        assert "Length must be between" in str(exc.value.messages)

    @pytest.mark.parametrize(
        "opening_time, closing_time",
        [
            ("15:00:00", "13:00:00"),
            ("14:00:00", "14:00:00"),
        ],
    )
    def test_invalid_opening_closing_time(
        self, opening_time, closing_time, valid_establishment_data
    ):
        """Test invalid opening and closing time."""
        updated_data = valid_establishment_data.copy()
        updated_data["opening_time"] = opening_time
        updated_data["closing_time"] = closing_time
        updated_data["establishment_id"] = 1
        updated_data["manager_id"] = 1
        schema = UpdateEstablishmentInfoSchema()
        with pytest.raises(ValidationError) as exc:
            schema.load(updated_data)
        assert "Closing time must be greater than opening time" in str(exc.value)
        updated_data["opening_time"] = "14:00:00"
        updated_data["closing_time"] = "15:00:00"
        result = schema.load(updated_data)
        assert result.get("is_24_hours") is False  # type: ignore
        assert str(result.get("opening_time")) == "14:00:00"  # type: ignore
        assert str(result.get("closing_time")) == "15:00:00"  # type: ignore
