from rest_framework import generics
from rest_framework.permissions import AllowAny
from services.models import Service
from services.serializers import ServiceSerializer
from providers.models import Provider
from providers.serializers import ProviderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from error_handling.views import BaseAPIView

class PublicServiceListView(BaseAPIView, generics.ListAPIView):
    """Публичный список всех сервисов"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получить публичный список всех сервисов",
        responses={200: openapi.Response('Публичный список сервисов', ServiceSerializer(many=True))},
        tags=['Public Services']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Список сервисов получен')

class PublicProviderListView(BaseAPIView, generics.ListAPIView):
    """Публичный список всех провайдеров"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получить публичный список всех провайдеров",
        responses={200: openapi.Response('Публичный список провайдеров', ProviderSerializer(many=True))},
        tags=['Public Providers']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Список провайдеров получен')

class PublicProviderDetailView(BaseAPIView, generics.RetrieveAPIView):
    """Публичная детальная информация о провайдере"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получить публичную информацию о провайдере по ID",
        responses={200: openapi.Response('Информация о провайдере', ProviderSerializer)},
        tags=['Public Providers']
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.success_response(data=serializer.data, message='Информация о провайдере получена')