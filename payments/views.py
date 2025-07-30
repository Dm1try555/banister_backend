from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import PermissionError, ValidationError
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class PaymentInitiateView(BaseAPIView):
    """Initialize new payment"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Initialize new payment (create payment request)",
        request_body=PaymentSerializer,
        responses={
            201: openapi.Response('Payment initialized', PaymentSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Payments']
    )
    @transaction.atomic
    def post(self, request):
        try:
            serializer = PaymentSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Check minimum payment amount
            amount = serializer.validated_data.get('amount', 0)
            if amount <= 0:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Payment amount must be greater than zero',
                    status_code=400
                )
            
            payment = serializer.save(user=self.request.user)
            
            # Here should be payment initialization logic through payment system
            # payment.initialize_payment()
            
            return self.success_response(
                data=serializer.data,
                message='Payment initialized successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_INIT_ERROR',
                error_message=f'Error initializing payment: {str(e)}',
                status_code=500
            )

class PaymentStatusView(BaseAPIView, generics.RetrieveAPIView):
    """Payment status"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get payment status by ID (owner only)",
        responses={
            200: openapi.Response('Payment status', PaymentSerializer),
            403: 'No permissions',
            404: 'Payment not found',
        },
        tags=['Payments']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check access rights
            if instance.user != self.request.user:
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='No permissions to view this payment',
                    status_code=403
                )
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Payment status retrieved successfully'
            )
            
        except Payment.DoesNotExist:
            return self.error_response(
                error_number='PAYMENT_NOT_FOUND',
                error_message='Payment not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_STATUS_ERROR',
                error_message=f'Error retrieving payment status: {str(e)}',
                status_code=500
            )

class PaymentHistoryView(BaseAPIView, generics.ListAPIView):
    """User payment history"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get user's payment history",
        responses={
            200: openapi.Response('Payment history', PaymentSerializer(many=True)),
        },
        tags=['Payments']
    )
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Payment history retrieved successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_HISTORY_ERROR',
                error_message=f'Error retrieving payment history: {str(e)}',
                status_code=500
            )

class PaymentListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """List and create payments"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user's payment history",
        responses={
            200: openapi.Response('Payment history', PaymentSerializer(many=True)),
        },
        tags=['Payments']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = Payment.objects.filter(user=self.request.user)
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message='Payment history retrieved successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_HISTORY_ERROR',
                error_message=f'Error retrieving payment history: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Initialize new payment (create payment request)",
        request_body=PaymentSerializer,
        responses={
            201: openapi.Response('Payment initialized', PaymentSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Payments']
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
                    error_message='Payment amount must be greater than zero',
                    status_code=400
                )
            payment = serializer.save(user=self.request.user)
            # Here can be payment initialization logic through payment system
            return self.success_response(
                data=serializer.data,
                message='Payment initialized successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='PAYMENT_INIT_ERROR',
                error_message=f'Error initializing payment: {str(e)}',
                status_code=500
            )