""" Configuration for the tests. """

from unittest.mock import Mock, patch

import pytest

@pytest.fixture
def mock_session():
    """Mock the session object."""
    session = Mock(autospec=True)
    with patch("app.utils.engine.session_local", return_value=session):
        yield session
