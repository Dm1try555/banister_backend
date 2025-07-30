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


class ErrorTestView(BaseAPIView):
    """Test view for checking error handling system"""
    
    def get(self, request):
        """Test successful response"""
        return self.success_response(
            data={'message': 'Test successful response'},
            message='Test passed successfully'
        )
    
    def post(self, request):
        """Test different types of errors"""
        error_type = request.data.get('error_type', 'validation')
        
        if error_type == 'validation':
            from .exceptions import ValidationError
            raise ValidationError('Test validation error')
        elif error_type == 'authentication':
            from .exceptions import AuthenticationError
            raise AuthenticationError('Test authentication error')
        elif error_type == 'not_found':
            from .exceptions import NotFoundError
            raise NotFoundError('Test not found error')
        elif error_type == 'server':
            from .exceptions import ServerError
            raise ServerError('Test server error')
        else:
            return self.success_response(
                data={'message': 'Test without errors'},
                message='Test passed successfully'
            ) 