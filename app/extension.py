""" Flask extension for the application. """

import boto3
from flask_mail import Mail
from flask_smorest import Api

api = Api()
mail = Mail()
s3_client = boto3.client('s3')
