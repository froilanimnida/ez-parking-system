""" Business Intelligence Routes """

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint

from app.services.reports import Reports
from app.schema.reports_validation import RevenueReportSchema
from app.utils.response_util import set_response
from app.utils.role_decorator import parking_manager_role_required

reports_blp = Blueprint(
    "reports",
    __name__,
    url_prefix="/api/v1/reports",
    description="Reports API for EZ Parking System Frontend"
)

@reports_blp.route("/occupancy")
class OccupancyReport(MethodView):
    """Occupancy report endpoint."""
    @reports_blp.doc(
        description="Get occupancy report.",
        responses={200: {"description": "Occupancy report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        """
        Return an occupancy report.
        """
        data = Reports.occupancy_report(user_id)
        return set_response(
            200,
            {
                "code": "success",
                "message": "Occupancy report.",
                "data": data
            }
        )

@reports_blp.route("/revenue")
class RevenueReport(MethodView):
    """Revenue report endpoint."""
    @reports_blp.arguments(RevenueReportSchema, location="query")
    @reports_blp.doc(
        description="Get revenue report.",
        responses={200: {"description": "Revenue report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, data, user_id):
        """
        Return a revenue report.
        """
        reports = Reports.revenue_report(
            user_id,
            data.get("start_date"),
            data.get("end_date")
        )
        return set_response(
            200,
            {
                "code": "success",
                "message": "Revenue report.",
                "data": reports
            }
        )

@reports_blp.route("/peak-hours")
class PeakHoursReport(MethodView):
    """Peak hours report endpoint."""
    @reports_blp.doc(
        description="Get peak hours report.",
        responses={200: {"description": "Peak hours report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):  # pylint: disable=unused-argument
        """
        Return a peak hours report.
        """
        return set_response(200, {"code": "success", "message": "Peak hours report."})


@reports_blp.route("/vehicle-dist")
class VehicleDistributionReport(MethodView):
    """Vehicle distribution report endpoint."""
    @reports_blp.doc(
        description="Get vehicle distribution report.",
        responses={200: {"description": "Vehicle distribution report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        """
        Return a vehicle distribution report.
        """
        print(user_id)
        return set_response(200, {"code": "success", "message": "Vehicle distribution report."})

@reports_blp.route("/duration-stats")
class DurationStatsReport(MethodView):
    """Duration stats report endpoint."""
    @reports_blp.doc(
        description="Get duration stats report.",
        responses={200: {"description": "Duration stats report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        """
        Return a duration stats report.
        """
        print(user_id)
        return set_response(200, {"code": "success", "message": "Duration stats report."})

@reports_blp.route("/payment-stats")
class PaymentStatsReport(MethodView):
    """Payment stats report endpoint."""
    @reports_blp.doc(
        description="Get payment stats report.",
        responses={200: {"description": "Payment stats report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        """
        Return a payment stats report.
        """
        print(user_id)
        return set_response(200, {"code": "success", "message": "Payment stats report."})

@reports_blp.route('/utilization')
class UtilizationReport(MethodView):
    """Utilization report endpoint."""
    @reports_blp.doc(
        description="Get utilization report.",
        responses={200: {"description": "Utilization report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        """
        Return a utilization report.
        """
        print(user_id)
        return set_response(200, {"code": "success", "message": "Utilization report."})

@reports_blp.route("/premium-analysis")
class PremiumAnalysisReport(MethodView):
    """Premium analysis report endpoint."""
    @reports_blp.doc(
        description="Get premium analysis report.",
        responses={200: {"description": "Premium analysis report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        """
        Return a premium analysis report.
        """
        print(user_id)
        return set_response(200, {"code": "success", "message": "Premium analysis report."})

@reports_blp.route("/trends")
class TrendsReport(MethodView):
    """Trends report endpoint."""
    @reports_blp.doc(
        description="Get trends report.",
        responses={200: {"description": "Trends report"}}
    )
    @jwt_required(False)
    @parking_manager_role_required()
    def get(self, user_id):
        """
        Return a trends report.
        """
        print(user_id)
        return set_response(200, {"code": "success", "message": "Trends report."})
