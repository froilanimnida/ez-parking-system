""" Production configuration. """

from os import getenv
from app.config.base_config import BaseConfig


class ProductionConfig(BaseConfig):  # pylint: disable=R0903
    """Production configuration."""

    DEBUG = False
    MAIL_USERNAME = getenv("MAIL_USERNAME")
    R2_ENDPOINT_URL = f"https://{getenv("R2_ACCOUNT_ID")}.r2.cloudflarestorage.com"
