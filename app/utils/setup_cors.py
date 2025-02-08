"""This module contains the function to set up CORS for the application."""

from os import getenv

from flask import Flask
from flask_cors import CORS


def set_up_cors(app: Flask):
    """Set up CORS for the application."""
    frontend_urls = getenv("FRONTEND_URL", "").split(",")
    static_origins = [
        "https://ez-parking.expo.app",
        "https://ez-parking-gamma.vercel.app",
        "https://ez-parking.vercel.app",
        "https://fuzzy-fortnight-j7vvwpjqjwr2vq6-8081.app.github.dev"
    ]

    allowed_origins = frontend_urls + static_origins

    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins,
        allow_headers=[
            "Content-Type", "X-CSRF-TOKEN", "Accept",
            "Authorization", "csrf_refresh_token", "refresh_token_cookie"
        ],
        expose_headers=["Set-Cookie", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    return app
