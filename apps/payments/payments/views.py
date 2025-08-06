from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import (
    PaymentSerializer, StripePaymentIntentSerializer, StripePaymentConfirmSerializer,
    StripeCustomerSerializer, StripePaymentMethodSerializer, PaymentStatusSerializer,
    PaymentRefundSerializer
)
from .stripe_service import stripe_service
from apps.bookings.models import Booking

# Import error handling system
from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

# ============================================================================
# ОСНОВНЫЕ ОПЕРАЦИИ С ПЛАТЕЖАМИ
# ============================================================================

class PaymentListView(BaseAPIView):
    """Список платежей пользователя"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить историю платежей пользователя",
        responses={200: openapi.Response('История платежей', PaymentSerializer(many=True))},
        tags=['Payments']
    )
    def get(self, request):
        """Получить список платежей"""
        try:
            payments = Payment.objects.filter(user=request.user).order_by('-created_at')
            serializer = PaymentSerializer(payments, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='История платежей получена'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_LIST_ERROR',
                error_message=f'Ошибка получения списка платежей: {str(e)}',
                status_code=500
            )

class PaymentDetailView(BaseAPIView):
    """Детали платежа"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить детали платежа по ID (только владелец)",
        responses={200: openapi.Response('Детали платежа', PaymentSerializer)},
        tags=['Payments']
    )
    def get(self, request, pk):
        """Получить детали платежа"""
        try:
            payment = Payment.objects.get(id=pk, user=request.user)
            serializer = PaymentSerializer(payment)
            
            return self.success_response(
                data=serializer.data,
                message='Детали платежа получены'
            )
            
        except Payment.DoesNotExist:
            return self.error_response(
                error_number='PAYMENT_NOT_FOUND',
                error_message='Платеж не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_DETAIL_ERROR',
                error_message=f'Ошибка получения деталей платежа: {str(e)}',
                status_code=500
            )

# ============================================================================
# STRIPE ОПЕРАЦИИ - ПЛАТЕЖИ
# ============================================================================

class StripeCreatePaymentIntentView(BaseAPIView):
    """Создание Payment Intent в Stripe"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Создать Payment Intent для обработки платежа через Stripe",
        request_body=StripePaymentIntentSerializer,
        responses={
            200: openapi.Response('Payment Intent создан', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'client_secret': openapi.Schema(type=openapi.TYPE_STRING),
                    'payment_intent_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'currency': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            500: 'Ошибка сервера'
        },
        tags=['Payments']
    )
    @transaction.atomic
    def post(self, request):
        """Создать Payment Intent"""
        try:
            serializer = StripePaymentIntentSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            amount = serializer.validated_data['amount']
            currency = serializer.validated_data['currency']
            booking_id = serializer.validated_data.get('booking_id')
            description = serializer.validated_data.get('description', '')
            
            # Проверка существования бронирования
            booking = None
            if booking_id:
                try:
                    booking = Booking.objects.get(id=booking_id, customer=request.user)
                except Booking.DoesNotExist:
                    return self.error_response(
                        error_number='BOOKING_NOT_FOUND',
                        error_message='Бронирование не найдено',
                        status_code=404
                    )
            
            # Создание Payment Intent в Stripe
            success, result = stripe_service.create_payment_intent(
                amount=amount,
                currency=currency,
                customer_email=request.user.email
            )
            
            if not success:
                return self.error_response(
                    error_number='STRIPE_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            # Создание записи платежа в базе данных
            payment_data = {
                'user': request.user,
                'amount': amount,
                'currency': currency,
                'status': 'pending',
                'payment_method': 'stripe',
                'stripe_payment_intent_id': result['payment_intent_id'],
                'transaction_id': result['payment_intent_id'],
                'description': description,
            }
            
            if booking:
                payment_data['booking'] = booking
            
            payment = Payment.objects.create(**payment_data)
            
            return self.success_response(
                data={
                    'client_secret': result['client_secret'],
                    'payment_intent_id': result['payment_intent_id'],
                    'amount': amount,
                    'currency': currency
                },
                message='Payment Intent создан успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_INTENT_ERROR',
                error_message=f'Ошибка создания Payment Intent: {str(e)}',
                status_code=500
            )

class StripeConfirmPaymentView(BaseAPIView):
    """Подтверждение платежа в Stripe"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Подтвердить платеж в Stripe",
        request_body=StripePaymentConfirmSerializer,
        responses={
            200: openapi.Response('Платеж подтвержден', PaymentSerializer),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            404: 'Платеж не найден',
            500: 'Ошибка сервера'
        },
        tags=['Payments']
    )
    @transaction.atomic
    def post(self, request):
        """Подтвердить платеж"""
        try:
            serializer = StripePaymentConfirmSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            payment_intent_id = serializer.validated_data['payment_intent_id']
            
            # Поиск платежа в базе данных
            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent_id,
                    user=request.user
                )
            except Payment.DoesNotExist:
                return self.error_response(
                    error_number='PAYMENT_NOT_FOUND',
                    error_message='Платеж не найден',
                    status_code=404
                )
            
            # Подтверждение платежа в Stripe
            success, result = stripe_service.confirm_payment(payment_intent_id)
            
            if not success:
                return self.error_response(
                    error_number='STRIPE_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            # Обновление статуса платежа
            payment.status = 'completed'
            payment.save()
            
            return self.success_response(
                data=PaymentSerializer(payment).data,
                message='Платеж подтвержден успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_CONFIRM_ERROR',
                error_message=f'Ошибка подтверждения платежа: {str(e)}',
                status_code=500
            )

class StripePaymentStatusView(BaseAPIView):
    """Получение статуса платежа в Stripe"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Получить статус платежа в Stripe",
        request_body=PaymentStatusSerializer,
        responses={
            200: openapi.Response('Статус платежа', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'currency': openapi.Schema(type=openapi.TYPE_STRING),
                    'created': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer_email': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            500: 'Ошибка сервера'
        },
        tags=['Payments']
    )
    @transaction.atomic
    def post(self, request):
        """Получить статус платежа"""
        try:
            serializer = PaymentStatusSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            payment_intent_id = serializer.validated_data['payment_intent_id']
            
            # Получение статуса платежа в Stripe
            success, result = stripe_service.get_payment_status(payment_intent_id)
            
            if not success:
                return self.error_response(
                    error_number='STRIPE_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            return self.success_response(
                data=result,
                message='Статус платежа получен'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_STATUS_ERROR',
                error_message=f'Ошибка получения статуса платежа: {str(e)}',
                status_code=500
            )

class StripeRefundPaymentView(BaseAPIView):
    """Возврат средств через Stripe"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Возврат средств через Stripe",
        request_body=PaymentRefundSerializer,
        responses={
            200: openapi.Response('Возврат создан', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refund_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            500: 'Ошибка сервера'
        },
        tags=['Payments']
    )
    @transaction.atomic
    def post(self, request):
        """Создать возврат средств"""
        try:
            serializer = PaymentRefundSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            payment_intent_id = serializer.validated_data['payment_intent_id']
            amount = serializer.validated_data.get('amount')
            reason = serializer.validated_data.get('reason', '')
            
            # Создание возврата в Stripe
            success, result = stripe_service.create_refund(payment_intent_id, amount, reason)
            
            if not success:
                return self.error_response(
                    error_number='STRIPE_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            return self.success_response(
                data={
                    'refund_id': result['refund_id'],
                    'amount': result['amount'],
                    'status': result['status']
                },
                message='Возврат средств создан успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='REFUND_ERROR',
                error_message=f'Ошибка создания возврата: {str(e)}',
                status_code=500
            )

# ============================================================================
# STRIPE ОПЕРАЦИИ - КЛИЕНТЫ И МЕТОДЫ ОПЛАТЫ
# ============================================================================

class StripeCreateCustomerView(BaseAPIView):
    """Создание клиента в Stripe"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Создать клиента в Stripe",
        request_body=StripeCustomerSerializer,
        responses={
            200: openapi.Response('Клиент создан', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'customer_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                    'name': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            500: 'Ошибка сервера'
        },
        tags=['Payments']
    )
    @transaction.atomic
    def post(self, request):
        """Создать клиента в Stripe"""
        try:
            serializer = StripeCustomerSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            name = serializer.validated_data.get('name', '')
            
            # Создание клиента в Stripe
            success, result = stripe_service.create_customer(email, name)
            
            if not success:
                return self.error_response(
                    error_number='STRIPE_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            return self.success_response(
                data={
                    'customer_id': result['customer_id'],
                    'email': email,
                    'name': name
                },
                message='Клиент создан успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='CUSTOMER_CREATE_ERROR',
                error_message=f'Ошибка создания клиента: {str(e)}',
                status_code=500
            )

class StripeAttachPaymentMethodView(BaseAPIView):
    """Привязка метода оплаты к клиенту"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Привязать метод оплаты к клиенту в Stripe",
        request_body=StripePaymentMethodSerializer,
        responses={
            200: openapi.Response('Метод оплаты привязан', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'payment_method_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'type': openapi.Schema(type=openapi.TYPE_STRING),
                    'card_last4': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            500: 'Ошибка сервера'
        },
        tags=['Payments']
    )
    @transaction.atomic
    def post(self, request):
        """Привязать метод оплаты"""
        try:
            serializer = StripePaymentMethodSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            customer_id = serializer.validated_data['customer_id']
            payment_method_id = serializer.validated_data['payment_method_id']
            
            # Привязка метода оплаты в Stripe
            success, result = stripe_service.attach_payment_method(customer_id, payment_method_id)
            
            if not success:
                return self.error_response(
                    error_number='STRIPE_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            return self.success_response(
                data={
                    'payment_method_id': payment_method_id,
                    'type': result.get('type', 'card'),
                    'card_last4': result.get('card', {}).get('last4', '')
                },
                message='Метод оплаты привязан успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_METHOD_ERROR',
                error_message=f'Ошибка привязки метода оплаты: {str(e)}',
                status_code=500
            )