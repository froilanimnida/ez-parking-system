"""Fixtures for the user model tests."""

from datetime import datetime
from uuid import uuid4

from unittest.mock import Mock, patch

import pytest


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
        "phone_number": "+1234567890",
        "email": "test@example.com",
        'creation_date': datetime.now(),
        'role': 'user',
        'otp_secret': None,
        'otp_expiry': None,
    }
