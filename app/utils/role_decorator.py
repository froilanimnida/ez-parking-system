""" Role Decorator Module """

# pylint: disable=missing-function-docstring

from functools import wraps

from flask_jwt_extended import get_jwt

from app.utils.response_util import set_response

def admin_role_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data = get_jwt()
            is_admin = jwt_data.get("role") == "admin"
            if not is_admin:
                return set_response(
                    401, {"code": "unauthorized", "message": "Admin required."}
                )
            admin_id = jwt_data.get("sub", {}).get("user_id")
            return fn(admin_id=admin_id, *args, **kwargs)
        return decorator
    return wrapper

def parking_manager_role_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data = get_jwt()
            is_parking_manager = jwt_data.get("role") == "parking_manager"
            is_admin = jwt_data.get("role") == "admin"
            if not is_parking_manager and not is_admin:
                return set_response(
                    401,
                    {
                        "code": "unauthorized",
                        "message": "Parking manager or admin required.",
                    },
                )
            user_id = jwt_data.get("sub", {}).get("user_id")
            return fn(*args, user_id=user_id, **kwargs)
        return decorator
    return wrapper

def user_role_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data = get_jwt()
            is_user = jwt_data.get("role") == "user"
            if not is_user:
                return set_response(
                    401, {"code": "unauthorized", "message": "User required."}
                )
            user_id = jwt_data.get("sub", {}).get("user_id")
            return fn(user_id=user_id, *args, **kwargs)
        return decorator
    return wrapper
