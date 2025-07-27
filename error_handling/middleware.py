import json
import logging
from django.http import JsonResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from .exceptions import BaseCustomException

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """
    Middleware для обработки ошибок и формирования стандартизированных ответов
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Обработка исключений и формирование стандартизированного ответа
        """
        error_response = self.format_error_response(exception)
        
        if isinstance(exception, BaseCustomException):
            status_code = exception.status_code
        elif isinstance(exception, DjangoValidationError):
            status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exception, IntegrityError):
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Логирование ошибки
        logger.error(f"Error occurred: {exception}", exc_info=True)
        
        return JsonResponse(error_response, status=status_code)

    def format_error_response(self, exception):
        """
        Форматирование ответа с ошибкой в стандартном виде
        """
        if isinstance(exception, BaseCustomException):
            error_number = exception.error_number
            error_message = str(exception.detail) if exception.detail else exception.default_detail
        elif isinstance(exception, DjangoValidationError):
            error_number = 'VALIDATION_ERROR'
            error_message = 'Ошибка валидации данных'
        elif isinstance(exception, IntegrityError):
            error_number = 'DATABASE_ERROR'
            error_message = 'Ошибка базы данных'
        else:
            error_number = 'UNKNOWN_ERROR'
            error_message = 'Произошла неизвестная ошибка'

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
        Получение текущего времени в ISO формате
        """
        from django.utils import timezone
        return timezone.now().isoformat()


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для DRF
    """
    # Сначала используем стандартный обработчик DRF
    response = exception_handler(exc, context)
    
    if response is not None:
        # Форматируем ответ в стандартном виде
        if isinstance(exc, BaseCustomException):
            error_number = exc.error_number
            error_message = str(exc.detail) if exc.detail else exc.default_detail
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
    
    return response


def get_timestamp():
    """
    Получение текущего времени в ISO формате
    """
    from django.utils import timezone
    return timezone.now().isoformat() 