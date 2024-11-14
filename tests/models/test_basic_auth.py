""" Test cases for user models in the database. """

# pylint: disable=redefined-outer-name
# pylint: disable=W0621
# pylint: disable=unused-import

from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy import Update
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, DatabaseError

from app.exceptions.authorization_exceptions import EmailNotFoundException
from app.models.user import User, UserOperations
from tests.models.user_conftest import (
    mock_session,
    valid_user_data,
)  # pylint: disable=unused-import


# noinspection PyTypeHints,SqlNoDataSourceInspection
class TestUserCreation:
    """Test for user operations."""

    def test_create_user_when_input_valid(
        self, mock_session, valid_user_data
    ):  # pylint: disable=C0103
        """Test creating a new user with valid data."""
        mock_session.commit = Mock()
        mock_user = Mock()
        mock_user.user_id = 1
        mock_session.add.return_value = None

        def side_effect(user):
            user.user_id = 1

        mock_session.add.side_effect = side_effect

        user_id = UserOperations.create_new_user(valid_user_data)

        assert user_id == 1  # type: ignore
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

        user_obj = mock_session.add.call_args[0][0]
        assert isinstance(user_obj, User)
        assert user_obj.first_name == valid_user_data["first_name"]
        assert user_obj.last_name == valid_user_data["last_name"]
        assert user_obj.email == valid_user_data["email"]
        assert user_obj.phone_number == valid_user_data["phone_number"]
        assert user_obj.creation_date == valid_user_data["creation_date"]
        assert user_obj.role == valid_user_data["role"]
        assert user_obj.otp_secret == valid_user_data["otp_secret"]
        assert user_obj.otp_expiry == valid_user_data["otp_expiry"]
        assert isinstance(user_obj.uuid, bytes)

    def test_raise_integrity_error_email_taken(
        self, mock_session, valid_user_data
    ):  # pylint: disable=C0103
        """Test creating a new user with an email that is already taken."""
        mock_session.add = Mock(
            side_effect=IntegrityError("statement", "params", "orig")  # type: ignore
        )  # type: ignore
        with pytest.raises(IntegrityError):
            UserOperations.create_new_user(valid_user_data)

    @pytest.mark.parametrize(
        "missing_field",
        [
            "uuid",
            "firstname",
            "lastname",
            "email",
            "phone_number",
            "role",
            "otp_secret",
            "otp_expiry",
            "creation_date",
        ],
    )
    def test_raise_integrity_error_required_field(
        self, mock_session, valid_user_data, missing_field
    ):  # pylint: disable=C0103
        """Test creating a new user with a missing required field."""
        # Arrange
        valid_user_data[missing_field] = None
        error_message = (
            f'null value in column "{missing_field}" of relation "user" '
            f"violates not-null constraint"
        )
        mock_session.commit.side_effect = IntegrityError(
            statement="INSERT INTO user ...", params={}, orig=Exception(error_message)
        )

        with pytest.raises(IntegrityError) as exc_info:
            UserOperations.create_new_user(valid_user_data)

        assert "violates not-null constraint" in str(exc_info.value)
        mock_session.rollback.assert_called_once()

    def test_create_new_user_data_error(self, mock_session, valid_user_data):
        """Test creating a new user with invalid data types."""
        mock_session.add = Mock()
        mock_session.commit.side_effect = DataError(
            statement="INSERT INTO user ...",
            params={},
            orig=Exception("invalid input syntax for type integer"),
        )

        with pytest.raises(DataError) as exc_info:
            UserOperations.create_new_user(valid_user_data)

        assert "invalid input syntax for type integer" in str(exc_info.value)
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_create_new_user_operational_error(self, mock_session, valid_user_data):
        """Test creating a new user when database connection fails."""
        mock_session.add.side_effect = OperationalError(
            "statement", "params", "orig"  # type: ignore
        )

        with pytest.raises(OperationalError):
            UserOperations.create_new_user(valid_user_data)

        mock_session.add.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_handle_database_error(self, mock_session, valid_user_data):
        """Test handling DatabaseError when creating a new user."""
        mock_session.add = Mock()
        mock_session.commit.side_effect = DatabaseError(
            "statement", "params", "orig"  # type: ignore
        )

        with pytest.raises(DatabaseError):
            UserOperations.create_new_user(valid_user_data)

        mock_session.add.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_create_user_phone_number_saved_correctly(
        self, mock_session, valid_user_data
    ):
        """Create  a new user and check that phone number is saved correctly."""

        # Arrange
        valid_user_data["phone_number"] = "+1234567890"
        mock_session.commit = Mock()
        mock_session.add.side_effect = lambda user: setattr(user, "id", 1)

        # Act
        UserOperations.create_new_user(valid_user_data)

        # Assert
        mock_session.add.assert_called_once()
        user_obj = mock_session.add.call_args[0][0]
        assert isinstance(user_obj, User)
        assert user_obj.phone_number == "+1234567890"  # type: ignore
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_create_new_user_with_unexpected_fields(
        self, mock_session, valid_user_data
    ):
        """Test creating a new user with unexpected fields in user_data."""
        # Add an unexpected field to the valid_user_data
        valid_user_data["unexpected_field"] = "some_value"

        mock_session.commit = Mock()
        mock_user = Mock()
        mock_user.user_id = 1
        mock_session.add.return_value = None

        def side_effect(user):
            user.user_id = 1

        mock_session.add.side_effect = side_effect

        user_id = UserOperations.create_new_user(valid_user_data)

        assert user_id == 1  # type: ignore
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

        user_obj = mock_session.add.call_args[0][0]
        assert isinstance(user_obj, User)
        assert not hasattr(user_obj, "unexpected_field")
        assert user_obj.first_name == valid_user_data["first_name"]
        assert user_obj.last_name == valid_user_data["last_name"]
        assert user_obj.email == valid_user_data["email"]
        assert user_obj.phone_number == valid_user_data["phone_number"]
        assert user_obj.role == valid_user_data["role"]
        assert user_obj.creation_date == valid_user_data["creation_date"]
        assert isinstance(user_obj.uuid, bytes)

    def test_create_user_with_minimum_required_fields(self, mock_session):
        """Test creating a new user with minimum required fields."""
        # Arrange
        minimum_user_data = {
            "uuid": uuid4().bytes,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "role": "user",
            "creation_date": datetime.now(),
        }
        mock_session.add.side_effect = lambda user: setattr(user, "id", 1)

        # Act
        UserOperations.create_new_user(minimum_user_data)

        # Assert
        mock_session.add.assert_called_once()
        user_obj = mock_session.add.call_args[0][0]
        assert isinstance(user_obj, User)
        assert user_obj.uuid == minimum_user_data["uuid"]  # type: ignore
        assert user_obj.first_name == minimum_user_data["first_name"]  # type: ignore
        assert user_obj.last_name == minimum_user_data["last_name"]  # type: ignore
        assert user_obj.email == minimum_user_data["email"]  # type: ignore
        assert user_obj.phone_number == minimum_user_data["phone_number"]  # type: ignore
        assert user_obj.role == minimum_user_data["role"]  # type: ignore
        assert user_obj.creation_date == minimum_user_data["creation_date"]  # type: ignore
        assert user_obj.nickname is None
        assert user_obj.otp_secret is None
        assert user_obj.otp_expiry is None
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_create_new_user_session_closed_on_exception(
        self, mock_session, valid_user_data
    ):
        """Test that the session is closed even if an exception is raised during user creation."""
        mock_session.add.side_effect = DatabaseError(
            "statement", "params", "orig"  # type: ignore
        )

        with pytest.raises(DatabaseError):
            UserOperations.create_new_user(valid_user_data)

        mock_session.add.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_create_new_user_return_nothing(self, mock_session, valid_user_data):
        """Test that create_new_user returns an integer id."""
        mock_session.commit = Mock()
        mock_session.add.side_effect = lambda user: setattr(user, "id", 1)

        user_id = UserOperations.create_new_user(valid_user_data)

        assert user_id is None  # type: ignore
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


class TestLoginOperation:
    """Test for user login operation."""

    def test_login_user_raises_email_not_found_exception_when_user_not_found(
        self, mock_session
    ):
        """Test that login_user raises IncorrectPasswordException when user is not found."""
        mock_session.execute.return_value.scalar.return_value = None
        email = "nonexistent@example.com"

        with pytest.raises(EmailNotFoundException) as exc_info:
            UserOperations.login_user(email)

        assert str(exc_info.value) == "Email not found."
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_not_called()
        mock_session.close.assert_called_once()

    def test_login_user_returns_email_when_user_found(self, mock_session):
        """Test that login_user returns the user's email when the user is found in the database."""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_session.execute.return_value.scalar.return_value = mock_user

        # Act
        result = UserOperations.login_user("test@example.com")

        # Assert
        assert result == "test@example.com"  # type: ignore
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    def test_login_user_operational_error(self, mock_session):
        """Test handling OperationalError when logging in a user."""
        mock_session.execute.side_effect = OperationalError(
            "statement", "params", "orig"  # type: ignore
        )

        with pytest.raises(OperationalError):
            UserOperations.login_user("test@example.com")

        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    def test_login_user_handles_database_error(self, mock_session):
        """Test that login_user handles DatabaseError and rolls back the session."""
        mock_session.execute.side_effect = DatabaseError(
            "statement", "params", "orig"  # type: ignore
        )

        with pytest.raises(DatabaseError):
            UserOperations.login_user("test@example.com")

        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()


class TestIsEmailTaken:
    """Test for is_email_taken operation."""

    def test_is_email_taken_returns_true_when_user_exists(self, mock_session):
        """Test that is_email_taken returns True when a user with the given email exists."""
        # Arrange
        mock_user = Mock(spec=User)
        mock_session.execute.return_value.scalar.return_value = mock_user
        email = "existing@example.com"

        # Act
        result = UserOperations.is_email_taken(email)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    def test_is_email_taken_returns_false_when_email_not_found(self, mock_session):
        """Test that is_email_taken returns False when no user with the given email exists."""
        # Arrange
        mock_session.execute.return_value.scalar.return_value = None
        email = "nonexistent@example.com"

        # Act
        result = UserOperations.is_email_taken(email)

        # Assert
        assert result is False
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    def test_is_email_taken_case_insensitive(self, mock_session):
        """Test that is_email_taken handles case-insensitive email matching."""
        # Arrange
        mock_session.execute.return_value.scalar.return_value = Mock(spec=User)
        email = "TEST@example.com"

        # Act
        result = UserOperations.is_email_taken(email)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        select_statement = mock_session.execute.call_args[0][0]
        assert '"user".email = :email_1' in str(select_statement)

    def test_is_email_taken_closes_session_on_exception(self, mock_session):
        """Test that is_email_taken closes the session even if an exception is raised."""
        # Arrange
        mock_session.execute.side_effect = DatabaseError(
            "statement", "params", "orig"  # type: ignore
        )
        email = "test@example.com"

        # Act
        with pytest.raises(DatabaseError):
            UserOperations.is_email_taken(email)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    def test_is_email_taken_handles_data_error(self, mock_session):
        """Test that is_email_taken handles DataError and rolls back the session."""
        # Arrange
        mock_session.execute.side_effect = DataError(
            "statement", "params", "orig"  # type: ignore
        )
        email = "test@example.com"

        # Act & Assert
        with pytest.raises(DataError):
            UserOperations.is_email_taken(email)

        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    def test_is_email_taken_handles_integrity_error(self, mock_session):
        """Test that is_email_taken handles IntegrityError and rolls back the session."""
        # Arrange
        mock_session.execute.side_effect = IntegrityError(
            "statement", "params", "orig"  # type: ignore
        )
        email = "test@example.com"

        # Act & Assert
        with pytest.raises(IntegrityError):
            UserOperations.is_email_taken(email)

        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    def test_is_email_taken_with_empty_string(self, mock_session):
        """Test that is_email_taken handles empty string as email input."""
        # Arrange
        mock_session.execute.return_value.scalar.return_value = None
        email = ""

        # Act
        result = UserOperations.is_email_taken(email)

        # Assert
        assert result is False
        mock_session.execute.assert_called_once()
        select_statement = mock_session.execute.call_args[0][0]
        assert '"user".email = :email_1' in str(select_statement)

    def test_is_email_taken_handles_very_long_email(self, mock_session):
        """Test that is_email_taken handles very long email addresses (256 characters)."""
        # Arrange
        long_email = "a" * 244 + "@example.com"  # 256 characters in total
        mock_session.execute.return_value.scalar.return_value = None

        # Act
        result = UserOperations.is_email_taken(long_email)

        # Assert
        assert result is False
        mock_session.execute.assert_called_once()
        select_statement = mock_session.execute.call_args[0][0]
        compiled = select_statement.compile()
        assert compiled.params["email_1"] == long_email

    def test_is_email_taken_handles_special_characters(self, mock_session):
        """Test that is_email_taken handles email addresses with special characters."""
        # Arrange
        mock_session.execute.return_value.scalar.return_value = Mock(spec=User)
        email = "test+special@example.com"

        # Act
        result = UserOperations.is_email_taken(email)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        select_statement = mock_session.execute.call_args[0][0]
        compiled = select_statement.compile()
        assert compiled.params["email_1"] == "test+special@example.com"

    def test_is_email_taken_handles_unicode_characters(self, mock_session):
        """Test that is_email_taken handles Unicode characters in email addresses."""
        # Arrange
        mock_session.execute.return_value.scalar.return_value = Mock(spec=User)
        email = "üser@exämple.com"

        # Act
        result = UserOperations.is_email_taken(email)

        # Assert
        assert result is True
        mock_session.execute.assert_called_once()
        select_statement = mock_session.execute.call_args[0][0]
        assert '"user".email = :email_1' in str(select_statement)
        mock_session.close.assert_called_once()


class TestSetNickname:
    """Test for set_nickname operation."""

    def test_set_nickname_for_existing_user(self, mock_session):
        """Test setting a valid nickname for an existing user."""
        # Arrange
        user_id = 1
        nickname = "test_nickname"
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        UserOperations.set_nickname(user_id, nickname)

        # Assert
        mock_session.execute.assert_called_once()
        update_statement = mock_session.execute.call_args[0][0]
        assert isinstance(update_statement, Update)
        assert str(update_statement) == (
            'UPDATE "user" SET nickname=:nickname WHERE "user".user_id = :user_id_1'
        )

    def test_set_nickname_with_empty_string(self, mock_session):
        """Test setting an empty string as a nickname."""
        # Arrange
        user_id = 1
        nickname = ""
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        UserOperations.set_nickname(user_id, nickname)

        # Assert
        mock_session.execute.assert_called_once()
        update_statement = mock_session.execute.call_args[0][0]
        assert isinstance(update_statement, Update)
        assert str(update_statement) == (
            'UPDATE "user" SET nickname=:nickname WHERE "user".user_id = :user_id_1'
        )
        assert update_statement.compile().params == {"nickname": "", "user_id_1": 1}
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_nickname_very_long(self, mock_session):
        """Test setting a very long nickname (255 characters)."""
        # Arrange
        user_id = 1
        long_nickname = "a" * 255
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        UserOperations.set_nickname(user_id, long_nickname)

        # Assert
        mock_session.execute.assert_called_once()
        update_statement = mock_session.execute.call_args[0][0]
        assert str(update_statement).startswith('UPDATE "user"')
        assert "SET nickname=:nickname" in str(update_statement)
        assert '"user".user_id = :user_id_1' in str(update_statement)

    def test_set_nickname_with_special_characters(self, mock_session):
        """Test setting a nickname with special characters."""
        # Arrange
        user_id = 1
        nickname = "User@123!#$%"
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        UserOperations.set_nickname(user_id, nickname)

        # Assert
        mock_session.execute.assert_called_once()
        update_statement = mock_session.execute.call_args[0][0]
        assert str(update_statement) == (
            'UPDATE "user" SET nickname=:nickname WHERE "user".user_id = :user_id_1'
        )

    def test_set_nickname_for_non_existent_user(self, mock_session):
        """Test setting a nickname for a non-existent user."""
        # Arrange
        user_id = 999
        nickname = "NewNickname"
        mock_session.execute.return_value = None
        mock_session.commit.side_effect = IntegrityError(
            statement="UPDATE user ...",
            params={},
            orig=Exception('Key (id)=(999) is not present in table "user".'),
        )

        # Act & Assert
        with pytest.raises(IntegrityError) as exc_info:
            UserOperations.set_nickname(user_id, nickname)

        assert 'is not present in table "user"' in str(exc_info.value)
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_nickname_duplicate_nickname(self, mock_session):
        """Test setting the same nickname for multiple users raises IntegrityError."""
        # Arrange
        user_id1 = 1
        user_id2 = 2
        nickname = "duplicate_nickname"
        mock_session.execute.side_effect = [
            None,
            IntegrityError("statement", "params", "orig"),  # type: ignore
        ]

        # Act & Assert
        UserOperations.set_nickname(user_id1, nickname)

        with pytest.raises(IntegrityError):
            UserOperations.set_nickname(user_id2, nickname)

        assert mock_session.execute.call_count == 2
        assert mock_session.commit.call_count == 1
        assert mock_session.rollback.call_count == 1
        assert mock_session.close.call_count == 2

    def test_update_existing_nickname(self, mock_session):
        """Test updating an existing nickname for a user."""
        user_id = 1
        new_nickname = "new_nickname"
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        UserOperations.set_nickname(user_id, new_nickname)

        mock_session.execute.assert_called_once()
        update_statement = mock_session.execute.call_args[0][0]
        assert isinstance(update_statement, Update)
        assert update_statement.table.name == "user"  # type: ignore
        assert str(update_statement.whereclause) == '"user".user_id = :user_id_1'

        compiled = update_statement.compile()
        assert compiled.params["nickname"] == new_nickname

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_nickname_with_whitespace(self, mock_session):
        """Test setting a nickname with leading/trailing whitespace."""
        user_id = 1
        nickname_with_whitespace = "  Nickname with Spaces  "
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        UserOperations.set_nickname(user_id, nickname_with_whitespace)

        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt.whereclause) == '"user".user_id = :user_id_1'

    def test_set_nickname_with_unicode_characters(self, mock_session):
        """Test setting a nickname with Unicode characters."""
        # Arrange
        user_id = 1
        nickname = "😊 Ünïcödë Nick 🎉"
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        UserOperations.set_nickname(user_id, nickname)

        # Assert
        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt) == (
            'UPDATE "user" SET nickname=:nickname WHERE "user".user_id = :user_id_1'
        )
        assert update_stmt.compile().params == {
            "nickname": "😊 Ünïcödë Nick 🎉",
            "user_id_1": 1,
        }
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_nickname_database_connection_lost(self, mock_session):
        """Test set_nickname when the database connection is lost."""
        # Arrange
        user_id = 1
        nickname = "new_nickname"
        mock_session.execute.side_effect = OperationalError(
            "statement", "params", "Connection lost"  # type: ignore
        )

        # Act & Assert
        with pytest.raises(OperationalError) as exc_info:
            UserOperations.set_nickname(user_id, nickname)

        assert "Connection lost" in str(exc_info.value)
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
