""" This is the entry point of the application. """

# pylint: disable=C0413

from os import getenv
from ssl import SSLContext, PROTOCOL_TLS_SERVER

from flask_cors import CORS
from dotenv import load_dotenv, find_dotenv
from werkzeug import run_simple

load_dotenv(find_dotenv())


from app import create_app


def create_ssl_context():
    """This function creates an SSL context for the Flask app."""
    ssl_context = SSLContext(protocol=PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile="certificates/localhost+2.pem",
        keyfile="certificates/localhost+2-key.pem",
    )
    return ssl_context


ENVIRONMENT = getenv("ENVIRONMENT", "")

IS_PRODUCTION = ENVIRONMENT == "production"

URL = IS_PRODUCTION and getenv("PRODUCTION_URL") or getenv("DEVELOPMENT_URL")

app = create_app()
CORS(
    app,
    supports_credentials=True,
    origins=URL,
    allow_headers=["Content-Type", "X-CSRF-TOKEN", "Accept"],
    expose_headers=["Set-Cookie", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)

if __name__ == "__main__":
    if IS_PRODUCTION:
        app.run(host="0.0.0.0", port=5000)
    else:
        run_simple(
            hostname="localhost",
            ssl_context=create_ssl_context(),
            port=5000,
            application=app,
            threaded=True,
            use_reloader=True,
            use_debugger=True,
        )
