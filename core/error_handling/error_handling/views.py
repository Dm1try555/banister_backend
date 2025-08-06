from rest_framework.views import APIView
from rest_framework.exceptions import MethodNotAllowed
from .utils import ErrorResponseMixin


class BaseAPIView(APIView, ErrorResponseMixin):
    """
    Базовый класс для всех API представлений
    """
    
    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    def delete(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE') 