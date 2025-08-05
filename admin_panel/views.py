from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from authentication.models import User
from authentication.serializers import UserSerializer
from error_handling.views import BaseAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class AdminUserListView(BaseAPIView):
    """Список всех пользователей для админа"""
    permission_classes = [IsAdminUser]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить список всех пользователей (только админ)",
        responses={200: openapi.Response('Список пользователей', UserSerializer(many=True))},
        tags=['Admin']
    )
    def get(self, request):
        """Получить список всех пользователей"""
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return self.success_response(
                data=serializer.data, 
                message='Список пользователей получен'
            )
        except Exception as e:
            return self.error_response(
                error_number='USER_LIST_ERROR',
                error_message=f'Ошибка получения списка пользователей: {str(e)}',
                status_code=500
            )

class AdminUserDetailView(BaseAPIView):
    """Детальная информация и удаление пользователя"""
    permission_classes = [IsAdminUser]
    http_method_names = ['get', 'delete']  # GET и DELETE
    
    @swagger_auto_schema(
        operation_description="Получить информацию о пользователе (только админ)",
        responses={200: openapi.Response('Информация о пользователе', UserSerializer)},
        tags=['Admin']
    )
    def get(self, request, pk):
        """Получить информацию о пользователе"""
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return self.success_response(
                data=serializer.data, 
                message='Информация о пользователе получена'
            )
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='Пользователь не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='USER_DETAIL_ERROR',
                error_message=f'Ошибка получения информации о пользователе: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Удалить пользователя (только админ)",
        responses={200: 'Пользователь удален'},
        tags=['Admin']
    )
    @transaction.atomic
    def delete(self, request, pk):
        """Удалить пользователя"""
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return self.success_response(message='Пользователь удален')
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='Пользователь не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='USER_DELETE_ERROR',
                error_message=f'Ошибка удаления пользователя: {str(e)}',
                status_code=500
            )

class CustomerListView(BaseAPIView):
    """Список клиентов для админа"""
    permission_classes = [IsAdminUser]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить список клиентов (только админ)",
        responses={200: openapi.Response('Список клиентов', UserSerializer(many=True))},
        tags=['Admin']
    )
    def get(self, request):
        """Получить список клиентов"""
        try:
            customers = User.objects.filter(role='customer')
            serializer = UserSerializer(customers, many=True)
            return self.success_response(
                data=serializer.data, 
                message='Список клиентов получен'
            )
        except Exception as e:
            return self.error_response(
                error_number='CUSTOMER_LIST_ERROR',
                error_message=f'Ошибка получения списка клиентов: {str(e)}',
                status_code=500
            )

class ProviderListView(BaseAPIView):
    """Список провайдеров для админа"""
    permission_classes = [IsAdminUser]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить список провайдеров (только админ)",
        responses={200: openapi.Response('Список провайдеров', UserSerializer(many=True))},
        tags=['Admin']
    )
    def get(self, request):
        """Получить список провайдеров"""
        try:
            providers = User.objects.filter(role='provider')
            serializer = UserSerializer(providers, many=True)
            return self.success_response(
                data=serializer.data, 
                message='Список провайдеров получен'
            )
        except Exception as e:
            return self.error_response(
                error_number='PROVIDER_LIST_ERROR',
                error_message=f'Ошибка получения списка провайдеров: {str(e)}',
                status_code=500
            )