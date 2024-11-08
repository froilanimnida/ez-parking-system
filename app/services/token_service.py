""" This module contains the TokenService class. """

from typing import Literal
from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token


class TokenService:  # pylint: disable=C0115
    @staticmethod
    def generate_jwt_csrf_token(
        email,
        user_id,
        role: Literal["user", "parking_manager", "admin"],
        remember_me=False,
    ):
        """Generate JWT access and refresh tokens."""
        access_token = create_access_token(
            identity={"email": email, "user_id": user_id},
            expires_delta=timedelta(days=1) if not remember_me else timedelta(days=30),
            fresh=True,
            additional_claims={"role": role},
        )
        refresh_token = create_refresh_token(
            identity={"email": email, "user_id": user_id}
        )
        return access_token, refresh_token

    @staticmethod
    def refresh_nearly_expired_token(access_token):
        """Refresh the nearly expired token."""
        print("Refreshing token")
        print(access_token)
