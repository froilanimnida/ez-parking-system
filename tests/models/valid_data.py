""" Returns the session """

from datetime import datetime
from uuid import uuid4

import pytest

@pytest.fixture
def valid_user_data():
    """Represents a valid user data."""
    return {
        "uuid": uuid4().bytes,
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1234567890",
        "email": "test@example.com",
        "creation_date": datetime.now(),
        "role": "user",
        "otp_secret": None,
        "otp_expiry": None,
    }
