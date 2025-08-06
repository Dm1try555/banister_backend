import logging
from django.http import JsonResponse
from django.utils import timezone

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Обработка исключений - оставляем стандартную обработку Django
        """
        # Логирование ошибки
        logger.error(f"Error occurred: {exception}", exc_info=True)
        
        # Возвращаем None, чтобы Django обработал ошибку стандартным способом
        return None


def custom_exception_handler(exc, context):
    """
    Обработчик исключений для DRF
    """
    from rest_framework.views import exception_handler
    
    # Используем стандартный обработчик DRF без изменений
    return exception_handler(exc, context) 