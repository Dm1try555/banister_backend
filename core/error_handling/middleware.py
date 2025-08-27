from rest_framework.views import exception_handler
from rest_framework import serializers
from .utils import create_error_response, handle_validation_error


def custom_exception_handler(exc, context):
    request = context.get("request")

    # Handle custom validation errors from views
    if hasattr(exc, 'error_code'):
        return create_error_response(
            error_code=exc.error_code,
            detail=exc.detail,
            request=request
        )

    # Handling validation errors
    if isinstance(exc, serializers.ValidationError):
        return handle_validation_error(exc.detail, request)

    # Standard DRF exceptions
    response = exception_handler(exc, context)
    if response is not None:
        # All errors are processed the same
        return create_error_response(
            error_code=None,
            detail=str(response.data.get("detail", response.data)),
            status_code=response.status_code,
            request=request
        )

    # Fallback for unexpected errors
    return create_error_response(
        error_code=None,
        detail=str(exc),
        status_code=500,
        request=request
    )