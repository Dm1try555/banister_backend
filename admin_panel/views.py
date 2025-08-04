from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from authentication.models import User
from authentication.serializers import UserSerializer
from error_handling.views import BaseAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class AdminUserListView(BaseAPIView, generics.ListAPIView):
    """Список всех пользователей для админа"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить список всех пользователей (только админ)",
        responses={200: openapi.Response('Список пользователей', UserSerializer(many=True))},
        tags=['Admin']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Список пользователей получен')

class AdminUserDetailView(BaseAPIView, generics.RetrieveDestroyAPIView):
    """Детальная информация и удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Получить информацию о пользователе (только админ)",
        responses={200: openapi.Response('Информация о пользователе', UserSerializer)},
        tags=['Admin']
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(data=serializer.data, message='Информация о пользователе получена')

    @swagger_auto_schema(
        operation_description="Удалить пользователя (только админ)",
        responses={200: 'Пользователь удален'},
        tags=['Admin']
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return self.success_response(message='Пользователь удален')

class CustomerListView(BaseAPIView, generics.ListAPIView):
    """Список клиентов для админа"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Получить список клиентов (только админ)",
        responses={200: openapi.Response('Список клиентов', UserSerializer(many=True))},
        tags=['Admin']
    )
    def get_queryset(self):
        return User.objects.filter(role='customer')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Список клиентов получен')

class ProviderListView(BaseAPIView, generics.ListAPIView):
    """Список провайдеров для админа"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Получить список провайдеров (только админ)",
        responses={200: openapi.Response('Список провайдеров', UserSerializer(many=True))},
        tags=['Admin']
    )
    def get_queryset(self):
        return User.objects.filter(role='provider')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Список провайдеров получен')