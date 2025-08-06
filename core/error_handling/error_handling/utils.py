from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .enums import ErrorCode


def create_error_response(error_code, custom_message=None):
    """
    Создание стандартизированного ответа с ошибкой
    """
    response_data = {
        'success': False,
        'error': {
            'error_number': error_code.error_number,
            'error_message': custom_message or error_code.error_message,
            'timestamp': timezone.now().isoformat()
        }
    }
    
    return Response(response_data, status=error_code.status_code)


def create_success_response(data=None, message="Операция выполнена успешно"):
    """
    Создание стандартизированного успешного ответа
    """
    response_data = {
        'success': True,
        'message': message,
        'timestamp': timezone.now().isoformat()
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status.HTTP_200_OK)


class ErrorResponseMixin:
    """
    Mixin для добавления методов создания ответов с ошибками к классам представлений
    """
    
    def error_response(self, error_code, custom_message=None):
        """
        Создание ответа с ошибкой
        """
        return create_error_response(error_code, custom_message)
    
    def success_response(self, data=None, message="Операция выполнена успешно"):
        """
        Создание успешного ответа
        """
        return create_success_response(data, message) 