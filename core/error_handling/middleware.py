from rest_framework.views import exception_handler
from rest_framework import serializers
from .exceptions import CustomAPIException
from .utils import create_error_response, handle_validation_error


def custom_exception_handler(exc, context):
    request = context.get("request")

    # Our custom exceptions
    if isinstance(exc, CustomAPIException):
        return create_error_response(
            error_code=exc.error_code,
            detail=str(exc.detail),
            status_code=exc.status_code,
            request=request
        )

    # Handle validation errors specifically
    if isinstance(exc, serializers.ValidationError):
        return handle_validation_error(exc.detail, request)

    # Standard DRF exceptions
    response = exception_handler(exc, context)
    if response is not None:
        return create_error_response(
            error_code=None,  # no binding to ErrorCode
            detail=str(response.data.get("detail", response.data)),
            status_code=response.status_code,
            request=request
        )

    # Fallback (unexpected errors)
    return create_error_response(
        error_code=None,
        detail=str(exc),
        status_code=500,
        request=request
    )