from rest_framework import viewsets, permissions, filters
from .models import Service
from .serializers import ServiceSerializer
from authentication.models import User

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import CustomPermissionError
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
    permission_classes = []  # Убираем permission class
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    @swagger_auto_schema(
        operation_description="Create new service (providers only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'description', 'price'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Service title'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Service description'),
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Service price'),
            },
            example={
                'title': 'Web Development',
                'description': 'Professional web development services',
                'price': 100.00,
            }
        ),
        responses={
            201: openapi.Response('Service created', ServiceSerializer),
            400: 'Validation error',
            401: 'Authentication required',
            403: 'Only providers can create services',
            500: 'Server error'
        },
        tags=['Services']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create new service"""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            # Check if user is a provider
            if request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='This function is only available for providers',
                    status_code=403
                )
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Set the provider automatically from the authenticated user
            service = serializer.save(provider=request.user)
            
            return self.success_response(
                data=serializer.data,
                message='Service created successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_CREATE_ERROR',
                error_message=f'Error creating service: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Update service data (owner only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Service title'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Service description'),
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Service price'),
                
            },
            example={
                'title': 'Updated Web Development',
                'description': 'Updated web development services',
                'price': 150.00,
                
            }
        ),
        responses={
            200: openapi.Response('Service updated', ServiceSerializer),
            400: 'Validation error',
            403: 'No permissions to update this service',
            404: 'Service not found',
            500: 'Server error'
        },
        tags=['Services']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update service"""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            instance = self.get_object()
            
            # Check if user owns the service
            if instance.provider != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='You do not have permission to modify this service',
                    status_code=403
                )
            
            serializer = self.get_serializer(instance, data=request.data, partial=False)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Service updated successfully'
            )
            
        except Service.DoesNotExist:
            return self.error_response(
                error_number='SERVICE_NOT_FOUND',
                error_message='Service not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_UPDATE_ERROR',
                error_message=f'Error updating service: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Partially update service data (owner only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Service title'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Service description'),
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Service price'),
                
            },
            example={
                'title': 'Updated Web Development',
                'price': 150.00
            }
        ),
        responses={
            200: openapi.Response('Service updated', ServiceSerializer),
            400: 'Validation error',
            403: 'No permissions to update this service',
            404: 'Service not found',
            500: 'Server error'
        },
        tags=['Services']
    )
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """Partially update service"""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            instance = self.get_object()
            
            # Check if user owns the service
            if instance.provider != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='You do not have permission to modify this service',
                    status_code=403
                )
            
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Service updated successfully'
            )
            
        except Service.DoesNotExist:
            return self.error_response(
                error_number='SERVICE_NOT_FOUND',
                error_message='Service not found',
                status_code=404
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
            200: 'Service deleted successfully',
            403: 'No permissions to delete this service',
            404: 'Service not found',
            500: 'Server error'
        },
        tags=['Services']
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """Delete service"""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            instance = self.get_object()
            
            # Check if user owns the service
            if instance.provider != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='You do not have permission to delete this service',
                    status_code=403
                )
            
            instance.delete()
            
            return self.success_response(
                message='Service deleted successfully'
            )
            
        except Service.DoesNotExist:
            return self.error_response(
                error_number='SERVICE_NOT_FOUND',
                error_message='Service not found',
                status_code=404
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
            500: 'Server error'
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
            500: 'Server error'
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
            
        except Service.DoesNotExist:
            return self.error_response(
                error_number='SERVICE_NOT_FOUND',
                error_message='Service not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_RETRIEVE_ERROR',
                error_message=f'Error getting service information: {str(e)}',
                status_code=500
            )