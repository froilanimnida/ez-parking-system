"""Celery configuration for the application."""

from celery import Celery

def make_celery(app):
    """Create a Celery instance for the Flask app."""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery
