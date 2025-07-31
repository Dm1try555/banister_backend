from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import ErrorResponseMixin, create_error_response, create_success_response
from .exceptions import BaseCustomException
import logging
from rest_framework.exceptions import MethodNotAllowed

logger = logging.getLogger(__name__)


class BaseAPIView(APIView, ErrorResponseMixin):
    """Base class for all API views with built-in error handling"""
    
    def handle_exception(self, exc):
        """Override exception handling for standardized responses"""
        if isinstance(exc, BaseCustomException):
            return create_error_response(
                error_number=exc.error_number,
                error_message=str(exc.detail) if exc.detail else exc.default_detail,
                status_code=exc.status_code
            )
        
        # Log unexpected errors
        logger.error(f"Unexpected error in {self.__class__.__name__}: {str(exc)}", exc_info=True)
        
        return create_error_response(
            error_number='UNKNOWN_ERROR',
            error_message='An unknown error occurred',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def finalize_response(self, request, response, *args, **kwargs):
        """Finalize response to add standard fields"""
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # Add timestamp to successful responses if not present
        if response.status_code < 400 and hasattr(response, 'data'):
            if isinstance(response.data, dict) and 'timestamp' not in response.data:
                from django.utils import timezone
                response.data['timestamp'] = timezone.now().isoformat()
        
        return response

    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    def delete(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def handle_registration_errors(self, exc):
        """Handle registration errors"""
        from rest_framework.exceptions import ValidationError as DRFValidationError
        from .exceptions import InvalidEmailError, EmailAlreadyExistsError, ValidationError, ServerError
        from django.db import IntegrityError

        if isinstance(exc, DRFValidationError) or hasattr(exc, 'detail'):
            errors = exc.detail if hasattr(exc, 'detail') else exc.args[0]
            if isinstance(errors, dict) and 'email' in errors:
                email_errors = errors['email']
                if isinstance(email_errors, list):
                    email_errors = email_errors
                else:
                    email_errors = [email_errors]

                for error in email_errors:
                    error_str = str(error).lower()
                    if 'valid email address' in error_str or 'invalid email' in error_str:
                        return self.error_response(
                            error_number='INVALID_EMAIL',
                            error_message='Invalid email format',
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                    if 'already exists' in error_str:
                        return self.error_response(
                            error_number='EMAIL_ALREADY_EXISTS',
                            error_message='User with this email already exists',
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                return self.validation_error_response(errors)
            return self.validation_error_response(errors)
        if isinstance(exc, IntegrityError):
            return self.error_response(
                error_number='EMAIL_ALREADY_EXISTS',
                error_message='User with this email already exists',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return self.error_response(
            error_number='REGISTRATION_ERROR',
            error_message='Registration failed',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
