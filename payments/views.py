from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import PermissionError, ValidationError
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class PaymentInitiateView(BaseAPIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Инициализировать новый платеж (создать заявку на оплату)",
        request_body=PaymentSerializer,
        responses={
            201: openapi.Response('Платеж инициализирован', PaymentSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
        },
        tags=['Платежи']
    )
    @transaction.atomic
    def post(self, request):
        try:
            serializer = PaymentSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Проверка минимальной суммы платежа
            amount = serializer.validated_data.get('amount', 0)
            if amount <= 0:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Сумма платежа должна быть больше нуля',
                    status_code=400
                )
            
            payment = serializer.save(user=self.request.user)
            
            # Здесь должна быть логика инициализации платежа через платежную систему
            # payment.initialize_payment()
            
            return self.success_response(
                data=serializer.data,
                message='Платеж инициализирован успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_INIT_ERROR',
                error_message=f'Ошибка инициализации платежа: {str(e)}',
                status_code=500
            )

class PaymentStatusView(BaseAPIView, generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить статус платежа по ID (только для владельца)",
        responses={
            200: openapi.Response('Статус платежа', PaymentSerializer),
            403: 'Нет прав',
            404: 'Платеж не найден',
        },
        tags=['Платежи']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Проверка прав доступа
            if instance.user != self.request.user:
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Нет прав для просмотра этого платежа',
                    status_code=403
                )
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Статус платежа получен успешно'
            )
            
        except Payment.DoesNotExist:
            return self.error_response(
                error_number='PAYMENT_NOT_FOUND',
                error_message='Платеж не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_STATUS_ERROR',
                error_message=f'Ошибка получения статуса платежа: {str(e)}',
                status_code=500
            )

class PaymentHistoryView(BaseAPIView, generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получить историю всех платежей пользователя",
        responses={
            200: openapi.Response('История платежей', PaymentSerializer(many=True)),
        },
        tags=['Платежи']
    )
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='История платежей получена успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_HISTORY_ERROR',
                error_message=f'Ошибка получения истории платежей: {str(e)}',
                status_code=500
            )

class PaymentListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить историю всех платежей пользователя",
        responses={
            200: openapi.Response('История платежей', PaymentSerializer(many=True)),
        },
        tags=['Платежи']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = Payment.objects.filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message='История платежей получена успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_HISTORY_ERROR',
                error_message=f'Ошибка получения истории платежей: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Инициализировать новый платеж (создать заявку на оплату)",
        request_body=PaymentSerializer,
        responses={
            201: openapi.Response('Платеж инициализирован', PaymentSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
        },
        tags=['Платежи']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            amount = serializer.validated_data.get('amount', 0)
            if amount <= 0:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Сумма платежа должна быть больше нуля',
                    status_code=400
                )
            payment = serializer.save(user=self.request.user)
            # Здесь может быть логика инициализации платежа через платежную систему
            return self.success_response(
                data=serializer.data,
                message='Платеж инициализирован успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_INIT_ERROR',
                error_message=f'Ошибка инициализации платежа: {str(e)}',
                status_code=500
            )