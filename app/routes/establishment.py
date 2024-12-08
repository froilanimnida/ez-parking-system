""" Routes related to parking establishment. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from flask.views import MethodView
from flask_smorest import Blueprint

from app.exceptions.establishment_lookup_exceptions import (
    EstablishmentDoesNotExist,
    EstablishmentEditsNotAllowedException,
)
from app.schema.query_validation import (
    EstablishmentQuerySchema,
    EstablishmentQueryValidation,
)
from app.schema.response_schema import EstablishmentResponseSchema
from app.services.establishment_service import EstablishmentService
from app.utils.error_handlers.establishment_error_handlers import (
    handle_establishment_does_not_exist,
    handle_establishment_edits_not_allowed,
)
from app.utils.response_util import set_response

establishment_blp = Blueprint(
    "establishment",
    __name__,
    url_prefix="/api/v1/establishment",
    description="Establishment API for EZ Parking System Frontend",
)


@establishment_blp.route("/query")
class GetEstablishments(MethodView):
    @establishment_blp.arguments(EstablishmentQuerySchema)
    @establishment_blp.response(200, EstablishmentResponseSchema)
    @establishment_blp.doc(
        description="Get establishments with optional filters and sorting",
        responses={
            200: "Establishments retrieved successfully.",
            400: "Bad Request",
        },
    )
    def get(self, query_params):
        establishments = EstablishmentService.get_establishments(query_params)

        return set_response(
            200,
            {
                "code": "success",
                "message": "Establishments retrieved successfully.",
                "establishments": establishments,
            },
        )


@establishment_blp.route("/info")
class GetEstablishmentInfo(MethodView):
    @establishment_blp.arguments(EstablishmentQueryValidation, location="query")
    @establishment_blp.response(200, EstablishmentResponseSchema)
    @establishment_blp.doc(
        description="Get establishment information by uuid and all slots of the establishment",
        responses={
            200: "Establishment information retrieved successfully.",
            400: "Bad Request",
        },
    )
    def get(self, query_params):
        establishment = EstablishmentService.get_establishment(query_params.get("establishment_uuid"))
        return set_response(
            200,
            {
                "code": "success",
                "message": "Establishment information retrieved successfully.",
                "establishment": establishment,
            },
        )


establishment_blp.register_error_handler(
    EstablishmentDoesNotExist, handle_establishment_does_not_exist
)
establishment_blp.register_error_handler(
    EstablishmentEditsNotAllowedException, handle_establishment_edits_not_allowed
)
