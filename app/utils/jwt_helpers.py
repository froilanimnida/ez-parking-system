"""This module contains helper functions for working with JWTs."""

from datetime import datetime, timedelta, timezone
from logging import getLogger

from flask import Response, request
from flask_jwt_extended import get_jwt, set_access_cookies, set_refresh_cookies, get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import InvalidHeaderError
from werkzeug.exceptions import Unauthorized

from app.services.token_service import TokenService
from app.utils.timezone_utils import get_current_time

logger = getLogger(__name__)



def refresh_token_before_request():
    """
    Refresh JWT before request processing if it's about to expire.
    This ensures the user has a valid token before hitting protected endpoints.
    """
    try:
        verify_jwt_in_request()  # Ensures we have a valid JWT
        jwt_data = get_jwt()
        exp_timestamp = jwt_data["exp"]

        now = get_current_time()
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))

        if target_timestamp > exp_timestamp:
            identity = get_jwt_identity()
            role = jwt_data["sub"].get("role")

            print("Refreshing access token before request...")

            token_service = TokenService()
            access_token, refresh_token = token_service.generate_jwt_csrf_token(
                email=identity["email"],
                user_id=identity["user_id"],
                role=role
            )

            response = Response()
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            logger.info("Access token refreshed before request.")

    except Exception as e:
        logger.warning(f"JWT refresh failed: {e}")
        raise Unauthorized("Invalid or expired token.")

# Attach it to the Flask app
def add_jwt_before_request_handler(app):
    app.before_request(refresh_token_before_request)
