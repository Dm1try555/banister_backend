from rest_framework import viewsets, permissions, filters
from .models import Service
from .serializers import ServiceSerializer
from authentication.models import User

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import PermissionError
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class IsProviderOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'provider'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.provider == request.user

class ServiceViewSet(BaseAPIView, viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsProviderOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    @transaction.atomic
    def perform_create(self, serializer):
        if self.request.user.role != 'provider':
            raise PermissionError('Только поставщики услуг могут создавать услуги')
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Создать новую услугу (только для провайдера)",
        request_body=ServiceSerializer,
        responses={
            201: openapi.Response('Услуга создана', ServiceSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав доступа',
        },
        tags=['Услуги']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Создание новой услуги
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Услуга создана успешно'
            )
            
        except PermissionError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_CREATE_ERROR',
                error_message=f'Ошибка создания услуги: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Обновить данные услуги (только для владельца)",
        request_body=ServiceSerializer,
        responses={
            200: openapi.Response('Услуга обновлена', ServiceSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            404: 'Услуга не найдена',
        },
        tags=['Услуги']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Обновление услуги
        """
        try:
            instance = self.get_object()
            
            # Проверка прав на обновление
            if instance.provider != self.request.user:
                raise PermissionError('Нет прав для обновления этой услуги')
            
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Услуга обновлена успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_UPDATE_ERROR',
                error_message=f'Ошибка обновления услуги: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Удалить услугу (только для владельца)",
        responses={
            200: 'Услуга удалена',
            403: 'Нет прав',
            404: 'Услуга не найдена',
        },
        tags=['Услуги']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Удаление услуги
        """
        try:
            instance = self.get_object()
            
            # Проверка прав на удаление
            if instance.provider != self.request.user:
                raise PermissionError('Нет прав для удаления этой услуги')
            
            instance.delete()
            
            return self.success_response(
                message='Услуга удалена успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_DELETE_ERROR',
                error_message=f'Ошибка удаления услуги: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Получить список всех услуг (поиск и фильтрация по параметрам)",
        responses={
            200: openapi.Response('Список услуг', ServiceSerializer(many=True)),
        },
        tags=['Услуги']
    )
    def list(self, request, *args, **kwargs):
        """
        Получение списка услуг
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Список услуг получен успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_LIST_ERROR',
                error_message=f'Ошибка получения списка услуг: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Получить подробную информацию об услуге по ID",
        responses={
            200: openapi.Response('Информация об услуге', ServiceSerializer),
            404: 'Услуга не найдена',
        },
        tags=['Услуги']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получение детальной информации об услуге
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация об услуге получена успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_RETRIEVE_ERROR',
                error_message=f'Ошибка получения информации об услуге: {str(e)}',
                status_code=500
            )