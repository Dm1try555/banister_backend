from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Provider
from .serializers import ProviderSerializer
from error_handling.views import BaseAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProviderListView(BaseAPIView):
    """List of all providers"""
    permission_classes = [AllowAny]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Get list of all providers",
        responses={200: openapi.Response('List of providers', ProviderSerializer(many=True))},
        tags=['Providers']
    )
    def get(self, request):
        """Получить список провайдеров"""
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

class ProviderDetailView(BaseAPIView):
    """Detailed provider information"""
    permission_classes = [AllowAny]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Get detailed provider information by ID",
        responses={200: openapi.Response('Provider information', ProviderSerializer)},
        tags=['Providers']
    )
    def get(self, request, pk):
        """Получить детали провайдера"""
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