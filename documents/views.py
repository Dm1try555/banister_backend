from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Document
from .serializers import DocumentSerializer

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    CustomPermissionError, ValidationError, NotFoundError
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
            raise ValidationError('File size exceeds 10MB')
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Get list of all user documents",
        responses={
            200: openapi.Response('Document list', DocumentSerializer(many=True)),
        },
        tags=['Documents']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
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
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Document uploaded successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='DOCUMENT_CREATE_ERROR',
                error_message=f'Error uploading document: {str(e)}',
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
        # Delete the file from storage if needed
        instance.delete()

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
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            
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
