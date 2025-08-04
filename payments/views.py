from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import (
    PaymentSerializer, StripePaymentIntentSerializer, StripePaymentConfirmSerializer,
    StripeCustomerSerializer, StripePaymentMethodSerializer, PaymentStatusSerializer,
    PaymentRefundSerializer
)
from .stripe_service import stripe_service
from bookings.models import Booking

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class StripeCreatePaymentIntentView(BaseAPIView):
    """Создание Payment Intent в Stripe"""
    permission_classes = [IsAuthenticated]
    
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
        tags=['Stripe Payments']
    )
    def post(self, request):
        """Создать Payment Intent"""
        try:
            serializer = StripePaymentIntentSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
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
                    'amount': result['amount'],
                    'currency': result['currency'],
                    'payment_id': payment.id
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
        tags=['Stripe Payments']
    )
    @transaction.atomic
    def post(self, request):
        """Подтвердить платеж"""
        try:
            serializer = StripePaymentConfirmSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            payment_intent_id = serializer.validated_data['payment_intent_id']
            booking_id = serializer.validated_data.get('booking_id')
            
            # Получение бронирования если указано
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
            
            # Обработка платежа в Stripe
            success, result = stripe_service.process_payment(
                payment_intent_id=payment_intent_id,
                user=request.user,
                booking=booking
            )
            
            if not success:
                return self.error_response(
                    error_number='PAYMENT_CONFIRMATION_ERROR',
                    error_message=result,
                    status_code=400
                )
            
            # Получение обновленной записи платежа
            payment = Payment.objects.get(id=result['payment_id'])
            payment_serializer = PaymentSerializer(payment)
            
            return self.success_response(
                data=payment_serializer.data,
                message='Платеж успешно подтвержден'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_CONFIRMATION_ERROR',
                error_message=f'Ошибка подтверждения платежа: {str(e)}',
                status_code=500
            )

class StripeCreateCustomerView(BaseAPIView):
    """Создание клиента в Stripe"""
    permission_classes = [IsAuthenticated]
    
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
        tags=['Stripe Customers']
    )
    def post(self, request):
        """Создать клиента"""
        try:
            serializer = StripeCustomerSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            email = serializer.validated_data['email']
            name = serializer.validated_data.get('name', '')
            
            # Создание клиента в Stripe
            success, result = stripe_service.create_customer(
                email=email,
                name=name
            )
            
            if not success:
                return self.error_response(
                    error_number='CUSTOMER_CREATION_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            return self.success_response(
                data=result,
                message='Клиент создан успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='CUSTOMER_CREATION_ERROR',
                error_message=f'Ошибка создания клиента: {str(e)}',
                status_code=500
            )

class StripeAttachPaymentMethodView(BaseAPIView):
    """Привязка метода оплаты к клиенту"""
    permission_classes = [IsAuthenticated]
    
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
        tags=['Stripe Payment Methods']
    )
    def post(self, request):
        """Привязать метод оплаты"""
        try:
            serializer = StripePaymentMethodSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            payment_method_id = serializer.validated_data['payment_method_id']
            customer_id = serializer.validated_data['customer_id']
            
            # Привязка метода оплаты в Stripe
            success, result = stripe_service.create_payment_method(
                payment_method_id=payment_method_id,
                customer_id=customer_id
            )
            
            if not success:
                return self.error_response(
                    error_number='PAYMENT_METHOD_ATTACH_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            return self.success_response(
                data=result,
                message='Метод оплаты привязан успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_METHOD_ATTACH_ERROR',
                error_message=f'Ошибка привязки метода оплаты: {str(e)}',
                status_code=500
            )

class StripePaymentStatusView(BaseAPIView):
    """Получение статуса платежа в Stripe"""
    permission_classes = [IsAuthenticated]
    
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
        tags=['Stripe Payments']
    )
    def post(self, request):
        """Получить статус платежа"""
        try:
            serializer = PaymentStatusSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            payment_intent_id = serializer.validated_data['payment_intent_id']
            
            # Получение статуса платежа в Stripe
            success, result = stripe_service.get_payment_status(payment_intent_id)
            
            if not success:
                return self.error_response(
                    error_number='PAYMENT_STATUS_ERROR',
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
        tags=['Stripe Refunds']
    )
    @transaction.atomic
    def post(self, request):
        """Создать возврат средств"""
        try:
            serializer = PaymentRefundSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            payment_intent_id = serializer.validated_data['payment_intent_id']
            amount = serializer.validated_data.get('amount')
            reason = serializer.validated_data.get('reason', '')
            
            # Создание возврата в Stripe
            success, result = stripe_service.refund_payment(
                payment_intent_id=payment_intent_id,
                amount=amount
            )
            
            if not success:
                return self.error_response(
                    error_number='REFUND_ERROR',
                    error_message=result,
                    status_code=500
                )
            
            # Обновление статуса платежа в базе данных
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
                payment.status = 'refunded'
                payment.metadata['refund_id'] = result['refund_id']
                payment.metadata['refund_reason'] = reason
                payment.save()
            except Payment.DoesNotExist:
                pass  # Платеж может не существовать в базе данных
            
            return self.success_response(
                data=result,
                message='Возврат средств создан успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='REFUND_ERROR',
                error_message=f'Ошибка создания возврата: {str(e)}',
                status_code=500
            )

# Обновленные существующие views
class PaymentListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """Список и создание платежей"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить историю платежей пользователя",
        responses={200: openapi.Response('История платежей', PaymentSerializer(many=True))},
        tags=['Payments']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='История платежей получена')

    @swagger_auto_schema(
        operation_description="Создать новый платеж (устаревший метод)",
        request_body=PaymentSerializer,
        responses={201: openapi.Response('Платеж создан', PaymentSerializer)},
        tags=['Payments']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
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
        return self.success_response(data=serializer.data, message='Платеж создан')

class PaymentStatusView(BaseAPIView, generics.RetrieveAPIView):
    """Статус платежа"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить статус платежа по ID (только владелец)",
        responses={200: openapi.Response('Статус платежа', PaymentSerializer)},
        tags=['Payments']
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.user != self.request.user:
            return self.error_response(
                error_number='PERMISSION_ERROR',
                error_message='Нет прав для просмотра этого платежа',
                status_code=403
            )
        
        serializer = self.get_serializer(instance)
        return self.success_response(data=serializer.data, message='Статус платежа получен')