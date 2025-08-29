"""
Оптимизированные базовые views для устранения дублирования кода
"""

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, CreateAPIView
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.base.swagger_mixin import SwaggerMixin
from core.base.permissions import RoleBasedQuerysetMixin
from core.error_handling.utils import create_error_response
from core.error_handling.enums import ErrorCode


class BaseAuthenticatedView(APIView):
    """Базовый класс для всех аутентифицированных views"""
    permission_classes = [IsAuthenticated]


class BaseAuthenticatedCreateView(CreateAPIView):
    """Базовый класс для создания с аутентификацией"""
    permission_classes = [IsAuthenticated]


class BaseAuthenticatedListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin):
    """Базовый класс для списка/создания с аутентификацией"""
    permission_classes = [IsAuthenticated]


class BaseAuthenticatedDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin):
    """Базовый класс для деталей/обновления/удаления с аутентификацией"""
    permission_classes = [IsAuthenticated]


class BaseAuthenticatedUpdateView(SwaggerMixin, RetrieveUpdateAPIView, RoleBasedQuerysetMixin):
    """Базовый класс для обновления с аутентификацией"""
    permission_classes = [IsAuthenticated]


class BaseAuthenticatedModelViewSet(SwaggerMixin, ModelViewSet, RoleBasedQuerysetMixin):
    """Базовый класс для ModelViewSet с аутентификацией"""
    permission_classes = [IsAuthenticated]


class TransactionalMixin:
    """Mixin для автоматического применения @transaction.atomic"""
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class OptimizedListCreateView(BaseAuthenticatedListCreateView, TransactionalMixin):
    """Оптимизированный ListCreateView с транзакциями"""
    pass


class OptimizedRetrieveUpdateDestroyView(BaseAuthenticatedDetailView, TransactionalMixin):
    """Оптимизированный RetrieveUpdateDestroyView с транзакциями"""
    pass


class OptimizedRetrieveUpdateView(BaseAuthenticatedUpdateView, TransactionalMixin):
    """Оптимизированный RetrieveUpdateView с транзакциями"""
    pass


class OptimizedCreateView(BaseAuthenticatedCreateView, TransactionalMixin):
    """Оптимизированный CreateView с транзакциями"""
    pass


class OptimizedModelViewSet(BaseAuthenticatedModelViewSet, TransactionalMixin):
    """Оптимизированный ModelViewSet с транзакциями"""
    pass


class BaseAPIView(BaseAuthenticatedView):
    """Базовый APIView с стандартными методами"""
    
    def get_error_response(self, error_code: ErrorCode, detail=None, status_code=None):
        """Стандартный метод для создания error response"""
        return create_error_response(
            error_code=error_code,
            detail=detail,
            status_code=status_code,
            request=self.request
        )
    
    def get_success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        """Стандартный метод для создания success response"""
        response_data = {"message": message}
        if data is not None:
            response_data.update(data)
        return Response(response_data, status=status_code)