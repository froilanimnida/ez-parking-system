"""Health check endpoint."""

from flask_smorest import Blueprint
from flask.views import MethodView
from app.utils.response_util import set_response

health = Blueprint(
    "health", __name__, url_prefix="/health", description="Health check endpoint."
)

@health.route("/check")
class HealthCheck(MethodView):
    """Health check endpoint for API monitoring."""
    @health.doc(
        description="Simple health check endpoint.",
        responses={200: {"description": "Health check passed"}}
    )
    def get(self):
        """
        Return a health status response.
        Useful for verifying API uptime and monitoring systems.
        """
        return set_response(200, {"code": "success", "message": "Health check passed"})
