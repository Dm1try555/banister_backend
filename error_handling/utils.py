from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .exceptions import BaseCustomException


def create_error_response(error_number, error_message, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Создание стандартизированного ответа с ошибкой
    
    Args:
        error_number (str): Код ошибки
        error_message (str): Сообщение об ошибке
        status_code (int): HTTP статус код
    
    Returns:
        Response: Стандартизированный ответ с ошибкой
    """
    response_data = {
        'success': False,
        'error': {
            'error_number': error_number,
            'error_message': error_message,
            'timestamp': timezone.now().isoformat()
        }
    }
    
    return Response(response_data, status=status_code)


def create_success_response(data=None, message="Операция выполнена успешно"):
    """
    Создание стандартизированного успешного ответа
    
    Args:
        data: Данные для ответа
        message (str): Сообщение об успехе
    
    Returns:
        Response: Стандартизированный успешный ответ
    """
    response_data = {
        'success': True,
        'message': message,
        'timestamp': timezone.now().isoformat()
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status.HTTP_200_OK)


def handle_exception(func):
    """
    Декоратор для обработки исключений в view методах
    
    Args:
        func: Функция для декорирования
    
    Returns:
        function: Обернутая функция с обработкой ошибок
    """
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
            # Логирование неожиданных ошибок
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            
            return create_error_response(
                error_number='UNKNOWN_ERROR',
                error_message='Произошла неизвестная ошибка',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return wrapper


class ErrorResponseMixin:
    """
    Миксин для добавления методов создания ответов с ошибками в view классы
    """
    
    def error_response(self, error_number, error_message, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Создание ответа с ошибкой
        """
        return create_error_response(error_number, error_message, status_code)
    
    def success_response(self, data=None, message="Операция выполнена успешно"):
        """
        Создание успешного ответа
        """
        return create_success_response(data, message)
    
    def validation_error_response(self, field_errors):
        """
        Создание ответа с ошибками валидации
        
        Args:
            field_errors (dict): Словарь с ошибками по полям
        
        Returns:
            Response: Ответ с ошибками валидации
        """
        response_data = {
            'success': False,
            'error': {
                'error_number': 'VALIDATION_ERROR',
                'error_message': 'Ошибка валидации данных',
                'field_errors': field_errors,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def format_validation_errors(serializer_errors):
    """
    Форматирование ошибок валидации сериализатора
    
    Args:
        serializer_errors: Ошибки из serializer.errors
    
    Returns:
        dict: Отформатированные ошибки
    """
    formatted_errors = {}
    
    for field, errors in serializer_errors.items():
        if isinstance(errors, list):
            formatted_errors[field] = errors[0] if errors else "Ошибка валидации"
        else:
            formatted_errors[field] = str(errors)
    
    return formatted_errors 