from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import AdminIssue
from .serializers import AdminIssueSerializer
from authentication.models import User
from authentication.serializers import UserSerializer
from error_handling.views import BaseAPIView
from error_handling.exceptions import PermissionError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class AdminUserListView(BaseAPIView, generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить список всех пользователей (только для админа)",
        responses={
            200: openapi.Response('Список пользователей', UserSerializer(many=True)),
        },
        tags=['Пользователи']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Список пользователей получен успешно'
        )

class AdminUserDetailView(BaseAPIView, generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить подробную информацию о пользователе по ID (только для админа)",
        responses={
            200: openapi.Response('Информация о пользователе', UserSerializer),
            404: 'Пользователь не найден',
        },
        tags=['Пользователи']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация о пользователе получена успешно'
            )
            
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='Пользователь не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_USER_RETRIEVE_ERROR',
                error_message=f'Ошибка получения информации о пользователе: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Удалить пользователя по ID (только для админа)",
        responses={
            200: 'Пользователь удален',
            404: 'Пользователь не найден',
        },
        tags=['Пользователи']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            
            return self.success_response(
                message='Пользователь удален успешно'
            )
            
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='Пользователь не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_USER_DELETE_ERROR',
                error_message=f'Ошибка удаления пользователя: {str(e)}',
                status_code=500
            )

class AdminIssueListView(BaseAPIView, generics.ListAPIView):
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить список всех обращений (только для админа)",
        responses={
            200: openapi.Response('Список обращений', AdminIssueSerializer(many=True)),
        },
        tags=['Админка']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Список обращений получен успешно'
        )

class AdminIssueCreateView(BaseAPIView, generics.CreateAPIView):
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Создать новое обращение (только для админа)",
        request_body=AdminIssueSerializer,
        responses={
            201: openapi.Response('Обращение создано', AdminIssueSerializer),
            400: 'Ошибка валидации',
        },
        tags=['Админка']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Обращение создано успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_CREATE_ERROR',
                error_message=f'Ошибка создания обращения: {str(e)}',
                status_code=500
            )

class AdminIssueDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить подробную информацию об обращении по ID (только для админа)",
        responses={
            200: openapi.Response('Информация об обращении', AdminIssueSerializer),
            404: 'Обращение не найдено',
        },
        tags=['Админка']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация об обращении получена успешно'
            )
            
        except AdminIssue.DoesNotExist:
            return self.error_response(
                error_number='ISSUE_NOT_FOUND',
                error_message='Обращение не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_RETRIEVE_ERROR',
                error_message=f'Ошибка получения информации об обращении: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Обновить обращение по ID (только для админа)",
        request_body=AdminIssueSerializer,
        responses={
            200: openapi.Response('Обращение обновлено', AdminIssueSerializer),
            400: 'Ошибка валидации',
            404: 'Обращение не найдено',
        },
        tags=['Админка']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Обращение обновлено успешно'
            )
            
        except AdminIssue.DoesNotExist:
            return self.error_response(
                error_number='ISSUE_NOT_FOUND',
                error_message='Обращение не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_UPDATE_ERROR',
                error_message=f'Ошибка обновления обращения: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Удалить обращение по ID (только для админа)",
        responses={
            200: 'Обращение удалено',
            404: 'Обращение не найдено',
        },
        tags=['Админка']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            
            return self.success_response(
                message='Обращение удалено успешно'
            )
            
        except AdminIssue.DoesNotExist:
            return self.error_response(
                error_number='ISSUE_NOT_FOUND',
                error_message='Обращение не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_DELETE_ERROR',
                error_message=f'Ошибка удаления обращения: {str(e)}',
                status_code=500
            )

class AdminIssueListCreateView(BaseAPIView, generics.ListCreateAPIView):
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить список всех обращений (только для админа)",
        responses={
            200: openapi.Response('Список обращений', AdminIssueSerializer(many=True)),
        },
        tags=['Админка']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message='Список обращений получен успешно'
        )

    @swagger_auto_schema(
        operation_description="Создать новое обращение (только для админа)",
        request_body=AdminIssueSerializer,
        responses={
            201: openapi.Response('Обращение создано', AdminIssueSerializer),
            400: 'Ошибка валидации',
        },
        tags=['Админка']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            self.perform_create(serializer)
            return self.success_response(
                data=serializer.data,
                message='Обращение создано успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_CREATE_ERROR',
                error_message=f'Ошибка создания обращения: {str(e)}',
                status_code=500
            )

class CustomerListView(BaseAPIView, generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Получение списка клиентов (админ)",
        responses={
            200: openapi.Response('Список клиентов', UserSerializer(many=True)),
        },
        tags=['Админка']
    )
    def get_queryset(self):
        return User.objects.filter(role='customer')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Список клиентов получен успешно'
        )

class ProviderListView(BaseAPIView, generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Получение списка провайдеров (админ)",
        responses={
            200: openapi.Response('Список провайдеров', UserSerializer(many=True)),
        },
        tags=['Админка']
    )
    def get_queryset(self):
        return User.objects.filter(role='provider')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Список поставщиков услуг получен успешно'
        )