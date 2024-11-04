""" Test cases for user models in the database. """

from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4, UUID

import pytest

from app.models.user import User, UserOperations

@pytest.fixture
def mock_session():
    """Mock the session object."""
    with patch('app.models.user.get_session') as mock:
        session = Mock()
        mock.return_value = session
        yield session


@pytest.fixture
def valid_user_data():
    """ Represents a valid user data. """
    return {
        'uuid': uuid4().bytes,
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        'creation_date': datetime.now(),
        'role': 'user',
        'otp_secret': None,
        'otp_expiry': None,
    }


# noinspection PyTypeHints,SqlNoDataSourceInspection
class TestUserOperation:
    """Test for user operations."""
    def test_create_user_when_input_valid(self, mock_session, valid_user_data):  # pylint: disable=C0103
        """Test creating a new user with valid data."""
        mock_session.commit = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_session.add.return_value = None

        def side_effect(user):
            user.id = 1
        mock_session.add.side_effect = side_effect

        user_id = UserOperations.create_new_user(valid_user_data)

        assert user_id == 1  #type: ignore
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

        user_obj = mock_session.add.call_args[0][0]
        assert isinstance(user_obj, User)
        assert user_obj.first_name == valid_user_data["first_name"]
        assert user_obj.last_name == valid_user_data["last_name"]
        assert user_obj.email == valid_user_data["email"]
        assert user_obj.creation_date == valid_user_data["creation_date"]
        assert user_obj.role == valid_user_data["role"]
        assert user_obj.otp_secret == valid_user_data["otp_secret"]
        assert user_obj.otp_expiry == valid_user_data["otp_expiry"]
        assert isinstance(user_obj.uuid, bytes)
