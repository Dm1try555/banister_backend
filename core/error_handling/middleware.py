from rest_framework.views import exception_handler
from rest_framework import serializers
from .utils import create_error_response, handle_validation_error
from .enums import ErrorCode


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
        # Handle specific DRF exceptions with proper error codes
        if response.status_code == 404:
            # Try to determine the correct error code based on the endpoint
            endpoint = request.path if request else ""
            if '/users/' in endpoint or '/admin/users/' in endpoint:
                error_code = ErrorCode.USER_NOT_FOUND
            elif '/services/' in endpoint:
                error_code = ErrorCode.SERVICE_NOT_FOUND
            elif '/bookings/' in endpoint:
                error_code = ErrorCode.BOOKING_NOT_FOUND
            elif '/documents/' in endpoint:
                error_code = ErrorCode.DOCUMENT_NOT_FOUND
            elif '/withdrawals/' in endpoint:
                error_code = ErrorCode.WITHDRAWAL_NOT_FOUND
            elif '/notifications/' in endpoint:
                error_code = ErrorCode.NOTIFICATION_NOT_FOUND
            elif '/chat/' in endpoint:
                error_code = ErrorCode.CHAT_ROOM_NOT_FOUND
            elif '/dashboard/' in endpoint:
                error_code = ErrorCode.DASHBOARD_NOT_FOUND
            else:
                error_code = None
            
            if error_code:
                return create_error_response(
                    error_code=error_code,
                    detail=str(response.data.get("detail", response.data)),
                    request=request
                )
        
        # All other errors are processed the same
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