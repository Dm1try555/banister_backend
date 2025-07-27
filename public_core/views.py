from rest_framework import generics
from rest_framework.permissions import AllowAny
from services.models import Service
from services.serializers import ServiceSerializer
from providers.models import Provider
from providers.serializers import ProviderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    NotFoundError, ValidationError
)

class PublicServiceListView(BaseAPIView, generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получить публичный список всех услуг",
        responses={
            200: openapi.Response('Список публичных услуг', ServiceSerializer(many=True)),
        },
        tags=['Публичные данные']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Список публичных услуг получен успешно'
        )

class PublicProviderListView(BaseAPIView, generics.ListAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получить публичный список всех провайдеров",
        responses={
            200: openapi.Response('Список публичных провайдеров', ProviderSerializer(many=True)),
        },
        tags=['Публичные данные']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Список публичных поставщиков услуг получен успешно'
        )

class PublicProviderDetailView(BaseAPIView, generics.RetrieveAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Получить публичную информацию о провайдере по ID",
        responses={
            200: openapi.Response('Информация о провайдере', ProviderSerializer),
            404: 'Провайдер не найден',
        },
        tags=['Публичные данные']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация о поставщике услуг получена успешно'
            )
            
        except Provider.DoesNotExist:
            return self.error_response(
                error_number='PROVIDER_NOT_FOUND',
                error_message='Поставщик услуг не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PUBLIC_PROVIDER_RETRIEVE_ERROR',
                error_message=f'Ошибка получения информации о поставщике услуг: {str(e)}',
                status_code=500
            )