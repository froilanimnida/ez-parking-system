""" Set up the logger for the application. """

from logging import INFO, Formatter
from logging.handlers import RotatingFileHandler
from os import path, makedirs

from filelock import FileLock
from flask import Flask


def setup_logging(app: Flask):  # pylint: disable=C0116
    log_dir = path.join(app.root_path, "logs")
    makedirs(log_dir, exist_ok=True)
    log_file_path = path.join(log_dir, "app.log")
    lock_file_path = log_file_path + ".lock"
    with FileLock(lock_file_path):
        file_handler = RotatingFileHandler(log_file_path, maxBytes=100000, backupCount=3)
        file_handler.setLevel(INFO)
        file_handler.setFormatter(Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(INFO)
