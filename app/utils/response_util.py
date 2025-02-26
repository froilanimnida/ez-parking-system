""" This is the modularize set response function that can be use anywhere inside the project """

from email.utils import formatdate
from time import time
from flask import make_response, jsonify, json


def set_response(status_code: int, data):
    """
    Sets the response for the API with proper timezone handling.

    Args:
        status_code (int): HTTP status code
        data: Response data to be JSON serialized

    Returns:
        Response: Flask response object with proper headers
    """
    response = make_response(jsonify(data), status_code)
    response.headers["Content-Type"] = "application/json"
    response.headers["Date"] = formatdate(time(), usegmt=True)
    response_data = json.dumps(data)
    response.data = response_data
    response.status_code = status_code
    response.headers["Content-Length"] = str(len(response_data))
    return response
