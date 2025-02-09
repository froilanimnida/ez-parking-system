""" Base configuration for the application. """

from datetime import timedelta
from os import getenv, getcwd, path


class BaseConfig:  # pylint: disable=too-few-public-methods
    """Base configuration."""

    SECRET_KEY = getenv("SECRET_KEY")
    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY")
    ENCRYPTION_KEY = getenv("ENCRYPTION_KEY", "")

    JWT_ALGORITHM = "HS256"
    JWT_DECODE_ALGORITHMS = ["HS256"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

    API_TITLE = "EZ-Parking API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"

    MAIL_SERVER = getenv("MAIL_SERVER")
    MAIL_PORT = getenv("MAIL_PORT")
    MAIL_USE_TLS = getenv("MAIL_USE_TLS")
    MAIL_USERNAME = getenv("MAIL_USERNAME")
    MAIL_PASSWORD = getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = getenv("MAIL_DEFAULT_SENDER")

    JWT_TOKEN_LOCATION = "cookies"
    JWT_COOKIE_SECURE = bool(getenv("JWT_COOKIE_SECURE", "True"))
    JWT_SESSION_COOKIE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = "None"
    JWT_CSRF_CHECK_FORM = False
    JWT_CSRF_IN_COOKIES = True
    JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
    
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    LOGGING_LEVEL = "INFO"
    LOGGING_PATH = path.join(getcwd(), "logs", "authentication.log")
    IS_PRODUCTION = getenv("ENVIRONMENT", "") == "production"

    FRONTEND_URL = getenv("FRONTEND_URL", "http://localhost:5000")
    CELERY_BROKER_URL = getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    R2_ACCOUNT_ID = getenv("R2_ACCOUNT_ID")
    R2_ACCESS_KEY_ID = getenv("R2_ACCESS_KEY_ID")
    R2_SECRET_ACCESS_KEY = getenv("R2_SECRET_ACCESS_KEY")
    R2_BUCKET_NAME = getenv("R2_BUCKET_NAME")
    R2_ENDPOINT = getenv("R2_ENDPOINT")
