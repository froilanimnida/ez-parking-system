"""This module contains the function to set up CORS for the application."""

from os import getenv

from flask import Flask
from flask_cors import CORS


def set_up_cors(app: Flask):
    """Set up CORS for the application."""
    allowed_origins = getenv("FRONTEND_URL").split(",")

    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins,
        allow_headers=["Content-Type", "X-CSRF-TOKEN", "Accept", "Authorization"],
        expose_headers=["Set-Cookie", "Authorization", ],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    return app
