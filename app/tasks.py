""" Wrapper for tasks that should be done asynchronously. """

from flask_mail import Message

from app.extension import mail, celery


@celery.task
def send_mail(email: str, message: str, subject: str):
    """This function sends an email."""
    msg = Message(subject=subject, recipients=[email])
    msg.html = message
    mail.send(msg)
