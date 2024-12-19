""" This is the modularize set response function that can be use anywhere inside the project """

from datetime import datetime

from flask import make_response, jsonify, json


def set_response(status_code: int, data):
    """This function sets the response for the API."""
    response = make_response(jsonify(data), status_code)
    response.headers["Content-Type"] = "application/json"
    response.headers["Date"] = f"{datetime.now()}"
    response_data = json.dumps(data)
    response.data = response_data
    response.status_code = status_code
    response.headers["Content-Length"] = str(len(response_data))
    return response
