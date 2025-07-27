from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Withdrawal
from .serializers import WithdrawalSerializer

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, ValidationError, WithdrawalError
)
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class WithdrawalCreateView(BaseAPIView, generics.CreateAPIView):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Создать заявку на вывод средств (только для провайдера)",
        request_body=WithdrawalSerializer,
        responses={
            201: openapi.Response('Заявка создана', WithdrawalSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
        },
        tags=['Вывод средств']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            # Проверка роли пользователя
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Только поставщики услуг могут создавать заявки на вывод средств',
                    status_code=403
                )
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Проверка минимальной суммы вывода
            amount = serializer.validated_data.get('amount', 0)
            if amount <= 0:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Сумма вывода должна быть больше нуля',
                    status_code=400
                )
            
            # Проверка баланса пользователя (здесь должна быть логика проверки баланса)
            # if self.request.user.balance < amount:
            #     return self.error_response(
            #         error_number='INSUFFICIENT_BALANCE',
            #         error_message='Недостаточно средств для вывода',
            #         status_code=400
            #     )
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Заявка на вывод средств создана успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_CREATE_ERROR',
                error_message=f'Ошибка создания заявки на вывод: {str(e)}',
                status_code=500
            )

class WithdrawalHistoryView(BaseAPIView, generics.ListAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Для генерации схемы swagger или если нет user.role — возвращаем пустой queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Withdrawal.objects.none()
        return Withdrawal.objects.filter(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить историю всех заявок на вывод средств (только для провайдера)",
        responses={
            200: openapi.Response('История выводов', WithdrawalSerializer(many=True)),
            403: 'Нет прав',
        },
        tags=['Вывод средств']
    )
    def list(self, request, *args, **kwargs):
        try:
            # Проверка роли пользователя
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Только поставщики услуг могут просматривать историю выводов',
                    status_code=403
                )
            
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='История выводов получена успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_HISTORY_ERROR',
                error_message=f'Ошибка получения истории выводов: {str(e)}',
                status_code=500
            )

class WithdrawalListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Withdrawal.objects.none()
        return Withdrawal.objects.filter(provider=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        if self.request.user.role != 'provider':
            raise PermissionError('Только поставщики услуг могут создавать заявки на вывод средств')
        amount = serializer.validated_data.get('amount', 0)
        if amount <= 0:
            raise ValidationError('Сумма вывода должна быть больше нуля')
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить историю всех заявок на вывод средств (только для провайдера)",
        responses={
            200: openapi.Response('История выводов', WithdrawalSerializer(many=True)),
            403: 'Нет прав',
        },
        tags=['Вывод средств']
    )
    def list(self, request, *args, **kwargs):
        try:
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Только поставщики услуг могут просматривать историю выводов',
                    status_code=403
                )
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message='История выводов получена успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_HISTORY_ERROR',
                error_message=f'Ошибка получения истории выводов: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Создать заявку на вывод средств (только для провайдера)",
        request_body=WithdrawalSerializer,
        responses={
            201: openapi.Response('Заявка создана', WithdrawalSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
        },
        tags=['Вывод средств']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Только поставщики услуг могут создавать заявки на вывод средств',
                    status_code=403
                )
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            amount = serializer.validated_data.get('amount', 0)
            if amount <= 0:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Сумма вывода должна быть больше нуля',
                    status_code=400
                )
            serializer.save(provider=self.request.user)
            return self.success_response(
                data=serializer.data,
                message='Заявка на вывод средств создана успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_CREATE_ERROR',
                error_message=f'Ошибка создания заявки на вывод: {str(e)}',
                status_code=500
            )