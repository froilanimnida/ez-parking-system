""" This is the entry point of the application. """

# pylint: disable=C0413, C0415, W0621

from os import getenv

from dotenv import load_dotenv, find_dotenv
from werkzeug import run_simple

load_dotenv(find_dotenv())

from app import create_app

app = create_app()

def create_ssl_context():
    """This function creates an SSL context for the Flask app."""
    from ssl import SSLContext, PROTOCOL_TLS_SERVER
    ssl_context = SSLContext(protocol=PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile="certificates/localhost+2.pem",
        keyfile="certificates/localhost+2-key.pem",
    )
    return ssl_context

def run_dev_server():
    """Run the development server with SSL"""
    run_simple(
        hostname="0.0.0.0",
        # ssl_context=create_ssl_context(),
        port=5000,
        application=app,
        threaded=True,
        use_reloader=False,
        use_debugger=True,
    )

ENVIRONMENT = getenv("ENVIRONMENT", "")

if __name__ == "__main__":
    if ENVIRONMENT == "production":
        app.run(host="0.0.0.0", port=5000)
    else:
        from watchfiles import run_process
        run_process(
            ".",  # Monitor current directory
            target=run_dev_server,
            watch_filter=lambda change, path: (
                path.endswith(".py") or
                "/templates/" in path or
                "/static/" in path
            )
        )
