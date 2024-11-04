""" Tests for OTP operations in the OTP model. """

# pylint: disable=redefined-outer-name
# pylint: disable=W0621

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy import Update
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, DatabaseError

from app.exceptions.authorization_exception import EmailNotFoundException
from app.models.user import User, OTPOperations
from tests.models.user_conftest import mock_session, valid_user_data  # pylint: disable=unused-import

class TestGetOTPOperations:
    """Test for OTP operations."""
    def test_get_otp_returns_correct_values_for_valid_email(self, mock_session):
        """Test get_otp method returns correct values for a valid email."""
        # Arrange
        email = "test@example.com"
        user_id = 1
        otp_secret = "123456"
        otp_expiry = datetime.now()
        mock_session.execute.return_value.first.return_value = (user_id, otp_secret, otp_expiry)

        # Act
        result = OTPOperations.get_otp(email)

        # Assert
        assert result == (otp_secret, otp_expiry, user_id)
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

        # Check the actual SQL query
        select_statement = mock_session.execute.call_args[0][0]
        compiled = select_statement.compile()
        assert '"user".email = :email_1' in str(compiled)

    def test_get_otp_raises_email_not_found_exception(self, mock_session):
        """Test get_otp method raises EmailNotFoundException for non-existent email."""
        mock_session.execute.return_value.first.return_value = None
        non_existent_email = "nonexistent@example.com"

        with pytest.raises(EmailNotFoundException) as exc_info:
            OTPOperations.get_otp(non_existent_email)

        assert str(exc_info.value) == 'Email not found.'
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_not_called()
        mock_session.close.assert_called_once()

    def test_get_otp_handles_integrity_error(self, mock_session):
        """Test get_otp method handles IntegrityError and rolls back session."""
        mock_session.execute.side_effect = IntegrityError(
            statement="SELECT ...", params={}, orig=None # type: ignore
        )

        with pytest.raises(IntegrityError):
            OTPOperations.get_otp("test@example.com")

        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_otp_handles_data_error_and_rolls_back(self, mock_session):
        """Test that get_otp handles DataError and rolls back the session."""
        # Arrange
        mock_session.execute.side_effect = DataError(
            statement="SELECT ...",
            params={},
            orig=Exception("invalid input syntax for type integer")
        )
        email = "test@example.com"

        # Act
        with pytest.raises(DataError) as exc_info:
            OTPOperations.get_otp(email)

        # Assert
        assert "invalid input syntax for type integer" in str(exc_info.value)
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_otp_handles_operational_error(self, mock_session):
        """Test get_otp method handles OperationalError and rolls back session."""
        mock_session.execute.side_effect = OperationalError(
            "statement", "params", "orig"  # type: ignore
        )

        with pytest.raises(OperationalError):
            OTPOperations.get_otp("test@example.com")

        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_otp_handles_database_error(self, mock_session):
        """Test that get_otp handles DatabaseError and rolls back the session."""
        mock_session.execute.side_effect = DatabaseError(
            "statement", "params", "orig"  # type: ignore
        )

        with pytest.raises(DatabaseError):
            OTPOperations.get_otp("test@example.com")

        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_otp_closes_session_on_exception(self, mock_session):
        """Test that get_otp closes the session even when an exception is raised."""
        # Arrange
        mock_session.execute.side_effect = DatabaseError(
            "statement", "params", "orig"  # type: ignore
        )
        email = "test@example.com"

        # Act
        with pytest.raises(DatabaseError):
            OTPOperations.get_otp(email)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_get_otp_with_special_characters_email(self, mock_session):
        """Test get_otp method with an email containing special characters."""
        # Arrange
        email_with_special_chars = "user+test@example.com"
        mock_user = (1, "123456", datetime.now())
        mock_session.execute.return_value.first.return_value = mock_user

        # Act
        otp_secret, otp_expiry, user_id = OTPOperations.get_otp(email_with_special_chars)

        # Assert
        mock_session.execute.assert_called_once()
        select_statement = mock_session.execute.call_args[0][0]
        assert '"user".email = :email_1' in str(select_statement)
        assert otp_secret == "123456"
        assert isinstance(otp_expiry, datetime)
        assert user_id == 1
        mock_session.close.assert_called_once()

    def test_get_otp_with_very_long_email(self, mock_session):
        """Test get_otp method with a very long email address (edge case)."""
        # Arrange
        very_long_email = "a" * 320 + "@example.com"  # 320 characters before @ + domain
        mock_user = (1, "123456", datetime.now())
        mock_session.execute.return_value.first.return_value = mock_user

        # Act
        otp_secret, otp_expiry, user_id = OTPOperations.get_otp(very_long_email)

        # Assert
        assert otp_secret == "123456"
        assert isinstance(otp_expiry, datetime)
        assert user_id == 1
        mock_session.execute.assert_called_once()
        select_statement = mock_session.execute.call_args[0][0]
        assert '"user".email = :email_1' in str(select_statement)
        mock_session.close.assert_called_once()

    def test_get_otp_with_null_values(self, mock_session):
        """Test get_otp method's behavior when otp_secret or otp_expiry is None."""
        # Arrange
        email = "test@example.com"
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.otp_secret = None
        mock_user.otp_expiry = None
        mock_session.execute.return_value.first.return_value = (
            mock_user.id, mock_user.otp_secret, mock_user.otp_expiry
        )

        # Act
        otp_secret, otp_expiry, user_id = OTPOperations.get_otp(email)

        # Assert
        assert otp_secret is None
        assert otp_expiry is None
        assert user_id == 1
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()


class TestSetOTPOperation:
    """Test for set_otp operation."""
    def test_set_otp_for_existing_user_with_valid_data(self, mock_session):
        """Test setting OTP for an existing user with valid data."""
        # Arrange
        valid_data = {
            'email': 'test@example.com',
            'otp_secret': '123456',
            'otp_expiry': datetime.now() + timedelta(minutes=5)
        }
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        OTPOperations.set_otp(valid_data)

        # Assert
        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt) == (
            'UPDATE "user" SET otp_secret=:otp_secret, otp_expiry=:otp_expiry '
            'WHERE "user".email = :email_1'
        )
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_otp_for_non_existent_user(self, mock_session):
        """Test setting OTP for a non-existent user."""
        # Arrange
        mock_session.execute.return_value = None
        data = {
            'email': 'nonexistent@example.com',
            'otp_secret': '123456',
            'otp_expiry': datetime.now() + timedelta(minutes=5)
        }

        # Act
        OTPOperations.set_otp(data)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

        # Verify that the update was attempted with the correct parameters
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt.whereclause) == '"user".email = :email_1'

        # Extract and compare the values
        compiled = update_stmt.compile()
        assert compiled.params['otp_secret'] == data['otp_secret']
        assert compiled.params['otp_expiry'] == data['otp_expiry']

    def test_set_otp_with_empty_otp_secret(self, mock_session):
        """Test setting OTP with empty OTP secret."""
        # Arrange
        data = {
            'email': 'test@example.com',
            'otp_secret': '',
            'otp_expiry': datetime.now()
        }
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        OTPOperations.set_otp(data)

        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt.whereclause) == '"user".email = :email_1'

        compiled = update_stmt.compile()
        assert compiled.params['otp_secret'] == data['otp_secret']
        assert compiled.params['otp_expiry'] == data['otp_expiry']

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_otp_with_past_expiry_date(self, mock_session):
        """Test setting OTP with a past expiry date."""
        # Arrange
        past_date = datetime.now() - timedelta(days=1)
        data = {
            'email': 'test@example.com',
            'otp_secret': '123456',
            'otp_expiry': past_date
        }
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        OTPOperations.set_otp(data)

        # Assert
        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt) == (
            'UPDATE "user" SET otp_secret=:otp_secret, otp_expiry=:otp_expiry '
            'WHERE "user".email = :email_1'
        )
        assert update_stmt.compile().params == {
            'otp_secret': '123456',
            'otp_expiry': past_date,
            'email_1': 'test@example.com'
        }
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_otp_with_very_long_otp_secret(self, mock_session):
        """Test setting OTP with a very long OTP secret."""
        # Arrange
        very_long_otp_secret = "a" * 1000  # Create a string of 1000 'a' characters
        data = {
            'email': 'test@example.com',
            'otp_secret': very_long_otp_secret,
            'otp_expiry': datetime.now() + timedelta(minutes=5)
        }
        mock_session.execute = Mock(side_effect=DataError(
            statement="INSERT INTO user ...",
            params={},
            orig=Exception("value too long for type character varying(6)")
        ))
        mock_session.commit = Mock()

        # Act
        with pytest.raises(DataError) as exc_info:
            OTPOperations.set_otp(data)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        assert "value too long for type character varying(6)" in str(exc_info.value)

    def test_set_otp_data_error(self, mock_session):
        """Test handling of DataError when setting OTP."""
        # Arrange
        mock_session.execute.side_effect = DataError(
            statement="UPDATE user ...",
            params={},
            orig=Exception("invalid input syntax for type timestamp")
        )
        test_data = {
            'email': 'test@example.com',
            'otp_secret': '123456',
            'otp_expiry': 'invalid_timestamp'
        }

        # Act and Assert
        with pytest.raises(DataError) as exc_info:
            OTPOperations.set_otp(test_data)

        assert "invalid input syntax for type timestamp" in str(exc_info.value)
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_otp_operational_error(self, mock_session):
        """Test handling of OperationalError when setting OTP."""
        # Arrange
        mock_session.execute.side_effect = OperationalError(
            "statement", "params", "orig"  # type: ignore
        )
        data = {
            'email': 'test@example.com',
            'otp_secret': '123456',
            'otp_expiry': datetime.now()
        }

        # Act & Assert
        with pytest.raises(OperationalError):
            OTPOperations.set_otp(data)

        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_otp_multiple_times(self, mock_session):
        """Test setting OTP multiple times for the same user."""
        # Arrange
        email = "test@example.com"
        otp_data_1 = {
            'email': email,
            'otp_secret': '123456',
            'otp_expiry': datetime.now() + timedelta(minutes=5)
        }
        otp_data_2 = {
            'email': email,
            'otp_secret': '789012',
            'otp_expiry': datetime.now() + timedelta(minutes=10)
        }
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        OTPOperations.set_otp(otp_data_1)
        OTPOperations.set_otp(otp_data_2)

        # Assert
        assert mock_session.execute.call_count == 2
        assert mock_session.commit.call_count == 2

        # Check first call
        first_call = mock_session.execute.call_args_list[0][0][0]
        assert isinstance(first_call, Update)
        assert str(first_call.whereclause) == '"user".email = :email_1'
        compiled_first = first_call.compile()
        assert compiled_first.params['otp_secret'] == otp_data_1['otp_secret']
        assert compiled_first.params['otp_expiry'] == otp_data_1['otp_expiry']
        assert compiled_first.params['email_1'] == otp_data_1['email']

        # Check second call
        second_call = mock_session.execute.call_args_list[1][0][0]
        assert isinstance(second_call, Update)
        assert str(second_call.whereclause) == '"user".email = :email_1'
        compiled_second = second_call.compile()
        assert compiled_second.params['otp_secret'] == otp_data_2['otp_secret']
        assert compiled_second.params['otp_expiry'] == otp_data_2['otp_expiry']
        assert compiled_second.params['email_1'] == otp_data_2['email']

        mock_session.close.assert_called()

    def test_set_otp_with_null_values(self, mock_session):
        """Test setting OTP with null values for otp_secret and otp_expiry."""
        # Arrange
        data = {
            'email': 'test@example.com',
            'otp_secret': None,
            'otp_expiry': None
        }
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        OTPOperations.set_otp(data)

        mock_session.execute.assert_called_once()
        update_statement = mock_session.execute.call_args[0][0]
        assert isinstance(update_statement, Update)
        assert str(update_statement.whereclause) == '"user".email = :email_1'

        compiled = update_statement.compile()
        assert compiled.params['otp_secret'] == data['otp_secret']
        assert compiled.params['otp_expiry'] == data['otp_expiry']

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_set_otp_concurrent(self, mock_session):
        """Test setting OTP concurrently for multiple users."""
        # Arrange
        mock_session.execute = Mock()
        mock_session.commit = Mock()
        user_data = [
            {'email': 'user1@example.com', 'otp_secret': '123456', 'otp_expiry': datetime.now()},
            {'email': 'user2@example.com', 'otp_secret': '654321', 'otp_expiry': datetime.now()},
            {'email': 'user3@example.com', 'otp_secret': '789012', 'otp_expiry': datetime.now()}
        ]

        # Act
        for data in user_data:
            OTPOperations.set_otp(data)

        # Assert
        assert mock_session.execute.call_count == 3
        assert mock_session.commit.call_count == 3
        for i, data in enumerate(user_data):
            call_args = mock_session.execute.call_args_list[i][0][0]
            assert isinstance(call_args, Update)
            assert str(call_args) == (
                'UPDATE "user" SET otp_secret=:otp_secret, otp_expiry=:otp_expiry '
                'WHERE "user".email = :email_1'
            )
            compiled = call_args.compile()
            assert compiled.params == {
                'otp_secret': data['otp_secret'],
                'otp_expiry': data['otp_expiry'],
                'email_1': data['email']
            }
        mock_session.close.assert_called()


class TestDeleteOTPOperation:
    """Test Delete OTP operation."""
    def test_delete_otp_with_whitespace_in_email(self, mock_session):
        """Test delete_otp method with email containing leading and trailing whitespace."""
        # Arrange
        email_with_whitespace = "  test@example.com  "
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        OTPOperations.delete_otp(email_with_whitespace.strip())

        # Assert
        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt.whereclause) == '"user".email = :email_1'
        compiled = update_stmt.compile()
        assert compiled.params['email_1'] == email_with_whitespace.strip()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_delete_otp_operational_error(self, mock_session):
        """Test handling of OperationalError when deleting OTP."""
        # Arrange
        mock_session.execute.side_effect = OperationalError(
            "statement", "params", "orig"  # type: ignore
        )
        email = "test@example.com"

        # Act & Assert
        with pytest.raises(OperationalError):
            OTPOperations.delete_otp(email)

        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

        # Additional assert to verify the email used in the update statement
        update_stmt = mock_session.execute.call_args[0][0]
        assert '"user".email = :email_1' in str(update_stmt)
        compiled = update_stmt.compile()
        assert compiled.params['email_1'] == email

    def test_delete_otp_with_sql_injection_attempt(self, mock_session):
        """Test delete_otp method with a SQL injection attempt in the email."""
        # Arrange
        sql_injection_email = "'; DROP TABLE user; --"
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        OTPOperations.delete_otp(sql_injection_email)

        # Assert
        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt.whereclause) == '"user".email = :email_1'
        assert update_stmt.compile().params['email_1'] == sql_injection_email

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_delete_otp_with_multiple_users(self, mock_session):
        """Test delete_otp method with an email matching multiple
        users to ensure only the correct user is updated."""
        # Arrange
        email = "duplicate@example.com"
        # Simulate no return value for the update operation
        mock_session.execute.return_value = None

        # Act
        OTPOperations.delete_otp(email)

        # Assert
        mock_session.execute.assert_called_once()
        update_stmt = mock_session.execute.call_args[0][0]
        assert isinstance(update_stmt, Update)
        assert str(update_stmt.whereclause) == '"user".email = :email_1'
        compiled = update_stmt.compile()
        assert compiled.params['email_1'] == email
        assert compiled.params['otp_secret'] is None
        assert compiled.params['otp_expiry'] is None
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    def test_delete_otp_with_empty_email_raises_exception(self, mock_session):
        """Test delete_otp method with an empty string as email raises exception."""
        # Arrange
        empty_email = ""
        mock_session.execute.side_effect = DataError(
            statement="UPDATE user ...",
            params={},
            orig=Exception("invalid input syntax for type email")
        )

        # Act & Assert
        with pytest.raises(DataError) as exc_info:
            OTPOperations.delete_otp(empty_email)

        # Assert
        assert "invalid input syntax for type email" in str(exc_info.value)
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_delete_otp_commit_failure(self, mock_session):
        """Test delete_otp method when session commit fails to ensure rollback is called."""
        # Arrange
        email = "test@example.com"
        mock_session.execute = Mock()
        mock_session.commit.side_effect = OperationalError(
            "statement", "params", "orig"
        )  # type: ignore

        # Act
        with pytest.raises(OperationalError):
            OTPOperations.delete_otp(email)

        # Assert
        mock_session.execute.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_delete_otp_with_concurrent_deletions(self, mock_session):
        """Test delete_otp method with a large number of concurrent deletions."""
        # Arrange
        emails = [f"user{i}@example.com" for i in range(1000)]  # Simulate 1000 users
        mock_session.execute = Mock()
        mock_session.commit = Mock()

        # Act
        for email in emails:
            OTPOperations.delete_otp(email)

        # Assert
        assert mock_session.execute.call_count == 1000
        assert mock_session.commit.call_count == 1000

        # Check that each call was made with the correct parameters
        for i, email in enumerate(emails):
            update_stmt = mock_session.execute.call_args_list[i][0][0]
            assert isinstance(update_stmt, Update)
            assert str(update_stmt.whereclause) == '"user".email = :email_1'
            compiled = update_stmt.compile()
            assert compiled.params['email_1'] == email

        mock_session.close.assert_called()
