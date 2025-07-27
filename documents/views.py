from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Document
from .serializers import DocumentSerializer

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, ValidationError, NotFoundError
)
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

# Create your views here.

class DocumentListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()
        return Document.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        if file and file.size > 10 * 1024 * 1024:
            raise ValidationError('Размер файла превышает 10MB')
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список всех документов пользователя",
        responses={
            200: openapi.Response('Список документов', DocumentSerializer(many=True)),
        },
        tags=['Документы']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Список документов получен успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='DOCUMENT_LIST_ERROR',
                error_message=f'Ошибка получения списка документов: {str(e)}',
                status_code=500
            )

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="Загрузить новый документ пользователя",
        request_body=DocumentSerializer,
        responses={
            201: openapi.Response('Документ загружен', DocumentSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
        },
        tags=['Документы']
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Документ загружен успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='DOCUMENT_CREATE_ERROR',
                error_message=f'Ошибка загрузки документа: {str(e)}',
                status_code=500
            )

class DocumentDeleteView(BaseAPIView, generics.DestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()
        return Document.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionError('Нет прав для удаления этого документа')
        instance.delete()

    @swagger_auto_schema(
        operation_description="Удалить документ пользователя по ID",
        responses={
            200: 'Документ удален',
            403: 'Нет прав',
            404: 'Документ не найден',
        },
        tags=['Документы']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            self.perform_destroy(instance)
            
            return self.success_response(
                message='Документ удален успешно'
            )
            
        except Document.DoesNotExist:
            return self.error_response(
                error_number='DOCUMENT_NOT_FOUND',
                error_message='Документ не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='DOCUMENT_DELETE_ERROR',
                error_message=f'Ошибка удаления документа: {str(e)}',
                status_code=500
            )
