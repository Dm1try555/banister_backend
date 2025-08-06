from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Document
from .serializers import DocumentSerializer

# Import error handling system
from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class DocumentListView(BaseAPIView):
    """Список документов пользователя"""
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Get list of all user documents",
        responses={
            200: openapi.Response('Document list', DocumentSerializer(many=True)),
        },
        tags=['Documents']
    )
    def get(self, request):
        """Получить список документов"""
        try:
            if getattr(self, 'swagger_fake_view', False):
                return self.success_response(data=[], message='Document list retrieved successfully')
            
            documents = Document.objects.filter(user=request.user)
            serializer = DocumentSerializer(documents, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Document list retrieved successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='DOCUMENT_LIST_ERROR',
                error_message=f'Error retrieving document list: {str(e)}',
                status_code=500
            )

class DocumentCreateView(BaseAPIView):
    """Загрузка нового документа"""
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="Upload new user document",
        request_body=DocumentSerializer,
        responses={
            201: openapi.Response('Document uploaded', DocumentSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Documents']
    )
    def post(self, request):
        """Загрузить новый документ"""
        try:
            serializer = DocumentSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            file = request.FILES.get('file')
            if file and file.size > 10 * 1024 * 1024:
                return self.error_response(
                    error_number='FILE_TOO_LARGE',
                    error_message='File size exceeds 10MB',
                    status_code=400
                )
            
            document = serializer.save(user=request.user)
            
            return self.success_response(
                data=DocumentSerializer(document).data,
                message='Document uploaded successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='DOCUMENT_CREATE_ERROR',
                error_message=f'Error uploading document: {str(e)}',
                status_code=500
            )

class DocumentDeleteView(BaseAPIView):
    """Удаление документа"""
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['delete']  # Только DELETE
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()
        return Document.objects.filter(user=self.request.user)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="Delete user document by ID",
        responses={
            200: 'Document deleted',
            403: 'No permissions',
            404: 'Document not found',
        },
        tags=['Documents']
    )
    def delete(self, request, pk):
        """Удалить документ"""
        try:
            document = self.get_queryset().get(pk=pk)
            document.delete()
            
            return self.success_response(
                message='Document deleted successfully'
            )
            
        except Document.DoesNotExist:
            return self.error_response(
                error_number='DOCUMENT_NOT_FOUND',
                error_message='Document not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='DOCUMENT_DELETE_ERROR',
                error_message=f'Error deleting document: {str(e)}',
                status_code=500
            )
