""" Security utilities for generating high-entropy seeds. """

from datetime import datetime, timedelta
from base64 import b32encode
from os import getenv, getpid, urandom, times
from time import time_ns, time, perf_counter_ns
from socket import gethostname
from hashlib import sha256

from psutil import Process
from pyotp import TOTP


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
        datetime.now() + timedelta(minutes=5)
    )