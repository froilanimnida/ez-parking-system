""" Flask extension for the application. """

import boto3
from flask_mail import Mail
from flask_smorest import Api
from celery import Celery

api = Api()
mail = Mail()
s3_client = boto3.client('s3')
celery = Celery()
