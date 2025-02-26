""" Security utilities for generating high-entropy seeds. """

from base64 import b32encode, urlsafe_b64encode
from datetime import timedelta
from hashlib import sha256
from os import getenv, getpid, urandom, times
from socket import gethostname
from time import time_ns, time, perf_counter_ns

from psutil import Process
from pyotp import TOTP

from app.exceptions.general_exceptions import FileSizeTooBig
from app.utils.timezone_utils import get_current_time


def get_otp_seed() -> str:
    """
    Generate a high-entropy seed for cryptographic operations.

    Returns:
        str: A hex string derived from multiple entropy sources.
    """
    try:
        process_id = str(getpid())
        hostname = gethostname()
        nano_time = str(time_ns())
        random_bytes = urandom(16).hex()
        memory_info = str(Process().memory_info().rss)
        totp_secret = str(getenv("TOTP_SECRET_KEY", ""))
        current_time = str(int(time()))

        combined = (
            f"{totp_secret}"
            f"{current_time}"
            f"{process_id}"
            f"{hostname}"
            f"{nano_time}"
            f"{random_bytes}"
            f"{memory_info}"
        )
        return sha256(combined.encode()).hexdigest()

    except Exception:  # pylint: disable=W0718
        system_time = str(perf_counter_ns())
        process_start_time = str(times().user)
        totp_secret = str(getenv("TOTP_SECRET_KEY", ""))
        current_time = str(int(time()))

        combined = (
            f"{totp_secret}" f"{current_time}" f"{system_time}" f"{process_start_time}"
        )
        return sha256(combined.encode()).hexdigest()

def generate_otp() -> tuple:
    """
    Generate a six-digit OTP using TOTP.

    Returns:
        tuple: A tuple containing the OTP code and its expiry time.
    """
    return (
        TOTP(
            b32encode(bytes.fromhex(f"{getenv('TOTP_SECRET_KEY')}{int(time())}")).decode("UTF-8"),
            digits=6,
            interval=300,
            digest=sha256).now(),
        get_current_time() + timedelta(minutes=5)
    )

def generate_token():
    """ Generate url safe token """
    return urlsafe_b64encode(urandom(128)).decode("utf-8").rstrip("=")

def get_random_string() -> str:
    """ Generate a random string of 32 characters. """
    return urandom(32).hex()

def check_file_size(request):
    """ Check the size of the files in the request. """
    for key, file in request.files.items():
        if file.content_length > 1024 * 1024 * 10:
            raise FileSizeTooBig(f"File size too large: {key}")
