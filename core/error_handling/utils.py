from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .enums import ErrorCode


def create_error_response(error_code: ErrorCode = None, detail=None, status_code=None, request=None):
    """Creates a unified error format for all types"""
    if error_code:
        # For our ErrorCode (from serializers)
        status_code = status_code or get_status_code_from_error_code(error_code)
        error_code_num = error_code.code
        title = error_code.title
        description = detail or error_code.description
    else:
        # For standard DRF errors (401, 404, 500, etc.)
        status_code = status_code or 400
        error_code = get_error_code_by_status(status_code)
        error_code_num = error_code.code
        title = error_code.title
        description = detail or error_code.description
    
    exception_type = get_exception_type(status_code)
    
    error_response = {
        "statusCode": status_code,
        "errorCode": error_code_num,
        "title": title,
        "description": description,
        "exceptionType": exception_type,
        "timestamp": now().isoformat(),
        "endpoint": request.path if request else "",
        "method": request.method if request else ""
    }
    
    return Response(error_response, status=status_code)


def get_status_code_from_error_code(error_code: ErrorCode) -> int:
    """Determines HTTP status code based on ErrorCode"""
    code = error_code.code
    
    # Specific error codes that need custom status codes
    if code == 1002:  # USER_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 2001:  # BOOKING_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 2101:  # INTERVIEW_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 3001:  # SERVICE_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 3101:  # SCHEDULE_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 4003:  # PAYMENT_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 4501:  # DOCUMENT_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 5001:  # WITHDRAWAL_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 5006:  # STRIPE_ACCOUNT_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 6001:  # NOTIFICATION_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 7001:  # CHAT_ROOM_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 7002:  # MESSAGE_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    if code == 8001:  # DASHBOARD_NOT_FOUND
        return status.HTTP_404_NOT_FOUND
    
    # General ranges
    if 1000 <= code < 2000: return status.HTTP_401_UNAUTHORIZED
    if 2000 <= code < 3000: return status.HTTP_409_CONFLICT
    if 3000 <= code < 4000: return status.HTTP_404_NOT_FOUND
    if 4000 <= code < 9000: return status.HTTP_400_BAD_REQUEST
    if 9000 <= code < 10000: return status.HTTP_422_UNPROCESSABLE_ENTITY
    return status.HTTP_400_BAD_REQUEST


def get_error_code_by_status(status_code: int) -> ErrorCode:
    """Returns ErrorCode based on HTTP status code"""
    status_to_error_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.AUTHENTICATION_REQUIRED,
        402: ErrorCode.PAYMENT_FAILED,
        403: ErrorCode.PERMISSION_DENIED,
        404: ErrorCode.USER_NOT_FOUND,
        409: ErrorCode.BOOKING_CONFLICT,
        422: ErrorCode.VALIDATION_ERROR,
        500: ErrorCode.INTERNAL_SERVER_ERROR
    }
    return status_to_error_map.get(status_code, ErrorCode.INVALID_DATA)


def get_exception_type(status_code: int) -> str:
    """Returns exception type based on status code"""
    exception_type_map = {
        400: "BadRequestException",
        401: "UnauthorizedException", 
        402: "PaymentRequiredException",
        403: "ForbiddenException",
        404: "NotFoundException",
        409: "ConflictException",
        422: "ValidationException",
        500: "InternalServerException"
    }
    return exception_type_map.get(status_code, "APIException")


def handle_validation_error(validation_errors, request=None):
    """Processes validation errors in a unified format"""
    # If there is an error code in the format "1001: Title: Description"
    if isinstance(validation_errors, dict):
        for field, errors in validation_errors.items():
            if isinstance(errors, list):
                for error in errors:
                    if isinstance(error, str) and error.count(':') >= 2:
                        try:
                            parts = error.split(':', 2)
                            code_str = parts[0].strip()
                            title = parts[1].strip()
                            description = parts[2].strip()
                            code = int(code_str)
                            # Search for ErrorCode by number
                            for error_code in ErrorCode:
                                if error_code.code == code:
                                    return create_error_response(
                                        error_code=error_code,
                                        detail=description,
                                        request=request
                                    )
                        except (ValueError, AttributeError):
                            pass
    
    # Format Django validation errors into readable text
    if isinstance(validation_errors, dict):
        error_messages = []
        for field, errors in validation_errors.items():
            if isinstance(errors, list):
                for error in errors:
                    if hasattr(error, 'message'):
                        error_messages.append(f"{error.message}")
                    else:
                        error_messages.append(f"{str(error)}")
            else:
                error_messages.append(f"{str(errors)}")
        
        formatted_error = "; ".join(error_messages)
    else:
        formatted_error = str(validation_errors)
    
    # If there is no error code, return a general validation error
    return create_error_response(
        error_code=ErrorCode.VALIDATION_ERROR,
        detail=formatted_error,
        request=request
    )


def create_success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """Creates a standardized successful response"""
    response_data = {
        'success': True,
        "message": message
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status_code) 