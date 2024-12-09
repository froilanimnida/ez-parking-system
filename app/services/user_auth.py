""" Wraps user authentication and registration services. """

from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from os import getenv, urandom

from flask import render_template

from app.exceptions.authorization_exceptions import (
    EmailAlreadyTaken,
    PhoneNumberAlreadyTaken,
)
from app.models.address import AddressRepository
from app.models.company_profile import CompanyProfileRepository
from app.models.operating_hour import OperatingHoursRepository
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.pricing_plan import PricingPlanRepository
from app.models.user import UserRepository
from app.tasks import send_mail

