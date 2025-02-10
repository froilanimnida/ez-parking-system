""" This module contains the TokenService class. """

from typing import Literal
from datetime import timedelta, datetime

from flask_jwt_extended import create_access_token, create_refresh_token

from app.utils.timezone_utils import get_current_time


class TokenService:  # pylint: disable=C0115, R0903
    @staticmethod
    def generate_jwt_csrf_token(
        email,
        user_id,
        role: Literal["user", "parking_manager", "admin"],
        remember_me=False,
    ) -> tuple[str, str]:
        """
        Generate JWT access and refresh tokens.

        Args:
            email: User's email
            user_id: User's ID
            role: User's role (user, parking_manager, or admin)
            remember_me: Whether to extend token expiry for remember me functionality

        Returns:
            tuple: (access_token, refresh_token)
        """
        # Use UTC for JWT operations as per standard
        now = get_current_time()

        access_token = create_access_token(
            identity={"email": email, "user_id": user_id},
            expires_delta=timedelta(days=30 if remember_me else 1),
            fresh=True,
            additional_claims={
                "role": role,
                "iat": datetime.timestamp(now)
            }
        )

        refresh_token = create_refresh_token(
            identity={"email": email, "user_id": user_id}
        )

        return access_token, refresh_token
