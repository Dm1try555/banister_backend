from core.base.common_imports import *
from .models import Withdrawal
from .serializers import (
    WithdrawalSerializer, WithdrawalCreateSerializer, WithdrawalUpdateSerializer,
    WithdrawalApproveSerializer, WithdrawalRejectSerializer
)
from core.stripe.service import stripe_service
from .permissions import WithdrawalPermissions


class WithdrawalListCreateView(OptimizedListCreateView, WithdrawalPermissions):
    queryset = Withdrawal.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return WithdrawalCreateSerializer if self.request.method == 'POST' else WithdrawalSerializer

    @swagger_list_create(
        description="Create new withdrawal request",
        response_schema=WITHDRAWAL_RESPONSE_SCHEMA,
        tags=["Withdrawals"]
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WithdrawalDetailView(OptimizedRetrieveUpdateDestroyView, WithdrawalPermissions):
    queryset = Withdrawal.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WithdrawalUpdateSerializer
        return WithdrawalSerializer




class WithdrawalApproveView(BaseAPIView, WithdrawalPermissions):
    serializer_class = WithdrawalApproveSerializer
    queryset = Withdrawal.objects.all().order_by('-created_at')

    @swagger_auto_schema(
        operation_description="Approve withdrawal request",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'withdrawal_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        },
        tags=["Withdrawals"]
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        withdrawal = self.get_object()
        
        if withdrawal.status != 'pending':
            ErrorCode.INVALID_WITHDRAWAL_STATUS.raise_error()
        
        withdrawal.status = 'approved'
        withdrawal.completed_at = timezone.now()
        withdrawal.save()
        
        return self.get_success_response({
            'status': 'success',
            'message': 'Withdrawal approved successfully',
            'withdrawal_id': withdrawal.id
        })


class WithdrawalRejectView(BaseAPIView, WithdrawalPermissions):
    serializer_class = WithdrawalRejectSerializer
    queryset = Withdrawal.objects.all().order_by('-created_at')

    @swagger_auto_schema(
        operation_description="Reject withdrawal request",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'withdrawal_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        },
        tags=["Withdrawals"]
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        withdrawal = self.get_object()
        serializer = self.get_serializer(withdrawal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if withdrawal.status != 'pending':
            ErrorCode.INVALID_WITHDRAWAL_STATUS.raise_error()
        
        withdrawal.status = 'rejected'
        withdrawal.save()
        
        return self.get_success_response({
            'status': 'success',
            'message': 'Withdrawal rejected successfully',
            'withdrawal_id': withdrawal.id
        })