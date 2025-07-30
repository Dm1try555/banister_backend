from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .exceptions import BaseCustomException


def create_error_response(error_number, error_message, status_code=status.HTTP_400_BAD_REQUEST):
    """Creating a standardized error response"""
    response_data = {
        'success': False,
        'error': {
            'error_number': error_number,
            'error_message': error_message,
            'timestamp': timezone.now().isoformat()
        }
    }
    
    return Response(response_data, status=status_code)


def create_success_response(data=None, message="Operation completed successfully"):
    """Creating a standardized successful response"""
    response_data = {
        'success': True,
        'message': message,
        'timestamp': timezone.now().isoformat()
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status.HTTP_200_OK)


def handle_exception(func):
    """Decorator for handling exceptions in view methods"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseCustomException as e:
            return create_error_response(
                error_number=e.error_number,
                error_message=str(e.detail) if e.detail else e.default_detail,
                status_code=e.status_code
            )
        except Exception as e:
            # Logging unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            
            return create_error_response(
                error_number='UNKNOWN_ERROR',
                error_message='An unknown error occurred',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return wrapper


class ErrorResponseMixin:
    """Mixin for adding methods for creating error responses to view classes"""
    
    def error_response(self, error_number, error_message, status_code=status.HTTP_400_BAD_REQUEST):
        """Creating an error response"""
        return create_error_response(error_number, error_message, status_code)
    
    def success_response(self, data=None, message="Operation completed successfully"):
        """Creating a successful response"""
        return create_success_response(data, message)
    
    def validation_error_response(self, field_errors):
        """Creating a response with validation errors"""
        response_data = {
            'success': False,
            'error': {
                'error_number': 'VALIDATION_ERROR',
                'error_message': 'Data validation error',
                'field_errors': field_errors,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def format_validation_errors(serializer_errors):
    """Formatting validation errors of the serializer"""
    formatted_errors = {}
    
    for field, errors in serializer_errors.items():
        if isinstance(errors, list):
            formatted_errors[field] = errors[0] if errors else "Validation error"
        else:
            formatted_errors[field] = str(errors)
    
    return formatted_errors 