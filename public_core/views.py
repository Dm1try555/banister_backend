from rest_framework import generics
from rest_framework.permissions import AllowAny
from services.models import Service
from services.serializers import ServiceSerializer
from providers.models import Provider
from providers.serializers import ProviderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from error_handling.views import BaseAPIView

class PublicServiceListView(BaseAPIView):
    """Публичный список всех сервисов"""
    permission_classes = [AllowAny]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить публичный список всех сервисов",
        responses={200: openapi.Response('Публичный список сервисов', ServiceSerializer(many=True))},
        tags=['Public Services']
    )
    def get(self, request):
        """Получить публичный список сервисов"""
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

class PublicProviderListView(BaseAPIView):
    """Публичный список всех провайдеров"""
    permission_classes = [AllowAny]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить публичный список всех провайдеров",
        responses={200: openapi.Response('Публичный список провайдеров', ProviderSerializer(many=True))},
        tags=['Public Providers']
    )
    def get(self, request):
        """Получить публичный список провайдеров"""
        try:
            providers = Provider.objects.all()
            serializer = ProviderSerializer(providers, many=True)
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

class PublicProviderDetailView(BaseAPIView):
    """Публичная детальная информация о провайдере"""
    permission_classes = [AllowAny]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить публичную информацию о провайдере по ID",
        responses={200: openapi.Response('Информация о провайдере', ProviderSerializer)},
        tags=['Public Providers']
    )
    def get(self, request, pk):
        """Получить публичную информацию о провайдере"""
        try:
            provider = Provider.objects.get(pk=pk)
            serializer = ProviderSerializer(provider)
            return self.success_response(
                data=serializer.data, 
                message='Информация о провайдере получена'
            )
        except Provider.DoesNotExist:
            return self.error_response(
                error_number='PROVIDER_NOT_FOUND',
                error_message='Провайдер не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PROVIDER_DETAIL_ERROR',
                error_message=f'Ошибка получения информации о провайдере: {str(e)}',
                status_code=500
            )