"""Utility functions for working with timezones"""

from datetime import datetime
from flask import current_app

def get_current_time():
    """Get current time in UTC"""
    return datetime.now(current_app.config["STORAGE_TIMEZONE"])

def convert_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt.tzinfo is None:
        utc_dt = current_app.config["STORAGE_TIMEZONE"].localize(utc_dt)
    return utc_dt.astimezone(current_app.config["DISPLAY_TIMEZONE"])

def convert_to_utc(local_dt):
    """Convert local datetime to UTC"""
    if local_dt.tzinfo is None:
        local_dt = current_app.config["DISPLAY_TIMEZONE"].localize(local_dt)
    return local_dt.astimezone(current_app.config["STORAGE_TIMEZONE"])
