from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Withdrawal
from .serializers import WithdrawalSerializer

# Import error handling system
from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class WithdrawalCreateView(BaseAPIView, generics.CreateAPIView):
    """Create withdrawal request"""
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Create withdrawal request (providers only)",
        request_body=WithdrawalSerializer,
        responses={
            201: openapi.Response('Request created', WithdrawalSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Withdrawals']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            # Check user role
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Only service providers can create withdrawal requests',
                    status_code=403
                )
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            # Check minimum withdrawal amount
            amount = serializer.validated_data.get('amount', 0)
            if amount <= 0:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Withdrawal amount must be greater than zero',
                    status_code=400
                )
            
            # Check user balance (balance checking logic should be here)
            # if self.request.user.balance < amount:
            #     return self.error_response(
            #         error_number='INSUFFICIENT_BALANCE',
            #         error_message='Insufficient funds for withdrawal',
            #         status_code=400
            #     )
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Withdrawal request created successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_CREATE_ERROR',
                error_message=f'Error creating withdrawal request: {str(e)}',
                status_code=500
            )

class WithdrawalHistoryView(BaseAPIView, generics.ListAPIView):
    """Withdrawal history"""
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # For swagger schema generation or if no user.role — return empty queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Withdrawal.objects.none()
        return Withdrawal.objects.filter(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Get history of all withdrawal requests (providers only)",
        responses={
            200: openapi.Response('Withdrawal history', WithdrawalSerializer(many=True)),
            403: 'No permissions',
        },
        tags=['Withdrawals']
    )
    def list(self, request, *args, **kwargs):
        try:
            # Check user role
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Only service providers can view withdrawal history',
                    status_code=403
                )
            
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Withdrawal history retrieved successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_HISTORY_ERROR',
                error_message=f'Error retrieving withdrawal history: {str(e)}',
                status_code=500
            )

class WithdrawalListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """List and create withdrawal requests"""
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Withdrawal.objects.none()
        return Withdrawal.objects.filter(provider=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        if self.request.user.role != 'provider':
            raise CustomPermissionError('Only service providers can create withdrawal requests')
        amount = serializer.validated_data.get('amount', 0)
        if amount <= 0:
            raise ValidationError('Withdrawal amount must be greater than zero')
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Get history of all withdrawal requests (providers only)",
        responses={
            200: openapi.Response('Withdrawal history', WithdrawalSerializer(many=True)),
            403: 'No permissions',
        },
        tags=['Withdrawals']
    )
    def list(self, request, *args, **kwargs):
        try:
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Only service providers can view withdrawal history',
                    status_code=403
                )
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message='Withdrawal history retrieved successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_HISTORY_ERROR',
                error_message=f'Error retrieving withdrawal history: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Create withdrawal request (providers only)",
        request_body=WithdrawalSerializer,
        responses={
            201: openapi.Response('Request created', WithdrawalSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Withdrawals']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            if self.request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Only service providers can create withdrawal requests',
                    status_code=403
                )
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            amount = serializer.validated_data.get('amount', 0)
            if amount <= 0:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Withdrawal amount must be greater than zero',
                    status_code=400
                )
            serializer.save(provider=self.request.user)
            return self.success_response(
                data=serializer.data,
                message='Withdrawal request created successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='WITHDRAWAL_CREATE_ERROR',
                error_message=f'Error creating withdrawal request: {str(e)}',
                status_code=500
            )