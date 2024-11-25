"""
    Contains the tests related to authentication marshmallow schema
    and other authentication related validation methods.

    This module includes tests for:
    - SignUpValidationSchema
    - OTPGenerationSchema
    - OTPSubmissionSchema
    - NicknameFormValidationSchema
    - LoginWithEmailValidationSchema

    The tests are written to ensure that the schema correctly validates
    the provided data.

"""

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import

import pytest
from marshmallow import ValidationError

from app.schema.auth_validation import (
    OTPGenerationSchema,
    OTPSubmissionSchema,
    NicknameFormValidationSchema,
    LoginWithEmailValidationSchema,
    SignUpValidationSchema,
)
from tests.models.config.config_test import mock_session


class TestSignUpValidation:
    """Tests for SignUpValidation schema."""

    @pytest.fixture
    def valid_data(self):
        """Represents valid user data."""
        return {
            "first_name": "john",
            "last_name": "doe",
            "email": "John.Doe@example.com",
            "phone_number": "+1234567890",
            "role": "User",
        }

    def test_valid_data(self, valid_data):
        """Test that valid data passes validation."""
        schema = SignUpValidationSchema()
        result = schema.load(valid_data)
        assert result.get("first_name") == "John"  # type: ignore
        assert result.get("last_name") == "Doe"  # type: ignore
        assert result.get("email") == "john.doe@example.com"  # type: ignore
        assert result.get("phone_number") == "+1234567890"  # type: ignore
        assert result.get("role") == "user"  # type: ignore

    def test_missing_first_name(self, valid_data):
        """Test that missing first name raises ValidationError."""
        schema = SignUpValidationSchema()
        valid_data.pop("first_name")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "first_name" in exc_info.value.messages

    def test_missing_last_name(self, valid_data):
        """Test that missing last name raises ValidationError."""
        schema = SignUpValidationSchema()
        valid_data.pop("last_name")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "last_name" in exc_info.value.messages

    def test_missing_email(self, valid_data):
        """Test that missing email raises ValidationError."""
        schema = SignUpValidationSchema()
        valid_data.pop("email")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "email" in exc_info.value.messages

    def test_invalid_email(self, valid_data):
        """Test that invalid email raises ValidationError."""
        schema = SignUpValidationSchema()
        # valid_data["email"] = "invalid-email"
        valid_data.update({"email": "invalid-email"})
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "email" in exc_info.value.messages

    def test_missing_phone_number(self, valid_data):
        """Test that missing phone number raises ValidationError."""
        schema = SignUpValidationSchema()
        del valid_data["phone_number"]
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "phone_number" in exc_info.value.messages

    def test_invalid_phone_number(self, valid_data):
        """Test that invalid phone number raises ValidationError."""
        schema = SignUpValidationSchema()
        valid_data["phone_number"] = "12345"
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "phone_number" in exc_info.value.messages

    def test_normalize_email(self, valid_data):
        """Test that email is normalized to lowercase."""
        schema = SignUpValidationSchema()
        result = schema.load(valid_data)
        assert result.get("email") == "john.doe@example.com"  # type: ignore

    def test_normalize_first_name(self, valid_data):
        """Test that first name is normalized to lowercase."""
        schema = SignUpValidationSchema()
        result = schema.load(valid_data)
        assert result.get("first_name") == "John"  # type: ignore

    def test_normalize_last_name(self, valid_data):
        """Test that last name is normalized to lowercase."""
        schema = SignUpValidationSchema()
        result = schema.load(valid_data)
        assert result.get("last_name") == "Doe"  # type: ignore


class TestLoginWithEmailValidation:
    """Tests for LoginWithEmailValidation schema."""

    @pytest.fixture
    def valid_data(self):
        """Represents valid login data."""
        return {"email": "User@example.com"}

    def test_valid_data(self, valid_data):
        """Test that valid data passes validation."""
        schema = LoginWithEmailValidationSchema()
        result = schema.load(valid_data)
        assert result.get("email") == "user@example.com"  # type: ignore

    def test_missing_email(self, valid_data):
        """Test that missing email raises ValidationError."""
        schema = LoginWithEmailValidationSchema()
        valid_data.pop("email")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "email" in exc_info.value.messages

    def test_invalid_email(self, valid_data):
        """Test that invalid email raises ValidationError."""
        schema = LoginWithEmailValidationSchema()
        valid_data["email"] = "invalid-email"
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "email" in exc_info.value.messages

    def test_normalize_email(self, valid_data):
        """Test that email is normalized to lowercase."""
        schema = LoginWithEmailValidationSchema()
        result = schema.load(valid_data)
        assert result.get("email") == "user@example.com"  # type: ignore


class TestOTPGenerationSchema:
    """Tests for OTPGenerationSchema schema."""

    @pytest.fixture
    def valid_data(self):
        """Represents valid OTP data."""
        return {"otp": "123456"}

    def test_valid_data(self, valid_data):
        """Test that valid data passes validation."""
        schema = OTPGenerationSchema()
        result = schema.load(valid_data)
        assert result.get("otp") == "123456"  # type: ignore

    def test_missing_otp(self, valid_data):
        """Test that missing OTP raises ValidationError."""
        schema = OTPGenerationSchema()
        valid_data.pop("otp")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "otp" in exc_info.value.messages

    def test_invalid_otp_length(self, valid_data):
        """Test that OTP with invalid length raises ValidationError."""
        schema = OTPGenerationSchema()

        valid_data.update({"otp": "1234567"})  # More than 6 characters
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "otp" in exc_info.value.messages
        valid_data.update({"otp": "12345"})  # Less than 6 characters
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "otp" in exc_info.value.messages


class TestOTPSubmissionFormValidation:
    """Tests for OTPSubmissionFormValidation schema."""

    @pytest.fixture
    def valid_data(self):
        """Represents valid OTP submission data."""
        return {"otp": "123456", "email": "User@example.com"}

    def test_valid_data(self, valid_data):
        """Test that valid data passes validation."""
        schema = OTPSubmissionSchema()
        result = schema.load(valid_data)
        assert result.get("otp") == "123456"  # type: ignore
        assert result.get("email") == "user@example.com"  # type: ignore

    def test_missing_otp(self, valid_data):
        """Test that missing OTP raises ValidationError."""
        schema = OTPSubmissionSchema()
        valid_data.pop("otp")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "otp" in exc_info.value.messages

    def test_missing_email(self, valid_data):
        """Test that missing email raises ValidationError."""
        schema = OTPSubmissionSchema()
        valid_data.pop("email")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "email" in exc_info.value.messages

    def test_invalid_otp_length(self, valid_data):
        """Test that OTP with invalid length raises ValidationError."""
        schema = OTPSubmissionSchema()
        valid_data.update({"otp": "12345"})  # Less than 6 characters
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "otp" in exc_info.value.messages

        valid_data.update({"otp": "1234567"})  # More than 6 characters
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "otp" in exc_info.value.messages

    def test_invalid_email(self, valid_data):
        """Test that invalid email raises ValidationError."""
        schema = OTPSubmissionSchema()
        valid_data.update({"email": "invalid-email"})
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "email" in exc_info.value.messages

    def test_normalize_email(self, valid_data):
        """Test that email is normalized to lowercase."""
        schema = OTPSubmissionSchema()
        result = schema.load(valid_data)
        assert result.get("email") == "user@example.com"  # type: ignore


class TestNicknameFormValidation:
    """Tests for NicknameFormValidation schema."""

    @pytest.fixture
    def valid_data(self):
        """Represents valid nickname data."""
        return {"nickname": "UserNickname"}

    def test_valid_data(self, valid_data):
        """Test that valid data passes validation."""
        schema = NicknameFormValidationSchema()
        result = schema.load(valid_data)
        assert result.get("nickname") == "usernickname"  # type: ignore

    def test_missing_nickname(self, valid_data):
        """Test that missing nickname raises ValidationError."""
        schema = NicknameFormValidationSchema()
        valid_data.pop("nickname")
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "nickname" in exc_info.value.messages

    def test_invalid_nickname_length(self, valid_data):
        """Test that nickname with invalid length raises ValidationError."""
        schema = NicknameFormValidationSchema()
        valid_data.update({"nickname": ""})  # Less than 1 character
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "nickname" in exc_info.value.messages

        valid_data.update({"nickname": "a" * 76})  # More than 75 characters
        with pytest.raises(ValidationError) as exc_info:
            schema.load(valid_data)
        assert "nickname" in exc_info.value.messages

    def test_normalize_nickname(self, valid_data):
        """Test that nickname is normalized to lowercase."""
        schema = NicknameFormValidationSchema()
        result = schema.load(valid_data)
        assert result.get("nickname") == "usernickname"  # type: ignore
