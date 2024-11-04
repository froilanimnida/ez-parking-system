""" This is the entry point of the application. """

from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug import run_simple

from app import create_app

load_dotenv(dotenv_path='.env')

app = create_app()
CORS(app, supports_credentials=True, origins='*')


if __name__ == '__main__':
    # app.run(
    #     host='localhost',
    #     port=5000,
    #     debug=True,
    #     threaded=True,
    #     load_dotenv=True,
    # )
    run_simple(
        hostname='localhost',
        port=5000,
        application=app,
        threaded=True,
        use_reloader=True,
        use_debugger=True,
    )
