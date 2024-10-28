from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug import run_simple

from app import create_app

load_dotenv(dotenv_path='.env')

app = create_app()
CORS(app, supports_credentials=True, origins='*')


if __name__ == '__main__':
    run_simple(
        'localhost',
        5000,
        app,
        threaded=True,
        use_reloader=True,
        use_debugger=True
    )
