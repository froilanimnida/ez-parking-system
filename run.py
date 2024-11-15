""" This is the entry point of the application. """

from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug import run_simple
from ssl import SSLContext, PROTOCOL_TLS_SERVER

from app import create_app

load_dotenv(dotenv_path=".env")

def create_ssl_context():
    """This function creates an SSL context for the Flask app."""
    ssl_context = SSLContext(protocol=PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile="certificates/localhost+2.pem", keyfile="certificates/localhost+2-key.pem"
    )
    return ssl_context

app = create_app()
CORS(app, supports_credentials=True, origins="*")

if __name__ == "__main__":
    run_simple(
        hostname="localhost",
        ssl_context=create_ssl_context(),
        port=5000,
        application=app,
        threaded=True,
        use_reloader=True,
        use_debugger=True,
    )
