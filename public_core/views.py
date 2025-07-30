from rest_framework import generics
from rest_framework.permissions import AllowAny
from services.models import Service
from services.serializers import ServiceSerializer
from providers.models import Provider
from providers.serializers import ProviderSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    NotFoundError, ValidationError
)

class PublicServiceListView(BaseAPIView, generics.ListAPIView):
    """Public list of all services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get public list of all services",
        responses={
            200: openapi.Response('Public service list', ServiceSerializer(many=True)),
        },
        tags=['Public data']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Public service list retrieved successfully'
        )

class PublicProviderListView(BaseAPIView, generics.ListAPIView):
    """Public list of all providers"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get public list of all providers",
        responses={
            200: openapi.Response('Public provider list', ProviderSerializer(many=True)),
        },
        tags=['Public data']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Public provider list retrieved successfully'
        )

class PublicProviderDetailView(BaseAPIView, generics.RetrieveAPIView):
    """Public detailed provider information"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get public provider information by ID",
        responses={
            200: openapi.Response('Provider information', ProviderSerializer),
            404: 'Provider not found',
        },
        tags=['Public data']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Provider information retrieved successfully'
            )
            
        except Provider.DoesNotExist:
            return self.error_response(
                error_number='PROVIDER_NOT_FOUND',
                error_message='Provider not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PUBLIC_PROVIDER_RETRIEVE_ERROR',
                error_message=f'Error retrieving provider information: {str(e)}',
                status_code=500
            )