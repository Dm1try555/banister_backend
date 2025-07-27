from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import ErrorResponseMixin, create_error_response, create_success_response
from .exceptions import BaseCustomException
import logging
from rest_framework.exceptions import MethodNotAllowed

logger = logging.getLogger(__name__)


class BaseAPIView(APIView, ErrorResponseMixin):
    """
    Базовый класс для всех API view с встроенной обработкой ошибок
    """
    
    def handle_exception(self, exc):
        """
        Переопределение обработки исключений для стандартизации ответов
        """
        if isinstance(exc, BaseCustomException):
            return create_error_response(
                error_number=exc.error_number,
                error_message=str(exc.detail) if exc.detail else exc.default_detail,
                status_code=exc.status_code
            )
        
        # Логирование неожиданных ошибок
        logger.error(f"Unexpected error in {self.__class__.__name__}: {str(exc)}", exc_info=True)
        
        return create_error_response(
            error_number='UNKNOWN_ERROR',
            error_message='Произошла неизвестная ошибка',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Финальная обработка ответа для добавления стандартных полей
        """
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # Добавляем timestamp к успешным ответам, если его нет
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
    """
    Тестовый view для проверки работы системы обработки ошибок
    """
    
    def get(self, request):
        """
        Тест успешного ответа
        """
        return self.success_response(
            data={'message': 'Тест успешного ответа'},
            message='Тест прошел успешно'
        )
    
    def post(self, request):
        """
        Тест различных типов ошибок
        """
        error_type = request.data.get('error_type', 'validation')
        
        if error_type == 'validation':
            from .exceptions import ValidationError
            raise ValidationError('Тестовая ошибка валидации')
        elif error_type == 'authentication':
            from .exceptions import AuthenticationError
            raise AuthenticationError('Тестовая ошибка аутентификации')
        elif error_type == 'not_found':
            from .exceptions import NotFoundError
            raise NotFoundError('Тестовая ошибка - ресурс не найден')
        elif error_type == 'server':
            from .exceptions import ServerError
            raise ServerError('Тестовая ошибка сервера')
        else:
            return self.success_response(
                data={'message': 'Тест без ошибок'},
                message='Тест прошел успешно'
            ) 