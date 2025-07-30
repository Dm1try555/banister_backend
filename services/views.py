from rest_framework import viewsets, permissions, filters
from .models import Service
from .serializers import ServiceSerializer
from authentication.models import User

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import PermissionError
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class IsProviderOrReadOnly(permissions.BasePermission):
    """Permissions for providers or read-only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'provider'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.provider == request.user

class ServiceViewSet(BaseAPIView, viewsets.ModelViewSet):
    """ViewSet for service management"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsProviderOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    @transaction.atomic
    def perform_create(self, serializer):
        """Create service with provider binding"""
        if self.request.user.role != 'provider':
            raise PermissionError('Only service providers can create services')
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Create new service (providers only)",
        request_body=ServiceSerializer,
        responses={
            201: openapi.Response('Service created', ServiceSerializer),
            400: 'Validation error',
            403: 'No access rights',
        },
        tags=['Services']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create new service"""
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Service created successfully'
            )
            
        except PermissionError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_CREATE_ERROR',
                error_message=f'Error creating service: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Update service data (owner only)",
        request_body=ServiceSerializer,
        responses={
            200: openapi.Response('Service updated', ServiceSerializer),
            400: 'Validation error',
            403: 'No permissions',
            404: 'Service not found',
        },
        tags=['Services']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update service"""
        try:
            instance = self.get_object()
            
            # Check update permissions
            if instance.provider != self.request.user:
                raise PermissionError('No permissions to update this service')
            
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Service updated successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_UPDATE_ERROR',
                error_message=f'Error updating service: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Delete service (owner only)",
        responses={
            200: 'Service deleted',
            403: 'No permissions',
            404: 'Service not found',
        },
        tags=['Services']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete service"""
        try:
            instance = self.get_object()
            
            # Check delete permissions
            if instance.provider != self.request.user:
                raise PermissionError('No permissions to delete this service')
            
            instance.delete()
            
            return self.success_response(
                message='Service deleted successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_DELETE_ERROR',
                error_message=f'Error deleting service: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Get list of all services (search and filtering by parameters)",
        responses={
            200: openapi.Response('List of services', ServiceSerializer(many=True)),
        },
        tags=['Services']
    )
    def list(self, request, *args, **kwargs):
        """Get list of services"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='List of services obtained successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_LIST_ERROR',
                error_message=f'Error getting service list: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Get detailed information about a service by ID",
        responses={
            200: openapi.Response('Service information', ServiceSerializer),
            404: 'Service not found',
        },
        tags=['Services']
    )
    def retrieve(self, request, *args, **kwargs):
        """Get detailed service information"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Service information obtained successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_RETRIEVE_ERROR',
                error_message=f'Error getting service information: {str(e)}',
                status_code=500
            )