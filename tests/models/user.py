"""Tests for the User model."""

# pylint: disable=redefined-outer-name

from uuid import uuid4
from unittest.mock import patch, Mock

import pytest

from app.models.user import UserOperations

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
        'nickname': 'jdoe',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone_number': '+1234567890',
        'role': 'user',
        'otp_secret': None,
        'otp_expiry': None,
    }


# noinspection PyTypeHints,SqlNoDataSourceInspection
class TestUserOperation:
    """Test for user operations."""
    def test_create_user_when_input_valid(self, mock_session, valid_user_data):
        """Test creating a new user with valid data."""
        mock_session.commit = Mock()
        mock_user = Mock()
        mock_user.user_id = 1
        mock_session.add.return_value = None
        
    