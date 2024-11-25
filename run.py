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

app = create_app()
CORS(
    app,
    supports_credentials=True,
    origins=[
        "https://127.0.0.1:5500",
        "https://localhost:5173",
        getenv("LIVE_FRONTEND_URL", ""),
    ],
)

if __name__ == "__main__":
    if IS_PRODUCTION:
        # In production (e.g., on Render), we don't need SSL handling.
        app.run(host="0.0.0.0", port=5000)
    else:
        # In development, run with SSL
        run_simple(
            hostname="localhost",
            ssl_context=create_ssl_context(),
            port=5000,
            application=app,
            threaded=True,
            use_reloader=True,
            use_debugger=True,
        )
