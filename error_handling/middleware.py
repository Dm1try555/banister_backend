import json
import logging
from django.http import JsonResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .exceptions import BaseCustomException, InvalidTokenError, TokenExpiredError, TokenMissingError


logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """
    Middleware for error handling and forming standardized responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request info for debugging
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Handle exceptions and form a standardized response
        """
        error_response = self.format_error_response(exception)
        
        if isinstance(exception, BaseCustomException):
            status_code = exception.status_code
        elif isinstance(exception, (InvalidToken, TokenError)):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exception, NotAuthenticated):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exception, permissions.exceptions.PermissionDenied):
            status_code = status.HTTP_403_FORBIDDEN
        elif 'authentication credentials were not provided' in str(exception).lower():
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exception, DjangoValidationError):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exception, IntegrityError):
            status_code = status.HTTP_409_CONFLICT
        elif 'permission' in str(exception).lower():
            status_code = status.HTTP_403_FORBIDDEN
        elif 'rest_framework.exceptions.PermissionDenied' in str(type(exception)):
            status_code = status.HTTP_403_FORBIDDEN
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Log the error
        logger.error(f"Error occurred: {exception}", exc_info=True)
        
        return JsonResponse(error_response, status=status_code)

    def format_error_response(self, exception):
        """
        Format the error response in a standard way
        """
        if isinstance(exception, BaseCustomException):
            error_number = exception.error_number
            error_message = str(exception.detail) if exception.detail else exception.default_detail
        elif isinstance(exception, (InvalidToken, TokenError)):
            error_number = 'INVALID_TOKEN'
            error_message = 'Invalid or expired token'
        elif isinstance(exception, NotAuthenticated):
            error_number = 'AUTHENTICATION_REQUIRED'
            error_message = 'Authentication required'
        elif isinstance(exception, permissions.exceptions.PermissionDenied):
            error_number = 'PERMISSION_DENIED'
            error_message = 'This function is only available for providers'
        elif 'permission' in str(exception).lower():
            error_number = 'PERMISSION_DENIED'
            error_message = 'This function is only available for providers'
        elif 'rest_framework.exceptions.PermissionDenied' in str(type(exception)):
            error_number = 'PERMISSION_DENIED'
            error_message = 'This function is only available for providers'
        elif 'authentication credentials were not provided' in str(exception).lower():
            error_number = 'AUTHENTICATION_REQUIRED'
            error_message = 'Authentication token is required'
        elif isinstance(exception, DjangoValidationError):
            error_number = 'VALIDATION_ERROR'
            error_message = 'Data validation error'
        elif isinstance(exception, IntegrityError):
            error_number = 'DATABASE_ERROR'
            error_message = 'Database error'
        else:
            error_number = 'UNKNOWN_ERROR'
            error_message = 'An unknown error occurred'

        return {
            'success': False,
            'error': {
                'error_number': error_number,
                'error_message': error_message,
                'timestamp': self.get_timestamp()
            }
        }

    def get_timestamp(self):
        """
        Get current time in ISO format
        """
        from django.utils import timezone
        return timezone.now().isoformat()


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF
    """
    # Use DRF's default handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Format the response in a standard way
        if isinstance(exc, BaseCustomException):
            error_number = exc.error_number
            error_message = str(exc.detail) if exc.detail else exc.default_detail
        elif isinstance(exc, (InvalidToken, TokenError)):
            error_number = 'INVALID_TOKEN'
            error_message = 'Invalid or expired token'
        elif isinstance(exc, NotAuthenticated):
            error_number = 'AUTHENTICATION_REQUIRED'
            error_message = 'Authentication required'
        elif isinstance(exc, permissions.exceptions.PermissionDenied):
            error_number = 'PERMISSION_DENIED'
            error_message = 'This function is only available for providers'
        elif 'authentication credentials were not provided' in str(exc).lower():
            error_number = 'AUTHENTICATION_REQUIRED'
            error_message = 'Authentication token is required'
        else:
            error_number = 'API_ERROR'
            error_message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)

        formatted_response = {
            'success': False,
            'error': {
                'error_number': error_number,
                'error_message': error_message,
                'timestamp': get_timestamp()
            }
        }
        
        return Response(formatted_response, status=response.status_code)
    
    # Handle exceptions that DRF doesn't handle
    if isinstance(exc, permissions.exceptions.PermissionDenied) or 'permission' in str(exc).lower():
        formatted_response = {
            'success': False,
            'error': {
                'error_number': 'PERMISSION_DENIED',
                'error_message': 'This function is only available for providers',
                'timestamp': get_timestamp()
            }
        }
        return Response(formatted_response, status=status.HTTP_403_FORBIDDEN)
    
    return response


def get_timestamp():
    """
    Get current time in ISO format
    """
    from django.utils import timezone
    return timezone.now().isoformat() 