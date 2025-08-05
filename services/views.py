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

class ServiceListView(BaseAPIView):
    """Список всех сервисов"""
    permission_classes = []
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Get list of all services (search and filtering by parameters)",
        responses={
            200: openapi.Response('List of services', ServiceSerializer(many=True)),
            500: 'Server error'
        },
        tags=['Services']
    )
    def get(self, request):
        """Получить список сервисов"""
        try:
            services = Service.objects.all()
            serializer = ServiceSerializer(services, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Список сервисов получен'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_LIST_ERROR',
                error_message=f'Ошибка получения списка сервисов: {str(e)}',
                status_code=500
            )

class ServiceDetailView(BaseAPIView):
    """Детали сервиса"""
    permission_classes = []
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Get detailed information about a service by ID",
        responses={
            200: openapi.Response('Service information', ServiceSerializer),
            404: 'Service not found',
            500: 'Server error'
        },
        tags=['Services']
    )
    def get(self, request, pk):
        """Получить детали сервиса"""
        try:
            service = Service.objects.get(pk=pk)
            serializer = ServiceSerializer(service)
            
            return self.success_response(
                data=serializer.data,
                message='Информация о сервисе получена'
            )
            
        except Service.DoesNotExist:
            return self.error_response(
                error_number='SERVICE_NOT_FOUND',
                error_message='Сервис не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_DETAIL_ERROR',
                error_message=f'Ошибка получения информации о сервисе: {str(e)}',
                status_code=500
            )

class ServiceCreateView(BaseAPIView):
    """Создание нового сервиса"""
    permission_classes = []
    http_method_names = ['post']  # Только POST
    
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
    def post(self, request):
        """Создать новый сервис"""
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
            
            serializer = ServiceSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Set the provider automatically from the authenticated user
            service = serializer.save(provider=request.user)
            
            return self.success_response(
                data=ServiceSerializer(service).data,
                message='Service created successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_CREATE_ERROR',
                error_message=f'Error creating service: {str(e)}',
                status_code=500
            )

class ServiceUpdateView(BaseAPIView):
    """Обновление сервиса"""
    permission_classes = []
    http_method_names = ['put']  # Только PUT
    
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
    def put(self, request, pk):
        """Обновить сервис"""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            try:
                service = Service.objects.get(pk=pk)
            except Service.DoesNotExist:
                return self.error_response(
                    error_number='SERVICE_NOT_FOUND',
                    error_message='Service not found',
                    status_code=404
                )
            
            # Check if user is the owner of the service
            if service.provider != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='No permissions to update this service',
                    status_code=403
                )
            
            serializer = ServiceSerializer(service, data=request.data, partial=False)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            updated_service = serializer.save()
            
            return self.success_response(
                data=ServiceSerializer(updated_service).data,
                message='Service updated successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_UPDATE_ERROR',
                error_message=f'Error updating service: {str(e)}',
                status_code=500
            )

class ServiceDeleteView(BaseAPIView):
    """Удаление сервиса"""
    permission_classes = []
    http_method_names = ['delete']  # Только DELETE
    
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
    def delete(self, request, pk):
        """Удалить сервис"""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            try:
                service = Service.objects.get(pk=pk)
            except Service.DoesNotExist:
                return self.error_response(
                    error_number='SERVICE_NOT_FOUND',
                    error_message='Service not found',
                    status_code=404
                )
            
            # Check if user is the owner of the service
            if service.provider != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='No permissions to delete this service',
                    status_code=403
                )
            
            service.delete()
            
            return self.success_response(
                message='Service deleted successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SERVICE_DELETE_ERROR',
                error_message=f'Error deleting service: {str(e)}',
                status_code=500
            )